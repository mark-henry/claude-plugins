---
name: tune-prompt
description: "Tune a prompt-driven component (a router or selector, a skill, an agent prompt, a workflow step) by shadowing it live, one case at a time: show the input, seal a prediction of what it will do, run it, then the human expert rules pass or fail with a critique, while the agent's prediction and its own verdict stay sealed until the ruling is in and are then scored against it; prompt edits come from patterns across critiques, and the critiques become the prompt's worked examples. Critique shadowing, Hamel Husain's method, at the scale of a handful of cases. Use for \"/evals:tune-prompt\", \"tune this prompt\", \"shadow this\", \"critique shadowing\", \"let's watch it run a few times\", \"one at a time, predict then run\", \"tune the selector\", or the first live runs of any new skill or prompt. Not for validating a judge whose numbers will be quoted (evals:build-judge) or for checking an existing score distribution (evals:spot-check)."
---

# Tune a prompt by watching it, one case at a time

A new prompt-driven component has no eval set yet, and its first few runs teach the most. Shadowing means running it on real cases one at a time, committing to a prediction of each result before the run, and having the expert rule on every outcome. It is the first stage of Hamel Husain's [critique shadowing](https://hamel.dev/blog/posts/llm-judge/) (one expert rules pass or fail with a critique, and the thing gets fixed), at the size where a component is still taking shape. The prompt edited here is the component's own. A grader that stands in for the expert, with a number you can quote, is the next stage: `evals:build-judge`, whose test cases must be ones this tuning never used. Writing the prediction down is a one-item preregistration: it stops the result from being rationalized after the fact, and a wrong prediction is itself a finding, about the component or about your model of it.

## The human is the expert; the agent bets

The human rules on every case, and the human's ruling is what goes in the log. The agent never shows a prediction, a verdict, a leaning or a critique before that ruling: anything shown first anchors the expert it was meant to help. The agent still commits in writing, twice: a prediction of what the component will do, sealed before the run, and a reasoned bet on the ruling, sealed before the human sees the output. Both are opened only after the ruling and scored against it. A missed bet shows where the agent's taste differs from the human's.

**Sealing.** A seal is a line appended to `${CLAUDE_PLUGIN_DATA}/<component>.sealed.jsonl` (this plugin's data folder, which survives updates) (case id, time, text), plus a receipt shown to the human: the first 12 characters of the line's SHA-256 (`shasum -a 256`). The receipt proves the text existed before the run or the ruling without revealing it; when the seal is opened, the hash can be checked against the receipt. Never edit a sealed line; a changed mind is a new line.

## Each case

1. **Pick the case.** Choose a real input, not a toy one, that exercises a different behavior from the cases already logged: another route, edge or failure mode. The first five or so should span the component's main branches.
2. **Show the input; seal the prediction.** Show the exact input the component will get (the args or prompt), short enough for the human to read in a minute. Before running, seal your prediction: what the component will do (route, verdict, shape of the output), with a rough probability when it is a choice, and what would surprise you. Show only its receipt.
3. **Run it**, once, as it will really be used: same settings and model.
4. **Seal your bet.** Read the whole trace, not just the final output, and seal your own verdict, receipt only, before you show the human anything from the run:
   - **pass or fail**, on one question: did it do what a good expert would have wanted for this input?
   - **the reason**, in a sentence or two.

   A case the run itself broke (a crash, a missing input, a bug in the code) is not a case to rule on: say so, fix it directly rather than tune around it, and run again.
5. **Get the ruling, blind.** Show the human what the component did: its output and the parts of the trace that produced it, described without judgment. Ask one question: pass or fail, and why? Don't show the prediction or the bet, hint at either, say whether the run surprised you, or summarize it in words that lean. The human answers in a word or a line; their reason becomes the critique, written so a new hire could act on it (for a pass, what made it right; for a fail, the first thing that went wrong and what should have happened instead).
6. **Open both seals and score them.** Show the prediction and the bet with their receipts. The bet: hit or miss against the ruling; on a miss, ask the human what you missed if their reason doesn't already say, and put that in the critique. The prediction: hit or miss against what the component did, and if missed, whether the component or the prediction was wrong.
7. **Log one line** (below). Then pick the next case, one at a time unless the human asks for a batch.

## Turning critiques into changes

- **Fix bugs at once.** A code defect or a broken schema is not a matter of taste.
- **Change the prompt only on a pattern.** Wait until two or three fails share a cause; one case is an anecdote, and editing on anecdotes makes a prompt that zigzags. Say which logged cases the change answers.
- **Promote clear critiques to worked examples** in the prompt (input, decision, one-line reason), especially near a boundary between two behaviors. Keep the examples few, and keep the cases they came from out of any later test.
- **Re-run an earlier failing case after a prompt change**, as a regression check, and log it as a new line with the new prompt version.
- **Graduate when the log reaches about 30 cases.** At that point the critiques are a labeled set: if the component's decisions matter enough to quote a number, move to `evals:build-judge` (dev/test split, TPR and TNR) rather than continuing one by one.

## The log

One JSON line per case, appended to the log the component names (for example a routing prompt that keeps `router-log.jsonl` beside its own code), else `${CLAUDE_PLUGIN_DATA}/<component>.jsonl`:

```json
{"date": "2026-11-08", "component": "<name>", "prompt_version": "<commit or hash>", "input": "<one-line summary, no secrets or private text>", "prediction": "<what and how sure; sealed until the ruling>", "prediction_receipt": "<hash>", "actual": "<what it did>", "prediction_hit": true, "bet": "pass|fail", "bet_reason": "<sealed until the ruling>", "bet_receipt": "<hash>", "verdict": "pass|fail", "bet_hit": true, "critique": "<one or two sentences>", "ruled_by": "human|agent-only"}
```

`ruled_by: agent-only` marks a line the human never ruled on: its verdict is only the agent's bet, so don't promote it to an example or count it in `bet_hit`. The share of bets that hit, over the lines the human ruled, says how far the agent's taste tracks the human's on this component.
