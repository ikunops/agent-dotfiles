# 树层级探测倒模法（dbx schema 层级实测记录）

> 场景：参考项目（dbx）的侧栏树对 PG 族是 `连接→库→模式→表` 三级命名，
> 我们却把模式前缀贴在表名上、丢掉了模式层级。本篇记录"怎么找"和"找到的方法"，
> 供任何"把 X 做成真层级节点"的倒模任务复用。

## 一、怎么找（十分钟定位法，普适）

前端树组件通常很大（dbx ConnectionTree.vue 2900 行），不要通读。按数据流倒着抓：

1. **grep 节点类型字符串**：`type: "schema"` / `"group-tables"` 这类字面量只会在
   ①节点构造处、②渲染分发处出现。`grep -rn 'type: "schema"' --include="*.ts" --include="*.vue"`，
   排除 `__tests__`。dbx 命中 `stores/connectionStore.ts` 两处 + 渲染层若干。
2. **找分发点（dispatcher）**：树组件里搜 `node.type === "schema"`，
   找到"展开节点时按类型路由到哪个 loader"的 if/else 链（dbx: `connectionStore.ts:6628`）。
   这一段就是整棵树的行为规范。
3. **找 loader 与它的回退**：顺着分发点读 loader（dbx: `loadSchemas`），
   **重点看"列表为空时干什么"**——空列表回退平铺才是防呆的关键设计。
4. **找 builder**：loader 调用的纯函数构建器（dbx: `buildTableTreeNodes({schema})`），
   看节点携带哪些上下文字段（dbx: `{connectionId, database, schema}`）。

## 二、找到的方法（dbx 原实现）

1. **展开库节点时按能力路由**（`connectionStore.ts:6626`）：
   ```ts
   if (usesTreeSchemaMode(dbType) || connectionShouldDiscoverJdbcSchemas(config)) {
     await loadSchemas(connId, database)      // 三级命名引擎
   } else {
     await loadTables(connId, database, undefined)  // 平铺
   }
   ```
2. **loadSchemas（:5068）**：`listSchemaInfos(库)` 有结果 → 每个模式生成
   `type:"schema"` 真节点（id=`conn:db:schema`，携带 database+schema 上下文）；
   **返回空 → 回退 `loadTables` 平铺**。原注释："keep the legacy flat object tree
   when it reports none so non-schema engines do not expand into an empty node"。
3. **一个加载器两用**：`loadTables(conn, db, schema?)` 第三参可选——
   库直下与模式内共用同一套对象加载/分组/渲染，schema 只是过滤条件。
4. **模式节点展开** → `loadTables(conn, db, node.schema)`，下游所有操作
   （打开表/右键/查询）从节点上下文取 schema 拼 `"schema"."table"` 限定名。
5. **渲染缩进**：子级自然多一层；搜索 scope 里 schema 也是一级
   （`SearchScope = "connection" | "database" | "schema" | "table" | "view"`）。

## 三、移植到 opscore（与 dbx 的差异点）

- dbx 用**引擎名单**（`usesTreeSchemaMode`）判定 + JDBC 未知驱动用**运行时探测**兜底；
  我们已有 `/api/dbmanager/schemas?id=` 能力探测接口（EngineHasSchema 注册表），
  于是**全部引擎走运行时探测**：连接展开时探测一次缓存，非空 → 模式层级，空 → 平铺。
  比名单更动态——引擎接入不需要改树代码。
- 对象加载复用：我们一次 `listTables(库)` 拿全量（PG 返回 `schema.table` 限定名），
  模式节点只做**客户端前缀过滤**，不逐模式请求（3.8G VM 上省查询）。
- 表节点 `table` 字段仍存限定名（下游 /data、describe、导出已支持两段名），
  仅**显示**裸名（模式层下前缀冗余）。
- 模式节点右键：新建查询 / 刷新 / 跨库同步此模式（预设进同步弹窗）/ 复制模式名。

## 四、验尸记录（防再犯）

- 之前 feature-matrix.md 已记录"⚠️ 缺 schema 层"缺口，但**没记 dbx 的实现方法**，
  导致缺口躺了几个迭代。教训：台账里每个对比项，参考项目的"实现方式"至少写一行
  指向源码位置（文件:行号 + 函数名），否则后续倒模还得重挖一遍。
