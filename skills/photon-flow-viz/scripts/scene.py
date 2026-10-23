# -*- coding: utf-8 -*-
"""
scene.py — the minimal contract a scene must satisfy.

A scene is plain data plus one render function. Keeping it data means it can be
audited (`audit.verify`) and diffed without running the renderer.

    from photonflow import scene, audit, fibre

    S = scene.Scene(
        nodes=[
            scene.Node("browsers", role="client", y=216, colour=(0.42,0.71,1.0)),
            scene.Node("nginx",    role="core",   x=800, y=450, r=102),
            scene.Node("app-01",   role="sink",   y=148, colour=(0.30,1.00,0.72)),
        ],
        lanes=[
            scene.Lane("browsers->nginx", [(138,216),(312,450),(560,462),(698,450)]),
            scene.Lane("nginx->app-01",   [(877,383),(970,300),(1014,148),(1288,148)]),
        ],
    )

Then `scene.render(S, phase=0.0)` gives you a PIL image.

Geometry helpers exist so you never hand-write a terminal coordinate:
    scene.ring_point(cx, cy, r, deg)     a point on a node's ring
    scene.box_left(box, frac=0.5)        the left edge of a card, vertically placed
    scene.lerp(a, b, t)                  interpolation
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

# Make sibling modules importable no matter where this file is invoked from.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

Point = Tuple[float, float]

# ------------------------------------------------------------------ palette
# Roles, not raw colours. A scene names the role; the module supplies the hue.
ROLE_COLOURS: Dict[str, Tuple[float, float, float]] = {
    "client":  (0.42, 0.71, 1.00),
    "core":    (0.20, 0.71, 1.00),
    "sink":    (0.30, 1.00, 0.72),
    "cache":   (0.43, 1.00, 0.93),
    "reject":  (1.00, 0.38, 0.30),
    "retry":   (1.00, 0.70, 0.26),
    "filter":  (0.58, 0.62, 0.68),
    "persist": (0.78, 0.96, 1.00),
}


# ------------------------------------------------------------------ geometry
def ring_point(cx: float, cy: float, r: float, deg: float) -> Point:
    """A point on a circle. Use this for lane terminals on ring-shaped nodes."""
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def box_left(box: Tuple[float, float, float, float], frac: float = 0.5) -> Point:
    """The left edge of a rectangle, at vertical fraction `frac` (0=top,1=bottom)."""
    x0, y0, x1, y1 = box
    return (x0, y0 + (y1 - y0) * frac)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp2(p: Point, q: Point, t: float) -> Point:
    return (lerp(p[0], q[0], t), lerp(p[1], q[1], t))


# ------------------------------------------------------------------ data
@dataclass
class Node:
    """A participant in the flow: client group, core, or sink."""

    name: str
    role: str = "sink"
    x: float = 0.0
    y: float = 0.0
    r: float = 0.0
    box: Optional[Tuple[float, float, float, float]] = None
    colour: Optional[Tuple[float, float, float]] = None
    label: str = ""

    def resolved_colour(self) -> Tuple[float, float, float]:
        if self.colour is not None:
            return self.colour
        return ROLE_COLOURS.get(self.role, ROLE_COLOURS["sink"])

    def centre(self) -> Point:
        if self.box is not None:
            x0, y0, x1, y1 = self.box
            return ((x0 + x1) * 0.5, (y0 + y1) * 0.5)
        return (self.x, self.y)

    def to_audit(self):
        import audit
        if self.box is not None:
            return audit.Node(self.name, box=self.box)
        return audit.Node(self.name, x=self.x, y=self.y, r=self.r)


@dataclass
class Lane:
    """A route between two nodes. `points` is a cubic bezier control polygon."""

    name: str
    points: Sequence[Point]
    style: str = "pulse"
    """Particle grammar: pulse | missile | clump | bead (see fibre.STYLE_PRESETS)."""

    ends_at: Optional[str] = None
    interior: bool = False
    amp: float = 0.075
    strands: int = 8
    spread: float = 18.0
    env: str = "tight"
    """Bundle envelope: tight (gather-spread-gather) | flat | open."""

    def colour(self, nodes: Sequence[Node]) -> Tuple[float, float, float]:
        for n in nodes:
            if n.name == self.ends_at:
                return n.resolved_colour()
        return ROLE_COLOURS["core"]

    def to_audit(self):
        import audit
        return audit.Lane(self.name, self.points,
                          interior=self.interior, ends_at=self.ends_at)


@dataclass
class Scene:
    """Everything needed to draw, and nothing that requires drawing to inspect."""

    nodes: List[Node] = field(default_factory=list)
    lanes: List[Lane] = field(default_factory=list)
    width: int = 1600
    height: int = 900
    title: str = ""
    subtitle: str = ""

    def audit_nodes(self):
        return [n.to_audit() for n in self.nodes]

    def audit_lanes(self):
        return [l.to_audit() for l in self.lanes]

    def verify(self, tol: float = 8.0):
        import audit
        return audit.verify(self.audit_nodes(), self.audit_lanes(), tol=tol)

    def audit_report(self, tol: float = 8.0) -> str:
        import audit
        return audit.report(self.audit_nodes(), self.audit_lanes(), tol=tol)


# ------------------------------------------------------------------ render
def render(sc: Scene, phase: float = 0.0, ssamp: float = 2.0,
           out_width: Optional[int] = None, seed: int = 7,
           bg_tint: Tuple[float, float, float] = (0.0, 0.0, 0.014)):
    """
    Draw the scene at `phase` (0..1 through one loop) and return a PIL image.

    Fails loudly if any lane does not land on a node: rendering a disconnected
    lane is worse than not rendering, because it looks like a bug in the system
    being described rather than a bug in the drawing.
    """
    import numpy as np
    from PIL import Image
    import fibre as F

    problems = sc.verify()
    if problems:
        msg = "\\n".join("  " + str(p) for p in problems)
        raise ValueError(
            "lanes do not land on nodes -- fix geometry before rendering:\\n" + msg)

    out_width = out_width or sc.width
    s = (out_width / float(sc.width)) * ssamp
    W = int(round(sc.width * s))
    H = int(round(sc.height * s))
    buf = np.zeros((H, W, 3), np.float32)
    rng = np.random.default_rng(seed)

    for i, lane in enumerate(sc.lanes):
        col = lane.colour(sc.nodes)
        F.route_styled(
            buf, s, list(lane.points), col,
            phase=phase + 0.11 * i, rng=rng,
            style=lane.style,
            nfib=lane.strands, spread=lane.spread, fib_amp=lane.amp,
            wob=2.2, freq=1.4, grow=1.2, steps=640,
            packets=2, packet_w=0.07, env=lane.env,
        )

    light = F.bloom(buf, s, scales=(1.8, 5.5, 17.0), weights=(0.44, 0.20, 0.10))
    bg = np.zeros((H, W, 3), np.float32)
    bg[..., 0] += bg_tint[0]
    bg[..., 1] += bg_tint[1]
    bg[..., 2] += bg_tint[2]
    img = Image.fromarray(F.tonemap(light, gain=2.1, bg=bg), "RGB")
    img = img.resize((int(out_width),
                      int(round(out_width * sc.height / sc.width))),
                     Image.LANCZOS)

    # chrome is drawn AFTER tone mapping so bloom cannot eat the text
    import chrome
    return chrome.compose(sc, img, scale=out_width / float(sc.width))
