---
name: experiment
description: "Standard checks for a single ML experiment (a fine-tune, an RL or rejection-sampling run, an LLM eval or judge, a skill test) so its number means what it will be quoted as meaning: fourteen lines, a script that stamps each run and refuses the label counted when they fail, and a fresh-agent sign-off. Use for \"/lab:experiment\", \"design this experiment\", \"what do you think of this design?\", \"set up this ablation\", \"what controls do I need?\", \"how many seeds?\", \"is this null real?\", \"prereg\", \"preregister\", \"sign off on this run\", \"can I quote this number?\", \"check the run record\", before a paid training or eval run, before any run whose number will be compared to a bar, reported or used to pick between arms, and when a surprising number is about to be quoted or built on. Not for deciding what is wanted and the cap (unattended:interview), large or unattended runs (unattended:go), validating an LLM judge (evals:build-judge), reading a sample of scored items (evals:spot-check)."
---

# lab:experiment

This skill assumes the code is in git and runs log to a tracker (MLflow, W&B, Inspect logs); without them its behavior is undefined. The tool is `prereg.py` in this directory; it stores the tracker's run id as a string and exits 1 on a refusal, naming the line.

Every run folder holds `stamp.json`, written by `stamp` at launch, and `items.jsonl`, written by your harness: one JSON object per line with `id`, `arm`, `unit`, `score` (a number, or null) and `status` (`ok`, `error`, `empty`, `truncated` or `parse_failure`).

## Exploratory run (the light path)

```
python3 prereg.py stamp runs/try1 --run-id <tracker id> -- <launch command>
<launch command>                       # stamp records it; it does not run it
python3 prereg.py check runs/try1      # lines 2 and 12 from items.jsonl
```

The stamp snapshots the working tree (untracked files included, `.gitignore` respected) under `refs/lab/<run id>` with the command, configuration, model, data hashes, seeds and packages. Uncommitted code gets a warning. A stamp is never overwritten: a new run gets a new folder. Its numbers are quoted as exploratory: they pass no bar and pick no arm.

## Counted run

1. `prereg.py new prereg/<slug>.json`, then fill it in: question, bar, decision, `primary` (metric, comparison, smallest effect as a number, unit), `intended_n`, the arms with each one's `out` folder, `command` and `data` file paths, `varies` (the keys allowed to differ between arms, e.g. `model`, `config.lr`, `code`; an arm's own name and folder never count, but different seeds per arm need `seed` and `seeds`), `pilot.runs`, `scorer`, `floors.runs`. A `bar` starting "none" opens the record exploratory.
2. Run two baseline pilot runs on the same units, each stamped with its own run id, and list their folders in `pilot.runs`. Counted also needs line 3's scorer and a whole-number `intended_n`.
3. `prereg.py open <record>` hashes the frozen fields and the line-6 fields, and records each data file's sha256 and line count. Commit the record. Missing line-6 fields open it exploratory. A record opened wrongly is left as it is: set its `status` to `abandoned` and start a new one.
4. Launch each arm: `prereg.py stamp <arm out> --record <record> --arm <arm> --counted --run-id <tracker id> --config <file> --model <id> --model-revision <rev> --data <file> --seed <n> -- <command>`. For an API model give `--model-date`; for a container, `--image <digest>`; with no model, omit `--model`. `--counted` is refused unless line 6 was hashed and line 7 holds; drop it and the run goes ahead exploratory.
5. `prereg.py check <record>`: lines 2, 3, 7, 8 and 12, and the counted gate. It writes `<record>.check.json`.
6. `prereg.py parity <record>`: line 13. `quote` refuses a counted record without a pass.
7. Each time the test split is scored, once per scoring and not per arm: `prereg.py ledger <record> <run folder>`. Report the count it prints.
8. `prereg.py close <record>`, then `prereg.py quote <report.md> <record>` before the report leaves your hands.

`prereg.py ls` lists records. An old record (no `schema`) still works with `close`, `ls` and `parity`; `prereg.py induct <record>` checks what can be checked after the fact, marks the rest "not established", and never edits the record.

Optional: list inputs outside the repository (a remote model revision, data on another disk) in `lab-inputs.md` at its root; `stamp` records its hash.

## The fourteen lines

1. **Read ten raw items per arm before any aggregate.** The stored input, output and judge output, not a rendered view.
2. **Scored n equals intended n; failure rates per arm, equal across arms.** `check` refuses otherwise (default threshold 5% and at least 2 items, set in `failure_threshold`). On a refusal, read ten raw items in each arm, failed ones included (line 1), before anything is aggregated or reported.
3. **The scorer fails a broken output and passes a known-good one.** Declare `scorer.command` (with `{output}`, exit 0 is a pass), `scorer.file`, `scorer.broken` and `scorer.good`. Make the broken one a near miss, not garbage.
4. **The baseline reproduces in this harness.** Rerun it here first; a gap you cannot explain stops the comparison.
5. **Name the independent unit; intervals resample that unit.** Usually the document, task or user, not the sample. With fewer than about 30 units, report win, loss and tie counts and a permutation test.
6. **One primary metric, comparison and smallest effect, written before scoring.** `open` hashes them.
7. **The detectable difference from pilot data is at most that effect, or the run is exploratory.** `check` prints the SE (unit resampling of two baseline runs' paired difference) and 2.8 × SE. Power gates the label, never the run; an exploratory result inside the noise is worded as line 10 says. To lower it, add units of middling difficulty before adding runs per unit.
8. **Count saturated items; they are not your n.** `check` prints the count at 0 and at 1 over the pilot runs.
9. **Pick on dev, count what was tried, confirm the pick once on test with fresh seeds.** `ledger` counts test scorings; a count above one is reported.
10. **Inside the noise is "no detectable difference at plus or minus X"; every number carries a run id.** Never "no effect". `quote` refuses a report line with a percentage or `a/b` and no run id.
11. **Train, dev and test share no unit; an LLM judge or baseline gets one item per call.** A baseline that reproduces the answer verbatim is a leak until audited.
12. **Score trivial policies (random, constant, best fixed rule, padded output) with the metric and any training reward on the real items; report floors beside results.** Write them to `items.jsonl` as arms named `floor:<name>`. Counted is refused with no floor arm and no `floors.none_reason`, or when a floor reaches the best arm.
13. **Recompute per arm, from the files actually loaded, example count, tokens, source mix and hash; differences between arms or from recorded values must be declared.** `stamp` refuses a data file whose hash or line count differs from the record; `parity` refuses any difference in configuration, model, data, seeds, packages or code that `varies` does not name. Tokens and source mix come from the harness.
14. **Before the run, raise an eyebrow at the design.** Run `check:eyebrow` on it with one added question: what is the cheapest way to score well without doing the task? Test that way; line 12 scores it.

## Judgment the script does not make

- Lines 1, 4, 5, 9, 11 and 14 are yours; the script only prints.
- A positive control, a treatment with a known effect run through every stage, is recommended where one exists; whether to run it is the agent's and the user's call. A failed one means the plumbing is broken: stop.
- For a fine-tune: confirm the intended checkpoint or adapter actually loaded, and read one fully rendered input as the model receives it.

## Sign-off

Only for a number that leaves the user's hands. Give one fresh agent the run folders, the record, `<record>.check.json`, the parity and quote output and the sentence as it will be quoted, never your own account of the run. It reruns the commands, reads raw items, and says whether the sentence is fit to quote, as counted or as exploratory, naming each line that fails. It fixes nothing.
