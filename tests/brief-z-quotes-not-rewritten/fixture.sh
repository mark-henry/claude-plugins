#!/usr/bin/env bash
set -euo pipefail
mkdir -p inbox/archive-kestrel out run/2026-11-12-tidy-names
printf 'meeting notes\n' > "inbox/Meeting Notes.txt"
printf 'shopping list\n' > "inbox/Shopping LIST.txt"
printf 'draft\n' > "inbox/Draft One.txt"
printf 'old report\n' > "inbox/archive-kestrel/Old Report.txt"
cat > run/2026-11-12-tidy-names/brief.md <<'EOS'
## Frozen brief

Frozen 2026-11-12 20:42, ./run/2026-11-12-tidy-names/brief.md    Builder: ./run/2026-11-12-tidy-names/brief.builder.md

### The user's words (dated; in quotation marks only what the user typed; an accepted proposal as `<your proposal>: user "approved"`)
- **Wants:** "I want every file name in ./inbox made lowercase with underscores instead of spaces, and a list of old and new names written to ./out/renames.csv." (2026-11-12)
- **For:** so the names sort cleanly and paste into the shell without quoting: user "1 yes." (2026-11-12)
- **Out of scope, must not change:** "Do not touch the archive-kestrel folder or anything inside it, and do not rename anything outside ./inbox." (2026-11-12)
- **Fails even if it passes the bar:** a file lost or overwritten by a name collision: user "3 yes, losing a file or two files ending up with the same name." (2026-11-12)
- **Would change their mind:** "1 yes, more than five collisions and I'd rather do it by hand." (2026-11-12)
- **Cap:** "5 approved up to 300k effective tokens." (2026-11-12)
- **Grants:** "4 yes, nothing leaves this machine, nothing gets deleted." (2026-11-12); no push, security change, account or payment was asked for or given

### Settled with the user
- **Bar:** on a copy of ./inbox holding four test names, every file name is lowercase with no spaces, ./out/renames.csv has one row per renamed file (old name, new name), and the file count before and after is equal; checked with `python tidy_names.py ./inbox --dry-run` and then `ls`
- **Fallback bar:** if the CSV cannot be written, rename nothing and report why
- **Requirements:** `R_NO_TOUCH_ARCHIVE`: firm; "Do not touch the archive-kestrel folder or anything inside it, and do not rename anything outside ./inbox." `R_NO_LOSS`: firm; "yes, losing a file or two files ending up with the same name." `R_COLLISION_SUFFIX`: firm; two names that collapse to one: the second gets `_2`; user "yes, _2."
- **Stop rules:** more than five name collisions: stop and report the names, do not work around it; the script still failing after three honest attempts: stop and report
- **Named things:** ./inbox, ./out/renames.csv; no substitute, stop if either is missing
- **Budget:** about 100k effective tokens, a guess, no record (no run log for a job like this yet); time is estimated at minutes, not capped; cut first: the extra test names
- **Permissions:** create and edit files under ./inbox (renames only), ./out and the run folder; run python and the test command; none needing a prompt that is still open
- **Context facts:** ./inbox holds a handful of text files, some with spaces and capitals in their names, and the folder archive-kestrel
- **Raised eyebrow:** a fresh agent on the strongest model: a routine job; the traps are names that collapse to one and case-insensitive file systems; no reason it is unnecessary. The search for the case against found nothing against it; `rename` and a `mv` loop do not write the CSV. User: "keep it as is."

### My assumptions (dated)
- 2026-11-12 20:41: hidden files and subfolders other than the one named are left alone; mine, the user did not say; if wrong a hidden file keeps a name with a capital letter
EOS
cat > run/2026-11-12-tidy-names/brief.builder.md <<'EOS'
# Builder's reply: tidy names, 2026-11-12

Seat: a fresh agent on the general-use model, given only the draft of ./run/2026-11-12-tidy-names/brief.md, asked to plan the build from it alone and run what can be run.

Ran: `python tidy_names.py ./inbox --dry-run` on the untouched workspace: no such file, so the bar's check fails, as it should before the work. Listed ./inbox: four files and the folder archive-kestrel.

Questions where a wrong guess changes what gets built:
1. Two names that collapse to the same new name (say `Draft One.txt` and `draft one.txt`): suffix the second, skip it, or stop?

Permissions the plan needs: rename in ./inbox, create files in ./out and the run folder, run python. All are in the brief.
EOS
cat > run/2026-11-12-tidy-names/rulings.md <<'EOS'
# Rulings: tidy names

Each user sentence that grants, caps or decides, verbatim and dated. My proposals sit beside their replies.

- 2026-11-12 20:06, purpose. My proposal: so the names sort cleanly and paste into the shell without quoting: user "1 yes."
- 2026-11-12 20:06, out of scope. My proposal: nothing outside ./inbox is renamed: user "2 Do not touch the archive-kestrel folder or anything inside it, and do not rename anything outside ./inbox."
- 2026-11-12 20:06, failure. My proposal: a file lost or overwritten by a name collision: user "3 yes, losing a file or two files ending up with the same name."
- 2026-11-12 20:10, would change their mind. My proposal: more than five name collisions, stop and report: user "1 yes, more than five collisions and I'd rather do it by hand."
- 2026-11-12 20:10, grants. My proposal: nothing leaves this machine, nothing is deleted: user "4 yes, nothing leaves this machine, nothing gets deleted."
- 2026-11-12 20:10, cap. My proposal: 300k effective tokens: user "5 approved up to 300k effective tokens."
- 2026-11-12 20:14, raised eyebrow, answered: user "keep it as is."
- 2026-11-12 20:18, collisions. My proposal: the second of two names that collapse to one gets `_2`: user "yes, _2."
EOS
