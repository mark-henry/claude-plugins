---
name: supervisor
description: "Hold one ML experiment to lab rules and sign it off or refuse: thirteen rules (one recorded difference between arms, prediction and denominator before results, controls, a noise floor that spans the claim, leakage and held-out discipline, a validated instrument, the freeze, a script-written run record with one commit per run), each checked against a file, a hash, a command's output or the run record. Use for \"/lab:supervisor\", \"is this design fit to run?\", \"sign off on this run\", \"can I quote this number?\", \"is this confirmatory?\", \"do the arms differ in only one thing?\", \"check the run record\", before a counted training or eval run launches, and before a number meets a bar, enters a report or picks an arm. Not for designing or running the experiment (use lab:experiment), writing or scoring a preregistration record (lab:prereg), validating an LLM judge (evals:judge) or reading a sample of scored items (evals:audit)."
---

# lab:supervisor

The rulebook and sign-off for one experiment. It launches no run and fixes nothing; it reruns checks (fixtures, hashes, intersections).

It is asked at two moments. At **launch** (is this design fit to run?) rules 1–8 apply. At **quote** (is this result fit to meet a bar, enter a report or pick an arm?) all thirteen apply, 1–8 against what actually ran. Where training and evaluation launch separately, each is a launch moment with its own FREEZE line.

A run launched to be quoted as confirmatory is *counted*. Every other run (smoke, pilot, screening, noise floor, positive control) is exploratory and owes rule 8's record; smoke, pilot and screening runs leave the sealed set untouched.

Below is each rule in short. Its exact conditions, and the evidence that shows it, are in [checks.md](checks.md) under the same number: read the entry before ruling on it. Open the evidence yourself: a summary is not evidence, and evidence you cannot find is not met. "n/a" needs a reason. No other rule is applied.

*Pinned* means committed, or, for a file that must stay out of any repository, hash-logged at the time in a place the experimenter cannot rewrite (checks.md says how). A timestamp pins nothing.

## Rules 1–8: the design

1. **One difference.** The treated arm differs from its untreated comparator in one named treatment, and each control in its own one. Every other knob is recorded as matched, fixed, or tuned per arm on an equal budget, including what travels with the treatment: warm start, output length, compute, when the arm ran, any model that generated or selected its data.
2. **Prediction and denominator first.** Each arm and metric has a predicted interval that a failing result would miss, its denominator, the bar and the decision each outcome leads to, pinned before the treated arm has produced output on the items the counted run scores, smoke runs included.
3. **Controls.** An untreated arm at the same settings, a simple baseline, a positive control that goes through every stage the treated arm does and must succeed if the plumbing works, and a control for each rival explanation.
4. **Noise floor.** A floor measured on this harness that spans what the claim spans: for a claim about a treatment, the unchanged baseline on at least three seeds.
5. **Leakage and held-out.** Train, dev and sealed sets are disjoint in content, and in time where data is ordered. Eval targets reach no training data, reward or prompt. Whatever is being optimized cannot read or edit the scorer or the sealed items. Nothing is tuned or picked on the sealed set, here or earlier.
6. **Instrument.** Every scorer or judge that a bar or decision reads has been seen to pass a known pass and fail a planted fail, on fixtures as hard to tell apart as the arms' own outputs. Its known confounds (output length, format) are controlled, or the claim is worded to what it measures.
7. **Freeze.** Before the first counted run, a dated, pinned FREEZE line in the plan names the commit, seeds, n, samples per item, kill thresholds, and the item-set, scorer and judge-prompt hashes.
8. **Run record.** Every run has one record, written by the launcher or a script at launch and completed at exit. One commit per run: a counted run executes one commit on a clean tree, and its finished record is pinned on its own and never edited.

```
at launch: run_id, parent_run_id, plan@commit or pinned hash, prereg and its pinned hash, arm, label (confirmatory/exploratory/screening),
           commit, command, config_resolved,
           models with revisions (base, checkpoint, adapter init, judge, generator; substitutions),
           hashes (train, dev, sealed, scorer, judge_prompt), seeds, env_lock, hardware, caps, launched_by, started
at exit:   ended, end_reason (completed/kill rule/cap/crash), cost
```

## Rules 9–13: the result

9. **Nothing moved after the freeze.** Nothing the FREEZE line or the prediction record names has changed, except by a dated amendment in the human's own words, reported beside the number. No trials, samples or rejudging were added after a result.
10. **Scores read.** A scorer, judge, metric or prompt that is new, changed or meeting a new kind of output (a treated arm's is one) has had a sample of its scored items on these runs read, ending in a verdict of "fit to quote".
11. **Declared denominator, beyond noise.** The number is the preregistered metric over its declared denominator, with an interval or every seed's value, and the untreated arm and simple baseline beside it. A difference is claimed only if it exceeds rule 4's floor and its own interval excludes zero; a null only if the positive control passed, with the largest effect its interval excludes.
12. **Confirmatory or exploratory.** Confirmatory means labeled so at launch, run on a commit descended from the FREEZE commit, prediction record closed, and every rule met or waived. Anything else travels with the word *exploratory* and cannot pass or fail a bar or pick an arm.
13. **The sentence.** As it will be quoted, its comparator, unit and scope are the artifact's; it credits only what a control isolates; it claims no more than the contrasts that met rule 11; and a preregistered guard or kill that fired is quoted with the number.

## Not met

One unmet rule blocks sign-off. At launch the supervisor refuses the counted run, and says the design may run as exploratory when rule 5 is met and rule 8's launch record exists, its missing fields named. At quote it refuses any use of the number beyond "exploratory, unsigned". It signs nothing "with caveats". Mark each unmet rule *record* when the thing was done and its evidence is unpinned or in the wrong form, and *claim* otherwise: a missing control, floor, prediction or reading is *claim*.

The ways out: meet the rule and ask again; get a waiver; or stop and report the rule, the evidence opened and what it showed. A stop with the facts is a good outcome.

Only the human who owns the experiment gives a waiver, naming the rule, and it counts only when the supervisor can open their own words for it: their message, or a commit they authored. A one-word approval counts only with the message it answers, and only when that message asks for nothing else and gives each rule and its reason. A line an agent wrote is a request. A waiver is recorded as `WAIVER <rule>: <who>, <date>, <reason>` in the plan and beside the result, and quoted with the number; with rule 2 or 7 waived the number travels as exploratory.

## Verdict

```
Supervisor: <experiment>, <launch|quote>, <date>, plan@<commit or pinned hash>, runs <ids or names>
1 One difference: met / NOT MET (claim) / NOT MET (record) / n/a (reason); <evidence opened, what it showed>
… a line per applicable rule: claim blocks first, then record blocks, then met; rules 1 and 11 get a line per contrast
Amendments, deviations and waivers: <what, who, date, where recorded>
Sentence signed (at quote): <the number as it will be quoted>
SIGNED / SIGNED WITH WAIVER / NOT SIGNED: <unmet rules, what would meet each>; at launch: may run as exploratory, yes or no
```
