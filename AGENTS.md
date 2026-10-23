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

## Shell 执行规则（Windows / PowerShell 优先）

本机存在 `pwsh`（PowerShell 7）、`powershell`（Windows PowerShell 5.1）、`cmd`，并可能有 Git Bash。**生成命令前先判定当前 shell，禁止跨方言拼接。**

### 1. 先判定 shell，后生成命令

- 工具调用带 `shell: "powershell"` → 只写 PowerShell 语法，禁止 `bash` 的 `$VAR` 展开习惯、`&&`、heredoc、`/c/...` 路径、`sed/awk/grep` 作为主逻辑。
- 明确要 Git Bash → 单独用 `bash -lc` 调用，并把整个脚本作为一个字符串传入；不要从 PowerShell 里直接拼 Bash 路径参数。
- `cmd` 只在确有必要时使用；`mklink`、`reg`、部分系统工具优先通过 `cmd /c` 或原生 PowerShell cmdlet。
- 同一个命令块只允许一种主 shell；需要跨 shell 时，拆成两步，前一步把结果写入文件，后一步读取文件。

### 2. PowerShell 7 与 Windows PowerShell 5.1 不混用

- 默认优先 `pwsh`（PowerShell 7）。脚本若依赖 `ForEach-Object -Parallel`、`??`、`?:`、`$PSVersionTable` 新语义，必须显式调用 `pwsh`。
- 需要 Windows PowerShell 5.1 兼容时，显式用 `powershell.exe`，并避免 PowerShell 7 专有语法。
- 调用脚本时写明解释器：PowerShell 脚本用 `pwsh -NoProfile -File <x.ps1>` 或 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <x.ps1>`；Python 脚本必须先调 `python <x.py>`。禁止把 `.py` 交给 `-File`，也禁止依赖当前会话自动继承。

### 3. 路径与参数

- 原生 PowerShell 使用 `-LiteralPath` 处理用户路径；含空格/方括号/中文的路径一律加引号。
- 不要生成 `/c/Users/...` 这种 MSYS 路径给 PowerShell；PowerShell 用 `C:\Users\...` 或 `C:/Users/...`。
- 调外部 exe 时的参数数组用 PowerShell 数组展开，不要把整个命令行拼成一个字符串再交给 `Invoke-Expression`。
- 需要传给 `cmd` 的路径不要包含未转义的 `&`、`|`、`^`；复杂参数写成临时 `.ps1` 或 `.cmd` 文件再执行。

### 4. 引号、管道与退出码

- PowerShell 单引号是字面量，双引号才展开变量；含 `$` 的字面量默认用单引号。
- 跨 PowerShell 进程传命令时，外层命令用单引号包裹，避免当前会话先展开 `$LASTEXITCODE`、`$env:...` 或 `$_`。
- 不使用 Bash heredoc（`<<EOF`）。多行文本用 here-string（`@' ... '@` 或 `@" ... "@`），结束标记必须顶格。
- 管道后不能只看控制台有无输出判断成功；必须检查 `$LASTEXITCODE`（外部 exe）或 `$?`（PowerShell cmdlet）。
- 外部命令失败时不要继续执行后续破坏性步骤；先 `if ($LASTEXITCODE -ne 0) { throw ... }`。

### 5. 中文与编码（Windows 必守）

- 所有 `.md`、`.json`、`.ps1`、`.py` 源文件统一 UTF-8 无 BOM、LF。
- 需要中文输出时，先设置 `$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)`；不要把 GBK 输出直接当 UTF-8 读。
- Python 子进程显式 `encoding="utf-8", errors="replace"`；读文件显式 `encoding="utf-8"`，禁止依赖系统默认编码。
- 终端出现乱码时，先判断是“源文件编码”还是“控制台代码页”，不要靠肉眼猜；用 `Format-Hex` 或字节检查确认。

### 6. 复杂操作落脚本

满足任一条件时，不写超长一行命令，改为生成临时脚本并执行：

- 超过 3 个管道或 2 层引号嵌套
- 需要循环、条件、错误处理
- 需要跨 shell
- 命令中包含中文路径或大量参数

临时脚本执行完即删；删除前确认路径位于 `$env:TEMP` 或当前工作区，禁止对计算出的未知路径做递归删除。

### 7. 失败后的固定恢复顺序

1. 停止重复同一条失败命令。
2. 打印并确认：当前 shell、解释器版本、工作目录、目标路径是否存在。
3. 用最小命令复现（只保留出错的那一段）。
4. 改为原生 PowerShell 写法，或拆成“写文件 → 读文件”的两步。
5. 修复后在规则/脚本中补一条回归检查，避免下次再犯。

**🔴 CHECKPOINT · Shell 变更前**：任何会改配置、删文件、改系统状态或跨盘移动的命令，必须先确认 shell、解释器和目标绝对路径；三项没说清，不准执行。

## 安全红线
- 禁止在未明确指定环境的情况下修改系统目录（C:\Windows\System32、Program Files、~/.ssh/）
- 禁止自动执行数据库 DELETE / DROP（必须人工确认）
- 禁止未授权的 Git 操作（force push、branch 删除、未切换直接 kill 进程）
- 浏览器操作禁止调用 browser_close / browser_restart（只允许只读和点击）

## Skills 调用规范
**任务第一步＝先路由（铁律）**：开始任何任务前，先扫 skill 清单找匹配当前任务类型的 skill / 部门，命中就整套加载再用——不要靠临场判断猜测，不要跳过侦查。布局/等高/塌缩相关一律先走 `layout-guardrails` 几何核验。

**看不到 ≠ 不存在（必读）**：常驻清单只列出约 109 个技能，另有约 180 个为省 token 被显式关闭了隐式调用（`allow_implicit_invocation: false`）。它们已安装、可用，只是不在你眼前。所以"我没找到对应的 skill"不能作为自己动手的理由。按顺序做：

1. 调 `find-skills` —— 它带全量路由表（含隐藏技能），告诉你该加载哪个
2. 若 `find-skills` 也不可达，直接读 `skills/INDEX.md`（按领域分组的全量登记）
3. 两条都空，才自己写；且要在回复里说明"查过 find-skills / INDEX，无匹配"

**这一步要在写方案之前做，不是做到一半再补。** 中途才发现已有技能覆盖，等于方案作废。

遇到对应场景时必须加载对应 skill，不要手写：
- 前端设计/视觉优化 → `frontend-design` / `make-interfaces-feel-better`
- 前端布局/层级防穿模 → `layout-guardrails` (z-index / stacking-context / overflow-clip / portal restack)
- 前端细节质感/反 AI 味 → `design-taste-frontend` / `hallmark`
- UI 验收/改动声称完成前 → `ui-acceptance` / `verification-loop`
- 写测试/端到端 → `e2e-testing` / `test-driven-development`
- 代码审查 → `requesting-code-review` / `receiving-code-review`
- 线框/原型 → `wireframe` / `interactive-prototype`
- 设计系统 → `create-design-system` / `opendesign`
- 图标查找 → `icon-finder`
- 演示文稿 → `make-a-deck`
- 动画/讲解片/逐帧渲染 → `code-motion-film`
- 数据流/拓扑/神经网络可视化 → `photon-flow-viz`
- 架构图/时序图 → `archify`
- 浏览器自动化 → `agent-browser` / `browser-use`
- 网页搜索/抓取 → `firecrawl`
- 视觉/图像 → `vision-eyes` / `vision-tools`
- K8s/运维 → `find-skills` 查 `function-specific/devops/`（该层为库层，不常驻）
- 排障/复用 → `debug-and-refactor` / `systematic-debugging`
- SQL/数据库 → `sql-review`
- 技能发现 → `find-skills`
- 项目测绘/结构探索 → `project-cartographer`（用户说"倒模""参考某项目来规划""帮我看看项目结构""有没有缺口/功能不全会用；含测绘、梳理前后端、检查前后端闭环）
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
