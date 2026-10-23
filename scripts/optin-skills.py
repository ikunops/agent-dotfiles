# -*- coding: utf-8 -*-
"""
Selective opt-in: re-enable implicit skill invocation for the high-frequency
library skills only.

Context
-------
209 of 285 skills carry `agents/openai.yaml` with
`policy.allow_implicit_invocation: false`, which keeps them out of the always-on
index (measured: saves ~77% index tokens). The trade-off is real -- but it
assumed the model would reliably route through `find-skills`, and in practice
sessions often don't. So a small, high-frequency subset goes back to implicit.

Rule of thumb for the list: skills a session should reach for WITHOUT being told,
because the task shape itself is a strong signal (write UI, verify UI, debug,
investigate). Specialised domain skills stay off and remain find-skills-only.
"""
import io
import os
from pathlib import Path

ROOT = Path(r"C:\Users\31807\opencode-dotfiles\skills")

# --- the list -------------------------------------------------------------
# group by why it's here, so the intent survives future edits
SELECT = {
    "frontend": [
        "layout-guardrails",            # z-index / stacking / overflow clip
        "make-interfaces-feel-better",  # the "why does this feel cheap" pass
        "design-taste-frontend",        # anti-AI-slop taste rules
        "frontend-patterns",
        "frontend-a11y",
        "frontend-design-direction",
        "interaction-design",
        "design-system",
        "claude-design",
        "hallmark",                     # design critique
        "impeccable",
        "frontend-slides",
    ],
    "workflow": [
        "blueprint",
        "plan-canvas",
        "plan-orchestrate",
        "verification-loop",
        "search-first",
        "iterative-retrieval",
    ],
    "testing": [
        "e2e-testing",
        "test-driven-development",
    ],
    "code-quality": [
        "requesting-code-review",
        "receiving-code-review",
        "sql-review",
        "api-design",
    ],
    "debug": [
        "systematic-debugging",
        "brainstorming",
        "agent-introspection-debugging",
    ],
    "security": [
        "security-review",
    ],
}

# names that may not exist -- resolved against disk, reported either way
WANT = []
for group in SELECT.values():
    WANT.extend(group)

MODE = os.environ.get("PF_MODE", "apply")  # "apply" | "dry"


def set_implicit(yaml_path: Path, allow: bool) -> bool:
    """Flip allow_implicit_invocation. Returns True if the file changed."""
    s = io.open(yaml_path, encoding="utf-8").read()
    val = "true" if allow else "false"
    if "allow_implicit_invocation:" in s:
        out = []
        for line in s.split("\n"):
            if line.strip().startswith("allow_implicit_invocation:"):
                indent = line[: len(line) - len(line.lstrip())]
                out.append("%sallow_implicit_invocation: %s" % (indent, val))
            else:
                out.append(line)
        new = "\n".join(out)
    else:
        if not s.endswith("\n"):
            s += "\n"
        new = s + "policy:\n  allow_implicit_invocation: %s\n" % val
    if new != s:
        if MODE == "apply":
            io.open(yaml_path, "w", encoding="utf-8", newline="\n").write(new)
        return True
    return False


def main():
    # index every skill that has an openai.yaml
    found = {}
    for dp, dn, fn in os.walk(ROOT):
        if "SKILL.md" not in fn:
            continue
        y = Path(dp) / "agents" / "openai.yaml"
        if y.is_file():
            found[Path(dp).name] = y

    missing = [w for w in WANT if w not in found]
    hit = [w for w in WANT if w in found]

    print("mode:", MODE)
    print("wanted: %d   found: %d   missing: %d" % (len(WANT), len(hit), len(missing)))
    if missing:
        print("  missing (skipped):", ", ".join(missing))
    print()

    changed = 0
    already = 0
    for name in sorted(set(hit)):
        y = found[name]
        s = io.open(y, encoding="utf-8").read()
        if "allow_implicit_invocation: true" in s:
            already += 1
            continue
        did = set_implicit(y, True)
        if did:
            changed += 1
            print("  ON  %-32s %s" % (name, y.relative_to(ROOT)))

    print()
    print("changed: %d   already on: %d" % (changed, already))


if __name__ == "__main__":
    main()
