#!/usr/bin/env python3
"""
前端 UI 一致性审计 —— **`ui-acceptance`「横向一致性（众数判定）」的机械化执行器**。

核心立场（重要）：
    数值本身没有绝对标准 —— 不同项目字号/尺寸差一两号很正常。
    **唯一要保障的是"同一个程序内部跨页面一致"**。
    所以本脚本**不比对任何写死的白名单**，而是：
      1. 统计项目里**硬编码字面量**的真实分布（用了 `var(--x)` 的不算，那是已 token 化）
      2. **取众数 = 该项目的事实基准**
      3. **非众数的少数派 = 离群嫌疑**，按 `ui-acceptance` 的固定格式汇报：
         《N 处中 M 处是 X，这 K 处是 Y》

用法
----
    python audit_ui_consistency.py --root <前端源码>
    python audit_ui_consistency.py --root web/src --out ui-audit.md
    python audit_ui_consistency.py --root web/src --props font,height,zindex --max-list 8

可靠性分级
----------
- **高可靠**：某个字面量出现了几次、众数是谁 —— 计数事实，不会误报。
- **低可靠**：*"这一处离群是不是错"* 无法自动判定 —— 可能是刻意设计、第三方覆盖、
  对齐补偿、或者本来就该是另一个语义层级。**必须人工核实后才可采信**。
"""

import argparse
import io
import os
import re
import sys
from collections import Counter, defaultdict

SUFFIXES = (".css", ".scss", ".less", ".tsx", ".jsx", ".ts", ".js", ".vue")
SKIP_DIRS = {"node_modules", "dist", "build", ".git", "coverage", ".next"}
REM_BASE = 16.0

PROPS = ("font", "height", "space", "radius", "zindex", "color")
PROP_LABEL = {
    "font": "字号 font-size", "height": "控件高度 height", "space": "间距 margin/padding/gap",
    "radius": "圆角 border-radius", "zindex": "层级 z-index", "color": "硬编码颜色",
}

RE_FONT = re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)(px|rem)")
RE_HEIGHT = re.compile(r"(?<!line-)(?<!min-)(?<!max-)(?<!box-)\bheight\s*:\s*(\d+(?:\.\d+)?)(px|rem)")
RE_SPACE = re.compile(
    r"\b(margin|padding|gap|row-gap|column-gap|margin-top|margin-bottom|margin-left|margin-right|"
    r"padding-top|padding-bottom|padding-left|padding-right)\s*:\s*([^;}]+)")
RE_RADIUS = re.compile(r"border-radius\s*:\s*([^;}]+)")
RE_Z = re.compile(r"z-index\s*:\s*(-?\d+)")
RE_COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+")


def norm(num, unit):
    v = float(num) * (REM_BASE if unit == "rem" else 1.0)
    v = round(v, 2)
    return int(v) if abs(v - int(v)) < 1e-6 else v


def collect(path):
    """返回 {prop: [(value, line, snippet), ...]}"""
    out = defaultdict(list)
    try:
        with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().split("\n")
    except OSError:
        return out
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if s.startswith(("//", "*", "/*", "<!--")):
            continue
        # 已 token 化的跳过（用 var(--x) 是好事，不该被当成离群；下面各处单独判 var(）
        for m in RE_FONT.finditer(ln):
            if "var(" not in m.group(0):
                out["font"].append((norm(m.group(1), m.group(2)), i, s[:80]))
        for m in RE_HEIGHT.finditer(ln):
            if "var(" not in m.group(0):
                v = norm(m.group(1), m.group(2))
                # 1px / 2px 多为分隔线、边框、对齐补偿，不是"控件高度"
                if v >= 16:
                    out["height"].append((v, i, s[:80]))
        for m in RE_SPACE.finditer(ln):
            if "var(" in m.group(2):
                continue
            for mm in re.finditer(r"(\d+(?:\.\d+)?)(px|rem)", m.group(2)):
                out["space"].append((norm(mm.group(1), mm.group(2)), i, s[:80]))
        for m in RE_RADIUS.finditer(ln):
            if "var(" in m.group(1):
                continue
            for mm in re.finditer(r"(\d+(?:\.\d+)?)(px|rem)", m.group(1)):
                out["radius"].append((norm(mm.group(1), mm.group(2)), i, s[:80]))
        for m in RE_Z.finditer(ln):
            out["zindex"].append((int(m.group(1)), i, s[:80]))
        for m in RE_COLOR.finditer(ln):
            out["color"].append((m.group(0).lower(), i, s[:80]))
    return out


def report(data, root, props, max_list):
    L = ["# 前端 UI 一致性审计（众数判定）\n",
         f"- 扫描根目录：`{root}`",
         "- **基准来源：项目自身的分布众数**（不是任何写死的白名单）",
         "- 判定规则（取自 `ui-acceptance` 横向一致性）：**取众数为基准，离群者报 FAIL**，"
         "汇报格式固定为《N 处中 M 处是 X，这 K 处是 Y》\n",
         "> ⚠️ **可靠性**：计数与众数 = 高可靠；**「这一处离群是不是错」 = 低可靠**，"
         "刻意设计 / 第三方覆盖 / 语义层级不同都会离群，**必须人工核实后才可采信**。\n"]

    L.append("## 一、项目的事实基准（众数）\n")
    L.append("| 属性 | 总处数 | 众数（事实基准） | 众数占比 | 不同取值数 |")
    L.append("|---|---:|---|---:|---:|")
    for p in props:
        vals = [v for v, _, _ in data.get(p, [])]
        if not vals:
            continue
        c = Counter(vals)
        mode, mc = c.most_common(1)[0]
        share = mc * 100 // len(vals)
        base = f"**{mode}**" if share >= 20 else f"**{mode}**（分散，无单一基准）"
        L.append(f"| {PROP_LABEL[p]} | {len(vals)} | {base} | {share}% | {len(c)} |")
    L.append("")

    L.append("## 二、离群清单（按固定格式汇报）\n")
    any_out = False
    for p in props:
        items = data.get(p, [])
        if not items:
            continue
        c = Counter(v for v, _, _ in items)
        mode, mc = c.most_common(1)[0]
        total = len(items)
        # 离群 = "长尾值"：出现 ≤2 次 或 ≤总数的 1%。
        # 理由：一个项目里存在多个合法角色档位（正文/说明/标题），"非众数"不等于"不一致"；
        # 真正可疑的是那些只出现一两次的值 —— 往往就是"A 页面用了它，其它页面没用"。
        tail = max(2, (total + 99) // 100)
        outliers = sorted([(v, n) for v, n in c.items() if v != mode and n <= tail], key=lambda x: x[1])
        if not outliers:
            continue
        any_out = True
        L.append(f"### {PROP_LABEL[p]} —— 众数 **{mode}**（{mc}/{total}）\n")
        for v, n in outliers[:max_list]:
            where = [f"`{f}:{ln}`" for val, f, ln in data["_items"].get(p, []) if val == v][:6]
            L.append(f"- 《{total} 处中 {mc} 处是 **{mode}**，这 {n} 处是 **{v}**》 → {', '.join(where)}"
                     + (f" …（共 {n} 处）" if n > 6 else ""))
        L.append("")

    if not any_out:
        L.append("**未发现离群**：硬编码字面量在各类别上完全一致（或已全部 token 化）。\n")

    L.append("## 三、跨文件分歧（同一属性在不同文件取值不同）\n")
    by_file = data.get("_byfile", {})
    for p in props:
        fmap = defaultdict(Counter)
        for f, props_map in by_file.items():
            for v, ln, _ in props_map.get(p, []):
                fmap[f][v] += 1
        if not fmap:
            continue
        global_mode = Counter(v for v, _, _ in data.get(p, [])).most_common(1)[0][0] if data.get(p) else None
        diffs = []
        for f, c in fmap.items():
            if sum(c.values()) < 3:      # 样本太少不判
                continue
            fm = c.most_common(1)[0][0]
            if fm != global_mode:
                diffs.append((f, fm, dict(c)))
        if diffs:
            L.append(f"### {PROP_LABEL[p]} —— 全局众数 {global_mode}\n")
            for f, fm, c in sorted(diffs, key=lambda x: -sum(x[2].values()))[:max_list]:
                L.append(f"- `{f}`：该文件主流 **{fm}**（分布 {c}）≠ 全局众数 **{global_mode}**")
            L.append("")

    L.append("## 四、怎么改\n")
    L.append("1. 第一节的**众数**就是本项目的事实基准 —— 先记住它。")
    L.append("2. 第二节每一条离群先问：**刻意设计 / 第三方覆盖 / 语义层级不同 / 还是真不一致？**")
    L.append("   前三种保留并在代码里注释原因；最后一种收敛到众数。")
    L.append("3. 第三节的跨文件分歧**优先修**：同一个程序里 A 页面一个尺寸、B 页面另一个尺寸，是这类问题里最该修的。")
    L.append("4. 改完重跑本脚本对比数字，结果写进提交信息。")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="前端 UI 一致性审计（众数判定）")
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--props", default=",".join(PROPS))
    ap.add_argument("--max-list", type=int, default=8)
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        print(f"目录不存在：{args.root}", file=sys.stderr)
        return 2
    props = tuple(p for p in args.props.split(",") if p in PROPS) or PROPS

    data = {p: [] for p in PROPS}
    data["_byfile"] = {}
    for dirpath, dirnames, filenames in os.walk(args.root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(SUFFIXES):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, args.root).replace("\\", "/")
            got = collect(path)
            data["_byfile"][rel] = got
            for p in PROPS:
                data[p].extend([(v, ln, s) for v, ln, s in got.get(p, [])])

    # 离群清单需要 file 信息 -> 重建带文件的列表
    file_items = defaultdict(list)
    for f, pm in data["_byfile"].items():
        for p in PROPS:
            for v, ln, s in pm.get(p, []):
                file_items[p].append((v, f, ln))
    data["_items"] = file_items

    text = report(data, args.root, props, args.max_list)
    if args.out:
        with io.open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"已写出报告：{args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
