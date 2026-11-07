---
name: blueprint
description: >-
  Turn a one-line objective into a step-by-step construction plan for
  multi-session, multi-agent engineering projects. Each step has a
  self-contained context brief so a fresh agent can execute it cold.
  Includes adversarial review gate, dependency graph, parallel step
  detection, anti-pattern catalog, and plan mutation protocol.
  TRIGGER when: user requests a plan, blueprint, or roadmap for a
  complex multi-PR task, or describes work that needs multiple sessions.
  DO NOT TRIGGER when: task is completable in a single PR or fewer
  than 3 tool calls, or user says "just do it".
metadata:
  origin: community
---

# Blueprint — Construction Plan Generator

Turn a one-line objective into a step-by-step construction plan that any coding agent can execute cold.

## When to Use

- Breaking a large feature into multiple PRs with clear dependency order
- Planning a refactor or migration that spans multiple sessions
- Coordinating parallel workstreams across sub-agents
- Any task where context loss between sessions would cause rework

**Do not use** for tasks completable in a single PR, fewer than 3 tool calls, or when the user says "just do it."

## How It Works

Blueprint runs a 5-phase pipeline:

1. **Research** — Pre-flight checks (git, gh auth, remote, default branch), then reads project structure, existing plans, and memory files to gather context.
2. **Design** — Breaks the objective into one-PR-sized steps (3–12 typical). Assigns dependency edges, parallel/serial ordering, model tier (strongest vs default), and rollback strategy per step.
3. **Draft** — Writes a self-contained Markdown plan file to `plans/`. Every step includes a context brief, task list, verification commands, and exit criteria — so a fresh agent can execute any step without reading prior steps.
4. **Review** — Delegates adversarial review to a strongest-model sub-agent (e.g., Opus) against a checklist and anti-pattern catalog. Fixes all critical findings before finalizing.
5. **Register** — Saves the plan, updates memory index, and presents the step count and parallelism summary to the user.

Blueprint detects git/gh availability automatically. With git + GitHub CLI, it generates full branch/PR/CI workflow plans. Without them, it switches to direct mode (edit-in-place, no branches).

## Runtime Contract (settle it in Design, not in CI)

A plan that only works on the author's machine is not a plan. Any blueprint that touches a runtime, a build, or a deployment must settle the **runtime contract** before the first implementation step. This is a design input, not a delivery checklist.

### Three judgements

**1. Reproducible build vs. accidentally working build.**

"Works locally" proves nothing. The only evidence of portability is a build from a clean clone in a clean environment. Every plan must be able to say which of these is true: the build is reproducible from a clean clone, or the build depends on untracked local files and that dependency is written down as a known gap.

The failure mode to design against is a file that exists in the working tree but was never committed - a `go:embed` target swallowed by `.gitignore`, a template, a migration, a generated asset. Locally everything compiles; any fresh checkout fails. If a step introduces a resource the build consumes, that step must also state how the resource is tracked.

**2. Hardcoding is three different things, not one.**

Do not write a blanket rule like "never hardcode". Classify each fixed value and handle it by class:

| Class | Test | Handling |
|---|---|---|
| Protocol constant / product constraint | Defined by an external protocol or product decision; identical on every machine | Keep it, but collapse it into one named constant with the source cited |
| Environment / instance value | Host, port, path, account, tenant, model name - varies by deployment | Externalize to config or environment, with a documented default |
| Machine capability | Screen size, CPU count, memory, DPI | Probe at runtime, clamp to a safe range, keep a fallback |
| One-off static content | A single fixed string that never varies | Leave it literal; abstraction here is over-engineering |

The most-missed class is **machine capability**. It looks like a configuration problem but is not: users will not configure their own screen resolution. The correct shape is `probe -> clamp -> fallback`, not "add another config key".

**3. Distance from the deployment boundary decides severity.**

The same hardcoded value is harmless in a test and an incident in a default config. When judging a fixed value, ask how close it sits to the boundary where the code leaves the author's machine. The closer to that boundary, the higher the priority - and the earlier in the plan it must be addressed.

### What every affected step must state

For any step that introduces a runtime dependency, a build artifact, or a deployable configuration, the step's context brief must include:

- **Runtime**: language/toolchain version and where it is declared (`go.mod`, `engines`, `python_requires`, `.nvmrc`, `.tool-versions`)
- **Target**: OS, architecture, and ABI assumptions (glibc vs musl, amd64 vs arm64)
- **Inputs**: every file the build reads, and confirmation that it is tracked
- **Configuration**: which values are externalized, which are constants, which are probed
- **Failure mode**: what happens when a prerequisite is missing - an explicit error, never a silent fallback to a plausible default

A step that cannot fill these in is not ready to be planned.

### Anti-patterns

- Planning a feature without naming the runtime version it targets.
- Adding a build input without checking whether it is tracked.
- Treating a machine capability as a user-configurable setting.
- Discovering the portability contract for the first time in CI.
- Writing "works on my machine" into the exit criteria.

## Verification Contract (what the checker can see is decided here)

An acceptance skill can only assert against what the implementation exposed. Techniques like "open every modal and check overlap" or "assert an observable state change" are not a substitute for building the hook - they work around its absence. Settle the verification contract in Design, alongside the runtime contract.

### The gate: three dimensions, not one

"Can this be detected afterwards?" is only one of the questions, and on its own it gives the wrong answer. Detectability is a *capability*, not a guarantee that anyone will run the check. Two independent dimensions decide where the work belongs:

| Dimension | Question | What it decides |
|---|---|---|
| **Verifiability** | If nobody handles this while coding, can it still be discovered reliably later? | Whether a hook must be built now, or a check can be added afterwards |
| **Rework cost** | If this turns out wrong mid-flight, how much has to be undone? | Whether it is worth pinning down up front |
| **Determinacy** | Is there one correct answer, or does it need exploration? | Whether to fix it now or leave it open |

Combined:

- **Uncertain + high rework** -> settle the contract before building. Guessing here means redoing whole steps.
- **Certain + high rework** -> decide it up front; it is cheap to state and expensive to retrofit.
- **Uncertain + low rework** -> decide while building; exploring is the cheapest way to find out.
- **Certain + low rework** -> do not pre-design it, **but it must still enter the verification list**. Skipping the design work is fine; skipping the check is not.

The critical correction: **"detectable later" means "can move to the acceptance list", never "can be dropped".** What gets saved is the up-front design effort, not the inspection.

Two consequences that follow:

- Anything moved to acceptance must be **written into the verification list with its check method**. An unlisted check is a check that will be skipped.
- Low rework cost is not a licence to ignore a problem - it only means the ordering can be later. Small inconsistencies found mid-flight are exactly the ones that cause repeated trial-and-error; if a small decision is cheap to fix *now* and repeatedly annoying *later*, pin it down now.

The tell-tale sign of an under-specified design: the checking step has to *invent* something - a selector, a way to trigger a surface, a guess at how many dialogs exist.

### What every affected step must specify

1. **Observable states.** For each interaction, name the state a checker can read to prove it worked: a data attribute, a class, a rendered node, a request issued, a value changed. "No console error" is not a state. An interaction with no observable consequence is a design defect, not a testing inconvenience.

2. **Stable selectors.** Anything that must be driven or measured gets a purpose-built hook (`data-testid` / `data-role`), independent of styling classes and of DOM position. A selector that relies on sibling-vs-child nesting is a trap the checker falls into later.

3. **Surface inventory.** Enumerate every independently observable surface the feature touches: route/page, modal, drawer, dropdown, popover, plus empty / loading / error / permission states. Each is its own implementation and verification unit. A page-level pass does not cover the inside of a dialog, and "tested the main view" does not mean the feature is done.

4. **Teardown for anything long-lived.** Every timer, subscription, listener, socket, or observer created by the step names where it gets cancelled. Unspecified async lifetime is what later shows up as "the process never exits", "the port is still held", and duplicated execution after remount.

5. **How to reach each surface.** A surface that needs an unusual path to appear (edge state, permission, error branch) records that path in the step. Otherwise the checker has to reverse-engineer it, and usually skips it.

### Anti-patterns

- Deferring "how will this be verified" to the acceptance phase, then finding there is nothing to assert against.
- Letting the checker invent selectors, trigger paths, or surface counts.
- Treating a modal or an error state as a detail of the main view instead of its own unit.
- Starting a repeating timer with no owner that stops it.
- Reporting coverage as "pages tested" when the inventory was dialogs.
## Examples

### Basic usage

```
/blueprint myapp "migrate database to PostgreSQL"
```

Produces `plans/myapp-migrate-database-to-postgresql.md` with steps like:
- Step 1: Add PostgreSQL driver and connection config
- Step 2: Create migration scripts for each table
- Step 3: Update repository layer to use new driver
- Step 4: Add integration tests against PostgreSQL
- Step 5: Remove old database code and config

### Multi-agent project

```
/blueprint chatbot "extract LLM providers into a plugin system"
```

Produces a plan with parallel steps where possible (e.g., "implement Anthropic plugin" and "implement OpenAI plugin" run in parallel after the plugin interface step is done), model tier assignments (strongest for the interface design step, default for implementation), and invariants verified after every step (e.g., "all existing tests pass", "no provider imports in core").

## Key Features

- **Cold-start execution** — Every step includes a self-contained context brief. No prior context needed.
- **Adversarial review gate** — Every plan is reviewed by a strongest-model sub-agent against a checklist covering completeness, dependency correctness, and anti-pattern detection.
- **Branch/PR/CI workflow** — Built into every step. Degrades gracefully to direct mode when git/gh is absent.
- **Parallel step detection** — Dependency graph identifies steps with no shared files or output dependencies.
- **Plan mutation protocol** — Steps can be split, inserted, skipped, reordered, or abandoned with formal protocols and audit trail.
- **Zero runtime risk** — Pure Markdown skill. The entire repository contains only `.md` files — no hooks, no shell scripts, no executable code, no `package.json`, no build step. Nothing runs on install or invocation beyond Claude Code's native Markdown skill loader.

## Installation

This skill ships with Everything Claude Code. No separate installation is needed when ECC is installed.

### Full ECC install

If you are working from the ECC repository checkout, verify the skill is present with:

```bash
test -f skills/blueprint/SKILL.md
```

To update later, review the ECC diff before updating:

```bash
cd /path/to/everything-claude-code
git fetch origin main
git log --oneline HEAD..origin/main       # review new commits before updating
git checkout <reviewed-full-sha>          # pin to a specific reviewed commit
```

### Vendored standalone install

If you are vendoring only this skill outside the full ECC install, copy the reviewed file from the ECC repository into `~/.claude/skills/blueprint/SKILL.md`. Vendored copies do not have a git remote, so update them by re-copying the file from a reviewed ECC commit rather than running `git pull`.

## Requirements

- Claude Code (for `/blueprint` slash command)
- Git + GitHub CLI (optional — enables full branch/PR/CI workflow; Blueprint detects absence and auto-switches to direct mode)

## Source

Inspired by antbotlab/blueprint — upstream project and reference design.
