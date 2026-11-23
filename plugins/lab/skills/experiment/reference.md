# lab:experiment reference

Detail moved out of SKILL.md. Read it when filling in a record or when `prereg.py` refuses something you do not understand.

## Record fields (`prereg.py new`)

- `question`, `bar`, `decision`. A `bar` starting "none" opens the record with status exploratory: its runs are never counted.
- `primary`: `metric`, `comparison`, `smallest_effect` (a number), `unit` (as written in items.jsonl), `range` (`[lo, hi]`, the scores the metric can take; counted needs it), `higher_is_better`. `open` hashes metric, comparison, smallest effect and unit (line 6); missing ones open the record exploratory.
- `intended_n`: a whole number, items per arm. When one unit has several cell rows, say which you counted (rows or units) in the record.
- `arms`: each with `out` (its run folder), `command`, `data` (file paths; `open` records sha256 and line count, and `stamp` refuses a file that differs).
- `varies`: the stamp fields allowed to differ between arms (`model`, `config.lr`, `code`); empty when only the arm differs. An arm's own name and folder never count. Different seeds per arm need `seed` and `seeds`.
- `pilot`: `runs` (stamped folders, run before `open`), `pass_at` (line 8's pass threshold), `noise_from` (`"runs"` by default: two pilots, SE of their paired difference; `"items"`: one pilot, SE = sqrt(2) x sd of unit means / sqrt(units per arm), unpaired, needs about 100 units in the run and pilot units the arms score), `deterministic` (a reason, only for a harness with no randomness; then identical pilots are accepted and `check` prints `counted: true (deterministic harness declared)`).
- `scorer`: `command` (with `{output}`, exit 0 is a pass), `file`, `broken`, `good` (line 3).
- `floors`: `runs` (plain stamped folders whose items.jsonl arms are named `floor:<name>`), or `none_reason` (a sentence). Counted is refused with no floor and no reason, when a floor has no scored item, or when a floor reaches the best arm.
- `failure_threshold`: `share` (default 0.05), `min_items` (2), `difference` (between arms).
- `units_differ_reason`: only when arms legitimately score different item or unit ids.
- `after_open`: harness fixes landed after `open` that leave the scorer's meaning unchanged, each `{"commit": ..., "change": ...}`. Not frozen; `check` prints them. A fix that changes what is scored needs a new record.
- A wrongly opened record: set `status` to `abandoned` (never counted) and start another.

## What the script enforces

- Stamps are never overwritten; a run id is used once (`refs/lab/<run id>`), failed launches aside (next section). Uncommitted and untracked code is in the snapshot; `.gitignore`d files and files over 5 MB (listed by hash) are not; `runs.jsonl` is not.
- A stamp or check result carries `counted: true|false`. Ones written before the boolean carry a `label` string ("exploratory", "counted", "counted, pending parity", with the deterministic-harness suffix) and are read the same way; `parity` rewrites an old check result in the new form when it updates it.
- `check` given several run folders reads them as one run: check each pilot folder on its own.
- `--counted` is refused without `--record`, without hashed line-6 fields, with fewer than two arms, into a folder that already holds scored items, or when line 7 fails.
- Runs stamped under another record, or with a scorer that has changed since, are never counted under this one: stamp and score them again.
- `check` until `parity` passes prints `counted: false (pending parity: ...)`.
- `quote` and `close` refuse until `check` has run and refused no line, and whenever anything `check` or `parity` judged has changed since. A run failing only the counted gate (power, pilots, floors) is quoted and closed, not counted. `quote` refuses the word "counted" unless the run is ("not counted" is always allowed).
- Line 10: `quote` refuses a report line with a percentage or `a/b` and no run id of the record's arms, pilots, floors or test-split ledger.

## Failed launches

- `run` calls a non-zero exit a failed launch when the run folder holds no file besides its stamps (empty directories are nothing; a log file is something). `--outputs GLOB` (repeatable, read against OUT, `**` allowed) replaces that test for a harness that logs into the folder before it dies or writes its outputs elsewhere: an output is then a file matching a glob and written since the launch began. With `--arms`, the launch failed only if every arm folder is empty, and then every arm is freed.
- On a failed launch `run` moves `stamp.json` to `stamp.failed-<n>.json` and the snapshot to `refs/lab/<launch id>.failed-<n>`, writes the `exit` line with `launch_failed: true`, `attempt` and `stderr_tail` (the last five stderr lines), prints `launch failed (exit N), nothing scored; rerun the same command to retry as attempt <n+1>`, and exits with the command's code. The command's stderr still streams as it arrives.
- A `run` or `stamp` into a freed folder keeps the run id (a generated one too; another `--run-id` is refused), takes a fresh snapshot and writes `attempt: <n+1>` in the stamp and its ledger line; no `attempt` means 1. A counted arm may be retried this way: nothing was scored. A code change between attempts is still a harness change after `open` (`after_open`).
- `ls` shows one entry per run id (`2 attempts, first failed at launch: <last stderr line>`; `LAUNCH FAILED` on a run not yet retried). `check` prints the attempt when it is over 1.
- A non-zero exit with outputs is a failed run: the stamp stands and the folder stays refused. Resume it with the harness's own command, or start again in a new folder under a new run id.
- `stamp` does not execute, so it cannot see a failed launch or free a folder; it does retry into one `run` freed.

## The run ledger (`runs.jsonl`)

One JSON object per line at the repository root, append-only (one `O_APPEND` write per line; nothing is rewritten). Kinds: `run` (from `stamp`/`run`: utc, run_id, counted, command, record, question, folder, launch_id), `exit` (from `run`: exit_code; launch_failed, attempt and stderr_tail after a failed launch), `note` (from `note`: finding, changes), `close` (from `close`: record, run_ids, result), `record` (from `backfill`, for a record no stamp names). `ls [query]` prints runs newest first with their findings, filtered to entries holding every word of the query (case-insensitive) across run id, question, command, folder, record and findings; `ls <dir>` or a repository with no ledger lists records as before. `backfill <dir>` seeds a ledger from stamps and records already on disk and can be rerun.

## Old records and other inputs

An old record (no `schema`) still works with `close`, `ls <dir>` and `parity`; `prereg.py induct <record>` checks what can be checked after the fact and marks the rest "not established". List inputs outside the repository in `lab-inputs.md` at its root; `stamp` records its hash.
\n\n`prereg.py --version` prints the tool version, a whole number bumped only when a change is breaking (an older script would misread what the new one writes). Stamps, opened records and check results record it as `tool_version`; the script refuses a file written by a newer version and reads older or unversioned ones as before.\n