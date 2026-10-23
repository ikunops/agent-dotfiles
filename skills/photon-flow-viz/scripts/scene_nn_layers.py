# -*- coding: utf-8 -*-
"""
scene_nn_layers.py — neural-network activation flow.

This is the reuse test: it uses the same kernel as the nginx scene but shares no
geometry, no roles, and no lane table with it. If this renders correctly, the
package generalises.

What it depicts: a forward pass through five layers of a small MLP. Clients never
appear — the "traffic" is activation values propagating layer to layer. Because
activations are thousands of tiny concurrent things rather than discrete
requests, the grammar is `clump`, not `pulse`.

    L0 input (784) -> L1 (256) -> L2 (128) -> L3 (64) -> L4 output (10)

Plus a dropout path that kills a fraction of connections (drawn as `filter`),
and a residual skip connection that bypasses L2 (drawn as `persist`, always on).
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import scene as S


# ------------------------------------------------------------------ layout
W, H = 1600, 900
COLS = [200.0, 480.0, 760.0, 1040.0, 1320.0]
LAYERS = [
    ("input",  784, "clump"),
    ("fc1",    256, "clump"),
    ("fc2",    128, "clump"),
    ("fc3",     64, "clump"),
    ("output",  10, "bead"),
]
NODE_H = 210.0
CENTRE_Y = 450.0


def layer_node(i: int) -> S.Node:
    """Each layer is a tall rounded slab; name carries the unit count."""
    name, units, _style = LAYERS[i]
    x = COLS[i]
    top = CENTRE_Y - NODE_H / 2
    bot = CENTRE_Y + NODE_H / 2
    role = "client" if i == 0 else ("reject" if i == len(LAYERS) - 1 else "core")
    return S.Node(
        name=name,
        role=role,
        box=(x - 34.0, top, x + 34.0, bot),
        label="%s  (%d)" % (name, units),
    )


def lane_points(i: int, j_from: float, j_to: float):
    """A bezier from column i to column i+1, fanned vertically."""
    x0 = COLS[i] + 34.0
    x1 = COLS[i + 1] - 34.0
    y0 = CENTRE_Y + (j_from - 0.5) * NODE_H * 0.82
    y1 = CENTRE_Y + (j_to - 0.5) * NODE_H * 0.82
    mx = (x0 + x1) * 0.5
    return [
        (x0, y0),
        (mx, y0 + (y1 - y0) * 0.22),
        (mx, y1 - (y1 - y0) * 0.22),
        (x1, y1),
    ]


def build(fan: int = 9) -> S.Scene:
    nodes = [layer_node(i) for i in range(len(LAYERS))]
    lanes = []

    # forward connections, fanned so the bundle reads as dense throughput
    for i in range(len(LAYERS) - 1):
        for k in range(fan):
            frac_from = (k + 0.5) / fan
            frac_to = ((k * 7) % fan + 0.5) / fan     # deterministic fan-in
            lanes.append(S.Lane(
                "L%d->L%d_%02d" % (i, i + 1, k),
                lane_points(i, frac_from, frac_to),
                style="clump",
                ends_at=LAYERS[i + 1][0],
                amp=0.055,
                strands=5,
                spread=10.0,
                env="tight",
            ))

    # residual skip: L1 -> L3, always connected, drawn as a persistent rail
    lanes.append(S.Lane(
        "residual_L1->L3",
        [(COLS[1] + 34.0, CENTRE_Y - NODE_H * 0.46),
         (700.0, CENTRE_Y - NODE_H * 0.78),
         (900.0, CENTRE_Y - NODE_H * 0.78),
         (COLS[3] - 34.0, CENTRE_Y - NODE_H * 0.46)],
        style="pulse",
        ends_at="fc3",
        amp=0.075,
        strands=7,
        spread=14.0,
        env="flat",
    ))

    # dropout: a few connections that terminate early (killed units)
    for k in range(3):
        fy = 0.72 + k * 0.09
        lanes.append(S.Lane(
            "dropout_%d" % k,
            [(COLS[2] + 34.0, CENTRE_Y + (fy - 0.5) * NODE_H * 0.82),
             (830.0, CENTRE_Y + NODE_H * 0.52),
             (872.0, CENTRE_Y + NODE_H * 0.60),
             (COLS[4] - 34.0, CENTRE_Y + NODE_H * 0.42)],
            style="bead",
            ends_at="output",
            amp=0.040,
            strands=3,
            spread=7.0,
            env="tight",
        ))

    return S.Scene(
        nodes=nodes,
        lanes=lanes,
        width=W,
        height=H,
        title="MLP FORWARD PASS",
        subtitle="784 -> 256 -> 128 -> 64 -> 10   ·   activation as light",
    )


if __name__ == "__main__":
    sc = build()
    print(sc.audit_report())
    problems = sc.verify()
    if problems:
        raise SystemExit("fix geometry first")

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_out")
    os.makedirs(out_dir, exist_ok=True)
    for i, ph in enumerate((0.0, 0.35, 0.7)):
        img = sc and S.render(sc, phase=ph, out_width=1280)
        p = os.path.join(out_dir, "nn_%d.png" % i)
        img.save(p)
        print("wrote", p)
