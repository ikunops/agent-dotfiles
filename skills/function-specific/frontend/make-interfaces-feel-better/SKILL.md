---
name: make-interfaces-feel-better
description: Apply concrete design-engineering details that make interfaces feel polished. Use when reviewing or improving UI spacing, typography, borders, shadows, motion, hit areas, icons, text wrapping, and interaction states.
metadata:
  origin: community
---

# Make Interfaces Feel Better

Use this skill for the small design-engineering details that compound into a
more polished interface.

Source: salvaged from stale community PR #1659 by `linus707`.

## When to Use

- The user says the UI feels off, flat, generic, cramped, jumpy, or unfinished.
- You are building controls, cards, lists, dashboards, navigation, forms, or
  toolbars.
- A component needs hover, active, focus, enter, exit, loading, or empty states.
- A frontend review needs specific before/after recommendations.

## Core Principles

### Concentric Radius

For nearby nested rounded surfaces:

```text
outer radius = inner radius + padding
```

If padding is large, treat layers as separate surfaces instead of forcing the
math. The point is optical coherence, not formula worship.

### Optical Alignment

Geometric centering is not visual centering. Measured starting points, not guesses:

| Shape | Perceived size | Correction |
|---|---|---|
| Circle vs. square of equal bounding box | Circle reads ~5-8% smaller | Overshoot the circle by 2-4% of its size |
| Triangle / play glyph | Reads small and low | Nudge up 1-2px, widen 2-4% |
| Star, arrow, asymmetric icon | Visual mass sits off-centre | Offset 1-2px toward the lighter side |
| Text set beside an icon | Icon appears low | Align the icon to cap height, not to the box |

Fix the SVG path when possible; only fall back to a pixel-level margin when the
source cannot change. Round shapes in a row of icons need overshoot or they look
shrunk next to their square neighbours - this is the single most visible symptom.

### Proportions: What Actually Holds

Golden ratio and Fibonacci get cited far more than they get used. Their boundary:

- **Golden ratio (1.618)** is a tie-breaker, not a generator. Use it when a two-column split needs a starting point; do not use it to build a type scale. 14px -> 22.6px -> 36.6px leaves no room for intermediate sizes, which is why real scales use 1.125 / 1.2 / 1.25 / 1.333 / 1.5.
- **Fibonacci spacing** looks elegant but fails in practice: 1/2/3 are visually identical, 34 -> 55 skips a usable step, and 13 is not divisible by 4 so it breaks grid alignment. An 8-point grid (4/8/16/24/32/48/64) wins because every step stays on-pixel and adjacent values are far enough apart to read as different.
- **Do not retro-fit the math.** Overlaying a golden spiral on a screenshot proves nothing; a coincidence is not a rationale.

What does hold, and is cheap to apply: an 8-point spacing grid, a geometric type scale chosen by information density, concentric radius, optical overshoot, and spacing (not rules) as the grouping signal.

### Shadows And Borders

Use borders for separation and focus rings. Use layered shadows when a card,
button, dropdown, or popover needs depth. Shadows should be transparent and
subtle enough to work across backgrounds.

### Text Wrapping

- Use `text-wrap: balance` on headings and short titles.
- Use `text-wrap: pretty` on short-to-medium body text, captions, descriptions,
  and list items.
- Avoid both on long prose, code, and preformatted content.
- Use `font-variant-numeric: tabular-nums` for counters, timers, prices, tables,
  and other updating numbers.

### Font Smoothing

On macOS, apply antialiased font smoothing at the root layout when the project
does not already do so:

```css
html {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

### Image Outlines

Images often need a subtle inset outline so their edges do not blur into the
surface.

```css
img {
  outline: 1px solid rgba(0, 0, 0, 0.1);
  outline-offset: -1px;
}

@media (prefers-color-scheme: dark) {
  img {
    outline-color: rgba(255, 255, 255, 0.1);
  }
}
```

Use neutral black or white alpha outlines. Do not tint image outlines with the
brand palette.

### Easing Curves

Duration and curve are one decision, not two. The same 200ms feels crisp with
`ease-out` and mechanical with `linear`.

| Intent | Curve | Duration |
|---|---|---|
| Enter (appear) | `cubic-bezier(0, 0, 0.2, 1)` | 200-300ms |
| Exit (disappear) | `cubic-bezier(0.4, 0, 1, 1)` | 120-180ms |
| State change | `cubic-bezier(0.4, 0, 0.2, 1)` | 150-200ms |
| Emphasis / overshoot | `cubic-bezier(0.34, 1.56, 0.64, 1)` | 250-400ms |
| Large surface move | `cubic-bezier(0.2, 0, 0, 1)` | 300-500ms |

Rules that matter more than the exact numbers:

- **Exit is faster than enter.** Leaving should feel like it got out of the way.
- **Distance changes duration, not curve.** A 4px fade and a full-screen sheet can share a curve; the sheet just takes longer.
- **Never animate `all`.** See Transition Scope below.
- **Respect `prefers-reduced-motion`.** Collapse to a near-instant opacity change, do not simply shorten the same transform.

### Corners: Arc, Bezier, Superellipse

`border-radius` is **not** a bezier curve - it is one or two arcs. That is why a
CSS radius and a designed radius do not look the same: the arc meets the straight
edge with a curvature jump, which reads as a visible corner.

| Shape | Math | Result |
|---|---|---|
| CSS `border-radius` | Circular / elliptical arc | Visible transition where arc meets edge |
| Bezier corner smoothing | Cubic bezier approximating constant curvature | Softer, but still an approximation |
| Superellipse (squircle) | \|x/a\|^n + \|y/b\|^n = 1, n ~ 4-5 | Most even, no dip at the join |

Superellipse is a different family from bezier, not a tweak of it. In CSS the
closest cheap approximation is a large radius plus generous padding; where the
shape is critical (app icon, large hero card) it is worth drawing the path instead
of approximating with `border-radius`.

### Motion

Use CSS transitions for interactive state changes because they can retarget
when the user changes intent mid-motion. Reserve keyframes for staged
one-shot entrances or loading sequences.

Good motion defaults:

- Enter: combine opacity, small `translateY`, and optionally blur.
- Exit: shorter and quieter than enter, usually 150ms.
- Press: `scale(0.96)` for tactile buttons, with a way to disable it when the
  movement distracts.
- Icon swaps: cross-fade with opacity, scale, and blur instead of instant
  visibility toggles.

### Transition Scope

Never use `transition: all`. Specify the changed properties:

```css
.button {
  transition-property: transform, background-color, box-shadow;
  transition-duration: 150ms;
  transition-timing-function: ease-out;
}
```

Use `will-change` only for first-frame stutter on compositor-friendly
properties such as `transform`, `opacity`, and `filter`. Never use
`will-change: all`.

### Hit Areas

Interactive controls should have at least a 40x40px hit area, ideally 44x44px
where the layout allows it. Expand with a pseudo-element when the visible icon
is smaller, but do not let expanded hit areas overlap.

## Review Output

When reviewing a UI polish pass, report concrete changes in before/after rows:

| Principle | Before | After |
| --- | --- | --- |
| Concentric radius | Same radius on parent and child | Parent radius accounts for padding |
| Tabular numbers | Counter shifts as digits change | Counter uses `tabular-nums` |
| Transition scope | `transition: all` | Explicit transition properties |

Include file paths and properties when they are not obvious from the snippets.
Omit principles that you checked but did not change.

## Checklist

- Nested rounded elements are optically coherent.
- Icons are visually centered; round icons in an icon row have overshoot.
- Easing curves are chosen per intent, not one `ease` everywhere.
- Exit motion is shorter than enter motion.
- Corner treatment matches the surface size (arc for small, squircle for hero shapes).
- Icons are visually centered.
- Buttons, cards, and popovers use borders or shadows for the right reason.
- Headings and short text avoid awkward wrapping.
- Dynamic numbers use tabular numerals.
- Images have neutral outlines where needed.
- Enter and exit animations are split, subtle, and interruptible where
  appropriate.
- Buttons have tactile active states without exaggerated motion.
- `transition: all` and `will-change: all` are absent.
- Small controls still have usable hit areas.
