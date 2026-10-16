const {openBrowser, ensureBrowser} = require("@remotion/renderer");
const {bundle} = require("@remotion/bundler");
const path = require("path"), http = require("http"), fs = require("fs");
const MIME = {".html":"text/html",".js":"text/javascript",".css":"text/css",".json":"application/json",".png":"image/png",".jpg":"image/jpeg",".ttf":"font/ttf",".woff2":"font/woff2",".svg":"image/svg+xml",".map":"application/json"};
const serve = (dir) => new Promise((res) => {
  const srv = http.createServer((req, r) => {
    let p = decodeURIComponent(req.url.split("?")[0].split("#")[0]);
    if (p === "/") p = "/index.html";
    fs.readFile(path.join(dir, p), (e, buf) => {
      if (e) { r.writeHead(404); r.end("nf"); return; }
      r.writeHead(200, {"Content-Type": MIME[path.extname(p)] || "application/octet-stream"});
      r.end(buf);
    });
  });
  srv.listen(0, "127.0.0.1", () => res({srv, port: srv.address().port}));
});
const wait = (ms) => new Promise(r => setTimeout(r, ms));

const FILMS = { Theseus: 720, Cave: 720, Zeno: 720, Trolley: 1080 };
const STEP = Number(process.argv[2] || 10);

const overlap = (a, b) => {
  const x = Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x));
  const y = Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
  return x * y;
};

(async () => {
  await ensureBrowser();
  const dir = await bundle({entryPoint: path.resolve("tools/overlap/entry.tsx"), publicDir: null, ignoreRegisterRootWarning: true, onProgress: () => {}});
  const {srv, port} = await serve(dir);
  const browser = await openBrowser("chrome");
  const page = await browser.newPage({context: null, logLevel: "error", indent: false, pageIndex: 0, onBrowserLog: () => undefined, onLog: () => undefined});
  page.setBrowserSourceMapGetter(() => null);
  await page.setViewport({width: 1920, height: 1080, deviceScaleFactor: 1});
  const report = {};
  for (const [id, dur] of Object.entries(FILMS)) {
    await page.goto({url: "http://127.0.0.1:" + port + "/index.html?id=" + id, timeout: 40000});
    await wait(3500);
    const issues = [];
    for (let f = 0; f <= dur; f += STEP) {
      await page.evaluate((fr) => window.__seek(fr), f);
      await wait(60);
      const m = await page.evaluate(() => window.__measure());
      const { texts, W, H } = m;
      // A) \u6587\u5b57\u8d85\u51fa\u753b\u5e03
      for (const t of texts) {
        if (t.y + t.h > H - 6 || t.y < -6 || t.x < -6 || t.x + t.w > W + 6) {
          issues.push({ f, kind: "OFFSCREEN", a: t.s, box: [t.x|0, t.y|0, t.w|0, t.h|0] });
        }
      }
      // B) \u6587\u5b57-\u6587\u5b57\u91cd\u53e0
      for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
        const ov = overlap(texts[i], texts[j]);
        const small = Math.min(texts[i].w * texts[i].h, texts[j].w * texts[j].h);
        if (ov > small * 0.12) issues.push({ f, kind: "TEXT-TEXT", a: texts[i].s, b: texts[j].s, ov: (ov/small*100)|0 });
      }
      // C) text-vs-subject: real pixel-hit test (not bounding boxes)
      for (const t of texts) {
        if (t.frac && t.frac > 0.06) {
          issues.push({ f, kind: "TEXT-FIG", a: t.s, fig: t.hit || "fig", ov: Math.round(t.frac * 100) });
        }
      }
    }
    // \u5408\u5e76\u8fde\u7eed\u5e27
    const merged = {};
    for (const it of issues) {
      const key = it.kind + "|" + it.a + "|" + (it.b || it.fig || "");
      if (!merged[key]) merged[key] = { ...it, frames: [it.f] };
      else merged[key].frames.push(it.f);
    }
    report[id] = Object.values(merged).map((m) => ({ kind: m.kind, a: m.a, b: m.b, fig: m.fig, ov: m.ov, span: m.frames[0] + "-" + m.frames[m.frames.length - 1], n: m.frames.length, box: m.box }));
  }
  console.log(JSON.stringify(report, null, 1));
  fs.writeFileSync("out/overlap-report.json", JSON.stringify(report, null, 1));
  srv.close(); await browser.close({silent: true}); process.exit(0);
})().catch(e => { console.log("ERR", e.message, e.stack); process.exit(1); });
