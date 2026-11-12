---
name: experiment
description: "The craft of designing, running and reading one ML experiment (a fine-tune, an RL or rejection-sampling run, an LLM eval or judge) so that its number means what it will be quoted as meaning and meets lab:supervisor's rules: the choices and traps that turn a clean-looking comparison into a confound, a blind instrument or an empty null. Use for \"/lab:experiment\", \"design this experiment\", \"what do you think of this design?\", \"set up this ablation\", \"what controls do I need?\", \"how many seeds?\", \"is this null real?\", before a paid training or eval run, and when a surprising number is about to be quoted or built on. Not for the rules and the sign-off (lab:supervisor), the preregistration record (lab:prereg), deciding what is wanted and the cap (swarm:brief), large or unattended runs (swarm:go), validating an LLM judge (evals:judge), reading a sample of scored items (evals:audit), or evals of skills and plugins (`claude plugin eval`)."
---

# lab:experiment

An experiment has no oracle for "does this mean what we think?", so its design is the checker. `lab:supervisor` holds the thirteen rules a design and a result must meet, and signs or refuses. This skill is how to meet them well: under each rule number, the choices and the traps, in the supervisor's vocabulary. Read the rule and its `checks.md` entry there first; nothing here repeats either. [templates.md](templates.md) has the plan page, the read and the report.

Every experiment gets a plan page and a written prediction; a small one buys fewer rungs, not less design. Every hypothesis, bar, rival and kill rule gets a code name on the plan (`H_FASTER`, `BAR_STEPS`, `RIVAL_LENGTH`, `KILL_DIVERGE`), defined once, never renamed, cited by every later file. A stop with the facts is a good outcome.

## Order of events

One folder per experiment, where the project's data policy allows. Inside `swarm:go` this skill designs the experiment piece, and go's attack, pilot ladder and report replace the same steps here. By hand:

1. **Frame.** `swarm:brief`, unless a brief is frozen: bring back the question, the bar with its denominator, the cap and the search record. If its search or a cheap check settles the question, that check is the experiment: a dated prediction, the result, stop.
2. **Read the harness,** before designing: scorer or reward code, a few full traces, where seeds enter, whether a held-out verdict can reach reward or training data, each checkpoint's provenance, your own earlier runs and why each died. Decide where the plan, prereg record and run records will be pinned: private data kept out of a repository needs its hash log before the first file is written.
3. **Design** the plan page ([templates.md](templates.md)) from the sections below.
4. **Attack.** `check:attack` on the plan page, packaged with the scorer or reward code and a few raw untreated traces. Close its findings, say in one line what will run and what it should cost, and run it. Nobody approves the plan.
5. **Untreated first.** On baseline and dev outputs only: the instrument checks, `evals:judge` for an LLM judge a bar reads (bring back its record), the floor runs, the positive control. Settle rubric and kill thresholds here.
6. **Predict.** `lab:prereg`: open and pin the record before a treated arm produces anything on the items the counted run scores. Treated smoke and pilot runs come after it and stay exploratory.
7. **Freeze and launch.** The FREEZE line, then `lab:supervisor` at launch: bring back SIGNED or the unmet rules. Ask it once earlier against a dry run's record, while a *record* block is still cheap to fix.
8. **Counted runs,** arms interleaved in time. `swarm:loop` for unattended work against a machine check.
9. **Read,** in the fixed order, with `evals:audit`; bring back its verdict.
10. **Quote.** `lab:prereg` close; `check:claims` on the draft report, the headline rebuilt from raw logs by a fresh agent; then `lab:supervisor` at quote, on the sentence as it will be written. `figure:make` draws it.
11. **Report,** the user's decisions last; then an amendment, a new plan or a stop.

A stop with the facts is a good outcome at any step: a positive control that fails, or a floor wider than the effect hoped for, is a finding.

## Start from the sentence

Before choosing arms, write the sentence you hope to quote, and the one for each other outcome: null, worse, inconclusive, no arm clears. Every word has to be bought: the comparator by an arm, the causal noun by a control that isolates it, the verb by what the metric measures, the scope by the models, seeds and items actually run. Rule 13 holds the final sentence to this, so strike now any word the design does not buy.

- **Null picture.** Sketch the figure you would see if the treatment did nothing, noise band drawn in, from the analysis script run on a synthetic null. If it cannot be told from the figure you hope for at the planned n, the design cannot answer the question.
- **A null has to be designed.** State the smallest effect worth detecting and show the design could have seen it: a positive control of about that size, and n to match. Find where the untreated arm sits on the metric before buying treated arms: with every arm at its floor, rule 11 allows no claim, a null included.

## Rule 1: one difference

- The reused baseline, trained last week on another commit, is the commonest break. Price its retrain into the plan from the start.
- Whatever made an arm's data is a knob: a generator, selector or best-of scorer upstream of an arm has a model and a commit.
- The usual failure is every arm at a setting (learning rate, most often) tuned on one of them. With no budget to tune per arm, fix it and narrow the claim, or show the gap at both ends of a plausible range.
- What a config diff cannot show: a continued adapter against a fresh one (match rank and optimizer reset, or merge each arm's adapter into its weights and start all fresh); a shared token cap, which truncates the longer arm more; anything installed in one arm only; an ablation whose arms remove unequal amounts.
- Prove parity by construction where you can: strip the treatment from the treated arm's inputs and show the remainder reproduces the untreated arm's, token for token.
- A treatment that bundles several changes (new data, more exposure, different behavior at sampling) is one difference only in name. Add a control that removes each part (the treated checkpoint with the mechanism off at sampling is the cheapest), and word the claim to the comparator it credits.
- For a break you cannot remove, write the share of the gain it could explain.

## Rule 2: prediction and denominator first

- Predict the mechanism as well as the number: which items should carry the gain, where the control should tie, what would surprise you. Then a hit or a miss tests why.
- A rate conditioned on something the treatment changes (attempts, parsed outputs, non-refusals) flatters the arm that does it rarely. A speed claim is steps to a threshold per run, the threshold still holding at the next eval with guard rates no worse than at step 0, censored at the horizon.
- Keep the treated arm dark until the record is pinned: do plumbing and instrument rungs on the untreated arm, or on items outside the counted set.

## Rule 3: controls

- Rivals come from traces: the rival that explains a result is usually found after it. Read untreated outputs and the scorer's code before listing rivals.
- Rivals to consider by default: ordinary capability, a signal supplied in the input, output length, a substitution only this judge rewards, one component's effect mistaken for the joint one. A mitigation ("the judge is another model family") is not a control.
- Add a constant-output arm, and "no action" where it exists. If it scores well, the harness measures something else; if every arm sits below it, there is nothing to compare.
- A scorer sanity check (its two ends separate) is not a positive control: a sampling fault that puts every arm at the floor passes it and reads as a null. For a training treatment, train an arm on a planted signal it must learn (copying the target will do), and write its pass before running it. Run it before the treated arms; if it fails, nothing else is worth buying.
- Where the claim names a mechanism, the condition with it switched off must score near zero. Where the behavior is rare, fix the allowed count in advance: 0 of n only bounds a rate below about 3/n.
- A multi-sample or multi-agent method (debate, self-correction, best-of-N) meets its simple baseline at a matched token budget: independent samples and a majority vote, or independent drafts and a judge's pick.

## Rule 4: noise floor

- Measure the floor before buying treated arms: it sets kill thresholds and n. Price it first: the baseline seeds often cost more than the treatment and are the first thing cut. If they do not fit the cap, run shorter with more seeds, when the effect still resolves inside the shorter horizon.
- Decide at design time what the claim will span. If the budget cannot buy three training seeds, word the claim now as "these checkpoints on these items".
- Three seeds a side make a figure, not a test: no one-sided rank test of 3 against 3 goes below p = 0.05; 4 against 4 reaches about 0.014.
- With items as the unit, choose n by power analysis from earlier variance on this eval and the smallest effect worth acting on; at a fixed n, state the smallest effect it can detect. Never invent an effect size or compute power after the fact. A pilot prices the run; it does not estimate the effect.

## Rule 5: leakage and held-out

- Dev drives curves and gates, and stops being held out once it has steered a decision. Sealed is generated after training or kept untouched. Start the exposure ledger (which runs scored which pack) with the first run; rebuilding it later is the slowest check there is.
- Routes a split does not close: generated training data that paraphrases the target (a rationale written after seeing the answer); failure reports that echo gold labels to an optimizing agent; the agent's memory, notes and config files; held-out logs the next run can read; a stopping rule that reads oracle labels.
- Out of reach is built, not instructed (`swarm:loop` has the mechanics): a read-only mount can still be read, and file tools bypass a shell-only sandbox.
- Hiding the scorer stops tampering, not attempts: read traces for them. A baseline that reproduces the answer verbatim is a leak until audited.
- Check in code that the held-out step the plan documents actually runs.

## Rule 6: instrument

- Use an LLM judge only where no code rule identifies the outcome (`evals:judge`; its "Valid for" line must cover the treated arm's outputs).
- Fixtures passing is not validity. Before the freeze, score baseline and dev outputs and look: do the fixture's pass and fail bracket where the arms sit; does the score track output length or format; do constant output and "no action" score below real work? A scorer can pass both fixtures and still rank by length where the arms sit.
- Hand-authored sets flatter scorers. Build fixtures from real items (a known pass made by minimally editing one), with negative controls where nothing should fire and a synthetic set whose known counts scorer and summarizer must reproduce through label remapping and shuffles. A null on an eval that never contains the hazard says nothing about a safeguard.
- Decide how cheats and errors score before any exist. Report illegitimate successes scored both ways; dropping them removes the hardest items. Test the cheat detector on a seeded cheat; its rates are lower bounds. Give output budgets room for hidden reasoning, so the scored answer is not cut off.
- Judge bias between arms: tell the judge extra length is not merit; a version that is a superset of the other cannot be blinded, so use a per-edit check that rejects when unsure; outputs identical across arms are a free bias probe. A model trained against a judge is scored by a held-out judge from another model family that reads the visible reply.
- Prompts: a prompt whose wording could move the result gets at least three variants of different stance, picked on dev and confirmed on held-out against the incumbent. A pick that ties its runners-up there is unconfirmed.
- Agentic evals: the candidate sees no eval words (eval, test, judge, rubric, benchmark) and no sibling arm's directory. Grade from what the transcript shows was opened or produced.
- A reward is an instrument under attack. Write the reward table: what the configured reward, penalties and blend weights pay each cheap strategy (refusing, invalid output, the shortest path to partial credit, moving work where the scorer does not look), computed by hand, and give it to the attacker. Sampling pays only where single attempts sometimes succeed: size the run from samples per step times the base pass rate, and scope any null to that horizon in advance.

## Rule 7: freeze

`swarm:go`'s pilot is the generic ladder. An experiment adds these rungs before the freeze; one that would change no decision is not bought.

- **Decode.** One step per arm: read the decoded tokens the model actually receives, and check that sampler and trainer log-probabilities agree. A renderer or format mismatch is the classic silent bug.
- **Census.** Every arm at step 0, twice. A treated arm already ahead means broken data, or a claim that becomes "starts closer".
- **Floor and positive control.** A failed positive control is plumbing or learning rate: no pilot until it passes.
- **Pilot.** The first N steps of the full run, gated at N so nothing is paid twice, with evals spaced finely enough to resolve the effect. It stays exploratory. Skim samples at fixed steps for degenerate output: token salad, length at the cap, work moved off the scored surface.

Criteria drift on contact with outputs. Before the freeze, read every item the scorer fails on baseline and dev runs, and check any generated item set for enough items in each subgroup the prediction names. After it, a live run is never patched: stop, amend, rerun the pilot.

## Rule 8: run record

- Build the launcher before the first rung, so exploratory runs leave records too. It enforces the cap and applies `KILL_` rules as written, and the agent can neither edit nor kill it. The fields found missing at quote are the ones nobody fills by hand: label, prereg pointer, parent run, launched-by, caps, cost, end reason, the exact cloud launch command.
- Log more than the record: per step, reward by component, validity and refusal rates, length, KL and zero-variance share; per item, verbatim input and output and raw judge output.
- After a resume, verify the freeze, that no frozen stage was regenerated, and that cached results are not empty.
- What an agent says ran is a claim: read every diff that touches measurement. Expect a crash "fixed" by a quiet hyperparameter change, and a retry reported without its failure.

## Rule 9: nothing moved after the freeze

- "A few more samples to be sure" is optional stopping. New counts are a new experiment.
- Iterating: one change per rerun. Keep a change only if it beats the incumbent by more than the floor, and keep the original as a candidate: the latest is not the best. A greedy loop on one seed that reuses its validation set proves nothing.
- Reproduce any earlier number before building on it. After a code change, rerun the step-0 eval and expect it inside the floor.

## Rule 10: scores read

- Read in the fixed order (templates): what decides whether to believe the number comes before the number you want.
- A failed probe can print the hoped-for outcome, and an empty output can look like "no": compare raw records with the rendered view before explaining anything.
- `evals:audit` on every treated arm's scores: give it the run IDs, check that its sample covers each contrast the claim credits, bring back "fit to quote".
- A jump usually means a shortcut or a leak: read traces before touching a knob.
- The human's read: about 30 passing items drawn by a stated rule, blind to arm and to any agent verdict, sorted into a taxonomy fixed in advance (exploit, omission, internalized, real effect, accident).
- Score the prediction last, number and mechanism: each `H_` a hit or a miss.

## Rule 11: declared denominator, beyond noise

- Items as the unit: standard errors clustered on the unit of randomization; paired tests on shared items (exact McNemar for pass or fail); Fisher's exact test for arms on different items; a Wilson interval for a pass rate at small n.
- Seeds as the unit: draw every run and report the range ("range of three", not ±). With a handful of seeds, never "significant".
- Report the effective denominator, the items on which the arms actually differed, and check that the result survives the other reasonable ways to aggregate.

## Rule 12: confirmatory or exploratory

- The pilot, or the seed that decided whether to buy more, is exploratory: drawn, labeled, out of the tally. A replicate counts only if it was launched after the decision to count it.
- A confirmatory miss is a result: quote it in the prereg form.

## Rule 13: the sentence

- Rebuild the sentence from the artifact and set it beside the plan's claim. Four words go wrong. The comparator: "beats random" when the number was against the untreated arm. The causal noun: the treatment, when the matched control did as well. The verb: "closer to the target" when the metric showed "shorter". The scope: a general claim from one base model, one seed and a metric at its floor. Never lift a favorable line from a section whose verdict was a miss.
- A flattering number gets its caveat first; cost sits beside the result; the user's decisions come last (templates).
