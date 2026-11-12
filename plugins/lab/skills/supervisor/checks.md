# What shows each rule

The evidence `lab:supervisor` opens for each rule, at launch and at quote. "Evidence" alone means the same evidence at both moments. Rerun a check rather than read its old output.

1. **One difference.** *Launch:* a diff of the two arms' resolved configs and commands shows only what the prereg record's `varies` names; the plan's knob list. *Quote:* the same diff over every run record of both arms (commit, command, config, models, hashes) shows only `varies` and seeds, and their `started` times interleave. `prereg.py parity` helps and does not suffice: it reads one stamp per arm folder and compares every arm to the first.
2. **Prediction and denominator first.** *Evidence:* a non-exploratory prereg record that `prereg.py open` accepted, present with its current frozen hash in the tree at every treated run's commit (`git show <commit>:<record>`), or pushed before the first treated run started when records live in another repo; the bar text it points to unchanged since.
3. **Controls.** *Evidence:* each is an arm with a command; the positive control's scored output shows the pass the plan defined.
4. **Noise floor.** *Evidence:* those runs' raw values, recomputed.
5. **Leakage and held-out.** *Launch:* intersect item IDs and content hashes; the ledger of every run that has scored the sealed set; a read of the scorer and sealed items as the optimizer's user fails; one logged call per judge and baseline; failure reports shown to whatever is optimizing carry no gold labels, and its memory and notes carry nothing from held-out items. *Quote:* each counted run scored the sealed set once, at its end; a leak audit of any result above its predicted interval.
6. **Instrument.** *Evidence:* rerun the fixture; the judge record; one logged judge call.
7. **Freeze.** *Evidence:* the FREEZE line; the scorer and judge-prompt hashes recompute at that commit, the item-set hashes from the stored files; each threshold cites untreated or dev runs.
8. **Run record.** *Launch:* a dry run's record, its `commit` set and `git status --porcelain` empty. *Quote:* every field filled or null with a reason; `git log --stat` per record; seeds and hashes equal to the FREEZE line, and no code path differs between the FREEZE commit and any counted run's commit; every run reported, killed and relaunched ones included, and the launcher's log lists no run without a record.
9. **Nothing moved after the freeze.** *Evidence:* `git log` on the plan, scorer and prereg record since the FREEZE; counted run records per arm equal the FREEZE's seeds and n; `prereg.py close`, run on a copy of the record, succeeds (it refuses changed frozen fields).
10. **Scores read.** *Evidence:* the audit block naming these run IDs; parse yield k/n.
11. **Declared denominator, beyond noise.** *Evidence:* `prereg.py close` output on a copy (it scores the predictions; apply the bar yourself); a committed script that rebuilds the number from run IDs.
12. **Confirmatory or exploratory.** *Evidence:* the label; `git merge-base --is-ancestor`; the sentence as quoted.

## What the tools do and do not show

- `prereg.py open` checks that a non-exploratory record has a bar, a decision, and a `[low, high]` prediction and a denominator for every arm and metric. It does not check that an interval could miss, and its frozen hash is stored in the record itself: only the record's presence in git at each treated run's commit shows the predictions came first.
- `prereg.py parity` compares launch arguments outside `varies`, the instance files it finds, the commits and any dirty trees. It reads one stamp per arm folder, compares every arm to the first against one `varies` list, and only warns when it finds no instance files, so a PASS is support for rule 1, not proof, and a FAIL on a control arm's declared difference is expected.
- `prereg.py stamp` records the commit, the uncommitted diff and the command. Its `dirty` list ignores untracked files.
- `prereg.py close` refuses a record whose frozen fields changed, and scores each prediction as hit or miss. It does not apply the bar. Running it again rewrites the record, so check on a copy.
- An `evals:judge` record is valid for the distribution its "Valid for" line names. An `evals:audit` verdict is a prescreen of how a scorer was applied; its verdicts are never validation labels.
