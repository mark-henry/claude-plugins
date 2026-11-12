---
name: supervisor
description: "Hold one ML experiment to lab rules and sign it off or refuse: twelve rules (one recorded difference between arms, prediction and denominator before results, controls, a noise floor that spans the claim, leakage and held-out discipline, a validated instrument, the freeze, a script-written run record with one commit per run), each checked against a file, a hash, a command's output or the run record. Use for \"/lab:supervisor\", \"is this design fit to run?\", \"sign off on this run\", \"can I quote this number?\", \"is this confirmatory?\", \"do the arms differ in only one thing?\", \"check the run record\", before a counted training or eval run launches, and before a number meets a bar, enters a report or picks an arm. Not for designing or running the experiment (use lab:experiment), writing or scoring a preregistration record (lab:prereg), validating an LLM judge (evals:judge) or reading a sample of scored items (evals:audit)."
---

# lab:supervisor

The rulebook and sign-off for one experiment, whoever runs it: one engineer, one agent or a fleet. It opens evidence and rules on it. It launches no run and fixes nothing; it reruns checks (fixtures, hashes, intersections). The procedure is `lab:experiment`'s.

It is asked at two moments. At **launch** (is this design fit to run?) rules 1–8 apply. At **quote** (is this result fit to meet a bar, enter a report or pick an arm?) all twelve apply, 1–8 against what actually ran. A run launched to be quoted as confirmatory is *counted*. Every other run (smoke, pilot, noise floor, positive control) is exploratory: it owes rule 8's record and leaves the sealed set untouched.

Each rule has named evidence, listed in [checks.md](checks.md): read it before signing. Open the evidence yourself: a summary is not evidence, and evidence you cannot find is not met. "n/a" needs a reason. No other rule is applied.

## Rules 1–8: the design

1. **One difference.** The treated arm differs from its untreated comparator in one named treatment; each control names its own one difference. Every other knob is marked matched, fixed, or tuned per arm on an equal budget, and a matched value says which arm it was tuned on. That includes what travels with the treatment: warm start, output length, compute, when the arm ran. A reused earlier arm is first reproduced inside rule 4's floor.
2. **Prediction and denominator first.** Each arm and metric has a predicted interval that a result on the failing side of the bar would miss, its denominator, the bar and the decision each outcome leads to, fixed before the treated arm has produced output on this experiment's items, smoke runs included.
3. **Controls.** An untreated arm at the same settings, a simple baseline, a positive control that must succeed if the plumbing works, and a control for each rival explanation the plan names.
4. **Noise floor.** A number measured on this harness that spans what the claim spans. A claim about a treatment needs the unchanged baseline on at least three seeds. Reruns of one checkpoint, or step 0 twice, bound eval noise only and license a claim about these checkpoints on these items. A measured floor of zero is replaced by the interval over items.
5. **Leakage and held-out.** Train, dev and sealed sets are disjoint in content, and in time where data is ordered. Eval targets reach no training data, reward or prompt, generated data included. Whatever is being optimized cannot read or edit the scorer or the sealed items. Nothing is tuned or picked on the sealed set, here or earlier: if an earlier result on it shaped this design, it is dev for this claim. LLM judges and baselines get one item per call.
6. **Instrument.** The scorer reproduces a fixture's known result: a known pass passes and a planted fail fails. An LLM judge has an `evals:judge` record (TPR and TNR from a test split run once) valid for this judge model and prompt; where its "Valid for" line does not cover a treated arm's outputs, the expert has re-checked a sample of them. The judge sees no arm label, and a pairwise judge runs both orders.
7. **Freeze.** Before the first counted run, a dated FREEZE line in the plan names the commit, seeds, n, kill thresholds, and the item-set, scorer and judge-prompt hashes. Rubric and thresholds were settled on baseline or dev outputs, never a treated arm's.
8. **Run record.** Every run has one record, written by the launcher or a script at launch and completed at exit, never by a person from memory:

```
at launch: run_id, parent_run_id, plan@commit, prereg, arm, label (confirmatory/exploratory), commit, command, config_resolved,
           models with revisions (base, checkpoint, adapter init, judge, generator; substitutions),
           hashes (train, dev, sealed, scorer, judge_prompt), seeds, env_lock, hardware, caps, launched_by, started
at exit:   ended, end_reason (completed/kill rule/cap/crash), cost
```

One commit per run: a counted run executes one commit on a clean tree, untracked files included, and its finished record is committed alone and never edited. An exploratory run on a dirty tree records its diff instead. A relaunch is a new run naming its parent, in the folder its arm's earlier runs used; a run whose launcher died is closed by a script from its logs. A field the experiment has no use for is null with the reason. A generated dataset has a manifest beside it: source commit, generating command, model and revision, prompt, time.

## Rules 9–12: the result

9. **Nothing moved after the freeze.** Nothing the FREEZE line or the prereg record names has changed, except by a dated amendment in the human's own words, reported beside the number. An amendment governs runs started after it: results already in hand are exploratory against what it changed. No trials, samples or rejudging were added after a result, except that a scorer defect is fixed by amendment and every arm rescored, both scores reported.
10. **Scores read.** A scorer, judge, metric or prompt that is new, changed or meeting a new kind of output (a treated arm's is one) has an `evals:audit` verdict of "fit to quote" on these runs, with no re-audit pending. Errored and missing items are counted apart from fails.
11. **Declared denominator, beyond noise.** The number is the preregistered metric over its declared denominator (for a mean, the unit and count averaged over), with an interval or every seed's value, and the untreated arm and simple baseline beside it. Any other denominator is labeled post hoc. If the arms can differ in the denominator (attempts, parsed, not refused), the all-items rate is quoted beside it for each arm. A difference is claimed only if it exceeds rule 4's floor and its own interval, paired on shared items or across seeds, excludes zero; a null only if the positive control passed.
12. **Confirmatory or exploratory.** Confirmatory means labeled so at launch, run on a commit descended from the FREEZE commit, prereg record closed, and every rule met or waived; it travels as `prereg <file>: predicted X, got Y (n/N)`. Anything else travels with the word *exploratory* and cannot pass or fail a bar or pick an arm.

## Not met

One unmet rule blocks sign-off: at launch the supervisor refuses the counted run, at quote any use of the number beyond "exploratory, unsigned". It repairs nothing and signs nothing "with caveats". There are three ways out. Meet the rule and ask again. Get a waiver: only the human who owns the experiment gives one, naming the rule, and it counts only when the supervisor can open their own words for it (their message, a commit they authored); a line an agent wrote is a request. It is recorded as `WAIVER <rule>: <who>, <date>, <reason>` in the plan and beside the result, and quoted with the number; with rule 2 or 7 waived the number travels as exploratory. Or stop and report the rule, the evidence opened and what it showed. A stop with the facts is a good outcome.

## Verdict

```
Supervisor: <experiment>, <launch|quote>, <date>, plan@<commit>, runs <ids>
1 One difference: met / NOT MET / n/a (reason); <evidence opened, what it showed>
… a line per applicable rule, not-met first
Amendments and waivers: <what, who, date, where recorded>
Sentence signed (at quote): <the number as it will be quoted>
SIGNED / SIGNED WITH WAIVER / NOT SIGNED: <unmet rules, what would meet each>
```
