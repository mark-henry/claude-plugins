# Tests for the skill pack

Behavior tests for the skills in `plugins/`, run with `claude plugin eval`. They live at the repo root because a case can only load plugins under the folder being evaluated, and most cases need more than one (`swarm:go` calls `check:attack`).

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
