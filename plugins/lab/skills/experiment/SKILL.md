---
name: experiment
description: "Standard checks for a single ML experiment (a fine-tune, an RL or rejection-sampling run, an LLM eval or judge, a skill test) so its number means what it will be quoted as meaning: procedural lines, a script that stamps each run, keeps a ledger of runs and findings, and refuses counted when a line fails, and a fresh-agent sign-off. Use for \"/lab:experiment\", \"design this experiment\", \"what do you think of this design?\", \"set up this ablation\", \"what controls do I need?\", \"how many seeds?\", \"is this null real?\", \"prereg\", \"preregister\", \"sign off on this run\", \"can I quote this number?\", \"check the run record\", \"what have we already run?\", before a paid training or eval run, before any run whose number will be compared to a bar, reported or used to pick between arms, and when a surprising number is about to be quoted or built on. Not for deciding what is wanted and the cap (afk:interview), large or unattended runs (afk:go), validating an LLM judge (evals:build-judge), reading a sample of scored items (evals:spot-check)."
---

# lab:experiment

The code is in git and runs log to a tracker (MLflow, W&B, Inspect logs). The tool is `prereg.py` in this directory; it exits 1 on a refusal, naming the line. Field-by-field detail, edge cases and old formats: [reference.md](reference.md).

**First, run `prereg.py ls` and read the recent findings; then `prereg.py ls <words>` for the question you are about to ask.** `runs.jsonl` at the repository root holds every stamped run, its findings and closed results; someone may have run this already.

A run is counted or it is not. Any number said to anyone carries a run id, counted or not. A run with no stamp has no run id, so its numbers are not quoted. Give the tracker run the same id (`--run-id`).

## Any run

```
python3 prereg.py run runs/try1 --run-id <tracker id> -- <command>    # stamp, then run it; exit code passed through
python3 prereg.py check runs/try1                                      # lines 2 and 12 from items.jsonl
python3 prereg.py note <run id> "<one-sentence finding>" [--changes "<what it changed>"]
```

`run` snapshots the working tree under `refs/lab/<run id>`, writes `stamp.json` and appends to `runs.jsonl`. Use `stamp` (same options, does not execute) when the harness launches elsewhere. One command writing several arm folders: `--arms base,A,Q5,floors` stamps `<out>/<arm>` each, run ids `<id>-<arm>`; `floor*` names are stamped as plain runs. The harness writes `items.jsonl` in each folder: `id`, `arm`, `unit`, `score` (number or null), `status` (`ok`, `error`, `empty`, `truncated`, `parse_failure`). Note a finding for every run you learn something from.

## Counted run

1. `prereg.py new prereg/<slug>.json`, fill it in (fields: reference.md), give every bar and hypothesis a capitalized name that says what it claims (`B1_LOADBEARING`), and cite it by that name.
2. Pilot on the real items before `open`, stamped, listed in `pilot.runs`. When the independent unit is an item and the run has at least about 100 units, one small pilot read by hand is enough: set `pilot.noise_from` to `"items"` and the noise comes from the items. When the unit is a run (training seeds, RL), two pilots with different seeds.
3. `prereg.py open <record>`, then commit it.
4. Launch: `prereg.py run <out> --record <record> --arms <arms> --counted --run-id <id> [--config --model --model-revision --data --seed] -- <command>`. `--counted` is refused unless lines 6 and 7 hold; drop it and the run goes ahead uncounted.
5. `prereg.py check <record>` (lines 2, 3, 7, 8, 12, the counted gate; prints `counted: true|false`), `prereg.py parity <record>` (line 13).
6. A harness fix that leaves the scorer's meaning unchanged and must land after `open`: add `{"commit", "change"}` to the record's `after_open` list, and restamp with a new run id. `check` prints the list. Anything that changes what is scored needs a new record.
7. Each test-split scoring: `prereg.py ledger <record> <run folder>`. Then `prereg.py close <record>` and `prereg.py quote <report.md> <record>` before the report leaves your hands.

## Lab procedure

1. **Read ten raw items per arm before any aggregate.** The stored input, output and judge output, not a rendered view.
2. **Scored n equals intended n; failure rates per arm, equal across arms.** On a refusal, read ten raw items per arm, failed ones included, before aggregating.
3. **The scorer fails a broken output and passes a known-good one.**
4. **The baseline reproduces in this harness.** A gap you cannot explain stops the comparison.
5. **Name the independent unit; intervals resample that unit.** With fewer than about 30 units, report win, loss and tie counts and a permutation test.
6. **One primary metric, comparison and smallest effect, written before scoring.**
7. **The detectable difference from pilot data is at most that effect, or the run is not counted.** When the primary is derived (a ratio or difference of cell rates), line 7 checks its components, and the record must say so. To lower it, add units of middling difficulty before runs per unit.
8. **Count saturated items; they are not your n.**
9. **Pick on dev, count what was tried, confirm the pick once on test with fresh seeds.**
10. **Inside the noise is "no detectable difference at plus or minus X".** Never "no effect". `quote` refuses a rate with no run id.
11. **Train, dev and test share no unit; an LLM judge or baseline gets one item per call.** A baseline that reproduces the answer verbatim is a leak until audited.
12. **Score trivial policies with the metric and any training reward on the real items; report floors beside results.** The floors include a constant answer and the majority answer scored on this exact item draw, checked before the run (a 40-item draw once let a constant guess score 62%).
13. **Recompute per arm, from the files actually loaded, example count, tokens, source mix and hash; declare differences.**
14. **Before the run, raise an eyebrow at the design.** Run `afk:eyebrow` with one added question: what is the cheapest way to score well without doing the task? Test that way; line 12 scores it. Its search covers the literature, not this project's own past runs; `prereg.py ls <words>` covers those.

Lines 1, 4, 5, 9, 11 and 14 are yours; the script only prints. A positive control is recommended where one exists. For a fine-tune, confirm the intended checkpoint loaded and read one fully rendered input.

## Sign-off

Only for a number that leaves the user's hands. Have a fresh agent (a careful reader that will not round a number) red-team the sentence as it will be quoted, given the run folders, the record, `<record>.check.json`, the parity and quote output (never your own account of the run) and the fourteen lines. Have it rerun the commands, read raw items, and say whether the sentence is fit to quote, counted or not, naming each line that fails.
