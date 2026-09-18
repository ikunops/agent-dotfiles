---
name: browser-profile-diag
description: Read-only diagnosis of browser login state — locate which Chrome/Edge user-data-dir & profile still holds a LIVE session for a target site, WITHOUT launching the browser (launching it loses the session). Scans Local State (identity) + Cookies sqlite (credential) via mode=ro.
description_zh: "浏览器登录态只读诊断：不启动浏览器，定位哪个 profile 还登录着"
description_en: "Read-only browser login-state diagnosis via Local State + Cookies sqlite"
version: 1.0.0
allowed-tools: Bash, Read
display_name: "浏览器登录态只读诊断"
tags:
  - browser
  - login-state
  - cookies
  - cdp
  - diagnostics
visibility: "public"
agent_created: true
---

# Browser Profile / Login-State Diagnosis (read-only)

## When to use
- "Which browser profile is still logged in to X?" (ChatGPT / Claude / Gemini / a SaaS…)
- You need to drive a logged-in browser via CDP but don't know which `user-data-dir` / `--remote-debugging-port` holds the live session.
- You previously lost a session by opening the browser "just to check".
- **Never** use this to inspect arbitrary users' private cookie stores beyond the local, logged-in account — that crosses into sensitive-data territory.

## 🚨 GOLDEN RULE — DO NOT LAUNCH THE BROWSER
Opening the browser to "see if I'm logged in" is the #1 way to **destroy** the session you're looking for:
- A fresh launch of the wrong user-data-dir re-prompts login.
- Even the *right* profile may auto-redirect to a re-auth wall on cold start.
- The running browser already holds a lock on `Cookies`; launching another instance can corrupt it.

**Always diagnose by reading files directly.** This is 100% read-only and lossless.

## Diagnosis has two layers

### Layer 1 — Identity (WHO): `Local State` JSON
Path: `<user-data-dir>/Local State` (JSON, not sqlite).
```python
import json, os
ls = r"C:\Users\30849\AppData\Local\Google\Chrome\User Data\Local State"
d = json.load(open(ls, encoding="utf-8", errors="replace"))
cache = (d.get("profile") or {}).get("info_cache") or {}
for k, v in cache.items():
    print(k, "->", v.get("gaia_name") or v.get("user_name"), "|", v.get("name"))
```
- Key path: `profile.info_cache` → per-profile `gaia_name` / `user_name` / `name`.
- This tells you the human identity behind each profile **without** needing the session cookie.

### Layer 2 — Credential (IS IT LIVE): `Cookies` sqlite
Path: `<user-data-dir>/<Profile>/Cookies`. **Connect read-only** so the running browser's lock is bypassed:
```python
import sqlite3
con = sqlite3.connect("file:" + path.replace("\\","/") + "?mode=ro", uri=True, timeout=1)
rows = con.execute(
    "SELECT host_key,name,expires_utc FROM cookies "
    "WHERE lower(name) LIKE '%session%'").fetchall()
```
- **Time encoding gotcha:** `expires_utc` is **microseconds since 1601-01-01** (Windows epoch), NOT Unix.
  ```python
  def ts(us):
      return datetime.datetime(1601,1,1) + datetime.timedelta(microseconds=us) if us else None
  ```
  `NULL` / `0` = session cookie (lives until browser close) → treat as **live**. `> now` = still valid.
- Filter by target host: `WHERE host_key LIKE '%chatgpt%' OR host_key LIKE '%openai%'` (or whatever site).
- The interesting token is usually `__Secure-next-auth.session-token` (NextAuth/OpenAI-style) or similar `*session*` cookies.

## ⚠️ 最关键的正确性陷阱：读不到 ≠ 没登录
`mode=ro` 并不能保证打得开。浏览器运行时会对 cookie 库加**排他锁**，此时：
- `sqlite3.connect(...?mode=ro)` → `OperationalError: unable to open database file`
- 连 `shutil.copyfile()` 兜底都 → `PermissionError: [Errno 13]`

若把这种失败当成「没有会话」，就会**把一个正在运行、很可能已登录的活跃 profile 误判成未登录**，结论完全反过来。

**必须区分三种状态并如实报告：**
1. ✅ 有存活会话
2. ⚠️ **读不到**（cookie 库被锁）→ 说明该目录正被运行中的浏览器使用，应**连接其已有调试端口，不要另起实例**
3. ❌ 无存活会话

检测方式：捕获打开异常，记录到 `unreadable` 列表；宁可标 ⚠️ 也不要标 ❌。

## 🔑 域名别名：登录态常落在「兄弟域」
只提取品牌词会漏判。ChatGPT 的会话既在 `chatgpt.com` 也在 `openai.com`（`__Secure-next-auth.session-token` 常见于 `.chatgpt.com`，而 `auth.openai.com` 也有相关 cookie）。
```python
HOST_ALIASES = {
    "chatgpt": ["chatgpt", "openai"],
    "gemini":  ["gemini", "google"],
    "kimi":    ["kimi", "moonshot"],
}
```
匹配 token 应包含：**品牌词 + 注册域名(eTLD+1) + 别名**。

## 🔑 KEY LESSON — user-data-dirs are NOT only `User Data`
A browser install (esp. Chrome) can have **multiple independent `user-data-dir`s** as sibling folders, not just `User Data\Profile N`. Examples seen in the wild:
```
Google\Chrome\
├── Application\          # the binary
├── User\                # an independent user-data-dir (relay/automation used THIS, not "User Data")
├── User Data\           # the "main" profile set
├── User Data Relay\     # a throwaway relay dir (no session)
└── User Data RelayLink\ # a junction (symlink) — ignore
```
**Enumerate ALL sibling dirs**, read each one's `Local State` + `Cookies`. The live session is often in the dir you were NOT looking at (e.g. the standalone `User`, not `User Data\Profile 1`).

## Reusable scanner (generalized)
Drop this, edit `TARGETS`, run with the managed python. It walks `AppData\Local` + `AppData\Roaming`, skips junk, and reports live sessions per host.
```python
import os, json, datetime, sqlite3
from pathlib import Path

TARGETS = ["chatgpt", "openai", "claude", "gemini", "google"]  # host substrings
BROWSERS = [
    r"C:\Users\30849\AppData\Local\Google\Chrome",
    r"C:\Users\30849\AppData\Local\Microsoft\Edge",
]
PRUNE = {"node_modules",".git","Crashpad","Code Cache","ShaderCache",
         "GPUCache","Cache","CacheStorage","Service Worker","blob_storage"}

def ts(us):
    try: return datetime.datetime(1601,1,1)+datetime.timedelta(microseconds=us)
    except Exception: return None

now = datetime.datetime.utcnow()
scanned=hits=0
for base in BROWSERS:
    if not os.path.isdir(base): continue
    # 1) identity from every sibling user-data-dir's Local State
    for name in os.listdir(base):
        ls = os.path.join(base, name, "Local State")
        if name in PRUNE or not os.path.exists(ls): continue
        try:
            cache = json.load(open(ls,encoding="utf-8",errors="replace")) \
                       .get("profile",{}).get("info_cache",{})
            for k,v in cache.items():
                print(f"  [{base.split(chr(92))[-1]}/{name}] {k} = "
                      f"{v.get('gaia_name') or v.get('user_name')} ({v.get('name')})")
        except Exception as e:
            print("  LocalState ERR", ls, e)
    # 2) credential scan — cookie 库位置是固定的，限深枚举比递归 walk 快一个数量级
    #    （walk 整个 profile 会遍历 Cache 等巨量文件，实测慢 10 倍以上）
    for name in os.listdir(base):
        ud = os.path.join(base, name)
        if name in PRUNE or not os.path.isdir(ud): continue
        for pname in os.listdir(ud):
            pdir = os.path.join(ud, pname)
            if not os.path.isdir(pdir): continue
            for rel in ("Cookies", os.path.join("Network", "Cookies")):
                f = os.path.join(pdir, rel)
                if not os.path.isfile(f): continue
                scanned += 1
                try:
                    con = sqlite3.connect(Path(f).as_uri()+"?mode=ro", uri=True, timeout=1)
                    rows = con.execute("SELECT host_key,name,expires_utc FROM cookies").fetchall()
                    con.close()
                except Exception as ex:
                    # 被排他锁占用 —— 读不到 ≠ 没登录，绝不能当成「无会话」
                    print(f"  ** LOCKED ** {f}  ({type(ex).__name__})")
                    continue
                for h,n,e in rows:
                    hl = (h or "").lower()
                    if not any(t in hl for t in TARGETS): continue
                    nl = (n or "").lower()
                    if not any(k in nl for k in ("session","token","auth","sid","login","jwt")): continue
                    dt = ts(e); live = (dt is None) or (dt > now)
                    if live:
                        hits += 1
                        print(f"  ** LIVE ** {f}\n       host={h} name={n} exp={dt}")
print(f"\n  scanned {scanned} cookie DBs, {hits} live sessions")
```
Run with the managed interpreter so websockets/stdlib are present:
`C:\Users\30849\.workbuddy\binaries\python\envs\default\Scripts\python.exe diag.py`

## Output contract
Report, per live session found:
1. **Which user-data-dir** (full path) — this is the dir to pass as `--user-data-dir` for CDP.
2. **Which profile** (Profile N / Default) — the `info_cache` key.
3. **Identity** (email/name from Local State).
4. **Expiry** (absolute UTC) — tells you how long the session lasts.

## Failure modes & fixes
- `sqlite3.OperationalError: database is locked` → you forgot `?mode=ro`. Always use the `file:...?mode=ro` URI form.
- **`unable to open database file` / `PermissionError [Errno 13]` even with `mode=ro`** → the browser holds an **exclusive** lock (it is running); even `shutil.copyfile()` cannot read it. **Do NOT report "no session"** — mark it `LOCKED`/unreadable and advise connecting to the already-running instance's debug port rather than launching a new one. See the correctness trap above.
- **Scan takes tens of seconds** → you're walking the entire profile (Cache, GPUCache, …). Cookie DBs live at fixed paths (`<profile>/Cookies` or `<profile>/Network/Cookies`) — enumerate those directly instead of `os.walk`. Measured ≈10× faster (tens of seconds → ~5s).
- Found sessions but they're all expired → the live one is in a dir you didn't enumerate. Enumerate **ALL** sibling user-data-dirs, not just `User Data`.
- `Local State` present but `info_cache` empty → profile has no signed-in Google account identity (local-only profile); rely on the Cookies layer instead.
- Chrome profile vs Edge profile: never pass a Chrome `user-data-dir` to Edge (or vice versa). Filter by brand when auto-selecting.
