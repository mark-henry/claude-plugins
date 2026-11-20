#!/usr/bin/env bash
set -euo pipefail
mkdir -p notes out run/2026-11-12-word-counter
: > run/2026-11-12-word-counter/brief.md
printf 'The cat sat on the mat. The dog sat too.\n' > notes/a.txt
printf 'A cat and a dog and a bird.\n' > notes/b.txt
cat > run/2026-11-12-word-counter/rulings.md <<'EOS'
# Rulings: word counter

Each user sentence that grants, caps or decides, verbatim and dated. My proposals sit beside their replies.

- 2026-11-12 20:06, purpose. My proposal: so you can see which words you lean on in your notes: user "1 yes."
- 2026-11-12 20:06, what counts as a word. My proposal: any run of letters between spaces or punctuation, lowercased: user "2 also drop words of one letter."
- 2026-11-12 20:06, output. My proposal: two columns, word and count, most common first, written to ./notes/top_words.csv: user "3 yes, but put it in ./out/top_words.csv instead, I don't want to touch ./notes."
EOS
