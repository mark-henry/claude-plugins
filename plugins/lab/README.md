# lab

One skill, `lab:experiment`, and its script `prereg.py`: standard checks for a single ML experiment, so the number it produces means what it will be quoted as meaning.

## What it assumes

- **The code is in git.** `prereg.py stamp` snapshots the working tree under `refs/lab/<run id>`, and `parity` compares arms by diffing commits. Outside a git repository the stamp prints a warning and takes no snapshot, so nothing ties a number to the code that produced it.
- **Runs have an id from a tracker** (MLflow, W&B, an Inspect log). The script never contacts the tracker; the id is a string you pass with `--run-id`, and every quoted number must carry it. With no tracker, the id falls back to the folder name and time.
- **Your harness writes `items.jsonl` in each run folder:** one JSON object per scored item with `id`, `arm`, `unit`, `score` and `status`. The checks read only this file. A harness that reports an aggregate and no per-item rows cannot be checked.
- **Each arm is one launch command** that can be wrapped as `prereg.py stamp <out> ... -- <command>`.
- **Python 3 with the standard library.** No packages are installed.
- **One experiment at a time:** a comparison between named arms on one primary metric. It does not manage sweeps, schedules or compute.

## What it points to but does not need

The skill mentions `afk:eyebrow` (a skeptic's look at the design), `evals:build-judge` and `evals:spot-check` (for LLM judges and scored samples), and `afk:interview` and `afk:go` (for deciding what is wanted and for large unattended runs). They are separate plugins; `lab` works without them.
