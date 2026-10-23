# Skills INDEX — 三层路由根节点

> 这是技能体系的根索引（Root Node），只负责分流，不复制技能正文。
> 先读本页，按任务领域进入 `indexes/` 下的中间页，再读目标技能的
> `SKILL.md`。根页保持小，新增技能时不需要把全量清单塞回来。

```text
skills/INDEX.md                 根节点：入口、维护规则、层选择
skills/indexes/active.md        中间节点：83 个顶层活跃技能
skills/indexes/library.md       中间节点：207 个库层技能，按目录分类
skills/indexes/external.md      中间节点：11 个外部本地依赖
skills/<skill>/SKILL.md         叶子：技能正文
```

## 选择索引层

| 任务信号 | 读取中间页 | 叶子位置 |
| --- | --- | --- |
| 常驻、自动触发、跨项目高频 | [`indexes/active.md`](indexes/active.md) | `skills/<name>/SKILL.md` |
| 非常驻、按需、需要特定领域能力 | [`indexes/library.md`](indexes/library.md) | `skills/<framework\|function\|platform>-specific/<path>/SKILL.md` |
| 上游开源或市场安装、缺失不算故障 | [`indexes/external.md`](indexes/external.md) | 由 `agents/openai.yaml` gate，按需显式调用 |
| 找不到路由 | `find-skills` 的任务路由表 | 再用关键词检索叶子 |

## 维护规则

1. 先检查是否已有技能覆盖，避免为一个场景新增近重复件。
2. 新增自有活跃技能：登记到 `indexes/active.md`，全页**恰好一次**。
3. 下沉：移动目录到 `function|framework|platform-specific/`，从活跃页移除，
   在 `library.md` 对应分类登记。不要复制目录。
4. 外部件：只登记到 `external.md`，不要放进活跃表格，也不要直接改上游
   `SKILL.md`。
5. 归档件：移入 `skills-archive/`，从三个中间页移除，并更新
   `_archived_list.json`。
6. 提交前运行：

```powershell
python scripts/audit-skills.py --strict
git diff --check
```

## 为什么不是物理三叉目录

三层树借鉴 B+Tree 的“根→内部节点→叶子”路由，而不是数据库的分裂算法：

- 根节点只保留分类入口和维护规则；
- 内部节点按领域/层拆分，只有进入该领域才读；
- 叶子仍是每个技能自己的 `SKILL.md`，不再复制正文；
- 客户端递归发现规则不变，因此不能靠目录嵌套降低自动扫描成本。

真正降低自动索引成本仍靠活跃层克制、库层 gate 和长期不用的归档。
根索引不是“全量清单”，全量账本在三个中间页。
