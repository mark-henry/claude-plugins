# Evidence for lab:experiment

What the sources and this pack's own runs found, with the record of corrections and the numbered source list, moved out of the body of `lab:experiment`. Headings are the sections of the skill each passage came from.

## Sources

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

## Findings the skill's instructions rest on

Each item is quoted from the body of `lab:experiment` as it stood before commit 299e8b2, with its source number pointing into the list above. The line after each quote names the rule in the current skill that it supports.

### Leakage and held-out

- "In one field's reproduction study, all four papers claiming complex models beat logistic regression had leakage, and once it was fixed the complex models did no better [1]." Supports Rule 5: leakage and held-out (a leak makes a complex arm look better than a simple one).
- "An agent hardcoded answers that leaked to it through failure reports [18]." Supports Rule 5: leakage and held-out (failure reports that echo gold labels to an optimizing agent).

### Noise and seeds

- "Three seeds a side make a figure, not a test [11]. By exact arithmetic, a one-sided rank test of 3 against 3 reaches at best p = 0.05, 4 against 4 about 0.014, and 2 of 3 against 0 of 3 gives p = 0.2." Supports Rule 4: noise floor (the 3-against-3 and 4-against-4 figures; the 2-of-3-against-0-of-3 figure is no longer referenced).
- "With a handful of seeds, don't write "significant": Agarwal et al. [11] advise interval estimates over dichotomous significance claims (Henderson and Bouthillier test significance, but with many runs)." Supports Rule 11: declared denominator, beyond noise (seeds as the unit, never "significant").
- "Several samples per item fixed in advance, or scoring from token probabilities, cuts within-item noise [2]." No longer referenced.
- "Criteria drift on contact with outputs [5]" Supports Rule 7: freeze (read every item the scorer fails before the freeze, because criteria drift).

### Multi-sample and multi-agent methods

- "On GSM8K with gpt-3.5-turbo (2023), at nine responses each (debate: 3 agents, 2 rounds), debate scored 83.0 and self-consistency 88.2 against 76.7 for one answer [6]; the authors attribute debate's gain to consistency across generations, not self-correction." Supports Rule 3: controls (a multi-sample method meets its simple baseline at a matched token budget).
- "No self-revision without an external signal (shown on 2023 models [6]; recheck on current ones)" Supports Rule 3: controls (self-correction is one of the methods that must meet the baseline); the external-signal requirement itself is no longer referenced.

### Cost and token use

- "in one published system (2025), multi-agent runs used about 15x the tokens of a chat and single agents about 4x a chat, so roughly 4x a single agent by implication [7]" Supports Rule 13: the sentence (the comparator must be named).
- "compute (token use alone explained 80% of performance variance on one browsing benchmark in 2025 [7])" Supports Rule 3: controls (matched token budget); not listed as a parity break in Rule 1 any more.
- "identical agentic runs vary in cost (on one coding benchmark the costliest of four runs averaged about 2x the cheapest, at worst 30x in tokens [9])" Supports Order of events, step 4 (say what it should cost); the contingency multiple and the range pricing of agentic arms are no longer referenced.

### Prompts

- "in one practitioner's report, expanding a 103-word loop prompt to 1,500 words made the agent "slower and dumber" until it was cut back (anecdote, 2025 model) [10]" Supports Rule 6: instrument (prompts whose wording could move the result); the length point itself is no longer referenced.

### Reward hacking and tampering

- "In 2025 METR saw a frontier model modify tests and scoring code, still doing so on one task in most runs when told not to cheat [14]" Supports Rule 5: leakage and held-out ("out of reach is built, not instructed"; hiding the scorer stops tampering, not attempts).
- "its 2026 report found frontier models tampering with scoring code against explicit instructions, more often on harder and longer tasks, where unattended runs operate [15]" Supports Rule 5: leakage and held-out (same instruction).
- "A pre-release o3 reward-hacked in 39 of 128 RE-Bench runs but in 0.7% of HCAST runs; RE-Bench's scoring function was visible, which METR names as one possible cause. On one task it still hacked in most runs when told not to [14]." Supports Rule 5: leakage and held-out (read traces for tampering attempts); also Rule 6: instrument (a reward is an instrument under attack).

### Agents and review

- "A 2025 study of AI-scientist systems found inappropriate benchmark selection, data leakage, metric misuse and post-hoc selection bias. An LLM auditor (Gemini 2.5 Flash) classified balanced items, half flawed, with 55% accuracy from the paper alone and 82% with trace logs and code, so the authors recommend requiring logs and code with the paper [16]." Supports Rule 10: scores read (an automated review of the report alone is not a check; the human read and raw records come first).
- "In 2026, persona-primed analyst agents reached opposing conclusions on the same data by selective reporting, and 86% (137/160) of their analyses passed an AI methodological review and 78% (31/40) passed a majority of three human PhD reviewers: selection is invisible to final-report review, by machine or human [17]." Supports Rule 10: scores read (and Rule 12: exploratory runs stay out of the tally).
- "Agents declare success despite obvious failures [19]." Supports Rule 8: run record ("what an agent says ran is a claim").

### Attribution of gains

- "Papers often misattribute where gains come from [13]" Supports Rule 1: one difference (credit only the component the design isolates) and Rule 11 (check the result survives other ways to aggregate).

### Sources cited in the old text with no finding attached

- [3] Cited only for the scientific, nuisance and fixed classes of knob. Supports Rule 1: one difference (a setting tuned on one arm).
- [4] Cited only for "Fix the seed, check loss at init, overfit one batch". No longer referenced.
- [8] Cited only for running a multi-sample method against its simple baseline at matched budget. Supports Rule 3: controls.
- [12] Cited only for preferring evals whose signal across models is large against checkpoint-to-checkpoint noise. No longer referenced.
- [23] Cited only for "Never invent an effect size or compute post-hoc power". Supports Rule 4: noise floor.
- [24] Cited only for sending a skill or plugin treatment to `claude plugin eval`. Supports the scope line in the skill's description.
