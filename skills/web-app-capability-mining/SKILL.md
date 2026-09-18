---
name: web-app-capability-mining
description: 摸清一个 Web 产品（尤其有 MCP/API 但功能远多于接口的客户端类产品）的完整能力面，避免只读文档/接口清单导致大面积遗漏。核心手法是读它的 i18n 语言包和前端 chunk 名——这两处是产品功能的权威词汇表，文档会滞后而它们不会。触发词：能力边界、功能对比、竞品分析、摸清某个工具有哪些功能、避免遗漏功能、capability discovery、枚举 API。
agent_created: true
---

# 摸清一个 Web 产品的真实能力面

## 什么时候用

- 「这个工具/竞品到底有哪些能力」——**尤其是它同时提供 API 或 MCP 的时候**
- 做功能对比、能力边界分析、竞品分析
- 想确认「除了文档写的，它还藏着什么」

## 核心认知：功能面 ≠ 接口面

一个成熟产品通常有**三层**，只读最上面一层会漏掉一个数量级：

| 层 | 典型规模 | 看哪里 |
|---|---|---|
| **API / MCP 工具层** | 十几个 | 文档、`tools/list`、OpenAPI |
| **HTTP 路由层** | 可能很少 | 抓包、路径探测 |
| **产品功能层** | **几百个** | **i18n 语言包 + chunk 名** ← 真正的能力面 |

实测教训（DBX 0.6.0）：MCP 工具 17 个、`/api` REST 路由 **611 条去重路径（649 处注册）**，
而 **174（源码）/ 177（实机）个 i18n 功能分组 + 79（源码）/ 80（实机）个引擎契约 + 226 个前端 chunk + 726 个 Tauri IPC**。
仅凭文档写出的对比报告，漏掉了数据对比、结构对比、血缘、测试数据生成、MQ 死信队列、GridFS 等整类功能。

> 旧版这里写的「REST 只有 7 条」「182 个功能分组」**都是错的**，已由实机复核推翻，见文末「判定功能是否真实存在」两节。

**文档一定会滞后**。DBX 的 README 只列 10 个工具，实际 17 个。

## 步骤

### 1. 先拿接口层的权威清单（如果有 MCP）

`tools/list` 这类元数据接口**通常不需要业务鉴权**，比文档准。MCP over stdio：

```
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```
（`notifications/initialized` 的 `id` 必须省略。每个 JSON-RPC 消息后跟 `\n`。）

### 2. 判断它到底走什么传输 —— 别浪费时间抓 REST

```bash
# 抓入口 chunk，看有没有 tauri / ipc 痕迹
grep -oE '__TAURI_INTERNALS__|__TAURI__|invoke\(' *.js | sort | uniq -c
```

如果走 **Tauri IPC**（桌面端套 Web），业务调用是 `invoke("cmd")`，**抓 HTTP 抓不到桌面端的业务流**——这时抓 REST 路径是白费功夫。

⚠️ **但别顺手得出"它没有 REST"的结论**。DBX 曾被认为「REST 只有 7 条」，实为 **611 条**；7 条只是**免鉴权**的那部分。它同时有桌面端（Tauri IPC 726 个）和 Web 服务端（REST 611 条）两条通路。
正确表述是：**抓不到是因为走了 IPC，不是因为没有 REST**。要确认 REST 规模，去源码里数路由注册（如 `grep -c '\.route(' main.rs`），并注意区分「去重路径数」与「注册次数」（同一路径注册多个方法会重复计）。

### 3. 拿完整 chunk 清单 —— 文件名就是功能地图

Vite / rolldown 会把所有懒加载 chunk 名写进入口 chunk：

```bash
curl -s "$BASE/" | grep -oE 'assets/[A-Za-z0-9_.-]+\.js'          # 种子（通常只有几个）
# 入口 chunk 里能挖出全部
grep -ohE '\./[A-Za-z0-9_.\-]+\.js' index-*.js | sed 's|^\./||' | sort -u
```

用**正则**从入口里把清单抠出来，然后 BFS 抓全（本例 227 个资源共 4.2MB，十几秒）。
剥掉哈希后，文件名本身就说明功能：`schemaDiff`、`productionSafetyStore`、`redisCommandTable`、
`mqDlq`、`dataGenerate`、`structureEditor`……一眼就能看出产品有哪些域。

### 4. ★ 读 i18n 语言包 —— 决定性的一步

```bash
ls chunks/ | grep -E '^(en|zh|zh-CN)-'          # 语言包通常单独一个 chunk，几百 KB
```

提取顶层 key：

```js
const t = fs.readFileSync('en-xxxx.js', 'utf8')
const top = new Set()
for (const m of t.matchAll(/(?:^|[{,])([a-zA-Z][a-zA-Z0-9_]{2,30}):\{/g)) top.add(m[1])
console.log([...top].sort().join(', '))
```

**为什么这条最有效**：i18n key 是产品功能的**完整词汇表**——
- 漏掉某个功能，界面上就会显示成 `someFeature.someLabel` 这样的 key，所以**不可能有遗漏**
- 键名是开发者的内部命名（`mqDlq`、`schemaDiff`、`productionExecutionGuard`），比文档的产品化描述更精确
- 一次拿到全部功能域，不用逐个猜

DBX 的 `en` chunk 448KB → **174 个功能分组（源码侧）/ 177（实机侧）**，包括文档和 MCP 工具清单里完全没有的
`dataCompare`、`lineage`、`dataGenerate`、`databaseBackup`、`gridfsBrowser`、`doltVersionControl`、24 个 `mq*`。

### 5. 挖引擎/驱动清单

产品通常在前端有一份「能力契约」对象（哪些引擎支持建库、支持什么命名空间语义）。
在最大的那个 chunk 里找引擎名和默认端口：

```js
const t = fs.readFileSync('api-*.js', 'utf8')
const keys = new Set()
for (const m of t.matchAll(/(?:^|[{\s,])([a-z][a-z0-9_]{2,20}):\{(?:deferred|database|connection|schema|namespace|catalog):`/g)) keys.add(m[1])
```

或直接搜默认端口：`t.indexOf('3306')` 然后打印上下文 ~1800 字符。

## 新接的 MCP 连接器：中途「信任」不会注入当前会话

给客户端（WorkBuddy / Claude Code / Cursor）加了 MCP server 并点了「信任」之后，
**当前会话仍然看不到它的工具**——工具表是**会话启动时**构建的。

排查顺序：

1. **确认配置写对了**：读 `~/.workbuddy/mcp.json`（注意不是 `.mcp.json`），
   用 Node 解析一遍确认 JSON 合法、`command`/`args`/`env` 都在。
2. **确认信任被记录**：`~/.workbuddy/mcp-approvals.json` 里应有
   `"<sha>::<serverName>": <毫秒时间戳>`。客户端有时还会自动补 `"disabled": false`。
3. **判断工具是否真的可用**：用 `ToolSearch` 查**完全限定名**（如 `mcp__dbx__dbx_list_connections`）。
   注意它做的是模糊匹配——搜 `..._list_tables` 可能命中 `mcp__genie-baas__..._db_list_tables` 之类的**同义词工具**，
   看返回里的 `Not found (n)` 才知道真没有。
4. **工具没出现 ≠ 配置有问题**：直接**用配置里那串命令自己跑一遍**，
   走 `initialize → notifications/initialized → tools/list → tools/call`，
   真调一个工具拿到结果，就能确定"配置是对的，只差重启会话"。

```bash
# 按 mcp.json 原样复现（以 npx 型 server 为例）
# spawn("npx", ["-y", "@dbx-app/mcp-server"], { env: {...process.env, ...配置里的 env} })
# 然后依次发 initialize / notifications/initialized / tools/list / tools/call
```

**结论话术**：告诉用户"配置已就绪且实测可用，但需要**新开一个会话**才会加载这些工具"，
而不是笼统地说"重启一下试试"。

## 坑

| 现象 | 原因 | 解法 |
|---|---|---|
| `grep` 正则返回 0，但肉眼能看到匹配 | **shell 把 `${...}` 当变量展开了**（在双引号里） | 正则里含 `$`/`{`/`}` 时改用 Node 跑，别跟 shell 引号斗 |
| 抓到的 REST 路径只有几条 | 该产品走 Tauri IPC / WebSocket | 见步骤 2，转去读 chunk |
| 用 grep 判断「某产品有没有某功能」误报多 | **匹配到了 i18n 语言包**（里面每个功能都提到） | 排除语言包：`--exclude-dir=i18n` + 过滤 `*/i18n/*`；再逐条人工确认命中文件 |
| 工具返回不是 JSON，解析全 null | 该 server 面向 LLM，返回 **Markdown 表格/项目符号** | 写 Markdown 表格解析器；列表类可能是 `- item (TYPE)` 项目符号而非表格 |

**「最后这条很重要」**：用 `grep -rli <关键词>` 判断「我们有没有 X」时，
语言包/文档目录会把所有关键词都命中，得出"全都有"的假结论。
反过来，**关键词组合搜得太窄**又会漏（第一次只 grep `service.go` 就得出"无事务"，漏了 `handlers.go`）。
→ **下结论前先把 grep 面铺够，并逐个核实命中文件的上下文。**

## 凭据：会话/文档里记的密码很可能已过期

从历史会话、文档、聊天记录里翻到密码后，**不要停在"找到了"**，必须验证：

1. 先确认**服务端把密码存哪、怎么校验**（读它的源码 / 公开仓库）。
   例：DBX 用 Argon2id 存在 SQLite 的 `app_settings.settings_json.password_hash`。
2. 拿到哈希后**本地校验候选值**（只验你手上已有的一两个候选，不是爆破）：
   ```python
   from argon2 import PasswordHasher
   PasswordHasher().verify(hash_str, candidate)   # 命中即真密码
   ```
3. 登录接口通常有限流（DBX 是 **5 次失败锁 60 秒**）。
   **盲目试密码会一路吃 429**，越试越久；定位到确切值再发一次请求。

**绝不**把哈希拿去跑字典/爆破——那是攻击，不是排查。只验证你已获得的候选。


## 反向用法：用竞品的 i18n 当 checklist 照自己的产品

拿到对方的功能域清单后，逐项 grep 自己的代码库：

```bash
EX="--include=*.go --include=*.tsx --include=*.ts --exclude-dir=i18n --exclude=*.json"
grep -rliE "schemaDiff|结构对比" internal/ src/ $EX | grep -v '/i18n/'
```

对每个命中项**必须打开上下文确认**，不要只信文件名——
`backup` 可能命中的是无关模块的备份逻辑，不是数据库备份功能。

---

## ★ 判定「它到底有没有这个能力」：三关规则（防高估）

找到模块 ≠ 功能已交付。按三关过滤，只过第①关就写进报告，会把**在制品当成已交付**：

| 关 | 判据 |
|---|---|
| ① | core / 后端**有实现**（有代码、有单测、`pub mod` 导出） |
| ② | 有**非测试**的生产调用方（调用点不能全在 `#[cfg(test)]` 里） |
| ③ | 接到**暴露面**：REST 路由 / IPC 命令 / MCP 工具 / 前端 chunk |

**实例**：DBX 的 `correction.rs`（659 行，联合修正计划）过了①（有实现有单测），但②的 7 个调用点全在自己的 `#[cfg(test)]` 内、③在 649 路由 + 726 IPC 里 0 命中 → **未上线能力**，不能当成"对方有而我们要追"的差距。

反向的坑同样存在：**i18n 无命中 ≠ 没有**。`script_generator` 就无独立 i18n 分组，但后端已实现。**两个方向都得防。**

还有两个易混点：
- **命中语言包是弱证据，命中代码 chunk 才是真实现**。判断某功能是否上线，看它命中的是 `en-*.js`（只有文案）还是 `api-*.js` / `App-*.js` / `xxxStore-*.js`（代码层）。
- **`supportLevel` 之类的元字段 ≠ 产品投入度**。DBX 的 `redis` 标为最低的 `connect` 档，但实机 chunk 命中 **16 文件 / 8 层**，压过多数 `operate` 档引擎。按这类字段排优先级会系统性低估；**用"命中文件数 / 贯穿层数"衡量投入度更可靠**。

## ★ 实机证据链层级（防低估）+ 两个已验证的陷阱

> **实机自报 > 实机产物 > 源码推断 > 文件时间戳**

| 层 | 取法 | 例子 |
|---|---|---|
| 实机自报 | 登录后端点（需鉴权也要试，密码往往就在文档里） | `GET /api/version` → `{"version":"0.6.0"}` |
| 实机产物 | 抓全量 chunk 做关键词/契约检索 | 226 个 chunk 4.8MB，检索 `dataCompare` 命中 4 文件 |
| 源码推断 | 数 yaml / 路由 / 枚举 | 79 个 `connection-types/*.yaml` |
| 文件时间戳 | `last-modified` vs commit 时间 | **别用，见下** |

**陷阱 1：mtime 不能用来定版本先后。** 构建产物的 mtime 是"构建动作发生的时间"，不是"从哪个 commit 构建的"——今天构建一个三年前的 commit，mtime 也是今天。它对"谁更新"**两个方向都没有证明力**。

**陷阱 2：比时间戳前先换算时区。** HTTP `last-modified` 强制 GMT，而 `git log` 默认带本地时区偏移（`2026-09-01 11:19:46 +0800` = `03:19:46 UTC`）。不换算会得出方向相反的结论。

**陷阱 3：版本号不一定硬编码进 bundle。** vite 没配 `define` 时，在 chunk 里 grep 版本串必然 0 命中。取版本号走 `/api/version`（需登录），或走 chunk 指纹比对。

## ★ 反向增量：实机可能比源码新

锁定了"实机 ≥ 源码"之后，只解决了「源码有 → 实机有没有」这一个方向。**反向的（实机有、源码没有）通常没枚举**，会系统性低估对手。

**实例**：`influxdb3` 在源码 0.5.99 全仓零命中（一度被判为"上一版误读、应删除"），但实机 0.6.0 是完整契约 → 源码侧判断是错的。

从实机 chunk 里提契约做集合 diff，能一次性定性"某引擎/某能力到底有没有"，比逐个猜名字可靠得多：

```bash
# 提取实机与源码两侧的引擎标识，做双向 diff
grep -ohE 'dbType:`[a-z0-9_]+' chunks/*.js | sed 's/dbType:`//' | sort -u > _live.txt
ls plugins/connection-types/*.yaml | xargs -n1 basename | sed 's/.yaml//' | sort -u > _src.txt
comm -23 _live.txt _src.txt    # 实机独有（反向增量）
comm -13 _live.txt _src.txt    # 源码独有（已下线）
```

**报告里要如实标注这个残留风险**：「本轮未枚举反向增量，不排除还有未识别的能力」。若要彻底消除，需要拿到与实机同版本的源码。

## 协作提醒：单一来源的结论在这个任务里基本不可信

一次 DBX 审计中，两位成员 + 主理人互相纠错 **7~8 个回合**，其中同一人连错三次（先低估、后高估、再把一个已被推翻的旧数字一起"平反"）。**每一次错误都是被独立复核抓住的，没有一次是自我发现的**——包括"纠正前一个错误时用力过猛，犯下第二个错误"这种典型模式。

所以：交叉复核不是形式主义。给出数字时注明**口径与取数命令**，让下游能自己复跑。
