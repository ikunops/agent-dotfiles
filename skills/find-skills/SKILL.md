---
name: find-skills
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.
---

# Find Skills

两段式：**先查本地路由表**（本文件，零安装成本），命中即直接读对应 SKILL.md 干活；路由表匹配不到再走外部生态（skills.sh / `npx skills`）。

## 路由总则

1. **先精确匹配**：任务自然语言里的关键词命中下表【触发关键词】→ 直达该 skill，读它的 SKILL.md 后动手。
2. **再模糊匹配**：关键词没命中但任务领域/意图与某条相近 → 取该条，开工前说明"按 X 匹配，理由 Y"，允许用户否决。
3. **匹配不到不硬凑**：两轮都落空 → 明确输出「**无匹配，建议手写**」，然后直接自己干（可顺手 `npx skills find` 找生态补位，但不得把不相干的 skill 塞给用户）。
4. **本地优先**：路由表能解决的，不做外部安装；`ponytail`/`debug-and-refactor` 这类常驻人格优先级高于一切单点 skill。
5. 一条任务命中多条时，按用户意图的主要矛盾选一条主 skill，其余作为辅助并列（表中用 `+` 标注）。

## 精确路由表（任务自然语言 → skill）

### A. 代码与交付（高频三件套置顶）

| 触发关键词（中 / 英） | skill | 适用边界（一句话） |
|---|---|---|
| 修 bug / 没反应 / 删不掉 / 不生效 / 改了没生效 / 数据重复 / 作用错对象 / 样式改动（尺寸·间距·行高·颜色·图标）/ 重构 · debug / fix / not working / refactor | `debug-and-refactor` | 先核查前提再归因代码；**样式改动必做同类项完整性核查**——横向枚举同布局全部同类项一起改，收尾交清单 |
| 写代码 / 加功能 / 新需求 / 嫌臃肿 / 太绕 / 过度设计 / boilerplate · write code / add feature / over-engineering / bloat / be lazy / simplest | `ponytail` | 常驻人格，lite/full/ultra 三档（小改/默认/大砍）；功能存在性归用户拍板，实现经济学归它走七级阶梯 |
| diff 里找可删的 · review diff | `ponytail-review` | 只审 diff、一行一条发现；全库级审计用 `ponytail-audit`，捷径补录 `ponytail-debt`，成效展示 `ponytail-gain`，速查 `ponytail-help` |
| 端到端做成一件事 / 倒模 / 仿照某项目做个 X / 完整交付 / 走流水线 / 多 skill 协同 · end-to-end / full delivery / pipeline | `delivery-pipeline` | 跨测绘→开发→测试→审查三个以上阶段才进（P1 倒模/P2 全新/P3 修复/P4 增量）；单点小修直接 debug-and-refactor；**CI/CD 基础设施问题不归它**（见 D 组） |
| 会话交接 / 交给别人接手 / 交给 Claude Code / handoff | `handoff-to-claude-code` | 产出自足交接包（spec README + zip）；跨工具/跨人交接用，普通会话总结不用 |

### B. 前端与设计

| 触发关键词（中 / 英） | skill | 适用边界（一句话） |
|---|---|---|
| 前端布局 / 新页面 / 视觉方向 / 审美太平庸 · frontend design / aesthetics | `frontend-design` | 无既有品牌系统时给 committed 的视觉方向；已有品牌要沉淀成规范 → 加 `create-design-system`（reusable design system / UI kit） |
| 线框 / 多方案粗稿 / 先画几个方向 · wireframe / low-fi | `wireframe` | 探索阶段出 3–5 个结构不同方案；定了方向要能点 → `interactive-prototype`（可交互原型 / clickable prototype） |
| 设计产物要开关/换色/改文案不重画 · toggle / variant / tweaks | `make-tweakable` | 给已成稿的设计产物加 Tweaks 面板；不是用来生成初稿 |
| shadcn 组件 / 组件注册表 · shadcn / component registry | `shadcn` | shadcn/ui 项目的加件/修件/排版；非 shadcn 项目不用 |
| 找图标 / 侧边栏/按钮/状态图标 · icon | `icon-finder` | 路由到合适图标库；生产 UI 禁用 Unicode 符号凑数 |
| 架构图 / 时序图 / 数据流图 / 生命周期图 · architecture diagram | `archify` | 交互式 HTML 图（含验收与导出）；幻灯片走 `make-a-deck`（deck / slides / PPT） |
| z-index / 层叠上下文 / 溢出裁剪 / portal 被裁 · stacking / bleed / clipped | `layout-guardrails`（下沉：function-specific/frontend/） | CSS 层叠与溢出专项；广义像素打磨 → `make-interfaces-feel-better`（同下沉路径） |

### C. React 与 Web 性能

| 触发关键词（中 / 英） | skill | 适用边界（一句话） |
|---|---|---|
| React / Next.js 写法规范 / 无谓 re-render / bundle 优化 / 数据获取模式 · best practices / re-render | `vercel-react-best-practices` | 写、审、重构 React/Next.js 代码时挂载的静态性能规范；要实测数据时配 `web-perf` |
| 页面慢 / 白屏 / LCP / INP / CLS / FCP / 性能剖析 · slow page / Core Web Vitals / profile | `web-perf` | Chrome DevTools **实测**剖析与优化建议；静态写法规范用上行，深性能问题两个都上 |

### D. 运维与基础设施

| 触发关键词（中 / 英） | skill | 适用边界（一句话） |
|---|---|---|
| K8s / kubectl / 集群 / Pod / Deployment / Docker / Istio / 服务网络 / 集群搭建 · kubernetes / cluster | `k8s-knowledge`（顶层与 function-specific/devops/ 各一份） | 36 专题运维知识库检索（含 CI/CD、网络、存储、监控、安全）；问 K8s 先查它，不现场凭记忆答 |
| CI/CD 基础设施 / 流水线搭建 / 发布策略 · CI pipeline / release strategy | 按 CI 所在平台取：K8s 语境 → `k8s-knowledge` CI/CD 专题；Cloudflare 部署 → 下沉层 cloudflare 系列（见 G） | "流水线"两义：基础设施搭建归这里；指多 skill 端到端交付流程才归 `delivery-pipeline`（A 组） |
| Cloudflare Workers/Pages/KV/R2/D1 · wrangler / workers | `cloudflare` `wrangler` `workers-best-practices` `durable-objects`（下沉：function-specific/cloud/） | Cloudflare 边缘开发部署全家桶；Zero Trust → `cloudflare-one`；邮件 → `cloudflare-email-service`；Agents SDK → `agents-sdk` |
| Turnstile 人机验证 / bot 校验 · captcha / turnstile | `turnstile-spin` | Turnstile 端到端接入（widget 创建+嵌入+服务端校验）；其他验证码不适用 |

### E. 浏览器 / 视觉 / 数据

| 触发关键词（中 / 英） | skill | 适用边界（一句话） |
|---|---|---|
| 浏览器自动化 / 操作网页 / 填表 / 点按钮 / 截图 / E2E 测试 · browser automation / e2e / fill form | `agent-browser` | CLI 语义化操作，**默认首选**；要 CDP 协议级直控或 agent-browser 不可用 → `browser-use`（direct CDP control） |
| 网页抓取 / 爬数据 / scraping / crawl | `firecrawl`（下沉：firecrawl/skills/firecrawl-cli/） | 批量抓取与结构化提取；单页交互操作走 E 组浏览器 skill |
| 看图 / 读截图 / 这张图里是什么 · look at image / describe screenshot | `vision-eyes` | 文本模型借 GLM-4v 免费视觉 API 得眼睛；配套工具集 `vision-tools` |

### F. 思维与元工具

| 触发关键词（中 / 英） | skill | 适用边界（一句话） |
|---|---|---|
| 需求拷问 / 方案评审 / 压力测试这个计划 / 帮我把把关 · grill me / stress-test this plan | `grill-me` | 对**计划/设计**逐分支拷问到达成共识；代码层面的删减审查是 `ponytail-review`，别混 |
| 项目测绘 / 摸清这个项目结构 / 竞品倒模 / 给项目做体检 · map the codebase / reverse-engineer | `project-cartographer` | 产出闭环结构地图（后端层级+前端层级+双向映射矩阵）；倒模场景配 `delivery-pipeline` P1 使用 |
| 沉淀经验 / 记住这个坑 / 写进项目规则 · remember this / project memory | `project-memory-sculptor` | [待确认]→[已生效] 工作流维护 AGENTS.md；节制使用，不是每个任务都值得沉淀 |
| 真正理解 X / 第一性原理 / 费曼技巧 · understand deeply / first principles | `understanding-anything` | 思维框架教练，非代码专属 |
| 造新 skill / 写 SKILL.md / 把重复流程固化成 skill · create a skill | `skill-creator`（官方版，本次入库） | 起草→试跑→迭代循环；OpenCode 生态的 skill 评测/基准/打包 → `opencode-skill-creator` |
| 有没有 skill 能做 X / find a skill for X | `find-skills`（本文件） | 路由表落空后走下方外部生态查找 |

## 本地检索命令（路由表没覆盖时的兜底）

```bash
# 两库位置：活跃层 + dotfiles 库
ls ~/.zcode/skills/ ; ls C:/Users/30849/opencode-dotfiles/skills/

# 关键词扫描（含下沉层）
rg -il "关键词" C:/Users/30849/opencode-dotfiles/skills/ --glob "SKILL.md"
```

下沉层取回：`git mv function-specific/<类>/<名> <名>` 移回顶层即重新激活；单次使用直接读其 SKILL.md。

## 外部生态查找（本地无匹配才走）

**Key commands:**

- `npx skills find [query] [--owner <owner>]` - Search for skills interactively or by keyword
- `npx skills add <package>` - Install a skill from GitHub or other sources
- `npx skills update` - Update all installed skills

**Browse skills at:** https://skills.sh/

Quality bar before recommending: 1K+ installs、可信来源（`vercel-labs` / `anthropics` / `microsoft`）、仓库 star 数正常。推荐时给：名称 + 一句话用途 + 安装量 + 安装命令，装前征得同意。

落空收尾：本地路由表无匹配、生态也没有 → 输出「无匹配，建议手写」并直接动手做任务本身，可建议 `npx skills init` 造一个。
