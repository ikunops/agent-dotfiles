# 活跃层索引（Internal Node）

> 本页是三层索引的中间节点：根入口为 `../INDEX.md`，叶子为每个技能目录下的
> `SKILL.md`。只改本页的登记，不复制技能正文。
>
> 活跃层 = 顶层平铺、自动触发的 skill。新增活跃 skill 必须在这里恰好登记一次；
> 下沉时从本页移除，并登记到 `library.md`。外部本地依赖写进 `external.md`。

## ① 测绘与理解（系统怎么懂）

| skill | 一句话 | 什么时候用 |
|---|---|---|
| `project-cartographer` | 项目测绘师：闭环结构地图（A/B/C/D 四型 + 形态牌） | 倒模参考项目 / 体检自己项目 / 摸清任何代码库 |
| `understanding-anything` | 思维框架教练（第一性原理/费曼/格栏…） | 想真正理解任何复杂事物，非代码专属 |
| `archify` | 架构/时序/数据流图 → 交互 HTML（带验收） | 测绘收尾的摘要图、文档配图、美化 Mermaid |
| `project-memory-sculptor` | 项目记忆塑形 | 沉淀项目长期记忆；bootstrap 初始化接手无记忆项目 |
| `web-app-capability-mining` | Web 产品能力面挖掘（读 i18n 语言包 + 前端 chunk 名当权威词汇表） | 摸清某工具到底有哪些功能、竞品能力对比、避免只读文档导致大面积遗漏 |
| `black-box-protocol-compatibility` | 黑盒客户端协议兼容工程（官方客户端请求矩阵 / 身份模型 / 错误码 / 契约测试） | 反代、私有 API、请求被拦截、设备指纹、会话 ID、签名参数、任意客户端协议复刻 |

## ② 任务路由与交付

| skill | 一句话 | 什么时候用 |
|---|---|---|
| `delivery-pipeline` | 交付流水线调度器（P1 倒模/P2 全新/P3 修复/P4 增量） | 端到端做成一件事、跨测绘/开发/测试/审查的多阶段任务 |
| `debug-and-refactor` | 调试与重构 | 修 bug、行为不对 |
| `find-skills` | 任务路由器：L0 项目记忆直达 → L1 路由表组链 → L2 外部生态 → L3 条件沉淀 | 每个任务开工时；"有没有 skill 能做 X" |
| `handoff-to-claude-code` | 交接给 Claude Code | 跨工具交接 |

## ③ 前端工艺

`frontend-review-squad` · `frontend-design` · `shadcn` · `wireframe` · `interactive-prototype` · `create-design-system` · `icon-finder` · `no-emoji-ui` · `make-a-deck` · `huashu-design` · `make-tweakable` · `code-motion-film` · `web-perf` · `vercel-react-best-practices`  · `ui-acceptance` · `frontend-ui-consistency` · `admin-console-design` · `photon-flow-viz`

## ④ 工程哲学（常驻人格）

`ponytail`（最懒可行方案：先问"这功能真需要吗"，再要最短 diff）· `ponytail-audit`（全仓过度工程审计）· `ponytail-review`（diff 级审查）· `ponytail-debt`（把 ponytail: 捷径注释汇成债务台账）· `ponytail-gain`（量化收益记分板）· `ponytail-help`（速查）

> 2026-09-25 曾整体归档，2026-09-30 恢复：常驻工程人格，属长期使用项而非低频库件。

## ⑤ 浏览器与视觉

`agent-browser` · `browser-use`（浏览器自动化）· `browser-automation`（无头浏览器自检：console/网络/断言/截图）· `web-browser-verify`（本机真实渲染验证，浏览器下载不可用时的兜底）· `firecrawl`（网页抓取；CLI 认证见项目规则）· `vision-eyes` · `vision-tools`（视觉能力）

## ⑥ 元工具

`opencode-skill-creator`（OpenCode 生态 skill 评测/基准/打包）· `skill-creator`（官方版：起草→试跑→迭代造 skill，2026-09-11 入库自 zcode plugin cache） · `darwin-skill`（达尔文.skill 2.1：像训练模型一样优化 skill——9 维评分 + 独立评委 + validation-gated 棘轮 + 人在回路，2026-10-15 入库） · `text-summary`（长文本→三段式摘要：核心结论 / 关键要点 / 待办与风险）

## ⑦ ZCode 官方插件镜像（2026-09-09 收编，源=插件缓存 zcode-plugins-official）

**文档工艺**: `docx` · `pdf` · `pptx` · `xlsx`（document-skills 0.1.4 全套）
**设备自动化**: `computer-use`（桌面控制）· `control-browser`（浏览器控制）· `web-gui-tester`（浏览器黑盒测试）
**ZCode 自诊断**: `zcode-configuration-guide`（资源装载地图）· `diagnosing-skills` · `diagnosing-commands` · `diagnosing-hooks` · `diagnosing-mcp` · `diagnosing-plugins`（五类不通排查）
**造 skill**: 通用流程和 OpenCode 专属流程已在 ⑥ 登记，本段不重复列名

## ⑧ 设计线

`opendesign` · `setup-opendesign` · `run-opendesign`

**个人风格库**（存放于仓库根目录 design-systems/，不是 skill、不进常驻索引）：6 套可复用风格 —— 极光玻璃、软陶新拟态、瑞士编辑、电影暗场、功能主义粗野、Stripe 工具风。每套含风格定义 + 设计 token + 预览页；用法：opendesign / create-design-system 开工时会同时扫项目内 opendesign/design-systems/ 和全局仓库的 design-systems/，同名时项目内优先。该目录自带 README：含六套风格对照表与跨风格通用陷阱。

## ⑨ WorkBuddy skillhub 收编（2026-09-18，源 = ~/.workbuddy/skills 独有）

`github`（gh CLI）· `github-trending-cn`（trending 监控）· `markitdown-skill`（文档转 MD）· `mcporter`（MCP 管理）· `nano-banana-pro`（Gemini 3 Pro 图像）· `excalidraw-diagram`（Excalidraw 图表，.venv 已剔除）· `browser-profile-diag`（浏览器登录态诊断）· `html-dashboard-regression`（单文件 dashboard 回归）· `minimax-pdf`（设计感 PDF）· `k8s-pitfalls`（K8s 避坑，原 k8s__skillhub 改名归一）

> 未收编（skillhub 同源重复，备份保留在 WorkBuddy）：agent-browser-core · agent-team-orchestration__skillhub。存疑未动：frontend-dev · university-applications（名实不符，待用户处置）。路由见 find-skills I 组。

## ⑪ 内容生产与架构迁移（2026-10-02 入库）

| skill | 一句话 | 什么时候用 |
|---|---|---|
| `pan-share-screenshots` | 网盘分享页分层截图流水线（目录树采集→严格匹配→点击链截图→平铺滚动→挂库） | 补真实网盘截图、鉴别空壳目录、要合规脱敏 |
| `mysql-to-sqlite-migration` | MySQL(+Redis)→SQLite 完整迁移方法论 | 单机/低并发、单文件独立版、迁移与验证 |
