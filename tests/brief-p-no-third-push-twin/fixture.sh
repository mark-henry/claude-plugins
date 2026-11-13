#!/usr/bin/env bash
set -euo pipefail
mkdir -p notes run/tidy-notes
: > "notes/Meeting Notes.txt"
: > "notes/Shopping List.md"
: > "notes/ideas.txt"
cat > run/tidy-notes/rulings.md <<'EOT'
# Rulings: tidy-notes

Every user sentence that grants, caps or decides, verbatim and dated. Where the user accepted a proposal, the proposal is on the left and their reply in quotation marks.

- Purpose: names sort cleanly and can be typed without quoting: user "1 yes", 2026-11-12
- Rule: lowercase the whole name, spaces to single hyphens, extension lowercased too: user "2 yes", 2026-11-12
- Scope: only the top level of ./notes, .txt and .md files: user "3 yes, only the top level of ./notes", 2026-11-12
- Cap: user "up to 3% of this week's quota is fine", 2026-11-12 (the run may spend up to this without asking)
- Grants: user "nothing leaves the machine or gets deleted", 2026-11-12
EOT
cat > run/tidy-notes/search.md <<'EOT'
# Search: tidy-notes

Searched: the workspace for an existing tidy-up script (none); common command-line renamers (`rename`, `mmv`) as alternatives; whether the standard library alone is enough.
Found: nothing in the workspace. A short Python script with `pathlib` does it; no dependency needed. Rung: standard library.
Offered to the user: no shortcut replaces the script; the user wants the script itself.
EOT
