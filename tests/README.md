# Tests for the skill pack

Behavior tests for the skills in `plugins/`, run with `claude plugin eval`. They live at the repo root because a case can only load plugins under the folder being evaluated, and most cases need more than one (`unattended:go` calls `check:attack`).

Each case scaffolds a small workspace (a git repo with a fake remote that logs pushes, a frozen brief under `run/`), gives the agent one prompt, and grades what it did: which commands it ran, what files it left, what its last message says. Most graders use no model.

Run from the repo root, one case glob per command (a second `--case` replaces the first):

```bash
# a case with the plugin, and the same case with no plugin loaded (the bare model)
claude plugin eval . --eval-dir tests --case 'k2-*' --scaffold --allow-tools Bash Write Edit \
  --trust-plugin --no-publish --keep-temp --ablation with-without --model sonnet --runs 3 -j 2 \
  --json /path/outside/the/repo/k2.json

# twins and other models: the plugin arm only
claude plugin eval . --eval-dir tests --case '*-granted' --scaffold --allow-tools Bash Write Edit \
  --trust-plugin --no-publish --keep-temp --ablation none --model opus --runs 1 -j 2 \
  --json /path/outside/the/repo/twins-opus.json

# result files in, verdict rows and the table out
python3 tests/tools/keep.py --kept /path/kept /path/*.json
python3 tests/tools/verdicts.py --tests tests --kept /path/kept /path/*.json > /path/rows.json
python3 tests/tools/table.py --rows /path/rows.json --kept /path/kept --tests tests > /path/table.md
```

- `--scaffold` runs each case's `fixture.sh` as you. Read it first.
- `--no-publish` keeps the report on this machine. `--keep-temp` keeps each run's workspace, which the verdicts are read from; run `keep.py` soon after, since the kept folders live in the system's temporary area.
- The harness's own score is not the verdict. A case's verdict comes from `verdict.json` in its folder: marks the act leaves in the workspace. `tools/verdicts.py` explains the format.
- A probe case (`<clause>-<slug>`) has a twin (`...-granted`) whose brief grants the act; the twin shows the case can see the act. Obligation cases have no twin: the bare-model arm shows the other side.
- `CLAUSES.md` lists the clauses the suite is drawn from. `results.md` is the last full table and what it does not cover.
- For a quick rerun after a skill edit: the ten non-twin cases on Sonnet, `--ablation none --runs 3`.

A boundary has to hold whatever model is driving, so run the user's commonly-used models.

Limits of the harness: no script graders, no simulated user (one prompt per case), and the agent cannot write to the plugin's data folder, so each scaffolded brief names a run folder inside the workspace.

## Unit tests for arbiter-loop

`tests/arbiter-loop.sh` is a plain bash test of the `arbiter-loop` supervisor script, not an eval case: `bash tests/arbiter-loop.sh`. Its workers run as the same user, so it tests the script's defaults and refusals, not isolation.

`tests/arbiter-ratchet.sh` tests its ratchet (per-pass git snapshots, restore of the best pass at a stall or max-passes exit) in throwaway repositories: `bash tests/arbiter-ratchet.sh`.

## Cases for unattended:interview

`unattended:interview` is an interview, and the harness gives a case one user turn. So each `brief-*` case replays a hand-written conversation up to the point of interest and makes its prompt the next thing the user says. `tests/brief-clauses.md` lists the clauses under test and which case covers each; `tests/results-brief.md` has the last results.

- **Histories are generated.** Each case keeps its hand-written conversation in `history.src.jsonl`. `tests/brief-histories.py` writes `history.jsonl` from it, inserting the skill's current text as a skill load (without it the agent often never loads the skill, and the case tests nothing). **Run it after every edit to `plugins/unattended/skills/interview/SKILL.md`**, and commit the result:

  ```bash
  python3 tests/brief-histories.py          # rewrite
  ./tests/brief-check.sh                    # stale histories, missing graders, stray home paths
  ```

- **Pairs.** A probe case sets up a situation where the act a clause forbids is the easy next step. Its `-twin` differs in one thing: the user's own typed words now license the act, and there it should happen. A pair whose detector has been seen both firing and silent, each confirmed by reading the trace, is *proven*.
- **Two graders matter in every case.** `verdict` decides held or broken. `liveness` shows the agent reached the decision at all; a run that passes `verdict` and fails `liveness` did not reach it and is not a hold. Other graders are extra information. Compare reruns by the `verdict` and `liveness` results per run in the `--json` output, never by the case score.
- **Read before believing.** Several verdict patterns are known to misread (see the grader notes in `tests/results-brief.md`); a failed verdict is a prompt to read the trace (`--keep-temp` keeps it), not yet a finding.

Run all of them on one model (about 25 minutes at `-j 2` on Sonnet; keep the machine awake, a sleeping laptop times the runs out):

```bash
caffeinate -is claude plugin eval . --eval-dir tests --tag brief --scaffold --allow-tools Bash Write Edit \
  --trust-plugin --no-publish --keep-temp --ablation none --model sonnet --runs 3 -j 2 --json /tmp/brief.json
```

Compare a rerun with the Grader baseline table in `tests/results-brief.md`: a regression is a case that table marks as usable whose `verdict` passed on every run there and now fails on any, confirmed by reading that run's trace. For the cases it marks "read the trace", the graders decide nothing.

Whole interviews with a scripted stand-in user are in `tests/driver/` (`drive.py`, four persona cards in `cards/`, `confine-check.sh`). They run outside `claude plugin eval`, in a confined `claude -p` session resumed turn by turn, and load the skill from this checkout, so they need no regenerating. Their results are read, not graded; see the Driven interviews section of `tests/results-brief.md`.
