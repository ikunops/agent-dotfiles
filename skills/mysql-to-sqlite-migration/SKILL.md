---
name: mysql-to-sqlite-migration
description: 把单机/低并发的 SQLAlchemy 项目从 MySQL(+Redis) 完整迁到 SQLite 的方法论。当用户觉得"MySQL/Redis 太重了"、要做单文件独立版、或迁移过程中出现 disk I/O error、BIGINT 主键不自增、INSERT IGNORE 报语法错、aiosqlite 不认 timeout 参数、Decimal/绑定类型错误、__all__ 幽灵名导致 import * 崩溃、**缓存或查询"永远读不出来"却无报错（raw SQL 读 DATETIME 得 str 与 datetime 比较抛 TypeError 被吞）**、**某表行数持续增长（手写 DDL 漏 UNIQUE 导致 upsert 退化成 insert）** 等问题时使用。含类型兼容层、引擎级方言改写器、**读侧类型语义与 coerce helper**、**DDL 约束核对清单**、Redis 锁替换、数据迁移与验证清单，全部条目来自真实迁移。
---

# MySQL(+Redis) → SQLite 迁移方法论

2026-10 真实迁移（闲鱼自动发货系统：3 进程、46+ 张表、1.8 万行、30MB）全量沉淀。
先回答"能不能"：**数据 < 几百 MB、进程数个位数、写入是"每分钟几十行"级别、无高并发** ——
SQLite（WAL 模式）完全胜任，Redis 若只用于锁和缓存也可一并去掉。

## 六步法

1. **配置分支**：`DB_BACKEND=sqlite` 环境开关；URL 属性分支返回
   `sqlite:///(sync)` / `sqlite+aiosqlite:///(async)`。MySQL 路径一行不动。
2. **引擎分支**：SQLite 用 `NullPool`（避免跨事件循环复用）+ 连接事件设 PRAGMA：
   `journal_mode=WAL`、`busy_timeout=8000`、`synchronous=NORMAL`、`foreign_keys=ON`。
3. **类型兼容层**（`@compiles(SomeType, 'sqlite')`）：模型里 MySQL 专属类型逐个映射。
4. **建表与种子**：放弃手写 MySQL DDL，改 `Base.metadata.create_all`（**先 import 全部模型**
   再建，否则只建到被 import 的那部分）；"仅 DDL 无模型"的表单独补 SQLite 版 DDL。
5. **方言改写器**：引擎级 `before_execute(retval=True)` 拦截存量 MySQL 语句改写（见下），
   比逐处改 SQL 划算得多。
6. **数据迁移 + 验证**：同步建表 → MySQL 读、SQLite 批量 `INSERT OR REPLACE` → 行数逐一核对。

## 类型兼容层（真实用到的全部）

```python
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles

@compiles(LONGTEXT, 'sqlite')
def _(t, c, **kw): return 'TEXT'

@compiles(BigInteger, 'sqlite')
def _(t, c, **kw): return 'INTEGER'   # 关键：BIGINT PRIMARY KEY 在 SQLite 不自增！
```

`BIGINT PRIMARY KEY` 不是 rowid 别名 → 不带 id 的 INSERT 全部
`NOT NULL constraint failed: id`。只有 `INTEGER PRIMARY KEY` 才自增。
全表 BigInteger 渲染成 INTEGER 语义无损（SQLite 整数即 64 位）。

## 引擎级方言改写器（覆盖存量 SQL，一处生效）

```python
@event.listens_for(engine.sync_engine, 'before_execute', retval=True)
def _(conn, clause, mp, params, eo):
    sql = str(clause)
    if 'INSERT IGNORE' in sql:
        sql = sql.replace('INSERT IGNORE INTO', 'INSERT OR IGNORE INTO')
    sql = sql.replace('NOW()', "datetime('now','localtime')")
    if 'ON DUPLICATE KEY UPDATE' in sql:   # 该子句总在语句末尾
        sql = re.sub(r'\bON DUPLICATE KEY UPDATE.*$', '', sql, flags=re.S|re.I)
        sql = sql.replace('INSERT INTO', 'INSERT OR REPLACE INTO', 1).rstrip().rstrip(',;')
    # DATE_FORMAT(col,'%Y-%m-%d %H:%i:%s') → strftime('%Y-%m-%d %H:%M:%S',col)（%i→%M,%s→%S）
    return text(sql), mp, params
```

无法改写的少数表达式（`SUBSTRING_INDEX`、`JSON_UNQUOTE`）在业务代码按后端分支：
Python 侧切分 / SQLite json1（`json_extract` 对文本可直接解 JSON 且标量不带引号）。

## 读侧类型语义（最容易漏的一层，2026-10-14 真实事故）

写入/DDL 层（`@compiles`、方言改写器）通常都会想到，**但"读出来是什么类型"才是最隐蔽的坑**：

| 类型 | MySQL 驱动返回 | SQLite 驱动返回 |
|---|---|---|
| `DATETIME` | `datetime` 对象 | **`str`**（DATETIME 在 SQLite 只是"亲和性"，实际存 TEXT） |
| `BOOLEAN` | `bool` | `int`（0/1） |
| `DECIMAL/NUMERIC` | `Decimal` | `float` 或 `str` |
| `JSON` | 已解析对象 | `str`（需 `json.loads`） |

**真实事故**：token 缓存读取 `if expire_at and expire_at > now:` 在 SQLite 下抛
`'>' not supported between instances of 'str' and 'datetime.datetime'`；
异常被外层 `except Exception` 吞掉 → 缓存**永远读不出来** → 每 3 分钟重新申请 token
→ 持续触发平台风控（表现为"一直在过滑块"，排查了几小时才定位）。

### 分界线：ORM 查询 vs raw SQL

**同一个项目里两种写法行为不同**，实测：

```python
# A) ORM 查询：SQLAlchemy 按模型声明的 DateTime 做转换 → datetime ✅
(await s.execute(select(XYOrder.created_at).limit(1))).scalar_one_or_none()  # datetime

# B) raw SQL：无类型声明，驱动原样返回 → str ❌
(await s.execute(text("SELECT created_at FROM xy_orders LIMIT 1"))).fetchone()  # str
```

**所以：项目里所有 `text(...)` + `fetchone()` 读时间字段的地方都要查。**

### 统一解法：一个 coerce helper

```python
def _coerce_dt(value):
    """把 DB 读出的时间值统一成 datetime（SQLite 返回 str，MySQL 返回 datetime）。"""
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace(" ", "T"))
        except ValueError:
            return None
    return value

# 用法：比较/运算前先转
expire_at = _coerce_dt(expire_at)
if expire_at and expire_at > now: ...
```

**扫描方法**：`grep -rn 'text(' --include='*.py'` 找 raw SQL 文件，再看里面有没有
`expire_at|created_at|updated_at` 与 `> < >= <=` 同现。ORM 写法可以放过。

## 手写 DDL 必须 1:1 抄约束（2026-10-14 同一事故的第二因）

SQLite 版 DDL 若手写（"仅 DDL 无模型"的表），**必须逐条对比 MySQL 版，尤其 UNIQUE/索引**：

| MySQL | SQLite 手写版漏掉后 |
|---|---|
| `UNIQUE KEY uk_user_id (user_id)` | 写入用 `INSERT ... ON DUPLICATE KEY UPDATE`（被改写器转成 `INSERT OR REPLACE`）时**没有唯一键可冲突** → 每次都是新增 → 表从 3 行涨到 105 行 |

**核对清单**：MySQL 版每张表 `SHOW CREATE TABLE` 或读源码 DDL，逐个确认
`UNIQUE KEY` / `PRIMARY KEY` / `KEY`（索引影响查询性能）都在 SQLite 版里有对应物。
SQLite 语法：列级 `user_id VARCHAR(128) NOT NULL UNIQUE` 或表级 `UNIQUE(user_id)`。

> 教训归纳：**迁移时"搬运 SQL 文本"是不够的，要验证三件事——
> 写入时的类型转换（DDL/绑定）、读取时的返回类型（ORM vs raw SQL）、约束是否齐全。**

## 坑速查表（每条都真实踩过）

| 症状 | 根因 → 解法 |
|---|---|
| **缓存/查询永远"读不出来"、却无报错** | raw SQL 读 DATETIME 得 str，与 datetime 比较抛 TypeError 被 except 吞掉 → `_coerce_dt()` 转换；见「读侧类型语义」 |
| **某表行数莫名持续增长** | SQLite 手写 DDL 漏了 UNIQUE 约束，upsert 退化成纯 insert → 补约束 + 重建表去重；见「手写 DDL 必须 1:1 抄约束」 |
| `disk I/O error` | 同一库文件被**两个连接并发**（异步引擎 + 迁移裸连接）→ 建表用同步引擎跑完 `dispose()` 再迁；`rm` 掉残留 `-wal/-shm` |
| 测试跑到了线上库 | pydantic `env_file=".env"` 相对 CWD，**.env 会盖过环境变量** → 测试换一个无 .env 的工作目录 |
| `INSERT ... ON CONFLICT` 后判断成败 | 读 `cursor.rowcount`（冲突未更新=0）；先 commit 再读 |
| 进程结束挂住不退出 | aiosqlite 后台线程非 daemon → 用完 `close()`；长驻服务无感 |
| `connect() got unexpected keyword 'timeout'` | aiosqlite 方言不收该参数 → 删 connect_args，用 `PRAGMA busy_timeout` |
| Decimal / datetime 绑定失败 | sqlite3 不认 → 迁移时 norm：Decimal→float，datetime→isoformat，bytes→decode |
| `import *` 报 AttributeError | 聚合模块 `__all__` 里有幽灵名（删了模型没清 __all__，注意**大小写**）→ 按 AST 实际导入名过滤自愈 |
| Redis 锁在 SQLite 模式失效 | 分支模块里 SQLite 锁类被**文件后部的原 Redis 类定义覆盖** → 文件末尾按后端重绑定；用例：`try_acquire` 用单条 upsert `ON CONFLICT DO UPDATE ... WHERE expires_at < now`，rowcount 判成败 |
| 迁移行数对不上 | `information_schema.table_rows` 是 InnoDB **估算值** → 核对必须 `SELECT COUNT(*)` |

## Redis 去化（当 Redis 只用于锁+缓存时）

- 同库建 `app_locks(name, holder, expires_at)` 与 `app_kv(key, value, expires_at)` 两张表；
- 锁：acquire=单条 upsert（WHERE 过期）原子抢占；release=`DELETE WHERE holder=自己`；
  extend=`UPDATE SET expires_at=MAX(expires_at,now)+add`；
- KV 客户端 shim 实现 get/set(ex)/setex/delete/exists/pipeline/ping；
- **保留原模块 API 1:1**（类名/签名/返回结构），调用方零改动；MySQL 模式走原实现。

## 验证清单（缺一不可）

1. 全部源文件 AST 通过（**用目标 Python 版本验证**，宿主机可能是旧版）
2. 全新库 `init` 跑通：表数、每张种子表行数、平台日等 KV 键
3. 数据迁移后逐表 `COUNT(*)` 与源库精确值核对；`PRAGMA foreign_key_check`
4. 锁专项：A 抢到→B 被拒→A 释放→B 拿到；发货/支付等幂等锁**必须**单独测
5. 应用真实启动：`/health` 且 `database=connected`；JWT/配置从新库加载成功
