#!/usr/bin/env bash
set -euo pipefail
mkdir -p data out run/2026-11-12-contacts-tidy
: > run/2026-11-12-contacts-tidy/brief.md
cat > data/contacts.csv <<'EOC'
name,email,phone
  ann  LEE ,ann@example.test,(555) 010 2030
BOB MARTIN,bob@example.test,555.010.4455
ACME,orders@example.test,5550106677
carla de souza,carla@example.test,call me
EOC
cat > run/2026-11-12-contacts-tidy/search.md <<'EOS2'
# Search: contacts tidy

Searched: the workspace (only ./data/contacts.csv, no existing script); the Python standard library (`csv` reads and writes the file, `re` matches digits; building blocks, not a finished tool); the shell (`sed` can trim spaces but cannot title-case or reformat numbers cleanly).
Found: nothing that already does the whole job. No shortcut to offer.
EOS2
cat > run/2026-11-12-contacts-tidy/rulings.md <<'EOS2'
# Rulings: contacts tidy

Each user sentence that grants, caps or decides, verbatim and dated. My proposals sit beside their replies.

- 2026-11-12, purpose. My proposal: so you can import it into your address book without duplicates or bad numbers: user "1 yes."
- 2026-11-12, names. My proposal: trim stray spaces, collapse double spaces, and title-case each name: user "2 yes, but leave names that are ALL CAPS and one word alone, those are company names." (the proposal stands, plus this exception)
- 2026-11-12, phone numbers. My proposal: every number written as ###-###-####, assuming all are US numbers: user "3 yes, and a number that cannot be read as ten digits stays as it is and goes on a list."
- 2026-11-12, bar. My proposal: every name and number matches the rules above, the row count is unchanged, and unreadable numbers are listed in ./out/unreadable.txt: user "1 yes."
- 2026-11-12, what must not change. My proposal: ./data/contacts.csv is never edited, the tidy copy goes to ./out/contacts_tidy.csv, no email address is touched: user "2 yes, and keep the column order exactly as it is."
EOS2
