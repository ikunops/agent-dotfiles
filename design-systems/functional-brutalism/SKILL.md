---
name: functional-brutalism
description: 功能主义粗野风格。当设计需要"可信、无装饰"时使用——开发者工具、文档站、状态页、API 产品、技术类 SaaS。纸白文档网格 + 系统字体 + 发丝分割线 + 功能蓝链接。
---

# Functional Brutalism

这个页面读起来像一份**规格表**或 **changelog**，不像一份营销材料。唯一的分层手段是发丝线；唯一的装饰是内容本身。

## 风格特征

| 维度 | 取值 |
|---|---|
| 纸面 | `#FBFBFB`（不是纯白） |
| 字段 | `#FFFFFF` |
| 墨色 | `#111111` / 次级 `#585858` |
| 发丝线 | `#E0E0E0`（**全站唯一分隔手段**） |
| 链接 | `#0000EE` **经典未加前缀的链接蓝** |
| 状态绿 | `#1E8E3E` |
| 字体 | `system-ui` 正文 + `ui-monospace` 标签/数据 |
| 圆角 | **0**（全站方角） |

## 关键决策与理由

### 为什么用"经典蓝"而不是品牌色？

功能主义网页自己的词汇表就是**灰发丝线 + 经典蓝链接**。这是 1990s-2000s Web 的原生语言，它携带"这是工具，不是广告"的强烈信息。

在这里**发明一个品牌色反而是 slop** —— 因为你把一个中性的、功能性的界面变成了"又一个 SaaS 落地页"。

### 密度 = 可信度

这个风格的招牌是**规格表**：

```
Timeline     Every alert, deploy and page lands on one auto-built timeline.
On-call      Routing follows your service graph, so the right responder is paged first.
Postmortems  Draft reports assemble from the incident as it happens.
```

- 术语用等宽字体、全大写、字距 `.06em`
- 定义用正常字体、`max-width:46ch`（可读行宽）
- 每一项之间只有一条发丝线

密度本身传递"这个产品有实质内容"。这与其他风格"少即是多"的克制逻辑**相反**，但同样有效——关键是密度来自**真实内容**，不是编造的 stats。

### 诚实 placeholder

没有真实客户 logo 时，画**虚线框 + 等宽字标签**：

```html
<span class="logo-slot">customer logo · todo</span>
```

这比编造 logo 墙或写假数据好得多。诚实占位是风格的一部分，不是妥协。

## 微调旋钮

- 想更宽松：`.col` padding 从 `46px 28px 60px` 提到 `64px 40px 80px`
- 想更密集：规格表 `padding` 减半，行高收紧到 `1.4`
- 想更"文档"：加侧边目录（sticky），左栏变 `200px + 1fr + 内容`
- 网格：`1.12fr 1fr` 可调到 `1fr 1fr`（更对称、更"表格"）

## 反面清单（不要做）

- 不要加圆角
- 不要加 box-shadow
- 不要用渐变
- **不要编造数据/logo/用户数** —— 这个风格的可信度完全建立在诚实上，编造会立刻摧毁它
- 不要用彩色区块分隔内容（发丝线就够了）

参见 `tokens/colors_and_type.css`。