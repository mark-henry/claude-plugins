---
name: spot-check
description: "Audit an eval's scores before anyone trusts the aggregate: a subagent pulls a stratified sample of 30–50 scored items (high, middle and low scorers, plus disagreements and outliers), reads each one in full, and flags screwups such as scores too high, scores too low, and broken items. Not a review of the whole eval pipeline (that is Hamel's `eval-audit`). Use for \"/evals:spot-check\", \"audit the scores\", \"sanity-check this eval\", after any new eval, judge, metric or scoring change produces numbers, before a number is reported or used to pick between arms, and whenever a rate surprises you."
---

# Audit an eval's scores

An aggregate hides the items that produced it: a mean of 0.72 can be a judge passing empty outputs, a parser zeroing correct answers, or a wrong reference. Before a number from a new or changed scorer is reported, compared to a bar or used to pick between arms, a fresh subagent reads a sample of the scored items, so the human looks at an eval that has already been debugged.

This catches mistakes in how a scorer was applied. It does not decide what "good" means, and its verdicts are never labels: that takes the expert's own labels (`evals:build-judge`).

## The contract

- **The sample** is 30 to 50 items stratified by score, not random: the top, the bottom, the middle near the threshold, and where they exist the disagreements (judge against human, arm against arm), outliers, parse failures, empty outputs and refusals. Record the seed and the selection rule so it can be redrawn.
- **The auditor** is a fresh subagent given how a score is produced and each sampled item whole: input, output, reference, score and any judge critique. It never gets your hypothesis or the headline number.
- **For each item** it says whether the score is right, too high, too low or broken, with one line quoted from the item and a suspected cause.
- **A flag that would change a decision** is rechecked by you, or by a second auditor told only "check this item".
- **The report** gives flagged counts by stratum, flags grouped by cause, and what each cause does to the aggregate. Fix scorer and data bugs, rescore, and audit again on a fresh sample, never the items just fixed.

## What the human sees

Counts, causes, fixes and a verdict: fit to quote, fix first, or scorer unreliable. No example items unless the user asks; offer them in one line. If they ask, show a uniform random draw, some high and some low scorers, and one example of each confirmed cause, each with its score and how it was chosen. When the human is about to label or judge items themselves, show no examples, scores or verdicts until their labels are in.

## Rules

- Zero flags in 30 to 50 items is evidence, not proof: say how many items were read when you say "looks clean".
- Items holding private or sensitive text are audited only on a route the user's data policy allows for that text.
- Keep the audit beside the results: sample file, seed, auditor brief, verdicts, fixes. A number whose audit cannot be found is not audited.
