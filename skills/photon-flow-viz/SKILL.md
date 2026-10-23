---
name: photon-flow-viz
description: 用加性光渲染"流经系统的数据"——请求路径、神经网络激活、数据包追踪、内存访问。不是画箭头，是让流量本身成为光：光纤束 + bloom + 色调映射，可出静态帧或逐帧播放器。当任务要求"把某个系统的流转可视化""看请求怎么走""画神经网络激活""做流量/拓扑动画"时使用。
---

# 光流可视化

## 先读这段：这是项目指引，不是技法大全

渲染内核已经写好且稳定，**不要重写**。参考实现就在同目录：

| 文件 | 是什么 |
|---|---|
| `scripts/fibre.py` | 内核：加性光累积、bloom、色调映射、车道几何、包络、渐变、四种粒子语法 |
| `scripts/scene.py` | 场景契约 + 几何helper（`ring_point` / `box_left`）+ `render()` |
| `scripts/chrome.py` | 文字与结构层（光画完后再画，否则被 bloom 吃掉） |
| `scripts/audit.py` | **车道端点审计**：每条线的起终点是否真的落在节点上 |
| `scripts/web.py` | 把帧序列烘成单文件 HTML 播放器 |
| `scripts/scene_nn_layers.py` | 参考场景 A：神经网络前向传播（`clump` 语法） |

需要技术细节时读 `scene_nn_layers.py`——一百多行，比任何文档都准。

## 怎么跑

调用约定与 `frontend-ui-consistency` 一致：先进入 skill 目录，再执行脚本。**不需要安装包。**

```bash
cd skills/photon-flow-viz
python scripts/scene_nn_layers.py
```

自己写新场景时，照抄这个骨架：

```python
import scene as S
import chrome, web

sc = S.Scene(nodes=[...], lanes=[...], title="...", subtitle="...")

problems = sc.verify()          # 必须先过审计
if problems:
    raise SystemExit(sc.audit_report())

for i, ph in enumerate([0.0, 0.33, 0.66]):
    S.render(sc, phase=ph, out_width=1600).save(f"frame_{i}.png")
```

## 选粒子语法（四种，都对，看场景）

```python
S.Lane("a->b", points, style="pulse")   # 线本身亮起，亮段滑动，宽度等于线宽
```

| 语法 | 看起来 | 什么时候用 |
|---|---|---|
| `pulse` | 光纤本身分段亮起，亮段沿线滑动，**宽度等于线宽** | 已建立的连接上传输数据（长连接、缓存命中、固定拓扑） |
| `missile` | 亮头 + 长指数尾迹 | 请求路径、"有东西正飞过去"、单向追踪 |
| `clump` | 密集柔和光团、彗星簇 | **神经网络激活、内存访问、粒子场**——成千上万微小实体并发 |
| `bead` | 小而离散的珠子 | 低频控制流量、健康检查、离散 RPC |

语法与场景的对应不是审美偏好，是语义：一条长连接上"亮点滑动"比"光点飞过"更准确，因为连接一直在，变的是通过量。而神经网络里每个激活是独立的小实体，所以用 `clump`。

## 包络：束宽怎么呼吸

`env` 控制光纤束沿路径的宽度分布：

| env | 形状 | 语义 |
|---|---|---|
| `tight` | 紧-松-紧（默认） | 源和目标收束、中段展开。**大多数场景选这个** |
| `flat` | 等宽 | 已经建立的稳定管道 |
| `open` | 松-紧 | 发散式扇出 |

## 🔴 四条硬规则（都是踩出来的，不是理论）

### 1. 端点必须落在节点上，渲染前先过审计

```python
if sc.verify():        # 返回非空 = 有线悬空
    raise SystemExit(...)
```

一条飞进空白处的线，观众看到的是"这个系统有 bug"，而不是"这张图有 bug"。`scene.render()` 内部也会拦，但先自己查能拿到清楚的报告。

### 2. 绝不手写端点坐标

一律从节点几何推导：

```python
S.ring_point(cx, cy, r, deg)          # 圆环节点
S.box_left(box, frac=0.5)             # 卡片左边缘
```

同一个 bug 在参考项目里出现过三次：卡片一挪位置，写死的终点就指向空气。其中一次是长连接轨道停在卡片**上边框外 1px**，看起来像悬在半空、没连到任何东西。

### 3. 粒子宽度必须等于线宽

亮段和光纤走同一个绘制调用（`line_add`，同宽度），所以宽度由构造保证。如果粒子的 blob 半径是线的 2–3 倍，观众看到的是一坨光球在跑，不是线在发光。这是最常见的观感失败。

### 4. 别在累积阶段裁剪

光是加性累积到 float32 缓冲区、允许超过 1.0 的；bloom 在这层做，最后才色调映射。中途裁到 0–1 会让画面变扁、变浑。Canvas 的 8bit 裁剪正是它看起来远不如 Python 版的原因。

## 播放器（`web.py`）

```python
web.bake(frames, "out/player.html", state=state, side_cards=cards,
         width=1600, height=900, fps=24)
```

体积预算：1600px + WebP q97 ≈ 170 KB/帧（36 帧约 6 MB）；1920px 无损 ≈ 550 KB/帧。

四条必须遵守的（每条都曾产出过一个坏交付）：

1. **全部内联**。页面去加载同级 `.js` 时，任何"单独打开 HTML"的查看器都是黑屏。
2. **DPR 锁 1**。帧已经是目标分辨率，再按 `devicePixelRatio` 放大只能插值——这就是"糊"的来源。
3. **提供确定性单帧模式**。headless 截图 rAF 循环会得到空白，因为虚拟时钟下 rAF 不推进。`?still=1&frame=0` 必须同步画一帧。
4. **查询串不要过 shell**。`?still=1&v=A` 在 PowerShell 里会被 `&` 截断，你截到的是浏览器 DNS 报错页，还以为自己验证过了。把参数烘进临时副本，别传查询串。

## UI 层：不要另起炉灶

数字、进度条、卡片一律遵守已有规范：

- `frontend-ui-consistency` —— 数值一致性、众数判定
- `ui-acceptance` —— 四层验收、硬阈值（**命中区 ≥ 44px**、对比度 ≥ 4.5:1）
- `admin-console-design` —— 后台/控制台的三档约束

**特别提醒两条我违反过的：**

- **不要用"圆角卡片 + 左侧彩色竖条"这个母题**。`create-design-system` 把它列为业界用尽的视觉默认。用短刻度线标记连接点，不要整条彩边。
- **实时数字不要每帧重写**。`ui-acceptance` 五b 要求"首屏不播、真实变化才播"。`web.py` 的 `setTxt` 做了现值比对，值没变就不碰 DOM。

## 常见失败模式

| 症状 | 原因 | 处理 |
|---|---|---|
| 线飞到一半消失 | 端点悬空 | 跑 `sc.verify()` |
| 一坨光球在跑 | 粒子比线粗 | 用 `pulse`，或确认走的是 `line_add` 同宽度 |
| 整体发灰发浑 | 累积阶段裁剪了 | 检查是否在 float 缓冲里裁 0–1 |
| 静态帧好看、动画糊 | 帧分辨率 < 画布尺寸 | DPR 锁 1，或提高 `out_width` |
| headless 截图为空白 | rAF 不推进 | 用 `?still=1` 确定性单帧 |
| 标签被光盖住 | 文字画进了光缓冲 | 用 `chrome.compose()`，在色调映射之后画 |
| 帧序列表情不动 | 相位没变化 | `phase` 要扫过 0→1 |

## 不做最小满足

参考图里有的氛围层、次要连线、材质细节不能因为"不影响主线"就省。少一层观众就判"简陋"，哪怕主体完全正确。这条来自 `code-motion-film`，对可视化同样成立。
