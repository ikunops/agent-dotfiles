# UI 菜单映射 —— 右键/菜单功能全集发现法

> 场景：想核对"参考项目的右键管理都有什么功能"，但手里没有功能名称（用户没给、报告没提）。
> 实证结论（2026-09，dbx 实测）：**不需要名称**——菜单是集中构建的，水流三步必达全集。

## 水流三步（任何前端框架通用）

1. **入口**：树/列表组件的右键事件（Vue `@contextmenu` / React `onContextMenu`）。
   实测：dbx `TreeItem.vue:1459 @contextmenu="onTreeItemContextMenu"`。
2. **构建函数**：事件 → 菜单构建函数（dbx: `buildContextMenu`/`treeItemMenuItems`，SidebarTreeRuntimeHost.vue:6114/6206）。
   **这个函数是功能全集的户口本**——全部菜单项按节点类型分支排列，一处不漏。
3. **分支清单**：读目标节点类型的分支（dbx 连接类型分支: 5190-5200），逐项即功能清单
   （processList / sqlServerTrace / serverDashboard / damengUsers…），
   条件表达式顺带给出各引擎的启用门控。

## i18n 逆向（第二来源，常被忽略）

i18n 文件按功能域分组，一段 = 一个功能的全部界面文案
（dbx: `serverDashboard: { autoRefresh, qps, connections, uptime… }` zh-CN.ts:3452）——
不看实现就知道功能存在、范围多大。菜单项的 `t("contextMenu.xxx")` 键 → 反查 i18n 得中文语义。
有些应用（GoNavi）更进一步：先列**动作键数组**（`open-data / pin-table / design-table…`，V2TableContextMenu.tsx:44-67）再渲染菜单——动作键数组就是功能清单本体。

## 沿单项到实现

菜单项的 `action: openServerDashboard` → handler（openServerDashboard:1694）→
按引擎分发组件（MySqlDashboard.vue / PostgresDashboard.vue）→ 数据源
（mysqlServerStatus.ts: `SHOW GLOBAL STATUS` 两次采样算速率 + `SHOW GLOBAL VARIABLES`）。

## 边界条件也是能力

分支里的条件函数（`connectionSupportsServerDashboard` → 引擎白名单）直接告诉你**哪些引擎支持该功能**——测绘时记录条件而非只记结论。

## 实现环节纪律（本次踩坑）

- **实现新功能前，必须回查测绘报告的对应清单**——报告里有"服务器 Dashboard"，
  实现时没回查、跟着用户给的词 grep，导致漏做自己都不知道存在的功能。
- 测绘报告的菜单/能力清单**必须逐项完整**（摘要压缩会丢项），每项标注源码位置（文件:行号），实现期回查才有可能。
