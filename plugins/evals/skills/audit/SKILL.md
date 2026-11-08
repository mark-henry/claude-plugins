---
name: audit
description: "Audit an eval's scores before anyone trusts the aggregate: a subagent pulls a stratified sample of 30–50 scored items (high, middle and low scorers, plus disagreements and outliers), reads each one in full, and flags screwups such as scores too high, scores too low, and broken items. Use for \"/evals:audit\", \"audit the scores\", \"sanity-check this eval\", after any new eval, judge, metric or scoring change produces numbers, before a number is reported or used to pick between arms, and whenever a rate surprises you."
---

# Audit an eval's scores

An aggregate hides the items that produced it. A mean of 0.72 can be a judge passing empty outputs, a parser zeroing correct answers, or a reference answer that is wrong. Reading a stratified sample finds these every time, and it costs machine effort, not human attention. Run the audit in a subagent first, so the human only sees what survives it.

This is a prescreen, not a substitute for the expert. It catches screwups in how an existing scorer was applied: parser bugs, empty outputs scored as passes, wrong references, leakage. It does not decide what "good" means, and its verdicts are not labels. Defining the criteria and validating a judge's TPR/TNR still need the expert's own labels (`evals:judge`). The human still looks; the audit means they look at an eval that has already been debugged.

## When it applies

- A new eval, judge, metric, prompt or scoring change has produced its first real numbers.
- A number is about to be reported, compared to a bar, or used to choose between arms.
- A rate surprises anyone, in either direction.
- A judge built with `evals:judge` is first applied to a new distribution.

## Steps

1. **Draw the sample.** Pick 30–50 items, stratified by score, not at random. A random sample spends itself on the middle.
   - **Top ≈10:** the highest scorers. Here look for passes that should have failed.
   - **Bottom ≈10:** the lowest scorers. Here look for fails that should have passed.
   - **Middle ≈10:** around the median and near the pass threshold, where the call is closest.
   - **Special ≈10, where they exist:**
     - items where the judge and a human disagree;
     - items where two arms or two judges disagree most;
     - items where a stochastic score varies most between samples;
     - outliers in length, latency or cost;
     - parse failures, empty outputs and refusals.

   For a binary eval, the strata are pass, fail and disagreement. Record the seed and the selection rule, so the sample can be redrawn exactly.
2. **Brief the auditor without anchoring it.** Spawn a fresh subagent and give it:
   - what the eval measures and how a score is produced (the metric definition, judge prompt or scorer code path);
   - the sample file;
   - the full item for each sample: input, output, reference or answer key, the score, and the judge's critique if there is one.

   Do not give it your hypothesis or the headline number. The auditor reads every item in full; excerpts are where screwups hide. If the sample is large or the items are long, split it across several auditors with the same brief, and give each a mix of strata, so no auditor sees only the top.
3. **For each item, the auditor gives:**
   - its own verdict;
   - whether the score is **right**, **too high**, **too low** or **broken** (the item itself is defective);
   - one line of evidence, quoted from the item;
   - for every flagged item, a suspected cause: wrong reference, parsing or formatting, truncation, judge leniency or harshness, rewarding length or style, leakage (the answer is visible in the context), a degenerate output scored as success, a mislabel, or a scorer bug.
4. **Verify the auditor's flags.** Recheck any flag that would change a decision yourself, or with a second auditor that is told only "check this item" and not what the first auditor concluded. Auditors can be wrong too.
5. **Report the pattern, not just the items.**
   - Give flagged counts by stratum, e.g. "top 10: 3 too high; bottom 10: 4 broken by the same parser bug".
   - Group flags by cause.
   - Estimate what each cause does to the aggregate, e.g. "fixing the parser would move ≈8% of fails to pass".
   - Fix scorer and data bugs, rescore, and re-audit with a fresh sample. Never re-audit the items you just fixed.
6. **Then show the human.** Show a curated handful:
   - the best high scorer and the worst high scorer;
   - the best low scorer and the worst low scorer;
   - one example of each confirmed failure cause;
   - if nothing was flagged, a few items that show the eval working as intended, so the human can see it.

   Each item comes with the auditor's one-line verdict. The human decides whether the eval is fit to quote.

## Rules

- No aggregate from a new or changed scorer is reported before its audit. A "clean" number counts as clean only after someone has read the clean items too.
- If items contain private or sensitive text, the auditor runs only on a route your data policy allows for that text.
- Keep the audit beside the results: sample file, seed, auditor brief, verdicts, fixes made. An eval number is trustworthy only if its audit can be found.
- An audit with zero flags in 30–50 items is evidence, not proof. Say how many items were read when you say "looks clean".

## Output

```markdown
## Audit: <eval> @ <commit / run id>
- Sample: <n> items (top <a>, bottom <b>, middle <c>, special <d>), seed <s>, file <path>
- Flags: too high <x>, too low <y>, broken <z> (by stratum: …)
- Causes: <cause> ×<k> (est. effect on aggregate: …); …
- Fixes made: <…>; re-audit: <pending / clean on n fresh items>
- Shown to human: <item ids>
- Verdict: fit to quote / fix first / scorer unreliable
```
