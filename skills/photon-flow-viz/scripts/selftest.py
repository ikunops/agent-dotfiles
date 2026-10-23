# -*- coding: utf-8 -*-
"""
Smoke test for the whole package: build a scene, audit it, render frames, bake a
player. Run this after touching anything in scripts/.

    python scripts/selftest.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import scene as S
import scene_nn_layers as NN
import web
import audit


def main():
    # 1. geometry must audit clean
    sc = NN.build()
    problems = sc.verify()
    if problems:
        print(sc.audit_report())
        raise SystemExit("FAIL: lanes do not land on nodes")
    print("PASS audit: every lane endpoint lands on a node")

    # 2. the audit must also CATCH a bad lane (guard against a no-op check)
    broken = S.Scene(
        nodes=[S.Node("a", box=(0, 0, 100, 100)),
               S.Node("b", box=(400, 0, 500, 100))],
        lanes=[S.Lane("orphan", [(50, 50), (200, 20), (300, 20), (900, 900)])],
    )
    if not broken.verify():
        raise SystemExit("FAIL: audit did not catch a deliberately dangling lane")
    print("PASS audit: catches a dangling lane")

    # 3. render a few frames
    frames = []
    for i in range(6):
        frames.append(S.render(sc, phase=i / 6.0, out_width=960))
    print("PASS render: %d frames at %dx%d" % (len(frames), *frames[0].size))

    # 4. bake a player and check it is self-contained
    out = os.path.join(HERE, "_out", "selftest.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    html = web.bake(frames, out, width=960, height=540, fps=12,
                    title="selftest",
                    state=[{"text": {"s-frame": "%d/6" % (i + 1)}, "bars": {}}
                           for i in range(6)],
                    side_cards=[{"title": "state",
                                 "rows": [{"label": "frame", "id": "s-frame",
                                           "initial": "1/6"}]}])
    body = open(html, encoding="utf-8").read()
    if "<script src=" in body:
        raise SystemExit("FAIL: player references an external script")
    if "data:image/webp;base64," not in body:
        raise SystemExit("FAIL: frames were not inlined")
    size_mb = os.path.getsize(html) / 1024 / 1024
    print("PASS player: self-contained, %.1f MB" % size_mb)

    print("\nall checks passed")


if __name__ == "__main__":
    main()
