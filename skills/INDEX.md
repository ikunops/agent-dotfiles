# Skills INDEX — 活跃层导航

> 活跃层 = 顶层平铺、自动触发的 skill。库存层（315 个）在 `framework/function/platform-specific/` 三分类里，用 find-skills 取用。
> 维护规则：新增 skill 必须在此登记一行；连续两周未触发且属平台专属的，评估下沉到库层。

## ① 测绘与理解（系统怎么懂）

| skill | 一句话 | 什么时候用 |
|---|---|---|
| `project-cartographer` | 项目测绘师：闭环结构地图（A/B/C/D 四型 + 形态牌） | 倒模参考项目 / 体检自己项目 / 摸清任何代码库 |
| `understanding-anything` | 思维框架教练（第一性原理/费曼/格栏…） | 想真正理解任何复杂事物，非代码专属 |
| `archify` | 架构/时序/数据流图 → 交互 HTML（带验收） | 测绘收尾的摘要图、文档配图、美化 Mermaid |
| `project-memory-sculptor` | 项目记忆塑形 | 沉淀项目长期记忆 |

## ② 任务路由与交付

| skill | 一句话 | 什么时候用 |
|---|---|---|
| `delivery-pipeline` | 交付流水线调度器（P1 倒模/P2 全新/P3 修复/P4 增量） | 端到端做成一件事、跨测绘/开发/测试/审查的多阶段任务 |
| `debug-and-refactor` | 调试与重构 | 修 bug、行为不对 |
| `find-skills` | 从生态里找/装 skill | "有没有 skill 能做 X" |
| `grill-me` | 拷问式检验 | 被挑战论证 |
| `handoff-to-claude-code` | 交接给 Claude Code | 跨工具交接 |

## ③ 前端工艺

`frontend-review-squad`（**前端审查小分队**：九 skill 编队组合审查——cartographer 闭环测绘 + debug-and-refactor 前提核查 + 布局/刻度/手感/UX/反AI味五件套，六步流程产出带证据的分级清单，2026-09-12 入库）· `frontend-design`（界面设计）· `shadcn`（组件体系）· `wireframe`（线框）· `interactive-prototype`（交互原型）· `create-design-system`（设计系统）· `icon-finder`（找图标）· `make-a-deck`（幻灯片）· `make-tweakable`（可调产物）· `web-perf`（性能）· `vercel-react-best-practices`（React 最佳实践）

## ④ 工程哲学（常驻人格）

`ponytail`（本体：懒惰资深开发 + 七级阶梯，lite/full/ultra）· `ponytail-review`（diff 审查）· `ponytail-audit`（全库过度工程审计）· `ponytail-debt`（捷径台账）· `ponytail-gain`（成效记分板）· `ponytail-help`（速查）

## ⑤ 浏览器与视觉

`agent-browser` · `browser-use`（浏览器自动化）· `firecrawl`（网页抓取）· `vision-eyes` · `vision-tools`（视觉能力）

## ⑥ 元工具

`opencode-skill-creator`（OpenCode 生态 skill 评测/基准/打包）· `skill-creator`（官方版：起草→试跑→迭代造 skill，2026-09-11 入库自 zcode plugin cache）· `turnstile-spin`（Turnstile 接入）

## ⑦ 已下沉库层（2026-09-06，路由见 find-skills/SKILL.md）

`cloudflare` · `cloudflare-one` · `cloudflare-one-migrations` · `cloudflare-email-service` · `wrangler` · `workers-best-practices` · `durable-objects` · `agents-sdk`（Cloudflare 全家桶 8 个）· `sandbox-next` · `sandbox-stable` · `sandbox-migrate-to-next`（沙箱 3 个）· `k8s-knowledge`

## ⑦b ZCode 官方插件镜像（2026-09-09 收编, 源=插件缓存 zcode-plugins-official）

> 16 个, 提升 Skill 版本随官方插件; 与插件本体同名时插件优先(先到先得)。更新法: 插件升级后从缓存重拷对应 skills/ 目录。

**文档工艺**: `docx` · `pdf` · `pptx` · `xlsx`（document-skills 0.1.4 全套）
**设备自动化**: `android-dev`（安卓模拟器）· `ios-dev`（iOS 模拟器）· `computer-use`（桌面控制）· `control-browser`/`web-gui-tester`（浏览器）
**ZCode 自诊断**: `zcode-configuration-guide`（资源装载地图）· `diagnosing-skills/-commands/-hooks/-mcp/-plugins`（五类不通排查）
**造 skill**: `skill-creator`（通用; OpenCode 专属流程仍走 `opencode-skill-creator`）

## ⑧ 设计线

`opendesign` · `setup-opendesign` · `run-opendesign`
