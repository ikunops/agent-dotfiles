# 各语言/框架的水流锚点表（trace markers）

> 水流追踪不依赖具体框架，依赖每个生态的**显眼标记**。任何语言都分三类锚点：
> ① **注册表标记**——功能挂上总线的地方（路由/菜单/命令/消费者注册），顺着它列出全部入口节点；
> ② **流转标记**——控制权/数据从一个节点跳到下一个（事件、emit、channel、调用约定），顺着它把链走通；
> ③ **终止标记**——真 IO（网络/磁盘/进程/FFI），见到即到底，记下函数名收工。
>
> 用法：确定目标生态 → 按表选 grep 模式 → ①列全部入口 → ②逐跳走链 → ③判终止。grep 命中即证据（file:line）。

## 前端

| 生态 | ① 注册表（找入口） | ② 流转（走链） | ③ 终止（真 IO） |
|---|---|---|---|
| Vue 2/3 | `createRouter`、`routes:`、`defineEmits`、组件注册表、菜单数据 | `@click="fn"`、`emit("x")`、`watch(`、`provide/inject`、`v-model` → setter、Pinia `defineStore` 内 action | `fetch(`、`axios.`、`invoke(`、`WebSocket(`、localStorage 封装 |
| React/Next | `App Router` 文件树、`<Route`、`createBrowserRouter`、菜单/导航配置、Context.Provider | `onClick={fn}`、`dispatch(`、`useEffect(`、props 回调名 grep、Redux `createSlice`、zustand `create(` | `fetch(`、`axios(`、`useQuery` 的 queryFn、`EventSource(`、`localStorage.` |
| Angular | `Routes`、`@NgModule` 声明、菜单组件 | `(click)="fn"`、`@Output()` + `EventEmitter`、RxJS `.subscribe(`、服务注入 `constructor(private x: XService)` | `HttpClient.`（get/post…）、`WebSocket` |
| Svelte/Solid | 路由文件、`<Router` | `on:click`、`dispatch(`、`$:` 响应式、store 订阅 | `fetch(` |
| 原生 JS/jQuery/桌面 Web | `addEventListener` 集中注册区、`data-*` 委托、`customElements.define` | `addEventListener("click"`、`$.on(`、CustomEvent `dispatchEvent` | `fetch`、`XMLHttpRequest`、`$.ajax`、`navigator.sendBeacon` |
| Electron/Tauri/VSCode 插件 | `ipcMain.handle(`、`invoke` 命令注册、`commands`（VSCode）、`registerCommand` | `ipcRenderer.send/invoke` ↔ `ipcMain.handle` 两头对 grep、`webContents.send` | `fs.`、`net.`、shell 命令、`invoke` 落到 Rust/原生 |
| Flutter | `MaterialApp(routes:)`、`go_router` 配置、`Menu`/`onPressed` 集中区 | `onPressed: ()`、`Navigator.push`、Provider/Riverpod `ref.read`、Bloc `add(Event)` | `http.`、`dio.`、`MethodChannel`（进原生） |

## 后端

| 生态 | ① 注册表（找入口） | ② 流转（走链） | ③ 终止（真 IO） |
|---|---|---|---|
| Go (net/http/gin/echo) | `http.HandleFunc(`、`r.GET/POST(`、`Group(`、`swagger` 注释 | 普通函数调用（IDE/grep 函数名）、middleware 链 `.Use(`、`context` 传递 | `sql.DB Query/Exec`、`redis.Client`、`http.Client.Do`、`os.`、`exec.Command`、goroutine `go func`（并行岔路，也要入账） |
| Java Spring | `@RestController/@Controller`、`@GetMapping…@RequestMapping`、`application.yml`、`@Scheduled`、`@KafkaListener/@RabbitListener` | `@Autowired`/构造注入 → 接口 grep 实现类、`@Transactional` 边界、AOP 切面 | MyBatis mapper XML/注解、JPA `Repository`、`RestTemplate/WebClient`、`JdbcTemplate`、`Files.` |
| Python (FastAPI/Flask/Django) | `@router.get/@app.route`、`urls.py`/`include()`、`APIRouter(`、`@celery.task`、管理命令注册 | 依赖注入 `Depends(`、service 层函数调用、Django `get_object_or_404` 等 ORM 链 | SQLAlchemy `session.execute`、`requests.`/`httpx.`、`subprocess`、`open(`、`boto3` |
| Node (Express/Nest) | `app.get/post(`、`router.use`、Nest `@Controller/@Get`、`module` 声明 | 中间件 `next()`、service 注入、事件总线 `emitter.on(` | `pg/knex/prisma/mongoose` 调用、`fetch/axios`、`fs.`、`child_process` |
| Rust (axum/actix/tauri) | `Router::new().route(`、`#[get("/…")]`、**`#[tauri::command]`**（dbx 即此）、` cargo workspace 成员清单 | 函数调用、`Result<? , E>` 传播、trait `impl` grep、channel `tx.send/rx.recv` | `sqlx/query!`、`reqwest`、`std::fs`、`tokio::process`、FFI `extern` |
| C#/.NET | `[ApiController]`、`[HttpGet("[route]")]`、`Program.cs`/`Startup.cs` 管道、`services.AddXxx` | 构造注入接口 → grep `: IXxx` 实现、MediatR `IRequest` | EF `DbContext`、Dapper、`HttpClient`、`File.` |
| PHP (Laravel/Symfony) | `routes/web.php`、`Route::get`、`#[Route]`、控制器方法名即路由一部分 | 服务容器 `app(Xxx::class)`、事件/监听器 `Event::listen` | Eloquent `::where`、DB facade、`Http::`、`Storage::` |
| Ruby (Rails) | `config/routes.rb`（`resources :x` 一行=7 入口）、引擎挂载 | controller→model 约定调用、ActiveSupport callbacks | ActiveRecord 模型方法、`Net::HTTP`、sidekiq worker |
| gRPC/Thrift | `.proto` 的 `rpc Foo(`（每个 rpc 是一个入口节点）、service 生成代码 | stub→server impl 两头 grep 同名方法 | 同宿主语言的 IO 层 |
| GraphQL | `type Query/type Mutation` 字段、resolver 注册表 | resolver → service 调用 | DataLoader/DB 调用 |
| 定时/队列/流（所有语言通用） | cron 表达式、`@Scheduled`/`@cron`、`celery task`、MQ consumer 订阅、`SUBSCRIBE`/`Stream` 消费组 | 消息体 schema → 处理函数 | 同宿主 IO |

## 通用兜底（标记失效时）

- **从字符串反查**：路由路径、事件名、命令名都是字符串，前后端 grep 同一字符串两头对上（dbx 的 `forward("executeQuery")` ↔ Rust `executeQuery` 即范例）。
- **从类型/schema 反查**：共享类型定义（TS interface ↔ Go struct json tag ↔ proto message）字段名 grep 两端。
- **从日志埋点反查**：`log("xxx:start")` 之类埋点是现成的流转证据。
- **依赖图兜底**：`goimports`/`depcheck`/`madge` 之类工具生成 import 图，验证"链上相邻节点确实互相引用"，防脑补。
