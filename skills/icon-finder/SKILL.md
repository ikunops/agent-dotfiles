---
name: icon-finder
description: Use when the project needs icons — sidebar nav, buttons, status indicators, feature labels, empty states, or any UI element that needs a visual symbol. Routes to the best icon library for the job. Never use raw Unicode symbols (☰◎⚙▣◉◈) for production UI.
---

# Icon Finder

当项目需要图标时使用此 skill。不要用 Unicode 符号（☰◎⚙▣◉◈）做生产级 UI，去专业图标库找。

## 优先级路线

按场景选库，不要每次从头搜：

| 场景 | 首选 | 备选 |
|------|------|------|
| 通用 UI（按钮/导航/状态） | Lucide | Heroicons, Tabler |
| 数据库/服务器/运维 | Lucide | Phosphor, Remix Icon |
| 文件/存储/磁盘 | Lucide | Bootstrap Icons |
| 网络/连接/WiFi | Lucide | Tabler, Phosphor |
| 操作/动作（增删改查） | Lucide | Feather Icons, Iconoir |
| 品牌/彩色图标 | Flaticon | Icons8 |
| 大量图标集/套图 | SVG Repo | IconScout |
| Material Design 风格 | Material Symbols | — |
| 轻量线性风格 | Feather Icons | Phosphor (light) |
| 填充/双色风格 | Phosphor | Remix Icon |

## 图标库速查

### Lucide（首选）
- **风格**：线性，24x24，一致性最好
- **网站**：https://lucide.dev/icons/
- **React**：`lucide-react`（项目已有的话直接用）
- **搜索**：按英文关键词，如 `server`, `database`, `hard-drive`, `network`, `folder`
- **适合**：几乎一切场景

### Phosphor Icons
- **风格**：6 种粗细（thin/light/regular/bold/fill/duotone）
- **网站**：https://phosphoricons.com/
- **React**：`@phosphor-icons/react`
- **适合**：需要填充或双色效果时

### Heroicons
- **风格**：outline（线性）+ solid（填充），24x24
- **网站**：https://heroicons.com/
- **React**：`@heroicons/react`
- **适合**：简洁线性图标

### Tabler Icons
- **风格**：线性，1.5px stroke，3000+ 图标
- **网站**：https://tabler.io/icons
- **React**：`@tabler/icons-react`
- **适合**：覆盖面最广

### Remix Icon
- **风格**：线性 + 填充双版本
- **网站**：https://remixicon.com/
- **React**：`remixicon-react`
- **适合**：中国开发者友好，中文搜索可用

### Bootstrap Icons
- **风格**：线性 + 填充，1800+ 图标
- **网站**：https://icons.getbootstrap.com/
- **React**：`react-bootstrap-icons`
- **适合**：Bootstrap 项目

### Iconoir
- **风格**：线性，开源，1600+ 图标
- **网站**：https://iconoir.com/
- **React**：`iconoir-react`
- **适合**：独特设计感

### Material Symbols
- **风格**：Google Material Design，可变粗细/大小
- **网站**：https://fonts.google.com/icons
- **React**：`@mui/icons-material`
- **适合**：Material Design 项目

### Feather Icons
- **风格**：线性，24x24，极简
- **网站**：https://feathericons.com/
- **React**：`feather-icons-react`
- **适合**：极简风格

### SVG Repo
- **网站**：https://svgrepo.com/
- **适合**：搜索大量开源 SVG 图标集，下载单个 SVG

### Flaticon
- **网站**：https://www.flaticon.com/
- **适合**：彩色图标、插画风格

### Icons8
- **网站**：https://icons8.com/
- **适合**：多风格（线性/填充/彩色），有 Figma 插件

### IconScout
- **网站**：https://iconscout.com/
- **适合**：图标包/Lottie 动画

## 使用方式

1. **项目已有图标库** → 直接从已有库中选，不引入新依赖
2. **项目无图标库** → 优先用 Lucide（SVG 内联，零依赖）
3. **需要特定风格** → 按上表选库
4. **下载 SVG** → 从 SVG Repo 或各库官网下载，内联到组件中

## 内联 SVG 的正确姿势

```tsx
// 推荐：直接内联 SVG，不引依赖
const IconServer = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="2" width="20" height="8" rx="2" ry="2" />
    <rect x="2" y="14" width="20" height="8" rx="2" ry="2" />
    <line x1="6" y1="6" x2="6.01" y2="6" />
    <line x1="6" y1="18" x2="6.01" y2="18" />
  </svg>
)
```

## 项目现有图标检查

在添加新图标前，先检查项目是否已有图标库：
- `package.json` 中搜索 `lucide`, `heroicons`, `tabler`, `phosphor`, `remix`, `feather`
- `src/` 中搜索 `import.*icon` 或 SVG 文件
- 如果已有库，优先从该库中选

## K8s 侧栏图标推荐（立即可替换）

当前 Unicode 符号 → 推荐 Lucide 替换：

| 分组 | 当前（丑） | Lucide 图标名 | 说明 |
|------|-----------|--------------|------|
| 工作负载 | ☰ | `Boxes` 或 `Container` | 容器/工作负载 |
| 网络 | ◎ | `Network` 或 `Globe` | 网络 |
| 配置 | ⚙ | `Settings` 或 `FileCog` | 配置 |
| 存储 | ▣ | `HardDrive` 或 `Database` | 存储 |
| 集群 | ◉ | `Server` 或 `Cluster` | 集群 |
| 策略 | ◈ | `Shield` 或 `Lock` | 安全策略 |
