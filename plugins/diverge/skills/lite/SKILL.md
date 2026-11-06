---
name: lite
description: "A quick multi-agent recommendation as a Workflow: five independent stances each propose one fix, a red-teamer attacks each, and a judge (Fable by default) picks or combines. Use for \"diverge lite\", \"/diverge:lite\", \"with more compute\", \"five ideas\", \"think harder with agents\", when a recommendation deserves more than one pass but not a full diverge:design run. Not for a bare \"what would you recommend\"."
---

# Diverge lite

Invoking this skill is the user's opt-in to running a Workflow (11 agents, a few minutes). The script is `diverge-lite.js` in this directory. `scriptPath` refuses plugin paths, so copy it to your scratchpad and run `Workflow({scriptPath: "<scratchpad>/diverge-lite.js", args: {...}})`.

Shape: five stance proposers (direct, outside, adversary, skeptic, minimal), each with one red-teamer, pipelined; then one judge sees every proposal and attack under letters and picks or combines. No interview, no sandboxes, read-only agents. If the pick needs a prototype or measurement to settle it, escalate to `/diverge:design`.

## Before launch, in this order

1. **Seal your own answer.** Write your single-pass recommendation to `<scratchpad>/sealed.md` first. It stays out of the agents' prompts; it's the baseline you compare against afterwards.
2. **Write `context` for strangers.** The agents know nothing of this conversation. Give facts: numbers with denominators, file paths to open, what was tried and what happened. Leave out your diagnosis and your earlier options (see the anchoring rules in [../design/SKILL.md](../design/SKILL.md), "Writing args without anchoring").
3. **Lint it.** Grep `context` for the sealed answer's key terms; rewrite each hit as a fact or delete it.
4. **Launch from this turn.** The harness relays the triggering user message to every agent. That's fine unless the message itself carries a diagnosis or candidate fixes; then use the full skill's one-shot `CronCreate` launch instead.

No argument given: restate the user's last question neutrally as `question`.

## Args

| arg | meaning |
|---|---|
| `question`, `context` | required |
| `constraints`, `bar` | optional; `bar` is what a good answer achieves |
| `judge` | `fable` (default, high effort) or `opus` (xhigh): the cheap switch |
| `control`, `sealed` | `control: true` with `sealed` (your sealed answer's text) adds one blind pairwise agent: workflow pick vs your sealed answer, better/tie/worse |
| `stances`, `models`, `efforts` | overrides; defaults propose medium, attack high, control xhigh |

Run with `control: true` about every third time; the trend over ten runs says whether lite beats a single pass, no single run does.

## After it returns

Relay `verdict` first. Then one line on how it differs from your sealed answer and where you disagree with it; never override it silently. Add a row to [runs.md](runs.md).
