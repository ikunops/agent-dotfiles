# -*- coding: utf-8 -*-
"""Validate the global Windows/PowerShell execution rules in AGENTS.md.

This is intentionally dependency-free so it can run on a fresh Windows machine.
It checks that the rule section exists, keeps the key hard constraints, and that
AGENTS.md stays UTF-8 without BOM and LF-only.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "AGENTS.md"
SECTION = "## Shell 执行规则（Windows / PowerShell 优先）"
NEXT = "## 安全红线"

REQUIRED = {
    "shell section": SECTION,
    "PowerShell 7": "pwsh",
    "Windows PowerShell 5.1": "Windows PowerShell 5.1",
    "literal paths": "-LiteralPath",
    "exit codes": "$LASTEXITCODE",
    "UTF-8": "UTF-8",
    "checkpoint": "🔴 CHECKPOINT",
    "recovery order": "失败后的固定恢复顺序",
    "cross-shell ban": "同一个命令块只允许一种主 shell",
    "outer quote": "跨 PowerShell 进程传命令时，外层命令用单引号包裹",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agents", type=Path, default=AGENTS, help="Path to AGENTS.md")
    agents = parser.parse_args().agents.resolve()
    data = agents.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        fail("AGENTS.md has a UTF-8 BOM")
    if b"\r\n" in data:
        fail("AGENTS.md contains CRLF; keep it LF-only")

    text = data.decode("utf-8")
    if SECTION not in text:
        fail("shell execution section is missing")
    start = text.index(SECTION)
    end = text.find(NEXT, start)
    if end < 0:
        fail("security section anchor is missing")
    section = text[start:end]

    for label, needle in REQUIRED.items():
        if needle not in section:
            fail(f"missing rule: {label}")

    print(f"OK: {agents} shell rules present and encoding valid")
    print(f"OK: {len(section.splitlines())} lines in shell rule section")


if __name__ == "__main__":
    main()
