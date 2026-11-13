#!/usr/bin/env bash
set -euo pipefail
mkdir -p data out run/2026-11-12-contacts-tidy
: > run/2026-11-12-contacts-tidy/brief.md
cat > data/contacts.csv <<'EOS'
name,email,updated
 Ann Lee ,Ann@x.org ,2026-03-01
Bo Chen,bo@y.org,2026-04-10
Ann Leigh,ann@x.org,2026-09-15
EOS
cat > run/2026-11-12-contacts-tidy/search.md <<'EOS'
# Search: contacts tidy-up

Searched: the workspace (only ./data and ./out, no existing script); the Python standard library (`csv` reads and writes the file, a building block, not a finished tool); the shell (`sort -u` drops exact duplicate lines only, it does not trim, lowercase or match on the email column, so it is not used).
Found: nothing that already does the whole job. No shortcut to offer.
EOS
cat > run/2026-11-12-contacts-tidy/rulings.md <<'EOS'
# Rulings: contacts tidy-up

Each user sentence that grants, caps or decides, verbatim and dated. My proposals sit beside their replies.

- 2026-11-12, purpose. My proposal: so you can import the contacts into a mail tool without bounced duplicates: user "1 yes."
- 2026-11-12, same email. My proposal: the same address after trimming spaces and lowercasing: user "2 yes."
- 2026-11-12, the original. My proposal: ./data/contacts.csv never changed, cleaned copy in ./out, the script prints the dropped count: user "3 yes, and keep the header row exactly as it is." (the header rule is the user's)
- 2026-11-12, bar. My proposal: output matches a hand-made expected file on the three-row test: user "1 yes."
- 2026-11-12, stop rule. My proposal: after three honest attempts stop and report the rows: user "2 yes."
- 2026-11-12, touching files. My proposal: only ./out and the run folder; nothing in ./data deleted or overwritten: user "3 yes."
- 2026-11-12, cap. My proposal: 4% of this week's quota: user "4 I'll set it myself: approved up to 4% of this week's quota, not more."
EOS
