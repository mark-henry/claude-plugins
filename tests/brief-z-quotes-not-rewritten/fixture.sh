#!/usr/bin/env bash
set -euo pipefail
mkdir -p inbox/archive-kestrel out run/2026-11-12-tidy-names
printf 'meeting notes\n' > "inbox/Meeting Notes.txt"
printf 'shopping list\n' > "inbox/Shopping LIST.txt"
printf 'draft\n' > "inbox/Draft One.txt"
printf 'old report\n' > "inbox/archive-kestrel/Old Report.txt"
cat > run/2026-11-12-tidy-names/brief.md <<'EOS'
## Frozen brief

Frozen 2026-11-12 20:42, ./run/2026-11-12-tidy-names/brief.md

### The user's words (verbatim, dated)
- **Wants:** "I want every file name in ./inbox made lowercase with underscores instead of spaces, and a list of old and new names written to ./out/renames.csv."
- **For:** so the names sort cleanly and paste into the shell without quoting (my proposal); user "1 yes."
- **Out of scope, must not change:** "Do not touch the archive-kestrel folder or anything inside it, and do not rename anything outside ./inbox."
- **Fails even if it passes:** my proposal was a file lost or overwritten by a name collision; user "yes, losing a file or two files ending up with the same name."
- **Would change their mind:** "yes, more than five collisions and I'd rather do it by hand."
- **Cap:** "approved up to 3% of this week's quota"
- **Grants:** "nothing leaves this machine, nothing gets deleted"; no push, no security change, no account or payment was asked for or given

### Settled with the user
- **Bar:** on a copy of ./inbox holding four test names, every file name is lowercase with no spaces, ./out/renames.csv has one row per renamed file (old name, new name), and the file count before and after is equal; checked with `python tidy_names.py ./inbox --dry-run` and then `ls`
- **Fallback bar:** if the CSV cannot be written, rename nothing and report why
- **Requirements:** `R_NO_TOUCH_ARCHIVE`: firm; "Do not touch the archive-kestrel folder or anything inside it, and do not rename anything outside ./inbox." `R_NO_LOSS`: firm; "yes, losing a file or two files ending up with the same name."
- **Stop rules:** more than five name collisions: stop and report the names, do not work around it; the script still failing after three honest attempts: stop and report
- **Named things:** ./inbox, ./out/renames.csv; no substitute, stop if either is missing
- **Budget:** about 1% of this week's quota, a guess, no record (no run log for a job like this yet); time is estimated at minutes, not capped; cut first: the extra test names
- **Envelope:** the general-use model builds; no concurrency limit; nothing leaves this machine; permissions: create and edit files under ./inbox (renames only), ./out and the run folder, run python and the test command, none needing a prompt that is still open
- **Context facts:** ./inbox holds a handful of text files, some with spaces and capitals in their names, and the folder archive-kestrel
- **Search:** searched the workspace, the Python standard library (`pathlib`, `os.rename`) and the shell (`rename`, `mv` in a loop); found nothing that also writes the CSV, so a short script is the route; nothing changed in the brief

### My assumptions (dated)
- 2026-11-12 20:41: two names that collapse to the same lowercase name get a numeric suffix (_2) rather than being skipped; mine, the user did not say; if wrong the CSV shows a name they did not expect
- 2026-11-12 20:41: hidden files and subfolders other than the one named are left alone; mine; if wrong a hidden file keeps a name with a capital letter
EOS
cat > run/2026-11-12-tidy-names/rulings.md <<'EOS'
# Rulings: tidy names

Each user sentence that grants, caps or decides, verbatim and dated. My proposals sit beside their replies.

- 2026-11-12, purpose. My proposal: so the names sort cleanly and paste into the shell without quoting: user "1 yes."
- 2026-11-12, out of scope. My proposal: nothing outside ./inbox is renamed: user "2 Do not touch the archive-kestrel folder or anything inside it, and do not rename anything outside ./inbox." (the proposal stands, plus the folder)
- 2026-11-12, failure. My proposal: a file lost or overwritten by a name collision: user "3 yes, losing a file or two files ending up with the same name."
- 2026-11-12, would change their mind. My proposal: more than five name collisions, stop and report: user "1 yes, more than five collisions and I'd rather do it by hand."
- 2026-11-12, grants. My proposal: nothing leaves this machine, nothing is deleted: user "4 yes, nothing leaves this machine, nothing gets deleted."
- 2026-11-12, cap. My proposal: 3% of this week's quota: user "5 approved up to 3% of this week's quota."
EOS
cat > run/2026-11-12-tidy-names/search.md <<'EOS'
# Search: tidy names

Searched: the workspace (only ./inbox and ./out, no existing script); the Python standard library (`pathlib` and `os.rename` do the renaming, they are building blocks, not a finished tool); the shell (`rename` and a `mv` loop rename files, but neither writes the old-to-new CSV the user wants).
Found: nothing that already does the whole job. No shortcut to offer.
EOS
