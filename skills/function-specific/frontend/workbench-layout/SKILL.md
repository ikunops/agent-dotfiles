---
name: workbench-layout
description: "Layout & interaction rules for workbench/opscopt-lite style UIs — sidebar/main, sticky tables, context menus, split views, terminal/embedded editors. Covers z-index budgets, scroll isolation, and overflow-safe positioning that generic design skills skip."
metadata:
  tags: [frontend, workbench, layout, z-index, table, sidebar, context-menu, split-view, terminal]
  triggers:
    primary:
      - workbench layout
      - sidebar layout
      - sticky table
      - context menu overflow
    secondary:
      - split view
      - terminal ui
      - monaco editor
      - frozen column
    context:
      - dashboard
      - cluster management tools
    anti:
      - "random z-index"
      - "overflow visible on root"
---

# Workbench Layout

## Why
General design skills cover color/typography/aesthetics.  
Workbenches (cluster managers, ops dashboards, IDEs-in-browser) have **special layout hazards**:

| hazard | rule |
|---|---|
| sidebar/menu z-fighting | 层级硬性 150/110/10 预算 |
| sticky table header clipping siblings | overflow 隔离 (独立 scroll container) |
| right键菜单跑到屏幕外 | fixed + flip positioning |
| split-view collapse/expand 抖动 | 状态同步 + min-width guard |
| terminal/monaco resize 死锁 | flex-basis 驱动 + theme inherit |

## 1. Sidebar — Main Layout

```
[sidebar(240px, z-10)] [main(flex-1)]
```

- sidebar `position: fixed` or `sticky`; z-index **10**.
- main `margin-left`/`margin-top` offset, `overflow:auto`.
- **never** let content overlap sidebar except floating surfaces (z-index ≥ 150).
- mobile: collapse to icon strip / hamburger slide-in (z-index 110).

## 2. Sticky Table Header + Frozen Column

```jsx
<div className="overflow-auto h-[calc(100vh-64px)]">
  <table className="border-separate border-spacing-0">
    <thead className="sticky top-0 z-10 bg-white">
    <tbody>
```

- **one scroll container** per table: `overflow-x:auto; overflow-y:auto`.
- sticky thead/th: `position:sticky; z-index:2`.
- frozen first column: clone to sibling fixed col (or use `position:sticky; left:0`).

Rule: no element **inside** table can use z > 10.

## 3. Context Menu (Right Click)

- Trigger on `contextmenu` (not click).
- Position via `fixed` (NOT `absolute`) relative to viewport.
- Use `@floating-ui/react` auto-placement: flip/fallback to `top-start` if near bottom.
- **guardian**: if menu width + X > viewport width → shift left.

```jsx
const { refs, context } = useFloating({
  placement: 'bottom-start',
  middleware: [autoPlacement({ allowedPlacements: ['bottom-start','top-start','right-start'] })],
});
```

## 4. Split View

- Track split ratio in React state.
- Each pane: `flex: flex-basis(${ratio}%)`.
- **min-width guard**: pane flex-basis cannot drop below 20% (or collapse to icon).
- Resize handle: `cursor:col-resize`; drag updates ratio, persists to localStorage.

## 5. Terminal / Embedded Editor

- Host: `<div class="h-full w-full">` with `display:flex; flex-direction:column;`
- monaco/xterm: `flex:1 1 auto; min-height:0` (critical: prevents flex overflow).
- theme inheritance: parent bg color → `--vscode-editor-background`.
- keyboard shortcuts: stopPropagation on arrows / ctrl/cmd combos to prevent scroll hijacking.

## 6. Z-Axis Budget and Local Coordinate Systems

Workbench layouts are layered surfaces, not a single flat page. Each container has its own local axes: X for width and columns, Y for height and row rhythm, Z for stacking, and S for the state profile of a layer.

**Z layer budget (closed set, one owner per layer):**

| Layer | Typical content | Rule |
|---|---|---|
| 0 | page content, cards, tables | no z-index needed; document flow owns it |
| 10 | sticky headers, sticky toolbars, fixed side rails | must not overlap main content outside its own scroll container |
| 100 | dropdowns, popovers, context menus | portal to the app root; never inside an overflow-hidden ancestor |
| 200 | modals, drawers, command palettes | must trap focus and restore it on close |
| 300 | toasts, global alerts | never block the only escape path |

Rules:

- A floating surface inherits the **nearest positioned ancestor's** coordinate system unless portaled; do not assume viewport coordinates from inside a scrolled panel.
- Every z value must come from the named budget above. `9999` or ad-hoc values are a defect, not a fix.
- When a surface is opened, its owning layer must be recorded in the component's state matrix (S axis): default / hover / focus / selected / disabled / expanded.
- A sticky element and a modal cannot share a layer; if they visually collide, fix the layer assignment rather than adding more z-index.

## Quick Check
- [ ] sidebar z == 10; every higher z (tooltip, menu) ≥ 150?
- [ ] table scroll container `overflow` set explicitly, no nested overflow:auto inside thead?
- [ ] right-click menu uses `position:fixed` + flip, tested on small viewport?
- [ ] split-view pane flex-basis has min-width floor?
- [ ] monaco/xterm has `min-height:0` in flex parent?

## See Also
- [`layout-guardrails`](../layout-guardrails/SKILL.md) — deep layer/overflow tracing
- [`design-taste-frontend`](../design-taste-frontend/SKILL.md) — aesthetic polish
- [`shadcn`](../../shadcn/SKILL.md) — ready components (Dashboard = Sidebar + Table + Chart)
