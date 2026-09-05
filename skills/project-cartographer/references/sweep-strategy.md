# 扫荡策略：怎么找入口和层级

按目标项目的技术栈挑对应小节读。找不到完全匹配的框架时，找"同类项"——大多数框架的入口都是"注册表"模式：总有一个文件集中声明了路由/菜单/模块清单，从那里开始画第一层。

## 通用技巧

- **先找注册表**：路由注册、菜单配置、模块声明、依赖注入容器配置，这些文件就是迷宫的"总入口图"。
- **顺着调用链往下，顺着数据流往上**：一个 API 从路由到数据库的调用链，和一条数据从数据库到按钮的渲染链，是同一座迷宫的两面。
- **目录结构≠功能层级**。目录经常按技术分层（controllers/ services/），而功能层级是按业务切的（设备管理下含增删改查）。地图要按**业务层级**画，目录路径只是节点的属性之一。
- **用 grep 销账而不是靠记忆**：找某 API 的所有前端调用点，grep 它的路径字符串；找某组件的使用者，grep 组件名。grep 结果为空本身就是一个发现（可能是死代码）。
- **对照 UI 文案与数据层行为**：页面里的"每 30s 刷新""实时更新"之类承诺，去数据层核对是否真的配了轮询/订阅；反过来数据层有而 UI 没消费的能力也要记一笔。这类"指示牌与实况不符"往往是体检模式里最值钱的发现。

## 水流追踪技巧（C 型功能流怎么做）

**从事件属性反查处理函数**：Vue 用 `@click="fn"` / `emit("x")`，React 用 `onClick={fn}`，Qt 用 `connect(...)`。grep 事件名逐跳往下：

```
grep '@open-data' → ConnectionTree.vue:2485 → openSidebarData (ConnectionTree.vue:2061)
grep 'function openSidebarData' → 调 useSidebarDataOpenRuntime → grep 'queryStore\.' 该 composable
→ queryStore.createTab / executeTabSql → grep 'api.executeQuery' lib/backend/api.ts → forward("executeQuery") → Rust
```

**每跳必须留 file:line**。允许自己偷懒不留证据的链路，就是会脑补的链路。

**emit 链在 Vue 大组件里会断**：处理函数常在父级（App.vue / 布局组件）。追法：`grep -rn '@event-name'` 找监听者，`grep -rn 'emit("event-name"'` 找发射者，两头对上才算接通。

**store 是水流的中转站**：交互点 → store 动作 → api 门面是最常见的三段式。在 store 里 grep `api\.[a-zA-Z]+` 就能列出它触达的所有后端函数，这是把 UI 链接到后端最快的桥。

**终止判据**（C 型流的两种合法终点）：
- UI 叶子：`set()` 本地状态 / 纯展示 / CSS 效果——写明"纯本地，无出站调用"。
- 后端函数：门面导出名 + 传输命令名（invoke 命令或 HTTP 路径）——写到名字为止，Rust 内部属于另一张图。

**防循环**：链路出现环（A→B→A）时画环、标"循环至条件退出"，不要无限展开。watcher/事件总线造成的隐式流，用 `watch(`、`on(`、事件名 grep 兜底。

## 后端常见形态

| 形态 | 入口注册表 | 层级链 |
|---|---|---|
| Express / Koa / Nest | app.ts 中间件挂载 / `@Controller` 装饰器 | 路由 → 控制器 → 服务 → ORM 模型 |
| FastAPI / Flask | 路由装饰器集中或 `include_router` | 路由 → 依赖项 → 服务 → 模型 |
| Spring Boot | `@RestController` 扫描、application.yml | Controller → Service → Repository → Entity |
| Django | urls.py（天然的注册表） | URL → View → Model/Serializer |
| Go (gin/echo) | 路由注册文件通常集中 | Handler → Service → Store |
| Electron / Tauri | 主进程 IPC handler 注册表 | IPC 通道 → 主进程模块 → 存储 |

额外要注意的后端岔路：定时任务（cron/scheduler）、WebSocket 通道、消息队列消费者、启动钩子（migration、seed）。这些不在 HTTP 路由表里，但都是功能——漏掉它们就是留了没标注的岔路。

## 前端常见形态

| 形态 | 入口注册表 | 层级链 |
|---|---|---|
| Vue / Nuxt | router/index、pages 目录约定、菜单配置 | 路由 → 页面 → 布局 → 组件 → 交互点 |
| React / Next.js | App Router 文件树、react-router 配置 | 同上 |
| Angular | AppRoutingModule、module 声明 | 同上 |
| Qt / GTK / 嵌入式 Web | 主窗口构建代码、菜单注册 | 窗口 → 面板 → 控件 |

**交互点是前端测绘的最深层**，逐页清点这几类：

1. **按钮/操作**：点击触发什么（API 调用 / 本地状态 / 弹窗）
2. **表格与列表**：数据来自哪个接口、行点击/右键菜单有哪些动作
3. **输入**：表单提交到哪、有无校验
4. **指示图/示波器/图表**：数据源是轮询还是推送（WebSocket/SSE），刷新频率
5. **导航类**：跳转到哪个路由、面包屑如何生成
6. **右键菜单**：桌面/富交互应用的重头。不要只记"某处有右键"——找到菜单项构建器（如 `buildContextMenu`/`menuItems`/菜单工厂），枚举到**菜单项清单级**（项名、危险项标记、子菜单、快捷键），并记清派发链：事件入口 → 构建器 → 危险操作的确认链。菜单即数据的项目里，菜单清单就是功能的完整倒影。

给每个交互点记两样东西：**触发词**（按钮文案/组件名，供 grep）和**它调用的后端端点**（映射矩阵的原料）。

## 单体仓库 / 前后端同仓

先在 `00-overview.md` 里画一张"仓库→应用"的第一层（apps/ packages/），再对每个应用分别走后端/前端扫荡。模块之间的引用（共享类型、共享组件）用一行注明"跨模块链接 → B-x / F-y"，不要展开复制对方的树。

## 规模控制

- 单节点指示牌控制在 15 行以内；细节属于代码，地图只管导航。
- 深度超过 4 层的节点，考虑把整棵子树压缩成一行死胡同牌："2.3.4 内部实现太细，展开见 `services/device/` 目录，按需再测绘"。
- 每测绘 20~30 个节点回头重读一次台账，检查有没有该合并、该升层的结构——地图画歪了越早发现越省。
