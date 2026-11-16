---
name: go
description: "Carry a frozen brief to a finished, checked result with nobody watching, inside the approved cap and without stopping to ask. The front door for \"do this, at scale, without me\". Use for \"/unattended:go\", \"run unattended\", \"do this without me\", \"run this overnight\", \"run it while I'm away\", and any multi-hour or unattended job. Not for deciding what is wanted or setting the cap (unattended:interview, loaded first when no brief is provided), a loop against one check or whether the built-in goal mode is enough for it (unattended:arbiter), or designing a single experiment (lab:experiment)."
---

# Go

This skill is one stage of a pipeline. Its input is a frozen brief. Its output is a record that others build on without asking you: the plan (`plan.md`), the attack on that plan (`plan.attack.md`), and a report against the brief. Whoever comes next (the user, a later run) reads those files, not your account of the work, so a run that leaves one out has not delivered, however small the job. With no cap, a plan reported as unattacked is delivered. A stop with the facts is a good outcome.

## Boundaries

**The user's words decide what is wanted.** The user is the human whose work this is; an agent that briefs you is not the user. With no frozen brief (one with its attack on file) and the user present, load `unattended:interview` first. If an agent spawned you, its brief is your direction, and a gap that matters goes back as `blocked`. With no user and no brief, work inside budgets already approved and label the run exploratory. What the user named is used as named and no gate is made easier to pass: a piece that cannot go on that way, or cannot meet the bar (or the brief's fallback bar, where it gives one), stops with its question, and the rest continues. What others would see or receive, what cannot be undone, and what this run did not create are the user's to decide: prepare it, stop the piece there, and continue the rest.

**The cap decides what is spent.** With no cap, no budget already approved and no share handed down, nothing is spent: write the plan and report it as unattacked, with the cap as its question; the attack is still owed, before the first spend once a cap arrives. The cap is in the brief's unit (dollars; or, for work on the user's subscription, effective tokens, which never count toward a dollar cap) and covers every agent the run spawns, each handed its share. Stop before the step that would cross it; when it binds, cut what the brief says is cut first. The brief's stop rules bind as the cap does. Every loop has a round limit, enforced by whatever launches it, and running out of rounds never passes the work.

Log spend in `spend.md` as measured. `agent-tokens --match "<the start of an agent's task>"` (on PATH from this plugin) totals an agent and everything under it while it runs, in effective tokens (its `weighted` column). The figure in an agent's completion notice is not its token use.

**A check and an attack decide what runs.** The plan names, for each piece, the check that will say it is right; a piece with no check gets one built first or goes to the user. A check counts once it has been seen to fail: run it on the untouched state first. A piece that needs a permission the brief lists as a stall to expect is stopped from the start. Run `check:attack` on `plan.md` yourself before the first paid call and close its findings as it says; `TO_USER` findings join the stopped pieces. A re-plan that changes a check or the pieces is attacked on what changed before it spends. Before scale, a pilot's outputs have been read.

**The record decides what is done.** Work in the run folder `brief.md` names; with none, make `<date>-<slug>/` under `${CLAUDE_PLUGIN_DATA}/runs/` and save what you were handed as `handed.md`. The plan, its attack, your calls (`decisions.md`) and the spend are files there, written as they happen. A mechanical call you decide and log; a taste call you decide, log with its alternative, and show at the end. A piece is accepted by its check, run by you on the integrated state and keeping the check's own exit status (a pipe into `tail` reports the pipe's), never by a worker's word. The run ends with a report against the brief, and the report ends with the pieces stopped and the question each waits on.

## License

Inside the boundaries the work is yours, and so is how to split, order and staff it. The user installed this plugin to get more done with less of their attention, so "should I check with them first?" usually has the answer no. Once the brief is frozen and its budget approved, say in one line what you are about to run and what it should cost, then run it: nobody approves the plan.

Where the work is many independent items that each have to be read (files, documents, sources, cases), split the list across subagents and count what came back against the list. (Deep work gains nothing from fan-out.)

A progress update is not a reason to stop. Something completely unexpected can be a reason to halt if you wish. Size, cost inside the cap, and "this feels like a big step" are not. Go boldly!

## Done

1. Write `report.md`. Its first line is the status: done; pending, with the number of decisions waiting; stopped at the cap or a limit; or blocked, when an agent spawned you and a gap goes back to it. Then the result against the bar, with the check's output and the judge's ruling; where the work is; your taste calls and the findings you declined; spend against estimate and cap; what was not run, reached or verified; what the run launched, shown gone; and last, each stopped piece and its question, readable cold, with your recommendation.
2. Proof of done: audit each claim in the report against a tool result from this session, with the bar's check run by you. A hand-back, a page or a file that says so is a claim, not a result, and a file you say you wrote is one you have read back. What has no result behind it is reported as unverified; what failed is reported with its output.
3. On an unattended run, a separate judge then rules on done, seated as `unattended:arbiter` says under "The judge": commit the work and give it the brief and that commit, and nothing you wrote about the work. Its ruling goes into the report as it came. A requirement ruled not met or could not check means the first line cannot say done; "cannot tell" is a fail. After a fix, seat a fresh judge; two at most.
4. Add a line to `${CLAUDE_PLUGIN_DATA}/runs.md` (what ran, cost against estimate and cap, hours, status) and, where the meter is quota, a row to `${CLAUDE_PLUGIN_DATA}/exchange.md` (effective tokens by model, the meter before and after); the next brief estimates from them. Write each in a command of its own: the files sit outside the workspace, and a refused write takes everything else in its command with it.
5. End your last message with the report's status line and its last item in full. Nothing follows it.
