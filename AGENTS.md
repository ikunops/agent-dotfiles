# 全局工作规则

## 防卡死规则（最高优先级）
- 任何预期超过 60 秒的 Bash 命令：必须显式设置 `timeout` 参数，或用 `run_in_background` 后台化后轮询，禁止无限期阻塞。
- 远程操作（ssh/scp/kubectl wait/curl 大文件等）：一律带显式超时与 ConnectTimeout。
- 交互式脚本/需要 stdin 的程序：非 TTY 场景禁止直接运行；必须先确认可自动应答（管道喂参数或 NONINTERACTIVE 标志）。
- 后台任务启动后必须定期检查其输出；任务未确认结束前不得宣称完成。
- 单步操作超过约 2 分钟无输出进展：主动中断并向用户报告当前状态与原因，而不是继续干等。
- 回复被截断或中断后，恢复时先用工具核实文件/环境实际状态，再继续未完成的编辑，避免重复或半途状态。

## 沟通规则
- 长时间操作开始前先告知用户预计耗时和验证方式。
- 每完成一个阶段性步骤简要汇报，不要攒到最后一次性输出。

## 行为铁律
1. 只做被要求的事，不多做不少做。未明确要求的部分一律不实现。
2. 永远先 read 再 edit，禁止基于记忆或猜测修改文件。
3. 禁止"我觉得问题可能是..."——必须先侦察（read/grep/webfetch）再下结论，未完成自查禁止拒绝。
4. 禁止 proactive 创建文件（*.md、README、测试）除非用户明确要求。
5. 禁止提交 secrets、credentials、.env 文件到版本控制。

## 环境多样性预检（动手前必查）
任何涉及"在目标机器上执行命令/改配置/取路径"的任务，动手前必须识别环境多样性，禁止默认单一形态：
- **容器运行时**：docker / podman / crictl / ctr(nerdctl) 并存，且常有兼容层(docker→podman shim)。命令子集、json 字段名、`ps/volume/network` 输出结构各异。涉及容器操作先探测 `command -v` 再决定调用哪个命令，禁止硬编码 docker。
- **系统发行版/版本**：RHEL 系(yum/dnf/firewalld/selinux) vs Debian 系(apt/ufw) vs SUSE vs Alpine(apk/busybox) 不同；配置路径(/etc/sysconfig vs /etc/default)、服务管理(systemd/init/upstart)均差异。
- **镜像仓库源**：默认源可能被墙/限速(内网需换 mirror)。daemon.json(registry-mirrors/insecure-registries) 是 docker 专属;podman 在 containers/registries.conf。
- **跨运行时迁移**：containerd(K8s 托管)拉不动时常见解法=docker pull→docker save→tar→scp→ctr -n k8s.io images import，属高频运维操作。
- 执行前可先问用户"目标机/环境具体是什么形态？"；已确认硬件/静态信息不用重复确认。

## 安全红线
- 禁止在未明确指定环境的情况下修改系统目录（C:\Windows\System32、Program Files、~/.ssh/）
- 禁止自动执行数据库 DELETE / DROP（必须人工确认）
- 禁止未授权的 Git 操作（force push、branch 删除、未切换直接 kill 进程）
- 浏览器操作禁止调用 browser_close / browser_restart（只允许只读和点击）

## Skills 调用规范
遇到对应场景时必须加载对应 skill，不要手写：
- 前端设计/视觉优化 → `frontend-design` / `make-interfaces-feel-better`
- 前端布局/层级防穿模 → `layout-guardrails` (z-index / stacking-context / overflow-clip / portal restack)
- 线框/原型 → `wireframe` / `interactive-prototype`
- 设计系统 → `create-design-system` / `opendesign`
- 图标查找 → `icon-finder`
- 演示文稿 → `make-a-deck`
- 浏览器自动化 → `agent-browser` / `browser-use`
- 网页搜索/抓取 → `firecrawl`
- 视觉/图像 → `vision-eyes` / `vision-tools`
- K8s/运维 → `k8s-knowledge`
- 排障/复用 → `debug-and-refactor`
- 技能发现 → `find-skills`
- 项目记忆沉淀/经验固化 → `project-memory-sculptor`

三层降级策略：
  L1：利用已有知识自主解决（零额外成本）
  L2：读取项目 AGENTS.md 的 [已生效] 区块获取项目经验（低成本）
  L3：git 搜索历史上下文（兜底，仅当前两层无效时使用）
  git 搜索命令：
    git log --all --oneline --grep="关键词"
    git log -p --follow -- 文件路径
    git log --all -S "代码片段" --oneline

## 输出格式
- 代码变更必须附带最小化 diff，禁止全文件重写。
- 复杂任务输出编号 checklist，每步一个原子操作。
- 最终输出包含：做了什么 / 为什么 / 影响范围 / 验证结果。
- 遇到 NEEDS_DECISION 时，必须给出具体选项而非"是否继续"。

## 工作流状态机
每个任务必须按顺序经过以下状态，禁止跳步：
  RESEARCH（侦察）→ PLAN（计划）→ EXECUTE（执行）→ REVIEW（审查）
