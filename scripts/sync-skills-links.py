#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一各 AI 客户端的 skills 目录指向同一份 dotfiles。

背景
----
本机常同时装着多个 AI 客户端（WorkBuddy / zcode / opencode / codex / Doubao / cline ...），
它们各自认一个 skills 目录。dotfiles 可能被不同客户端各拉一份，于是出现：

    zcode   → 软链到 A 份 dotfiles（较早拉的）
    opencode→ 自己的真实目录
    codex   → 空目录
    后来又拉了 B 份 dotfiles（更新）……  —— 谁指谁、哪份新，全靠人记

本脚本把这件事一次性做对：
  1. 发现所有客户端的 skills 路径 + 所有 dotfiles 副本
  2. 按「新鲜度」选出权威副本（git 提交时间 > skills 内最新文件 mtime）
  3. 计算各客户端相对权威副本的 "独有 skill"（重定向后会丢的）
  4. 用目录链接（junction/symlink）把客户端指向权威副本
  5. 旧副本 / 被替换的真实目录 → 移入备份区（绝不直接删除）

安全设计
--------
* 默认 **dry-run**：只报告打算做什么，不动任何东西
* `--apply` 才真正执行
* 发现任何"独有 skill" → 默认**跳过该客户端**并高亮告警（`--force` 可强制）
* 所有替换都留备份，路径打印在结尾

用法
----
    python sync-skills-links.py                  # 体检：报告现状与建议（不改动）
    python sync-skills-links.py --apply          # 执行
    python sync-skills-links.py --apply --force  # 即使有独有 skill 也强制重定向
    python sync-skills-links.py --home /root     # 指定用户目录（默认自动取）

跨平台
------
* **Windows**：用目录联接（`mklink /J`）——**不需要管理员权限**，也不需要开发者模式。
  （不用符号链接 `/D` 正是因为它要提权。）
* **Linux / macOS**：用符号链接（`ln -s`），先删后建，不依赖 `-n`/`-T` 这类 GNU 专属选项。
* 客户端 skills 路径按平台分别探测：Windows 的 `AppData/{Roaming,Local}/*/skills`、
  以及通用的 `~/.config/*/skills`、`~/.local/share/*/skills`、`~/.cache/*/skills`、`~/*/skills`。
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# ---------- 控制台编码兜底 ----------
# Windows 默认 cp936/GBK 下，输出里的 emoji（✅/🔁/⚠️/📦）会抛 UnicodeEncodeError
# 直接把脚本打断。这里统一把 stdout/stderr 切到 UTF-8；即便切换失败，
# 也退化成 errors=replace，保证打印永远不会中断主流程。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        try:
            _stream.reconfigure(errors="replace")
        except Exception:
            pass

# ---------- 客户端 skills 路径的候选形态（跨平台）----------
CLIENT_GLOBS = [
    "*/skills",                          # ~/.zcode/skills、~/.workbuddy/skills、~/Doubao/skills
    ".config/*/skills",                  # ~/.config/opencode/skills（Win + Linux 通用）
    ".local/share/*/skills",             # Linux：~/.local/share/<client>/skills
    ".cache/*/skills",                   # Linux：部分客户端把 skills 放 cache
    "AppData/Roaming/*/skills",          # Windows
    "AppData/Local/*/skills",            # Windows
]
# 这些目录名不参与"客户端"身份（它们是 dotfiles 仓库本身或无关目录）
# 注意：这里**故意不含 "cache"** —— 探测规则里有 `.cache/*/skills`，
# 若把 cache 列为排除项，那条规则会永远命中不到（自相矛盾）。
NOT_CLIENT_HINTS = ("dotfiles", "node_modules", ".git")


def is_link(p: Path) -> bool:
    try:
        return p.is_symlink()
    except OSError:
        return False


def link_target(p: Path) -> str | None:
    """返回链接/junction 的指向；不是链接则 None。（跨平台）"""
    if is_link(p):
        t = os.readlink(str(p))
        # MSYS 风格 /c/Users/... → C:/Users/... （Windows + Git Bash 场景）
        if os.name == "nt" and t.startswith("/") and len(t) > 2 and t[2] == "/":
            t = t[1] + ":" + t[2:]
        # Linux/macOS 的 readlink 可能返回相对路径 → 相对链接所在目录解析
        if not os.path.isabs(t):
            t = os.path.join(os.path.dirname(str(p)), t)
        return os.path.normpath(t)
    # Windows junction 在 Python 里 is_symlink() 可能为 False；用 realpath 判定：
    # 若解析结果与自身不同，说明它是个重定向点（junction 或其他 reparse point）。
    # Linux 上没有 junction，这段自然不触发。
    if os.name == "nt" and os.path.exists(str(p)):
        try:
            rp = os.path.realpath(str(p))
            if os.path.normcase(rp) != os.path.normcase(str(p)):
                return rp
        except Exception:
            pass
    return None


def git_commit_time(repo: Path) -> int | None:
    if not (repo / ".git").exists():
        return None
    try:
        r = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%ct"],
                           capture_output=True, text=True, timeout=20)
        if r.returncode == 0 and r.stdout.strip().isdigit():
            return int(r.stdout.strip())
    except Exception:
        pass
    return None


def newest_file_mtime(d: Path) -> int:
    latest = 0
    try:
        for f in d.rglob("*"):
            try:
                if f.is_file():
                    latest = max(latest, int(f.stat().st_mtime))
            except OSError:
                continue
    except Exception:
        pass
    return latest


def fmt_time(ts: int | None) -> str:
    if not ts:
        return "—"
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))


def skill_names(d: Path) -> set[str]:
    if not d.exists():
        return set()
    try:
        return {p.name for p in d.iterdir()
                if not p.name.startswith(".") and (p.is_dir() or is_link(p))}
    except Exception:
        return set()


# ---------- 发现 ----------
def find_client_skills(home: Path) -> dict[Path, str | None]:
    found: dict[Path, str | None] = {}
    for pat in CLIENT_GLOBS:
        for p in home.glob(pat):
            parts = set(part.lower() for part in p.parts)
            if any(h in " ".join(parts) for h in NOT_CLIENT_HINTS):
                continue
            if p.is_dir() or is_link(p):
                found[p] = link_target(p)
    return dict(sorted(found.items(), key=lambda kv: str(kv[0])))


def find_dotfiles_copies(home: Path) -> list[Path]:
    """含 skills/ 且（有 .git 或名字含 dotfiles）的目录。"""
    cands: list[Path] = []
    for p in list(home.glob("*dotfiles*")) + list(home.glob("*/*dotfiles*")):
        if (p / "skills").is_dir():
            cands.append(p)
    # 再扫一层：agent-dotfiles/xxx 这种两级
    for p in home.glob("*/*/"):
        if (p / "skills").is_dir() and "dotfiles" in str(p).lower():
            cands.append(p)
    return sorted(set(cands), key=lambda x: str(x))


def freshness(copy: Path) -> tuple[int, str]:
    g = git_commit_time(copy)
    if g:
        return g, "git 提交"
    return newest_file_mtime(copy / "skills"), "文件 mtime"


# ---------- 动作 ----------
def make_link(link: Path, target: Path, apply: bool) -> bool:
    # 调用方通常已先删旧链接；这里再兜一层：若 DEST 仍存在，`ln -s` 会把链接
    # 建到目标目录**内部**（而不是替换它），mklink 则会直接失败。
    if apply and (is_link(link) or link.exists()):
        remove_link(link, apply)
    if os.name == "nt":
        cmd = ["cmd", "/c", "mklink", "/J", str(link), str(target)]   # 目录联接，无需管理员
    else:
        cmd = ["ln", "-s", str(target), str(link)]                    # Linux/macOS，避免 -n/-T 等 GNU 专属
    print("      $ " + " ".join(cmd))
    if apply:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print("      !! 失败: " + (r.stdout or "") + (r.stderr or ""))
            return False
    return True


def remove_link(p: Path, apply: bool) -> None:
    if os.name == "nt":
        cmd = ["cmd", "/c", "rmdir", str(p)]      # junction/symlink 都能这样删（不带 /S 不会删目标内容）
    else:
        cmd = ["rm", "-f", str(p)]
    print("      $ " + " ".join(cmd))
    if apply:
        subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")


def backup_dir(p: Path, apply: bool, backup_root: Path) -> Path:
    client = p.parent.name.lstrip(".") or "client"
    dst = backup_root / (time.strftime("%Y%m%d-%H%M%S") + "-" + client + "-" + p.name)
    print("      $ mv \"%s\" \"%s\"" % (p, dst))
    if apply:
        backup_root.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(dst))
    return dst


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--home", default=str(Path.home()), help="用户目录（默认自动）")
    ap.add_argument("--apply", action="store_true", help="真正执行（默认只体检）")
    ap.add_argument("--force", action="store_true", help="即使有独有 skill 也强制重定向")
    args = ap.parse_args()

    home = Path(args.home)
    print("=" * 78)
    print("skills 统一指向    home=%s    模式=%s" % (home, "APPLY（会改动）" if args.apply else "DRY-RUN（只报告）"))
    print("=" * 78)

    # 1. 现状
    clients = find_client_skills(home)
    copies = find_dotfiles_copies(home)
    if not copies:
        print("\n!! 没找到任何 dotfiles 副本（含 skills/ 的 *dotfiles* 目录），无法确定权威来源。")
        return 2

    print("\n【1】dotfiles 副本（按新鲜度排序）")
    ranked = sorted(((freshness(c), c) for c in copies), key=lambda x: -x[0][0])
    for (ts, how), c in ranked:
        g = git_commit_time(c)
        branch = ""
        if g:
            try:
                branch = subprocess.run(["git", "-C", str(c), "rev-parse", "--abbrev-ref", "HEAD"],
                                        capture_output=True, text=True).stdout.strip()
            except Exception:
                pass
        print("   %-58s %s (%s) %s" % (str(c).replace(str(home), "~"), fmt_time(ts), how, branch))
    authority = ranked[0][1]
    print("\n   → 权威副本: %s" % str(authority).replace(str(home), "~"))

    # 2. 客户端现状
    print("\n【2】客户端 skills 现状")
    print("   %-46s %-10s %s" % ("路径", "形态", "项数 / 指向"))
    for p, tgt in clients.items():
        shape = "链接" if tgt else "真实目录"
        info = (str(Path(tgt)).replace(str(home), "~") if tgt else "%d 项" % len(skill_names(p)))
        print("   %-46s %-10s %s" % (str(p).replace(str(home), "~"), shape, info))

    # 3. 逐个客户端决策
    auth_names = skill_names(authority / "skills")
    print("\n【3】决策")
    backup_root = home / ".skills-link-backups"
    todo: list[str] = []
    for p, tgt in clients.items():
        pp = str(p).replace(str(home), "~")
        if tgt and Path(tgt).resolve() == (authority / "skills").resolve():
            print("   ✅ %-44s 已指向权威副本，跳过" % pp)
            continue
        own = skill_names(p) - auth_names
        if own:
            print("   ⚠️  %-44s 有 %d 个独有 skill（重定向后会丢）：%s"
                  % (pp, len(own), ", ".join(sorted(own)[:6]) + ("..." if len(own) > 6 else "")))
            if not args.force:
                print("         → 跳过（如需丢弃这些独有 skill，加 --force）")
                continue
            print("         → --force：将被移入备份，不会真丢")
        print("   🔁 %-44s → 指向权威副本" % pp)
        todo.append(pp)
        if tgt:
            remove_link(p, args.apply)
        elif p.exists():
            b = backup_dir(p, args.apply, backup_root)
            todo.append("      备份: " + str(b).replace(str(home), "~"))
        make_link(p, authority / "skills", args.apply)

    # 4. 旧副本处理
    stale = [c for _, c in ranked[1:]]
    if stale:
        print("\n【4】旧副本（建议清理，已保留不删）")
        for c in stale:
            print("   📦 %-58s %s" % (str(c).replace(str(home), "~"), fmt_time(freshness(c)[0])))
        print("   → 本脚本不会自动删；确认无用后手工删除，或加 --apply 时它会提示是否移入备份")

    print("\n" + "=" * 78)
    if args.apply:
        print("执行完毕。备份目录: %s" % str(backup_root).replace(str(home), "~"))
        print("提示：若开了新客户端，重跑本脚本即可让它也指过来。")
    else:
        print("以上为体检结果，未做任何改动。确认无误后加 --apply 执行。")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
