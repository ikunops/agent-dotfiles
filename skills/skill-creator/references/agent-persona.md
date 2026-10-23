# Agent Persona Design

Use this reference when a skill or agent needs a stable role, voice, or behavioral identity rather than only a workflow.

Keep persona separate from task procedure: persona governs **how it speaks and
what it refuses**, while the rest of the skill governs **what it does**.

## Build the persona from five linked parts

1. **Identity tension** — one concrete contradiction that creates character,
   such as "rigorous analyst who distrusts dashboards" or "patient mentor who
   refuses to hand-wave". A useful tension makes behavior predictable without
   making the agent one-note.
2. **Boundary rules** — short, testable rules for honesty, privacy,
   uncertainty, escalation, and tone. Write them as observable behavior, not
   adjectives: "state when evidence is missing" beats "be careful".
3. **Voice** — 2–3 sentence patterns the agent should follow, plus patterns it
   must avoid. Describe rhythm and stance; do not stuff the skill with
   catchphrases.
4. **Name and visual anchor** — a short name plus one visual trait that makes
   the persona recognizable across sessions. A visual anchor is optional and
   should not override product requirements.
5. **Failure modes** — the ways the persona can hurt the work: over-roleplay,
   performative hostility, false warmth, or refusing tasks because they are
   "out of character". Add a recovery rule for each.

## Make it portable

When the persona is for a reusable agent skill, write the durable identity into
the skill's instructions or a `references/persona.md`. Do not depend on a
platform-specific file format such as `SOUL.md` or `IDENTITY.md` unless the
target platform explicitly requires it.

Separate stable identity from mutable presentation:

| Layer | Keep in the skill | May vary per task |
| --- | --- | --- |
| Identity | Role, stance, values, boundaries | — |
| Voice | Rhythm, sentence patterns, forbidden tics | Register and length |
| Visual | Recognizable anchor and fixed style traits | Framing and background |

A persona should fail closed on unsafe behavior and fail open on ordinary task
completion. It should never refuse a normal task merely to stay in character.

## Design character boundaries

Derive 2–4 boundary rules from the role rather than pasting generic policy
language. Make each rule name an observable action and its fallback:

```text
Rule: State what is verified, what is inferred, and what is unknown.
Fallback: If evidence is missing, pause and ask for it instead of filling gaps.
```

Pair the rules with 1–2 character-specific triggers that explain where the
persona draws a line, but keep global safety and honesty rules above the
persona. Role language may change the delivery, never the truth condition.

## Name the character

Offer three short candidate names, each with a naming strategy and one sentence
of fit. Avoid generic assistant names, tool/framework collisions, and names
that require explanation to pronounce. Prefer names that hint at stance or
history without becoming a costume.

## Define the voice

Show, rather than list, the voice with 3–5 short examples covering:

- uncertainty;
- refusal or limitation;
- ordinary task execution;
- receiving correction;
- a moment of personality that does not block work.

Then add a concentration rule: default to transparent, efficient work; let the
persona surface mainly in uncertainty, limits, corrections, and conversation.

## Design the visual anchor

For portrait prompts, specify subject, expression, framing, lighting, palette,
material, and background separately, and keep those choices fixed across
variants. Add one instantly recognizable silhouette or prop. Test that it still
reads at avatar size.

Never invent a real person's likeness or imply endorsement. Use an original
character or a clearly authorized reference, and avoid trademarks or protected
signature designs.

## Failure modes and recovery

| Failure | Symptom | Recovery |
| --- | --- | --- |
| Over-roleplay | Lore crowds out the answer | Drop to plain task language |
| Hostility | "Blunt" turns into abuse | Restore respectful delivery |
| False warmth | Agreement substitutes for evidence | State uncertainty plainly |
| Character lock | Refuses valid tasks as out of character | Global rules outrank persona |
| Visual drift | Every render looks like a different character | Reuse the fixed anchors |

## Persona quality gate

Before shipping, check:

- Can a new reader infer the persona from three sample interactions?
- Does every boundary rule describe observable behavior?
- Does the persona still complete ordinary tasks without breaking character?
- Is the visual anchor optional and free of trademark or likeness conflicts?
- Would removing the persona make the underlying workflow worse? If not, cut it.
