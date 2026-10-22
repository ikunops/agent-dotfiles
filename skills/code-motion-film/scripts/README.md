# 几何自检脚本用法

用于在**无头浏览器**里真实渲染组件、逐帧 seek、量测每个元素的矩形，自动找出：
文字×文字重叠、文字×主体重叠、元素越界。

## 依赖

- Node + 一个 Remotion 项目（`@remotion/renderer`、`@remotion/bundler`、`@remotion/player`、`react`、`react-dom`）。
- Remotion 自带的 Chrome（`ensureBrowser()`），**无需**额外装 puppeteer / playwright。

## 安装到项目

1. 建 `tools/overlap/`，放入：
   - `player-harness.tsx`（改里面的 `FILMS` 导入路径）
   - `overlap-check.cjs`、`trajectory.cjs`（改里面的 `entry.tsx` 路径）
2. 建 `tools/overlap/films.json`，片表与画布均从这里读：
   ```json
   {"width": 1920, "height": 1080, "films": {"<filmId>": 720}}
   ```
   `films` 的值是该片总帧数。脚本不再写死任何片名或分辨率。
3. 给要检查的**主体图形**加标记，例如：
   ```tsx
   <g data-fig="主体图形"><Figure ... /></g>
   ```
   只包图形本体，别把标签/引线一起包进来（否则会误报）。

## 运行

```bash
node tools/overlap/overlap-check.cjs 8     # 单帧式抽查（快，步长 8）
node tools/overlap/trajectory.cjs 4       # 轨迹扫描（慢，但能抓到"动的元素扫过静止文字"）
node tools/overlap/trajectory.cjs 4 <id>  # 只扫一支片
```

输出 JSON 到 stdout，同时写 `out/trajectory-report.json`。空数组 = 该片无重叠。

## 两个脚本的分工（重要）

| 脚本 | 查什么 | 何时用 |
|---|---|---|
| `overlap-check.cjs` | 抽查帧的静态重叠 | 快速回归 |
| `trajectory.cjs` | **整条时间线的轨迹 × 时间线碰撞** | 交付前必跑 |

**为什么必须跑 trajectory**：静止帧没撞不代表后面不撞。移动的主体、滑块、光标、扫描线、
运镜会在时间线上"扫过"大片区域——一个静止的标签可能正好落在它的扫掠路径里。
trajectory 逐帧 seek，用**真实像素命中**（`elementFromPoint`）+ **矩形相交**两条路
交叉验证，报告里带**帧区间**（如 `f828-934 n=32`），能看出"什么时候撞、撞多久"。

## 报告怎么读

- `[像素命中]` = 高置信，一定是真撞（文字像素落在图形元素上）。**优先修这条。**
- `[矩形相交]` = 可能假阳性（包围盒相交不代表图形相交），但要**逐条确认**——
  细线擦过文字一角的碰撞像素网格抓不到，只能靠这一路。
- 自己的底板（完全包住文字、面积 ≥2.2 倍）会被自动过滤，不算碰撞。

## 调试经验

- **采样网格有盲区**：7×4 = 21 个采样点会漏掉"3px 细线擦过文字边缘"。
  所以矩形相交这一路不能省。
- 修完必须**重跑扫描**确认清零，不能只看静帧。
- 扫完记得渲染静帧**放大目视确认**（`crop` + `scale=neighbor`），
  像素统计和目视要互相印证。

## 判定规则（可调）

- 文字×文字：重叠面积 > 较小者 10% → 报警
- 文字×主体：重叠面积 > 文字面积 10% → 报警
- 越界：矩形超出画布 ±6px → 报警

## 注意

- `page.setBrowserSourceMapGetter(() => null)` 必须调用，否则 console 事件会崩。
- 画布尺寸变了要同步改 harness 里的 `compositionWidth/Height` 与 `W/H` 常量。
---

## transition-continuity.cjs — 转场连续性检查

转场交接前后各取若干帧，检查是否至少保留一项连续证据（亮度/主色/粗结构），并拦截“黑屏→亮起→新场景”“闪白→新场景”“静帧→直接切”。这是启发式闸门，最终仍要人眼审片。

```powershell
# 单对交接帧
node transition-continuity.cjs --left before.png --right after.png

# 帧目录：检查第 120 帧附近（默认前后各 5 帧）
node transition-continuity.cjs --dir frames --at 120 --radius 5

# 批量清单
node transition-continuity.cjs --manifest transitions.json
```

输入要求：**PNG**。JPG 先用图像工具转 PNG；视频先用 ffmpeg 抽帧为 PNG，例如：

```powershell
ffmpeg -i final.mp4 -vf "select='between(n,115,125)'" -vsync 0 frames/%05d.png
```

依赖：脚本优先使用 `pngjs`，没有时走内置 8-bit RGB/RGBA PNG 解码器；不支持的格式会明确报错，不会静默给假 PASS。

`transitions.json` 格式：

```json
{
  "transitions": [
    { "left": "frames/0115.png", "right": "frames/0125.png" }
  ]
}
```

**判定口径**：至少一项连续证据成立，且交接帧两侧都不是接近全黑/全白，才 PASS。黑场/白场若确实是章节分隔，应在项目配置里登记为例外，不要直接改脚本阈值。

## readability.cjs — 字幕可读时长检查

```bash
node readability.cjs captions.json 60
node readability.cjs captions.json 60 --cps 5.2
node readability.cjs --selftest
```

`captions.json` 两种格式：

```json
[{"text":"比较是本能","start":0.0,"end":1.4}]
[{"text":"比较是本能","from":0,"to":84}]
```

帧号格式必须传 fps。会报三类问题：单屏停留低于可读下限、相邻两屏切换过急、两屏时间重叠。

默认 5.2 字/秒（含理解余量）+ 0.35s 进出场余量。中文按字、英文按词折算、标点按 0.3 字计。

## camera-projection.cjs — 逐帧相机投影 + 假运镜检测

```bash
node camera-projection.cjs --selftest
```

给"平面画法也能环绕/升降/推拉"提供一个最小可跑的参照实现：

- `makeCamera({yaw, pitch, dist, fov, target})`：相机的方位角/俯仰/距离。每帧改参数，`project()` 就重算这一帧的屏幕坐标。
- `cylinder({base, radius, height, segments})`：低面数柱体，8–16 段就够读出体积。
- `renderScene(cam, faces, size)`：投影 → 剔背面 → 按深度从远到近排序。环绕时遮挡关系自动变，不用手调图层。
- `silhouettePoints(faces)` / `shapeDiff(a, b)`：把轮廓归一化后比较。**平移和等比缩放不会改变它，形变了才会变。**

自测在做的事，就是把判定标准变成可执行的断言：

1. 相机 yaw 从 0 转到 90，轮廓必须连续变化（否则就是纸片翻转）。
2. 整个画面平移 200px，轮廓差必须接近 0（平移不是运镜）。

在自己的项目里接这套逻辑时，注意两点：

- **元素和相机共用同一个 `frame`**。不要相机逐帧算、元素用 CSS transition，两者对不齐。
- **文字层不参与投影**。字幕固定屏幕层，只让世界层随相机变。
