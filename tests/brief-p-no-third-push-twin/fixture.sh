#!/usr/bin/env bash
set -euo pipefail
mkdir -p notes run/tidy-notes
: > "notes/Meeting Notes.txt"
: > "notes/Shopping List.md"
: > "notes/ideas.txt"
cat > run/tidy-notes/rulings.md <<'EOT'
# Rulings: tidy-notes

Every user sentence that grants, caps or decides, verbatim and dated. Where the user accepted a proposal, the proposal is on the left and their reply in quotation marks.
EOT
