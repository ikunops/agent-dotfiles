---
name: html-dashboard-regression
description: Use when building, reviewing, or regression-testing a self-contained HTML/CSS/JS dashboard, admin panel, or single-file SPA — especially when you need evidence-based verification of logic, layout, contrast, and accessibility without a build system. Triggers include "单文件面板", "HTML dashboard", "admin panel", "冒烟测试", "回归验证", "dashboard review", "验证 UI 布局与对比度", or any request to prove a UI works rather than eyeball it.
agent_created: true
---

# HTML Dashboard Regression（单文件面板的三层验证）

面向「无构建体系、单文件 HTML + 原生 JS」的面板类交付物。核心原则：
**逻辑用 jsdom 跑，布局与对比度用真实浏览器量，全部落盘成脚本可复跑。**
不要只靠目测，也不要只看截图。

## 三层验证

| 层 | 工具 | 能证明什么 | 证明不了什么 |
|---|---|---|---|
| 结构 | 源码正则审计 | 语法、视图/模块一一对应、接口登记完整性 | 运行时行为 |
| 逻辑 | jsdom 执行真实脚本 | 交互、状态流转、事件委托、错误分支 | 布局、CSS、对比度 |
| 表现 | headless 浏览器 + CDP | 溢出、计算样式、对比度、可访问名、控制台异常 | 视觉美感 |

## 关键实现要点

### 1. jsdom 冒烟脚本必须显式退出
页面里的 `setInterval`（指标轮询、相对时间刷新）会被 jsdom 持续持有，
`process.exitCode = n` **不会**让进程退出 → 直接跑会被外部超时杀掉（表现为"日志写完了但退出码异常"），
被 CI / 上层 runner 嵌套调用则永久挂起。结尾务必：

```js
process.exit(fails === 0 ? 0 : 1);
```

### 2. 元素引用会在重渲染后失效
表格排序/筛选/翻页会重建 `tbody`（甚至整卡）内部结构。
测试里**每次操作前重新查询**，不要缓存 DOM 引用：

```js
const sortBtn = () => doc.querySelector('#mt-x .sort-btn[data-val="cpu"]');
sortBtn().click(); await wait(30);
check('...', !!sortBtn().querySelector('.sort-ind.up'));
```

### 3. 结构化选择器：分清容器与兄弟节点
`<div class="filters">chips</div><div class="table-scroll" id="mt-x"></div>`
—— 筛选 chip 是表格容器的**兄弟**，不是子节点。
`#mt-x [data-act="status"]` 永远匹配不到，应写 `[data-mt="x"][data-mt-act="status"]`。

### 4. 动态生成的 id 必须区分前缀
同一份数据清单若既内嵌在页面、又渲染进弹窗，两次都会生成相同 id →
重复 id 是非法 HTML，且 `getElementById` 只返回文档中第一个，会静默命中错误元素。
把前缀做成参数：`apiListHtml('api-')` / `apiListHtml('set-')`。
**加一条断言**：文档内无重复 id。

### 5. ID 里可以有点号，但别用 querySelector 选它
`id="api-containers.node"` 用 `getElementById('api-containers.node')` 没问题，
但 `querySelector('#api-containers.node')` 会把点号当类选择器。定位用 `getElementById`。

### 6. 对比度必须按公式反算，且要用「合成后」的底色
半透明 `rgba()` 软底色叠在不同父容器上，会得到不同对比度 ——
同一个 token 在白色卡片上达标（4.90），叠在页面底色上就掉到 4.43。
算法：沿父链合成 `background-color` 直到遇到不透明层，再套 WCAG 相对亮度公式：

```js
const f = v => { v /= 255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); };
const lum = c => 0.2126*f(c.r) + 0.7152*f(c.g) + 0.0722*f(c.b);
const ratio = (a, b) => (Math.max(lum(a),lum(b)) + 0.05) / (Math.min(lum(a),lum(b)) + 0.05);
```

**修复模式**：给该元素一个**不透明**底色锁定对比度，而不是继续调透明度：

```css
.chip { background-color: var(--surface);
        background-image: linear-gradient(var(--soft), var(--soft)); }
```

大字判定：`fontSize >= 24px` 或 `>= 18.66px 且 font-weight >= 700` → 阈值 3:1，否则 4.5:1。

### 7. CDP 直连（无需 playwright/puppeteer）
Node 22 自带 `fetch` 与 `WebSocket`：
启动 `msedge --headless=new --remote-debugging-port=9333 --user-data-dir=<temp> --no-first-run`，
轮询 `GET /json/version` 直到就绪 → `GET /json/list` 取 `webSocketDebuggerUrl` → WebSocket 发 CDP：
`Page.navigate` / `Runtime.evaluate` / `Emulation.setDeviceMetricsOverride`。
用 `Runtime.exceptionThrown` + `Log.entryAdded` 收集运行期错误。

### 8. 死活按钮审计（"点了没反应"的机械保证）
给每个依赖后端/未实现的按钮挂 `data-<x>-path="<endpointId>"`，
document 级委托统一拦截 → toast + 弹窗定位到接口清单条目。
断言：**每个 `data-*-path` 引用都必须能在清单里查到**（孤儿引用 = 0），
且**模块内不存在既无 `data-*-path` 又无 `data-*-act` 的裸按钮**。
这样"无响应"在结构上不可能出现。

### 9. 布局溢出要同时量页面和容器
只看 `document.scrollingElement` 会漏掉"卡片内部被撑爆"的情况。
两个都量，并在多宽度（1440/1024/768/390）下循环：

```js
pageOverflowX = root.scrollWidth - root.clientWidth;
contentOverflowX = content.scrollWidth - content.clientWidth;
```

表格类容器的内部横向滚动是**设计意图**，不计为失败。
真正的缺陷是：grid 子项缺少 `min-width: 0` 导致表格最小内容宽度撑爆父网格。

### 10. 统一入口用 spawnSync 聚合，但先修好子脚本退出
`run-all.cjs` 里 `spawnSync` 子脚本时给 `timeout`，并解析子脚本**落盘的日志**而不是
经管道回传 stdout（管道缓冲 + 未退出进程会让父进程挂起）。

### 11. 把「接口清单」变成可运行的桥接层（离线演示 → 真实联调）
只登记 `API_DEPS` 只能让按钮"有反馈"，证明不了契约正确。再进一步：
写一个**零依赖本地服务**实现同一份清单，前端自动探测并切换数据源。

```
面板 ──HTTP──▶ 桥接服务 ──SSH/SQL──▶ 真实机器
        └─ mock 数据源（默认，不需要任何远端权限）
```

- **同源托管**面板（`GET /` 直接返回 index.html），免 CORS，一条命令就能演示。
- **清单双份必须机器校验**：前端一份、桥接一份，加断言逐项比对 `id/method/path/group`，
  防止两份清单漂移（这是最容易悄悄腐化的地方）。
- **桥接返回规范字段，前端做适配**（`LIVE_ADAPTERS`）——桥接不该知道表格列长什么样。
- **但表格 `rows` 的字段必须与列定义同形**，这样水合就是一次数组替换，不需要映射层。
  用断言逐个接口校验 `rows[0]` 含全部列字段。
- 辅助端点极有用：`/health`、`/deps`（机器可读清单）、`/_requests`（最近 N 条请求日志，排障神器）。

### 12. 只读默认 + 结构化 dry-run（而不是静默成功）
沙箱/合规环境最常见的诉求是"只准看"。写操作**不要静默失败，也不要偷偷执行**，返回：

```json
{ "ok": false, "code": "READONLY", "executed": false,
  "intent": "重启实例",
  "wouldCall": { "method": "POST", "path": "/api/v1/x/demo/restart", "body": {} },
  "received": { ...实际收到的请求体... } }
```

前端据此弹"只读拦截"卡片，把**本该调用什么**摆出来 —— 对接后端时可直接照此核对契约。
两个配套细节：
- 写接口被拦后，**读能力仍要可用**：如「同步状态」自动回退成只读拉取（`GET`），
  并用 `info` 语气横幅说明，而不是红色报错。
- 横幅语气要区分：**策略拦截 ≠ 故障**。给 `showBanner` 加 `tone: 'info'`，
  否则用户会去"排障"一个本来正常的行为。

### 13. 前端实时数据源要能优雅退化
`if (typeof fetch !== 'function') return;` + `AbortController` 超时 + 候选地址逐个试
（`?api=` → localStorage → 同源 → 默认端口）。探测失败**不报错、不阻塞**，
完整回落到种子数据 —— 离线与在线是**同一份代码**，不要搞两套分支。

- 顶栏放一个数据源徽标（种子/探测中/实时），点击重探测；
- 支持 `?api=none` **强制离线**：测试要确定性，否则本机恰好跑着服务时用例结果随环境漂移；
- 接口清单的标记随运行状态切换（离线 `待接入` → 联网 `已连通 / 只读拦截`），
  否则会出现"42 项待接入"和满屏"已连通"自相矛盾的画面。

### 14. 测实时链路：注入桩 fetch + 导航后重新注入
jsdom 用例里**注入桩 `fetch`**（在 `beforeParse` 里），就能端到端验证探测→水合→按钮发请求→响应面板，
完全不依赖真服务：

```js
new JSDOM(html, { beforeParse(win) {
  win.fetch = opts.fetch || undefined;
  if (!opts.fetch) { try { delete win.fetch; } catch (e) {} }   // 默认强制离线
} });
```

CDP 探针里要**同时验证真实桥接**：探针自己 `spawn` 桥接进程 → 导航到 `?api=http://127.0.0.1:<port>` → 断言
`mode==='live'`、水合项数、点击写按钮后弹出只读卡。
⚠️ `Page.navigate` 会清空执行上下文，**注入的 helper 必须重新注入**，
否则整轮审计都返回 `AUDIT_FAILED`（极易误判为功能坏了）。
⚠️ 被**故意**触发的 `403` 会被浏览器记为控制台错误 —— 按 `entry.url` 归属到已知端口且文本含 403 时
归类为"预期内的拒绝"，单独计数，不要污染"0 console error"这个闸门。

### 15. 同一文件不要并行 Edit
一次消息里发多个 Edit 打到同一个文件，会发生读-改-写竞争：
**工具报 success，但改动可能静默丢失**（表现为运行时报"参数个数不对"这类莫名其妙的问题）。
同一文件一律串行编辑，改完 `Grep` 复核关键签名。

### 16. 写 HTTP 服务端时的三个必踩坑
自己实现桥接/桩服务（哪怕是 `http.server`）时：

| 坑 | 现象 | 修 |
|---|---|---|
| 不读请求体 | HTTP/1.1 长连接下残留 body 被当成下一条请求行 → `501 Unsupported method`；现象是"前几个正常、之后随机失败"，从业务侧极难定位 | 统一排空 body（含 `Transfer-Encoding: chunked`） |
| 默认 `protocol_version = 'HTTP/1.0'` | 每次响应后关 socket，浏览器 fetch 复用已关闭连接 → `fetch failed` | 改 HTTP/1.1 且**始终**发 `Content-Length` |
| `request_queue_size` 默认 5 | 并发连接被直接拒绝 | 子类化 `TCPServer` 提到 128 |
| `allow_reuse_address = True`（`HTTPServer` 默认） | **Windows 专有坑**：`SO_REUSEADDR` 语义与 Unix 不同，允许多进程绑同一端口且不报错 → 本服务"启动成功"却收不到请求（被先绑的进程接走），表现为日志正常、进程在跑、接口全 404 | 关掉复用，并改用 `SO_EXCLUSIVEADDRUSE`；端口冲突立即以 `OSError` 暴露 |
| 启动失败无提示 | 用户以为在跑 | 捕获 `OSError`，明确打印"端口被占用，请换 `--port`" |

另外两条：
- mock 数据若用 Python 内置 `hash()` 做种子会随 `PYTHONHASHSEED` 变（同一接口不同进程不同数据，
  "确定性数据集"名不副实）→ 用 `zlib.crc32`。
- **健康检查必须校验服务身份**（如 `data.service === '<name>-bridge'`），不能只看 `200 + ok:true`。
  否则端口被无关程序占用时，探针会对着一个陌生服务全套"通过" —— 这比直接失败危险得多。
  前端探测、契约测试的 `waitReady`、浏览器探针都要加这道校验。

### 17. 产出物轮次（截图）必须「重置状态 + 断言渲染前提」
断言的测试轮次和**生成交付图**的轮次是两回事，后者极易出静默错误——
断言全绿但截图是错的，而截图恰恰是用户唯一会看的东西。三条硬约束：

| 坑 | 现象 | 修 |
|---|---|---|
| 外壳裁剪整页 | `.app{height:100vh; overflow:hidden}` 把 `captureBeyondViewport` 的内容裁掉，所有长图高度都等于视口高（≈1200px），看起来"都一样长" | 截图前注入：`.app{height:auto!important;overflow:visible!important}` + `.main/.content{overflow:visible!important}` + 侧栏 `.nav-scroll{overflow:visible!important}` |
| 主题 / 皮肤漂移 | 前面的主题切换用例把页面留在浅色，交付图全是浅色（默认应是深色画布） | 截图前**显式设置**主题，并把 `data-theme` + `getComputedStyle(document.body).backgroundColor` 打进每条 `[shot]` 日志——让图与前提绑定，可事后审阅 |
| 交互态残留 | Tab / 筛选 / 分页用例跑完，选中态留在第 3 个 Tab，长图展示的不是默认视图 | 截图前清空状态表（`Object.keys(TAB).forEach(k=>delete TAB[k])`）并重渲 |

推论：**取整页图前，先量 `document.body.scrollHeight`，再按它设 `setDeviceMetricsOverride` 的高度**。
若所有页面量出的高度都相同，几乎一定是外壳还在裁剪——这就该是一条断言，不是靠眼睛。

### 18. 「为什么能work」的结论要用变体矩阵验证，不要凭记忆写注释
给修复写注释断言因果（如「`min-height:0` 是关键」）时，先做一次 A/B/C 变体对照：
每种变体只改一处、都量同一个指标。往往真实结论与直觉相反
（实测：`overflow-y:auto` 才是承重项；`min-height:0` 与它**完全等价**，因为滚动容器的自动最小尺寸本就是 0）。
注释写错比没有注释更糟——下一个维护者会照着错误结论去改。

### 19. 探针自身的三个静默失败（都是「绿着绿着就错了」）
1. **双重 JSON.parse**。CDP 助手 `evalJs()` 通常已经 `JSON.parse` 过返回值了，
   外面再 parse 一次：`JSON.parse(JSON.parse('[]'))` → `JSON.parse([])` →
   `Unexpected end of JSON input`（因为 `[].toString() === ''`）。
   规则：**要么助手返回原文、外面 parse；要么助手 parse、外面直接用，绝不两边都 parse。**
2. **块类型写错不报错，只渲染 `undefined`**。声明式渲染器里把
   `{type:'table', cols, rows}` 误写成 `{type:'card', cols, rows}`，cols/rows 被忽略，
   `card-body` 的文本变成字符串 `"undefined"` —— 它**绕过了「空卡片」断言**
   （`textContent.trim()===''` 为假）。空内容断言必须同时拒掉 `'undefined'` / `'null'`，
   并额外断言「每个表格块真的产出了 `tbody tr`」。
3. **选择器把设计意图内的局部滚动算成溢出**。量「容器内横向溢出」时只选叶子组件
   （`.card / .banner / .preview / .cap`），把 `.table-scroll` 这类滚动容器排除在外。
   反向的坑同样致命：`overflow: hidden` 的父级不会报 `scrollWidth > clientWidth`，
   所以**长 token 撑破卡片只在叶子层级能量到**——要挑最内层那个 flex 子项。
   常见元凶：`white-space: nowrap` 的徽标/代码片段。修法是给它
   `white-space: normal; overflow-wrap: anywhere; min-width: 0; flex: 1 1 auto`。

### 20. 多维筛选状态不要跨维度复用
把「筛选条」做成模块级 `let CF` 全局状态、而筛选 UI 只出现在某一个页面上时，
用户在那一页筛完再切到别的页，**别的页会被静默过滤**，且界面上找不到原因
（筛选条不在这一页）。规则：筛选只作用于拥有筛选 UI 的那个视图；
子视图要么自带一份状态，要么显式忽略全局筛选。

## 目录约定

```
panel/
  index.html
  bridge/  <name>_bridge.py  README.md  config.example.json  config.local.json  recon.py
  tests/   smoke.cjs  bridge.cjs  syntax.cjs  run-all.cjs  review-metrics.cjs  *.log
  tools/   browser-probe.cjs  (其它一次性探针)
```

## 环境坑（Windows）

- **Bash shim 可能不可用**（`dirname: command not found`）→ 一律走 PowerShell。
- **PowerShell 的 stdout 可能完全不回传**（命令退出码正常但看不到任何输出）→
  所有需要看结果的原生命令都必须**落盘到临时文件再 Read**，不要靠 stdout 判断成功与否。
- **PowerShell 在原生进程后会中断后续语句** → 同上，落盘。
- **强制安全删除策略**：`Remove-Item` 会走回收站，回收站机制失败时报
  `[safe-delete][SAFE_DELETE_FAIL_CLOSED]` 并**拒绝兜底删除**。
  这是保护机制，**不要绕过**；清理不了就如实告知用户残留了哪些文件。
- **沙箱可能拦截 `reg.exe`**，导致 `npm install` 直接失败 → 优先复用已装依赖。
- **沙箱常拦截 `~/.ssh/*`**：`ssh.exe` 会读密钥目录被拦；改用 paramiko 并显式
  `look_for_keys=False` / `allow_agent=False` / **不调** `load_system_host_keys()`
  后**仍可能**被按路径规则预判拦截（策略级，不是行为级）。
  被明确拒绝后**不要重试、不要换等价写法**，改为「不需要远端权限」的方案推进，
  并把三条可选路径交给用户决定。
- 需要 paramiko / pymysql 时用隔离 venv 安装，不要污染系统 Python。
- jsdom 常位于某个共享 `node_modules`，运行时设 `NODE_PATH`。

## 交付前自检清单

- [ ] `node tests/run-all.cjs` → `ALL SUITES PASSED`
- [ ] 浏览器探针：全宽度无横向溢出、无未命名按钮、0 异常（预期内的 403 单独计数）
- [ ] 对比度全部 ≥ 阈值（明/暗两种主题都测；**点开才出现的组件**也要单独取样）
- [ ] 文档内无重复 id
- [ ] 每个未接入操作都有 `data-*-path` 且已在清单登记
- [ ] 清单里明确区分 `pending`（待接入）与 `mock`（已模拟）
- [ ] 有桥接层时：前后端清单**逐项比对通过**，46 个接口逐个真实调用通过
- [ ] 桥接层：写操作返回 403 + dry-run（不静默、不转发），并发 32 连击无失败
- [ ] 前端：`?api=none` 强制离线可用；探针不因本机跑着服务而漂移
- [ ] 交付图轮次：显式设主题、清空交互状态，且每条 `[shot]` 日志带当时主题 + 计算底色
- [ ] 交付图轮次：长图高度随页面内容变化（全部相同 ⇒ 外壳仍在裁剪，先修再交）
- [ ] 任何「为什么 work」的代码注释都经过变体对照验证，不是凭印象写的
- [ ] **是「重设计」还是「换皮」？** 拿这条自检：把新稿和原稿的**导航分组名逐条念一遍** ——
      如果分组仍然是对方的产品结构（模块名、标签页名照抄），那就只是换皮。
      真重设计会重划边界（例如从「代码模块」改成「用户的作业域」），导航本身就是论据。
- [ ] 测试用完后清理自己产生的一次性脚本（清不掉就如实说明）
- [ ] 交付目录里不混入暂存文件 / 中间产物（拼接用的 `.js` `.py` `.txt` 一律不留；
      用户说「只留 html」时尤其注意，删不掉就如实列出文件名）
