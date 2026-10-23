# -*- coding: utf-8 -*-
"""
Lane endpoint verification.

WHY THIS EXISTS
---------------
Three separate bugs in the reference project had the same root cause: a lane's
terminal coordinate was written as a literal pixel value, and when the layout
moved (cards relocated, a new upstream added) the lane kept pointing at the old
spot. The renderer happily drew a bright streak into empty space, and the only
symptom was a viewer asking "what is that line connected to?"

No amount of staring at the output catches this reliably. Measuring does.

USAGE
-----
    import audit
    problems = audit.verify(nodes, lanes)
    if problems:
        for p in problems:
            print(p)
        raise SystemExit("lanes do not land on nodes; do not render yet")

`nodes` and `lanes` are plain data:

    nodes = [
        audit.Node("nginx",   x=800, y=450, r=102),          # circle
        audit.Node("app-01",  box=(1288, 107, 1538, 189)),   # rectangle
    ]
    lanes = [
        audit.Lane("port0->app-01", points=[(877,383), (1000,120), (1294,148)]),
    ]

`points` is the bezier control polygon; the lane's endpoints are its first and
last control points, which is what the renderer uses.

TOLERANCE
---------
A lane may terminate anywhere ON a node's surface, not at its centre. Distance
is therefore measured to the node's boundary, and anything beyond `tol` is a
problem. The default 8px is deliberate: it is small enough that a 20px orphan
is caught, large enough that a lane touching a ring at 40 degrees is not
flagged for being 1px off the arc.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple

Point = Tuple[float, float]


@dataclass
class Node:
    """A drawable node. Supply either `box` (rectangle) or x/y/r (circle)."""

    name: str
    x: float = 0.0
    y: float = 0.0
    r: float = 0.0
    box: Optional[Tuple[float, float, float, float]] = None  # x0, y0, x1, y1

    def distance_to_surface(self, p: Point) -> float:
        if self.box is not None:
            x0, y0, x1, y1 = self.box
            dx = max(x0 - p[0], 0.0, p[0] - x1)
            dy = max(y0 - p[1], 0.0, p[1] - y1)
            return math.hypot(dx, dy)
        return max(0.0, math.hypot(p[0] - self.x, p[1] - self.y) - self.r)


@dataclass
class Lane:
    """A route. `points` is the bezier control polygon."""

    name: str
    points: Sequence[Point]
    interior: bool = False
    """True for lanes that legitimately end inside a node's body (a hairpin
    that bounces off a cache glyph, a deny stub absorbed at the core). Interior
    lanes are only checked against the node they declare via `ends_at`."""

    ends_at: Optional[str] = None
    """Optional: assert this lane ends on the NAMED node specifically, rather
    than merely landing on *some* node."""

    def start(self) -> Point:
        return tuple(self.points[0])

    def end(self) -> Point:
        return tuple(self.points[-1])


@dataclass
class Problem:
    lane: str
    which: str          # "start" | "end"
    point: Point
    nearest: str
    gap: float

    def __str__(self) -> str:
        return (
            "%-28s %s at (%.0f, %.0f) is %.1fpx from %s"
            % (self.lane, self.which, self.point[0], self.point[1],
               self.gap, self.nearest)
        )


def _nearest(p: Point, nodes: Iterable[Node]) -> Tuple[str, float]:
    best = ("(none)", float("inf"))
    for n in nodes:
        d = n.distance_to_surface(p)
        if d < best[1]:
            best = (n.name, d)
    return best


def verify(nodes: Sequence[Node], lanes: Sequence[Lane], tol: float = 8.0
           ) -> List[Problem]:
    """Return every lane endpoint that does not land on a node surface."""
    problems: List[Problem] = []
    by_name = {n.name: n for n in nodes}

    for lane in lanes:
        for which, p in (("start", lane.start()), ("end", lane.end())):
            if lane.ends_at and which == "end":
                node = by_name.get(lane.ends_at)
                if node is None:
                    problems.append(Problem(lane.name, which, p,
                                            "MISSING NODE " + lane.ends_at,
                                            float("inf")))
                    continue
                gap = node.distance_to_surface(p)
                if gap > tol:
                    problems.append(Problem(lane.name, which, p,
                                            node.name, gap))
                continue

            name, gap = _nearest(p, nodes)
            if gap > tol:
                problems.append(Problem(lane.name, which, p, name, gap))

    return problems


def report(nodes: Sequence[Node], lanes: Sequence[Lane], tol: float = 8.0
           ) -> str:
    """Human-readable table, for pasting into a review note."""
    rows = []
    problems = verify(nodes, lanes, tol)
    bad = {(p.lane, p.which) for p in problems}
    for lane in lanes:
        for which, p in (("start", lane.start()), ("end", lane.end())):
            name, gap = _nearest(p, nodes)
            flag = " <<< DANGLING" if (lane.name, which) in bad else ""
            rows.append(
                "%-28s %-5s (%5.0f,%4.0f)  %-14s %6.1f%s"
                % (lane.name, which, p[0], p[1], name, gap, flag)
            )
    head = "%-28s %-5s %-16s %-14s %6s" % ("lane", "end", "point", "nearest", "gap")
    tail = ("\nDANGLING: %d" % len(problems)) if problems else \
           "\nOK: every lane endpoint lands on a node surface"
    return "\n".join([head, "-" * 78] + rows + [tail])
