#!/usr/bin/env python3
"""
E13 逃生动作入口审计 —— 把"清除 / 取消 / 返回 / 刷新 / 重置"这类**逃生动作**的
全部入口列出来，按**动作族**分组，标注每个入口的渲染条件（常驻？门控？菜单型？），
并生成待填的「入口 × 状态边界」矩阵骨架。

它对应 debug-and-refactor 的 E13（交互点在特定状态下不可达）——把 E13 从
"一段案例叙述"变成"一条命令 + 一张表"，和 audit_styles.py 对 E12 做的一样。

用法
----
    python audit_escape_entries.py --root <前端源码目录>
    python audit_escape_entries.py --root web/src --out escape-report.md

可靠性分级（重要，别越级采信）
------------------------------
- **高可靠**：关键仅在**UI 文本位**（JSX 文本节点 / 字符串字面量 / label·title 属性）匹配，
  不在注释、不在标识符里匹配（所以 `backdrop`/`fallback`/`close()` 不会被误当成入口）。
- **低可靠**：*"该入口是否被门控 / 是否常驻"* 是**行扫描近邻推断**，判不准 DOM 层级与多行嵌套。
  输出里的「疑似门控」必须**人工核实**后才可采信。
- 本脚本**不判断可达性**。可达性只有三种办法确证：读门控条件、看 DOM、**跑起来点**
  （零行 / 出错 / 门控未开 / 超宽 四个状态各一次）。矩阵里的格子默认 `?`。
"""

import argparse
import os
import re
import sys

# 动作族：用户"想退出当前困境"时按族去找入口
FAMILIES = [
    ("清除 / 重置", ["清除", "清空", "重置", "clear", "reset"]),
    ("取消", ["取消", "cancel", "dismiss"]),
    ("返回 / 关闭", ["返回", "关闭", "back", "close", "exit"]),
    ("刷新 / 重试", ["刷新", "重试", "refresh", "retry", "reload"]),
    ("撤销 / 恢复", ["撤销", "还原", "恢复", "undo", "revert", "restore"]),
]

SUFFIXES = (".tsx", ".jsx", ".ts", ".js", ".vue")
SKIP_DIRS = {"node_modules", "dist", "build", ".git", "coverage", ".next"}

RE_COMMENT = re.compile(r"^\s*(//|/\*|\*|#|<!--)")
RE_MENU_ITEM = re.compile(r"label\s*:\s*['\"`]")
RE_CLICKABLE = re.compile(r"<[Bb]utton|<[Aa]\b|onClick=|onContextMenu=|<[Ss]elect|<[Oo]ption")
RE_TAG = re.compile(r"<[A-Za-z]")
# 门控签名收紧：行尾是 `&& (` / `&&` / `? (` —— 这才是"整块 JSX 被条件包住"的形态
RE_GATE = re.compile(r"&&\s*\(?\s*$|\?\s*\(?\s*$")
RE_TEXT_NODE = re.compile(r">([^<>{}]{1,40})<")
RE_ATTR_TEXT = re.compile(r"""(?:label|title|placeholder|text|children)\s*[:=]\s*['"`]([^'"`]{1,40})['"`]""")
RE_LITERAL = re.compile(r"""['"`]([^'"`\n]{1,40})['"`]""")
RE_ONLY_TEXT = re.compile(r"^\s*[\u4e00-\u9fa5A-Za-z0-9\s，。、·:：\-—/()（）]{1,40}\s*$")


def ui_texts(line: str):
    """只取该行出现的 **UI 文本候选**（高可靠：不在标识符/注释里匹配）。"""
    if RE_COMMENT.match(line):
        return []
    out = []
    for rx in (RE_TEXT_NODE, RE_ATTR_TEXT, RE_LITERAL):
        out.extend(m.group(1) for m in rx.finditer(line))
    s = line.strip()
    # 多行 JSX 文本节点：整行只有文字（如 `<button>` 与 `</button>` 之间的那行）
    if RE_ONLY_TEXT.match(line) and not RE_TAG.search(s):
        out.append(s)
    return [t for t in out if t]


def match_family(text: str):
    low = text.lower()
    for fam, kws in FAMILIES:
        for k in kws:
            if k.isascii():
                if re.search(rf"\b{re.escape(k)}\b", low):
                    return fam, k
            elif k in text:
                return fam, k
    return None, None


def find_gate(lines, idx, back=25):
    """向上找最近的门控（低可靠：收紧签名 = 行尾 `&&` / `&& (`）。"""
    for j in range(idx - 1, max(-1, idx - back - 1), -1):
        s = lines[j].rstrip()
        if s.strip().startswith(("//", "*", "/*")):
            continue
        if RE_GATE.search(s) and ("{" in s or s.strip().startswith("{")):
            return s.strip()[:110], idx - j
    return None, None


def carrier(line: str) -> str:
    if RE_MENU_ITEM.search(line):
        return "菜单项(需目标元素)"
    if RE_CLICKABLE.search(line):
        return "按钮/控件"
    return "文本节点"


def scan(root: str):
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(SUFFIXES):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    lines = fh.readlines()
            except OSError:
                continue
            rel = os.path.relpath(path, root).replace("\\", "/")
            for i, raw in enumerate(lines):
                # 同一行多个文本候选只留最长的一个（去重：`清空表 (TRUNCATE)` 与 `清空` 是同一入口）
                matched = {}
                for text in ui_texts(raw):
                    fam, kw = match_family(text)
                    if fam and (fam not in matched or len(text) > len(matched[fam][0])):
                        matched[fam] = (text.strip(), kw)
                for fam, (text, kw) in matched.items():
                    gate, dist = find_gate(lines, i)
                    car = carrier(raw)
                    if car.startswith("菜单项"):
                        nature = "菜单型(需目标元素)"
                    elif gate:
                        nature = "门控"
                    else:
                        nature = "常驻候选"
                    hits.append({
                        "file": rel, "line": i + 1, "family": fam, "kw": kw,
                        "text": text, "carrier": car, "nature": nature,
                        "gate": gate, "gate_dist": dist,
                    })
    return hits


def build_report(hits, root):
    L = [f"# 逃生动作入口审计（E13）\n",
         f"- 扫描根目录：`{root}`",
         f"- 命中入口：**{len(hits)}** 条（只匹配 UI 文本位 —— 高可靠）",
         f"- 可靠性：**「疑似门控 / 是否常驻」为行扫描近邻推断，低可靠，必须人工核实**\n"]

    fams = {}
    for h in hits:
        fams.setdefault(h["family"], []).append(h)

    L.append("## 一、按动作族分组的入口清单\n")
    L.append("> 纪律：**每个「具体动作」至少要有一个不依赖数据状态的常驻入口**，")
    L.append("> 否则用户陷入困境时无路可走（E13 的现场：清不掉、只能刷新）。")
    L.append("> ⚠️ **判定单位是「具体动作对象」，不是关键词族**：`清除筛选` 与 `清空表` 都在")
    L.append("> 「清除」族里，但它们是两件事 —— **别用族级的数字给自己虚假安慰**。\n")

    for fam, _ in FAMILIES:
        rows = fams.get(fam, [])
        if not rows:
            continue
        res = [r for r in rows if r["nature"] == "常驻候选"]
        gat = [r for r in rows if r["nature"] == "门控"]
        men = [r for r in rows if r["nature"].startswith("菜单型")]
        L.append(f"### {fam} —— 入口 {len(rows)} 个：常驻候选 {len(res)} · 门控 {len(gat)} · 菜单型 {len(men)}\n")
        L.append("| # | 位置 | 文案 | 性质 | 疑似门控条件（**需人工核实**） |")
        L.append("|---|---|---|---|---|")
        for n, r in enumerate(rows, 1):
            g = r["gate"] if r["gate"] else "—"
            L.append(f"| {n} | `{r['file']}:{r['line']}` | {r['text'][:24]} | {r['nature']} | `{g}` |")
        L.append("")
        L.append("> 逐条自问：**上表里哪个入口，在「零行 / 出错 / 门控未开」时还碰得到？**")
        L.append("> 若某个具体动作（如「清除筛选」）名下**只有 门控 / 菜单型**入口 → 该动作在边界态下")
        L.append("> 很可能整族不可达。修法：给它加一个**常驻入口**（不依赖数据、不依赖折叠状态）。\n")

    L.append("## 二、状态边界矩阵（**待填**：每格 ✅可达 / ❌不可达 / ?未验证）\n")
    L.append("四类边界按 E13：**零行·空结果 / 查询出错 / 门控未开·默认折叠 / 超宽超长**。")
    L.append("每格三问：**在 DOM 里吗？够得着吗？动作还成立吗？**\n")
    L.append("| 动作族 | 零行·空结果 | 查询出错 | 门控未开 | 超宽超长 |")
    L.append("|---|---|---|---|---|")
    for fam, _ in FAMILIES:
        if fams.get(fam):
            L.append(f"| {fam} | ? | ? | ? | ? |")
    L.append("\n> 填表纪律：**禁止只验证你自己举的例子**（E13 的四个子情形是例证，不是验证对象）。")
    L.append("> 必须逐个入口 × 逐个状态实际去过一遍；表里任何 `?` 都要出现在结论的缺口清单里，")
    L.append("> 不能只在末尾一句「未覆盖」带过。\n")

    L.append("## 三、可达性确证的三条路（缺一不可）\n")
    L.append("1. **读门控条件**：`{showX && data && ...}` 要看它依赖**数据内容**还是**开关** ——")
    L.append("   内部要用 `data.columns` 的不能盲目放宽门控（去了会崩）。")
    L.append("2. **看 DOM**：入口在 DOM 里 ≠ 够得着（可能在视口外、或被 `overflow:hidden` 裁掉）。")
    L.append("3. **跑起来点**：四个状态边界各点一次 —— 这是**唯一**能确证的办法。")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="E13 逃生动作入口审计")
    ap.add_argument("--root", required=True, help="前端源码目录")
    ap.add_argument("--out", default=None, help="报告输出路径（默认打印到 stdout）")
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        print(f"目录不存在：{args.root}", file=sys.stderr)
        return 2
    hits = scan(args.root)
    text = build_report(hits, args.root)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"已写出报告：{args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
