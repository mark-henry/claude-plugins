---
name: experiment
description: "Run one ML-lab experiment (a fine-tune, an RL or rejection-sampling run, an LLM eval or judge) with an airtight design, file by file: prior-art memo, dated plan page (codenamed hypotheses, bars and kill rules; prediction and null picture; matched arms, positive control, simple baseline, noise floor, leakage gates, validated instrument), attack before spend, priced slow-start ladder with a gated pilot, freeze, run record, fixed-order read, claim-first report, decision log. Use for \"/lab:experiment\", \"design this experiment\", \"what do you think of this design?\", \"has this been done before?\", before any paid training or eval run, when a run has no prediction, null or baseline, when setting up an ablation, dev/test split or preregistration, and before a surprising number is quoted or built on. Hands off to brief:lock, prereg:launch, evals:judge / audit / shadow, gauntlet:run / vote / auto, swarm:plan / loop, figure:make. Not for evals of skills or plugins: use `claude plugin eval`."
---

# lab:experiment

This skill exists so an experiment never burns an afternoon and ten million tokens on a question the field already answered, a comparison confounded from the start, or a number nobody can believe. An experiment has no oracle for "does this mean what we think?", so the design supplies one: a prediction written in advance, a null, a baseline, a confound check, and a denominator chosen pre-data. This is the front door for one experiment, intake to iteration; neighbors are named only for mechanics.

**Posture.** A forced, known-good pattern beats tendencies, and ceremony is welcome: tokens are cheap, wasted runs are not. Every use produces a plan page and a written prediction; there is no "too simple to plan" exit, only fewer ladder rungs bought. If the user names a method, use it. Evidence before claims: every "done", "works" or "better" arrives with the run ID, command or file that shows it. A stage you cannot point to did not happen. The human appears as roles and decisions, never a schedule.

## When it applies

- A paid run with no effect size, null or cheaper diagnostic, often with the winner already picked; a multi-arm design with no hypothesis, controls or per-arm prediction.
- An ablation "validating" a result while its arms remove unequal amounts; an RL reward whose partial credit could pay a shortcut.
- Work about to stack on a confounded or unreproduced result; a surprising number about to be quoted.
- "What do you think of this design?" is a request to attack it (stage 3); "has this been done before?" starts at intake.

A skill or plugin treatment goes to `claude plugin eval` [24], which runs a no-plugin arm beside it. Add planted positives the skill must catch and negatives it must leave alone, and keep eval words out of case prompts. The bare model may close the gap on a scaffold as models improve [habit], so a scaffold claim needs the bare arm, with an interval across runs. A sequence of unattended experiments is a loop (`swarm:loop`, or an autoresearch skill if adopted) whose every experiment follows this flow.

## The flow

One folder per experiment, kept where the project's data policy allows. Each stage receives the previous stage's file and writes its own before the next begins: contracts, attack surface and record at once.

```
experiments/<YYYY-MM-DD>-<slug>/
  prior-art.md   plan.md (dated; FREEZE line, amendments)   attack.md   ladder.md
  runs/<id>/record.json (launcher-written)   actions.log   read.md   report.md   decisions.md
```

| Stage | Receives → produces |
|---|---|
| 1. Intake | request → `prior-art.md` |
| 2. Design | `prior-art.md` → `plan.md` |
| 3. Attack, go-ahead | `plan.md` → `attack.md`, prereg record, verdict |
| 4. Ladder | approved plan → `ladder.md` |
| 5. Freeze, run | `ladder.md` → FREEZE line, `record.json`, `actions.log` |
| 6. Read | records → `read.md` |
| 7. Report | `read.md` → `report.md` |
| 8. Iterate | report, ruling → `decisions.md`; amendment, new plan or stop |

Each stage ends in a **Gate:** line; pass it before the next stage starts.

**Codenames.** Every hypothesis, bar, rival and kill rule gets a SHOUTY codename on the plan (`H_FASTER`, `BAR_STEPS`, `RIVAL_LENGTH`, `KILL_DIVERGE`); every later artifact cites it. Never rename one. Agents and humans track named requirements far better than numbered ones.

**Small steps.** Plan in concrete steps (file, command, check) so an attacker has something to hit; when a step shows the path is wrong, stop and request a re-plan, with a description of what went wrong.

**Launch** means any paid run or any run of a treated arm; free reads, unit tests and checks over existing code and counts are not launches.

**Order of events.** The prediction is written before any treated-arm output exists, smoke rungs included. The attack precedes any long interview or preregistration. Rubric, noise floor and kill thresholds are settled from baseline, step-0 and dev outputs only. The freeze comes after the pilot read and before the first counted run.

**Hard gates.** Each is a stop.
1. Intake launches nothing.
2. No launch before a filled plan page and a written prediction.
3. No paid run above your review threshold before an answered attack; no paid run of any size without an approved price, unless already authorized.
4. No counted run before the freeze.
5. No aggregate quoted, compared to a bar or used to pick an arm before an audit, when its eval, judge, metric, prompt or scorer is new, changed, or meeting a new distribution (every treated arm's outputs are one).
6. No "done" without evidence.

**Logs,** from the first minute, written by the launcher or script because nothing else enforces them. Plan changes are amendments on the plan with an entry in `decisions.md`.

```markdown
## <YYYY-MM-DD> <decision | Ruling (agent's call without the human) | Result (human ruling on a result)>
Evidence: <run ids>  Options: <...>  Choice: <...; accepted | killed (KILL_<NAME>) | redirected>  Why: <reason>
By: <human | agent: mechanical / taste>  Codenames: <...>  Expect: <...>  Cost: <spent; if wrong>
```
`actions.log`, append-only: `<time> | <command> | <run id> | <$ / tokens> | deviation: <none | what, why>`

## 1. Intake: `prior-art.md`

Receives the request; produces `prior-art.md`. Nothing launches. Read the brief once for the claim, again for the numbers, then open raw material: scorer or reward code, logs, a few full traces. Summaries say what someone concluded; traces say what the model does. Brief helpers from this. Inventory the harness read-only: where seeds enter, what is logged per item or rollout, whether held-out verdicts can reach reward or training data, whether anything counts dollars; get each checkpoint's provenance (data, steps, renderer, continued or fresh adapter) from whoever produced it. Goal, bar or denominator undefined: write down the interpretation you are taking and flag it; the bar is frozen after the attack (stage 3), not by a long interview now.

```markdown
# Prior art: <question>  (<YYYY-MM-DD>)
In the field's words: <naive idea = the field's name for it>
First rung: <can a test, lookup, benchmark or read of code and counts settle it? command, result | ruled out: why>
Own earlier work: <run ids, abandoned attempts, why each died | none found>
| Approach | Layer: tried-and-true / new-and-popular / first principles | Who, when, maturity, scar tissue, incentive | [V]/[S]/[M] | done, answer X / partly / open | Applies here? (scale, base model, adapter, data) | Why it failed |
Searched: <angles and sources covered; what was out of scope>
Premises: <each claim about model behavior: measured (model, date) | unevidenced>
Verdict: answered (short plan and report, then stop) | partly (design the open part) | open
```

- **First rung.** A machine check beats opinion: run the system to learn how it behaves, quick-test a capability the docs are silent on, turn a taste dispute into a small check on real items. If a check or applicable prior art settles it, the experiment is that check: write a short `plan.md` (question, dated prediction, the check or citation) and a `report.md` with the result, then stop. The rung is cheap; it is never an exit from the record.
- **Three layers,** then the field's name for the idea. Map every failed method with why it died: usually the landmine. "Answered" stands only if the answer applies at this scale, base model and data. An "open" verdict names what was searched: no hit is not novelty, and memory is not prior art. For width, a research skill (e.g. deep-research). Tags: [V] read in the primary, [S] search result only, [M] memory.
- **Premises are not evidence.** Quick agreement with the user is suspect: take the outside view; a long conversation of shared assumptions is not grounding. Model-behavior premises are measured or labelled unevidenced. Date model-dependent findings and re-check them on current models; structural ones (statistics, prices, human attention) do not age.

**Gate:** a verdict per approach with tagged sources; the first rung run or ruled out with a reason.

## 2. Design: `plan.md`

Receives `prior-art.md`; produces one dated page before any launch. One experiment answers one question; a piece needing two kinds of checker is two experiments. Each field is a threat to validity; an empty one is unchecked.

```markdown
# Plan: <slug>  (<YYYY-MM-DD>; draft | attacked | frozen <date> | closed)
Question: <one>   Decision it informs: <action per outcome>   Prior art: <verdict>
Claim: <one sentence: metric, denominator, threshold, comparator, horizon>
Hypotheses: | H_<NAME> | hypothesis | prediction per arm (interval; probability) | where the gain should concentrate; where the control ties | surprise if | written <date> |
Data: <datasets or benchmarks and why chosen; any subsample or synthetic data, its size and rule; who assigned the split>
Bars:       | BAR_<NAME> | metric | pass bar | direction | denominator | what a miss means |
Null picture: <the figure if the treatment does nothing, noise band drawn in>
Outcomes:   | class | test assigning it | next action |  (incl. inconclusive, none clears, worse)
Rivals:     | RIVAL_<NAME> | explanation | control arm or decomposed eval |
Arms:       | arm | differs in | matched on | parity breaks; share of gain they could explain |
Knobs:      | knob | scientific / nuisance / fixed | value, or tuning budget per arm |
Controls:   untreated <arm>; simple baseline <what>; trivial <what>; positive <what>; floor <allowed count>;
            matched-budget <what | n/a: reason>; third arm <later | n/a>
Noise and n: <how measured; seeds and items per arm, fixed now; why that n>
Instrument: <checker and why; hashes; known pass/fail; seeded positives, decoys (n, how made);
             judge TPR/TNR; bias controls; candidate blinding; how cheats score>
Leakage gates: <each: yes/no, evidence>     Held-out: <tiers; hashes; exposure ledger>
Prompts: <variants, dev pick, held-out confirmation>     RL/RFT: <reward table; base pass rate; horizon>
Kill rules: | KILL_<NAME> | condition in numbers | set from | action |
Caps: <$ and tokens, launcher-enforced>; iteration cap <n, no reset>; debug attempts per idea <= 3
Ladder, price: <rung: price, kill rule, decision>; total with contingency   Analysis: <script path, before results>
Agents: <who, tier, brief>   Amendments: <date - change - reason - codenames - how reported>
```

**Claim.** Fixing metric, denominator and threshold stops the metric being picked after the data. A ratio conditioned on a behavior the treatment changes flatters the arm that does it rarely: plot the unconditional rate beside it, in raw counts. Every ratio names its comparator: in one published system (2025), multi-agent runs used about 15x the tokens of a chat and single agents about 4x a chat, so roughly 4x a single agent by implication [7]. A speed claim ("converges faster") is steps-to-threshold per run, where the threshold must still hold at the next eval with guard rates (validity, the behavior's own rate) no worse than at step 0, censored at the horizon; report area under the curve to the horizon beside it.

**Prediction, null, outcomes.** Predict per arm and metric, dated, an interval with a probability (for a discrete outcome, a probability per class) if you will commit [habit]; without a prior nothing can surprise you. Name where the gain should come from (which items or categories), where the control should tie or win, and what would surprise you: a hit or miss then tests the mechanism, not just the number. A smoke rung gets a one-line expectation. Draw the null with measured noise before results. Fix the outcome classes and the test assigning each, including "no arm clears", "worse" (keep the original as an unlabelled candidate) and "inconclusive". Verdicts are confirmed, rejected or unresolved; no counterexample found is not confirmation. Judges and reviewers may reject every option or the framing; selection code handles "nothing eligible".

**Rivals.** Name what the claim must exclude (ordinary capability, a signal supplied in the input, output length, judge-specific substitution, a component-only effect mistaken for the joint one); each gets a control arm or a decomposed eval.

**Arms and parity.** Arms differ in one recorded thing. Check what travels with the treatment: a continued adapter against a fresh one (match rank and optimiser reset, or merge each arm's adapter into its weights and give every arm a fresh one; record which). A warm start (a continued checkpoint, seeded examples or demos) is its own arm or a recorded match, never a silent default; unequal amounts removed in an ablation; length under a shared token cap, which truncates one arm more (plot against tokens and KL, not only steps); context length; prompt or scaffold wording; compute (token use alone explained 80% of performance variance on one browsing benchmark in 2025 [7]); anything installed in one arm only. Run arms interleaved in time (alternating or randomised order in one window), never one after the other, so provider drift, cache warmth and rate limits fall on both. Name any break, the share of gain it could explain and whether it matters; `prereg:launch` runs the mechanical check.

**Knobs.** Scientific (its effect is what is measured), nuisance (its best value may interact with the treatment, e.g. learning rate: tuned separately for each arm so the comparison is fair) or fixed (held constant; the claim is conditional on it) [3]. Give each arm's nuisance search the same budget [habit]. The trap: every arm at a setting tuned on one. On a small budget, fix knobs and narrow the claim openly, or check the gap at both ends of a plausible range. An unclassified knob is an unchecked confound.

**Controls.**
- Untreated arm at the same settings and a simple baseline, always. In one field's reproduction study, all four papers claiming complex models beat logistic regression had leakage, and once it was fixed the complex models did no better [1]. A trivial input-independent control: if it scores well, the harness measures something else.
- A positive control that must succeed if the plumbing works, showing the manipulation was active; a null without one is a non-result, and is called that.
- Floor controls: accidents, with rare-event counts pooled across evals and the allowed count fixed in advance (0 of n bounds a rate only below about 3/n); and a mechanism-off condition (e.g. reasoning disabled) that must stay near zero, or the mechanism is not load-bearing.
- A multi-sample or multi-agent method (debate, self-correction, council, best-of-N, a new workflow) meets the simple baseline once at matched budget [8]: independent samples plus majority vote, or independent drafts plus a judge's pick for free text. On GSM8K with gpt-3.5-turbo (2023), at nine responses each (debate: 3 agents, 2 rounds), debate scored 83.0 and self-consistency 88.2 against 76.7 for one answer [6]; the authors attribute debate's gain to consistency across generations, not self-correction. Self-revision needs an external signal (tests, a verifier, ground truth). On your task assume neither wins: run the matched baseline as a cheap diagnostic on a few real inputs with a blind judge, then at the plan's n for any counted claim.
- A third arm (same data without the active ingredient) turns "this checkpoint" into "this treatment"; buy it once a two-arm gap exists.

**Noise and n.**
- Measure noise first: a step-0 census of every arm twice, an A/A run, or the unchanged baseline three to five times. Zero measured deviation is not zero uncertainty. The floor sets kill thresholds and the keep rule (stage 8).
- Runs are noisy, agentic ones especially: one run per arm decides nothing; report the spread. A seed varies every source of variance (data sample and order, init), not just one [11]. One context playing several judges or replicates is one sample; a reused context is not a new attempt. Prefer evals whose signal (spread across models) is large against their noise (checkpoint-to-checkpoint jitter) [12].
- Fix seed, trial and samples-per-item counts before confirmatory runs; no extra trials, resampling or rejudging after a result. Several samples per item fixed in advance, or scoring from token probabilities, cuts within-item noise [2].
- Three seeds a side make a figure, not a test [11]. By exact arithmetic, a one-sided rank test of 3 against 3 reaches at best p = 0.05, 4 against 4 about 0.014, and 2 of 3 against 0 of 3 gives p = 0.2. Shorter runs with more seeds can cost the same, if the effect still resolves inside the shorter horizon.
- Items as the unit: choose n by power analysis, with variance from earlier eval data and the smallest effect worth detecting; at a fixed n, state the minimum detectable effect [2]. Never invent an effect size or compute post-hoc power [23]. A few-item priced pilot prices the run; it does not measure the effect for power.

**Instrument.** Checker first, width second, human last: name the checker before you spend; never scale generation or agents onto work no machine checks. A flawed verifier lets scale optimise the wrong target; a known-good reference turns an undiagnosable failure into a diff. Buy verification, not volume.
- *Metric.* Code check where a rule identifies the outcome, LLM judge only where judgment is needed. Binary over 1–5 scales; outcomes ("was the appointment made?"), not technical implementation ("did the tool call succeed?") or composite dashboards [5]. Tallies and validation in code, every dropped row logged. Hard constraints are gates, apart from graded preference. Fix in advance how illegitimate successes score; report them scored as failure and as success. Dropping them is not neutral: it removes the hardest items. The cheat detector is part of the instrument: test it on a seeded cheat and report detected rates as lower bounds. Majority agreement is the weakest check, and a margin means confidence only when voters' errors are roughly independent (same-model voters are not): spot-check unanimous items; never swap a validated judge for a cheap vote.
- *Both poles.* A known pass (minimally edit a real item so it should pass; confirm with the rule checker) and a known fail; seeded positives and decoys (how many, how made, what a decoy pass proves); a synthetic fixture where scorer and summariser reproduce known counts through label remapping and shuffles (red-green for the scorer); parser edge cases; mutation tests both ways. Judges agreeing all on one class prove nothing. Real items mined from actual use (paraphrased where private) from the first round, plus negative controls where nothing should fire: hand-authored sets flatter scorers. A null on an eval that never contains the hazard is no evidence a safeguard is unneeded.
- *Judges.* An LLM-produced metric is validated with `evals:judge` before its numbers are quoted; its TPR and TNR travel with them; revalidate on any change of model, prompt or distribution.
- *Judge bias between arms.* Neutral shuffled labels, both orders, blind to arm and incumbent; one judge sample is noisy. Self-preference is contested: where the judge shares a model family with one arm's generator, say so, and use a judge from neither family where available. Judges favor longer, more complete text: tell the judge extra length is not merit; a superset version cannot be blinded at all, so use a per-edit check that rejects when unsure. Identical outputs across arms are a free bias probe. A model trained against a judge is scored by a held-out judge from another model family that also reads the visible output. The judge prompt holds only criteria the human stated (audit for injected ones); the judge writes its own ideal first and sees clean artifacts, never the producer's reasoning.
- *Candidate blinding (agentic evals).* No eval words (eval, test, judge, rubric, benchmark, candidate) the candidate can see; project-shaped fixtures; no sibling arm directories; grade from what the transcript shows was opened or produced.
- *Out of reach.* Scorer, test items and held-out set sit out of the agents' reach and sight: another user, a container, or a sandbox runtime that denies reading them, not a readable read-only mount (a shell-only sandbox is not enough: file tools and other servers bypass it). The launcher, not the agent, runs the scorer, verifies hashes before accepting a result and enforces caps and kill rules; the agent can neither edit nor kill it, and its reported pass is a claim. A scorer that runs candidate-written code (tests, builds, cleanup scripts) runs it isolated and only reads results: code executed as the supervisor's user can kill it or rewrite outputs. An instruction to lock is not access control. In 2025 METR saw a frontier model modify tests and scoring code, still doing so on one task in most runs when told not to cheat [14]; its 2026 report found frontier models tampering with scoring code against explicit instructions, more often on harder and longer tasks, where unattended runs operate [15]. Hiding the scorer stops tampering, not attempts: read traces for them, and check a surprising gain for tampering. Mechanics: `swarm:loop`.

**Leakage gates**, adapted from [1]'s taxonomy, each yes or no with evidence:
- *Classic:* a split exists; no preprocessing, feature selection or duplicates across it; no temporal leakage; train and test independent; no illegitimate features; test drawn from the distribution of interest.
- *Agent era:* eval targets and future text cannot reach training data or prompts, including through generated data; failure reports shown to an optimising agent echo inputs and predictions, never gold labels; held-out outputs and logs are unreadable by later runs; the agent's own memory, notes and config files carry nothing from gold labels or held-out items into later runs (audit them); no stopping rule uses oracle labels.
- *One item per call* for LLM baselines, judges and generators, always over time-ordered data: batching leaks earlier answers, numbering and context. Each subject sees only its own item. With a cached prefix it costs little more, so cost is never the reason to batch.

Anything too good, or a baseline reproducing the answer verbatim, gets a leak audit before it is believed.

**Held-out tiers.** The training scorer gives reward. Dev drives curves and gates, and stops being held out once it steers decisions. Sealed is generated after training or kept untouched, scored once by the supervisor, not the optimising agent, at stop. Sets are disjoint by seed and checked by hash; an exposure ledger records which runs and models saw each. Never read, paste or summarise held-out items; tune on dev only. Verify in code that a documented held-out step actually runs.

**Prompts.** A prompt choice that matters gets at least three variants with different stances, picked on dev and confirmed on held-out against the incumbent. Say when a pick was made on test items; a dev pick tying its runners-up on test is unconfirmed. Length and wording can dominate: in one practitioner's report, expanding a 103-word loop prompt to 1,500 words made the agent "slower and dumber" until it was cut back (anecdote, 2025 model) [10].

**RL / RFT.** Build a *reward table*: what the configured reward, penalties and blend weights pay each cheap strategy (refusing, invalid output, the shortest path to partial credit, moving work where the scorer does not look); attack it before paying for steps. Check the *base pass rate*: sampling pays only where single attempts sometimes succeed, and needs a cheap verifier. A fine difficulty knob and graded judge strength (rule, weak model, strong model) keep signal off zero. Mix synthetic data with real, verifier-filtered. No self-revision without an external signal (shown on 2023 models [6]; recheck on current ones); select across the chain. Size steps from evidence (published step counts; expected signal per step = samples per step x the behavior's base rate); scope any null to that horizon in advance. Log zero-variance groups.

**Kill rules and caps.** Numbers, written before launch, thresholds from measured noise. A dollar or token cap enforced by the launcher (no standard kill switch exists; build one). An iteration cap that cannot be reset; three debugging attempts per idea. A refused reservation ends the step: no retrying, no splitting a call to slip under. An API or rate-limit error stops a priced run, or is retried and logged by the launcher; errored items are never scored as fails.

**Gate:** every field filled or "n/a: reason" (guidance text is not content); prediction dated; codenames assigned; a control per rival; every knob classified; arms differ in one recorded thing; noise method and counts fixed; each leakage line answered; the checker named with the known pass and fail it must get right; scorer, eval sets and judge prompts out of reach and hashed.

## 3. Attack and go-ahead: `attack.md`

Receives `plan.md`; produces `attack.md`, a `prereg:launch` record when triggered, and a verdict in `decisions.md`: **go**, **fix first** (with fixes) or **do not run** (with reason). Steps run in order, each by agents other than the plan's author.

```markdown
# Attack: <slug>  (<YYYY-MM-DD>; plan.md@<commit>)
Reviewer: <Opus | Fable, and why; fresh context; files given>   Lens: <all | correctness | leakage | confounds>
| Flag | Evidence | Severity | Codenames | fixed (how) / accepted (reason) / rejected (evidence) | Rechecked by |
Diagnostic: <command, cost, result, what it settled>   Completeness questions: <...; answers>
Verdict: go | fix first (<fixes>) | do not run (<reason>)
```

1. **Attack.** Before any paid run above your review threshold (about $10 if none is set), a fresh-context reviewer attacks plan and predictions. The reviewer is Opus by default; save Fable, the strongest and scarcest reviewer, for the largest experiments (the biggest spend, or the run hardest to repeat). It attacks: confounds, leakage, denominator, noise floor, parity, judge validity, researcher degrees of freedom, the null, already answered (own earlier runs, literature) or a known answer to re-run, a cheaper diagnostic. Its answer gates the spend; a larger run gets a second, independent attack. Brief it with facts and files, not your hypothesis; never say what not to flag. Single lenses work (correctness, leakage, confounds). A decision-changing flag is re-checked by a second fresh agent. Named reviewer unavailable: stop and ask. Mechanics: `gauntlet:run`, `gauntlet:vote` (discrete designs), `gauntlet:auto`.
2. **Cheapest diagnostic,** required: a roughly one-dollar test of the mechanism (score and leak-check a few traces per arm; one sample per arm), before any full run; unauthorised money is asked for alone, with its price. Skip the heavier check once it answers.
3. **Lock and preregister.** `brief:lock` for any loose term, then a `prereg:launch` record citing `plan.md#BAR_<NAME>` whenever the number will meet a bar, be reported or choose an arm: consequence, not cost.
4. **Completeness check** before unattended agents run it: a fresh reader who cannot ask lists only questions where a wrong guess would matter. Completeness is not correctness; it never replaces the attack.
5. **Price and wait.** Loading this skill asks for a plan, not approval to spend: present plan and price and wait unless already authorised. A hand-back or notification is never approval; unattended, write the gate item to `decisions.md` and stop. Contingency about 1.5x [habit]: lengthening outputs raise cost, and identical agentic runs vary in cost (on one coding benchmark the costliest of four runs averaged about 2x the cheapest, at worst 30x in tokens [9]); unknown charges visible; reconcile against actual cost. Price agentic arms as a range (typical and worst run), not a point times the contingency. Shared money: three estimates at three effort sizes, each set against the next-best use of the money; owners choose. Optional checks come with cost and what they would show; pending decisions as a numbered list with a recommendation (`court:hold`). If a gate changes an arm, bar, budget or pattern, re-present the whole plan, not a delta.

**Gate:** every flag fixed, accepted with reason or rejected with evidence; the diagnostic ran; the prereg record open where triggered; the price approved or already authorised.

## 4. Ladder: `ladder.md`

Receives the approved plan; produces one row per rung. Each rung buys the right to climb the next; if a rung changes no decision, don't buy it. Rungs are exploratory, never part of n; the counted run is not a rung.

```markdown
| Rung | Checks | $ est/actual | Stop or redirect when | Decision it changes |
| 0 free | code read; reward/scorer tests; mocked run, every exit path; a stub model over every real row (not a sample); scorer once before treatment | 0 | an exit path untested; an empty or malformed prompt; an unpriced arm; scorer already passes or is broken | fix plumbing; stop |
| 1 instrument | known pass/fail; seeded positives; decoys; fixture counts | cents | known pass fails, known fail or decoy passes | rebuild scorer |
| 2 dry run | one step per arm; decoded tokens; sampler/trainer log-probs agree | ~1 | decoded input differs from plan; truncation | fix renderer, budget |
| 3 census | every arm at step 0, twice | <$> | treated broken or ahead | fix data; claim becomes "starts closer" |
| 4 positive control | must succeed | <$> | it fails | plumbing or learning rate; no pilot |
| 5 samples | 1 per arm, then ~10; each reply read with its label | <$> | any reply or label not yet read | fix prompt, parser, label |
| 6 bulk smoke | ~20 calls; parse yield | <$> | yield below <x> | fix parser, prompt |
| 7 pilot | first N steps of the full run, gated at N; a few samples per arm skimmed at fixed steps | <$> | KILL_<NAME> fires; BAR_<NAME> missed; degenerate output (token salad, length near the cap, work moved off the scored surface); a gain from surface substitution alone | continue, change, stop |
```

- **Cheap rungs.** Mocks through every exit path (done, stall, cap, broken baseline, already passing). A strong-model stand-in may drive real rows for crashes and plumbing; its yield is not the target model's (re-measure at rung 6), and it cannot reveal a confound or leak. Every arm has a price; output budgets cover hidden reasoning (e.g. at least 8k tokens for reasoning models, so the answer the scorer reads is not truncated); print the exact retry prompt. A format or renderer mismatch is the classic silent bug. Fix the seed, check loss at init, overfit one batch [4].
- Smoke every code path and arm; keep a 1–10% fast mode of every slow check. Before bulk generation, check quota and models with your quota or roster skill; log yield live.
- **Pilot** = the first N steps of the full run, gated at N so nothing is paid twice, eval spacing fine enough to resolve the effect. The run it starts stays exploratory. A missed bar stops it without asking. Don't watch the curve. Extrapolate the full run's price from the pilot's measured per-item spend, with an interval; above the approved price plus contingency, stop and re-present before the freeze.
- **Settle.** Criteria drift on contact with outputs [5], so settle rubric, metric definition, noise floor and kill thresholds from baseline, step-0 and dev outputs only, never the pilot's treated outputs. Before the freeze, read every item the scorer fails on baseline and dev runs and every decoy or seeded-positive miss. Read a generated or curated item set before freezing it: per-stratum counts sufficient for every subgroup the prediction names, controls present, nothing private or leaked.

**Gate:** both instrument poles and the positive control passed; the noise floor is a number; rubric and kill thresholds settled.

## 5. Freeze, then run: `runs/<id>/record.json`

Receives `ladder.md` with the pilot read; produces the FREEZE line, run records and `actions.log`.

**Freeze.** After the pilot read and before the first counted run, date a FREEZE line on the plan naming commit, item-set, scorer and judge-prompt hashes and the final kill thresholds (item sets were frozen before any arm ran; the protocol is committed before any result). After it, any change to a bar, arm, item set, decoy, stop rule, blinding, scorer or judge prompt is a new experiment or a dated amendment with its reason, reported as such. Never patch a live run: stop, amend, rerun the pilot.

The launcher writes the record at launch, never by hand; it refuses a dirty tree, verifies hashes, enforces the cap and applies KILL_ rules as written.

```json
{"run_id": "", "parent_run_id": null, "plan": "plan.md@<commit>", "codenames": ["H_..", "BAR_.."],
 "label": "confirmatory | exploratory", "commit": "", "config_resolved": "<path>", "command": "",
 "models": {"base": "<name + snapshot>", "checkpoint": "<id + producing run, data>",
            "adapter": {"rank": 0, "init": "fresh-zero | continued <id>"},
            "judge": "", "generator": "", "reviewer": "", "substitutions": ["<asked X, ran Y, why>"]},
 "hashes": {"train": "", "dev": "", "sealed": "", "scorer": "", "judge_prompt": ""},
 "judge_temperature": 0, "seeds": [], "env_lock": "<lock or image digest>", "hardware": "<accelerator type, count>", "started": "",
 "launched_by": "<who; agent's brief>", "caps": {"usd": 0, "tokens": 0},
 "ended": "", "end_reason": "completed | KILL_<NAME> | cap | crash", "cost": {"usd": 0, "tokens": 0}}
```

- **Per step:** reward by component, validity and refusal rates, judge scores, length, KL, entropy, gradient norm, zero-variance share, tokens, dollars. **Per item:** verbatim inputs and output, reward components, raw judge output with prompt version, choice and runner-up with confidence.
- **Immutable:** rollouts, run records, scorer versions, eval sets, the dated plan; never rewrite git history a run record points at. **Versioned:** analysis, figures, reports. Failed and killed runs are kept; a relaunch gets a new ID pointing at its parent. Every derived dataset (generated data, eval packs, holdout draws, teacher answers) gets a manifest beside it at generation time: source commit, generating code and command, generator model and revision, prompt recipe, judge and its decisions, time. Without one it is untrusted for new experiments.
- **Any tooling** if: one resolved config per run; figures from a script taking run IDs; judge calls cached by snapshot, prompt and input hash; a rerun buildable from the record alone. Promise the same inputs and attributable execution, not bitwise determinism.
- **Analysis first:** while it runs, write the analysis and figure script against census data and a synthetic null.
- **Confirmatory or exploratory** on every result. The pilot or seed that decided whether to buy more is exploratory: drawn, labelled, out of the tally [rare]. A replicate counts only if launched after the decision to count it.
- **Resume is a hazard.** Keep the experiment's place on disk in a ledger that survives compaction. After a resume, verify the freeze, check no frozen stage was regenerated and cached results are not empty; read raw per-agent records before diagnosing.
- Unattended grinding against a machine check: `swarm:loop`.

**Gate:** each run ended for a recorded reason and has its launcher record; frozen hashes verified, including after any resume.

## 6. Read: `read.md`

Receives run records; produces `read.md` in fixed order: whatever decides whether to believe the number comes before the number you want, so the audit precedes the held-out headline.

```markdown
## Read: <run ids>  (<date>)
- [ ] Ran as configured: config diff, cost, truncation
- [ ] Instrument ran: parse yield <k/n>; missing counted apart from negative
- [ ] Samples read per arm (rule: ...); validity, refusal, length
- [ ] evals:audit (hard gate 5): <verdict>
- [ ] Training scorer, then held-out headline: BAR_<NAME> <value, n/N, interval>
- [ ] Effective denominator; components isolated; mechanism checks
- [ ] Blind packet for the human: <path, n, rule>
- [ ] H_<NAME>: hit / miss / half; confirmed / rejected / unresolved; leak audit if too good
```

- **Did it run?** A failed probe can print the hoped-for outcome; an empty output can look like "no". Compare raw records with the rendered view before "fixing" a defect.
- **Traces before knobs.** When a rate surprises either way, have readers profile the failures; read the clean cases before publishing a clean or yield number. A jump usually means a shortcut or leak: check eval code and arm sizes, then the judge's reasons on disputed items.
- **Audit:** `evals:audit` on any number covered by hard gate 5, and whenever a rate surprises; its verdicts are a prescreen, never labels.
- **Statistics.** Items as unit: an interval with every score, standard errors clustered on the unit of randomisation, paired tests on shared items [2]; for pass rates at small n a Wilson interval, never a normal approximation near 0 or 1; two arms on different items, Fisher's exact test; on shared items, exact McNemar (paired). Seeds as unit: each run drawn, each value or the range reported ("range of three", not ±) [habit]. With a handful of seeds, don't write "significant": Agarwal et al. [11] advise interval estimates over dichotomous significance claims (Henderson and Bouthillier test significance, but with many runs). Counts carry denominators; winners carry margins; a split is reported as a split.
- **Attribution.** Papers often misattribute where gains come from [13]: credit only the component an ablation isolates, with baselines tuned as hard as the treatment; report the effective denominator (items where arms actually differed); check the result survives reasonable aggregation choices.
- **Mechanism and the human's read.** Causal checks (paraphrase then rejudge, counterfactual edits, ablation); confirm checkpoint and task version, since passes can be accidents. Prepare about 30 passing items, drawn by a stated rule (not picked by an agent), blind to arm and to any agent verdict (agent suggestions anchor the expert), for the human to sort into the taxonomy fixed in advance (e.g. exploit, omission, internalised, real effect, accident) before seeing the prescreen. Agents prescreen; the human rules; a human read stays beside any automated judge.
- **Provisional labels** before expert labels exist: one judge, then repeated rolls, then a multi-model cohort with agreement statistics, each step recording what it proves. Marked provisional; never a stand-in for the expert's.

**Gate:** parse yield, audit verdict, statistics on declared denominators, effective n and the prediction's hit / miss / half, all stated.

## 7. Report: `report.md`

Receives `read.md` and the records. Before release, someone who has not seen the first analysis recomputes the headline from raw logs [rare], and an outside reader reads the report and five or more raw traces and tries to break the claim, with the lenses used on the plan. Close the `prereg:launch` record; figure via `figure:make`.

```markdown
# <claim in one sentence, with n>   [confirmatory | exploratory]
prereg <file>: predicted <X>, got <Y> (<n/N>)        (or: exploratory)
<figure: claim as title; every seed drawn; "one seed" in the title if so>
What ran: <arms, steps, seeds, items; $ and tokens (this run; cumulative on this question); run ids>
Checks: passed <BAR_/KILL_>; failed <...>   Data: <subsampling, synthetic data disclosed>   Limits: <judges, TPR/TNR; samples per item; effective n; biases>
Not excluded: <RIVAL_>   Would change my mind: <...>   Killed: <run id: KILL_<NAME>>
Next: <proposal, price>   Traces: <~10 links, rule: ...>; examples on request
Needs your decision: <numbered, with recommendation>   (non-empty = not finished)
```

- A flattering number gets its caveat first. Cost sits beside the result; whether spend pays off across experiments is `swarm:review`'s question.
- **Nulls** get the same format and prominence, with scope and positive control ("no change in BAR_X by step N at these settings, one seed; positive control passed").
- **Examples:** link traces picked by a stated rule and offer examples in one line; no item text inline unless asked.
- **Every number carries provenance:** denominator, comparator, conditions (dataset, model, n), and whether measured, estimated (reconstructed after the fact, e.g. cost from billing logs), approximate (taken from a summary, not the primary) or unverified (only cited by a subagent). Where sources disagree, give both with their conditions. Unmeasured stays qualitative; inference is marked apart from observation; unevidenced claims are listed apart; cited figures are checked against the primary (a swapped pair can invert a finding); overstatements are retracted openly. Watch for quoted paraphrase, secondary as primary, anecdote as rule, bound as practice, a renamed metric.
- "Done, unverified" is not "done". Keep what was learned apart from what should change.

**Gate:** recomputation matches; the outside reader's objections answered or listed as limits; the prereg record closed.

## 8. Iterate: `decisions.md`

Receives the report and the human's ruling; produces a `decisions.md` entry, then an amendment, a new plan or a stop.

- **Keep rule.** Keep a change only if it beats the incumbent by more than measured noise; rerun borderline results on the same seeds. A heuristic, not a significance test across many adaptive trials.
- **One change per rerun,** read each time. A defect (a bug, or a breach of a stated design rule) is fixed at once with a regression check and a dated amendment; after the freeze it takes the stage-5 path, and results measured with the defect are rerun or rescored, not kept. A judgment critique from one case is logged, not acted on: a prompt changes when two or three critiques share a cause, the change names them, and a failing case is rerun as a regression check. First live runs of a component: `evals:shadow`.
- **Latest is not best:** keep the original as a candidate; select by eval. Add a costlier mechanism only after its failures appear. Anti-pattern: a greedy loop on one seed reusing its validation set.
- **Reproduce before building** on any earlier number, yours or anyone's. Rerun the step-0 eval after code changes; it must land inside measured noise.
- **A wasted run becomes a check,** red-green: fails on the defect, passes on the fix (if the fix exists, disable it briefly). A lesson goes in its cheapest durable form (a check, else a line in a skill), only if a future reader would otherwise repeat it.
- **Stop and consolidate** when the work becomes a growing pile of tool; want evidence from real outside use first.

**Gate:** the next step logged as an amendment, a new plan or a stop; any number it builds on reproduced from its record.

## Agents

| Alone | With the human's sign-off | Never |
|---|---|---|
| read code, logs, traces; write analysis, plotting, test code; run anything free; launch an approved config inside a launcher-enforced envelope; apply written kill rules; draft logs, figures, reports | spend outside the envelope; change reward, scorer, judge prompt, eval set, kill rule or plan; relaunch a killed run; delete; post to others | edit a held-out judge prompt or eval set; route held-out verdicts into reward; edit a test or scorer so something passes; choose which runs appear in a figure |

Grey zone: **mechanical** choices decided silently and logged; **taste** choices decided with a recommendation, surfaced at one gate; a **challenge** to the human's stated direction never auto-decided. The human owns the question, claim, predictions, metric, threshold, kill rules, spending, what a result means, when to stop, and the report's signature. Anything a machine can check goes to the machine first.

- **Brief** like a new colleague: goal, what is ruled out, files, scope, budget, forbidden surfaces, what evidence to bring back. Pair every prohibition with a sanctioned exit ("if gate X fails after honest attempts, stop and report"): a stop-report is a success, because a cornered agent satisfies the letter of a gate. Never hand over the conclusion you want checked. Fan-out sizing: `swarm:plan`.
- **Independence.** Replicates, proposers and reviewers get fresh contexts without your preferred answer or sibling outputs. Listing candidates anchors proposers; an "or something better" hatch collapses diversity. No agent filters, rewrites or ranks its own candidates before the next verdict-holder (judge, tally or human) sees them. A checker gets your hypothesis as one possibility, tries to disconfirm its own first answer, and may answer "unknown". Decisions that matter sample several independent trajectories; to test a multi-agent method, seal a single-pass answer first. Agents agreeing with agents is not evidence.
- **Hand-backs are claims.** Establish what ran from records; rerun a claimed fix's test; check two or three claims per session against raw logs; read every diff touching measurement. Claims return with command and artifact path. Expect a crash "fixed" by a quiet hyperparameter change, a retry reported without the failure, a summary sunnier than the log, a test edited to pass, early victory. Self-application is not evidence.
- **Why** (dated; recheck on current models).
	- A 2025 study of AI-scientist systems found inappropriate benchmark selection, data leakage, metric misuse and post-hoc selection bias. An LLM auditor (Gemini 2.5 Flash) classified balanced items, half flawed, with 55% accuracy from the paper alone and 82% with trace logs and code, so the authors recommend requiring logs and code with the paper [16].
	- In 2026, persona-primed analyst agents reached opposing conclusions on the same data by selective reporting, and 86% (137/160) of their analyses passed an AI methodological review: selection is invisible to final-report review [17].
	- An agent hardcoded answers that leaked to it through failure reports [18].
	- A pre-release o3 reward-hacked in 39 of 128 RE-Bench runs but in 0.7% of HCAST runs; RE-Bench's scoring function was visible, which METR names as one possible cause. On one task it still hacked in most runs when told not to [14].
	- Agents declare success despite obvious failures [19]. Hence: keep logs and code, isolate by construction, never let AI review be the last check or an agent choose which runs appear.

## Red flags

| Thought | Reality |
|---|---|
| "Small run, no plan needed." | Write the page; buy fewer rungs. |
| "I know which arm wins; just train the variants." | Then the prediction and null take a minute. |
| "The ablation validated it." | Did the arms remove equal amounts? |
| "We can build on that result." | Not while its flagged confound stands; reproduce it. |
| "We already know the answer." | Then the memo cites it in five minutes. |
| "The user agrees, so the premise holds." | Agreement isn't measurement. |
| "The design is fine; skip the attack." | The author is the one person who can't attack it. |
| "Both arms use the same config." | Same file, different adapter init, token cap or wording. |
| "Three seeds all agree." | p = 0.05 at best: a figure, not a test. |
| "The pilot looked good, count it." | It decided the purchase: exploratory. |
| "A few more samples to be sure." | Optional stopping; new counts, new experiment. |
| "Batch the judge calls, it's cheaper." | Not with caching, and batching leaks. |
| "The judges agree." | All on one class? Where are TPR and TNR? |
| "The scorer is read-only; the agent was told." | Readable is gameable; an instruction is not a boundary. |
| "The reward pays the right behaviour." | Write the reward table first. |
| "Great result." | Shortcut or leak until audited. |
| "Tweak the rubric after seeing the treated arm." | Baseline and dev only; then an amendment. |
| "Tweak the config, keep it running." | Stop, amend, rerun the pilot. |
| "The agent says it passed." | A claim. Read the record; rerun the check. |
| "This case needs a prompt fix." | One case is logged; act on two or three. |
| "It's a null, nothing to report." | Same format, with its positive control. |
| "The null shows the safeguard is unneeded." | Did the eval contain the hazard? Positive control? |

## Neighbors

Each is named at the moment it applies; bring back its artifact, not its summary. `brief:lock` (locked bar), a research skill (tagged prior-art claims), `prereg:launch` (record, parity, tag), `gauntlet:run` / `auto` / `vote` (attacked plan, discrete picks), `evals:judge` (TPR/TNR), `evals:audit` (audit verdict), `evals:shadow` (logged live cases), `swarm:plan` (briefs), `swarm:loop` (exit reason, held-out result), `swarm:review` (cost per accepted result), `figure:make` (the figure), `court:hold` (rulings), your quota or roster skill (quota, models), `claude plugin eval` (scaffold evals).

## Sources

[habit]: one careful practitioner's practice, not settled standard. [rare]: what the careful do and most skip. (unverified): not yet checked against the primary.

1. Kapoor and Narayanan, "Leakage and the reproducibility crisis in ML-based science", *Patterns* 2023: https://arxiv.org/abs/2207.07048; REFORMS: https://reforms.cs.princeton.edu/. Leakage taxonomy, simple baselines.
2. Miller, "Adding Error Bars to Evals", 2024: https://arxiv.org/abs/2411.00640. SEM, clustering, paired tests, power.
3. Google Research, Deep Learning Tuning Playbook: https://github.com/google-research/tuning_playbook. Knob classes.
4. Karpathy, "A Recipe for Training Neural Networks", 2019: https://karpathy.github.io/2019/04/25/recipe/. Sanity gates.
5. Husain and Shankar, LLM evals FAQ: https://hamel.dev/blog/posts/evals-faq/; Shankar et al., "Who Validates the Validators?", 2024: https://arxiv.org/abs/2404.12272. Binary judges, criteria drift.
6. Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet", ICLR 2024, Table 7: https://arxiv.org/abs/2310.01798.
7. Anthropic, "How we built our multi-agent research system", 2025: https://www.anthropic.com/engineering/multi-agent-research-system. Token use, variance, token multiples.
8. Snell et al., 2024: https://arxiv.org/abs/2408.03314; Tran and Kiela, 2026: https://arxiv.org/abs/2604.02460. Matched compute budgets.
9. "How Do AI Agents Spend Your Money? Analyzing and Predicting Token Consumption in Agentic Coding Tasks", 2026: https://arxiv.org/abs/2604.22750. Cost spread across identical runs (OpenHands, SWE-bench Verified).
10. RepoMirror, 2025: https://github.com/repomirrorhq/repomirror/blob/main/repomirror.md. The 103-word prompt.
11. Henderson et al., 2018: https://arxiv.org/abs/1709.06560; Agarwal et al., 2021: https://arxiv.org/abs/2108.13264; Bouthillier et al., 2021: https://arxiv.org/abs/2103.03098. Seed variance and reporting.
12. Heineman et al. (AI2), "Signal and Noise: A Framework for Reducing Uncertainty in Language Model Evaluation", 2025: https://arxiv.org/abs/2508.13144. Eval signal-to-noise.
13. Lipton and Steinhardt, 2018: https://arxiv.org/abs/1807.03341; Recht et al., 2019: https://arxiv.org/abs/1902.10811. Misattributed gains; fresh test sets scoring below reported ones (attributed to harder images, not reuse).
14. METR, "Recent Frontier Models Are Reward Hacking", Jun 2025: https://metr.org/blog/2025-06-05-recent-reward-hacking/
15. METR, Frontier Risk Report (Feb–Mar 2026), May 2026: https://metr.org/blog/2026-05-19-frontier-risk-report/
16. Luo, Kasirzadeh and Shah, "The More You Automate, the Less You See: Hidden Pitfalls of AI Scientist Systems", 2025: https://arxiv.org/abs/2509.08713.
17. Miao, Pritchard and Zou, "The Agentic Garden of Forking Paths", 2026: https://arxiv.org/abs/2607.01507.
18. Askarbekuly et al., "Autoresearch with Coding Agents: Generalizers and Metric-Maximizers on Quran Recitation Data", 2026: https://arxiv.org/abs/2607.18064.
19. Trehan and Chopra, "Why LLMs Aren't Scientists Yet: Lessons from Four Autonomous Research Attempts", 2026: https://arxiv.org/abs/2601.03315.
20. driveline's autoresearch skill: https://github.com/drivelineresearch/autoresearch-claude-code. Scorer lock, trivial control, keep rule, untouched test, caps.
21. gstack's eval-plan: https://github.com/garrytan/gstack/blob/main/eval-plan/SKILL.md. The closest prior art, strong on process and money, weak on inference; its guarded failure modes (an unpriced arm admitted at $0, bars changed after a priced call, prompt-less rows reaching the paid run, reservations past the cap) shaped the dry-run, pilot, freeze and cap rules, decoys, fixtures, candidate blinding and held-out exposure record. Elsewhere in gstack: Search Before Building (ETHOS.md §2) and the mechanical / taste / user-challenge decision classes (autoplan/SKILL.md).
22. Every's compound-engineering: https://github.com/EveryInc/compound-engineering-plugin (one plan file with requirement IDs carried through stages, ternary validator verdicts, rejection as a first-class outcome); obra's superpowers: https://github.com/obra/superpowers (saved plan files handed between stages, small-step plans, hard gates, red-flag tables). Codenames for requirements: [habit].
23. K-Dense AI, scientific-agent-skills: https://github.com/K-Dense-AI/scientific-agent-skills (no post-hoc power; repetitions and acceptance rule agreed before search). Orchestra Research, AI-Research-SKILLs: https://github.com/Orchestra-Research/AI-Research-SKILLs (flag single-run results).
24. Claude Code plugin evals: https://code.claude.com/docs/en/plugin-evals
