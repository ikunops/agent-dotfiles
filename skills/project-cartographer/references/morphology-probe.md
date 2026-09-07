# 形态测绘 — 表面节点的质感提取法

> 回答的问题：拓扑地图只说"A 到 B"，本篇说"**这条路两边长什么样、摸着什么手感**"。
> 适用对象：**表面节点**——页面、面板、弹窗、工作区这些"有脸面"的 UI 节点（B 型子树里的叶子面）。
> 纪律不变：一切可 grep、一切有 file:line，不许"看起来像"。

## 一、为什么形态可机械提取：控件词汇表是封闭的

前端项目几乎都有设计系统组件库（shadcn/antd/自绘 ui 目录）。这个库就是**封闭的控件词汇表**——界面无论多复杂，都是词汇表里的词组合出来的。所以形态不是玄学，是**用词统计**：

- 控件谱 = 表面文件对词汇表的使用频次
- 交互语法 = 事件指令的普查
- 布局骨架 = 布局件 + 排版方向的普查

## 二、四步提取（对每个表面文件执行）

**1. 控件谱** —— 先抄词汇表，再统计用词：

```bash
# 词汇表 = ui 目录 + 图表/覆盖层件的导出名
ls components/ui components/charts* components/overlays* 2>/dev/null
# 用词统计（按项目词汇表调整名单）
grep -oE '<(Button|Input|Select|Chip|Sheet|Dialog|Popover|Tooltip|Tabs|Switch|'
         'ScrollArea|Terminal|Gauge|Sparkline|Bar|Badge|…)' Surface.vue | sort | uniq -c | sort -rn
```

**2. 交互语法** —— 事件指令普查：

```bash
grep -oE '@(click|dblclick|contextmenu|keydown|pointerdown|change|input|drop|submit|long-press)[a-z.]*' Surface.vue | sort | uniq -c
grep -c 'v-model' Surface.vue   # 受控输入密度
```

读法：`@contextmenu` 多 = 右键宇宙；`v-model` 密 = 表单型；`@keydown` 多 = 键盘驱动型；`@dblclick` = 快捷编辑型。

**3. 布局骨架** —— 布局件 + 排版方向：

```bash
grep -oE '<(Splitpanes|Pane|ScrollArea|ResizableSplit|Teleport|Drawer|Tabs)[ />]' Surface.vue
grep -oE 'flex-(col|row)|grid-cols-[0-9]' Surface.vue | sort | uniq -c | sort -rn | head -5
```

读法：`flex-col` 占优 = 纵向分区（工具栏在上/内容在下）；Splitpanes = 可调分栏工作台；`grid-cols` 多 = 卡片矩阵。

**3.5 布局缺口探查（grid/flex 子控件可收缩性）** —— 布局骨架要说"能放得下"，不只"分成了几块"：

```bash
# 裸 1fr 与 minmax(0,…) 混用 = 溢出高危（裸 1fr 等价 minmax(auto,1fr), 子项最小宽度=内容/全局 min-width, 弹窗/卡片里撑爆）
grep -rnE "gridTemplateColumns|grid-template-columns" Surface.vue
# 全局是否压了 min-width 在子控件上（如 .input { min-width: 9.375rem }）, 让 minmax(0) 大概率失效
grep -rn "min-width"  全局样式.css
```

读法：容器（弹窗/卡片/动态行）内出现 `1fr` 而没配 `minmax(0,…)`、或子控件被全局 `min-width` 顶住且无容器级 `.container > .input { min-width: 0 }` → 形态存在"放不下/溢出/截断"风险，形态牌记入 `🚧 布局缺口`。这是「新模式掺旧写法」的高发点：同类容器一半用 `minmax(0)` 一半用裸 `1fr`，多半是倒模时落笔那几行沿用了旧约定。

**4. 形态指纹** —— 前三步的量化画像归入性格类（按主导交互定名，不按视觉喜好）：

| 指纹 | 特征 | 典型 |
|---|---|---|
| **工作台型** | 多区拼装 + 右键/快捷键密集 + 高控件多样性 | 编辑器+结果网格、IDE |
| **表单型** | v-model 密 + 分组字段 + 提交/取消对 | 连接配置、设置页 |
| **看板型** | 图表/仪表为主 + 轮询 + 弱交互 | 监控总览、仪表盘 |
| **浏览器型** | 树/列表 + 单击展开 + 右键 + 搜索过滤 | 连接树、文件管理器 |
| **对话型** | 流式追加 + 输入框常驻 + 附件 | AI 助手、聊天 |
| **终端型** | 只读大块文本 + 少量控件 + 等宽字体 | 日志页、原始输出页 |

混合表面允许双指纹（如"浏览器+工作台"）。

## 三、形态牌（指示牌第六行）写法

写进该表面所在 B 型子树的节点牌：

```markdown
**形态**：纵向三分（工具栏/树/状态条）· 控件谱：树×1 搜索×1 Chip×4 Dialog×8 ·
语法：@contextmenu×N @click×M dblclick 编辑 · 指纹：浏览器型 → 证据 Surface.vue:L12-40
```

密度纪律：谱列 Top5、语法列 Top3，其余用 "…等 N 项"；一面一牌，牌超 3 行说明这表面该拆子节点。

## 〇、开牌前先定"面"：表面 ≠ 单文件

实测教训（dbx ConnectionTree.vue）：文件只有 327 行，树的真实质感（指针三态、右键宇宙、虚拟滚动）全在行为文件 `SidebarTreeRuntimeHost`（6300 行）和 TreeItem 里。**表面 = 一个交互面，不是一张文件**。开牌步骤：
1. 先答"这个面用户摸到的是什么"；
2. 找齐承载它的文件群（模板 + 行为 composable + 子件），谱和语法**合并统计**；
3. 牌上注明文件群清单，否则读者会按单文件误判复杂度。

## 四、倒模时的用法：质感对比

两家同功能表面各提一张形态牌并排：差异即**质感差距清单**（他有何控件我没有 → 是缺组件还是缺交互语法；布局不同 → 主从 vs 平铺）。对照"两权分立"：差距清单是建议，采不采纳、要不要同质感，用户拍板。
