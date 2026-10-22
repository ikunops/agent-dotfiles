#!/usr/bin/env node
/**
 * readability.cjs - 字幕可读时长检查
 *
 * 用法:
 *   node readability.cjs captions.json [fps] [--cps 5.2]
 *   node readability.cjs --selftest
 *
 * captions.json 支持两种格式:
 *   1) [{"text":"...","start":0.5,"end":2.0}, ...]   单位秒
 *   2) [{"text":"...","from":30,"to":120}, ...]      单位帧 (需传 fps)
 */
const fs = require('fs');

function charCount(s) {
  const cjk = (s.match(/[\u3400-\u9FFF\uF900-\uFAFF]/g) || []).length;
  const latin = (s.match(/[A-Za-z]+/g) || []).length;
  const digits = (s.match(/\d+(\.\d+)?/g) || []).length;
  const punct = (s.match(/[，。、；：！？,.;:!?"'（）()《》—…]/g) || []).length;
  return cjk + latin * 1.6 + digits * 1.2 + punct * 0.3;
}

function toSeconds(item, fps) {
  const hasFrames = item.from != null || item.to != null;
  if (hasFrames) {
    if (!fps) throw new Error('captions 用的是帧号，需要传 fps');
    return { start: item.from / fps, end: item.to / fps };
  }
  return { start: item.start, end: item.end };
}

function check(items, opts) {
  opts = opts || {};
  const fps = opts.fps || null;
  const cps = opts.cps || 5.2;
  const pad = opts.pad != null ? opts.pad : 0.35;
  const minGap = opts.minGap != null ? opts.minGap : 0.18;

  const rows = items.map((it, i) => {
    const t = toSeconds(it, fps);
    const n = charCount(it.text || '');
    const dur = t.end - t.start;
    const need = n / cps + pad;
    return { i, text: it.text, start: t.start, end: t.end, dur, n, need, ok: dur >= need };
  });

  const errors = [];
  rows.forEach(r => {
    if (r.dur <= 0) errors.push('#' + r.i + ' 时长非正: ' + r.text);
    else if (!r.ok) {
      errors.push('#' + r.i + ' 停留不足: ' + r.dur.toFixed(2) + 's < 需要 ' + r.need.toFixed(2) +
        's (' + r.n.toFixed(1) + ' 字 @ ' + cps + ' 字/秒) | ' + r.text);
    }
  });

  const sorted = rows.slice().sort((a, b) => a.start - b.start);
  for (let k = 1; k < sorted.length; k++) {
    const a = sorted[k - 1], b = sorted[k];
    if (b.start < a.end - 1e-6) {
      errors.push('#' + a.i + ' 与 #' + b.i + ' 时间重叠: ' + a.end.toFixed(2) + 's > ' + b.start.toFixed(2) + 's');
    } else if (b.start - a.end < minGap) {
      errors.push('#' + a.i + ' -> #' + b.i + ' 切换过急: 间隔 ' + (b.start - a.end).toFixed(2) + 's < ' + minGap + 's');
    }
  }
  return { rows, errors };
}

function fmt(rows) {
  const head = 'idx  start   end    dur   chars  need   verdict  text';
  const body = rows.map(r => [
    String(r.i).padStart(3),
    r.start.toFixed(2).padStart(6),
    r.end.toFixed(2).padStart(6),
    r.dur.toFixed(2).padStart(6),
    r.n.toFixed(1).padStart(6),
    r.need.toFixed(2).padStart(6),
    (r.ok ? 'ok' : 'FAIL').padStart(8),
    r.text
  ].join(' '));
  return [head].concat(body).join('\n');
}

function main() {
  const argv = process.argv.slice(2);
  if (argv.indexOf('--selftest') >= 0) {
    const demo = [
      { text: '比较，是偷走幸福的小偷', start: 0, end: 0.4 },
      { text: '是', start: 0.4, end: 0.45 },
      { text: '你羡慕的，是别人愿意让你看见的那一面', start: 1.0, end: 3.2 },
      { text: '还是你真正想要的那一面', start: 3.18, end: 5.0 }
    ];
    const r = check(demo);
    console.log(fmt(r.rows));
    console.log('\n发现 ' + r.errors.length + ' 处问题:');
    r.errors.forEach(e => console.log(' - ' + e));
    console.log('\n(自测预期: 停留不足 + 时间重叠都应报出)');
    return;
  }
  const file = argv[0];
  if (!file) {
    console.error('用法: node readability.cjs captions.json [fps] [--cps 5.2]');
    process.exit(2);
  }
  const fps = argv[1] && argv[1].charAt(0) !== '-' ? Number(argv[1]) : null;
  const cpsIdx = argv.indexOf('--cps');
  const cps = cpsIdx >= 0 ? Number(argv[cpsIdx + 1]) : 5.2;
  const items = JSON.parse(fs.readFileSync(file, 'utf8'));
  const r = check(items, { fps, cps });
  console.log(fmt(r.rows));
  if (r.errors.length) {
    console.log('\n发现 ' + r.errors.length + ' 处问题:');
    r.errors.forEach(e => console.log(' - ' + e));
    process.exit(1);
  }
  console.log('\n全部通过。');
}

if (require.main === module) main();
module.exports = { check, charCount, fmt };
