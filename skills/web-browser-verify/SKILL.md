---
name: web-browser-verify
description: 在本机（Windows + 无外网下载条件）对本地运行的网页/SPA 做真实的浏览器渲染与交互验证——截图、点按钮、开弹层、读控制台报错。当需要确认「页面是不是白屏」「改了前端后界面有没有崩」「某个按钮/弹层能不能正常出现」，且 agent-browser / playwright CLI 因浏览器下载失败或启动失败不可用时，用本技能。触发词：白屏、页面渲染、截图验证、点开弹层、前端实测、控制台报错、headless 验证。
agent_created: true
---

# 用本地 Chromium + CDP 实测网页

## 什么时候用

- 改完前端要确认**页面真的渲染出来了**（不是白屏）
- 要确认某个**交互**有效：点按钮 → 弹层出现、弹层能关、表单能填
- 要抓**浏览器控制台异常**（`tsc` 和构建都不会告诉你运行时报错）
- `agent-browser` 起不来、`playwright` CLI 装不上（本环境 storage.googleapis.com 超时）

## 第一步：找到可用的浏览器

不要急着下载。**先看缓存里有没有现成的**（本机就有）：

```bash
ls ~/AppData/Local/ms-playwright/            # 期望看到 chromium-<build>
ls ~/AppData/Local/ms-playwright/chromium-*/chrome-win64/chrome.exe
```

拿到路径后记为 `$CH`。若确实没有，再退回系统浏览器：

```bash
ls "/c/Program Files/Google/Chrome/Application/chrome.exe"
ls "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
```

## 第二步：只要截图 → 一条命令

```bash
export PATH="/usr/bin:/bin:$PATH"
"$CH" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --window-size=1600,1000 --virtual-time-budget=10000 \
  --screenshot="C:/tmp/shot.png" "http://127.0.0.1:8088/"
```

`--virtual-time-budget` 让页面把 JS 跑完再截，SPA 必须给（8~10 秒）。

截图文件大小能直接判断成败：**几十 KB 基本就是白屏**，几百 KB 才有内容。然后再用 Read 工具把 PNG 读出来**亲眼看**。

## 第三步：要交互 → CDP + Node 内置 WebSocket

**不需要** `npm i puppeteer` 或 `playwright`。Node 22 自带全局 `WebSocket` 和 `fetch`，够用。

```js
// cdp.mjs —— 用 managed node 跑: C:/Users/<u>/.workbuddy/binaries/node/versions/22.22.2-3/node.exe cdp.mjs
import { spawn } from 'node:child_process'
import { setTimeout as sleep } from 'node:timers/promises'
import { writeFileSync } from 'node:fs'

const CH = process.env.HOME + '/AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe'
const PORT = 9222

const chrome = spawn(CH, [
  '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
  '--no-proxy-server',              // ← 必加，见下方「坑」
  '--disable-http-cache',           // ← 必加
  `--remote-debugging-port=${PORT}`,
  '--user-data-dir=C:/tmp/cdp-profile',
  '--window-size=1600,1000', 'about:blank',
], { stdio: 'ignore' })

// 等 CDP 起来
let page
for (let i = 0; i < 80 && !page; i++) {
  try {
    const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()
    page = list.find((t) => t.type === 'page' && t.webSocketDebuggerUrl)
  } catch { /* 还没起来 */ }
  if (!page) await sleep(300)
}

const ws = new WebSocket(page.webSocketDebuggerUrl)
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej })

let id = 0
const pending = new Map()
const exceptions = []
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data)
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id) }
  if (m.method === 'Runtime.exceptionThrown')
    exceptions.push(m.params.exceptionDetails?.exception?.description || m.params.exceptionDetails?.text)
}
const send = (method, params = {}) =>
  new Promise((res) => { const n = ++id; pending.set(n, res); ws.send(JSON.stringify({ id: n, method, params })) })

const js = async (expr) =>
  (await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true }))
    .result?.result?.value
const shot = async (file) => {
  const r = await send('Page.captureScreenshot', { format: 'png' })
  writeFileSync(file, Buffer.from(r.result.data, 'base64'))
}

await send('Page.enable'); await send('Runtime.enable')
await send('Page.navigate', { url: 'http://127.0.0.1:8088/' })
await sleep(7000)                                  // SPA 首屏 + 懒加载

// 点一个按钮
await js(`[...document.querySelectorAll('button')].find(b => b.textContent.includes('创建'))?.click()`)
await sleep(1200)

// 检查结果 —— 关键：把真实 DOM 结构读回来，而不是猜
console.log(await js(`(() => {
  const ov = document.querySelector('.modal-overlay')
  if (!ov) return 'NO MODAL'
  const p = ov.firstElementChild
  return 'overlay > .' + p.className + ' maxWidth=' + getComputedStyle(p).maxWidth
       + ' | ' + JSON.stringify(ov.innerText.replace(/\\n+/g, ' / ').slice(0, 120))
})()`))
await shot('C:/tmp/modal.png')

console.log('异常:', exceptions.length ? exceptions.join('\n') : '(无)')
ws.close(); chrome.kill(); process.exit(0)   // 必须显式 exit，否则子进程挂着
```

## 必踩的坑

| 现象 | 原因 | 解法 |
|---|---|---|
| `ERR_CONNECTION_REFUSED`、资源全挂 | Chrome 走了**系统代理**（本机是 `127.0.0.1:56231`），代理没跑 | Chrome 加 `--no-proxy-server` |
| 页面加载的是**旧版本**、报错里出现磁盘上已不存在的旧哈希文件名 | HTTP/磁盘缓存命中了旧 `index.html` | 加 `--disable-http-cache` + `Network.setCacheDisabled`，或 URL 加 `?t=<时间戳>` |
| 脚本跑完不退出 | Chrome 子进程还活着 | 结尾 `chrome.kill()` + `process.exit(0)` |
| 按钮点了没反应 | 按钮**是 disabled 的**（业务前置条件没满足） | 先 `if (b.disabled) return 'disabled'` 顺手报出来，别默认代码有 bug |
| 找不到要点的元素 | 选择器猜错了 | 先**探测**：`[...document.querySelectorAll('*')].filter(e=>e.textContent.trim()==='X'&&!e.children.length).map(e=>e.tagName+'.'+e.className+' < '+e.parentElement.className)`，拿到真实 class 再点 |

## 判断「白屏」的正确方法

1. 截图文件大小（几十 KB = 可疑）
2. `console.log(await js('document.querySelector("#root").innerHTML.length'))`
3. `console.log(await js('document.title'))`
4. 收集 `Runtime.exceptionThrown` + `Log.entryAdded`（level=error）

**只 `curl` 拿到 HTTP 200 不能证明页面可用**——之前就因此误判过一次（`-w "%{http_code}"` 显示 200、但 `size_download` 是 0）。要么看 `Content-Length` 响应头，要么真跑浏览器。

## 附带技巧：纯函数逻辑用 Node 直接跑，不用开浏览器

格式化/计算这类纯函数，不需要浏览器。Node ≥ 22 自带类型擦除，可以直接 import `.ts`：

```bash
node --experimental-strip-types scripts/selftest.mts     # .mts 里 import '../src/lib/format.ts'
```

要点：
- 断言要写成**与运行环境无关**的形式。时区尤其坑：`new Date(ts).getHours()` 的结果依赖本机时区，
  硬编码 `'11:20'` 的期望值会错。改成断言"毫秒/秒两条路径结果一致"、"格式形状正则匹配"、"切片长度等于 11"。
- 测试脚本放 `scripts/` 而不是 `src/`：多数项目的 `tsconfig.include` 只有 `"src"`，
  放 src 里会被 `tsc --noEmit` 卷进构建。
- 顺手在 `package.json` 加一条 `"test:format": "node --experimental-strip-types scripts/xxx.mts"`，
  让下一个人能直接跑。

## 长命令：构建/安装一律丢后台

本环境里 `npm run build` 在前台跑容易被 SIGTERM 打断（输出为空、exit 1）。
用后台执行（`run_in_background`），完成后再取输出——不要前台硬等。
`vite build` 大约 16~45 秒。

## 注意

- `--user-data-dir` 每次用不同目录，避免上一次的缓存/锁残留。
- 项目的 `.dockerignore`/`.gitignore` 不会替你清理，脚本和截图**用完要删**，别留在源码目录里。
- 若部署的是 `web/dist` 且后端用 `http.FileServer` 磁盘热读，**重跑 `npm run build` 后不必重启后端**，刷新即可；但浏览器要禁缓存才看得到。
