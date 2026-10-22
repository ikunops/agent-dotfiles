// 轨迹扫描器：逐帧记录每个绘制元素的真实矩形，并做像素级命中测试。
// 目的：不仅看"某一帧有没有撞"，而是看"整条时间线上两个东西的轨迹会不会撞"。
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
// 片表与画布从 tools/overlap/films.json 读，换项目时不用改脚本。
// {"width":1920,"height":1080,"films":{"<id>":<durationFrames>}}
const CFG = JSON.parse(fs.readFileSync(path.resolve("tools/overlap/films.json"), "utf8"));
const FILMS = CFG.films;
const W = CFG.width, H = CFG.height;
const STEP = Number(process.argv[2] || 3);
const ONLY = process.argv[3] || null;

const inter = (a, b) => {
  const x = Math.max(0, Math.min(a.x+a.w, b.x+b.w) - Math.max(a.x, b.x));
  const y = Math.max(0, Math.min(a.y+a.h, b.y+b.h) - Math.max(a.y, b.y));
  return x * y;
};
const contains = (a, b) =>
  a.x <= b.x + 2 && a.y <= b.y + 2 &&
  a.x + a.w >= b.x + b.w - 2 && a.y + a.h >= b.y + b.h - 2;

(async () => {
  await ensureBrowser();
  const dir = await bundle({entryPoint: path.resolve("tools/overlap/entry.tsx"), publicDir: null, ignoreRegisterRootWarning: true, onProgress: () => {}});
  const {srv, port} = await serve(dir);
  const browser = await openBrowser("chrome");
  const page = await browser.newPage({context: null, logLevel: "error", indent: false, pageIndex: 0, onBrowserLog: () => undefined, onLog: () => undefined});
  page.setBrowserSourceMapGetter(() => null);
  await page.setViewport({width: W, height: H, deviceScaleFactor: 1});

  const report = {};
  const films = ONLY ? {[ONLY]: FILMS[ONLY]} : FILMS;
  for (const [id, dur] of Object.entries(films)) {
    await page.goto({url: "http://127.0.0.1:" + port + "/index.html?id=" + id, timeout: 60000});
    await wait(4000);

    // 逐帧采集：文字盒 + 所有图形盒 + 像素命中率
    const frames = [];
    for (let f = 0; f < dur; f += STEP) {
      await page.evaluate((fr) => window.__seek(fr), f);
      await wait(38);
      const m = await page.evaluate(({W, H}) => {
        const svg = document.querySelector("#harness-root svg");
        if (!svg) return {texts: [], arts: [], W, H};
        const rb = svg.getBoundingClientRect();
        const kx = W/(rb.width||W), ky = H/(rb.height||H);
        const box = (el) => { const q = el.getBoundingClientRect();
          return {x:(q.left-rb.left)*kx, y:(q.top-rb.top)*ky, w:q.width*kx, h:q.height*ky}; };
        const effOp = (el) => { let o=1,n=el;
          while (n && n!==svg) { const st=getComputedStyle(n);
            if (st.display==="none"||st.visibility==="hidden") return 0;
            o*=parseFloat(st.opacity||"1"); n=n.parentElement; } return o; };

        const all = [...svg.querySelectorAll("text,rect,line,circle,ellipse,path,polyline,polygon")];
        const texts = [], arts = [];
        for (const el of all) {
          if (effOp(el) <= 0.04) continue;
          const b = box(el);
          if (b.w <= 0 || b.h <= 0) continue;
          const tag = el.tagName.toLowerCase();
          if (tag === "text") {
            const s = (el.textContent||"").trim();
            if (!s) continue;
            texts.push({s, cap: !!el.closest("[data-cap]"), fig: !!el.closest("[data-fig]"), ...b});
          } else {
            arts.push({tag, fig: !!el.closest("[data-fig]"), el, ...b});
          }
        }
        // 像素命中：只给"非文字、非背景"的图形开放 pointer-events
        const C = W*H;
        const probes = arts.filter(a => a.w*a.h < C*0.28);
        const prevRoot = svg.style.pointerEvents;
        const prev = probes.map(a => a.el.style.pointerEvents);
        svg.style.pointerEvents = "none";
        probes.forEach(a => { a.el.style.pointerEvents = "auto"; });
        // 只统计真正命中图形元素的点；
        // 命中 div/svg 说明该处没有图形（是兑底），不算命中。
        const ART = new Set(["path","rect","line","circle","ellipse","polyline","polygon"]);
        // 判定某个图形是不是这段文字的「自己的底」：
        // 完全包住文字、且面积远大于文字（面板/色块）→ 不算碰撞。
        const ownBg = (a, t) => {
          const c = a.getBoundingClientRect();
          const A = {x:(c.left-rb.left)*kx, y:(c.top-rb.top)*ky, w:c.width*kx, h:c.height*ky};
          const wrap = A.x <= t.x+2 && A.y <= t.y+2 &&
                       A.x+A.w >= t.x+t.w-2 && A.y+A.h >= t.y+t.h-2;
          return wrap && (A.w*A.h) > (t.w*t.h)*2.2;
        };
        const COLS=7, ROWS=4;
        const hits = texts.map(t => {
          let hit=0, tot=0, tags={};
          for (let i=1;i<COLS;i++) for (let j=1;j<ROWS;j++) {
            const sx=t.x+t.w*i/COLS, sy=t.y+t.h*j/ROWS;
            const el = document.elementFromPoint(rb.left+sx/kx, rb.top+sy/ky);
            tot++;
            if (!el || !el.tagName) continue;
            const k = el.tagName.toLowerCase();
            if (!ART.has(k)) continue;                             // div/svg → 没碰到东西
            if (el.closest && el.closest("[data-cap]")) continue;   // 字自己
            if (ownBg(el, t)) continue;                             // 它自己的背景板
            hit++; tags[k]=(tags[k]||0)+1;
          }
          return {frac: tot? hit/tot : 0, tags};
        });
        svg.style.pointerEvents = prevRoot;
        probes.forEach((a,i) => { a.el.style.pointerEvents = prev[i]; });
        return {
          texts: texts.map((t,i) => ({s:t.s, cap:t.cap, fig:t.fig, x:t.x, y:t.y, w:t.w, h:t.h, frac:hits[i].frac, tags:hits[i].tags})),
          arts: arts.map(a => ({tag:a.tag, fig:a.fig, x:a.x, y:a.y, w:a.w, h:a.h})),
          W, H,
        };
      }, {W, H});
      frames.push({f, ...m});
    }

    // 汇总：文字被图形"像素命中"的时间段
    const byText = {};
    for (const fr of frames) {
      for (const t of fr.texts) {
        if (!t.frac || t.frac <= 0.10) continue;
        const k = t.s;
        (byText[k] = byText[k] || {s:k, cap:t.cap, maxFrac:0, tags:{}, frames:[]});
        byText[k].maxFrac = Math.max(byText[k].maxFrac, t.frac);
        for (const [g,c] of Object.entries(t.tags||{})) byText[k].tags[g] = (byText[k].tags[g]||0)+c;
        byText[k].frames.push(fr.f);
      }
    }
    // 汇总：矩形相交（捕捉快速移动物体在采样间隙穿过的情况）
    const rectHits = {};
    for (const fr of frames) {
      const arts = fr.arts.filter(a => a.w*a.h < fr.W*fr.H*0.28);
      for (const t of fr.texts) {
        for (const a of arts) {
          const ov = inter(t, a);
          if (ov <= 0) continue;
          const small = Math.min(t.w*t.h, a.w*a.h);
          if (ov <= small*0.10) continue;
          if (contains(a,t) && a.w*a.h > t.w*t.h*1.06) continue;
          const k = t.s + " || " + a.tag;
          (rectHits[k] = rectHits[k] || {t:t.s, a:a.tag, ov:0, frames:[]});
          rectHits[k].ov = Math.max(rectHits[k].ov, Math.round(ov/small*100));
          rectHits[k].frames.push(fr.f);
        }
      }
    }
    const collapse = (arr) => arr.map(o => ({...o, span:o.frames[0]+"-"+o.frames[o.frames.length-1], n:o.frames.length}))
      .map(({frames, ...rest}) => rest).sort((a,b)=>b.n-a.n);

    report[id] = {
      pixelHits: collapse(Object.values(byText).map(o => ({...o, maxFrac:o.maxFrac, tags:o.tags, frames:o.frames}))),
      rectHits: collapse(Object.values(rectHits)),
      trajectories: frames.map(fr => ({
        f: fr.f,
        texts: fr.texts.map(t => ({s:t.s, x:Math.round(t.x), y:Math.round(t.y), w:Math.round(t.w), h:Math.round(t.h)})),
      })),
    };
  }
  fs.writeFileSync("out/trajectory-report.json", JSON.stringify(report, null, 1));
  for (const [id, v] of Object.entries(report)) {
    console.log("=== " + id);
    console.log("  [像素命中]");
    for (const c of v.pixelHits.slice(0,12))
      console.log("    " + String(Math.round(c.maxFrac*100)).padStart(3) + "%  " + c.s.slice(0,26) + "  f" + c.span + " n=" + c.n + "  " + JSON.stringify(c.tags));
    console.log("  [矩形相交]");
    for (const c of v.rectHits.slice(0,12))
      console.log("    " + String(c.ov).padStart(3) + "%  " + c.t.slice(0,22) + "  x  " + c.a + "  f" + c.span + " n=" + c.n);
  }
  srv.close(); await browser.close({silent: true}); process.exit(0);
})().catch(e => { console.log("ERR", e.message, e.stack); process.exit(1); });
