---
name: frontend-design
description: Use when designing without an existing brand system. Pushes for a committed, distinctive aesthetic rather than generic defaults — extreme directions, bold typography, decisive color commitment.
---

Loaded when designing without an existing brand system. Push for a committed, distinctive aesthetic. Generic defaults are a failure state.

## Output location

Write all output files to `./opendesign/mockups/<task-slug>/`. Derive the slug from the page or feature name (e.g. `landing-page`, `pricing-redesign`).

## Reference before invention

Before choosing an original direction, inspect any reference the user supplied: screenshots, current product UI, brand assets, prior artifacts, visual systems, and real product imagery. Treat a reference as evidence of structure — rhythm, hierarchy, proportions, motion logic, information order — not as a surface to copy. State which structural parts are being followed.

If no reference exists, say so explicitly. A small set of deliberately different directions is better than presenting a generic default as if it were grounded.

## Pre-build thinking

Before touching HTML, answer three questions in your plan:
- **Purpose.** What job does this page do in one sentence?
- **Tone.** Which human adjective describes the feeling — clinical, warm, severe, playful, reverent, brash?
- **Differentiation.** What would make a viewer remember this over a generic SaaS landing page?

Pick an extreme direction and execute it with precision: brutalist, maximalist, editorial, retro-futuristic, organic, industrial, anti-design, swiss-modernist, zine-punk. Indecisive middles read as stock templates.

## Typography

Pair a distinctive display face with a refined body face. Avoid Inter, Roboto, Arial, and generic system stacks. Candidates: editorial serifs (Fraunces, GT Sectra, Tiempos), geometric display (Space Grotesk, PP Neue Montreal, Söhne Breit), mono accents (JetBrains Mono, IBM Plex Mono), quirky unicase and variable fonts where the direction supports it. Set a real type scale with intentional ratios; do not rely on default browser sizes.

## Color

Commit to a cohesive palette. Dominant colors with one or two sharp accents outperform timid even distribution. Use oklch for accents so chroma and lightness stay consistent across hues. Restrict neutrals to chroma ≤ 0.02.

## Color resources

- 渐变色彩库：https://www.qijishow.com/Colors/gradient
- 中国色彩：https://www.qijishow.com/Colors/color
- 潘通年度：https://www.qijishow.com/Colors/pantone
- 色彩搭配：https://www.qijishow.com/Colors/pick

## Motion

One or two high-impact motion moments beat a dozen scattered micro-interactions. Favor CSS-only animation: transforms, transitions, `@keyframes`, `scroll-timeline` where it is supported. Reserve JS for motion that depends on state.

## Spatial composition

Break the grid deliberately: asymmetry, overlap, diagonal baselines, oversized type against tight columns, generous negative space — or controlled, dense information surfaces if the aesthetic demands it. Either direction beats an evenly padded three-column grid.

## Backgrounds

Default to atmosphere: gradient meshes, film grain, noise, layered transparencies, dramatic shadows, tinted halftones, subtle paper textures. Flat white on flat black is a choice, not a default — use it only when the direction demands it.

## Variation across generations

Never converge on the same choices across different projects or variation runs. Rotate axes: aesthetic direction, dominant hue family, typographic register, motion philosophy, compositional strategy. Two designs in a row should not feel like siblings unless the user asked for continuity.

## Matching complexity to direction

Maximalist direction → elaborate implementation: layered textures, dense type, rich motion, intricate detail.
Minimalist direction → restrained implementation: fewer elements, tighter type scale, longer transitions, more white.
Do not half-commit. A restrained layout executed with maximalist intent reads as unfinished; a maximalist layout executed with minimalist intent reads as confused.
