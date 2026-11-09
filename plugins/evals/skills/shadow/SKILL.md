---
name: shadow
description: "Tune a prompt-driven component (a router or selector, a skill, an agent prompt, a workflow step) by shadowing it live, one case at a time: write the input and a prediction of what it will do, run it, then the centaur expert (the agent drafts a pass/fail verdict and critique from the trace, the human rules) logs the verdict; prompt edits come from patterns across critiques, and the critiques become the prompt's worked examples. Critique shadowing, Hamel Husain's method, at the scale of a handful of cases. Use for \"/evals:shadow\", \"shadow this\", \"let's watch it run a few times\", \"one at a time, predict then run\", \"tune the selector\", or the first live runs of any new skill or prompt. Not for validating a judge whose numbers will be quoted (evals:judge) or for checking an existing score distribution (evals:audit)."
---

# Shadow a component, one case at a time

A new prompt-driven component has no eval set yet, and its first few runs teach the most. Shadowing means running it on real cases one at a time, predicting each result in writing first, and having the expert rule on every outcome. It is Hamel Husain's critique shadowing (one expert, pass/fail plus a critique, critiques become few-shot examples) shrunk to the size where a component is still taking shape. Writing the prediction down is a one-item preregistration: it stops the result from being rationalized after the fact, and a wrong prediction is itself a finding, about the component or about your model of it.

## The expert is a centaur

The expert is the human and the agent together. The agent reads the whole trace and drafts the verdict and critique; the human confirms or overrules, and the human's ruling is what goes in the log. That keeps the human's share to the ruling itself. When they disagree, the human wins, and the disagreement goes in the critique, because it shows where the agent's taste differs from the human's.

## Each case

1. **Pick the case.** Choose a real input, not a toy one, that exercises a different behavior from the cases already logged: another route, edge or failure mode. The first five or so should span the component's main branches.
2. **Show the input and the prediction before running.** Show the exact input the component will get (the args or prompt), then the prediction: what it will do (route, verdict, shape of the output), with a rough probability when it is a choice, and what would surprise you. Keep it short enough for the human to read in a minute.
3. **Run it**, once, as it will really be used: same settings and model.
4. **Draft the verdict from the trace**, not just the final output:
   - **pass or fail**, on one question: did it do what a good expert would have wanted for this input?
   - **a critique** a new hire could act on. For a pass, say what made it right. For a fail, name the first thing that went wrong and what should have happened instead.
   - **the prediction check**: hit or miss, and if missed, whether the component or the prediction was wrong.
   - **any defect outside the prompt's control** (a bug in the code, a missing input), to fix directly rather than tune around.
5. **Get the ruling.** Present the draft. The human confirms or overrules in a word or a line.
6. **Log one line** (below). Then pick the next case, one at a time unless the human asks for a batch.

## Turning critiques into changes

- **Fix bugs at once.** A code defect or a broken schema is not a matter of taste.
- **Change the prompt only on a pattern.** Wait until two or three fails share a cause; one case is an anecdote, and editing on anecdotes makes a prompt that zigzags. Say which logged cases the change answers.
- **Promote clear critiques to worked examples** in the prompt (input, decision, one-line reason), especially near a boundary between two behaviors. Keep the examples few, and keep the cases they came from out of any later test.
- **Re-run an earlier failing case after a prompt change**, as a regression check, and log it as a new line with the new prompt version.
- **Graduate when the log reaches about 30 cases.** At that point the critiques are a labelled set: if the component's decisions matter enough to quote a number, move to `evals:judge` (dev/test split, TPR and TNR) rather than continuing one by one.

## The log

One JSON line per case, appended to the log the component names (for example `gauntlet:auto` uses `~/.gauntlet/auto-log.jsonl`), else `~/.shadow/<component>.jsonl`:

```json
{"date": "2026-11-08", "component": "gauntlet:auto", "prompt_version": "<commit or hash>", "input": "<one-line summary, no secrets or private text>", "prediction": "<what and how sure>", "actual": "<what it did>", "prediction_hit": true, "draft": "pass|fail", "verdict": "pass|fail", "critique": "<one or two sentences>", "ruled_by": "human|agent-only"}
```

`ruled_by: agent-only` marks a line the human never ruled on; don't promote those to examples.

## Sources

- Hamel Husain, "Using LLM-as-a-Judge For Evaluation: A Complete Guide" (critique shadowing): https://hamel.dev/blog/posts/llm-judge/
