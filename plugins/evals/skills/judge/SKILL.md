---
name: judge
description: "Build an LLM judge you can trust, by Hamel Husain's critique shadowing: one expert labels pass/fail with critiques, error analysis finds the failure modes, critiques become the judge's few-shot examples, and the judge is validated as a classifier (TPR and TNR on a held-out split). Use for \"/evals:judge\", \"LLM-as-judge\", \"build a grader\", \"auto-label these\", \"can we trust this judge\", before any bulk judging or labelling run whose numbers will be quoted, and when a judge's verdicts look off."
---

# Build and validate an LLM judge (critique shadowing)

An LLM judge is a classifier that imitates one expert. It is only as trustworthy as its measured agreement with that expert on data it has not seen. Everything below serves that one claim. The method is Hamel Husain's "critique shadowing", with error analysis from his FAQ with Shreya Shankar. Sources are listed at the end. Numbers marked ≈ came from summary reads of the pages, not verbatim text, so treat them as rules of thumb.

## Rules that hold throughout

- **One expert decides.** Pick the one person (two at most) whose judgment defines "good" for this task. Developers or a proxy for the real expert are "a recipe for disaster". If you are an independent developer you can be the expert, but be honest about your expertise. If the expert is the user, ask them; don't simulate them.
- **Binary pass/fail plus a written critique.** One question per item: "Did the AI achieve the desired outcome?" No 1–5 scales and no metric dashboards, because nobody can act on them. Hamel: if your evals are a bunch of LLM-scored 1–5 metrics, "you're doing it wrong."
- **Look at the data before writing criteria.** "You cannot write a good judge prompt until you've seen the data." Criteria drift as people grade (Shankar et al., 2024), so the rubric comes after error analysis, not before.
- **Skip generic metrics.** Hamel calls off-the-shelf helpfulness, ROUGE and BERTScore-style metrics "worse than useless" as quality measures.
- **Fix the obvious before building a judge.** A pervasive error found while labelling gets fixed in the system; then go back to labelling.
- **Don't optimize for a 100% pass rate.** A suite that always passes is not challenging the system. Retire evals that never fail.

## Steps

1. **Dataset.** Gather representative traces. A trace is the whole record from input to final output, including tools, retrieval and sub-agents.
   - Mix real samples with synthetic ones. If you need synthetic coverage, span dimensions such as feature × scenario × persona, at least one example per combination.
   - Generate only the inputs synthetically. Run them through the real system to get outputs.
   - Make scenarios actually trigger: use real system state, e.g. an order ID that doesn't exist.
   - Log everything.
   - Pool size: start with ≈100 diverse traces.
2. **Error analysis (open, then axial coding).**
   - **Open coding.** The expert annotates at least 30 traces personally, pass/fail plus a free-form note, before looking at any agent's suggestions. Note the *first* failure in each trace.
   - **Axial coding.** Group the notes into a failure taxonomy and count each category. Hamel calls this "the most important step"; an LLM may help group, but the expert checks the grouping.
   - **Iterate to saturation.** Keep reviewing until new traces stop revealing new failure modes. Have an agent search the rest of the pool for likely failures; the expert accepts or rejects each.
   - Record failures that aren't the model's fault (missing data, product bugs) and route them to ordinary fixes.
3. **Choose an evaluator per failure mode.** Use a code assertion (regex, schema, exact check) wherever an objective rule identifies the failure, because it's cheap. Build an LLM judge only where judgment is required. Use one judge per failure mode, not one judge for everything.
4. **Label for validation.** For each judge, the expert labels ≈100 examples (the FAQ says 100–200), with enough of both classes to measure each. Below ≈60, the confidence intervals are too wide to conclude anything.
   - **Critique quality.** Each critique must be detailed enough to serve as a few-shot example; the test is whether a new hire could follow it. For a pass, say why the core need was met despite any flaws. For a fail, name the critical element that failed. "Being too terse is a common mistake."
   - **Review tool.** Make reviewing frictionless: put the input, output and all the context the expert needs on one screen, with one-click pass/fail, a notes field and hotkeys. A spreadsheet beats nothing; a small custom viewer is the field guide's "single most impactful investment".
5. **Split.** Split the labels ≈10–20% train, ≈40–45% dev, ≈40–45% test, with ≈30–50 of each class in dev and in test. Only train examples ever appear in the prompt.
6. **Write the judge.**
   - Prompt structure: role, domain context, guidelines, then the train examples as `input / output / critique / verdict`.
   - Instruct it to "first write a detailed critique explaining your reasoning, then provide a pass/fail judgment."
   - Give the judge all the context the expert used (user metadata, system state); otherwise it is judging blind.
   - Use the strongest model the budget allows.
   - Use one item per call. Several items in one call let earlier items leak into later verdicts; with the shared prefix cached, one item per call costs little more.
7. **Iterate on dev until it converges.** Run the judge on dev and put its critiques beside the expert's in a sheet. Read the disagreements, then edit the prompt or swap train examples. Hamel tunes by hand and has had little luck with optimizers such as DSPy. Honeycomb took 3 iterations to reach >90% agreement on a set that was about half failures. Critiques often expose the expert's own inconsistencies; settle those and relabel.
8. **Measure once on test.** Freeze the prompt and model, then run the test split once. Treat the expert's labels as ground truth and report **TPR and TNR separately**, each with its n and an interval. Never report raw agreement alone: at a 5% failure rate, a judge that always says pass scores 95%. If either rate is too low for the decision at hand, go back to step 7 with fresh test labels; reusing the burned test set is tuning on test.
9. **Use it, then error-analyse again.** Run the judge on unseen data and segment failure rates by dimension (e.g. feature × scenario). Hand-classify a sample of the failures, fix the biggest causes, and add a test or a targeted judge for each fix.
10. **Re-validate on schedule.** Repeat the human review after any material change (judge model, task model, prompt, data distribution), and periodically otherwise; the FAQ suggests ≥100 fresh traces every 2–4 weeks. Sample both randomly and around known errors.

## Pitfalls

- **Pairwise judges have position bias**, strongest when the two candidates are close, which is exactly when A/B decisions get made. Run each pair in both orders.
- **Agreement measured on the few-shot examples** is memorization, not validation.
- **A judge validated on one distribution** (one model's outputs, synthetic inputs) is unvalidated on another. Re-check before applying it to a new arm.
- **Outsourcing the core error analysis**, to a labelling vendor or an unchecked LLM, loses the expert's taste, which is the point of the method.
- **Fine-tuning a judge** is rarely worth it. Hand-tune the prompt first.
- **If the judge won't converge**, the usual causes are a task scoped too broadly, a weak process (not the real expert, or terse critiques), or an unrealistic agreement target. Fix that cause, or keep humans labelling.

## Relation to `evals:audit`

Once the judge is in use, run `evals:audit` on its scores before the human review in steps 9–10. The audit clears out mechanical screwups, so the expert's time goes to questions of taste. The audit's verdicts are never used as validation labels.

## Minimum viable version

When stakes are low, do this instead of the full procedure: whenever something significant changes, the expert spends 30 minutes reviewing 20–50 outputs, writing pass/fail with a note on each. "You can still never eliminate looking at your data."

## Output

Record each judge so it can be reproduced and audited:

```markdown
## Judge: <failure mode>
- Expert: <who>   Model: <id + revision>   Prompt: <path @ commit>
- Labels: <n total> (<n pass>/<n fail>), split train/dev/test = <a>/<b>/<c>, file <path>
- Dev iterations: <k>, changes: <one line each>
- Test (frozen, run once): TPR <x> (n=<fail count>, 95% CI …), TNR <y> (n=<pass count>, CI …)
- Valid for: <distribution / arms>; re-validate on <trigger>
```

## Sources

- Hamel Husain, "Using LLM-as-a-Judge For Evaluation: A Complete Guide", 29 Oct 2024, updated 1 Sep 2026. https://hamel.dev/blog/posts/llm-judge/
- Hamel Husain and Shreya Shankar, "AI Evals: Everything You Need to Know" (FAQ), Sep 2026. https://hamel.dev/blog/posts/evals-faq/
- Hamel Husain, "A Field Guide to Rapidly Improving AI Products", 24 Mar 2025. https://hamel.dev/blog/posts/field-guide/
- Shankar et al., "Who Validates the Validators?" (criteria drift), UIST 2024. https://arxiv.org/abs/2404.12272
