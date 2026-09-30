#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
库层技能 gate —— 让它们退出常驻索引，只在被显式需要时加载。

背景
----
Codex 递归扫描 $CODEX_HOME/skills，**不分层**。本仓库 INDEX.md 把技能分成
「顶层活跃层」与「分类库层」，但 Codex 两边都扫：实测 273 条索引里 205 条是
库层，占 77% 的常驻 token，每一轮请求都要付。

Codex 原生支持 per-skill 退出索引（skill-creator/references/openai_yaml.md）：
    agents/openai.yaml → policy.allow_implicit_invocation: false
「技能不进模型上下文，但仍可 $skill 显式调用」。默认 true。

本脚本给库层技能批量写入该配置，把索引压回活跃层规模。发现通道不变：
find-skills 路由表 + INDEX.md + rg 检索（都只在需要时加载）。

用法
----
    python scripts/gate-library-skills.py                    # 体检（只读）
    python scripts/gate-library-skills.py --apply            # 写入 gate
    python scripts/gate-library-skills.py --revert --apply   # 撤销 gate

设计原则：**幂等**。重复运行结果一致；--revert 只移除本脚本写入的 gate，
不碰技能自身的其它 openai.yaml 字段。
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

try:
    _stream = sys.stdout
    _stream.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
META = ".system"
PRUNE = {".git", "node_modules", "__pycache__", ".venv"}
YAML_NAME = "openai.yaml"

GATE_TEMPLATE = """interface:
  display_name: "{display}"
  short_description: "{short}"

policy:
  allow_implicit_invocation: false
"""


def library_skills() -> list[Path]:
    """库层 = 嵌套深度 > 1 的 skill（顶层平铺的是活跃层）。"""
    out = []
    for dirpath, dirs, files in os.walk(SKILLS):
        dirs[:] = [d for d in dirs if d not in PRUNE]
        if "SKILL.md" not in files:
            continue
        d = Path(dirpath)
        rel = d.relative_to(SKILLS)
        if len(rel.parts) > 1 and META not in rel.parts:
            out.append(d)
    return sorted(out)


def display_name(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.split("-") if w)


def short_desc(skill: Path) -> str:
    """从 SKILL.md 的 description 取一句短摘要（25-64 字符）。"""
    try:
        txt = (skill / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return display_name(skill.name)
    m = re.match(r"^---\r?\n(.*?)\r?\n---", txt, re.S)
    desc = ""
    if m:
        dm = re.search(r"^description:\s*(.*?)(?=^\w+:|\Z)", m.group(1), re.S | re.M)
        if dm:
            desc = re.sub(r"^[>|][-+]?\s*", "", dm.group(1).strip())
            desc = re.sub(r"\s+", " ", desc).strip().strip('"')
    if not desc:
        return display_name(skill.name)
    first = re.split(r"(?<=[.。!?！？])\s", desc)[0].strip()
    if len(first) > 64:
        first = first[:61].rstrip() + "..."
    return first.replace('"', "'")


def yaml_path(skill: Path) -> Path:
    return skill / "agents" / YAML_NAME


def has_gate(p: Path) -> bool:
    if not p.is_file():
        return False
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    m = re.search(r"^\s*allow_implicit_invocation\s*:\s*(\S+)", t, re.M)
    return bool(m and m.group(1).strip().lower() in ("false", "no", "off"))


def write_gate(skill: Path, apply: bool) -> str:
    p = yaml_path(skill)
    if p.is_file():
        t = p.read_text(encoding="utf-8", errors="replace")
        if re.search(r"^\s*allow_implicit_invocation\s*:", t, re.M):
            new = re.sub(r"(^\s*allow_implicit_invocation\s*:\s*)\S+", r"\1false", t, flags=re.M)
        elif re.search(r"^policy\s*:", t, re.M):
            new = re.sub(r"(^policy\s*:\s*\n)", r"\1  allow_implicit_invocation: false\n", t, flags=re.M)
        else:
            new = t.rstrip("\n") + "\n\npolicy:\n  allow_implicit_invocation: false\n"
        if new != t:
            if apply:
                p.write_text(new, encoding="utf-8", newline="\n")
            return "改写现有"
        return "已是 gate"
    body = GATE_TEMPLATE.format(display=display_name(skill.name), short=short_desc(skill))
    if apply:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8", newline="\n")
    return "新建"


def revert_gate(skill: Path, apply: bool) -> str:
    p = yaml_path(skill)
    if not p.is_file():
        return "无配置"
    t = p.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"^\s*allow_implicit_invocation\s*:", t, re.M):
        return "无 gate"
    new = re.sub(r"(^\s*allow_implicit_invocation\s*:\s*)\S+", r"\1true", t, flags=re.M)
    if apply:
        p.write_text(new, encoding="utf-8", newline="\n")
    return "已撤销"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真正写入（默认只报告）")
    ap.add_argument("--revert", action="store_true", help="撤销 gate（改回 true）")
    args = ap.parse_args()

    lib = library_skills()
    print("=" * 74)
    print("库层技能 gate    root=%s" % SKILLS)
    print("模式=%s%s" % ("APPLY" if args.apply else "DRY-RUN（只报告）",
                        "  动作=REVERT" if args.revert else ""))
    print("=" * 74)

    todo, done, skip = [], 0, 0
    for s in lib:
        rel = s.relative_to(SKILLS).as_posix()
        if args.revert:
            r = revert_gate(s, args.apply)
            if r == "已撤销":
                todo.append(rel)
            else:
                skip += 1
        else:
            if has_gate(yaml_path(s)):
                done += 1
                continue
            r = write_gate(s, args.apply)
            todo.append("%s  (%s)" % (rel, r))

    print("\n库层技能 %d 个" % len(lib))
    if args.revert:
        print("待撤销 %d   无需处理 %d" % (len(todo), skip))
    else:
        print("已是 gate %d   本次处理 %d" % (done, len(todo)))
    for r in todo[:15]:
        print("   " + r)
    if len(todo) > 15:
        print("   ... 另有 %d 个" % (len(todo) - 15))
    print("\n" + "=" * 74)
    if not args.apply:
        print("以上为体检结果，未做任何改动。确认无误后加 --apply 执行。")
    else:
        print("执行完毕。")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
