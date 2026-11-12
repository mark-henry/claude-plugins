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
