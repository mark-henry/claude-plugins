---
name: plan
description: "A working method for shaping any piece of work for agents before spending on it: name what will check each piece, build missing checkers first, shape tasks so agents don't collide, pick a pattern with caps (oracle loop, bulk judge calls, best-of-N, majority vote, research fan-out, fresh review), stop for a go-ahead, then gate, dispatch, review, and measure cost per accepted result. Writes a one-table swarm plan. Use for \"/swarm:plan\", \"plan this for agents\", \"how should I parallelize this\", \"fan this out\", \"spend more compute on this\", \"what can run unattended\", or at the start of any multi-hour, multi-agent or unattended task. Not for a task one session finishes in about an hour with you watching, for measuring spend already made (swarm:review), for generating design options (diverge:design, diverge:lite), or for challenging a proposal you already have (gauntlet:run)."
---

# Plan work for a swarm

**Checker first, width second, you last.**

The limit on getting a lot done with agents is not tokens or models. It is your review attention, plus the quality of the checks a machine can run without you. Interactive, human-reviewed agent work tops out at a handful of parallel sessions per person: four agents wiped Willison out by 11am [1], the Claude Code docs recommend 3–5 teammates [2], and at 5–7 agents "most agents spend more time waiting for review than working" [3]. Beyond that, compute pays only where a machine checks the output [4][5]. Every step below moves work off your attention and onto a check.

## How to use it

The plan is five questions, one per step:

1. **Who says it's right?**
2. **Does that checker exist, out of the agent's reach?**
3. **How wide can it go without collisions?**
4. **Which pattern, with what caps?**
5. **What counts as accepted, and who reads it in what order?**

- **Any piece of work, 60 seconds:** answer the five in your head. If every answer is "me" or "one agent", stop planning and do the work.
- **Anything multi-hour, multi-agent, unattended or over a few dollars:** walk steps 1–5, write the swarm plan, and stop for the go-ahead. Then run the gates and dispatch, and review what comes back.
- **To check whether the spend pays:** `swarm:review`.

**When an agent runs this skill:** fill in the plan from the request and the repo. Ask the user, inline as a short list with a recommendation, only about the human-only pieces and about checkers you cannot find. Invoking the skill asks for a plan, not for approval to spend: nothing that costs more than the planning runs until the user approves the plan, unless they already asked for this run within a stated budget. The sibling skills named here (`brief:lock`, `evals:judge`, `evals:audit`, `prereg:launch`, `gauntlet:run`, `diverge:lite`, `court:hold`, `quota:check`) ship in the same marketplace; if one isn't installed, do its step by hand.

## 1. Who says it's right? Sort the work by its checker

If the goal or its "done when" bar is vague, lock it with `brief:lock` first. Then list the pieces. Split bundles: a refactor plus a perf fix plus test cleanup is three pieces [6]. A piece that needs two kinds of checker is two pieces: an experiment's code has tests, but its interpretation has only you. For each piece, name who or what will say it's right:

| Checker | Examples | Pattern (step 4) |
|---|---|---|
| **Machine oracle**: tests, type checker, reference implementation, sealed eval | ports, migrations, refactors, harness builds, reproducing a result | loop |
| **Validated judge**: an LLM judge with measured TPR and TNR against the expert's labels | labelling, grading outputs, filtering synthetic data | bulk calls |
| **Selector**: a cheap check that picks the winner from many attempts | bug hunting, hard fixes, prompt variants | best-of-N |
| **Agreement**: independent samples converge on a short, comparable answer | a label, a yes/no, a choice among fixed options, a number | majority vote |
| **Checkable summary**: a conclusion with sources you can spot-check | literature, codebase archaeology, debugging hypotheses | fan-out |
| **Only the human** | experiment design, taste, what to do next | you, with one lead agent |

The last row is the human's share; keep it short. A piece with no checker yet gets one in step 2, or moves to the last row.

**Done when:** every piece has one checker, or a task to build one.

## 2. Does the checker exist, out of reach? Build it before scaling

Long unattended runs succeeded only where an external pass/fail signal existed that the agent could not fake: "the task verifier must be nearly perfect, or Claude solves the wrong problem" [4]. Mark each checker **exists** or **to build**. A checker to build is its piece's first task, for one agent, and no second agent starts on the piece until the checker runs.

- **Oracle.** A spec with a "done when" bar, a ledger only the check can flip, and the scorer, test items and held-out set outside the agent's writable tree, because frontier models have modified tests and scoring code to raise scores [7]. Add a fast sampled mode. `swarm:loop` step 1 has the full setup.
- **Judge.** Build and validate it with `evals:judge`. Before believing any aggregate it produces, run `evals:audit`.
- **Selector.** A reproducer, a test or a validated judge that tells a real hit from noise. Raw samples are mostly noise: Heelan's novel kernel bug came at about one true report per 50 false ones [8].
- **Agreement.** Answers that compare exactly (normalize them first) and samples that are truly independent: fresh contexts, none seeing another's answer. It is the weakest machine checker, because agreement is not correctness: use a selector or validated judge instead where one exists, and spot-check a few unanimous items.
- **Summary.** A source for every claim, plus a planned spot check of a few claims.

**Done when:** every machine checker runs from one command, gives pass/fail per item and is out of the agent's reach, and every summary piece has its spot checks named.

## 3. How wide without collisions? Shape and isolate the tasks

- One owner per file, module, failing test or item, claimed atomically through lock files or a task board [4]. Keep claims short: at Cursor, agents held locks too long, and 20 agents ran at the throughput of 2–3 [5].
- Hierarchy, not a flat swarm: planners create tasks, workers don't coordinate with each other, and a judge ends each cycle with a fresh start [5].
- Size each task so its diff can be reviewed in one sitting [6]. One task per fresh context, with a commit and a progress note at each step [9]. Quality drops at about 60% context fill [6], so long work gets fresh sessions, not one long one.
- Keep briefs short and factual: a 1,500-word prompt made agents "slower and dumber" than a 103-word one [10]. Subagents write results to files and pass back references [11].
- Match width to the question: one agent for a simple fact, 2–4 for a comparison, more than 10 only for complex research. Anthropic's research system pairs a stronger lead model with cheaper subagents, and its early versions spawned 50 subagents for simple queries [11]. Pick a model per role.
- Each agent gets its own worktree or container. Bypass permission prompts only inside a sandbox [12].

**Done when:** each task has an owner, its own checkout, a brief under a page and an output path.

## 4. Which pattern, with what caps?

- **Loop** (oracle): one prompt file, a fresh agent each pass, state on disk, and a supervisor that runs the check itself and stops on done, a cap or a stall [13]. Run it with `swarm:loop`.
- **Bulk calls** (judge): one item per call, with the shared rubric first so it caches. Batch APIs halve the price when latency doesn't matter [14].
- **Best-of-N** (selector): slice narrowly and sample many times. In 100 runs over kernel code, a known bug turned up 8 times on a 3.3k-line slice and once on the full 12k lines [8]. Extra samples pay mainly on problems the model already solves sometimes [16]: if the first attempts all fail, narrow the slice or fix the context instead of raising N.
- **Majority vote** (agreement): independent samples, most common answer wins. It needs about 1/Δ² samples where a verifier needs 1/Δ [15], so it costs more per item; stop sampling an item once its vote is confidently decided, which in one study raised accuracy at a fixed 16-sample budget [28].
- **Fan-out** (summary): an orchestrator plus narrow subagents. In Anthropic's research system this beat a single agent by 90.2%, at about 15x the tokens [11].
- **Fresh review**, before anything merges or gets reported. A reviewer that hasn't seen the reasoning helps; handing the same task to another agent doesn't [17]. Give each reviewer one lens (correctness, leakage, confounds, security). A reviewer asked for problems "will always find something" [17], so each flag carries evidence and a severity, and a flag that would change a decision gets a second fresh check.
- **Debate is not a free upgrade.** At 9 responses on GSM8K, multi-agent debate scored 83.0% against 88.2% for a majority vote over the same number of samples, and its gains came from aggregation, not discussion [18]. A 2025 study found debate can leave answers worse than majority voting, especially with mixed agents [29]. Where answers compare, vote. Where they don't (a design, a plan, a fix), adversarial workflows (`gauntlet:run`, `diverge:lite`) are the tool, but check one once against independent drafts plus a judge's pick at the same budget before relying on it.

Give each piece a budget and a **stop rule**, the condition that ends it even if it isn't done: an iteration cap, a cost cap, or "N passes with no new tests passing". Interactive sessions stay at 3–5 [2]; background runs carry the volume. Check quota before a big fan-out (`quota:check` if you route through a proxy). Weekly caps arrived in 2025 aimed at users running Claude Code "continuously in the background, 24/7" [19], so keep bulk jobs restartable and spread them across model families and providers.

**Done when:** each piece has a pattern, an agent count, a model, a budget and a stop rule.

## 5. What counts as accepted, and who reads it in what order?

For each piece, write the acceptance check: the check that passes, not "looks done". Then fix the review order: audits, judges and reviewers first, you last. Every result will get one of three rulings: accept, kill or redirect.

**Done when:** every piece has an acceptance check and a place in the review order.

## Write the plan, then stop

Save the plan where the dispatched agents' briefs can link to it and the review can update it: the user's task tracker or notes if they keep one, otherwise `~/.swarm/plans/<YYYY-MM-DD>-<slug>.md`. Present it, then wait for the go-ahead.

```markdown
## Swarm plan: <work>
Done when: <bar, with its denominator>. Brief: <locked / not needed>.

| Piece (files it owns) | Checker | Build first? | Pattern | Agents × model; caps | Accepted when |
|---|---|---|---|---|---|
| <piece> (<files>) | <oracle / judge / selector / agreement / summary / human> | <yes: what / no> | <loop / bulk / best-of-N / vote / fan-out / review / you> | <N × model; M iterations; $ or quota cap; stop rule> | <the check that passes> |

Yours (only the human): <short list>
Gates: prereg <yes / n/a>; second opinion <who / n/a>; checkers to build <list / none>; smoke <3 items of which piece>
Quota: <ok / short on what; fallback>
Review order: <machine filters, then you>
Waiting on: <your go-ahead / nothing, run already authorized>

## Results
- <date> <piece>: <accepted / killed / redirected>, cost <$ API-equivalent or quota %>, review <minutes>, <why>
```

## Run it

After the go-ahead, run these gates in order before any piece scales:

1. **Preregister** any run whose number will be compared to a bar, reported, or used to choose between arms, with `prereg:launch`.
2. **Get a second opinion** on a costly design: a stronger model, `diverge:lite` or `gauntlet:run`. Prefer a $1 diagnostic of the mechanism to the full run.
3. **Build the missing checkers** (step 2), one agent each, and confirm each one runs.
4. **Smoke test:** run three items, read what went wrong, fix the prompt, then run the rest [17].

If a gate changes a piece's pattern, budget or done-bar, present the whole revised plan and wait again. Then dispatch. Once checkers exist, throughput is limited by the supply of well-specified tasks, not by agents: "you have to do a LOT of design and planning to keep the engine fed" [20]. ccusage and ccwhy attribute tokens to sessions [21], which fills in each result's cost.

## Review what comes back

- Read the filtered results first, in the planned order; you go last.
- Distrust claims of completion. Agents overstated how finished their ports were [10], and a coordinating agent reported bugs fixed that were not, while one PR merged past failing tests and had to be reverted [22]. Check the oracle, not the summary.
- Audit any result that looks too good for leakage before believing it.
- Write each ruling as a Results line in the plan. For a backlog of rulings, use `court:hold`.
- Stay engaged on the hard calls. Engineers who learned a library with AI scored 50% vs 67% on comprehension, with debugging hit hardest [23], and debugging is how you catch agent mistakes.
- Report back in one list: accepted (with the check that passed), killed or redirected and why, still running with budget left, rulings waiting on the user in priority order, and whether the done-bar is met.

## Measure whether it pays

Use `swarm:review` once enough Results lines have accumulated: cost per accepted result for each kind of work, the discard rate, review time, and a half-budget comparison, ending in a scale, hold or build-a-better-checker call.

## Anti-patterns

- Token counts as a goal. Meta took down its token leaderboard within days of it being reported [24]; Amazon called token metrics disconnected from results "deeply flawed" [25]; Uber used up its 2026 AI-coding budget by about April and capped spend per engineer [26].
- Fanning out implementation work faster than you can review it.
- Subagents that inherit or rebuild a large context for a small job. In one audit of 187 sessions, 97% of tokens were cache reads, and 840 subagent calls each duplicated full context for what were essentially searches [21]. Use plain search for a grep.
- Long MCP tool lists, giant plan files and long role prompts [27].

## Sources
1. Willison, via Axios, Apr 2026: https://www.axios.com/2026/04/04/ai-agents-burnout-addiction-claude-code-openclaw
2. Claude Code docs, agent teams: https://code.claude.com/docs/en/agent-teams
3. Paradev, "Roadmap to 100 agents", updated Oct 2026: https://paradev.com/blog/roadmap-to-100-agents
4. Carlini, Anthropic, Feb 2026: https://www.anthropic.com/engineering/building-c-compiler
5. Cursor, Jan 2026: https://cursor.com/blog/scaling-agents
6. Kilo blog, May 2026: https://blog.kilo.ai/p/how-7-kilo-code-engineers-run-up
7. METR, Jun 2025: https://metr.org/blog/2025-06-05-recent-reward-hacking
8. Heelan, May 2025: https://sean.heelan.io/2025/05/22/how-i-used-o3-to-find-cve-2025-37899-a-remote-zeroday-vulnerability-in-the-linux-kernels-smb-implementation/
9. Anthropic, Nov 2025: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
10. RepoMirror, Aug 2025: https://github.com/repomirrorhq/repomirror/blob/main/repomirror.md
11. Anthropic, Jun 2025: https://www.anthropic.com/engineering/multi-agent-research-system
12. Claude Code sandbox docs: https://code.claude.com/docs/en/sandbox-environments
13. Huntley, Jul 2025: https://ghuntley.com/ralph/
14. Anthropic batch processing: https://platform.claude.com/docs/en/build-with-claude/message-batches
15. arXiv 2506.05295: https://export.arxiv.org/abs/2506.05295
16. Snell et al., ICLR 2025: https://arxiv.org/abs/2408.03314v1
17. Claude Code best practices: https://code.claude.com/docs/en/best-practices
18. Huang et al., ICLR 2024: https://arxiv.org/pdf/2310.01798
19. TechCrunch, Jul 2025: https://techcrunch.com/2025/07/28/anthropic-unveils-new-rate-limits-to-curb-claude-code-power-users
20. Yegge's Gas Town, via a secondary summary: https://second-brain-nuxt.vercel.app/gas-towns-agent-patterns
21. SingYee, Apr 2026: https://dev.to/singyee/i-analyzed-187-claude-code-sessions-6744-worth-of-tokens-heres-where-they-actually-went-2ae5
22. DoltHub, Jan 2026: https://www.dolthub.com/blog/2026-01-15-a-day-in-gas-town/
23. Anthropic skill-formation study, via Osmani: https://addyosmani.com/blog/comprehension-debt/
24. Fortune, Apr 2026: https://fortune.com/2026/04/09/meta-killed-employee-ai-token-dashboard/
25. Tom's Hardware, Oct 2026: https://www.tomshardware.com/tech-industry/artificial-intelligence/amazon-tells-engineers-to-stop-tokenmaxxing-to-look-productive-says-ai-will-be-central-to-software-development-but-usage-is-not-the-goal-new-guidelines-claim
26. Willison, Jun 2026: https://simonwillison.net/2026/jun/3/uber-caps-usage
27. Steinberger, Oct 2025: https://steipete.me/posts/just-talk-to-it
28. Efficient Test-Time Scaling via Self-Calibration, NeurIPS 2025: https://arxiv.org/abs/2503.00031v1
29. "Talk Isn't Always Cheap", 2025: https://arxiv.org/html/2509.05396v2
