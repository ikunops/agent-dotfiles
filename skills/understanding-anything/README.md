# understanding-anything

A skill for AI agents that turns "explain this to me" into actual understanding.

## The problem with most explanations

Ask an AI to explain quantum mechanics, how markets work, or why empires collapse — and you get a well-written summary. You read it, nod, and forget it within a week. That's not understanding. That's just information with good formatting.

Real understanding is different. It's being able to break something down to its core, predict how it behaves, connect it to things you already know, and explain it back in plain language. That takes a different kind of conversation.

## What this skill does

It turns the agent into a thinking coach rather than a textbook.

Instead of explaining *at* you, it walks *with* you — asking the questions that force your model of the topic to actually form. It uses proven thinking frameworks: First Principles, Decomposition, Inversion, the Feynman Technique, Systems Thinking, Socratic Questioning, Mental Model Latticework, and more.

The experience feels like talking to someone who genuinely knows how to think about hard things — not like being processed through a methodology.

Works on any topic. Concepts, systems, decisions, phenomena, problems. Anything.

## Install

```bash
git clone https://github.com/rohitpatill/understanding-anything
```

Then drop the `understanding-anything` folder into wherever your agent loads skills from. That's it.

## How it works in practice

You bring a topic. The agent reads where you are — whether you're starting from scratch, stuck on something specific, confident but untested, or just want it to stick — and meets you there.

A session might look like:

> **You:** Help me actually understand how inflation works — I keep reading about it but it never clicks.
>
> **Agent:** What do you think is happening when prices go up? Just your instinct, doesn't have to be right.
>
> **You:** More money around, so things cost more?
>
> **Agent:** Close — so what's the ratio that's actually changing? If you doubled the number of dollars *and* doubled the number of goods at the same time, what happens to prices?

That's the style. Short questions. Your thinking in the driver's seat. The agent pushing you to go one level deeper each time.

## What's inside

```
understanding-anything/
├── SKILL.md                        # Core skill — routing logic and session rules
└── references/
    ├── 01-foundations.md           # First Principles, Decomposition, Pareto, Structural Mapping, Levels of Abstraction
    ├── 02-pattern-recognition.md   # Analogical Reasoning, Systems Archetypes, Reference Class, Signal vs Noise
    ├── 03-framing-questioning.md   # Inversion, 5 Whys, Socratic Questioning, Reframing, Challenging Assumptions
    ├── 04-synthesis.md             # Mental Model Latticework, Integrative Thinking, Cross-Pollination, Multiple Perspectives
    ├── 05-validation.md            # Hypothesis Testing, Falsification, Calibration of Confidence
    ├── 06-tools-for-building.md    # Visual Models, Thought Experiments, Feynman Technique, Learning by Teaching
    └── 07-mindset-metacognition.md # Growth Mindset, Curiosity, Meta-Cognition, Intellectual Humility, Embracing Ambiguity
```

## The difference

Most "explain X" prompts produce knowledge transfer. This skill produces understanding. The gap between those two things is enormous — and it's the gap between forgetting something in a week and actually being able to use it.
