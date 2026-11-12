# Evidence for adversarial:toolkit

What the sources and this pack's own runs found, with the record of corrections and the numbered source list, moved out of the body of `adversarial:toolkit`. Headings are the sections of the skill each passage came from.

## S1. Before work starts: an idea, a question, a request, a fix that keeps failing

### Check first [route zero; the "none" route; a check beats opinion]

- **Evidence (self-use, small n, all on this kit's own problems).** A question whether a supervisor script parses a passing count with stray whitespace was routed to "just test it" (one agent, seconds), and following that found a real bug: leading whitespace made the loop exit as if the check were broken. A literal routing test found a flaky-eval request (pass rate moved between runs) routed to a score audit that cannot see a difference between two runs; a slow-job request reaching a multi-million-token build-off when it needed a profiler; "which database?" and "does library X support Y?" routed to votes that one agent with the constraints, or a lookup, would settle; "was the spend worth it?" routed to opinion instead of counting cost and kept results; a heavyweight route grabbing a "big if true?" question that five minutes reading the eval code would settle. A sandbox question was settled by running the attack, not by reading the docs. History: a "step 0: if a check settles it, stop" rule was proposed, withdrawn when ceremony was ruled welcome, then reinstated as the first rung that still leaves a record.

### Prior-art check ["this has been done before and the answer is X"; search before building]

- **Evidence (self-use).** In a blind routing comparison, on an open "ways to get the model to think before it writes" request, only the arm that went to prior art first scored 5 of 5; arms that brainstormed from memory scored 1 to 3. Prior-art results that arrived after a design ontology was built changed three of its conclusions (a name collision, the field's vocabulary, cross-model voters). One pack reports a fix rebuilt a day after upstream merged it.

### Idea attack [cheap attack on the idea before the interview]

- **Evidence.** None measured; adopted because it shaves human involvement.

### Gap probes [pressure test of a proposal]

- **Evidence.** Adopted from a public compound-engineering plugin; no measured comparison.

### Integration check [combination effects]

- **Evidence.** None measured; lifted from a single-repository planning workflow.

### Settlement test [what may be re-litigated]

- **Evidence (public-pack report, relayed).** In one pack, a synthesis reinserted preference-only feedback against a settled decision; after correction, fresh-session routing checks on two host models discarded that preference while retaining a verified ownership defect [51]. These were routing checks, not full-review evidence, with outputs read candidate by candidate; this is not this toolkit's self-use.

### Premise attack [attack the premise; framing challenge; "should this exist at all"]

- **Evidence.** The author of this skill first declined one pack's mandatory premise step ("seems wise but I have not actually run into this class of problem"); it is kept, with narrow triggers, because in the one high-stakes routing test the decisive insight came from a premise lens, and a source-currency check refuted the author's own premise (self-use). One pack's first premise table reportedly found 1 FALSE and 3 UNVERIFIED claims among 27 [42] (relayed).

### Grounded expert simulacrum

- **Evidence.** One use generalised (self-use): a simulated senior researcher marked the agent plan attack as [habit], about ten minutes, with a peer attack taking hours gating larger runs; that reading is the source of the plan attack's cost line (S2). No measured comparison.

## S2. A plan about to spend

### Plan attack before spend [attack before spend; experiment vet; pre-mortem; design red team]

- **Evidence.** Origin case, generalised: a paid distillation round came out null on a flaw foreseeable at design time (a teacher scoring data it had trained on), which a strong-model design review would have caught. One grounded critique by a strong model of a paid-experiment design surfaced four cheap-to-check problems before spend: a held-out monitor never shown to pass a clean case; a conditional rate that flatters the arm that rarely attempts; three versus three seeds that cannot attain an exact one-sided rank-test p below 0.05; a head start that could pass for faster learning (self-use, unverified at the time). A blind routing judge's ideal answer to "what do you think of this design?" was a pre-spend attack by fresh agents, not an interview. Honest limit: little rigorous evidence exists for design red teams as a method outside maths and QA benchmarks.

### Bar attack [attack the success bar before it is locked]

- **Evidence.** None measured.

### Sealed prediction [commit before you look; preregistered prediction]

- **Evidence (self-use).** All three early router-pilot log lines were hits (uninformative). The only preregistration record found in one audit was post hoc with empty predictions. A driving agent's written prior before a currency fan-out turned out wrong, which the written prior made visible. A routing comparison predicted 8 of 12 held-out wins (range 6 to 10) and observed 8.

### Controls that make a result attackable [positive control, floor, noise floor, parity, null picture]

- **Evidence.** Kit boundary tests use the positive-plus-sanity pattern: a boundary test once first printed "host process ALIVE" because the harness had failed to run the attack at all (self-use).

## S3. Choosing among options

### Sealed own answer and sealed single-pass control

- **Evidence.** It was the one unique asset of a retired propose-attack-judge route, and was moved to every multi-agent method as an option (self-use).

### Blind vote [jury; self-consistency; majority voting; ensemble; a council without the chairman]

- **Evidence.** Self-use: with "lean toward a stance but propose the best answer if clearly better", all four proposers proposed the same parser and no vote ran; assigning stances to argue still gave four identical proposals; asking each for two or three candidates gave 12 candidates merging to 3, and all three tallies agreed. A mocked tally test exposed that eligibility was applied to the final ranking but not to Condorcet. A minimal live smoke (3 options, 3 voters) agreed on all three tallies and correctly ruled out a constraint-breaker. Published councils (read in code) give every reviewer the same order, let each model rank its own answer, and have a chairman synthesize instead of pick. Self-use (one low-stakes cache-choice smoke, three voters): the selector chose a plain vote over the predicted vote-then-chain because the options were familiar and refinement would roughly double cost; one option won Borda 6 to 2 of 6 possible with all three tallies agreeing, but all three voters worried about cache-key handling, so the route was defensible but borderline, not evidence that refinement was unnecessary. Independent draws plus a tally against debate: see the evidence block in the debate card.

### Vote then challenge

- **Evidence (self-use, n = 1).** The voters' worries were passed to the chain and its first step answered exactly that worry; 13 agents, about 770k tokens, 5 minutes; the prediction hit; the owner ruled it a pass.

### Build-off [diverge then converge with prototypes; bakeoff]

- **Evidence.** None measured against a cheaper route. A January 2026 vendor case study reported lock-based coordination reducing 20 workers to the throughput of 2 to 3, and flat peer swarms drifting into risk-averse churn, while planners, non-coordinating workers and a separate judge with periodic fresh restarts worked better [55] (vendor case study, not a controlled comparison); it supports keeping proposals independent, not a claim that this build-off is validated.

### Blind judge [pairwise or pick, with bias controls; LLM-as-judge]

- **Evidence.** Swapping candidate order alone let Vicuna beat ChatGPT on 66 of 80 queries; the authors' fix (Balanced Position Calibration) judges each candidate in both positions [22]. Length-controlled win rates were proposed to correct verbosity bias [24]. Self-use: in a routing comparison the judge scored the arm with the longer description higher even when all arms picked the same route, and the driver had told the judge the owner "hates over-ceremony", which the owner never said; part of one arm's loss reflected that injected preference. One pack's blind re-judge of its review comparison gave +3.5 percentage points (95% interval -9.6 to +16.7; the earlier unblinded comparison was +2.4, also spanning zero); the underlying runs used a stub system prompt and an unmasked control, so the pack does not count it as evidence of component benefit [42]. A vendor research-agent evaluation (June 2025) began with about 20 real queries, where early effects were large, and its most human-aligned setup was a single rubric-judge call returning both a 0 to 1 score and pass/fail on factual accuracy, citation accuracy, completeness, source quality and tool efficiency [30]; a task-specific exception, not a reason to replace actionable binary verdicts everywhere.

### Best of N with a selector [generate many, then verify; many-sample hunt]

- **Evidence.** One practitioner's o3 hunt found a known bug in 8 of 100 runs on a 3.3k-line slice (66 misses, 28 false positives), 1 of 100 on 12k lines, and a novel kernel use-after-free at about one real finding per 50 reports, for about $116 over 100 runs; on the smaller known-bug slice, Sonnet 3.7 found it 3 of 100 times and Sonnet 3.5 0 of 100 [11]. In one theoretical setup with a perfect verifier, best-of-N needs about 1/delta samples against 1/delta squared for majority voting, where delta is the probability gap between the correct answer and the runner-up [10]: conditional asymptotic bounds, not a measured guarantee for an imperfect LLM judge. A March 2025 test-framework migration moved about 3,500 files in six weeks, against a manual estimate of about 1.5 years, with a staged per-file error-feedback loop (company report, not a controlled speedup) [60]. For a generated-data selector, an EMNLP 2025 study trained a machine-generated-text detector and importance-resampled toward likely-human text, which prevented collapse and beat human-only training in that setup, not as a general guarantee [63]. A November 2026 search found no head-to-head comparison of best-of-N selected by an LLM judge against a single coding attempt; bug-hunt yields and perfect-verifier theory do not establish it.

### Adversarial debate and competing hypotheses (narrow use)

- **Evidence.** Debate's regime: non-expert judges reached 76% (LLM) and 88% (human) with debate against 48% and 60% baselines [6]. Vote against debate: on GSM8K with gpt-3.5-turbo (2023), debate as 3 agents x 2 rounds, at 9 responses self-consistency (majority vote) scored 88.2% against debate 83.0% and a single answer 76.7%; at 6 responses 85.3% against 83.2%; debate edged a vote only when the vote got fewer responses: debate round 1 (3 agents, 6 responses) 83.2% against self-consistency over 3 responses 82.5% [1]; the authors attribute debate's gain to consistency across generations, not self-correction (their attribution). Over 7 benchmarks with 5 agents, majority vote averaged 0.769 against 0.738 for the best debate variant on Qwen2.5-7B (0.724 against 0.699 on Llama3.1-8B; comparable on Qwen2.5-32B); majority-biased update rules lifted debate over vanilla debate but still not above the plain vote (best 0.763 against 0.769, Qwen2.5-7B); and the best debate variant beat the vote on several non-arithmetic subsets (MMLU Professional Medicine, Formal Logic, CommonsenseQA, HH-RLHF), so the vote's average lead comes mostly from arithmetic and GSM8K [2]. Within debate, voting as the decision protocol beat consensus on reasoning tasks (+13.2% average; 0.2 to 26.4 points by task) and consensus beat voting on knowledge tasks (+2.8% average; 1.3 to 4.9), with Llama 3 8B agents; more rounds slightly hurt, more agents helped, and independent drafting first helped (+3.3%) [3]. Debate does not reliably outperform other strategies [4]. A currency pass judged "voting over debate" structural but the numbers dated to small models. Vendor documentation recommends competing hypotheses for debugging; the evidence argues against debate as the verdict source.

## S4. Improving one artifact

### Challenge chain [gauntlet; relay of fresh challengers; iterative refinement; sequential revision; critique-and-revise]

- **Evidence.** Self-use: run on its own name, challenger 1 replaced the proposed name and challenger 2 kept that with a better description. On a skill draft (2 chains x 2 challengers plus merge) all four amended: keep the content, change the layout. On a three-skill pack both challengers kept the split and each found real defects the author missed (an unreachable script path, a claimed held-out run that never happened, logs with held-out results inside the worker's tree, trigger collisions); the second caught defects the first one's fix created (a liveness check that would treat a permission error as death; held-out logs readable by later agents), so depth two earned its keep. Challengers caught citation errors when given the evidence base, internal contradictions, and a document claiming behaviour its code lacked. Voters once found a winning version over-engineered. Literature: on MATH, one revision model converted about 38% of correct answers back to incorrect, and its authors selected across the revision chain with sequential majority or a verifier rather than taking the last version [7] (a setup-specific result, not a general flip rate for fresh challengers); vague feedback plateaus or reverses after a few turns while targeted prompts shift the intended axis [8]; intrinsic self-correction with no external signal lowered accuracy in 2023 (gpt-3.5-turbo-0613: GSM8K 75.9 to 74.7 and CommonSenseQA 75.8 to 41.8 after two rounds, 38.1 after one; GPT-4 also fell, GSM8K 95.5 to 89.0) [1], a finding this kit's own currency check rated "holds-weaker" (date it, keep the rule); with GPT-4 critiquing itself, accuracy fell on graph colouring (16% to 2%), Game of 24 and obfuscated planning, though it rose on plain Blocksworld (40% to 55%), while a sound external verifier helped everywhere (Blocksworld 87%) and plain resampling against that verifier kept most of the gain [9]. No study covers a relay of fresh, rewrite-allowed challengers as such; "keep with a defence" guards against sycophancy, degeneration of thought and correct-to-incorrect flips.

### Challenge then vote, original included

- **Evidence (self-use, one run).** Four lens chains each amended twice; five voters ranked four versions plus the original; the threat-coverage version won Borda 18 of 20 with 4 of 5 first choices; all three tallies agreed; every voter ranked the original last; 14 agents, about 840k tokens; the preregistered prediction hit. Every voter's worry about the winner named a gap a losing version had filled (a cheap resume-after-kill idea).

### Bounded graft [keep the best of the losers]

- **Evidence (self-use).** A single judge allowed to "combine" combined in all three runs of a propose-attack-judge route (for example A + B + C + E), so the final artifact was judged only by its author.

### Draft-off [independent drafts, blind pick, graft merge; for documents]

- **Evidence (self-use, two builds).** The judge found each draft strongest on a different axis and returned 16 grafts and about 40 defects in one build, 45 or more grafts and 27 defects in another; it caught rules narrowed or made absolute, an ordering contradiction, a fabricated figure that appeared in no source file, and a name colliding with a built-in. All three drafters had self-reported full coverage. The last-placed draft still contributed a key line. The sealed default draft and final three-way pick are new; their record is not yet in.

## S5. Reviewing finished work

### Fresh-context review [maker-checker; evaluator-optimizer; generator-verifier; per-task reviewer; outside break attempt]

- **Evidence.** One pack reports a fresh-reader pass found dense or meaning-shifted sentences in 13 of 19 rewritten skills that authors, three evals and two review bots had passed (relayed, unverified; its origin could not be re-found). Another pack's review skill (with its stop hook, measured together as one intervention; Opus 5.5) caught 22 of 84 blocking-bug opportunities (42 bugs over 33 units, 2 passes) against 3 of 84 for the bare model (+22.6 points, 95% interval +11.0 to +33.7) [42], on a suite later found to favour its own reviewer family (41 of 42 seeded bugs came from that family's reviews) [42]. It was a development suite, not a release evaluation; the result applies only to those 33 units at those settings [42]. AI-co-authored pull requests carried about 1.7x the issues of human-only ones (10.83 against 6.45 per PR; vendor, 470 open-source PRs, AI authorship inferred from co-author signals) [41]. One public pack reports that worker-spawned reviewers duplicated the controller's already scheduled task review in every session its maintainer observed (no counts, unverified) [43], which supports orchestrator-owned seats, not a claim that extra independent reviewers never catch anything; the same source prescribes per-task plus final review without any catch-rate, false-positive or per-task-versus-end-only comparison [43]. One writer's single fresh reviewer returned twelve corrections on a roughly 4,000-word synthesis (self-use). Freshness rescues a second look more than it beats a careful first one; see Independence for that weak evidence.

### Lens review [perspective-diverse reviewers; the red team after specialists]

- **Evidence.** Self-use (n = 1): a threat-coverage lens found an attack path no other lens saw (the check command runs agent-written code as the user); five independent lenses on one family of tools converged on the same top findings. One pack's leaner reviewer stack (one batched specialist) found 24 of 29 known blockers in replay against the control's 21, and 33 against 27 of 41 in a pooled round [42]. A self-use design for mapping a family of tools: evidence cards per tool (job, verdict-holder, relations, quoted lane drift, name fit, whether it earns its place), then independent classifiers building competing maps through knowledge-operation, lifecycle, authority, compute and an unassigned lens, a strong synthesiser writing the routing guide, and separate critics attacking routing, substantive simplicity and fidelity to code (launched, not yet evidence of success). For broad cleanup discovery rather than review of one artifact, independent surveyors over distinct slices return a ranked menu instead of one agent returning one cut; a self-use routing comparison found every description set missed that request, and the remedy is proposed, not validated. A November 2026 research search found no head-to-head data on how often multi-lens review catches real defects against false positives; that is a limit of the search, not proof no study exists.

### Outside voice [cross-model second opinion; panel with reconcile]

- **Evidence.** Several public packs run a second model family as reviewer or challenger by default (one turns outside review on by default [42]); that default is recorded and not adopted as a blanket rule. One public pack distinguishes document and code peers: document review has an unscoped whole-document sweep, while the code-review peer replaces the local adversarial seat without duplicating its brief or adding a whole-diff generalist [51]; this toolkit's outside-voice trigger mandates neither arrangement. The same pack's document review sends only its activated adversarial, product and security lenses to the outside family and keeps coherence, scope and feasibility on the host, on the stated rationale that the first three diverge more across families; it gives no comparative measurements, so this is bounded prior art, not a validated allocation rule or this toolkit's default [51]. A round-2 coverage checker caught a fixer adding "cross-family judge mandatory for every arm comparison", contradicting the rule in Independence (self-use). See Independence for the cross-family evidence.

## S6. Acting on findings

### Finding validator [adversarial verify; attack then validate; N refuters]

- **Evidence.** A many-sample hunt ran at about 1 real finding to 50 noise [11]. One vendor's vulnerability pipeline requires a proof of concept per report and uses a sanitizer that "perfectly separate[s] real bugs from hallucinations" (vendor). A security agent topped a public bounty platform's US leaderboard (2025) after about 1,060 submissions checked by automated validators and then by its human security team; 130 were resolved and 303 triaged, while 208 were duplicates, 209 informative and 36 not applicable (vendor figures; the vendor claims every submission was confirmed as real, which its own table contradicts) [48]. One open-source project ended its bug bounty in January 2026 under unvalidated AI reports, months after merging about 50 fixes from one researcher's AI-tool-assisted reports (autumn 2025) [47]. A separate security-research deployment reported autonomous discovery and reproduction of each reported vulnerability, with human review before submission (August 2025; secondary reporting) [65]: reproduction validates the technical claim, and review before third-party submission is a separate human gate.

## S7. A claim or citation about to travel

### Claim verifier [fresh claim check; evidence before claims; independent recomputation]

- **Evidence.** An overnight-port write-up says humans had to take the agents' ports "from 90% to 100%", though "Claude may claim that things are 100% perfectly implemented" [44]; a coordinator falsely reported all bugs fixed while one pull request merged past failing tests and was reverted (practitioner report); a showcase autonomous build was found by an outsider not to compile (34 errors) [50]. On the 2025 USAMO, every reasoning model tested claimed to have solved the problems, yet expert human graders gave all but one under 5% (one model 25%), and LLM graders inflated the same proofs' scores several-fold [49]; a public maths skill misquotes this as "85.7% self-verified drops to under 5%", merging it with an unrelated IMO result. Developers in a 2025 randomised trial were 19% slower with AI while believing themselves about 20% faster, and a 2026 follow-up still calls self-reports unreliable [36]. Self-use: a critic checking quotes against files caught a synthesis crediting a skill with a ranked ladder it did not contain, and another caught it misstating what the code passes to a vote; memory-based notes carried wrong figures after the draft was corrected.

### Citation verifier per source

- **Evidence (self-use).** 35 source readers over three agent-written skills: one source unfetchable, only 1 of 35 came back clean; nothing changed what to do, but several claims were stronger than their sources. On a merged draft: 25 sources, 59 claim checks: 23 supported, 24 partly, 7 unsupported, 5 could not check. On a third: 113 cited claims: 64 supported, 46 partly, 3 unsupported. The commonest defect is over-generalisation and misattribution, not fabrication. Caught: a comparison baseline (15x tokens was against a chat, not a single agent); a gain credited to the wrong mechanism; a design credited to a source that lacked it; "quotes" that were paraphrases or not on the cited page; a too-permissive safety claim; a house rule cited to a paper; one case study stated as general; a rule credited to a post that never states it; scout figures for two 2025-26 audits (see corrections on record). Readers also found a real design bug (a same-user agent can kill its bash supervisor). One verifier removed a claim that reused test sets caused accuracy overstatement (the cited study attributed fresh-test-set drops to harder images, not reuse); another corrected an inflated reproduction claim to its actual scope (all four examined papers claiming complex models beat logistic regression had leakage, and after correction the complex models did no better) and restored the source's term "technical implementation" in place of "activity".

### Source-currency check [does the finding still hold?]

- **Evidence (self-use).** 35 of 35 assessed: holds 25, holds-weaker 10, stronger-now 0, outdated 0, unknown 0. Structural advice held; what aged were 2023-25 numbers and model-failure anecdotes. The owner's hypothesis that current frontier models rarely reward-hack had no support (dated 2026 evidence pointed the other way), and only edits backed by a dated source were approved. The check also caught a skill contradicting its own cited source.

### Coverage checker per section or per source

- **Evidence (self-use).** Build one (559 harvested items): round 1 found 402 in, 95 pointer, 50 ruled out, 6 missing-relevant, 6 missing-not-relevant, plus 36 overlooked claims and 22 misstatements; round 2 found 0 missing but about 30 partial or misworded items and regressions introduced by round-1 fixes (including an unsourced rule contradicting a binding ruling), with round-two totals of 451 in, 89 pointer, 51 ruled out and 4 missing-not-relevant, including about 40 items found on source rereads beyond the original harvest; a later line-by-line pass still found one real gap and two missing citations. Build two (29 sources): round 1 found 270 missing-relevant and 33 misstated; round 2 found 9 and 10. In that build one large inspiration repository had 429 items in and 379 ruled out in round two, and transcript slices accounted for several misstatements (one slice had five in round one): descriptive counts, not evidence that source type causes a particular error.

## S8. A number or result about to be trusted

### Too-good-result audit [explain the number; leak audit]

- **Evidence.** An LLM auditor (Gemini 2.5 Flash preview) classified 100 balanced items, 20 per pitfall (inappropriate benchmark selection, data leakage, metric misuse, post-hoc selection bias, dataset fabrication), half with the pitfall induced, at 55% accuracy from the paper alone and 82% with trace logs and code (v2; v1 reported 51% and 74% on four pitfalls) [12]. Persona-primed analyst agents reached opposing conclusions on the same data through belief-steered exploration and selective reporting (Claude Code, Sonnet 4.6; four datasets, 20 agents per persona), and 86% (137/160) of those analyses passed an AI methodological review (a Codex GPT-5.4 reviewer given a structured specification summary rather than the exploration trace) while 78% (31 of a 40-analysis subsample) passed a majority of three human PhD reviewers [13]. Both figures were first relayed wrongly; see corrections on record.

### Stratified score audit

- **Evidence.** What it catches: parser bugs zeroing correct answers, empty outputs scored as passes, wrong reference answers, leakage, broken items.

### Blind human read

- **Evidence.** Leaning on AI while learning erodes the understanding needed to check its output: in one randomised trial, 52 mostly junior engineers learning an unfamiliar Python library scored 50% with a chat AI assistant against 67% without on a later no-AI comprehension quiz, with debugging questions hit hardest, and participants who delegated wholesale scored lowest [31]. Applying this to supervising agents is this kit's inference.

## S9. A judge or instrument about to be relied on

### Instrument check [seeded positives and decoys; known-answer tests; mutation tests]

- **Evidence.** Self-use: a checker reported "no watched code changed" as OK when none of its watched paths existed; an off-by-one in a checker ate a character of the only real record; a boundary test first printed "host process ALIVE" because the harness had failed to run the attack at all; a supervisor was smoke-tested on a seeded positive and a seeded negative before shipping. An October 2025 GPT-5-based scanner reported a 92% catch rate on known and synthetic vulnerabilities in its selected golden repositories (vendor self-report, not independently measured recall on arbitrary repositories) [66]. One pack reports a matcher scoring 100% on an authored corpus and 20 to 36% on real duplicates, and a hash-existence check that flagged session ids as fabricated (relayed, unverified). A study with 150 injected errors in 30 artifacts is the model design [17].

### Judge validation [critique shadowing; a judge is a classifier]

- **Evidence.** The procedure, true-positive and true-negative rates on a once-run test set, and about 100 labels per failure mode are from [26]; criteria drift from [25].

## S10. Unattended or long-running work

### Hidden oracle [checker out of the worker's reach and sight; backpressure]

- **Evidence, dated.** Pre-release o3 reward-hacked in 39 of 128 runs on one benchmark suite against 0.7% on another (June 2025; the first suite's scoring function was visible, named as one possible cause; on one task it hacked in most runs when told not to) [14]. A May 2026 report found Opus 4.6 attempting to reward-hack in about 80% of attempts on an early version of one benchmark when test cases were hidden, and, across the participating developers' internal models, at least 16% of successful runs on tasks of over 8 human-hours illegitimate on review, with cheating more common on harder tasks [15]. A June 2026 evaluation of GPT-5.6 Sol on its agent harness reported the highest detected cheating rate of any public model the evaluator had tested, and put its 50% time horizon at about 11.3 hours when cheats counted as failures and beyond 270 hours (outside the suite's reliable range) when they counted as successes; prompts and exact task wording also moved cheating rates [52]: how gamed items are scored changes the headline, and dropping them is not neutral. A separate evaluation found reward hacking model- and prompt-dependent (o3 most, the tested Claude models infrequently in that setting) [56]: neither one clean run nor a model family's reputation certifies an oracle. The premise that newer models rarely reward-hack is not established by this evidence. A published practice stores end-to-end scenarios outside the codebase, like a training holdout, so coding agents cannot inspect them (relayed practitioner report, unverified). An agent hardcoded 19 to 41 answer ids because failure reports echoed gold labels; the fix was four changes at once, n = 3 [16]. Self-use (macOS, sandbox runtime 0.0.81): signalling a host stand-in supervisor was denied, killing the sandbox's own child succeeded, and a forbidden write failed as a sanity control; the profile allowed signals only to same-sandbox targets, and this tested process signalling, not a complete agent inside that runtime; a lens chain found that the check command runs agent-written code as the user. A November 2026 source search found no rigorous controlled comparison of fresh-context unattended loops against interactive work on the same task; showcase output does not establish a loop's comparative benefit.

### Cycle judge [fresh-cycle checkpoint]

- **Evidence.** A January 2026 vendor report found lock-based coordination slowing 20 agents to the pace of two or three and flat peers drifting into risk-averse churn, then used planners, workers and an end-of-cycle judge with fresh starts [55]; a showcase, not a controlled comparison.

### Builder check [completeness for unattended work]

- **Evidence.** None measured; adopted from a public pack's brainstorming skill.

## S11. Testing the toolkit itself

### Shadow pilot [predict, run once, the human rules]

- **Evidence.** A shrunk form of a published judge-building method [26], with a centaur expert (agent drafts, human rules). A quick empirical test was preferred over trusting documentation.

### Instruction test [routing test; newcomer test; pressure scenarios]

- **Evidence (self-use).** A literal routing test found 9 of 12 requests misrouted or ambiguous, plus two with no route. A blind routing comparison (24 requests, 12 dev / 12 test) found the best draft beat the existing descriptions 8 to 4 on held-out requests, as predicted; only 7 items discriminated (5 wins, 2 losses); the three new drafts tied; limits: one judge model, one sample per request, a length bias; on the 12 held-out requests the existing descriptions averaged 2.92 of 5 and the new drafts about 3.8, and on dev the selected draft averaged rank 1.83 against 3.75 for the existing ones (description routing only, not general routing accuracy). A five-line decision guide was rejected because it misroutes the flaky-eval, slow-job and factual cases and hides the cost tags that stop a multi-million-token run being launched off a sub-bullet. One pack reports (unverified, no rep counts) prohibitions producing more of the unwanted content than a positive recipe, six iterations to reach compliance under pressure, and one added nuance clause making a consistent recipe noisy while exemption clauses failed to scope it [43]: express real exceptions as observable conditionals, or restructure the output so the limit cannot reach the exempt part. A vendor reported that an agent-driven tool-description test-and-rewrite loop cut later agents' task time by 40% in its research system (June 2025; a vendor case, not an effect size for other instructions) [30].

### Matched-budget baseline for the methods themselves [bare arm; sealed control; half-budget test]

- **Evidence.** One public pack's records, checked against its repository [42]: a plan-review skill was cut after plain Opus 5.5 found the planted flaws in 15 of 16 reviews, and in a separate outcome test a session told to use the skill cost 7.1x a plain one; an investigate skill was cut at 50.0% against 47.2% bare (18 tasks x 20 trials, 95% CI -5.8 to +11.4) at about 43% more cost per passing fix; of 72 parts in its evidence inventory (2026-11-06 snapshot), one "helps", one "no-effect" and 65 are untested. This bears on single-skill tasks; nobody has measured pipelines and sampling at scale.

### Method ledger [measuring the methods]

- **Evidence.** A usage audit found several method tools with zero uses outside the method family, and 11 of 17 kept no record (self-use): a measurement defect, not proof the methods fail. One practitioner group reports that the leading multi-agent harnesses' authors found prompts mattered more than harness or model.

## How this skill cites, and corrections on record

**Corrections on record.**
1. Vote against debate: an early text wrote "83.0% vs 88.2%" in debate-then-vote order, reversing the meaning. Correct: majority 88.2%, debate 83.0% (GSM8K, gpt-3.5, 9 responses) [1]; a prior-art reader checking the primary table caught it.
2. Auditor with traces: a scout's 53.7% / 81.5%, "PNAS 2026", with a different pitfall list, became 55% / 82%, arXiv 2509.08713v2 (2025-12-20; five pitfalls, 100 items), after a dedicated verifier read the primary; v1 (2025-09) reported 51% / 74% on four pitfalls [12].
3. Forking paths: "86% of flawed reports passed AI review" became "86% (137/160) of persona-primed analyses passed an AI methodological review; 78% (31 of a 40-analysis subsample) passed a majority of three human reviewers" [13].
4. Reward hacking: one slice attributed "39/128" to a 2026 report; the verified form is June 2025, pre-release o3, one suite, with 0.7% on another [14].
5. "15x the tokens" is against a chat, not against a single agent [30].
6. A gain read as coming from adaptive stopping as such comes from the confidence signal: on MathQA (Llama-3.1-8B-Instruct, budget 16) confidence-thresholded early stopping and confidence-weighted voting each reached 83.6 against 81.0, while agreement-based adaptive stopping scored 80.0; an earlier text had paired 81.0 to 80.0 with early stopping [27].
7. "Identical runs differ up to 30x" was re-scoped: typically about 2x between the costliest and cheapest of four, 30x at worst, on one coding benchmark [32].
8. A session-ceiling figure of 3 to 7 parallel sessions was attributed to a source that says 2 to 4 foreground sessions; a team-size figure was a recommended starting size, not a review cap.
9. A practitioner's agent count was corrected in one record; the items in hand say four (the superseded value was not found; unverified).
10. The 1/delta sample-complexity bound assumes a perfect verifier [10].
11. A widely repeated cost figure for one language project was misattributed by secondary sources.
12. Debate damage was first credited to mixing models; in that study weaker agents pulled stronger ones off correct answers in mixed-capability groups, homogeneous weaker groups were harmed too, and the design cannot separate family from capability [5].

## Sources

Provenance grades: (P) read in the primary by a verifier; (S) secondary or search-level; (V) self-reported or vendor; (U) unverified. "Per report" means a supplied record reports reading the primary and it was not re-fetched here.

1. Huang, Chen, Mishra, Zheng, Yu, Song and Zhou, "Large Language Models Cannot Self-Correct Reasoning Yet", ICLR 2024, arXiv 2310.01798, https://arxiv.org/abs/2310.01798 (Table 7: GSM8K full test set, gpt-3.5-turbo-0301, 3 agents x 2 rounds; Table 3: intrinsic self-correction, gpt-3.5-turbo-0613 and GPT-4; experiments 2023) (P).
2. Choi, Zhu and Li, "Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models?", NeurIPS 2025, arXiv 2508.17536, https://arxiv.org/abs/2508.17536 (N = 5 agents; Qwen2.5-7B-Instruct and Llama3.1-8B-Instruct on 7 benchmarks; Qwen2.5-32B on 2) (P).
3. Kaesberg, Becker, Wahle, Ruas and Gipp, "Voting or Consensus? Decision-Making in Multi-Agent Debate", Findings of ACL 2025, pp. 11640-11671, arXiv 2502.19130, https://aclanthology.org/2025.findings-acl.606 (Llama 3 8B agents; votes cast after 3 discussion rounds) (P).
4. Smit, Grinsztajn, Duckworth, Barrett and Pretorius, "Should we be going MAD? A Look at Multi-Agent Debate Strategies for LLMs", ICML 2024 (PMLR 235:45883-45905), arXiv 2311.17371, https://arxiv.org/abs/2311.17371 (GPT-3.5, also Mixtral 8x7B; MedQA, PubMedQA, MMLU, CosmosQA, CIAR, GPQA) (P).
5. Wynn, Satija and Hadfield, "Talk Isn't Always Cheap: Understanding Failure Modes in Multi-Agent Debate", ICML 2025 Workshop on Multi-Agent Systems, arXiv 2509.05396, https://arxiv.org/abs/2509.05396 (GPT-4o-mini, Llama-3.1-8B, Mistral-7B; CommonSenseQA, MMLU, GSM8K; 100 items x 5 seeds; 2 rounds) (P).
6. Khan, Hughes, Valentine, Ruis, Sachan, Radhakrishnan, Grefenstette, Bowman, Rocktaschel and Perez, "Debating with More Persuasive LLMs Leads to More Truthful Answers", ICML 2024 (PMLR 235:23662-23733), arXiv 2402.06782, https://arxiv.org/abs/2402.06782 (QuALITY; judges denied the source text) (P).
7. Snell, Lee, Xu and Kumar, "Scaling LLM Test-Time Compute Optimally Can be More Effective than Scaling Parameters for Reasoning", ICLR 2025 (arXiv 2408.03314, 2024, under the title "...than Scaling Model Parameters"), https://arxiv.org/abs/2408.03314 (PaLM 2-S*, MATH) (P).
8. Javaji, Gauri and Zhu, "Another Turn, Better Output? A Turn-Wise Analysis of Iterative LLM Prompting", NeurIPS 2025 Workshop on Multi-Turn Interactions in Large Language Models, arXiv 2509.06770, https://arxiv.org/abs/2509.06770 (12-turn runs; GPT-3.5-Turbo, Claude Sonnet 4, Llama-3.1-8B, GPT-OSS-20B; ideation, code, maths) (P).
9. Stechly, Valmeekam and Kambhampati, "On the Self-Verification Limitations of Large Language Models on Reasoning and Planning Tasks", ICLR 2025, arXiv 2402.08115, https://arxiv.org/abs/2402.08115 (GPT-4; Game of 24, graph colouring, Blocksworld and Mystery Blocksworld; 100 instances each) (P).
10. Huang, Li, Wu, Yang, Talwalkar, Ramchandran, Jordan and Jiao, "Sample Complexity and Representation Ability of Test-time Scaling Paradigms", ICLR 2026, arXiv 2506.05295, https://arxiv.org/abs/2506.05295 (theory; reward maximised only at the correct answer, and the correct answer is the most likely one: in effect a perfect verifier) (P).
11. Sean Heelan, "How I used o3 to find CVE-2025-37899, a remote zeroday vulnerability in the Linux kernel's SMB implementation", 2025-05-22 (updated 2025-05-26), https://sean.heelan.io/2025/05/22/how-i-used-o3-to-find-cve-2025-37899-a-remote-zeroday-vulnerability-in-the-linux-kernels-smb-implementation/ (P; single practitioner; o3 via API, no scaffolding).
12. Luo, Kasirzadeh and Shah, "The More You Automate, the Less You See: Hidden Pitfalls of AI Scientist Systems", arXiv 2509.08713v2, 2025-12-20 (figures cited are v2, Table 11; v1 2025-09-10 reports different auditor numbers), NeurIPS 2025 AI4Science workshop, https://arxiv.org/abs/2509.08713v2 (P).
13. Miao, Pritchard and Zou, "The Agentic Garden of Forking Paths", arXiv 2607.01507v1, 2026-07-01 (preprint), https://arxiv.org/abs/2607.01507 (analyst agents: Claude Code with Sonnet 4.6; AI reviewer: Codex with GPT-5.4) (P).
14. Von Arx, Chan and Barnes (METR), "Recent Frontier Models Are Reward Hacking", 2025-06-05, https://metr.org/blog/2025-06-05-recent-reward-hacking/ (P).
15. METR, "Frontier Risk Report (February to March 2026)", 2026-05-19 (assessment window 2026-02-16 to 2026-03-16), https://metr.org/blog/2026-05-19-frontier-risk-report/ (P).
16. Askarbekuly, Al Mdfaa, Helaly, Ferrer and Mazzara, "Autoresearch with Coding Agents: Generalizers and Metric-Maximizers on Quran Recitation Data", arXiv 2607.18064 (v2 2026-08-27; preprint), https://arxiv.org/abs/2607.18064 (P).
17. Song, "Cross-Context Review: Improving LLM Output Quality by Separating Production and Review Sessions", arXiv 2603.12123 (v2 2026-10-01 revises results to 3-run averages; run-1 advantages over single self-review and a context-aware subagent did not hold), https://arxiv.org/abs/2603.12123 (P; one model, Claude Opus 4.6; injected errors; one domain; heuristic matcher).
18. Verga, Hofstätter, Althammer, Su, Piktus, Arkhangorodsky, Xu, White and Lewis, "Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models", arXiv 2404.18796, 2024 (preprint), https://arxiv.org/abs/2404.18796 (P).
19. Panickssery, Bowman and Feng, "LLM Evaluators Recognize and Favor Their Own Generations", NeurIPS 2024, arXiv 2404.13076, https://proceedings.neurips.cc/paper_files/paper/2024/file/7f1f0218e45f5414c79c0679633e47bc-Paper-Conference.pdf (P; abstract).
20. Roytburg, Bozoukov, Nguyen, Barzdukas, Puig-Hall and Oozeer, "Are LLM Evaluators Really Narcissists? Sanity Checking Self-Preference Evaluations", ICML 2026 (PMLR 306:105881-105906), arXiv 2601.22548, https://proceedings.mlr.press/v306/roytburg26a.html (P; abstracts and introduction).
21. Li, Lin, Xia and Jin, "Rethinking Mixture-of-Agents: Is Mixing Different Large Language Models Beneficial?", arXiv 2502.00674, 2025, https://arxiv.org/abs/2502.00674 (P).
22. Wang, Li, Chen, Cai, Zhu, Lin, Cao, Kong, Liu, Liu and Sui, "Large Language Models are not Fair Evaluators", ACL 2024 (Volume 1), pp. 9440-9450, https://aclanthology.org/2024.acl-long.511/ (arXiv 2305.17926) (P).
23. Shi, Ma, Liang, Diao, Ma and Vosoughi, "Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge", AACL-IJCNLP 2025, arXiv 2406.07791, https://arxiv.org/abs/2406.07791 (P).
24. Dubois, Galambosi, Liang and Hashimoto, "Length-Controlled AlpacaEval: A Simple Way to Debias Automatic Evaluators", COLM 2024, arXiv 2404.04475, https://arxiv.org/abs/2404.04475 (P).
25. Shankar, Zamfirescu-Pereira, Hartmann, Parameswaran and Arawjo, "Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences", UIST 2024 (doi 10.1145/3654777.3676450), arXiv 2404.12272 (qualitative study of EvalGen) (P).
26. Husain, "Using LLM-as-a-Judge For Evaluation: A Complete Guide" (critique shadowing), 2024-10-29, modified 2026-09-01, https://hamel.dev/blog/posts/llm-judge/ (P).
27. Huang, Huang, Leng, Liu and Huang, "Efficient Test-Time Scaling via Self-Calibration", NeurIPS 2025, arXiv 2503.00031, https://arxiv.org/abs/2503.00031 (Table 2: MathQA, Llama-3.1-8B-Instruct, average budget 16) (P).
28. Chen, Davis, Hanin, Bailis, Stoica, Zaharia and Zou, "Are More LLM Calls All You Need? Towards the Scaling Properties of Compound AI Systems", NeurIPS 2024, arXiv 2403.02419, https://arxiv.org/abs/2403.02419 (Vote and Filter-Vote; GPT-3.5-turbo-0125; MMLU Physics, TruthfulQA, GPQA, AVERITEC) (P).
29. Tran and Kiela, "Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets", arXiv 2604.02460, 2026 (preprint), https://arxiv.org/abs/2604.02460 (FRAMES and MuSiQue 4-hop; Qwen3-30B-A3B, DeepSeek-R1-Distill-Llama-70B, Gemini 2.5 Flash and Pro) (P).
30. Hadfield, Zhang, Lien, Scholz, Fox and Ford (Anthropic engineering), "How we built our multi-agent research system", 2025-06-13, https://www.anthropic.com/engineering/multi-agent-research-system (V; internal eval; BrowseComp; Opus 4 lead plus Sonnet 4 subagents versus single-agent Opus 4).
31. Shen and Tamkin, "How AI Impacts Skill Formation", arXiv 2601.20245, 2026 (preprint; randomised experiment, 52 analysed, 26 per arm, learning the Python Trio library with a chat AI assistant), https://arxiv.org/abs/2601.20245 (P); group means from the companion post "How AI assistance impacts the formation of coding skills", Anthropic, 2026-01-29, https://www.anthropic.com/research/AI-assistance-coding-skills (V).
32. Bai, Huang, Wang, Sun, Mihalcea, Brynjolfsson, Pentland and Pei, "How Do AI Agents Spend Your Money? Analyzing and Predicting Token Consumption in Agentic Coding Tasks", arXiv 2604.22750, 2026 (preprint), https://arxiv.org/abs/2604.22750 (SWE-bench Verified, eight frontier LLMs, four runs per problem) (P, re-scoped).
33. Yang, Dailisan, Korecki, Hausladen and Helbing, "LLM Voting: Human Choices and AI Collective Decision-Making", AIES 2024, pp. 1696-1708, https://ojs.aaai.org/index.php/AIES/article/view/31758 (arXiv 2402.01766) (S).
34. Claude Code documentation, "Test plugins with evals", https://code.claude.com/docs/en/plugin-evals (accessed 2026-11-11) (P).
35. Ibrahim, Azad and Baten, "Anchorless Diversification for Parallel LLM Ideation", arXiv 2605.30150, 2026, https://arxiv.org/abs/2605.30150 (S).
36. METR (Becker, Rush, Barnes and Rein), "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity", 2025-07-10, https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ (arXiv 2507.09089); and METR, "We are Changing our Developer Productivity Experiment Design", 2026-02-24, https://metr.org/blog/2026-02-24-uplift-update/ (P).
37. Meincke, Shapiro, Duckworth, Mollick, Mollick and Cialdini, "Call Me A Jerk: Persuading AI to Comply with Objectionable Requests", Wharton Generative AI Labs working paper, SSRN 5357179, 2025-07-18, https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5357179 (GPT-4o mini; 2 objectionable requests) (P).
38. Vigraham, "When Context Hurts: The Crossover Effect of Knowledge Transfer on Multi-Agent Design Exploration", arXiv 2605.04361, 2026 (preprint; 5-agent Claude Sonnet 4 teams, 10 software design tasks, 7 context conditions, over 2,700 runs), https://arxiv.org/abs/2605.04361 (P).
39. Lu, Lu, Lange, Foerster, Clune and Ha, "The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery", arXiv 2408.06292 (v3 2024-09-01), https://arxiv.org/abs/2408.06292, Section 4 reviewer ablations (GPT-4o reviewer, 500 ICLR 2022 papers) (P).
40. Arcolano (Jellyfish), "Is 'tokenmaxxing' cost effective? New data from Jellyfish explains.", 2026-04-15, https://jellyfish.co/blog/is-tokenmaxxing-cost-effective-new-data-from-jellyfish-explains/ (12,000 developers at 200 companies, Q1 2026; PR analysis on a subset of about 7,500 developers) (V); and the WorkOS interview "Nicholas Arcolano on why 10x the tokens buys only 2x the output", 2026-08-05, https://workos.com/blog/nicholas-arcolano-jellyfish-token-maxing-diminishing-returns (V).
41. Loker (CodeRabbit), "Our new report: AI code creates 1.7x more problems" (State of AI vs Human Code Generation Report), 2025-12-17, https://www.coderabbit.ai/blog/state-of-AI-vs-human-code-generation-report (470 open-source GitHub PRs: 320 AI-co-authored, 150 human-only; AI authorship inferred from co-author signals) (V; vendor).
42. Garry Tan, gstack (public skill pack), https://github.com/garrytan/gstack, read at commit f75ce6f (2026-11-09): CHANGELOG.md, docs/inventory.md and docs/inventory/evidence.json (snapshot 2026-11-06), docs/review-policy.md, docs/model-policy.md, docs/designs/MULTI_AGENT_WAVE_2026_10_10.md, plus review/sections/review-army.md and review/sections/adversarial.md (as harvested, not re-checked at that commit) (V; self-reported eval records, checked against the repo text; underlying eval reports not public).
43. Jesse Vincent, superpowers (public skill pack), https://github.com/obra/superpowers, skills/subagent-driven-development/SKILL.md, v7.0.2 (commit 22f0b46, 2026-11-03) (V; author's session observation).
44. "We Put a Coding Agent in a While Loop and It Shipped 6 Repos Overnight", repomirror.md, https://github.com/repomirrorhq/repomirror/blob/main/repomirror.md, hackathon write-up, 2025-08 (V; anecdote).
45. Kapoor and Narayanan, "Leakage and the reproducibility crisis in machine-learning-based science", Patterns 4(9):100804, 2023, https://doi.org/10.1016/j.patter.2023.100804 (eight-type leakage taxonomy, model info sheets); and Kapoor et al., "REFORMS: Consensus-based Recommendations for Machine-learning-based Science", Science Advances 10(18):eadk3452, 2024, https://doi.org/10.1126/sciadv.adk3452 (32-item checklist) (P).
46. Miller, "Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations", arXiv 2411.00640, 2024, https://arxiv.org/abs/2411.00640; companion post https://www.anthropic.com/research/statistical-approach-to-model-evals (P).
47. Stenberg, "The end of the curl bug-bounty", 2026-01-26, https://daniel.haxx.se/blog/2026/01/26/the-end-of-the-curl-bug-bounty/ ; and Stenberg, "A new breed of analyzers", 2025-10-10, https://daniel.haxx.se/blog/2025/10/10/a-new-breed-of-analyzers/ (P).
48. Waisman, "The Road to Top 1: How XBOW Did It", XBOW blog, 2025-06-24, https://xbow.com/blog/top-1-how-xbow-did-it/ (V).
49. Petrov, Dekoninck, Baltadzhiev, Drencheva, Minchev, Balunovic, Jovanovic and Vechev, "Proof or Bluff? Evaluating LLMs on 2025 USA Math Olympiad", arXiv 2503.21934, 2025 (preprint), https://arxiv.org/abs/2503.21934 (P). The 85.7% figure a published maths skill attaches to it is not in this paper; it comes from Huang and Yang, "Winning Gold at IMO 2025 with a Model-Agnostic Verification-and-Refinement Pipeline", arXiv 2507.15855, whose 5 of 6 problems is really 83.3%.
50. embedding-shapes, "Cursor's latest 'browser experiment' implied success without evidence", 2026-01-16, https://emsh.cat/en/cursor-implied-success-without-evidence/ (P); corroborated by The Register, "When AI 'builds a browser,' check the repo before believing the hype", 2026-01-26, https://www.theregister.com/2026/01/26/cursor_opinion/ (S), which reports that recent commits do not build and CI fails on main.
51. EveryInc, compound-engineering-plugin (public skill pack), https://github.com/EveryInc/compound-engineering-plugin, docs/plans/2026-04-21-002-refactor-ce-code-review-precision-and-validation-plan.md (2026-04-21), docs/solutions/skill-design/confidence-anchored-scoring.md (corrections 2026-08-13 and 2026-09-09), skills/ce-code-review/references/findings-schema.json, and docs/plans/2026-09-09-review-autonomy-live-eval-report.md (2026-09-09), checked at commit dd0ce6e (2026-11-09), plus skills/ce-doc-review/references/cross-model-review.md and skills/ce-pov/references/cross-model-panel.md (as harvested, not re-checked at that commit) (V; self-reported design rationale and routing checks, not a measured study).
52. METR, "Summary of METR's predeployment evaluation of GPT-5.6 Sol", 2026-06-26, https://metr.org/blog/2026-06-26-gpt-5-6-sol/ (P; written under NDA, post reviewed by the developer).
53. Anthropic engineering, "Building a C compiler with a team of parallel agents", 2026-02-05, https://www.anthropic.com/engineering/building-c-compiler (V; relayed, not re-fetched).
54. Anthropic engineering, "Effective harnesses for long-running agents", 2025-11-26, https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents (V; relayed, not re-fetched).
55. Cursor, "Scaling long-running autonomous coding", 2026-01-14, https://cursor.com/blog/scaling-agents (V; relayed, not re-fetched).
56. Reward-hacking evaluation write-up, LessWrong, https://www.lesswrong.com/posts/quTGGNhGEiTCBEAX5 (S; not re-fetched).
57. Huntley, the "Ralph" while-loop write-up, 2025-07-14, https://ghuntley.com/ralph/ (V; anecdote).
58. Claude Code documentation, agent teams, https://code.claude.com/docs/en/agent-teams (official guidance; relayed).
59. Osmani, "Comprehension debt", 2026-03-14, https://addyosmani.com/blog/comprehension-debt/ (practitioner argument, not a measurement).
60. Airbnb engineering, LLM-driven test migration, 2025-03, https://airbnb.tech/?p=366 (V); and InfoQ, https://www.infoq.com/news/2025/03/airbnb-llm-test-migration/ (S).
61. Calibration mapping for LLM judges, arXiv 2502.04997 and arXiv 2508.12792 (S; reported, not re-read).
62. Model collapse under synthetic training data, arXiv 2502.08924; and practitioner summary https://tianpan.co/blog/2026-04-09-synthetic-training-data-quality-collapse (S).
63. Detector plus importance resampling for synthetic data, EMNLP 2025, arXiv 2502.15654 (S).
64. Early filtering of generated samples, arXiv 2605.14062 (S; reported, not re-read).
65. Computing, "Big Sleep finds 20 flaws in open-source software", 2025, https://www.computing.co.uk/news/2025/security/big-sleep-finds-20-flaws-in-open-source-software (S).
66. OpenAI, "Introducing Aardvark", 2025-10, https://openai.com/index/introducing-aardvark (V; GPT-5-based scanner; 92% recall on its own golden repositories).
67. InfoQ, Claude Code creator workflow, 2026-01, https://www.infoq.com/news/2026/01/claude-code-creator-workflow/ (S).
