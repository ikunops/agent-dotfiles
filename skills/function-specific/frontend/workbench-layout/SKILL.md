---
name: workbench-layout
description: "Layout & interaction rules for workbench/opscopt-lite style UIs — sidebar/main, sticky tables, context menus, split views, terminal/embedded editors. Covers z-index budgets, scroll isolation, and overflow-safe positioning that generic design skills skip."
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
