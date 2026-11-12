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
