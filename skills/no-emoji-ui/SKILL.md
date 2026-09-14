---
name: no-emoji-ui
description: UI 与前端界面禁止使用 emoji 作为图标、装饰或状态指示。适用于任何 Web/App/桌面端界面开发与改造任务，全局生效。
---

# Skill: no-emoji-ui（界面禁用 emoji）

## 规则

在任何面向用户的界面（Web / App / 桌面 / 终端 TUI / 弹窗 / 空态 / toast / 按钮 / 图标位）中：

1. **禁止用 emoji 当图标**：📡 ⚙ 🌙 🔍 ★ ✅ ❌ 📁 📰 💬 等一律不得出现在按钮、标题、菜单、列表项、状态指示中。
2. **禁止 emoji 装饰**：空态插画、欢迎语、toast 前缀、徽标、chip 标签中的 emoji 一并禁止。
3. **替代方案（按优先级）**：
   - **内联 SVG 线性图标**（首选）：统一 viewBox、stroke 用 `currentColor`、尺寸 14–16px，随文字颜色变化；多个图标用 `<symbol>` sprite + `<use>` 复用。可用 Lucide/Feather 的 MIT path 数据。
   - **纯文字标签**：语义已明确时文字本身就是最好的图标（"设置""刷新"）。
   - **CSS 绘制**：圆点、竖条、计数徽标等几何元素用 CSS 实现。
4. **允许的例外**：用户生成内容（文章正文/评论里的 emoji）、`<textarea>` 默认值、品牌方官方 logo 资源。
5. **表单 `<option>` 无法内嵌 SVG**：直接用纯文字，不放 emoji。

## 为什么

emoji 图标跨平台渲染不一致（Windows Segoe UI Emoji / macOS Apple Color Emoji 风格冲突）、无法继承主题色、深浅色主题下不可控、密集排布时产生廉价的"AI 生成感"。线性 SVG 图标 + 统一色板是成熟产品的共同选择。

## 检查清单（交付前 grep 一遍）

- [ ] `grep -P '[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}\x{2B00}-\x{2BFF}]'` 对模板/组件文件零命中
- [ ] 图标位全部为 SVG / 文字 / CSS 几何
- [ ] 深色与浅色主题下图标颜色均正确（currentColor）
