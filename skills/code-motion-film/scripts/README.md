# 几何自检脚本用法

用于在**无头浏览器**里真实渲染组件、逐帧 seek、量测每个元素的矩形，自动找出：
文字×文字重叠、文字×主体重叠、元素越界。

## 依赖

- Node + 一个 Remotion 项目（`@remotion/renderer`、`@remotion/bundler`、`@remotion/player`、`react`、`react-dom`）。
- Remotion 自带的 Chrome（`ensureBrowser()`），**无需**额外装 puppeteer / playwright。

## 安装到项目

1. 建 `tools/overlap/`，放入：
   - `player-harness.tsx`（改里面的 `FILMS` 导入路径与画布尺寸）
   - `overlap-check.cjs`（改顶部 `FILMS` 时长表、`tools/overlap/entry.tsx` 路径）
2. 给要检查的**主体图形**加标记，例如：
   ```tsx
   <g data-fig="乌龟"><Tortoise ... /></g>
   ```
   只包图形本体，别把标签/引线一起包进来（否则会误报）。

## 运行

```bash
node tools/overlap/check.cjs 8      # 8 = 抽帧步长
```

输出 JSON 到 stdout，同时写 `out/overlap-report.json`。空数组 = 该片无重叠。

## 判定规则（可调）

- 文字×文字：重叠面积 > 较小者 10% → 报警
- 文字×主体：重叠面积 > 文字面积 10% → 报警
- 越界：矩形超出画布 ±6px → 报警

## 注意

- `page.setBrowserSourceMapGetter(() => null)` 必须调用，否则 console 事件会崩。
- 画布尺寸变了要同步改 harness 里的 `compositionWidth/Height` 与 `W/H` 常量。
