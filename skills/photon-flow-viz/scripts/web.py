# -*- coding: utf-8 -*-
"""
web.py — bake a frame sequence into ONE self-contained HTML player.

Why bake frames instead of shipping a live canvas renderer
---------------------------------------------------------
The look depends on additive float accumulation: light is allowed to exceed 1.0,
bloom is applied there, and only then is it tone-mapped. A browser canvas clips
to 8 bits per draw, so a live re-implementation looks flat and the highlights
lose their falloff. Baking the frames in Python keeps the look exact.

The cost is bytes. Budget accordingly:

    1600px wide, WebP q97  ->  ~170 KB/frame  (~6 MB for 36 frames)
    1920px wide, WebP lossless -> ~550 KB/frame (~20 MB for 36 frames)

36 frames at 24 fps is a 1.5s loop; 48 is 2s. Most flow animations read fine at
1.5s.

Hard-won details, each of which produced a broken deliverable at least once
----------------------------------------------------------------------------
1. INLINE EVERYTHING. A page that loads sibling .js files shows a black canvas
   in any viewer that renders the HTML alone. One file, no dependencies.

2. CAP DPR AT 1. If you render 1600px frames and then let the canvas scale by
   devicePixelRatio, you are upscaling: it can only interpolate, never add
   detail, and the result reads as "blurry" next to the stills. Blit 1:1.

3. PROVIDE A DETERMINISTIC STILL MODE. Headless screenshots of a
   requestAnimationFrame loop come back blank because rAF does not advance
   under a virtual clock. `?still=1&frame=0` must paint one frame synchronously.

4. NEVER PASS A QUERY STRING THROUGH A SHELL UNESCAPED. `?still=1&v=A` becomes
   `?still=1` plus a background command in PowerShell, and you end up
   screenshotting the browser's DNS error page while believing you verified the
   app. Bake the parameters into a temp copy instead.

5. SURFACE ERRORS VISIBLY. A thrown error leaves a black rectangle and no clue.
   Catch it and paint it into the page.
"""
from __future__ import annotations

import base64
import io
import json
import os
from typing import Callable, Dict, List, Optional


_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; background: #04070c; overflow: hidden; }
  body { display: flex; flex-direction: column;
         font-family: ui-monospace, Menlo, Consolas, monospace; }
  #main { flex: 1 1 auto; min-height: 0; display: flex; align-items: stretch; }
  #wrap { flex: 1 1 auto; min-width: 0; display: flex;
          align-items: center; justify-content: center; overflow: hidden; }
  canvas { display: block; }

  #side { flex: 0 0 260px; display: none; flex-direction: column; gap: 10px;
          padding: 14px; overflow: hidden; font-size: 11.5px; color: #8fb3c7; }
  #side.on { display: flex; }
  .card { border: 1px solid #172a35; border-radius: 8px; padding: 9px 11px;
          background: rgba(7,13,20,.72); }
  .card h4 { margin: 0 0 7px; font-size: 10.5px; font-weight: 600;
             letter-spacing: .09em; color: #5f8499; text-transform: uppercase; }
  .row { display: flex; justify-content: space-between; margin: 3px 0; }
  .row b { color: #cfe6f2; font-weight: 600; font-variant-numeric: tabular-nums; }
  .bar { height: 3px; border-radius: 2px; background: #16232c; margin: 3px 0 7px; }
  .bar i { display: block; height: 100%; border-radius: 2px; background: #4fc9ff;
           transition: width .18s linear; }
  .tiny { font-size: 10px; color: #56758a; }

  #bar { flex: 0 0 auto; height: 46px; display: flex; align-items: center;
         gap: 10px; padding: 0 14px; background: #070d14;
         border-top: 1px solid #16262f; font-size: 12px; color: #7d9fb2;
         user-select: none; }
  .btn { padding: 6px 14px; border: 1px solid #24404f; border-radius: 7px;
         background: #0a141d; color: #7fa4ba; cursor: pointer; font: inherit; }
  .btn:hover { border-color: #3d6a80; color: #b9d6e4; }
  .btn.on { border-color: #5bd0ff; color: #d6f4ff; background: #0d2231; }
  /* 44px minimum hit target per ui-acceptance */
  #spd { -webkit-appearance: none; appearance: none; width: 160px; height: 44px;
         background: transparent; cursor: pointer; }
  #spd::-webkit-slider-runnable-track { height: 4px; border-radius: 2px;
         background: #1c323e; }
  #spd::-webkit-slider-thumb { -webkit-appearance: none; width: 16px; height: 16px;
         margin-top: -6px; border-radius: 50%; background: #d6f4ff;
         border: 1px solid #5bd0ff; }
  #fps { margin-left: auto; opacity: .8; }
  #err { position: fixed; inset: 0; display: none; padding: 34px 40px;
         background: #0b0f14; color: #ff9d8a; font-size: 13px;
         white-space: pre-wrap; overflow: auto; z-index: 99; }
</style>
</head>
<body>
<div id="main">
  <div id="wrap"><canvas id="c"></canvas></div>
  <div id="side">__SIDE__</div>
</div>
<div id="bar">
  <button class="btn" id="bpause">pause</button>
  <input type="range" id="spd" min="0.25" max="3" step="0.05" value="1">
  <b id="spdv">1.00x</b>
  <span style="opacity:.7">space pause &nbsp; &larr;&rarr; speed</span>
  <span id="fps"></span>
</div>
<div id="err"></div>
<script>
var FRAMES = __FRAMES__;
var STATE = __STATE__;
var FW = __W__, FH = __H__;
(function () {
  "use strict";
  var errBox = document.getElementById("err");
  function fatal(m) {
    errBox.style.display = "block";
    errBox.textContent = "render failed\\n\\n" + String(m);
  }
  window.addEventListener("error", function (e) {
    fatal((e.message || "unknown") + "\\n" + (e.filename || "") + ":" + (e.lineno || ""));
  });
  try {
    if (!FRAMES || !FRAMES.length) throw new Error("no frames embedded");
    var cv = document.getElementById("c");
    var ctx = cv.getContext("2d", { alpha: false });
    var sideEl = document.getElementById("side");

    // Cap DPR at 1: frames are already rendered at target resolution, so extra
    // device pixels can only interpolate. Upscaling is what "blurry" means.
    var DPR = 1;

    function resize() {
      var main = document.getElementById("main");
      var wrap = document.getElementById("wrap");
      var totalW = window.innerWidth || main.clientWidth;
      var totalH = main.clientHeight || (window.innerHeight - 46);
      var SIDE_W = 260;
      var wantSide = (totalW - SIDE_W) >= 760;
      sideEl.className = wantSide ? "on" : "";
      var aw = Math.max(320, (wrap.clientWidth || (totalW - (wantSide ? SIDE_W : 0))) - 10);
      var ah = Math.max(200, totalH - 10);
      var sc = Math.min(aw / FW, ah / FH);
      var cssW = Math.round(FW * sc), cssH = Math.round(FH * sc);
      cv.width = Math.round(cssW * DPR);
      cv.height = Math.round(cssH * DPR);
      cv.style.width = cssW + "px";
      cv.style.height = cssH + "px";
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
      ctx.imageSmoothingQuality = "high";
    }
    resize();
    window.addEventListener("resize", resize);

    var imgs = [], loaded = 0;
    for (var i = 0; i < FRAMES.length; i++) {
      (function (idx) {
        var im = new Image();
        im.onload = function () { if (++loaded === FRAMES.length) start(); };
        im.onerror = function () { fatal("frame " + idx + " failed to decode"); };
        im.src = "data:image/webp;base64," + FRAMES[idx];
        imgs[idx] = im;
      })(i);
    }

    var idx = 0, paused = false, speed = 1, last = 0, acc = 0;
    var FPS = __FPS__;
    var bpause = document.getElementById("bpause");
    var spd = document.getElementById("spd");
    var spdv = document.getElementById("spdv");
    var fpsEl = document.getElementById("fps");

    function setPaused(p) {
      paused = p;
      bpause.textContent = p ? "resume" : "pause";
      bpause.className = "btn" + (p ? " on" : "");
    }
    function setSpeed(v) {
      speed = Math.max(0.25, Math.min(3, v));
      spd.value = speed;
      spdv.textContent = speed.toFixed(2) + "x";
    }
    bpause.onclick = function () { setPaused(!paused); };
    spd.addEventListener("input", function () { setSpeed(parseFloat(spd.value)); });
    window.addEventListener("keydown", function (e) {
      if (e.code === "Space") { setPaused(!paused); e.preventDefault(); }
      else if (e.code === "ArrowRight") setSpeed(speed + 0.25);
      else if (e.code === "ArrowLeft") setSpeed(speed - 0.25);
    });

    // ---- telemetry: only changes that actually differ are written.
    // Per ui-acceptance, a counter that re-renders every frame reads as noise.
    var lastWritten = {};
    function setTxt(id, v) {
      var s = String(v);
      if (lastWritten[id] === s) return;
      lastWritten[id] = s;
      var el = document.getElementById(id);
      if (el) el.textContent = s;
    }
    function setBar(id, pct) {
      pct = Math.max(0, Math.min(100, pct)).toFixed(1);
      if (lastWritten[id] === pct) return;
      lastWritten[id] = pct;
      var el = document.getElementById(id);
      if (el) el.style.width = pct + "%";
    }
    function updatePanel(i) {
      var st = STATE && STATE[i];
      if (!st) return;
      for (var k in st.text) setTxt(k, st.text[k]);
      for (var b in st.bars) setBar(b, st.bars[b]);
    }

    function paint(i) {
      ctx.clearRect(0, 0, cv.width / DPR, cv.height / DPR);
      if (imgs[i] && imgs[i].complete) {
        ctx.drawImage(imgs[i], 0, 0, cv.width / DPR, cv.height / DPR);
      }
      if (sideEl.className === "on") updatePanel(i);
    }

    // deterministic still mode for headless verification:
    //   ?still=1&frame=0
    var qs = new URLSearchParams(location.search);
    if (qs.get("still") === "1") {
      var f = parseInt(qs.get("frame") || "0", 10) | 0;
      var show = function () {
        paint(f);
        if (window.__PHOTONFLOW_STILL__ !== undefined) window.__PHOTONFLOW_STILL__ = f;
      };
      if (loaded === FRAMES.length) show();
      else {
        var poll = setInterval(function () {
          if (loaded === FRAMES.length) { clearInterval(poll); show(); }
        }, 20);
      }
      return;
    }

    function start() { last = performance.now(); requestAnimationFrame(tick); }
    function tick(now) {
      var raw = (now - last) / 1000; last = now;
      if (!(raw > 0)) raw = 1 / FPS;
      if (!paused) {
        acc += raw * speed;
        var step = 1 / FPS;
        while (acc >= step) { acc -= step; idx = (idx + 1) % imgs.length; }
      }
      paint(idx);
      fpsEl.textContent = Math.round(1 / raw) + " fps · " + (idx + 1) + "/" + imgs.length;
      requestAnimationFrame(tick);
    }
  } catch (e) { fatal(e && e.stack ? e.stack : e); }
})();
</script>
</body>
</html>
"""


def _side_html(cards: List[Dict]) -> str:
    """cards: [{"title": str, "rows": [{"label","id","unit"}], "bars": [{...}]}]"""
    out = []
    for c in cards:
        out.append('<div class="card"><h4>%s</h4>' % c["title"])
        for r in c.get("rows", []):
            out.append('<div class="row"><span>%s</span><b id="%s">%s</b></div>'
                       % (r["label"], r["id"], r.get("initial", "")))
        for b in c.get("bars", []):
            out.append('<div class="bar"><i id="%s" style="width:0%%;background:%s"></i></div>'
                       % (b["id"], b.get("colour", "#4fc9ff")))
        out.append("</div>")
    return "".join(out)


def bake(
    frames: List["object"],
    out_path: str,
    state: Optional[List[Dict]] = None,
    side_cards: Optional[List[Dict]] = None,
    width: int = 1600,
    height: int = 900,
    fps: int = 24,
    title: str = "photon flow",
    quality: int = 97,
    lossless: bool = False,
) -> str:
    """
    Write a single self-contained player.

    frames      PIL images, already rendered at `width`
    state       optional per-frame telemetry:
                [{"text": {"id": "value"}, "bars": {"id": percent}}, ...]
    side_cards  optional panel layout for the telemetry column
    """
    encoded = []
    for im in frames:
        b = io.BytesIO()
        im.save(b, format="WEBP", quality=quality, lossless=lossless, method=6)
        encoded.append(base64.b64encode(b.getvalue()).decode("ascii"))

    payload = "[" + ",".join('"%s"' % e for e in encoded) + "]"
    state_js = json.dumps(state or [], separators=(",", ":"))
    side = _side_html(side_cards or [])

    html = (_TPL
            .replace("__TITLE__", title)
            .replace("__SIDE__", side)
            .replace("__FRAMES__", payload)
            .replace("__STATE__", state_js)
            .replace("__W__", str(width))
            .replace("__H__", str(height))
            .replace("__FPS__", str(fps)))

    d = os.path.dirname(os.path.abspath(out_path))
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path
