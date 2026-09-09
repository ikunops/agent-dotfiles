# Layout Guardrails — PR Checklist

1. [ ] **Scope declared** — element annotated with `data-scope="…"` or `data-z-layer="…"`.
2. [ ] **Z-index cap respected** — ≤ scope cap table in `strategies.md`.
3. [ ] **Parent overflow** — immediate ancestor `overflow` verified not to clip floating child.
4. [ ] **Portal restack** — after teleport, child re-opens own stacking-context / `overflow-visible`.
5. [ ] **Edge flip** — dropdown auto-flips or scrolls into view at viewport boundary.

## 几何核算（尺寸核算 + 重叠判定）—— 布局按实际内容尺寸安排，验证用数字不用目测

> 形而上：布局不是"看着好看"，是"内容需求宽度 ≤ 容器可用宽度"的算术成立。改任何尺寸/宽度/容器后必跑本段。

**A. 重叠判定（先量再猜）**
两两取 `getBoundingClientRect()` 求交：`ox = min(a.right,b.right) - max(a.left,b.left)`、`oy = min(a.bottom,b.bottom) - max(a.top,b.top)`，`ox > 4 && oy > 4` 即真重叠。用数字反推溢出量，再定位到具体元素与它的父容器宽度。

**B. 内容尺寸核算（fit-content / max-content）**
- `w-fit`（fit-content）在 **inline-block/按钮/trigger** 上取 **max-content** 尺寸，**不收缩**——父容器定宽时必须核算 `内容 max-content 宽 ≤ 容器宽`，否则子元素溢出压住后续兄弟。
- 修法优先让子元素 `w-full` 自适应父容器，而不是把父容器改大（改大只是匹配当前内容，内容一变又溢出）。
- flex 子项默认可收缩（shrink:1），块级/固定宽子项不可——两者混排是错位与重叠的温床。

**C. 环境敏感性三查**
1. 根字号：`getComputedStyle(document.documentElement).fontSize` —— `w-40`=10rem 在缩放环境比 16px 环境窄，"标准机器不复发"≠没 bug；
2. 视口宽度：布局在断点分界线上最容易露出换行/溢出差异；
3. 缩放：`devicePixelRatio` / CSS `zoom` 影响 rect 数值的解读。

**D. flex-wrap 掩盖反查**
`flex-wrap` 让溢出行换行隐藏问题；容器加宽/字段变少使行不再换行时，被掩盖的溢出立即暴露。**改布局尺寸后，反查"之前依赖换行排布的行"**是否开始叠压。

**E. 收尾清单**
- [ ] 表单/弹窗/动态行改动后：跑一遍矩形两两相交检测（editor/dialog 内全部 input、select-trigger、textarea），`overlaps == []`
- [ ] 用到的 rem 定宽容器都按实际根字号核算过可用宽度
- [ ] 加宽/加字段改动后，确认没有"因不再换行而暴露"的旧溢出
