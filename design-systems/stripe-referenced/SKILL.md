---
name: stripe-referenced
description: 干净工具风（Stripe 语汇）。当设计需要"可靠、成熟、克制"时使用——SaaS 登录页、定价页、营销落地页。白底 + 靛蓝主色 + 理性栅格 + 斜切彩色渐变横幅。
---

# Stripe Referenced

干净的白底、理性的栅格、自信但克制的语气。彩色只出现在一个被**框住**的横幅里。

## 风格特征

| 维度 | 取值 |
|---|---|
| 表面 | `#FFFFFF` |
| 墨色 | `#1A1F36` / 次级 `#59617A` |
| 线条 | `#E6E8EF` |
| 主色 | 靛蓝 `#635BFF`（hover `#4B44D6`） |
| 字体 | Hanken Grotesk（Söhne 的开源近似替身）+ Geist Mono |
| 圆角 | 卡片 12px / 输入 8px |
| 栅格 | `max-width:1080px`，三等分特性栏 |

## 关键决策与理由

### 渐变必须被"框住"

这是 craft 与 slop 的**唯一分界线**：

| | |
|---|---|
| ❌ slop | 整页铺一层靛蓝→紫的渐变背景 |
| ✅ craft | 渐变被裁进一个有明确边界的 `band`，**有斜切底边**，且卡片压在它上面 |

```css
.band {
  background: <amber radial>, <pink radial>, <core linear>;
  clip-path: polygon(0 0, 100% 0, 100% 78%, 0 100%);   /* 斜切底边是招牌 */
}
.card { margin: -72px auto 0; }   /* 负 margin 上提，压在斜边上 */
```

三个要点：
1. **斜切**（`clip-path`）—— 直角横幅会显得廉价
2. **多层渐变叠加**（线性核心 + 两个角部径向点缀）—— 单层线性渐变太平
3. **卡片负 margin 压上去** —— 制造层次，让横幅"在卡片后面"

### 类型选择

Söhne 是 Stripe 的定制字体，不可用。**Hanken Grotesk** 是开源世界里最接近的几何无衬线——同样的圆形字腔、克制的字距。

不要在 display 位置用 Inter/Roboto（太常见，见不出"有设计"）。

## 微调旋钮

- 主色换品牌色：`--accent` / `--accent-d` 成对改，`focus` 的 `rgba` 也要跟着
- 横幅角度：`clip-path` 的 `78%` 调到 `70%`（更斜）或 `85%`（更平）
- 卡片宽度：`460px` → `400px`（更紧凑）
- 想减弱渐变：去掉 `--grad-amber`，只留粉+核心

## 反面清单（不要做）

- 不要整页渐变
- 不要给横幅用直角
- 不要加第三个强调色（靛蓝 + 渐变里已有的颜色就够）
- 不要在正文用 display 字体
- 不要忘记 `::placeholder` 用 `--placeholder`（默认灰太深，破坏轻盈感）

参见 `tokens/colors_and_type.css`。