---
name: layout-guardrails
description: Enforce layout stacking-context, z-axis, and overflow containment driven by nesting depth and feature scope. Guards dropdowns, modals, portals, sticky tables, and nested menus against clipping, bleed, and layer-collision bugs.
metadata:
  tags: [frontend, css, layout, z-axis, stacking-context, overflow]
  triggers:
    primary:
      - layout guardrails
      - stacking context
      - z-index clash
    secondary:
      - dropdown overflow
      - portal clipping
      - menu bleed
      - sticky z-layer
    context:
      - nested menus
      - modal stacking
      - fixed vs absolute
    anti:
      - "just add z-index 9999"
---

# Layout Guardrails

## Why
Deep UI architectures (e.g. opscope-lite cluster management) nest **global → page → entity → sub-entity** scopes.
Each scope hosts floating surfaces (dropdowns, portals, sticky headers, right-click menus).
Without depth-aware rules, menus render behind parents, portals get clipped by `overflow:hidden`, and z-index escalates to magic numbers.

## Rules live in
- [`strategies.md`](./strategies.md) — dynamic decision tree (scope + depth → layout)
- [`checklist.md`](./checklist.md) — PR / runtime self-audit

## Use
Trigger on any surface whose parent tree > 2 levels deep, or when a dropdown/modal/portal is created.
Hand off to `make-interfaces-feel-better` once positioning is **correct**, not just **pretty**.

## Axis Boundary (轴边界)

Layout failures are axis-confusion failures. Classify before fixing:

| Symptom | Wrong axis being used | Correct owner |
|---|---|---|
| content clipped vertically | padding/margin used to "make room" | Y: height, row rhythm, scroll container |
| sidebar squeezed or pushed out | z-index used to hide overflow | X: column ratio, min-width, flex-basis |
| dropdown clipped by ancestor | more z-index inside the same overflow context | Z: portal to app root + layer budget |
| modal visually behind sticky bar | sticky raised to 9999 | Z: named layer budget (sticky 10, modal 200) |
| expanded panel breaks page width | width animation on an X-owned container | Y: expand within the allocated X cell |

Rules:

- **Collapse and expand belong to Y**; they may change height and scroll position, never the X partition of a sibling.
- **Overlap belongs to Z**; if two elements collide, first ask whether the layer assignment is wrong, not whether the z-index is too low.
- **A container that owns X must not let a child dictate its width.** Use `min-width: 0` on the flex/grid child, not a wider parent.
- **Overflow is a property of the scroll container, not a patch.** Do not put `overflow: hidden` on a page root to hide a child that should have been portaled or constrained.
- When a component changes breakpoint, re-derive its local axis: desktop X-dominant split may become mobile Y-dominant stack; do not carry the desktop partition into the mobile layout.

## Sizing (尺寸核算)
Layout must satisfy "content needs ≤ container capacity" arithmetically, not visually.
Any element using `w-fit`/fit-content inside a fixed-width parent can overflow by max-content width —
sizing decisions and the rect-based overlap check live in [`checklist.md`](./checklist.md) §几何核算.
