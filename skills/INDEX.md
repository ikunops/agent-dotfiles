# Skills INDEX — 活跃层导航

> 活跃层 = 顶层平铺、自动触发的 skill。库存层（208 个）在 `framework/function/platform-specific/` 三分类里，用 find-skills 取用。
> 2026-09-25 瘦身：147 个长期未调用的技能已移入 `skills-archive/`（移动非删除，不参与索引）。
> 维护规则：新增 skill 必须在此登记一行；连续两周未触发且属平台专属的，评估下沉到库层。
> 下沉 = **移动**，不是复制（同一 skill 只应存在一份）；提交前跑 `python scripts/audit-skills.py --strict`。

## ① 测绘与理解（系统怎么懂）

| skill | 一句话 | 什么时候用 |
|---|---|---|
| `project-cartographer` | 项目测绘师：闭环结构地图（A/B/C/D 四型 + 形态牌） | 倒模参考项目 / 体检自己项目 / 摸清任何代码库 |
| `understanding-anything` | 思维框架教练（第一性原理/费曼/格栏…） | 想真正理解任何复杂事物，非代码专属 |
| `archify` | 架构/时序/数据流图 → 交互 HTML（带验收） | 测绘收尾的摘要图、文档配图、美化 Mermaid |
| `project-memory-sculptor` | 项目记忆塑形 | 沉淀项目长期记忆；bootstrap 初始化接手无记忆项目 |
| `web-app-capability-mining` | Web 产品能力面挖掘（读 i18n 语言包 + 前端 chunk 名当权威词汇表） | 摸清某工具到底有哪些功能、竞品能力对比、避免只读文档导致大面积遗漏 |

## ② 任务路由与交付

| skill | 一句话 | 什么时候用 |
|---|---|---|
| `delivery-pipeline` | 交付流水线调度器（P1 倒模/P2 全新/P3 修复/P4 增量） | 端到端做成一件事、跨测绘/开发/测试/审查的多阶段任务 |
| `debug-and-refactor` | 调试与重构 | 修 bug、行为不对 |
| `find-skills` | 任务路由器：L0 项目记忆直达 → L1 路由表组链 → L2 外部生态 → L3 条件沉淀 | 每个任务开工时；"有没有 skill 能做 X" |
| `handoff-to-claude-code` | 交接给 Claude Code | 跨工具交接 |

## ③ 前端工艺

`frontend-review-squad`（**前端审查小分队**：九 skill 编队组合审查——cartographer 闭环测绘 + debug-and-refactor 前提核查 + 布局/刻度/手感/UX/反AI味五件套，六步流程产出带证据的分级清单，2026-09-12 入库）· `frontend-design`（界面设计）· `shadcn`（组件体系）· `wireframe`（线框）· `interactive-prototype`（交互原型）· `create-design-system`（设计系统）· `icon-finder`（找图标）· `no-emoji-ui`（界面禁 emoji：SVG/文字/CSS 替代 + grep 清单）· `make-a-deck`（幻灯片）· `make-tweakable`（可调产物）· `web-perf`（性能）· `vercel-react-best-practices`（React 最佳实践）· `design-taste-frontend`（生产级设计审美：色彩承诺/字号阶梯/间距节奏/对比度/动效克制）· `interaction-design`（交互设计模式库，32KB）· `ui-acceptance`（四层验收+硬阈值+众数一致性+失败二分+汇报三件套）· `frontend-ui-consistency`（前端 UI 相对一致性规范 + 一键审计脚本）

### ③b 前端工艺库层新增（2026-09-12 收编 14 个，均在 function-specific/frontend/，用 find-skills 取用）

- **动画（gsap 家族 7 个）**：`gsap-core`（基础/核心 → timeline）· `gsap-frameworks`（框架对接 React/Vue）· `gsap-performance`（性能）· `gsap-timeline`（时间线编排）· `gsap-scrolltrigger`（滚动触发）· `gsap-plugins`（插件库）· `gsap-utils`（工具）
- **设计语言与参考**：`ui-ux-pro-max`（UI/UX 知识库 3.4MB）· `hallmark`（设计标杆/惯例库 107 文件）· `claude-design`（Anthropic 设计规范）· `pencilplaybook`（铅笔设计手册 6.7MB）· `cinematic-ui`（电影感 UI 素材 6.5MB；设计语言主用 ui-ux-pro-max）

## ④ 工程哲学（常驻人格）

（2026-09-25 已全部归档 → skills-archive/：ponytail 家族 6 个）

## ⑤ 浏览器与视觉

`agent-browser` · `browser-use`（浏览器自动化）· `browser-automation`（无头浏览器自检：console/网络/断言/截图）· `web-browser-verify`（本机真实渲染验证，浏览器下载不可用时的兜底）· `firecrawl`（网页抓取：全局 `firecrawl` CLI，认证见 `rules/install.md`）· `vision-eyes` · `vision-tools`（视觉能力）

## ⑥ 元工具

`opencode-skill-creator`（OpenCode 生态 skill 评测/基准/打包）· `skill-creator`（官方版：起草→试跑→迭代造 skill，2026-09-11 入库自 zcode plugin cache）

## ⑦ 已下沉库层（2026-09-06，路由见 find-skills/SKILL.md）

`cloudflare` · `cloudflare-one` · `cloudflare-one-migrations` · `cloudflare-email-service` · `wrangler` · `workers-best-practices` · `durable-objects` · `agents-sdk`（Cloudflare 全家桶 8 个）· `sandbox-next` · `sandbox-stable` · `sandbox-migrate-to-next`（沙箱 3 个）· `k8s-knowledge`

## ⑦b ZCode 官方插件镜像（2026-09-09 收编, 源=插件缓存 zcode-plugins-official）

> 16 个, 提升 Skill 版本随官方插件; 与插件本体同名时插件优先(先到先得)。更新法: 插件升级后从缓存重拷对应 skills/ 目录。

**文档工艺**: `docx` · `pdf` · `pptx` · `xlsx`（document-skills 0.1.4 全套）
**设备自动化**: `computer-use`（桌面控制）· `control-browser`/`web-gui-tester`（浏览器）
**ZCode 自诊断**: `zcode-configuration-guide`（资源装载地图）· `diagnosing-skills/-commands/-hooks/-mcp/-plugins`（五类不通排查）
**造 skill**: `skill-creator`（通用; OpenCode 专属流程仍走 `opencode-skill-creator`）

## ⑧ 设计线

`opendesign` · `setup-opendesign` · `run-opendesign`

## ⑨ WorkBuddy skillhub 收编（2026-09-18，源 = ~/.workbuddy/skills 独有）

`github`（gh CLI）· `github-trending-cn`（trending 监控）· `markitdown-skill`（文档转 MD）· `mcporter`（MCP 管理）· `nano-banana-pro`（Gemini 3 Pro 图像）· `excalidraw-diagram`（Excalidraw 图表，.venv 已剔除）· `browser-profile-diag`（浏览器登录态诊断）· `html-dashboard-regression`（单文件 dashboard 回归）· `minimax-pdf`（设计感 PDF）· `k8s-pitfalls`（K8s 避坑，原 k8s__skillhub 改名归一）

> 未收编（skillhub 同源重复，备份保留在 WorkBuddy）：agent-browser-core · agent-team-orchestration__skillhub。存疑未动：frontend-dev · university-applications（名实不符，待用户处置）。路由见 find-skills I 组。

## ⑩ 未归类（待归位）

> 这两个原本不属于任何一组（一个是编辑器自动化，一个是领域咨询）；2026-09-25 一并归档。

## 已归档（2026-09-25 瘦身，移入 skills-archive/，不参与索引）

> 这些技能长期未被调用，白占每轮请求的技能索引 token。**移动不是删除**，随时可移回。

本次共归档 147 个（顶层平铺 15 + 分类目录 132），完整清单见 skills-archive/_archived_list.json。

顶层这 15 个：

android-dev · android-native-dev · darwin-skill · game-development · grill-me · ios-dev · notebooklm-studio · ponytail · ponytail-audit · ponytail-debt · ponytail-gain · ponytail-help · ponytail-review · turnstile-spin · ziwei-doushu-master

> 恢复：把 skills-archive/ 下对应目录移回 skills/ 原位（顶层放平铺位，其余放 function|framework|platform-specific/），
> 并在本文件重新登记。校验：python scripts/audit-skills.py --strict
