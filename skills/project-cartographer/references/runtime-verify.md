# 运行时实测 — 交互点闭环的第二级验证

> 常见静默假设：**静态走通 + 后端 curl 200 ≈ 交互正常**。这个假设会漏一类 bug。
> 真实案例（opscore 日志按钮）：`fetchLog → /pod/log → 后端函数` 链路静态通，`curl` 实测后端 `ok:True`（1478B），全绿。但浏览器里点「日志」无反应——根因在**渲染层**：回调触发了、请求发出去了，但输出没落点（弹层未挂载 / setState 后无渲染 / 样式溢出盖住），这类只在浏览器运行时暴露。

## 一、什么时候必须做运行时实测

交互点（按钮 / 右键项 / 输入框 / 弹层）命中任意一条：

- 用户报过「点了没反应 / 点了没变化 / 无输出 / 卡住」；
- 静态链路有多跳前端→后端且中间有异步（`fetch().then().catch()` / promise）；
- 交互点与落点不在一处（点按钮 → 开弹层，弹层按别的条件挂载）；
- 交互涉及 WS（连接成功≠界面可用，看连接后的渲染与帧解析）。

## 二、怎么实测（配浏览器自动化 skill：agent-browser / browser-use）

1. **导航到真实页面**，走真实登录态（非 dev mock）。
2. **点击目标交互点**，同时开 DevTools 抓三条线：
   - **Console**：红字 / uncaught / CSP；
   - **Network**：请求发了没、URL+状态码、是否 pending；
   - **DOM**：应出现的弹层 / 输出节点挂载了没。
3. **三线对账**，结论落台账：
   - 期望界面出现了吗？
   - 后端收到请求了吗（Network URL + 状态码）？
   - Console 有异常吗？
4. **分类**（对应 debug-and-refactor 的事件层 / 样式层二分）：
   - **事件层**：请求根本没发 → 回调没绑上 / 被遮挡层吃掉点击；
   - **渲染层**：请求发了、后端 200、界面却没变化 → 弹层无落点 / setState 后不渲染 / 溢出被藏住；
   - **契约层**：请求发了、后端 4xx → 前后端参数名 / 契约不匹配。

## 二·五、后端契约直探（跳过 UI 验后端，运行时实测的第一刀）

浏览器实测前/失败后，先用**最小客户端直连后端端点**，把"后端是否正常"这一变量独立出来。别再绕 UI 猜链条。两种协议：

**HTTP 探针**（前端明明有请求参数就去造假请求）：

```bash
# ① 从前端调用处抠出真实 URL+参数（grep 调用点, 别脑补参数名）
grep -n "pod/log" web/src/modules/K8sModule.tsx
# ② 原样复刻请求(含参数名/值), 观察 ok 字段而非只兑 200
curl -s "http://127.0.0.1:8088/api/plugins/containers/k8s/pod/log?cluster=1&ns=default&name=$pod&container=&tail=200" | python3 -c "import json,sys;d=json.load(sys.stdin);print('ok:',d.get('ok'),'bytes:',len(d.get('log') or ''))"
```

铁律：**参数名以调用方为准**（前端写 `name=` 就发 `name=`，别自创 `pod=`）；返回体若带 `ok:false` 还配 `error`，那才是契约层的实锤。**一次测一个端点**，别一根 curl 测三个路由，逐一归因断在哪一跳。

**WS 探针**（流式日志/终端这类走 WS 的，前端 UI 测不出协议问题，必须独立客户端打帧，如 gorilla/websocket 的 Go 客户端）：

```bash
# 独立小客户端: dial ws://127.0.0.1:PORT/path?params
# ① 连接 + 读原始帧 (json: {type, data}) —— 别在浏览器 F12 里戳, 直接程序里看字节
# ② 发一帧 stdin (如 "echo MARK1\n") → 读回帧: 应见 echo→输出→新提示符 三段
# ③ 帧归因: 提示符若含 \x1b[6n 等控制序列, 属 shell 发给终端的光标查询 → 前端需吞掉,
#    不是后端 bug; 输入帧若两段重复 = 前端 TTY echo 与后端 echo 叠加(前端多管了一次)
```

```go
// 探针骨架 (发 stdin→收 frames), 可按此扩成模板:
c, _, _ := websocket.DefaultDialer.Dial(u, nil)
defer c.Close()
c.WriteJSON(map[string]any{"type": "stdin", "data": "echo MARK1\n"})
for {
  _, data, err := c.ReadMessage()   // json: {type,data,...}
  if err != nil { break }
  fmt.Printf("FRAME %s\n", data)    // 逐字节看 data, 区分 UI 层 vs 传输层
}
```

WS 判据表（人肉对帧）：

| 现象 | 归因 |
|---|---|
| 连接建立但一帧不来 | 服务端没进读循环 / 权限链断了，属后端 |
| 帧来了带控制字符（`\x1b[6n`/`\x1b[2J`）| shell 发给终端的光标/清屏序列，终端该应答或吞掉，**不是后端错** |
| 输入 send 一次、收到两份回显 | TTY echo + 前端手动 append 双重回显，前端 bug |
| 数据两帧拼接错位 | `lines.join('')`/append 时序，前端渲染 bug |

> 原则：**HTTP 先煲后端, WS 再煲协议**——后端窖（闭环）由 HTTP 直探判定；WS 只归因协议层，剩下的渲染层再回浏览器三线。

## 三、台账状态细化（关键）

**静态联通 ≠ 运行时闭环。**

- `✅ 静态联通` — 链条走到后端函数名、有 file:line 证据，但**浏览器没跑过**。这是交互点的**默认**状态，不算完成。
- `🚧 待运行时验证` — 静态通了，命中第二节任一条件，明确欠一场浏览器实测。
- `✅ 运行时实测` — 真机 / headless 点过，Console / Network / DOM 三线正常。

判法：链接续到后端函数名只证明"这条路在代码里存在"，不证明"在浏览器里点得动"。把静态车通直接标 `✅ 已测绘` 就是这类 bug 漏网的根源。

> 交互点若走 WS/流式（日志跟随、终端、事件流），`✅ 运行时实测` 必须含**独立 WS 探针成功打帧**（见二·五），浏览器三线正常 ≠ WS 帧层无异常。

## 四、产物

- 实测抓到的 Console / Network 摘录、DOM 断言写进 `_receipt.md`（可复跑）。
- WS 探针收到的原始帧样本（贴关键 3~5 帧）、HTTP 直探的 `ok` 字段值，一并入 `_receipt.md`。
- 台账里 `✅ 已测绘` 的交互点不带"已实测"字样 = 未实测，概览要如实说明覆盖范围。