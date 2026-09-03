---
name: find-skills
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.
---

# Find Skills

This skill helps you discover and install skills from the open agent skills ecosystem.

## When to Use This Skill

Use this skill when the user:

- Asks "how do I do X" where X might be a common task with an existing skill
- Says "find a skill for X" or "is there a skill for X"
- Asks "can you do X" where X is a specialized capability
- Expresses interest in extending agent capabilities
- Wants to search for tools, templates, or workflows
- Mentions they wish they had help with a specific domain (design, testing, deployment, etc.)

## What is the Skills CLI?

The Skills CLI (`npx skills`) is the package manager for the open agent skills ecosystem. Skills are modular packages that extend agent capabilities with specialized knowledge, workflows, and tools.

**Key commands:**

- `npx skills find [query] [--owner <owner>]` - Search for skills interactively or by keyword
- `npx skills add <package>` - Install a skill from GitHub or other sources
- `npx skills update` - Update all installed skills

**Browse skills at:** https://skills.sh/

## How to Help Users Find Skills

### Step 1: Understand What They Need

When a user asks for help with something, identify:
1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Whether this is a common enough task that a skill likely exists

### Step 2: Check the Leaderboard First

Before running a CLI search, check the [skills.sh leaderboard](https://skills.sh/) to see if a well-known skill already exists for the domain.

### Step 3: Search for Skills

```bash
npx skills find [query] [--owner <owner>]
```

Examples:
- `npx skills find react performance`
- `npx skills find pr review`
- `npx skills find changelog`

### Step 4: Verify Quality Before Recommending

1. **Install count** — Prefer skills with 1K+ installs
2. **Source reputation** — Official sources (`vercel-labs`, `anthropics`, `microsoft`) are more trustworthy
3. **GitHub stars** — Check the source repository

### Step 5: Present Options to the User

Share the skill name, description, install count, and the install command.

### Step 6: Offer to Install

```bash
npx skills add <owner/repo@skill> -g -y
```

## Common Skill Categories

| Category | Example Queries |
|----------|----------------|
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing | testing, jest, playwright, e2e |
| DevOps | deploy, docker, kubernetes, ci-cd |
| Documentation | docs, readme, changelog, api-docs |
| Code Quality | review, lint, refactor, best-practices |
| Design | ui, ux, design-system, accessibility |
| Productivity | workflow, automation, git |

## Local Skill Discovery

Before falling back to external sources, check the locally installed skill set.

### Search local skills by keyword/trigger
```bash
# list all installed skill names (triggers included)
ls -R ~/.config/opencode/skills/ | grep SKILL.md

# keyword scan for relevant skills
grep -rl "triggers:" ~/.config/opencode/skills/*/SKILL.md
# example keyword lookup
rg -il "z-index|overflow|portal|clipping" ~/.config/opencode/skills/
```

### Common local mappings
| Problem phrase | Local skill to invoke |
|---|---|
| z-index / stacking-context conflict | `/layout-guardrails` |
| dropdown/menu bleed outside parent | `/layout-guardrails` |
| portal / teleport clipped by parent | `/layout-guardrails` |
| CSS / layout pixel polish | `make-interfaces-feel-better` |
| frontend design / aesthetic direction | `frontend-design` |
| need a reusable design system | `create-design-system` |
| K8s / DevOps ops questions | `k8s-knowledge` |

> Tip: local skills take priority over external lookups when no extra installation is required.

If no relevant skills exist, acknowledge the result and offer to help directly or suggest creating a skill with `npx skills init`.
