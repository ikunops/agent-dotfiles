# -*- coding: utf-8 -*-
"""
chrome.py — text and structure drawn ON TOP of the light.

`scene.render()` deliberately only produces light. Labels, frames and titles are
drawn afterwards, crisp, because bloom would otherwise eat them.

Two rules, learned the hard way:

1. Draw chrome AFTER tone-mapping, directly on the RGB image. Text rendered into
   the light buffer comes out looking etched into fog.

2. Anything that can be specified as data should be. `Scene.title`,
   `Node.label` and `Lane.ends_at` exist so that no scene file has to contain
   pixel offsets for text.
"""
from __future__ import annotations

import os
from typing import Optional, Sequence

from PIL import Image, ImageDraw, ImageFont

_FD = r"C:\Windows\Fonts"


def _font(size: int, bold: bool = False, mono: bool = False):
    """Best-effort font pick that works on Windows and degrades gracefully."""
    size = int(max(8, size))
    if mono:
        cands = ["consolab.ttf" if bold else "consola.ttf"]
    else:
        cands = ["msyhbd.ttc", "msyh.ttc", "segoeuib.ttf", "arialbd.ttf"] if bold \
            else ["msyh.ttc", "segoeui.ttf", "arial.ttf"]
    for c in cands:
        p = os.path.join(_FD, c)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def rgba(col, a=1.0):
    """Colour tuple 0..1 -> PIL RGBA 0..255."""
    return (int(min(255, col[0] * 255)), int(min(255, col[1] * 255)),
            int(min(255, col[2] * 255)), int(max(0.0, min(1.0, a)) * 255))


def draw_text(img: Image.Image, xy, text, size=12, colour=(1, 1, 1),
              alpha=1.0, anchor="la", bold=False, mono=True, shadow=True):
    """Text with an optional dark halo so it stays legible over bright light."""
    d = ImageDraw.Draw(img, "RGBA")
    f = _font(size, bold=bold, mono=mono)
    if shadow:
        d.text((xy[0] + 1, xy[1] + 1), text, font=f, anchor=anchor,
               fill=(0, 0, 0, int(alpha * 150)))
    d.text(xy, text, font=f, anchor=anchor, fill=rgba(colour, alpha))


def frame_nodes(img: Image.Image, sc, scale: float = 1.0,
                show_units: bool = True) -> None:
    """Draw each node's outline frame and its label."""
    d = ImageDraw.Draw(img, "RGBA")
    for n in sc.nodes:
        col = n.resolved_colour()
        if n.box is not None:
            x0, y0, x1, y1 = [v * scale for v in n.box]
            d.rounded_rectangle([x0, y0, x1, y1], radius=int(8 * scale),
                                fill=(6, 11, 19, 110),
                                outline=rgba(col, 0.55),
                                width=max(1, int(1.4 * scale)))
            # accent: a short tick at the left edge, NOT a full-length colour bar
            # (create-design-system: exhausted motif). The tick marks the
            # connection point so lanes visibly land somewhere.
            cy = (y0 + y1) * 0.5
            d.line([(x0, cy - 9 * scale), (x0, cy + 9 * scale)],
                   fill=rgba(col, 0.95), width=max(2, int(3 * scale)))
            if n.label:
                draw_text(img, (x0 + 12 * scale, y0 + 8 * scale), n.label,
                          size=13 * scale, colour=col, alpha=0.95, bold=True)
        else:
            r = n.r * scale
            cx, cy = n.x * scale, n.y * scale
            d.ellipse([cx - r, cy - r, cx + r, cy + r],
                      outline=rgba(col, 0.60), width=max(1, int(2 * scale)))
            if n.label:
                draw_text(img, (cx, cy + r + 10 * scale), n.label,
                          size=13 * scale, colour=col, alpha=0.95,
                          anchor="ma")


def draw_title(img: Image.Image, sc, scale: float = 1.0) -> None:
    if sc.title:
        draw_text(img, (28 * scale, 22 * scale), sc.title,
                  size=24 * scale, colour=(0.95, 0.98, 1.0), alpha=1.0,
                  bold=True, mono=False)
    if sc.subtitle:
        draw_text(img, (28 * scale, 52 * scale), sc.subtitle,
                  size=12 * scale, colour=(0.52, 0.68, 0.78), alpha=1.0,
                  mono=False)


def compose(sc, light_img: Image.Image, scale: float = 1.0) -> Image.Image:
    """Light image -> finished frame with chrome."""
    out = light_img.convert("RGB")
    frame_nodes(out, sc, scale=scale)
    draw_title(out, sc, scale=scale)
    return out
