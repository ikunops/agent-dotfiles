---
name: quark-drive-ops
description: 夸克网盘（Quark Drive）全操作手册：转存分享链接、批量重命名与撤销、上传下载（断点续传）、创建分享、目录浏览与搜索、文件移动/建夹、AI 总结问答。当需要「把某分享存到我网盘」「去掉文件名里的推广标记」「把这个课分享出去」「网盘里找 XX 文件」或排查夸克授权/环境问题时使用。含 KM1 双账号、node16+CLAUDECODE 环境坑、开放平台 fid 与网页版 fid 不可混用等实战要点。
---

# 夸克网盘操作手册（quark-drive-ops）

夸克网盘官方开放平台 CLI 的完整用法，跑在 **KM1（192.168.94.20）**，账号已授权，无需扫码。

> 与 `pan-share-screenshots`（分享页截图）互补：那个只读页面截图，这个动真实网盘文件。

## 1. 环境准备（每次调用前必须做）

系统自带 node 的 glibc 太老（CentOS 7 / glibc 2.17），**必须用 nvm 的 node16**，且必须设 `CLAUDECODE` 让 CLI 识别 agent 环境，否则报 `{"code":-104,"msg":"无法识别当前 Agent 环境"}`。

```bash
export PATH=/root/.nvm/versions/node/v16.20.2/bin:$PATH
export CLAUDECODE=1 CLAUDE_CODE_ENTRY_POINT=1 CLAUDE_CODE_SESSION_ID=<唯一会话id>
cd /root/.config/opencode/skills/quarkclouddrive2   # 或 quarkclouddrive
```

**两个账号、两份独立授权**：

| 目录 | 账号 | 用途 |
|---|---|---|
| `skills/quarkclouddrive` | 夸父*429 | 主资源盘（所有课程 + 分享链接） |
| `skills/quarkclouddrive2` | 有毅力的金雕 | 新账号盘 |

**公共参数**：所有子命令都要带 `--session-input "<用户原话>"` 和 `--session-id <时间戳-随机6位>`（如 `1793800000-a1b2c3`），同一对话内复用同一个 session-id。

**每个 session 第一次调用前**跑一次 `bash scripts/install.sh` 检查环境。

## 2. 能对网盘做什么（能力全景）

| 能力 | 命令 | 关键参数 |
|---|---|---|
| 看目录 | `browse` | `--parent-fid <fid>`（根为 `0`）、`--page-size 100` |
| 搜自己网盘 | `search` | `--keyword`（≤50字）、`--search-type mix/video/doc/dir/package` |
| 看分享内容 | `share-detail` | `--url`、`--passcode`、`--pdir-fid` 逐层进 |
| 分享内搜文件 | `share-search` | `--url --keyword` |
| **转存** | `saveas` | `--url`、`--passcode`、`--to-pdir-path` 或 `--to-pdir-fid`、`--fid-list` 部分转存 |
| 查转存更新 | `get-share-update-list` → `get-share-update-files` | 只看新增了哪些文件 |
| 转存增量 | `saveas-update` | `--url`，自动存回上次目录 |
| 查上次转存目录 | `get-share-saved-dir` | `--url` → `data.pdir_fid` |
| **批量重命名** | `rename` | `--items-file`、`--batch-id` |
| **整批撤销改名** | `rename-revert` | `--batch-id`、`--record-file` |
| 上传 | `upload` | 本地路径 + `--parent-fid`；支持 `list/resume/delete` 续传 |
| 下载 | `download` | `--fid`、`--output-dir`、`--overwrite`；支持 `list/resume` |
| 创建分享 | `share` | `--title`、`--url-type 1`（公开）、`--expired-type 1`（永久） |
| 建文件夹 | `create-folder` | `--dir-path`、`--parent-fid` |
| 移动文件 | `move` | fids + `--target-fid` |
| AI 总结 | `summary` | `--query`、`--fid-list` |
| AI 问答 | `qa` | `--query`、`--fid-list` |
| 智能整理 | `organize` → `organize-copy`/`organize-move` | `--query` 自然语言 |
| 账号信息 | `get-user-info` | 返回昵称、已用/总容量 |
| 登录/换号 | `login` → `login --token AAC-xxx` | 见 §7 |

## 3. 目录遍历的坑（重要）

`browse` 有两个互斥行为，**必须用 `--page-size 100`，不要用 `--all`**：

- `--all`：只返回**前 5 条**（真实 bug，total 显示 9 但只给 5 条）
- `--page-size 100`：返回全部，但输出格式变了——每行是 `type:"list"`，最后一行 `type:"result"` 只含 `{total, hasMore}`

所以解析时要收集所有 `type=="list"` 的行：

```python
for line in out.splitlines():
    d = json.loads(line)
    if d.get('action')=='browse' and d.get('type')=='list':
        collected.append(d['data'])       # 每个 data 是一个文件项
    elif d.get('action')=='browse' and d.get('type')=='result':
        return collected                   # 别从 result 里找 file_list
```

递归遍历大目录（几百个文件）要 5-10 分钟，**用 `setsid nohup` 后台跑 + 轮询 JSON 文件**，不要阻塞在 SSH 里（paramiko 会 socket.timeout）。

## 4. 批量重命名（最常用）

### 流程

1. 遍历拿到全部 `{fid, name, parent_fid}`
2. 按规则算出 `new_name`，生成 items JSON
3. **向用户展示**：总数 N、规则、前 5 条原名→新名（不展示 FID）
4. 用户确认后提交
5. 成功后可用原 batch 整批撤销

### items JSON 格式

```json
{
  "schema_version": 1,
  "items": [
    {"fid": "<完整FID>", "old_name": "原名.mp4", "new_name": "新名.mp4"}
  ]
}
```

约束：`fid`/`old_name`/`new_name` 非空；`new_name` 长度 ≤255；FID 不能重复；一个 batch 1~5000 条。

### 执行

```bash
BID=$(node -e 'process.stdout.write(require("node:crypto").randomBytes(8).toString("hex"))')
node scripts/quark-drive.cjs rename --batch-id "$BID" \
  --items-file /root/rename-items.json \
  --session-input "<用户原话>" --session-id <sid>
```

成功返回：

```json
{"code":0,"data":{"batch_id":"...","record_file":"/root/rename-records/xxx.json",
 "total":308,"success_count":308,"fail_count":0,"skip_count":0}}
```

**内部保留 `batch_id` 和 `record_file`**（撤销要用），不向用户展示。

### 撤销

```bash
node scripts/quark-drive.cjs rename-revert --batch-id <原BID> \
  --record-file <原record_file绝对路径> --session-input "..." --session-id <sid>
```

一次 REVERT 覆盖该 batch 的一次正向请求。多个 batch 要分别撤销。

### 真实案例：去掉文件名推广标记

308 个文件全带 `【公众号：GG学习社】】` 后缀，正则 `【公众号：GG学习社】】` → 空串，一次 batch 全部改完，0 失败。改完用 `search --keyword "GG学习社"` 验证返回 0 条。

## 5. 转存分享链接

```bash
# 整个分享
node scripts/quark-drive.cjs saveas --url "https://pan.quark.cn/s/xxxx" \
  --passcode "abcd" --to-pdir-path "/我的课程"

# 只存指定文件（先 share-detail 拿 fid）
node scripts/quark-drive.cjs saveas --url "..." --fid-list "fid1,fid2"

# 增量（仅限已转存过的链接）
node scripts/quark-drive.cjs get-share-update-files --url "..."
node scripts/quark-drive.cjs saveas-update --url "..."
```

**目录参数规则**：用户没指定目录时**不要**传 `--to-pdir-fid 0`，直接省略让 CLI 用默认行为。

## 6. 开放平台 fid ≠ 网页版 fid

两套 fid 格式不同，**绝对不能混用**：

| 来源 | fid 形态 | 用途 |
|---|---|---|
| 开放平台 CLI（browse/search） | `~1xxx\|xxxx`（含竖线） | 所有 CLI 命令 |
| 网页版接口（drive-pc.quark.cn） | 32位十六进制 | 网页版 API |

**CLI 没有删除功能**。要删文件只能走网页版接口，且在已登录的浏览器里同源 fetch：

```js
// POST https://drive-pc.quark.cn/1/clouddrive/file/delete?pr=ucpro&fr=pc
// body: {"action":1,"filelist":[网页版fid...]}
// 搜网页版fid: GET .../file/search?pr=ucpro&fr=pc&q=关键词&_page=1&_size=100
```

## 7. 授权过期 / 换号

```bash
node scripts/quark-drive.cjs login --verbose   # 日志里有 authorize_page_url
# 用户在目标账号的浏览器/App 打开授权，拿到 AAC- 开头的口令
node scripts/quark-drive.cjs login --token AAC-xxx
```

授权信息落在 `skills/quarkclouddrive2/claudecode/config.json`（按 agent 渠道分目录：`claudecode/`、`openclaw/`）。

## 8. 常见错误

| 报错 | 原因 | 解法 |
|---|---|---|
| `code:-104 无法识别当前 Agent 环境` | 没设 `CLAUDECODE` | `export CLAUDECODE=1` |
| `GLIBC_2.27 not found` | 用了系统 node | 用 `/root/.nvm/versions/node/v16.20.2/bin/node` |
| `code:-100 unknown option '--fid'` | browse 的参数是 `--parent-fid` | 改参数名 |
| browse 只返回 5 条 | 用了 `--all` | 改用 `--page-size 100` 并解析 `type:list` |
| 转存失败 | 空间满 | `get-user-info` 查 `used`/`capacity` |
| `token [st invalid]` | 授权过期 | 重新 `login` |

## 9. 硬性约束

- **重命名/撤销必须先拿到用户明确确认**，展示总数+规则+前 5 条对照，确认后冻结计划
- 一个 batch 一次提交，**不自行分片**；超过 5000 条先做 5000 条再问
- `get-share-update-files` / `saveas-update` 成功后返回的 `msg` 必须**完整原样**展示，禁止改写
- 不要向用户暴露 batch_id、record_file、fid、协议字段等技术细节
- 搜索结果只作为中间步骤取 fid 时传 `--stdout-only`；要展示给用户时不传
