---
name: design-taste-frontend
description: "Design-taste rules for production frontend work — color commitment, typography scale, spacing rhythm, contrast, and motion restraint — applied at PR review. Use when building dashboards, workbench UIs (like opscope-lite), or any product surface where aesthetics matter but ad budgets do not."
tags: [frontend, design, taste, ui, color, typography, motion, contrast]
triggers:
  primary:
    - design taste
    - frontend aesthetics
    - UI polish
  secondary:
    - color palette
    - typography scale
    - contrast check
    - motion design
  context:
    - dashboard
    - workbenches
    - ops tools
  anti:
    - "rainbow ui"
    - "random font sizes"
---

# Design Taste — Frontend

## Why
Ad-landing-page skills (`make-a-deck`, `wireframe`) over-index on marketing copy.
This skill covers **product/workbench UIs** where users spend hours (dashboards, ops tools, IDEs).
Taste here = legibility + calm + durability under fatigue.

## Core Rules
1. **Color** — commit to ≤3 hues. Use `colorize`/`frontend-design` for generation, freeze in CSS vars.
2. **Typography** — follow a modular scale (16/19/24/32/40 …) — no arbitrary px.
3. **Spacing** — 4px grid system; 1 level per nesting tier.
4. **Contrast** — WCAG 2.2 AA for body; avoid decorative borders near text.
5. **Motion** — 1 curve/token (ease-in-out), max 250 ms. Disable on prefers-reduced-motion.
6. **Grid sanity** — cards respect a 12-col grid; gutters consistent (24 px desktop / 16 px mobile).

## Use with
- [`layout-guardrails`](../layout-guardrails/SKILL.md) — layout/overflow, this skill — visual polish
- [`make-interfaces-feel-better`](../make-interfaces-feel-better/SKILL.md) — pixel-level tweaks, micro-interactions

## Quick Check
- [ ] Can you name all brand colors in hex offhand? (≤3 hues)
- [ ] Is there exactly one `font-size` value per visual level (H1…body)?
- [ ] Are borders + shadows used on ≤2 elevations?
- [ ] Does the page feel "quieter" or "louder" than yesterday?
