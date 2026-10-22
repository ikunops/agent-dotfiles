// transition-continuity.cjs - heuristic continuity checks around a cut/transition.
//
// Usage:
//   node transition-continuity.cjs --left before.png --right after.png
//   node transition-continuity.cjs --dir frames --at 120 [--radius 5]
//   node transition-continuity.cjs --manifest transitions.json
//   node transition-continuity.cjs --selftest
//
// This is a guardrail, not a substitute for human review. It catches the common
// "black -> bright -> new scene" and "static -> hard cut" failures. A match cut
// between different scenes is allowed when at least one continuity signal
// (luminance band, color family, or coarse structure) survives the handoff.

const fs = require('fs');
const path = require('path');

let PNG = null;
try { PNG = require('pngjs').PNG; } catch (_) { PNG = null; }

// Fallback PNG decoder for common 8-bit RGB/RGBA non-interlaced PNGs.
// This keeps the checker usable in projects without pngjs.
function decodePngFallback(file) {
  const zlib = require('zlib');
  const buf = fs.readFileSync(file);
  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  if (buf.length < 33 || !buf.subarray(0, 8).equals(sig)) throw new Error('not a PNG: ' + file);
  let off = 8, width = 0, height = 0, bitDepth = 0, colorType = 0, interlace = 0;
  const idat = [];
  while (off + 8 <= buf.length) {
    const len = buf.readUInt32BE(off);
    const type = buf.toString('ascii', off + 4, off + 8);
    const data = buf.subarray(off + 8, off + 8 + len);
    off += 12 + len;
    if (type === 'IHDR') {
      width = data.readUInt32BE(0); height = data.readUInt32BE(4);
      bitDepth = data[8]; colorType = data[9]; interlace = data[12];
    } else if (type === 'IDAT') idat.push(data);
    else if (type === 'IEND') break;
  }
  if (bitDepth !== 8) throw new Error('fallback decoder supports 8-bit PNG only: ' + file);
  if (![2, 6].includes(colorType)) throw new Error('fallback decoder supports RGB/RGBA PNG only: ' + file);
  if (interlace !== 0) throw new Error('fallback decoder does not support interlaced PNG: ' + file);
  const channels = colorType === 6 ? 4 : 3;
  const raw = zlib.inflateSync(Buffer.concat(idat));
  const stride = width * channels;
  const out = Buffer.alloc(width * height * 4);
  let prev = Buffer.alloc(stride), pos = 0;
  for (let y = 0; y < height; y++) {
    const filter = raw[pos++];
    const row = Buffer.from(raw.subarray(pos, pos + stride)); pos += stride;
    for (let x = 0; x < stride; x++) {
      const a = x >= channels ? row[x - channels] : 0;
      const b = prev[x] || 0;
      const c = x >= channels ? (prev[x - channels] || 0) : 0;
      let v = row[x];
      if (filter === 1) v = (v + a) & 255;
      else if (filter === 2) v = (v + b) & 255;
      else if (filter === 3) v = (v + ((a + b) >> 1)) & 255;
      else if (filter === 4) {
        const p = a + b - c, pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c);
        v = (v + (pa <= pb && pa <= pc ? a : pb <= pc ? b : c)) & 255;
      } else if (filter !== 0) throw new Error('unsupported PNG filter: ' + filter);
      row[x] = v;
    }
    for (let x = 0; x < width; x++) {
      const si = x * channels, di = (y * width + x) * 4;
      out[di] = row[si]; out[di + 1] = row[si + 1]; out[di + 2] = row[si + 2];
      out[di + 3] = channels === 4 ? row[si + 3] : 255;
    }
    prev = row;
  }
  return {width, height, data: out};
}

function usage() {
  console.error('usage: node transition-continuity.cjs --left before.png --right after.png');
  console.error('   or: node transition-continuity.cjs --dir frames --at 120 [--radius 5]');
  console.error('   or: node transition-continuity.cjs --manifest transitions.json');
  console.error('   or: node transition-continuity.cjs --selftest');
  process.exit(2);
}

function parseArgs(argv) {
  const out = {radius: 5, at: null, dir: null, left: null, right: null, manifest: null, selftest: false};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--selftest') out.selftest = true;
    else if (a === '--left') out.left = argv[++i];
    else if (a === '--right') out.right = argv[++i];
    else if (a === '--dir') out.dir = argv[++i];
    else if (a === '--at') out.at = Number(argv[++i]);
    else if (a === '--radius') out.radius = Number(argv[++i]);
    else if (a === '--manifest') out.manifest = argv[++i];
    else usage();
  }
  return out;
}

function readPng(file) {
  return PNG ? PNG.sync.read(fs.readFileSync(file)) : decodePngFallback(file);
}

function stats(img) {
  const {width, height, data} = img;
  let n = 0, sum = 0, sum2 = 0, dark = 0, bright = 0, r = 0, g = 0, b = 0;
  for (let y = 0; y < height; y += 2) {
    for (let x = 0; x < width; x += 2) {
      const i = (y * width + x) * 4;
      if (data[i + 3] < 16) continue;
      const R = data[i], G = data[i + 1], B = data[i + 2];
      const l = 0.2126 * R + 0.7152 * G + 0.0722 * B;
      sum += l; sum2 += l * l; n++;
      if (l < 8) dark++;
      if (l > 247) bright++;
      r += R; g += G; b += B;
    }
  }
  if (!n) return {n: 0, mean: 0, std: 0, dark: 1, bright: 1, r: 0, g: 0, b: 0};
  const mean = sum / n;
  return {n, mean, std: Math.sqrt(Math.max(0, sum2 / n - mean * mean)), dark: dark / n, bright: bright / n, r: r / n, g: g / n, b: b / n};
}

function colorDist(a, b) {
  return Math.hypot(a.r - b.r, a.g - b.g, a.b - b.b) / 441.67;
}

function structureSignature(img) {
  const {width, height, data} = img;
  const gw = 16, gh = 16, cells = [];
  for (let gy = 0; gy < gh; gy++) {
    for (let gx = 0; gx < gw; gx++) {
      let sum = 0, n = 0;
      const x0 = Math.floor(gx * width / gw), x1 = Math.floor((gx + 1) * width / gw);
      const y0 = Math.floor(gy * height / gh), y1 = Math.floor((gy + 1) * height / gh);
      for (let y = y0; y < y1; y += 2) for (let x = x0; x < x1; x += 2) {
        const i = (y * width + x) * 4;
        sum += 0.2126 * data[i] + 0.7152 * data[i + 1] + 0.0722 * data[i + 2];
        n++;
      }
      cells.push(n ? sum / n : 0);
    }
  }
  const mean = cells.reduce((s, v) => s + v, 0) / cells.length;
  const std = Math.sqrt(cells.reduce((s, v) => s + (v - mean) ** 2, 0) / cells.length) || 1;
  return cells.map(v => (v - mean) / std);
}

function structureDist(a, b) {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += Math.abs(a[i] - b[i]);
  return s / a.length / 4;
}

function checkPair(leftImg, rightImg, options = {}) {
  const L = stats(leftImg), R = stats(rightImg);
  const structure = structureDist(structureSignature(leftImg), structureSignature(rightImg));
  const evidence = {
    luminance: Math.abs(L.mean - R.mean) / 255 < 0.12,
    color: colorDist(L, R) < 0.10,
    structure: structure < 0.28,
  };
  const blackGap = L.dark > 0.85 || R.dark > 0.85;
  const whiteGap = L.bright > 0.85 || R.bright > 0.85;
  const allowBlack = options.allowBlack === true && blackGap;
  const allowWhite = options.allowWhite === true && whiteGap;
  const pass = (evidence.luminance || evidence.color || evidence.structure) && (!blackGap || allowBlack) && (!whiteGap || allowWhite);
  return {pass, evidence, blackGap, whiteGap, allowBlack, allowWhite, left: L, right: R, structure};
}

function report(rows) {
  let failed = 0;
  for (const row of rows) {
    const r = row.result;
    if (!r.pass) failed++;
    const ev = Object.entries(r.evidence).filter(([, v]) => v).map(([k]) => k).join(',') || 'none';
    console.log((r.pass ? 'PASS ' : 'FAIL ') + row.from + ' -> ' + row.to);
    console.log('  continuity: ' + ev);
    console.log('  luminance ' + r.left.mean.toFixed(1) + ' -> ' + r.right.mean.toFixed(1) + ' | structure ' + r.structure.toFixed(3));
    if (r.blackGap) console.log('  black gap: one side is nearly all black');
    if (r.whiteGap) console.log('  white gap: one side is nearly all white');
    if (r.allowBlack) console.log('  exception: black gap allowed');
    if (r.allowWhite) console.log('  exception: white gap allowed');
    if (row.reason) console.log('  exception reason: ' + row.reason);
  }
  console.log('\n' + (rows.length - failed) + '/' + rows.length + ' passed');
  return failed;
}

function loadFrame(dir, n) {
  const candidates = [
    n + '.png',
    'frame-' + String(n).padStart(5, '0') + '.png',
    'frame_' + String(n).padStart(5, '0') + '.png',
  ];
  for (const c of candidates) {
    const p = path.join(dir, c);
    if (fs.existsSync(p)) return p;
  }
  return null;
}

function runDir(opts) {
  if (!Number.isFinite(opts.at)) usage();
  const radius = Math.max(1, Math.min(30, opts.radius || 5));
  const left = loadFrame(opts.dir, opts.at - radius);
  const right = loadFrame(opts.dir, opts.at + radius);
  if (!left || !right) throw new Error('frames not found around ' + opts.at + ' in ' + opts.dir);
  const result = checkPair(readPng(left), readPng(right));
  report([{from: left, to: right, result}]);
  process.exit(result.pass ? 0 : 1);
}

function runManifest(file) {
  const cfg = JSON.parse(fs.readFileSync(file, 'utf8'));
  const rows = [];
  for (const t of cfg.transitions || []) {
    if (!t.left || !t.right) throw new Error('manifest entry needs left/right: ' + JSON.stringify(t));
    const left = path.isAbsolute(t.left) ? t.left : path.resolve(path.dirname(file), t.left);
    const right = path.isAbsolute(t.right) ? t.right : path.resolve(path.dirname(file), t.right);
    const result = checkPair(readPng(left), readPng(right), t);
    if ((t.allowBlack || t.allowWhite) && String(t.reason || "").trim().length < 4) {
      throw new Error("manifest exception needs a specific reason (4+ chars): " + JSON.stringify(t));
    }
    rows.push({from: left, to: right, result, reason: t.reason || null});
  }
  const failed = report(rows);
  process.exit(failed ? 1 : 0);
}

function selftest() {
  const make = fn => {
    if (PNG) {
      const img = new PNG({width: 64, height: 64});
      for (let y = 0; y < 64; y++) for (let x = 0; x < 64; x++) {
        const i = (y * 64 + x) * 4;
        const c = fn(x, y);
        img.data[i] = c[0]; img.data[i + 1] = c[1]; img.data[i + 2] = c[2]; img.data[i + 3] = 255;
      }
      return img;
    }
    const data = Buffer.alloc(64 * 64 * 4);
    for (let y = 0; y < 64; y++) for (let x = 0; x < 64; x++) {
      const i = (y * 64 + x) * 4;
      const c = fn(x, y);
      data[i] = c[0]; data[i + 1] = c[1]; data[i + 2] = c[2]; data[i + 3] = 255;
    }
    return {width: 64, height: 64, data};
  };
  const blue = make(() => [30, 60, 180]);
  const blue2 = make(() => [32, 62, 182]);
  const black = make(() => [0, 0, 0]);
  const white = make(() => [255, 255, 255]);
  const redCircle = make((x, y) => ((x - 32) ** 2 + (y - 32) ** 2 < 400 ? [220, 40, 40] : [20, 20, 20]));
  const cases = [
    ['same scene', blue, blue2, true],
    ['black gap', blue, black, false],
    ['white gap', blue, white, false],
    ['black gap explicit exception', blue, black, true, {allowBlack: true}],
    ['different but structural', blue, redCircle, true],
  ];
  let bad = 0;
  for (const [name, a, b, expected, options] of cases) {
    const r = checkPair(a, b, options);
    if (r.pass !== expected) { bad++; console.error('FAIL selftest ' + name + ': expected ' + expected + ', got ' + r.pass); }
    else console.log('PASS selftest ' + name + ': expected ' + expected + ', got ' + r.pass);
  }
  process.exit(bad ? 1 : 0);
}

try {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.selftest) selftest();
  else if (opts.left && opts.right) {
    const result = checkPair(readPng(opts.left), readPng(opts.right));
    report([{from: opts.left, to: opts.right, result}]);
    process.exit(result.pass ? 0 : 1);
  } else if (opts.dir) runDir(opts);
  else if (opts.manifest) runManifest(opts.manifest);
  else usage();
} catch (e) {
  console.error('ERR ' + e.message);
  process.exit(1);
}
