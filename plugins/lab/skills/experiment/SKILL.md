---
name: experiment
description: "The one guideline for designing, preregistering, running, reading and signing off a single ML experiment (a fine-tune, an RL or rejection-sampling run, an LLM eval or judge), so that its number means what it will be quoted as meaning. Use for \"/lab:experiment\", \"design this experiment\", \"what do you think of this design?\", \"set up this ablation\", \"what controls do I need?\", \"how many seeds?\", \"is this null real?\", \"prereg\", \"preregister\", before a paid training or eval run, before any run whose number will be compared to a bar, reported or used to choose between arms, and when a surprising number is about to be quoted or built on. Not for deciding what is wanted and the cap (unattended:interview), large or unattended runs (unattended:go), validating an LLM judge (evals:build-judge), reading a sample of scored items (evals:spot-check). An eval of a skill or plugin is an experiment too: `claude plugin eval` is the tool that runs its arms, and this skill is still the design."
---

# lab:experiment

An experiment has no oracle for "does this mean what we think?", so its design is the checker. [checks.md](checks.md) has each rule's exact conditions and evidence; [templates.md](templates.md) the plan page, the read and the report; [references/evidence.md](references/evidence.md) the sources.

Every experiment gets a plan page and a written prediction; a small one buys fewer rungs, not less design. Every hypothesis, bar, rival and kill rule gets a code name on the plan (`H_FASTER`, `BAR_STEPS`, `RIVAL_LENGTH`, `KILL_DIVERGE`), defined once, never renamed, cited by every later file. A positive control that fails, or a floor wider than the effect hoped for, is a finding: stop and report it.

## Order of events

One folder per experiment. Inside `unattended:go` this skill designs the experiment piece, and go's attack, pilot ladder and report replace the same steps here; the supervisor's verdict line goes into go's report beside each number quoted. By hand:

1. **Frame.** `unattended:interview`, unless a brief is frozen: bring back the question, the bar with its denominator, the cap and the search record. If a cheap check settles the question, that check is the experiment.
2. **Read the harness** before designing: scorer or reward code, a few full traces, where seeds enter, each checkpoint's provenance, your earlier runs and why each died. Decide where the plan, prereg record and run records will be pinned: private data kept out of a repository needs its hash log first.
3. **Design** the plan page (templates.md) from "Start from the sentence" and rules 1–8.
4. **Attack.** `check:attack` on the plan page, with the scorer or reward code and a few raw untreated traces. Close its findings, say in one line what will run and what it should cost, and run it. Nobody approves the plan.
5. **Untreated first,** on baseline and dev outputs only: the instrument checks, `evals:build-judge` for an LLM judge a bar reads, the floor runs, the positive control.
6. **Predict.** Open and pin the prereg record ("The record and its tool"). Treated smoke and pilot runs come after it and stay exploratory.
7. **Freeze and launch.** The FREEZE line, then Sign-off at launch. Ask once earlier against a dry run's record, while a *record* block is cheap to fix.
8. **Counted runs,** arms interleaved in time; `unattended:arbiter` for unattended work against a machine check.
9. **Read** in the fixed order (templates.md), with `evals:spot-check`.
10. **Quote.** `prereg.py close`; each number in the draft report audited against a tool result from this session; Sign-off at quote, on the sentence as it will be written; `figure:make` draws it.
11. **Report,** the user's decisions last; then an amendment, a new plan or a stop.

## Start from the sentence

Before choosing arms, write the sentence you hope to quote, and the one for each other outcome: null, worse, inconclusive, no arm clears. Every word has to be bought: the comparator by an arm, the causal noun by a control that isolates it, the verb by what the metric measures, the scope by the models, seeds and items actually run. Strike now any word the design does not buy: rule 13 holds the final sentence to this.

- **Null picture.** Sketch the figure you would see if the treatment did nothing, noise band drawn in, from the analysis script run on a synthetic null. If it cannot be told from the figure you hope for at the planned n, the design cannot answer the question.
- **A null has to be designed.** State the smallest effect worth detecting and show the design could have seen it: a positive control of about that size, and n to match.

## The rules

The rules are asked at two moments. At **launch** (is this design fit to run?) rules 1–8 apply. At **quote** (is this result fit to meet a bar, enter a report or pick an arm?) all thirteen apply, 1–8 against what actually ran. Where training and evaluation launch separately, each is a launch moment with its own FREEZE line.

A run launched to be quoted as confirmatory is *counted*. Every other run (smoke, pilot, screening, noise floor, positive control) is exploratory and owes rule 8's record; smoke, pilot and screening runs leave the sealed set untouched.

*Pinned* means committed, or hash-logged by a script at the time where the experimenter cannot rewrite it (checks.md, "Pinned"). A timestamp pins nothing.

Below is each rule in short, the first paragraph under its heading. Its exact conditions and exceptions, and the evidence that shows it, are in [checks.md](checks.md) under the same number. What follows the paragraph is advice on meeting the rule, not conditions.

## Rules 1–8: the design

### Rule 1: one difference

The treated arm differs from its untreated comparator in one named treatment, and each control in its own one. Every other knob is recorded as matched, fixed, or tuned per arm on an equal budget, including what travels with the treatment: warm start, output length, compute, when the arm ran, any model that generated or selected its data. A reused earlier arm is retrained first.

- The usual failure is a setting (learning rate, most often) tuned on one arm and given to all. With no budget to tune per arm, fix it and narrow the claim, or show the gap at both ends of a plausible range.
- A config diff misses a continued adapter against a fresh one, a shared token cap (it truncates the longer arm more) and an ablation whose arms remove unequal amounts.
- Parity by construction: the treated arm's inputs with the treatment stripped reproduce the untreated arm's, token for token.
- A treatment that bundles several changes gets a control removing each part; the treated checkpoint with the mechanism off at sampling is the cheapest.

### Rule 2: prediction and denominator first

Each arm and metric has a predicted interval that a failing result would miss, its denominator, the bar and the decision each outcome leads to, pinned before the treated arm has produced output on the items the counted run scores, smoke runs included.

- Keep the treated arm dark until the record is pinned: do plumbing and instrument rungs on the untreated arm, or on items outside the counted set.
- A speed claim is steps to a threshold per run, the threshold still holding at the next eval with guard rates no worse than at step 0, censored at the horizon.

### Rule 3: controls

An untreated arm at the same settings, a simple baseline, a positive control that goes through every stage the treated arm does and must succeed if the plumbing works, and a control for each rival explanation the plan names or a trace reading has surfaced.

- Rivals come from traces: read untreated outputs and the scorer's code before listing them. Consider by default: ordinary capability, a signal supplied in the input, output length, a substitution only this judge rewards, one component's effect mistaken for the joint one. A mitigation ("the judge is another model family") is not a control.
- A scorer sanity check is not a positive control: a sampling fault that floors every arm passes it and reads as a null. A training treatment needs an arm trained on a planted signal it must learn (copying the target will do), its pass written first, run before any treated arm.
- Where the claim names a mechanism, switching it off must score near zero. For a rare behavior, fix the allowed count in advance: 0 of n only bounds the rate below about 3/n.

### Rule 4: noise floor

A floor measured on this harness that spans what the claim spans: for a claim about a treatment, the unchanged baseline on at least three training seeds (data order and initialization); the treated arm's seed count is rule 11's, or three reruns of the judge or sampler when that is the treatment.

- Measure and price the floor first: it sets kill thresholds and n, and the baseline seeds often cost more than the treatment. If they do not fit the cap, run shorter with more seeds, or word the claim now as "these checkpoints on these items".
- Floor runs come before the FREEZE and stay exploratory: the counted untreated arm is run again, interleaved with the treated runs, so price the baseline twice.
- Three seeds a side make a figure, not a test. A pilot prices the run and does not estimate the effect. The floor runs supply the spread for the power calculation.
- **Power is a gate.** Before any counted run, write the smallest difference that would change the decision, and the chance this design detects it, simulated from the floor runs. Under 80%, add samples or label the run exploratory before it starts; which one is the user's call, asked as its own question.
- **Screen items, not sets.** Run each item several times on the untreated arm before counting. An item that always or never succeeds is replaced or dropped: it adds cost and no information.
- **Put the samples where the spread is.** From the floor runs, compare the spread between reruns of the same item with the spread between items. When reruns disagree more, add runs per item; when items disagree more, add items. Say which you chose and the two numbers.

### Rule 5: leakage and held-out

Train, dev and sealed sets are disjoint in content, and in time where data is ordered. Eval targets reach no training data, reward or prompt. Whatever is being optimized cannot read or edit the scorer or the sealed items. Nothing is tuned or picked on the sealed set, here or earlier. LLM judges and baselines get one item per call.

- Start the exposure ledger (which runs scored which pack) with the first run.
- Routes a split does not close: generated training data that paraphrases the target; failure reports that echo gold labels to an optimizing agent; the agent's memory, notes and config files; held-out logs the next run can read; a stopping rule that reads oracle labels.
- Out of reach is built, not instructed (`unattended:arbiter`). Hiding the scorer stops tampering, not attempts: read traces for them.
- A baseline that reproduces the answer verbatim is a leak until audited. Check in code that the held-out step the plan documents actually runs.

### Rule 6: instrument

Every scorer or judge that a bar or decision reads has been seen to pass a known pass and fail a planted fail, where the planted fail is a near miss: the known pass minimally broken, or a baseline or dev output a person marked failing. Its known confounds (output length, format) are controlled, or the claim is worded to what it measures. An LLM judge also has a validation record for this model and prompt, sees no arm label and, if pairwise, runs both orders.

- Fixtures passing is not validity: a scorer can pass both and still rank by length where the arms sit. Before the freeze, look at where baseline, dev, constant-output and "no action" outputs score against the fixture's pass and fail.
- Decide how cheats and errors score before any exist, and report illegitimate successes scored both ways: dropping them removes the hardest items.
- Outputs identical across arms are a free probe of judge bias.
- In agentic evals the candidate sees no eval words (eval, test, judge, rubric, benchmark) and no sibling arm's directory.
- A reward is an instrument under attack. Write the reward table, what the configured reward pays each cheap strategy (refusing, invalid output, the shortest path to partial credit, moving work where the scorer does not look), computed by hand, and give it to the attacker.

### Rule 7: freeze

Before the first counted run, a dated, pinned FREEZE line in the plan names the commit, seeds, n, samples per item, kill thresholds, and the item-set, scorer and judge-prompt hashes. Rubric and thresholds were settled on baseline or dev outputs, never a treated arm's. A FREEZE line no counted run has launched under may be replaced by a new dated, pinned FREEZE line, the old one kept beneath it; rule 9 counts from the line the first counted run launched under.

Rungs an experiment adds to `unattended:go`'s pilot ladder before the freeze:

- **Decode.** One step per arm: read the decoded tokens the model actually receives, and check that sampler and trainer log-probabilities agree.
- **Census.** Every arm at step 0, twice. A treated arm already ahead means broken data, or a claim that becomes "starts closer".
- **Pilot.** The first N steps of the full configuration on a seed no counted run uses; the counted runs start from step 0 after the FREEZE. Skim samples for degenerate output and work moved off the scored surface.

Criteria drift on contact with outputs: before the freeze, read every item the scorer fails on baseline and dev runs, and check any generated item set for enough items in each subgroup the prediction names. After it, a live run is never patched: stop, amend, rerun the pilot.

### Rule 8: run record

Every run has one record, written by the launcher or a script at launch and completed at exit. One commit per run: a counted run executes one commit on a clean tree (untracked files count), and its finished record is pinned on its own and never edited.

```
at launch: run_id, parent_run_id, plan@commit or pinned hash, prereg and its pinned hash, launch verdict and its pinned hash, arm, label (confirmatory/exploratory/screening),
           commit, tree (`git status --porcelain` output, empty for a counted run), command, config_resolved,
           models with revisions (base, checkpoint, adapter init, judge, generator; substitutions),
           hashes (train, dev, sealed, scorer, judge_prompt), seeds, env_lock, hardware, caps, launched_by, started
at exit:   ended, end_reason (completed/kill rule/cap/crash), cost
```

- Build the launcher before the first rung, so exploratory runs leave records too.
- Run folders are git-ignored or outside the repository, so one arm's record does not dirty the tree for the next; each finished record is pinned in its own commit with `git add -f`, or by hash.
- Log per item the verbatim input, output and raw judge output, and per step the validity, refusal and length rates.
- After a resume, verify that no frozen stage was regenerated and that cached results are not empty.
- What an agent says ran is a claim: read every diff that touches measurement.

## Rules 9–13: the result

### Rule 9: nothing moved after the freeze

Nothing the FREEZE line or the prereg record names has changed, except by a dated amendment in the human's own words, reported beside the number. No trials, samples or rejudging were added after a result, except the two cases its checks.md entry allows (a scorer defect fixed by amendment, a failed step rerun).

### Rule 10: scores read

A scorer, judge, metric or prompt that is new, changed or meeting a new kind of output (a treated arm's is one) has had a sample of its scored items on these runs read by someone not given the hypothesis, ending in a verdict from that reader, or from the human who owns the experiment, of "fit to quote".

- A failed probe can print the hoped-for outcome, and an empty output can look like "no": compare raw records with the rendered view.
- Give `evals:spot-check` the run IDs of every treated arm, and check that its sample covers each contrast the claim credits.

### Rule 11: declared denominator, beyond noise

The number is the preregistered metric over its declared denominator, with an interval or every seed's value, and the untreated arm and simple baseline beside it, and the all-items rate too where arms can differ in the denominator (attempts, parsed, not refused). A difference is claimed only if it exceeds rule 4's floor and, with seeds as the unit, every treated run lies on the same side of every untreated run, three or more a side; with items as the unit, for a claim about these checkpoints on these items, its paired interval excludes zero; a null only if the positive control passed, with the largest effect its interval excludes or, with seeds as the unit, a positive control that cleared the floor in the same way. Where every arm sits at the metric's floor or below the simple baseline, nothing is claimed.

- With a handful of seeds, draw every run and report the range ("range of three", not ±); never "significant".
- With items as the unit, cluster standard errors on the unit of randomization and pair on shared items: samples of one item are not independent.
- Report the effective denominator, the items on which the arms actually differed, and whether the result survives the other reasonable ways to aggregate.

### Rule 12: confirmatory or exploratory

Confirmatory means labeled so at launch, run on a commit descended from the FREEZE commit, prereg record closed, and every rule met, or waived other than rules 2 and 7. Anything else travels with the word *exploratory* and cannot pass or fail a bar or pick an arm, though a screening run may nominate one for a counted run not yet launched.

- The pilot, or the seed that decided whether to buy more, is exploratory and out of the tally.

### Rule 13: the sentence

As it will be quoted, its comparator, unit and scope are the artifact's; it credits only what a control isolates; it claims no more than the contrasts that met rule 11; and a preregistered guard or kill that fired is quoted with the number.

- The usual slips, found by setting the rebuilt sentence beside the plan's claim: "beats random" when the number was against the untreated arm; the treatment credited when the matched control did as well; "closer to the target" when the metric showed "shorter". Never lift a favorable line from a section whose verdict was a miss.

## Sign-off

At launch and at quote the designer launches one fresh agent with this brief, unaltered, and nothing else: `You are the supervisor of <experiment> at <launch|quote>. Load lab:experiment, read Sign-off and checks.md, launch no agent. Experiment folder: <path> @ <commit>. Sentence to be quoted: <verbatim, at quote>, in <path or link of the draft it will appear in>. Waivers and amendments: <for each, where it was sent: transcript path and line, or channel link | none>. Open everything yourself; return the Verdict block.` The brief and the reply are appended verbatim to `signoff.md` in the experiment folder and pinned; every reply is appended, NOT SIGNED included, and asking again without changing the evidence earns nothing: the earlier verdict stands; beside each number quoted, the report gives that file's last verdict at quote on that number's sentence, and how many verdicts on that sentence came before it. Where no fresh agent can be launched, the designer's own pass is labeled a self-review and signs nothing.

The supervisor launches no run and fixes nothing; it reruns checks (fixtures, hashes, intersections). Open the evidence yourself: a summary is not evidence, and evidence you cannot find is not met. "n/a" needs a reason. No other rule is applied.

### Not met

One unmet rule blocks sign-off. At launch the supervisor refuses the counted run, and says the design may run as exploratory when rule 5 is met, rule 8's launch record exists (its missing fields named) and the treated arm scores no sealed item. At quote it refuses any use of the number beyond "exploratory, unsigned". It signs nothing "with caveats". Mark each unmet rule *record* when the thing was done and its evidence is unpinned or in the wrong form, and *claim* otherwise: a missing control, floor, prediction or reading is *claim*.

The ways out: meet the rule and ask again; get a waiver; or stop and report the rule, the evidence opened and what it showed.

Only the human who owns the experiment gives a waiver, naming the rule, and it counts only when the supervisor can open their own words for it: their message, opened where it was sent (the session transcript file or the channel), never a transcription; a commit counts only in a repository where no agent commits under the human's name. A one-word approval counts only with the message it answers, and only when that message asks for nothing else and gives each rule and its reason. A line an agent wrote is a request. A waiver is recorded as `WAIVER <rule>: <who>, <date>, <reason>` in the plan and beside the result, and quoted with the number; with rule 2 or 7 waived the number travels as exploratory.

### Verdict

```
Supervisor: <experiment>, <launch|quote>, <date>, plan@<commit or pinned hash>, runs <ids or names>
1 One difference: met / NOT MET (claim) / NOT MET (record) / n/a (reason); <evidence opened, what it showed>
… a line per applicable rule: claim blocks first, then record blocks, then met; rules 1 and 11 get a line per contrast
Amendments, deviations and waivers: <what, who, date, where recorded>
Sentence signed (at quote): <the number as it will be quoted>
SIGNED / SIGNED WITH WAIVER / NOT SIGNED: <unmet rules, what would meet each>; at launch: may run as exploratory, yes or no
```

## The record and its tool

The prereg record is one JSON file per contrast (a design with controls has several), frozen before the run and scored after it, and owed on consequence, not cost: the question, the bar, the decision per outcome, the arms and what varies between them, each metric with its denominator, a `[low, high]` prediction per arm and metric, the mechanism and the surprises. It is pinned before any treated output on the items the counted run scores, never committed with the results. Its tool is `prereg.py` in this directory; the commands (`new`, `open`, `stamp`, `parity`, `close`, `ls`) are in checks.md, "The commands".
