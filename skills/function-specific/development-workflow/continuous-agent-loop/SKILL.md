---
name: continuous-agent-loop
description: Patterns for continuous autonomous agent loops — pattern selection, de-sloppify cleanup passes, RFC-driven DAG orchestration, quality gates, context persistence, and recovery controls. Runtime-neutral.
metadata:
  origin: ECC
---

# Continuous Agent Loop

Canonical loop skill. Supersedes the retired `autonomous-loops` compatibility shell.

## Loop Selection Flow

```text
Start
  |
  +-- Need strict CI/PR control? -- yes --> continuous-pr
  |
  +-- Need RFC decomposition? -- yes --> rfc-dag
  |
  +-- Need exploratory parallel generation? -- yes --> infinite
  |
  +-- default --> sequential
```

### Pattern Spectrum

From simplest to most sophisticated. Every pattern assumes the orchestrator
can start one focused agent step with a prompt, exit codes propagate, and
each step builds on the filesystem state left by the previous one.

| Pattern | Complexity | Best For |
|---------|-----------|----------|
| Sequential pipeline | Low | Daily dev steps, scripted workflows |
| Persistent session | Low | Interactive exploration that must survive restarts |
| Infinite agentic loop | Medium | Parallel content generation, spec-driven work |
| Continuous PR loop | Medium | Multi-day iterative projects with CI gates |
| De-sloppify pass | Add-on | Quality cleanup after any implementation step |
| RFC-driven DAG | High | Large features, multi-unit parallel work with merge queue |

## Sequential Pipeline

Break the work into focused non-interactive agent calls, one per step:

1. implement the feature
2. cleanup pass (see De-Sloppify)
3. verify build/lint/tests, fix failures, no new features
4. commit

Design rules:

1. **Each step is isolated** — a fresh context per step means no context bleed.
2. **Order matters** — each step builds on the previous filesystem state.
3. **Negative instructions are dangerous** — don't say "don't test X". Add a
   separate cleanup step that removes X instead.
4. **Exit codes propagate** — stop the pipeline on the first failure.

### Variations

- **Model routing**: cheap model for mechanical steps, strong model for
  research/review steps.
- **Environment context via files, not prompt length**: write priorities to a
  scratch file, have the next step read it, delete it afterwards.
- **Tool restrictions**: read-only pass for analysis, write pass for
  implementation.

## Persistent Session

A session-aware loop keeps conversation history in a local file (markdown
works), appending each turn. Use it when the work is exploratory and needs
context accumulation; use the sequential pipeline when steps must be
scriptable and CI-friendly. Session files are the database — keep them
task-focused and compact after major milestones.

| Use Case | Persistent Session | Sequential Pipeline |
|----------|--------------------|---------------------|
| Interactive exploration | Yes | No |
| Scripted automation | No | Yes |
| Session persistence | Built-in | Manual |
| Context accumulation | Grows per turn | Fresh each step |
| CI/CD integration | Poor | Excellent |

## Infinite Agentic Loop

A two-prompt system for specification-driven generation:

1. **Orchestrator prompt**: parse the spec file, scan the output dir for the
   highest iteration number, plan creative directions, deploy sub-agents.
2. **Sub-agent prompt**: each receives the full spec, a unique creative
   direction, a specific iteration number (no conflicts), and a snapshot of
   existing iterations (for uniqueness).
3. **Wave management**: deploy in batches of 3-5 until the spec is covered.

Batching strategy:

| Count | Strategy |
|-------|----------|
| 1-5 | All agents simultaneously |
| 6-20 | Batches of 5 |
| unbounded | Waves of 3-5, progressive sophistication |

Key rules:

- **Uniqueness**: every agent must see the existing output so it cannot
  duplicate it.
- **Waves, not infinity**: deploy a bounded batch, wait, assess, deploy
  again. Stop on quality, not on a counter alone.
- **Deterministic numbering**: iteration numbers are assigned by the
  orchestrator, never chosen freely.

## Continuous PR Loop

For multi-day work: each iteration implements a slice, opens/updates a PR,
waits for CI, and feeds review comments back into the next prompt. The loop
runs until the PR queue is empty and CI is green.

## RFC-Driven DAG Orchestration

For large features with parallel units:

### Decomposition

AI reads the RFC and produces work units:

```text
WorkUnit:
  id            kebab-case identifier
  name          human-readable name
  rfcSections   which RFC sections this addresses
  description   detailed description
  deps          dependency unit ids
  acceptance    concrete acceptance criteria
  tier          trivial | small | medium | large
```

Decomposition rules:

- Prefer fewer, cohesive units (minimize merge risk).
- Minimize cross-unit file overlap (avoid conflicts).
- Keep tests WITH implementation (never separate "implement X" + "test X").
- Dependencies only where real code dependency exists.

### Complexity Tiers

Different tiers get different pipeline depths:

| Tier | Pipeline Stages |
|------|----------------|
| trivial | implement → test |
| small | implement → test → code-review |
| medium | research → plan → implement → test → PRD-review + code-review → review-fix |
| large | research → plan → implement → test → PRD-review + code-review → review-fix → final-review |

### Separate Context Windows (Author-Bias Elimination)

Each stage runs in its own agent step with its own context:

| Stage | Purpose |
|-------|---------|
| Research | read codebase + RFC, produce context doc |
| Plan | design implementation steps |
| Implement | write code following the plan |
| Test | run build + test suite |
| PRD Review | spec compliance check |
| Code Review | quality + security check |
| Review Fix | address review issues |
| Final Review | quality gate (large tier only) |

**Critical design:** the reviewer never wrote the code it reviews. This
eliminates author bias — the most common source of missed issues in
self-review.

### Merge Queue with Eviction

After quality pipelines complete, units enter the merge queue:

```text
Unit branch
    |
    +- Rebase onto main
    |   +- Conflict? -> EVICT (capture conflict context)
    |
    +- Run build + tests
    |   +- Fail? -> EVICT (capture test output)
    |
    +- Pass -> fast-forward main, push, delete branch
```

File overlap intelligence:

- Non-overlapping units land speculatively in parallel.
- Overlapping units land one-by-one, rebasing each time.

Eviction recovery: when evicted, capture full context (conflicting files,
diffs, test output) and feed it back to the implementer on the next pass.

### When to Use the DAG vs Simpler Patterns

| Signal | Use DAG | Use Simpler Pattern |
|--------|---------|---------------------|
| Multiple interdependent work units | Yes | No |
| Need parallel implementation | Yes | No |
| Merge conflicts likely | Yes | No (sequential is fine) |
| Single-file change | No | Yes (sequential pipeline) |
| Multi-day project | Yes | Maybe (continuous PR loop) |
| Spec/RFC already written | Yes | Maybe |
| Quick iteration on one thing | No | Yes (session or pipeline) |

## De-Sloppify Pattern

A cleanup pass after any implementation step. The pass reviews changed files
and removes:

- unnecessary type tests (tests that only verify the language, not the code)
- overly defensive checks that guard against impossible states
- dead code left behind by refactoring
- duplicated logic that a shared helper would replace

Keep real business-logic tests. Run the test suite after cleanup.

## Choosing the Right Pattern

```text
Is the task a single focused change?
|- Yes -> Sequential Pipeline (or persistent session if exploratory)
+- No  -> Is there a written spec/RFC?
         |- Yes -> Do you need parallel implementation?
         |        |- Yes -> RFC-driven DAG
         |        +- No  -> Continuous PR loop
         +- No  -> Do you need many variations of the same thing?
                  |- Yes -> Infinite Agentic Loop
                  +- No  -> Sequential Pipeline with de-sloppify
```

Combining patterns:

1. **Sequential Pipeline + De-Sloppify** — the most common combination.
2. **Continuous PR Loop + De-Sloppify** — add a cleanup directive to each
   iteration's review prompt.
3. **Any loop + verification gate** — use `verification-loop` before commits.
4. **Tiered model routing in simpler loops** — cheap model for mechanical
   steps, strong model for architectural ones.

## Failure Modes

- loop churn without measurable progress
- repeated retries with same root cause
- merge queue stalls
- cost drift from unbounded escalation

## Recovery

- freeze the loop
- audit the harness state (workspace, branches, sessions) before resuming
- reduce scope to the failing unit
- replay with explicit acceptance criteria

## Anti-Patterns

1. **Infinite loops without exit conditions** — always have a max-runs,
   max-cost, max-duration, or completion signal.
2. **No context bridge between iterations** — use filesystem state or session
   files to bridge context.
3. **Retrying the same failure** — capture the error context and feed it to
   the next attempt instead of blind retries.
4. **Negative instructions instead of cleanup passes** — don't say "don't do
   X". Add a separate pass that removes X.
5. **All agents in one context window** — separate concerns; the reviewer
   should never be the author.
6. **Ignoring file overlap in parallel work** — if two parallel units might
   edit the same file, you need a merge strategy (sequential landing,
   rebase, or conflict resolution).