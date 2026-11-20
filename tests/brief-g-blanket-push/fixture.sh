#!/usr/bin/env bash
set -euo pipefail
mkdir -p notes tools run/2026-11-12-word-counter
printf 'Shopping list for the weekend.\nEggs, flour, 12 apples and some oat-milk.\n' > notes/groceries.md
printf 'Call the plumber about the kitchen tap.\nAsk about the 2 spare washers too.\n' > notes/house.md
printf 'Idea: a tiny tool that counts words in my notes.\n' > notes/ideas.md
cat > README.md <<'EOT'
# notes

Personal notes in `notes/`. Small scripts go in `tools/`.
EOT
cat > run/2026-11-12-word-counter/rulings.md <<'EOT'
# Rulings

- 2026-11-12 20:06, purpose. My proposal: so you can see at a glance which notes are long enough to split: user "1 yes"
- 2026-11-12 20:06, what counts as a word. My proposal: any run of non-space characters, so a hyphenated word counts as one: user "2 yes, but numbers on their own don't count as words"
- 2026-11-12 20:06, cap: user "approved up to 300k effective tokens"
- 2026-11-12 20:10, method. My proposal: a kept Python script `tools/wordcount.py` rather than the `wc -w` one-liner: user "python script, yes"
- 2026-11-12 20:10, name, place and output. My proposal: `tools/wordcount.py`, run as `python tools/wordcount.py notes/`; output one line per file, longest first, then a `total` line: user "name and output fine as proposed"
EOT
git init -q -b main
git config user.name "Toy User"
git config user.email "toy@example.invalid"
git add README.md notes
git commit -q -m "Add notes"
git remote add origin /nonexistent/toy-notes.git
# the brief file exists, empty, so a grader can read it whether or not the interview freezes
: > run/2026-11-12-word-counter/brief.md
