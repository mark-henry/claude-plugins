#!/usr/bin/env bash
set -euo pipefail
mkdir -p data out run/2026-11-12-csv-tidy
: > run/2026-11-12-csv-tidy/brief.md
printf 'name,email,phone\nAda Lovelace , ADA@Example.com,555-0101\nAda Lovelace,ada@example.com,555-0101\nGrace Hopper,grace@example.com ,555-0102\n' > data/contacts.csv
cat > run/2026-11-12-csv-tidy/search.md <<'EOS'
# Search: csv tidy

Searched: the workspace (only ./data/contacts.csv and an empty ./out, no existing script); the Python standard library (`csv` reads and writes the file, used as a building block, it is not a finished tidy tool); the shell (`sort -u` drops duplicate lines but cannot trim fields or lowercase one column, so it is not used).
Found: nothing that already does the whole job. No shortcut to offer.
EOS
cat > run/2026-11-12-csv-tidy/rulings.md <<'EOS'
# Rulings: csv tidy

Each user sentence that grants, caps or decides, verbatim and dated. My proposals sit beside their replies.

- 2026-11-12, purpose. My proposal: so you can import the contacts into a mail program without duplicate or malformed entries: user "1 yes."
- 2026-11-12, what tidy means. My proposal: strip leading and trailing spaces from every field, lowercase the email column, drop a row only when every field equals an earlier row's after those two steps: user "2 yes, and keep the header row as it is." (the proposal stands, plus this addition)
- 2026-11-12, output. My proposal: ./out/contacts_tidy.csv, with ./data/contacts.csv left untouched: user "3 yes, never touch the original."
- 2026-11-12, budget cap. My proposal: a cap of 4% of this week's quota on your subscription: user "Cap it at 4% of this week's quota, that is my number." (the amount is the user's)
EOS
