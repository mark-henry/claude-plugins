---
name: launch
description: "Preregister a comparison before its runs launch: a numeric prediction per arm and metric, the denominator fixed in advance, the commit and uncommitted diff stamped, then a parity check that the arms differ only where intended and a close that scores predicted against observed. Use for \"prereg\", \"preregister\", \"/prereg:launch\", before any run whose number will be compared to a bar, reported (design doc, deck, Slack, vault) or used to choose between arms, at any cost. Not for smoke tests or slow-start rungs."
---

# Preregister, launch, close

A number that decides something gets a prediction written before the run, a denominator chosen before the run, and a record of the code it ran on. Afterwards it's scored against that prediction, and the arms are checked for differences nobody intended. The helper is `prereg.py` in this directory (stdlib only); call it as `python3 <this dir>/prereg.py`.

This skill doesn't restate rules the user already has: lock an undefined bar with `brief:lock` first; consult Fable before spend over ~$10; slow start; prompts best of three; read traces before turning knobs. It adds what those leave out: the written prediction, the fixed denominator, provenance, parity and scoring.

## When it applies

Trigger on consequence, not cost. A $0.50 run that will pass or fail a design-doc gate row needs a record. A $5 exploration whose numbers nobody will quote doesn't. Smoke tests and slow-start rungs (1 sample, ~10) are exploratory and are not part of the comparison's n.

## Steps

1. **Bar.** Name the bar as `file#CODENAME` (e.g. `concealment_tasks/twentyninebench/DESIGN.md#SFT-PARITY`). If the bar doesn't say its denominator (out of all samples? out of attempts?), it isn't locked: run `brief:lock` on it, or mark the record exploratory.
2. **Write the record.** Run `prereg.py new prereg/<YYYY-MM-DD>-<slug>.json` in the repo root, outside gitignored log folders. Fill it in:
   - `question` and `decision`: what you do on pass and on fail.
   - `arms`: each arm's out dir and command.
   - `varies`: the launch args the arms are meant to differ in.
   - `metrics`: each one as `num` and `den`, either report-JSON paths or numbers.
   - `predictions`: a `[low, high]` rate per arm and metric.
   - `max_usd`.

   Write the predictions yourself, before seeing any sample of a treated arm, smoke rungs included. A reused earlier run is an arm with `"reused": {"commit": "<sha or unrecoverable>", "reason": "..."}`.
3. **Open.** `prereg.py open <record>` validates the record, freezes the question, arms, metrics and predictions, and stamps the commit, the dirty files and the uncommitted diff. Commit the record before launching if it gates a design-doc row or the run costs over $10; otherwise commit it with the results.
4. **Launch** each arm, one at a time, with the plan or dry run first. Run folders need a commit stamp. If the harness doesn't write `git` into `launch.json`, run `prereg.py stamp <out_dir> -- <command>` just before launching.
5. **Parity.** `prereg.py parity <record>` compares the arms' launch args outside `varies`, their instance files (hashes), their commits (with any change to watched code listed) and any dirty trees. A failure means the comparison isn't clean: rerun the stale arm at the current commit (usually cheaper than arguing), or report the failure next to the number.
6. **Close.** `prereg.py close <record> --note "..."` prints observed against predicted, hit or miss, on the declared denominators, and sets the status. It refuses if the frozen fields have changed since open.

## Reporting

A number from a record that goes into a design doc, deck, Slack post or the vault carries `prereg <file>: predicted X, got Y (n/N)`. Otherwise it carries the word *exploratory*, and an exploratory number cannot pass or fail a gate row. Quote any other denominator only labeled post hoc. If a verdict flips with the denominator, say so: that is a finding about the bar, not a choice to make after the fact.

`prereg.py ls` lists open records and the calibration over closed ones (intervals hit, mean width). Wide intervals that always hit aren't predictions.

## Teammates' launchers

If a launcher already preregisters (e.g. a config with `meta.hypothesis` and `meta.success` written before running, and a run folder holding the commit and `code.diff`), don't duplicate it. Write a record only to run `parity` and `close` over its outputs.
