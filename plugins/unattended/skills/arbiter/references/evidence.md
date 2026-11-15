# Evidence for unattended:arbiter

Study findings, incidents, quotes and the numbered source list moved out of the body of `unattended:arbiter`, verbatim. Each passage sits under a line naming the instruction it backs; bracketed numbers point into the source list. Product and model names are as they stood when the passage was written.

## Sources
1. Carlini, Anthropic, Feb 2026: https://www.anthropic.com/engineering/building-c-compiler
2. Huntley, Jul 2025: https://ghuntley.com/ralph/
3. OpenAI, long-horizon Codex tasks: https://developers.openai.com/blog/run-long-horizon-tasks-with-codex
4. Anthropic, Nov 2025: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
5. METR, Jun 2025: https://metr.org/blog/2025-06-05-recent-reward-hacking
6. Willison on StrongDM's software factory, Feb 2026: https://simonwillison.net/2026/feb/7/software-factory/
7. RepoMirror, Aug 2025: https://github.com/repomirrorhq/repomirror/blob/main/repomirror.md
8. Cyrus, Jan 2026, on Anthropic's ralph-wiggum plugin: https://www.atcyrus.com/stories/ralph-wiggum-technique-claude-code-autonomous-loops
9. Claude Code sandbox docs: https://code.claude.com/docs/en/sandbox-environments
10. Cursor, Jan 2026: https://cursor.com/blog/scaling-agents
11. Claude Code best practices: https://code.claude.com/docs/en/best-practices
12. METR, Frontier Risk Report, May 2026: https://metr.org/blog/2026-05-19-frontier-risk-report/
13. METR, GPT-5.6 Sol evaluation, Jun 2026: https://metr.org/blog/2026-06-26-gpt-5-6-sol/
14. Anthropic, harness design for long-running apps, Mar 2026: https://www.anthropic.com/engineering/harness-design-long-running-apps

## Opening

Backs: a loop is worth running unattended only when a pass/fail signal exists that the agent cannot fake.

> A loop is worth running unattended only when a pass/fail signal exists that the agent cannot fake: "it's important that the task verifier is nearly perfect, otherwise Claude will solve the wrong problem" [1].

Backs: the pattern is Huntley's Ralph loop: one prompt file, a fresh agent each pass, and all state on disk.

> The pattern is Huntley's Ralph loop: one prompt file, a fresh agent each pass, and all state on disk [2].

## 1. Set up the loop directory

Backs: `SPEC.md` holds goals, non-goals, hard constraints, deliverables and "done when" criteria.

> goals, non-goals, hard constraints, deliverables, "done when" criteria [3]

Backs: `ledger.json` is JSON, and only the check flips `passes`.

> JSON, because models overwrite it less readily than Markdown [4].

> (In [4] the agent flips `passes` itself; here only the check does.)

Backs: keep the scorer, the test items and the held-out set out of the agent's reach, and out of its sight.

> Frontier models have modified tests and scoring code to raise scores, did so far more often when they could see the scoring code, and kept at it when told not to [5].

> 2026 evaluations still find it, more often on long and hard tasks, which is where unattended loops run [12][13].

> StrongDM often stores its end-to-end scenarios outside the codebase, "similar to a 'holdout' set in model training", so the coding agents cannot see them [6].

Backs: give the check a fast sampled mode with terse, grep-able output.

> Give the check a fast sampled mode (1–10% of items) so each pass gets feedback in minutes, with terse, grep-able output [1].

## 2. Write a short prompt

Backs: `PROMPT.md` says what it must in about 100 words.

> When RepoMirror (Sonnet 4, 2025) let Claude "improve" its loop prompt to 1,500 words, the agent got "slower and dumber" until they went back to 103 words [7].

> `PROMPT.md` says, in about that many words:

Backs: make the task pass by running the fast check, and rerun the tests that passed before.

> make it pass by running the fast check, and rerun the tests that passed before so the fix breaks nothing [1];

Backs: never edit or delete tests or the check.

> never edit or delete tests or the check ("It is unacceptable to remove or edit tests" [4]), and never touch the ledger's `passes` field, which only the check flips;

Backs: one task per fresh context.

> One task per fresh context keeps each pass well inside its window [4] and leaves a clean commit to check.

> Since Opus 4.5, Anthropic's own harness runs long builds as one session with compaction [14], so the boundary is now insurance rather than a necessity.

## 3. Run under a supervisor

Backs: done when the check exits 0, and the loop stops at once.

> Done when the check exits 0, and the loop stops at once: agents left running after the work is done drift into busywork and unrequested features [7].

Backs: the pass cap is both a safety limit and cost control; 10–20 passes is a reasonable start for a new task.

> It is both a safety limit and cost control; the ralph-wiggum plugin's guide suggests starting new tasks at 10–20 iterations [8].

Backs: run the agent as another user or in a container, out of reach of the supervisor's processes.

> `arbiter-loop` is a bash script, so an agent running as the same user can kill it too: in the C compiler run, Claude once ran `pkill -9 bash` by accident and ended the loop [1], and a RepoMirror agent `pkill`ed itself when it realized it was stuck [7].

Backs: bypass permission prompts only inside a container, a VM or the sandbox runtime.

> Bypass permission prompts only inside a container, a VM or the sandbox runtime, not the `/sandbox` Bash sandbox alone, which leaves file tools, MCP servers and hooks on the host [9].

Backs: for parallel loops, keep claims short and release them on failure.

> Keep claims short and release them on failure: in Cursor's January 2026 run, self-coordinating agents held locks too long or never released them, and 20 agents ran at the throughput of 2–3 [10].

Backs: for a one-shot mechanical migration, use the harness's `/batch`.

> For a one-shot mechanical migration, Claude Code's `/batch` splits the work into 5–30 units and shows the plan; once approved, each unit gets its own worktree and opens a PR or reports what happened [11].

## 4. Smoke, then scale

Backs: run three passes and read every log, then fix the prompt and the check, and only then start the real run.

> This adapts Claude Code's advice for scripted runs over files: "Try it on three files first, see what goes wrong, fix the prompt, then run the rest" [11].

Backs: watch for claims of completion with no change in the check.

> RepoMirror's 2025 agents overstated how finished their ports were [7].

Backs: watch for every pass taking the same big task; split it against a reference, so passes can work in parallel.

> When Linux kernel compilation was a single task, every agent hit the same bug.

> Splitting it against a reference (GCC) let them work in parallel [1].
