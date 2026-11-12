---
name: shadow
description: "Tune a prompt-driven component (a router or selector, a skill, an agent prompt, a workflow step) by shadowing it live, one case at a time: write the input and a prediction of what it will do, run it, then the human expert rules pass or fail with a critique, while the agent's own verdict stays sealed until the ruling is in and is then scored against it; prompt edits come from patterns across critiques, and the critiques become the prompt's worked examples. Critique shadowing, Hamel Husain's method, at the scale of a handful of cases. Use for \"/evals:shadow\", \"shadow this\", \"let's watch it run a few times\", \"one at a time, predict then run\", \"tune the selector\", or the first live runs of any new skill or prompt. Not for validating a judge whose numbers will be quoted (evals:judge) or for checking an existing score distribution (evals:audit)."
---

# Shadow a component, one case at a time

A new prompt-driven component has no eval set yet, and its first few runs teach the most. Shadowing means running it on real cases one at a time, predicting each result in writing first, and having the expert rule on every outcome. It is Hamel Husain's critique shadowing (one expert, pass/fail plus a critique, critiques become few-shot examples) shrunk to the size where a component is still taking shape. Writing the prediction down is a one-item preregistration: it stops the result from being rationalized after the fact, and a wrong prediction is itself a finding, about the component or about your model of it.

## The human is the expert; the agent bets

The human rules on every case, and the human's ruling is what goes in the log. The agent never shows a verdict, a leaning or a critique before that ruling: a draft shown first anchors the expert it was meant to help. The agent may still commit to a reasoned bet, written down and sealed before the human sees the case, and opened only after the ruling. The bet is scored against the ruling, and a miss shows where the agent's taste differs from the human's.

## Each case

1. **Pick the case.** Choose a real input, not a toy one, that exercises a different behavior from the cases already logged: another route, edge or failure mode. The first five or so should span the component's main branches.
2. **Show the input and the prediction before running.** Show the exact input the component will get (the args or prompt), then the prediction: what it will do (route, verdict, shape of the output), with a rough probability when it is a choice, and what would surprise you. Keep it short enough for the human to read in a minute.
3. **Run it**, once, as it will really be used: same settings and model.
4. **Seal your bet.** Read the whole trace, not just the final output, and write your own verdict where the human will not see it (the log line's `bet` and `bet_reason` fields, or a file) before you show them anything from the run:
   - **pass or fail**, on one question: did it do what a good expert would have wanted for this input?
   - **the reason**, in a sentence or two.

   A case the run itself broke (a crash, a missing input, a bug in the code) is not a case to rule on: say so, fix it directly rather than tune around it, and run again.
5. **Get the ruling, blind.** Show the human what the component did: its output and the parts of the trace that produced it, described without judgment. Ask one question: pass or fail, and why? Don't show the bet, hint at it or summarize the run in words that lean. The human answers in a word or a line; their reason becomes the critique, written so a new hire could act on it (for a pass, what made it right; for a fail, the first thing that went wrong and what should have happened instead).
6. **Open the bet and score it.** Hit or miss against the ruling. On a miss, ask the human what you missed if their reason doesn't already say; that goes in the critique. Also check the prediction from step 2: hit or miss, and if missed, whether the component or the prediction was wrong.
7. **Log one line** (below). Then pick the next case, one at a time unless the human asks for a batch.

## Turning critiques into changes

- **Fix bugs at once.** A code defect or a broken schema is not a matter of taste.
- **Change the prompt only on a pattern.** Wait until two or three fails share a cause; one case is an anecdote, and editing on anecdotes makes a prompt that zigzags. Say which logged cases the change answers.
- **Promote clear critiques to worked examples** in the prompt (input, decision, one-line reason), especially near a boundary between two behaviors. Keep the examples few, and keep the cases they came from out of any later test.
- **Re-run an earlier failing case after a prompt change**, as a regression check, and log it as a new line with the new prompt version.
- **Graduate when the log reaches about 30 cases.** At that point the critiques are a labelled set: if the component's decisions matter enough to quote a number, move to `evals:judge` (dev/test split, TPR and TNR) rather than continuing one by one.

## The log

One JSON line per case, appended to the log the component names (for example `gauntlet:auto` uses `~/.gauntlet/auto-log.jsonl`), else `~/.shadow/<component>.jsonl`:

```json
{"date": "2026-11-08", "component": "gauntlet:auto", "prompt_version": "<commit or hash>", "input": "<one-line summary, no secrets or private text>", "prediction": "<what and how sure>", "actual": "<what it did>", "prediction_hit": true, "bet": "pass|fail", "bet_reason": "<sealed until the ruling>", "verdict": "pass|fail", "bet_hit": true, "critique": "<one or two sentences>", "ruled_by": "human|agent-only"}
```

`ruled_by: agent-only` marks a line the human never ruled on: its verdict is only the agent's bet, so don't promote it to an example or count it in `bet_hit`. The share of bets that hit, over the lines the human ruled, says how far the agent's taste tracks the human's on this component.

## Sources

- Hamel Husain, "Using LLM-as-a-Judge For Evaluation: A Complete Guide" (critique shadowing): https://hamel.dev/blog/posts/llm-judge/
