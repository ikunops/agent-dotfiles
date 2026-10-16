import React from "react";
import { createRoot } from "react-dom/client";
import { Player } from "@remotion/player";
import { FILMS } from "../../src/films";

const params = new URLSearchParams(location.search);
const id = params.get("id") || "Zeno";
const film = FILMS.find((f) => f.id === id);
if (!film) throw new Error("unknown film " + id);

let player: { seekTo: (f: number) => void } | null = null;

const App: React.FC = () => (
  <Player
    ref={(r) => {
      player = r as unknown as { seekTo: (f: number) => void };
    }}
    component={film.component}
    durationInFrames={film.frames}
    compositionWidth={1920}
    compositionHeight={1080}
    fps={30}
    style={{ width: 1920, height: 1080 }}
    controls={false}
    autoPlay={false}
    acknowledgeRemotionLicense
  />
);

const host = document.getElementById("video-container") || document.body;
const mount = document.createElement("div");
mount.id = "harness-root";
host.appendChild(mount);
createRoot(mount).render(<App />);

const w = window as unknown as {
  __seek: (f: number) => void;
  __ready: () => boolean;
  __film: unknown;
  __measure: () => unknown;
};

w.__seek = (f) => player?.seekTo(f);
w.__ready = () => !!document.querySelector("#harness-root svg");
w.__film = { id: film.id, frames: film.frames };

// 量测：文字用包围盒；主体重叠用「真实像素命中测试」（非包围盒）
w.__measure = () => {
  const W = 1920, H = 1080;
  const svg = document.querySelector("#harness-root svg") as SVGSVGElement | null;
  if (!svg) return { texts: [], figs: [], W, H };
  const rb = svg.getBoundingClientRect();
  const kx = W / (rb.width || W), ky = H / (rb.height || H);
  const toScreen = (r: DOMRect) => ({
    x: (r.left - rb.left) * kx, y: (r.top - rb.top) * ky,
    w: r.width * kx, h: r.height * ky,
  });
  const effOp = (el: Element): number => {
    let o = 1, n: Element | null = el;
    while (n && n !== svg) {
      const s = getComputedStyle(n as Element);
      if (s.display === "none" || s.visibility === "hidden") return 0;
      o *= parseFloat(s.opacity || "1");
      n = n.parentElement;
    }
    return o;
  };

  const textNodes = [...svg.querySelectorAll("text")] as SVGTextElement[];
  const texts = textNodes.map((t) => {
    const r = t.getBoundingClientRect();
    return { s: (t.textContent || "").trim(), op: effOp(t), ...toScreen(r) };
  }).filter((t) => t.s.length > 0 && t.op > 0.02);

  const figEls = [...svg.querySelectorAll("[data-fig]")] as SVGGraphicsElement[];
  const figs = figEls.map((g) => ({
    name: (g as unknown as HTMLElement).dataset.fig || "fig", ...toScreen(g.getBoundingClientRect()),
  }));

  // 真实命中：全局 pointer-events:none，只给主体开放；在文字框内采样点做 elementFromPoint
  const prevRoot = svg.style.pointerEvents;
  const prevFig = figEls.map((f) => f.style.pointerEvents);
  svg.style.pointerEvents = "none";
  figEls.forEach((f) => { f.style.pointerEvents = "auto"; });

  const COLS = 9, ROWS = 5;
  for (const t of texts) {
    let hits = 0, total = 0, name: string | null = null;
    for (let i = 1; i < COLS; i++) {
      for (let j = 1; j < ROWS; j++) {
        const sx = t.x + (t.w * i) / COLS;
        const sy = t.y + (t.h * j) / ROWS;
        const cx = rb.left + sx / kx;
        const cy = rb.top + sy / ky;
        const el = document.elementFromPoint(cx, cy);
        total++;
        if (el && (el as Element).closest("[data-fig]")) {
          hits++;
          if (!name) name = ((el as Element).closest("[data-fig]") as unknown as HTMLElement).dataset.fig || "fig";
        }
      }
    }
    (t as unknown as { hit: string | null; frac: number }).hit = name;
    (t as unknown as { hit: string | null; frac: number }).frac = total ? hits / total : 0;
    void 0;
  }

  svg.style.pointerEvents = prevRoot;
  figEls.forEach((f, i) => { f.style.pointerEvents = prevFig[i]; });

  return { texts, figs, W, H };
};
