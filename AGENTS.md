# 全局固定规则 v1.0
# 最后更新：2026-08-15
# 变更摘要：初始化

## [行为铁律]

1. 只做被要求的事，不多做不少做。未明确要求的部分一律不实现。
2. 永远先 read 再 edit，禁止基于记忆或猜测修改文件。
3. 禁止"我觉得问题可能是..."——必须先侦察（read/grep/webfetch）再下结论，未完成自查禁止拒绝。
4. 禁止 proactive 创建文件（*.md、README、测试）除非用户明确要求。
5. 禁止提交 secrets、credentials、.env 文件到版本控制。

## [安全红线]

- 禁止在未明确指定环境的情况下修改系统目录（C:\Windows\System32、Program Files、~/.ssh/）
- 禁止自动执行数据库 DELETE / DROP（必须人工确认）
- 禁止未授权的 Git 操作（force push、branch 删除、未切换直接 kill 进程）
- 浏览器操作禁止调用 browser_close / browser_restart（只允许只读和点击）

## [Skills 调用规范]

- 前端设计/视觉优化 → frontend-design / make-interfaces-feel-better
- 前端布局/层级防穿模 → layout-guardrails (z-index / stacking-context / overflow-clip / portal restack)
- 线框/原型 → wireframe / interactive-prototype
- 设计系统 → create-design-system / opendesign
- 演示文稿 → make-a-deck
- 浏览器自动化 → agent-browser / browser-use
- 网页搜索/抓取 → firecrawl
- 视觉/图像 → vision-eyes / vision-tools
- K8s/运维 → k8s-knowledge
- 技能发现 → find-skills

三层降级策略：
  L1：利用已有知识自主解决（零额外成本）
  L2：读取项目 AGENTS.md 的 [已生效] 区块获取项目经验（低成本）
  L3：git 搜索历史上下文（兜底，仅当前两层无效时使用）
  git 搜索命令：
    git log --all --oneline --grep="关键词"
    git log -p --follow -- 文件路径
    git log --all -S "代码片段" --oneline

## [输出格式]

- 代码变更必须附带最小化 diff，禁止全文件重写。
- 复杂任务输出编号 checklist，每步一个原子操作。
- 最终输出包含：做了什么 / 为什么 / 影响范围 / 验证结果。
- 遇到 NEEDS_DECISION 时，必须给出具体选项而非"是否继续"。

## [工作流状态机]

每个任务必须按顺序经过以下状态，禁止跳步：
  RESEARCH（侦察）→ PLAN（计划）→ EXECUTE（执行）→ REVIEW（审查）
