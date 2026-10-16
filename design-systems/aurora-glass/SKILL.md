---
name: aurora-glass
description: 深色极光玻璃风格。当设计需要"科技感但克制"的暗色界面时使用——登录页、落地页、AI 产品界面、Dashboard。紫青双色光晕 + 玻璃拟态面板 + 噪点颗粒。
---

# Aurora Glass

深色极光玻璃：三团模糊光斑在近黑底上缓慢漂移，内容坐在一块半透明玻璃板上。

## 风格特征

| 维度 | 取值 |
|---|---|
| 底色 | `#070912` 近黑带蓝（**不是**纯黑、**不是**均匀深蓝） |
| 光晕 | 三团：紫 `#6D28D9` / 青 `#0891B2` / 玫红 `#DB2777`，`blur(90px)`，`mix-blend-mode:screen` |
| 主色 | 紫 `#7C5CFF`，次色青 `#22D3EE` |
| 文字 | `#EEF1FF` / 次级 `#98A1C6` |
| 玻璃 | `rgba(255,255,255,.06)` + `backdrop-filter:blur(22px)` |
| 字体 | Inter（display 与正文同族，靠字重和字号分层） |
| 动效 | 光斑 18/22/26s 缓慢漂移，`prefers-reduced-motion` 时停止 |

## 关键决策与理由

- **紫青渐变是"品牌签名"还是"slop"？** 这里**是签名**。判别标准：渐变只出现在**光晕层**（背景），不进入组件；内容区一律无渐变（除了 logo 与主按钮的一处 accent 渐变）。全页紫洗才是 slop。
- **噪点颗粒**（`.grain`，`fractalNoise` at `opacity:.06`）不是装饰——它消除大面积渐变的"数字平滑感"，让暗部有胶片质感。
- **玻璃边缘**：见下方陷阱。默认**不要**给玻璃面板加 border。

## 核心陷阱（实测）

**给玻璃面板加 `border` / `background` / `backdrop-filter` 会勾出一圈可见的圆角矩形轮廓。**
用户实测反馈"边框很出戏"。修法：把玻璃面收进 `::before`，四周用 `mask` 羽化：

```css
.card { background: none; border: 0; box-shadow: none; backdrop-filter: none; }
.card::before {
  content: ""; position: absolute; inset: 0; border-radius: 28px;
  background: linear-gradient(120deg, rgba(124,92,255,.16), rgba(34,211,238,.05) 52%, transparent 84%),
              rgba(255,255,255,.055);
  backdrop-filter: blur(24px) saturate(1.1);
  -webkit-mask-image: linear-gradient(to right,  transparent 0, #000 110px, #000 calc(100% - 110px), transparent 100%),
                      linear-gradient(to bottom, transparent 0, #000  90px, #000 calc(100% -  90px), transparent 100%);
  -webkit-mask-composite: source-in;      /* 两轴取交 = 四边同时羽化 */
  mask-composite: intersect;
}
```

实测：边缘亮度台阶 **11.7 → 5.0**（且残值是极光自身渐变，非卡片）。

另外两条坑：
1. `background:...padding-box/border-box` 双层渐变会**渗进卡片内部**（内部亮度 42→89，整张卡被洗白）。要用 `mask` 锁进 1px 环。
2. 只改外壳不够——**子容器自己的背景渐变也是硬边矩形**，要一起去掉。

## 微调旋钮

- 想更亮：`--bg-deep` 提到 `#0D1020`
- 想更冷：把 `--blob-3`（玫红）换成 `#1E40AF`
- 想更克制：`--accent` 降饱和（`#6D5CE0`），光斑 `opacity` 降到 `.55`
- 移动端：光斑尺寸按视口缩放，否则大屏好看、小屏只剩一团色

## 反面清单（不要做）

- 不要加 `border:1px solid rgba(255,255,255,.2)` —— 就是上面那条陷阱
- 不要在内容区铺渐变
- 不要用 emoji 当图标（玻璃风格下尤其廉价）
- 不要加"科技感"装饰线/SVG 几何块 —— 极光本身已经是全部视觉密度

参见 `tokens/colors_and_type.css`。