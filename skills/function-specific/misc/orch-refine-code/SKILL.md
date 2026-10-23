---
name: orch-refine-code
description: >
  行为保持型重构（orch-refine-code）。用于结构需要改善但外部行为必须完全不变的情况，例如拆分模块、消除重复、删除死代码、降低嵌套层级或为提升可读性重命名。执行前先确认相关测试通过，再小步重构并持续保持测试为绿，最后审查并在人工确认后提交。
  触发词：行为保持型重构、代码重构、拆分模块、消除重复、删除死代码、降低嵌套、refactor、refine code、behavior-preserving refactor。
metadata:
  origin: ECC
---

# orch-refine-code

Actor · action · target: **orch · refine · code**. Thin wrapper over the shared
engine in [`orch-pipeline`](../orch-pipeline/SKILL.md).

## When to Use

- Same behavior, **better structure**: extract modules, remove duplication, kill
  dead code, reduce nesting, rename for clarity.
- Distinguish from siblings: if behavior is meant to change at all, this is the
  wrong skill (`orch-change-feature` / `orch-fix-defect`).

## Operation settings

- **Default size floor:** standard — restructures touch multiple files.
- **Phase mask:** 0 → 2 (plan the restructure) → 4 (keep green) → 5 → 6. No new
  behavior tests are written — the existing suite is the safety net.
- **First move (phase 4):** confirm the relevant tests exist and are **green
  before** touching code; if coverage is thin, add characterization tests first.
  Then restructure in small steps, re-running tests after each.

## How It Works

1. Run the `orch-pipeline` engine with the settings above.
2. For dead-code / duplication sweeps, delegate to the `refactor-cleaner` agent
   (it runs knip / depcheck / ts-prune and removes safely).
3. Stop at **Gate 1** (restructure plan) and **Gate 2** (pre-commit).
4. Commit as `refactor:` — the diff must be behavior-neutral.

## Example

```
orch-refine-code: extract the NWS HTTP client out of poller.py
→ confirm tests green → plan extraction  [GATE 1: approve]
→ move in small steps, tests green throughout → code-review
→ commit refactor:  [GATE 2: confirm]
```
