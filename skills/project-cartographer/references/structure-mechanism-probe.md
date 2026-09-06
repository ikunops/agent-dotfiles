# 结构机制提取法 —— 把"标签"倒模成"真结构"

> **适用问题类（不限树、不限本项目）**：参考项目把某个业务维度组织成了**结构**
> （层级 / 分组 / 步骤 / 级别 / 阶段），而我们的实现把它压扁成了**标签**
> （前缀、徽标、纯文本、装饰性分组头）。本篇给普适方法；dbx 模式层级作为
> 案例档案放在文末。同类任务映射：树层级=节点 type、右键菜单=条目分组字段、
> 向导=step 枚举、权限界面=role 常量、多栏布局=pane 类型——方法完全同构。

## 一、先判定：那是结构，还是装饰？

动手倒模前必须先回答。唯一判据：

**对该维度下的对象做操作时，这个维度是否参与寻址？**
（寻址 = 出现在 API 参数、请求路径、事件上下文、数据契约字段里）

- **参与寻址 → 真结构**：节点有自己的身份和上下文，压扁它等于丢功能。
- **不参与 → 装饰**：只是显示层的东西，压扁无碍，也别为它建空层级。

正例：点击"打开表"的操作上下文里带 schema 字段 → 模式是真结构。
反例：表名显示成 `public.users` 前缀，但点击只传表名 → 前缀只是装饰。

## 二、四个锚点：沿数据流倒着抓，永不通读大组件

参考项目的大组件动辄几千行（dbx 的树组件 2900 行），通读必输。
任何生态、任何结构类型，按数据流反向抓四个点，一两个小时内出结论：

1. **身份锚点** —— grep 类型字面量。
   `type: "schema"` / `"group-tables"` 这类 union/enum/常量集只在
   ①节点构造处、②事件分发处出现，一抓一个准（排除 `__tests__`）。
   得到：这个结构一共有哪几种节点（=节点词汇表）。
2. **分发锚点** —— 找"UI 事件 → 按节点类型路由到哪个 loader"的 if/else 链
   （搜 `node.type === "..."`，通常在 store/composable 的 expand/click 处理里）。
   这一段就是整个结构的行为规范，一段顶一万行。
3. **回退锚点** —— 顺着分发链读每个 loader，**必看"列表为空/失败时走哪条路"**。
   回退分支是原作者踩坑后补的防呆，往往也是能力判定逻辑的藏身处；
   照抄回退能避免"支持面窄的引擎展开成空节点"这类事故。
4. **契约锚点** —— loader 调用的纯函数 builder（看函数签名和节点字段）。
   节点携带哪些上下文字段 = 下游所有操作（点击/右键/导出/查询）的数据契约。
   字段没带全，下游操作必然断。

## 三、能力判定：三档取其动态

结构是否出现，谁来决定？按动态程度三档，取代价可接受的最动态一档：

| 档 | 方式 | 特点 |
|---|---|---|
| 1 | **运行时探测**：加载一次列表，空 = 无此层级 | 最动态；新引擎/新数据源零改动接入 |
| 2 | **类型注册表**：引擎→能力在一处声明 | 需要显式声明时用；一处维护 |
| 3 | 前端硬编码名单 | 永远是下策，只配当兜底 |

dbx 取 2+1（已知引擎用名单、未知 JDBC 驱动用探测兜底）；
opscore 已有探测接口，直接全走 1。

## 四、移植裁决：不变量带走，实现细节重写

从案例里分清两类东西，这是倒模不走样的核心：

**不变量（机制，必须保留）**
- 维度成为真节点，且节点携带完整上下文字段（契约锚点抄来的那份）
- 空探测回退（回退锚点抄来的那份）
- 单加载器两用：被压扁的维度只是加载器的可选参数，不做两套代码
- 下游契约用限定标识符（如 `schema.table` 两段名），显示与存储分离

**实现细节（按己方约束重写）**
- 探测时机与缓存粒度、图标、显示裸名还是全名、
  全量加载+客户端过滤 vs 逐级请求、右键菜单的具体条目

**自检一句话：换一个引擎 / 数据源 / 维度，这条设计还成立吗？**
成立 = 机制，带走；不成立 = 细节，重写。

---

## 案例档案：dbx 库→模式→表 层级（证据，2026-09 实测）

**怎么抓到的**（四锚点实录，可复用到任何 Vue/React 项目）：
1. 身份：`grep -rn 'type: "schema"' --include="*.ts" --include="*.vue"`（排除 __tests__）
   → 命中 `stores/connectionStore.ts` 两处构造 + 渲染层若干
2. 分发：`connectionStore.ts:6626` 展开分发链——
   `usesTreeSchemaMode(引擎) || connectionShouldDiscoverJdbcSchemas` → `loadSchemas(库)`；否则 → `loadTables(库)` 平铺
3. 回退：`loadSchemas`（:5068）里 `listSchemaInfos(库)` 为空 → 回退 `loadTables` 平铺。
   原注释："keep the legacy flat object tree when it reports none so
   non-schema engines do not expand into an empty node"
4. 契约：schema 节点携带 `{connectionId, database, schema}`；对象加载器
   `loadTables(conn, db, schema?)` 第三参可选两用；搜索 scope 里 schema 也是一级
   （`SearchScope = "connection" | "database" | "schema" | "table" | "view"`）

**机制摘要**：库展开 → 有模式列表则每个模式生成 `type:"schema"` 真节点
（id=`conn:db:schema`），展开模式 → `loadTables(conn, db, node.schema)`；
下游打开表/右键/查询从节点上下文拼 `"schema"."table"` 限定名。

**移植到 opscore 的裁决记录**：
- 不变量全保留：真节点+上下文、空回退平铺、单加载器两用（我们的
  `listTables(库)` 全量加载后模式节点做客户端前缀过滤，不再逐模式请求）、
  `table` 字段存限定名而显示裸名（/data、describe、导出已支持两段名，零改动）
- 细节重写：dbx 名单判定+探测兜底 → 我们全走运行时探测（`/api/dbmanager/schemas`
  能力接口，空数组=平铺）；探测时机=连接展开时一次并缓存
- 自检通过：换任何引擎，"探测非空出层级、空则平铺"依然成立

## 案例档案二：单元格/行/列 详情卡片（证据，2026-09 实测）

**问题**：我们的单元格详情只有"列名+原始值"两行；dbx 是结构卡片：
列名 / 行号 / 类型 / 长度 / 注释 / 值，且右键另有列详情、行详情。

**四锚点实录**：
1. 身份：`grep -rln "cellDetail\|CellDetail"` → `components/grid/DataGridCellDetailDialog.vue`
   + `lib/dataGrid/dataGridDetail.ts`（类型与构建器分文件——UI 与数据解耦）
2. 分发：DataGrid 内右键项 setDetail/setRowDetail/setColumnDetail → 同一 Dialog 组件按 detail 类型渲染
3. 契约（本案例的核心发现）：`DataGridCellDetail` 接口 15 个字段，
   三个构建函数共用一个原子构建器：
   - `buildDataGridCellDetail(行,列)` → 单格信息
   - `buildDataGridRowDetail` = 每列各 build 一次 → fields 数组
   - `buildDataGridColumnDetail` = 同列每行 build 一次 → fields 数组
   **详情不是三套实现，是一个原子构建器的三种聚合方向。**
4. 回退/元数据来源（零后端调用）：
   - 类型 = `typeByColumn(表元数据优先) ?? resultColumnTypes(结果集推断兜底)`
   - 注释 = `commentByColumn`，无则显示"暂无注释"
   - **长度 = `String(value).length`——是值的长度不是列定义长度**，
     猜"要查 information_schema"就会去加后端接口，看了源码才知道是纯前端
   - 值分层: raw/display/preview(12000 截断)/formattedJson(美化开关)/图片预览/二进制下载

**移植到 opscore 的裁决**：
- 不变量照抄：原子构建器 `buildCellInfo(r,c)` + 三种聚合；元数据分层
  （describe 优先/结果集兜底）；"暂无注释"占位；行/列详情带过滤与
  复制 JSON/TSV；复制列名进底部操作区
- 细节重写：Dialog→轻量 portal 卡片（无 reka-ui）；JSON 美化/图片/二进制
  预览暂不做（YAGNI，等有真实需求）
- 关键实现路径：DataPanel 原本就调了 describeTable 却只留 type 字符串——
  完整 ColumnInfo（注释/可空/键）本来就在手里，只是没人去接

## 验尸记录（防再犯）

- feature-matrix.md 早记了"⚠️ 缺 schema 层"缺口，但没记参考项目的实现方式，
  缺口躺了几个迭代。**教训：台账里每个对比项，至少写一行实现方式指向
  源码位置（文件:行号 + 函数名）**——台账管"有没有"，锚点档案管"怎么做"。
- 反面教材（本文初版）：把方法写死成"dbx 怎么做"，例子缠着方法论。
  修订原则：方法论必须能脱离案例独立执行，案例只是方法论的一次代入验证。
