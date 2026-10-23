---
name: using-superpowers
description: Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, ignore this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## The Rule

**Invoke relevant or requested skills BEFORE any response or action** — including clarifying questions, exploring the codebase, or checking files. If it turns out wrong for the situation, you don't have to use it.

**Before entering plan mode:** if you haven't already brainstormed, invoke the brainstorming skill first.

Then announce "Using [skill] to [purpose]" and follow the skill exactly. If it has a checklist, create a todo per item.

## When the skill you need is not in the visible list

Only part of the library is advertised to you. Roughly 180 skills are deliberately
kept out of the always-on index to save context (`allow_implicit_invocation: false`).
They are still installed and still usable — you simply cannot see them until you ask.

So "I don't see a skill for this" is **not** evidence that none exists. It means you
have to go look:

1. Invoke the `find-skills` skill. It carries a full routing table over every skill
   in the library, including the hidden ones, and tells you which to load.
2. If `find-skills` isn't reachable either, read the small `skills/INDEX.md` root,
   then enter the relevant page under `skills/indexes/` before opening a leaf.
3. Only after both come up empty should you solve it from scratch.

**Do this before writing a plan, not after.** Discovering halfway through that a
skill already covers the problem means throwing the plan away.

Signals that you should go look, even though nothing in the visible list matched:

| You are about to… | Look for |
|---|---|
| design a UI, or fix one that "feels cheap" | `design-taste-frontend`, `make-interfaces-feel-better`, `layout-guardrails` |
| verify a UI change actually works | `ui-acceptance`, `verification-loop`, `e2e-testing` |
| debug something that "didn't take effect" | `systematic-debugging`, `debug-and-refactor` |
| review code you or someone else just wrote | `requesting-code-review`, `receiving-code-review` |
| handle SQL, schema, migrations | `sql-review`, and the database category |
| build anything visual from scratch — animation, diagram, chart, video | `code-motion-film`, `photon-flow-viz`, `archify` |
| work in a stack you rarely touch (React, Vue, FastAPI, Vite…) | `framework-specific/*` |

## Skill Priority

When multiple skills apply, process skills come first — they set the approach, then implementation skills (frontend-design, etc.) carry it out. Brainstorming and systematic-debugging are Superpowers' most common process skills, but the rule holds for any of them.

- "Let's build X" → superpowers:brainstorming first, then implementation skills.
- "Fix this bug" → superpowers:systematic-debugging first, then domain skills.

## Red Flags

These thoughts mean STOP—you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "Let me gather information first" | Skills tell you HOW to gather information. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |
| "I know what that means" | Knowing the concept ≠ using the skill. Invoke it. |

## Platform Adaptation

If your harness appears here, read its reference file for special instructions:

- Codex: `references/codex-tools.md`
- Pi: `references/pi-tools.md`
- Antigravity: `references/antigravity-tools.md`

## User Instructions

User instructions (CLAUDE.md, AGENTS.md, GEMINI.md, etc, direct requests) take precedence over skills, which in turn override default behavior. Only skip skill workflows or instructions when your human partner has explicitly told you to.
