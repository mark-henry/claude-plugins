---
name: cut
description: "Big-picture simplification audit for code grown by many small edits: find the one reframing that removes the most branches. Use for \"gordian\", a simplification pass, or suspected death by a thousand patches."
---

# Gordian knot check (complexity & simplification audit)

Step back from local diffs. Ask whether the **whole** still matches a **simple** mental model, or whether many small changes have stacked flags, branches, and special cases that obscure the real goal.

## When to run
- After a long series of small PRs or tweaks on the same area.
- When files grow many `if` / `try` / feature toggles / "temporary" workarounds.
- When the user feels the code is hard to explain in one sentence.
- Proactively when reviewing a module that "does everything."

## Workflow
1. **Restate the job in one sentence.** What is this code *for* (user-visible or API outcome), not how it is implemented?
2. **Map structure to intent.** List main types, modules, or layers. For each, note whether it exists because of the core job or because of history (workarounds, backwards compatibility, duplicated concepts).
3. **Smell scan** (quick pass; flag, don't fix yet):
   - Same concept represented in multiple places (state, validation, naming).
   - Parameters or enums that encode "which code path" instead of a single model.
   - Deep nesting or long functions that mix policy, I/O, and formatting.
   - Comments that apologize or say "for historical reasons."
   - Tests that mirror implementation detail rather than behavior.
4. **Forest test.** If a new teammate had only the **public surface** (API, CLI, main types), could they infer the right model? If not, the internal structure may have diverged from the problem.
5. **Gordian-knot question.** *If we were allowed one breaking or bold change*, what single refactor would collapse the most branches? Examples: one state machine instead of scattered flags; one pipeline stage; replace ad-hoc parsing with a grammar or schema; delete a "compatibility" layer that no longer pays for itself.
6. **Recommend.** Prefer one **insightful** simplification over a list of micro-optimizations. If a big cut is too risky, name the **smallest** step toward it (e.g. extract one invariant, narrow one type).

## Output format
```markdown
## Gordian knot check: [area or file]

### One-sentence job
[…]

### Forest (does structure match the job?)
[Yes / partly / no — short why]

### Accumulated complexity
- [bullet: symptom → likely cause]

### Gordian option (big picture)
[One paragraph: the simplification and what it deletes or unifies]

### If not cutting the knot now
[Smallest next step + what to measure or test]

### Risk / tradeoffs
[What breaks, migrations, or learning cost]
```

## Principles
- Simplification is not deletion for its own sake; it is aligning code with a **clearer model**.
- Prefer **fewer concepts** over **more options**; prefer **data that implies behavior** over **switches everywhere**.
- Scope the audit to the area under discussion; don't rewrite unrelated code unless the user asks for a wider pass.
