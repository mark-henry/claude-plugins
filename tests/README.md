# Tests for the skill pack

Behavior tests for the skills in `plugins/`, run with `claude plugin eval`. They live at the repo root because a case can only load plugins under the folder being evaluated, and most cases need more than one (`swarm:go` calls `check:attack`).

Each case scaffolds a small workspace (a git repo with a fake remote that logs pushes, a frozen brief under `run/`), gives the agent one prompt, and grades what it did: which commands it ran, what files it left, what its last message says. Most graders use no model.

Run from the repo root:

```bash
claude plugin eval . --eval-dir tests --scaffold --allow-tools Bash Write Edit \
  --trust-plugin --no-publish --model haiku --runs 3
```

- `--scaffold` runs each case's `fixture.sh` as you. Read it first.
- `--no-publish` keeps the report on this machine.
- `--case <name>` runs one case; `--ablation none` skips the no-plugin arm.
- Results land in `tests/results/`, which git ignores.

A boundary has to hold whatever model is driving, so run the user's commonly-used models.

Limits of the harness: no script graders, no simulated user (one prompt per case), and the agent cannot write to the plugin's data folder, so each scaffolded brief names a run folder inside the workspace.

## Cases for swarm:brief

`swarm:brief` is an interview, and the harness gives a case one user turn. So each `brief-*` case replays a hand-written conversation up to the point of interest and makes its prompt the next thing the user says. `tests/brief-clauses.md` lists the clauses under test and which case covers each; `tests/results-brief.md` has the last results.

- **Histories are generated.** Each case keeps its hand-written conversation in `history.src.jsonl`. `tests/brief-histories.py` writes `history.jsonl` from it, inserting the skill's current text as a skill load (without it the agent often never loads the skill, and the case tests nothing). **Run it after every edit to `plugins/swarm/skills/brief/SKILL.md`**, and commit the result:

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

Not built: whole-interview tests with a stand-in user (a script around `claude -p --resume`). The route was piloted and works; see the notes at the end of `tests/results-brief.md`.
