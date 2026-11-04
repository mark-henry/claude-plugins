---
name: design
description: "Diverge-then-converge adversarial design as a Workflow: unanchored brainstormers, pick maximally distinct solution families, prototype, red-team and repair each, then a blind judge. Use for \"diverge\", \"adversarially design a fix\", or a wide-solution-space design problem where the first idea would anchor every attempt."
---

# Diverge, then converge adversarially

Invoking this skill is the user's opt-in to running a Workflow. The mechanism is the bundled script `diverge-converge.js` in this skill's directory. `scriptPath` only loads files under the working directory, an added directory or the scratchpad, so the plugin's own path is refused. Copy the script to your scratchpad and run `Workflow({scriptPath: "<scratchpad>/diverge-converge.js", args: {...}})`. Load the `workflow-authoring` skill first if its reference isn't already in context.

The script can't stop anchoring on its own: anchoring enters through the `args` you write. Most of this skill is about writing them.

## Roles

- **Planner: this thread.** You are lead, interviewer and planner in one. You get the brief locked (step 0), write the `args`, launch, and report afterwards. The planner never sees the brainstorm before it writes the brief, which is what keeps the brief clean.
- **Generators:** the brainstormers, the prototypers and the repairers. A repairer is a fresh agent in the prototyper's seat. It gets the prototype and the attack and patches the design. It's one round, not an open-ended charrette.
- **Evaluators:** the selector (which families are worth building), the red team (one per family) and the judge. The red team and the repairer are the pair locked in combat. The judge stands outside it and is blind to other runs.

## Step 0: lock the brief

If the conversation doesn't already contain a `## Locked brief` for this problem, invoke the `brief:lock` skill and run its interview with the user first. Don't launch without one: a vague brief is built into every agent downstream, and the red team grades against its own guess.

Map the brief onto `args`: Bar and Fallback bar become `target` (the red team grades "survives" against it as written), Constraints become `constraints`, Goal and Context facts become `context`. Before mapping, strip any diagnosis or solution example that crept into the brief.

**When you're ready, show the plan and launch it from a neutral turn.** Don't wait for approval; the user interrupts if they object. The harness relays the user message that triggered the Workflow call, verbatim, to every agent as "the only user voice in this task", and no script can turn that off. Launched straight after the interview, every agent sees the user's last answer, along with any example, diagnosis or "don't anchor on X" in it. So end the plan turn by scheduling the launch with a one-shot `CronCreate` firing about a minute later (it fires only when the session is idle). Its prompt is just "Launch the diverge:design run planned above." A cron-fired turn isn't a user request, so the harness relays nothing and agents see only the script's text (tested 2026-11-03 with a one-agent probe: launched from a user turn, the agent's first message was that turn verbatim; launched from a cron, it had no relay block). If the user replies before it fires, read the reply; if it changes the plan, `CronDelete` the job and re-plan.

The plan names the framings (one line each), the number of picks and why, the model and effort per role, the sandboxes, the measurement commands, any spend the prototypes may incur, and the agent count. Use the defaults below unless you say why not.

## Counts and models (defaults; tune these from experience)

| Choice | Default | Change it when |
|---|---|---|
| Brainstormers | 4: open, outside, adversary, skeptic | Add a fifth stance only if the domain has a distinct vantage none of the four covers (e.g. "the person who has to maintain this"). Never drop the skeptic. |
| Ideas per brainstormer | 8-10 (6-8 for adversary and skeptic, who spend effort on analysis first) | Fewer only for very narrow problems. |
| Picks (families prototyped) | 3 | 2 if the selector finds fewer than 5 genuinely distinct families. 4 if it finds 8 or more and the user accepts the cost. |
| Picks inside the obvious component | at most 1 | Explained below. |
| Repair rounds | 1 | A second round only if every family came back "broken" and the attacks share a cause. |
| Models | inherit the session model for all roles; `judge: fable` | Use a cheaper model for brainstormers only if the problem is well-trodden. Never cheapen the red team or the judge. |
| Effort | set it explicitly; don't inherit by accident. A role without `efforts` inherits the session's effort, but a role with a `models` override silently falls back to that model's own default (Fable: high), tested 2026-11-02. Both logged runs ran at medium (judge at high), so nothing yet says whether higher pays. | Try `high` or `xhigh` for attack and judge first, where depth matters most, and log the result. |

**Why "at most one pick inside the obvious component".** The problem statement nearly always points at a component ("the generator leaks the answer"). Ideas that patch that component are the easiest to think of, so they dominate any brainstorm, and a selector picking "most promising" would fill every slot with variants of them. The rule reserves the other picks for fixes elsewhere: how results are measured, the incentives, the analysis plan, or the bar itself. One inside pick is kept as the baseline the outside ideas have to beat.

**Cost.** At 3 picks, about 15 agents and 2–2.5M tokens, which has cost between about 1.5 and 12 points of one Ultra account's weekly quota at Opus medium (runs 1-3; the expensive run had 7 h of overloaded measurements), plus any paid API spend in the prototypes. Wall time ranged from 70 minutes to 7 hours, driven by the measurements. Measured runs are in [runs.md](runs.md). Quote them when showing the plan, with the quota you expect it to use, and say so if the session has a workflow-size guideline. Run `subquota` before launch and record the reading.

> **After every run, add a row to [runs.md](runs.md).** These defaults are tuned from it, and it has very few rows so far.

## Shape

1. **Diverge.** Four independent brainstormers, one framing each: open, outside the obvious component, adversary, skeptic. None sees the others.
2. **Select.** One agent clusters every idea into families and picks the N most promising, maximally distinct ones, at most one inside the obvious component.
3. **Prototype, attack, repair**, pipelined per family, each in its own sandbox.
   The selector also lists shared requirements, fixes every family needs (such as a bug in the shared measurement script); the script hands them to every prototype, so no family absorbs them as its own mechanism.
4. **Judge.** It may recommend a design, a combination, a reframing, or that nothing meets the target (with the best achievable bar). It surfaces framing challenges for the user to decide.

## Writing `args` without anchoring

- **State facts, not your diagnosis.** Measurements, what was tried, what happened. Leave out "the root cause is X" and "widening Y didn't help, because Z": a causal story narrows every brainstormer to fixes for that story.
- **Never pass in your earlier options.** If you already proposed fixes to the user, they're your priors. Leave them out. They'll come back if they're good.
- **Frame by stance, not by solution area.** "Think as the adversary" and "challenge the premise" widen the search. "Try distribution changes" narrows it. Override the default framings only with other stances.
- **Write framings like tarot cards, not requirements.** A framing is a broad, slightly evocative prompt to look from somewhere else: the adversary, the skeptic, the far side of the system. It's an inspiration to interpret, not a checklist to satisfy. The concrete rules ("8-10 ideas", "at least half outside") are scaffolding around the card, not its content.
- **Keep a skeptic.** One brainstormer must be allowed to argue that the problem is smaller, the bar is wrong, or the metric's definition is the real issue.
- **The bar goes in `target`, not in `context`.** It's locked by the interview. The skeptic may still argue against it with evidence, and the judge surfaces that argument as a decision for the user, but the red team grades against it as written.
- **Keep other runs blind.** Don't put another run's results (an earlier workflow, a parallel one) into `context` or into the judge. Compare runs yourself afterwards.
- **Don't go looking for them either.** Never read other sessions' transcripts (`~/.claude/projects/*.jsonl`) or workflow outputs about this problem, even to find where a number came from. Measure it yourself from the repo or ask the user.
- **No solution examples in `target`.** A bar like "requires combining ≥3 printed numbers (e.g. weekly rows to sum)" hands every brainstormer the weekly-rows fix. State the property, never an example of meeting it.
- **Write `context` for everyone, sandbox or not.** Brainstormers and the selector read it too, and have no sandbox. Don't say "your sandbox" in it; the script adds each prototype's sandbox itself.
- **Constraints are hard limits only.** Spend, files that must not change, data-handling rules. A preference stated as a constraint prunes whole families.

## Sandboxes

Prepare one disposable copy per pick before launching (e.g. `rsync -a --exclude .git --exclude .venv --exclude logs <repo>/ <scratch>/copy-N/`). Check that imports in a copy resolve to the copy, not the original, and that the test command runs in it (excluding `.venv` breaks `uv run`). Pass absolute paths in `sandboxes`. Prototypes and attackers edit only their sandbox.

**Share the CPU.** All sandboxes run at once on one machine. Give each at most (cores ÷ picks) worker processes and write that cap into `measure`, e.g. "use at most 2 processes" on an 8-core machine with 3 picks. Run 3 let each sandbox use every core; load hit 163 and the run took 7 hours instead of about 1.

**Check the measurement before launch.** Every family is only as comparable as the script that measures it. Before launching:
- Build any shared measurement script and run it on cases whose answers you already know, including the domain's edge cases. Run 3's audit mis-graded every instance with a pre-existing shift until an agent caught it mid-run, and the fix never reached the other sandboxes, so their final reports quoted the wrong baseline.
- Have one agent red-team the script itself: which policy games its metrics, which cheap baseline it underrates. In run 3 every attacker independently found that a per-arm constant beat the audit's cheap-policy finder.
- Run it once at full size with the per-sandbox process cap, to see its real wall time and that it doesn't hang under load.
- Run the test command inside a sandbox copy, not the original. Excluding `.venv` from the copy broke `uv run pytest` for ten agents in run 3. Paste the invocation that actually works into `measure`.
- Keep numbers the script derives (baselines, fixed-rule rates) out of `context`. Put them in a file it regenerates and point to that file, so a fix to the script corrects them for everyone.

## args

| Key | Required | Meaning |
|---|---|---|
| `context` | yes | problem: goal, facts, measurements, where to read |
| `constraints` | yes | hard limits |
| `sandboxes` | yes | absolute paths, one per pick |
| `target` | yes | the bar from step 0, with definitions and how to measure it; the red team's survival bar |
| `measure` | no | local measurement commands, test command |
| `framings` | no | `[{key, text}]` stance overrides |
| `picks` | no | families to prototype; defaults to the number of sandboxes |
| `models` | no | model per role: `{diverge, select, proto, attack, repair, judge}`, e.g. `{judge: "fable"}` |
| `efforts` | no | effort per role, same keys, e.g. `{attack: "high", judge: "xhigh"}`; omitted roles inherit the session's |
| `minutes` | no | wall-time budget per prototype, attack and repair agent; default 45. Over budget, they report unfinished work instead of overrunning. In run 3 one repairer took 168 minutes and the judge waited 4 hours on that chain. |
| `audience` | no | who reads the recommendation |

Size: 4 brainstormers + 1 selector + 3 per pick + 1 judge, so 15 agents at 3 picks.

## After it returns

Read the judge's recommendation and the `clusters` list yourself. Read the run's log for `unfinished` lines: work an agent couldn't finish within `minutes` and numbers it couldn't verify. Report to the user: the recommendation, the framing challenges they need to decide, and which families were not prototyped. Verify any number you repeat. If the run exposed a hole in the bar, say so plainly: the interview missed it, and the lesson belongs in the attacks list above.

Then run `subquota` again and add the run's row to [runs.md](runs.md), with the quota drop and its outcome in a sentence.
