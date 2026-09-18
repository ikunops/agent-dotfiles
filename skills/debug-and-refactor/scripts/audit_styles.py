#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端样式体质审计 —— 找出「引用了不存在的 CSS 变量」与「无样式兜底的裸控件」

用法:
    python audit_styles.py --root <项目前端源码目录> [--css-var-prefix SKIP1,SKIP2]

示例:
    python audit_styles.py --root C:/proj/web/src
    python audit_styles.py --root ./src --exclude node_modules,dist,build

输出两部分（可靠性不同，见 SKILL.md）:
    A. 未定义 CSS 变量   —— 高可靠，可直接采信（变量名精确匹配）
    B. 无兜底裸控件       —— 低可靠，**必须人工核实**（行扫描判不准 DOM 层级）
"""
import argparse
import collections
import os
import re
import sys

# 运行时注入的变量（不是"未定义"，是框架在运行时写入的）——按需扩充
RUNTIME_VARS_DEFAULT = {
    "--spacing",                                  # Tailwind v4
    "--radix-dropdown-menu-content-available-height",
    "--radix-select-trigger-height",
    "--radix-select-trigger-width",
    "--radix-popper-anchor-width",
    "--radix-popper-available-width",
    "--radix-popper-available-height",
    "--radix-popper-transform-origin",
}
# Tailwind v4 @theme 生成的 --color-* 也算运行时
RUNTIME_PREFIXES = ("--radix-", "--tw-", "--color-")

SKIP_TYPES = ("checkbox", "radio", "hidden", "file", "range", "submit", "button", "color", "date")


def walk(root, excludes):
    css, src = [], []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in excludes]
        for fn in fns:
            p = os.path.join(dp, fn)
            if fn.endswith(".css"):
                css.append(p)
            elif fn.endswith((".tsx", ".ts", ".jsx", ".js", ".vue", ".svelte")):
                src.append(p)
    return css, src


def check_undefined_vars(css_files, src_files, root, runtime_vars):
    defined = set()
    for p in css_files:
        for line in open(p, encoding="utf-8", errors="replace"):
            for m in re.finditer(r"(--[a-zA-Z0-9_-]+)\s*:", line):
                defined.add(m.group(1))

    used = collections.defaultdict(list)
    for p in css_files + src_files:
        for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
            for m in re.finditer(r"var\((--[a-zA-Z0-9_-]+)", line):
                used[m.group(1)].append((os.path.relpath(p, root).replace("\\", "/"), i))

    problems = {}
    for v, locs in used.items():
        if v in defined or v in runtime_vars or v.startswith(RUNTIME_PREFIXES):
            continue
        # 有 fallback 的危害小（标注出来区分）
        with_fb, no_fb = [], []
        for f, ln in locs:
            try:
                txt = open(os.path.join(root, f.replace("/", os.sep)), encoding="utf-8",
                           errors="replace").read().split("\n")[ln - 1]
            except Exception:
                txt = ""
            m = re.search(re.escape("var(%s" % v) + r"\s*,", txt)
            (with_fb if m else no_fb).append((f, ln, txt.strip()[:100]))
        problems[v] = (no_fb, with_fb)
    return problems, defined, used


def container_selectors(css_files):
    rules = set()
    for p in css_files:
        txt = open(p, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"([.#][a-zA-Z0-9_.\-\[\]=\"']+)\s+(?:input|select|textarea)\b", txt):
            rules.add(m.group(1).lstrip(".#"))
    return rules


def find_bare_controls(src_files, root, rules):
    """返回疑似裸控件。⚠️ 结果不可靠：行扫描无法判断真实 DOM 层级，必须人工核实。"""
    cands = []
    for p in src_files:
        rel = os.path.relpath(p, root).replace("\\", "/")
        lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
        for i, line in enumerate(lines, 1):
            m = re.search(r"<(input|select|textarea)\b([^>]*)", line)
            if not m:
                continue
            tag = m.group(1)
            # 拼接到标签结束。注意不能用 `">" not in joined` 判断：
            # 箭头函数 onChange={(e) => ...} 里的 `>` 会让拼接提前中断，漏掉后面的 style=。
            # 因此只在遇到真正的标签闭合 `/>` 或 `[^=]>` 时停止。
            joined, j = line, i
            while j < len(lines):
                if re.search(r"/>\s*$", joined) or re.search(r"[^=]>", joined):
                    break
                joined += " " + lines[j]
                j += 1
            if "className" in joined or "class=" in joined:
                continue
            if tag == "input":
                tm = re.search(r'type="([a-z]+)"', joined)
                if tm and tm.group(1) in SKIP_TYPES:
                    continue
            # 注意：这只是"最近的一个 className"，可能是兄弟元素而非祖先！
            anc = ""
            for k in range(i - 1, max(0, i - 26), -1):
                am = re.search(r'className="([^"]+)"', lines[k - 1])
                if am:
                    anc = am.group(1)
                    break
            inline = "style=" in joined
            aria = re.search(r'aria-label="([^"]*)"', joined)
            ph = re.search(r'placeholder="([^"]*)"', joined)
            cands.append((rel, i, tag, (aria.group(1) if aria else "") or (ph.group(1) if ph else ""),
                          anc, inline))
    return cands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="前端源码根目录")
    ap.add_argument("--exclude", default="node_modules,dist,build,.git,out",
                    help="逗号分隔的排除目录")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    excludes = tuple(x.strip() for x in args.exclude.split(",") if x.strip())
    css_files, src_files = walk(root, excludes)

    print("=" * 78)
    print("前端样式体质审计   根目录: %s" % root)
    print("CSS %d 个 | 源码 %d 个" % (len(css_files), len(src_files)))
    print("=" * 78)

    problems, defined, used = check_undefined_vars(css_files, src_files, root, RUNTIME_VARS_DEFAULT)

    no_fb_all = {v: p[0] for v, p in problems.items() if p[0]}
    with_fb_all = {v: p[1] for v, p in problems.items() if p[1]}

    print()
    print("【A1】未定义变量 · 无 fallback（会直接失效，优先修）  %d 个" % len(no_fb_all))
    print("-" * 78)
    if not no_fb_all:
        print("  ✅ 无")
    for v in sorted(no_fb_all):
        print("\n  %s" % v)
        for f, ln, txt in no_fb_all[v][:6]:
            print("      %s:%d   %s" % (f, ln, txt[:88]))

    print()
    print("【A2】未定义变量 · 有 fallback（不会坏，但硬编码色可能不贴合主题）  %d 个" % len(with_fb_all))
    print("-" * 78)
    if not with_fb_all:
        print("  ✅ 无")
    for v in sorted(with_fb_all):
        locs = with_fb_all[v]
        print("  %-22s %d 处   e.g. %s:%d" % (v, len(locs), locs[0][0], locs[0][1]))

    rules = container_selectors(css_files)
    print()
    print("【B1】CSS 中能给表单控件套样式的后代选择器（兜底来源）  共 %d 个" % len(rules))
    print("-" * 78)
    for r in sorted(rules):
        print("      .%s input/select/textarea" % r)

    print()
    print("【B2】⚠️ 疑似无兜底裸控件（候选，必须人工核实！）")
    print("-" * 78)
    print("  行扫描无法判断真实 DOM 层级：脚本取到的是「最近的 className」，")
    print("  很可能是兄弟元素而不是祖先容器。请逐个打开源码确认。")
    cands = find_bare_controls(src_files, root, rules)
    # 三分类，逐级减少人工核实量：
    #   1) 自带内联 style      → 通常不是问题
    #   2) 最近 class 命中兜底清单 → 很可能有兜底（仍建议扫一眼）
    #   3) 两者都不是            → 真正需要核实
    inline_ok = [c for c in cands if c[5]]
    def _guarded(c):
        return any(a in rules for a in c[4].split())
    guarded = [c for c in cands if not c[5] and _guarded(c)]
    risky = [c for c in cands if not c[5] and not _guarded(c)]

    if not cands:
        print("  ✅ 无候选")
    if guarded:
        print("      ── 疑似已兜底（最近 class 命中 【B1】清单，建议扫一眼确认）%d 个 ──" % len(guarded))
        for rel, ln, tag, desc, anc, _ in guarded:
            print("      %-40s %-5d <%-8s> %-18s class: %s" % (rel, ln, tag, desc[:18], anc or "(无)"))
    if risky:
        print("\n      ── ⚠️ 需重点核实（既无内联样式、最近 class 也不在兜底清单）%d 个 ──" % len(risky))
        for rel, ln, tag, desc, anc, _ in risky:
            print("      %-40s %-5d <%-8s> %-18s class: %s" % (rel, ln, tag, desc[:18], anc or "(无)"))
    if inline_ok:
        print("\n      ── 自带内联样式（通常不是问题）%d 个 ──" % len(inline_ok))
        for rel, ln, tag, desc, anc, _ in inline_ok[:10]:
            print("      %-40s %-5d <%-8s> %s" % (rel, ln, tag, desc[:24]))

    print()
    print("=" * 78)
    print("汇总")
    print("=" * 78)
    print("  未定义变量: 无fallback %d 个 / 有fallback %d 个" % (len(no_fb_all), len(with_fb_all)))
    print("  裸控件候选: %d 个（待人工核实；其中自带内联样式 %d 个）" % (len(cands), len(inline_ok)))
    print("  定义的变量: %d   被引用的变量: %d" % (len(defined), len(used)))


if __name__ == "__main__":
    main()
