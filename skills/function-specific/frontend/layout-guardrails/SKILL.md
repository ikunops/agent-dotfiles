---
name: layout-guardrails
description: Enforce layout stacking-context, z-axis, and overflow containment driven by nesting depth and feature scope. Guards dropdowns, modals, portals, sticky tables, and nested menus against clipping, bleed, and layer-collision bugs.
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
