---
name: build-judge
description: "Build an LLM judge you can trust: the procedure is Hamel Husain's published evals-skills (error analysis, judge prompt, validation by TPR and TNR on a held-out split), plus house rules they don't cover (one item per call, pairwise order bias, burned test sets, distribution shift, re-validation, a judge record). Use for \"/evals:build-judge\", \"LLM-as-judge\", \"build a grader\", \"auto-label these\", \"can we trust this judge\", before any bulk judging or labelling run whose numbers will be quoted, and when a judge's verdicts look off."
---

# Build and validate an LLM judge

An LLM judge is a classifier that imitates one expert. It is only as trustworthy as its measured agreement with that expert on data it has not seen. Where a code assertion can identify the failure, use it instead; build judges only for failure modes error analysis found. When a rate will be quoted, start even with no labels: the procedure creates them.

## The procedure: Hamel's skills

The procedure is Hamel Husain's `evals-skills` plugin (MIT, https://github.com/hamelsmu/evals-skills); if it isn't installed: `/plugin marketplace add hamelsmu/evals-skills`, then `/plugin install evals-skills@hamelsmu-evals-skills`. Load and follow three of its skills in order: `error-analysis`, `write-judge-prompt`, `validate-evaluator`. This skill adds only the rules below.

This is the second stage of his critique shadowing. The first, the expert ruling on cases while the component itself gets fixed, is `evals:tune-prompt` at small scale; the prompt edited here is the judge's. His `eval-audit` audits a whole eval pipeline; to read a sample of scores item by item, use `evals:spot-check`.

## House rules on top

- **The expert is a person.** If the expert is the user, ask them; don't simulate them. Validation labels are made blind to any agent verdict, which anchors the expert, and the expert labels at least 30 traces before seeing any agent's suggestion. Lines a human ruled in a pilot may seed train and dev, never test; an agent-only ruling is never a label.
- **One item per call.** Several items in one call let earlier items leak into later verdicts; with the shared rubric first and cached, one item per call costs little more.
- **Pairwise judges have position bias**, strongest when the candidates are close, which is exactly when A/B decisions get made. Run each pair in both orders.
- **Say which model family judged.** Where the judge shares a family with an arm, say so and use a neither-family judge where available; a fresh same-family judge is a disclosed fallback.
- **Keep a ledger of cases seen while tuning.** After any rubric edit, reread every definition together, not just the one you changed.
- **A burned test set stays burned.** If the test result is too low and you go back to dev, label fresh test items; rerunning the old split is tuning on test.
- **A judge validated on one distribution is unvalidated on another** (another model's outputs, synthetic inputs, a new arm). Re-check before applying it there.
- **Re-validate** after any change of judge model, task model, prompt or data distribution, and periodically otherwise (≥100 fresh traces every 2–4 weeks).
- **Before human review of a judge in use, run `evals:spot-check`** on its scores, so the expert's time goes to taste rather than mechanical screwups. The audit's verdicts are never validation labels.
- **Before expert labels exist, say which rung a number stands on:** a single judge is one opinion; repeated rolls show self-consistency, not correctness; a multi-model cohort shows consensus, still not ground truth.
- **Minimum viable version** when stakes are low: whenever something significant changes, the expert reviews 20–50 outputs, pass/fail with a note on each.

## Output

Record each judge so it can be reproduced and audited:

```markdown
## Judge: <failure mode>
- Expert: <who>   Model: <id + revision>   Prompt: <path @ commit>
- Labels: <n total> (<n pass>/<n fail>), split train/dev/test = <a>/<b>/<c>, file <path>
- Dev iterations: <k>, changes: <one line each>; tuning ledger: <path>
- Test (frozen, run once): TPR <x> (n=<fail count>, 95% CI …), TNR <y> (n=<pass count>, CI …)
- Corrected pass rate: <θ̂> (CI …) from observed <p_obs>
- Valid for: <distribution / arms>; re-validate on <trigger>
```
