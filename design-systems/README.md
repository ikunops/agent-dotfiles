# Design Systems — 个人风格库

跨项目复用的视觉风格库。每个子目录是一套**完整的、可独立使用的设计系统**。

## 六个风格

| 目录 | 风格 | 一句话 | 适用 | 来源 |
|---|---|---|---|---|
| `aurora-glass/` | 深色极光玻璃 | 紫青光晕 + 玻璃板 + 噪点 | 暗色 SaaS、AI 产品 | 无 skill 产出（baseline） |
| `soft-clay/` | 软陶新拟态 | 同色材质凸起/内凹 + 暖橘 | 移动工具、健康/记账 | 无 skill 产出（baseline） |
| `swiss-editorial/` | 瑞士编辑 | 黑白 + 强网格 + 信号橙 | 品牌主页、金融数据 | 无 skill 产出（baseline） |
| `cinematic-dark/` | 电影暗场 | 近黑舞台 + 单一暖光 | 发布页、暗色品牌站 | huashu-design 逻辑 C |
| `functional-brutalism/` | 功能主义粗野 | 纸白文档网格 + 经典蓝 | 开发者工具、文档站 | huashu-design 逻辑 A |
| `stripe-referenced/` | 干净工具风 | 白底 + 靛蓝 + 斜切渐变 | SaaS 登录/定价页 | huashu-design 逻辑 B |

## 每个系统的内容

```
<name>/
  SKILL.md                    风格定义、关键决策与理由、微调旋钮、反面清单
  tokens/colors_and_type.css  颜色 / 字体 / 形状 / 效果 token（可直接 @import）
  preview.html                完整可运行的示例页面
  preview.png                 1440×900 截图
```

## 怎么用

### 1. 直接抄 token

```css
@import url("../../design-systems/aurora-glass/tokens/colors_and_type.css");
```

或把需要的变量块复制进项目。

### 2. 读设计意图

用某个风格前**先读它的 `SKILL.md`**。里面写了"为什么这么做"和"哪些事不要做"——后者更重要，六个风格都有明确的反面清单。

### 3. 看预览

直接浏览器打开对应 `preview.html`。

## 关于这六个的关系

- **前三个**（aurora-glass / soft-clay / swiss-editorial）来自**无 skill 的 baseline 产出** —— 审美在线，作为"未经方法论干预"的对照组
- **后三个**（cinematic-dark / functional-brutalism / stripe-referenced）来自 **huashu-design 的三方向流程** —— 走的是「轮盘 / 现实参照 / 最佳设计师」三条逻辑
- 实测对比结论见仓库里的 darwin 记录：带 skill 的产出在**方向质量 / 反 slop / 内容驱动 / 工艺**四项上都更高，但 baseline 的风格**更保守、更容易被大众接受**

两组都保留，因为它们是**不同的工具**：要突破时用后三个，要稳妥时用前三个。

## 通用陷阱（跨风格）

1. **玻璃类面板加 border/background/backdrop-filter 会勾出可见轮廓** → 见 `aurora-glass/SKILL.md` 的羽化 mask 方案
2. **子容器的背景渐变也是硬边矩形** → 光改外壳不够，要一并处理
3. **移动端的 `display:contents` 会在桌面断点继续生效** → 见 `soft-clay/SKILL.md`
4. **新拟态天生低对比** → 正文/标签必须实测 ≥4.5:1
5. **渐变必须被框住** → 整页渐变是 slop，被裁进有边界的 band 才是 craft
6. **ch 限宽 × 中文 = 大标题竖排** → ch 是数字「0」的宽度，汉字约占 2ch；欧洲语言下安全的 max-width:16ch，机器翻译成中文后会让 80px 标题一行只放 1.8 个字。修法见 cinematic-dark/SKILL.md（翻译态用 html.translated-ltr 钩子 + em 限宽）