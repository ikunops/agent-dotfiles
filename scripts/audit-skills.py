#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skills 库体检 —— 把账一次算清。

用法
----
    python scripts/audit-skills.py             # 体检（只读，不写任何东西）
    python scripts/audit-skills.py --strict    # 有发现则 exit 1（可挂 push 前钩子 / CI）
    python scripts/audit-skills.py --json      # 机器可读输出

检查项
------
  A 空壳         SKILL.md 0 字节 / 任何 0 字节文件（__init__.py 豁免）/ 顶层目录整个不是 skill
  B frontmatter  活跃层：无 frontmatter / 缺 name / 缺 description / name != 目录名\n                 （库层同类问题只提示、不计入问题）
  C 重名         跨层同名 skill；逐对树哈希判「一致」/「仅行尾不同」/「已分叉」，
                 并按 INDEX.md 的登记层给出「正身应该在哪」
  D 嵌套         skill 内部又套了 skill（vendor 目录夹带的 .claude/skills 等）
  E 语言         正文以中文为主、description 却纯英文（风格割裂）
  F 登记         INDEX.md 与磁盘双向核对（登记未落盘 / 落盘未登记）

设计原则：**只读**。本脚本永不修改、删除、移动任何文件 —— 修不修由人决定。

为什么重名要「行尾归一后」再比
------------------------------
本仓库 .gitattributes 规定 *.md/*.py 一律 LF，但工作区常因 Windows 工具回写成 CRLF。
若直接按字节哈希，会把「纯行尾差异」误报成「内容分叉」。所以先 CRLF→LF 再哈希，
并把「仅行尾不同」单列一类：它不是分叉，但仍然是该合并的信号。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

# 控制台编码兜底（Windows GBK 下 emoji 会崩，同 sync-skills-links.py）
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        try:
            _stream.reconfigure(errors="replace")
        except Exception:
            pass

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
INDEX = SKILLS / "INDEX.md"

CONTAINERS = {"function-specific", "framework-specific", "platform-specific"}
META = ".system"
PRUNE = {".git", "node_modules", "__pycache__", ".venv"}

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.S)
CIRCLED = re.compile(r"^[①②③④⑤⑥⑦⑧⑨⑩]")


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def norm(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n")


def tree_hash(d: Path, normalize: bool = True) -> str:
    h = hashlib.sha256()
    for root, dirs, files in os.walk(d):
        dirs[:] = sorted(x for x in dirs if x not in PRUNE)
        for f in sorted(files):
            p = Path(root) / f
            h.update(os.path.relpath(str(p), str(d)).replace("\\", "/").encode("utf-8"))
            try:
                b = p.read_bytes()
            except Exception:
                b = b""
            h.update(norm(b) if normalize else b)
    return h.hexdigest()[:12]


def parse_fm(p: Path):
    """返回 (name, description, body)。无 frontmatter -> (None, None, text)"""
    txt = read_text(p)
    m = FM_RE.match(txt)
    if not m:
        return None, None, txt
    fm = m.group(1)
    body = txt[m.end():]

    def field(key: str):
        mm = re.search(r"^%s:\s*(.*)$" % key, fm, re.M)
        if not mm:
            return None
        val = mm.group(1).strip()
        if val in (">", ">-", "|", "|-", ">+", "|+"):
            lines = fm.split("\n")
            i = next((i for i, l in enumerate(lines) if re.match(r"^%s:" % key, l)), None)
            if i is None:
                return ""
            buf = []
            for l in lines[i + 1:]:
                if not l.strip():
                    buf.append("")
                    continue
                if not l.startswith((" ", "\t")):
                    break
                buf.append(l.strip())
            return " ".join(x for x in buf if x).strip()
        return val.strip("\"'")

    return field("name"), field("description"), body


def find_skills(root: Path):
    out = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in PRUNE]
        if "SKILL.md" in files:
            out.append(Path(dirpath))
    return sorted(out)


def expand_shorthand(tok: str):
    """`diagnosing-skills/-commands/-hooks` -> diagnosing-skills / diagnosing-commands / ..."""
    if "/" not in tok:
        return [tok]
    parts = tok.split("/")
    head = parts[0]
    pre = head[:head.rfind("-") + 1] if "-" in head else ""
    out = [head]
    for p in parts[1:]:
        out.append(pre + p.lstrip("-"))
    return out


def index_layers():
    """解析 INDEX.md -> (active_names, library_names)"""
    txt = read_text(INDEX)
    active, library = set(), set()
    bucket = None
    for line in txt.split("\n"):
        s = line.strip()
        if s.startswith("##") or s.startswith("###"):
            head = s.lstrip("#").strip()
            if "库层" in head or "镜像" in head:
                bucket = "library"
            elif CIRCLED.match(head):
                bucket = "active"
            else:
                bucket = None
            continue
        if bucket and "`" in line:
            # 先剥掉括号内的说明（交叉引用都写在括号里，如 ⑦b 的
            # "（通用; OpenCode 专属流程仍走 `opencode-skill-creator`）"），
            # 再把 `diagnosing-skills/-commands/-hooks` 这类省略前缀写法展开。
            stripped = re.sub(r"[（(][^）)]*[）)]", "", line)
            for tok in re.findall(r"`([A-Za-z0-9][A-Za-z0-9._/-]*)`", stripped):
                for nm in expand_shorthand(tok):
                    (active if bucket == "active" else library).add(nm)
    return active, library


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="有发现则 exit 1")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    args = ap.parse_args()

    all_skills = find_skills(SKILLS)
    meta = [d for d in all_skills if META in d.relative_to(SKILLS).parts]
    rest = [d for d in all_skills if d not in meta]
    active = [d for d in rest if d.parent == SKILLS]
    library = [d for d in rest if d.parent != SKILLS]

    idx_active, idx_library = index_layers()
    findings = {"shell": [], "fm": [], "fm_info": [], "dup": [], "nested": [], "lang": [], "index": []}

    # ---------- A 空壳 ----------
    for d in all_skills:
        sk = d / "SKILL.md"
        try:
            if sk.stat().st_size == 0:
                findings["shell"].append({"path": str(d.relative_to(SKILLS)), "why": "SKILL.md 0 字节"})
        except OSError:
            pass
    for name in sorted(os.listdir(SKILLS)):
        p = SKILLS / name
        if not p.is_dir() or name in CONTAINERS or name == META:
            continue
        if not (p / "SKILL.md").exists():
            deep = [x for x in all_skills if p in x.parents]
            why = ("非 skill 目录（%d 层下才有 SKILL.md：%s）"
                   % (len(deep[0].relative_to(p).parts), deep[0].relative_to(p))) if deep else "无 SKILL.md"
            findings["shell"].append({"path": name, "why": why})

    # 全库 0 字节文件（__init__.py 空文件是合法的 Python 包标记，豁免）
    for root, dirs, files in os.walk(SKILLS):
        dirs[:] = [x for x in dirs if x not in PRUNE]
        for f in files:
            if f == "__init__.py":
                continue
            fp = Path(root) / f
            try:
                if fp.stat().st_size == 0:
                    findings["shell"].append({"path": str(fp.relative_to(SKILLS)), "why": "0 字节文件"})
            except OSError:
                pass

    # ---------- B frontmatter ----------
    # 活跃层必须规范（模型直接读它来触发）；库层多为上游原样，name 与目录名不一致属正常，
    # 降级为提示、不当作问题 —— 改了反而跟上游分叉，下次重拷又回来。
    active_set = set(active)
    info = {}
    for d in all_skills:
        name, desc, body = parse_fm(d / "SKILL.md")
        info[d] = (name, desc, body)
        rel = str(d.relative_to(SKILLS))
        key = "fm" if d in active_set else "fm_info"
        if name is None and desc is None:
            findings[key].append({"path": rel, "why": "无 frontmatter"})
            continue
        if not name:
            findings[key].append({"path": rel, "why": "缺 name"})
        if not desc:
            findings[key].append({"path": rel, "why": "缺 description"})
        if name and name != d.name:
            findings[key].append({"path": rel, "why": "name(%s) != 目录名(%s)" % (name, d.name)})

    # ---------- C 重名 ----------
    groups = {}
    for d in rest:
        groups.setdefault(d.name, []).append(d)
    for name, ds in sorted(groups.items()):
        if len(ds) < 2:
            continue
        hashes = {d: tree_hash(d) for d in ds}
        raw = {d: tree_hash(d, normalize=False) for d in ds}
        if len(set(hashes.values())) == 1:
            verdict = "一致"
        elif len(set(raw.values())) == 1:
            verdict = "一致（原始字节也同）"
        else:
            verdict = "已分叉"
        where = []
        if name in idx_active:
            where.append("活跃层")
        if name in idx_library:
            where.append("库层")
        findings["dup"].append({
            "name": name,
            "copies": [str(d.relative_to(SKILLS)) for d in ds],
            "layers": ["活跃层" if d.parent == SKILLS else "库层" for d in ds],
            "hashes": [hashes[d] for d in ds],
            "verdict": verdict,
            "index_says": "/".join(where) if where else "（未登记）",
        })

    # ---------- D 嵌套 ----------
    for d in all_skills:
        for anc in all_skills:
            if anc != d and anc in d.parents:
                findings["nested"].append({
                    "path": str(d.relative_to(SKILLS)),
                    "inside": str(anc.relative_to(SKILLS)),
                })
                break

    # ---------- E 语言 ----------
    for d in active:
        name, desc, body = info[d]
        if not desc or CJK_RE.search(desc):
            continue
        stripped = re.sub(r"\s+", "", body)
        if not stripped:
            continue
        ratio = len(CJK_RE.findall(stripped)) / len(stripped)
        if ratio > 0.15:
            findings["lang"].append({"path": d.name, "body_cjk": round(ratio, 2)})

    # ---------- F INDEX 登记 ----------
    disk = {d.name for d in rest}
    for n in sorted((idx_active | idx_library) - disk):
        findings["index"].append({"path": n, "why": "INDEX 登记了但磁盘没有"})
    for n in sorted({d.name for d in active} - idx_active - idx_library):
        findings["index"].append({"path": n, "why": "活跃层存在但 INDEX 未登记"})

    total = sum(len(v) for k, v in findings.items() if k != "fm_info")

    if args.json:
        print(json.dumps({"scale": {"active": len(active), "library": len(library), "meta": len(meta)},
                          "total_findings": total, "findings": findings},
                         ensure_ascii=False, indent=2))
        return 1 if (args.strict and total) else 0

    W = 78
    print("=" * W)
    print("skills 库体检    root=%s" % SKILLS)
    print("=" * W)
    print("\n【规模】")
    print("  活跃层（顶层平铺，自动触发）  %d" % len(active))
    print("  库存层（分类目录，按需取用）  %d" % len(library))
    print("  .system（客户端官方件）      %d" % len(meta))
    print("  合计                        %d" % (len(active) + len(library) + len(meta)))

    def sec(title, key, render):
        rows = findings[key]
        print("\n【%s】%s" % (title, "OK 无问题" if not rows else "%d 处" % len(rows)))
        for r in rows:
            print("   " + render(r))

    sec("A 空壳", "shell", lambda r: "X  %-50s %s" % (r["path"], r["why"]))
    sec("B frontmatter（活跃层）", "fm", lambda r: "X  %-50s %s" % (r["path"], r["why"]))
    if findings["fm_info"]:
        print("\n【B' 库层 frontmatter（提示，不计入问题）】%d 处" % len(findings["fm_info"]))
        for r in findings["fm_info"]:
            print("   .  %-50s %s" % (r["path"], r["why"]))

    rows = findings["dup"]
    print("\n【C 重名】%s" % ("OK 无问题" if not rows else "%d 组" % len(rows)))
    if rows:
        print("   %-25s %-7s %-7s %-16s %s" % ("skill", "第1份", "第2份", "比对结果", "INDEX 说正身在"))
        for r in rows:
            flag = "!" if r["verdict"] == "已分叉" else " "
            print("   %s %-24s %-7s %-7s %-16s %s"
                  % (flag, r["name"], r["layers"][0], r["layers"][1], r["verdict"], r["index_says"]))

    sec("D 嵌套", "nested", lambda r: "X  %-50s 套在 %s 里" % (r["path"], r["inside"]))
    sec("E 语言割裂", "lang", lambda r: "X  %-50s 正文中文占比 %.0f%%" % (r["path"], r["body_cjk"] * 100))
    sec("F INDEX 登记", "index", lambda r: "X  %-50s %s" % (r["path"], r["why"]))

    print("\n" + "=" * W)
    print("共 %d 处发现。本脚本只读，未改动任何文件。" % total)
    print("=" * W)
    return 1 if (args.strict and total) else 0


if __name__ == "__main__":
    sys.exit(main())
