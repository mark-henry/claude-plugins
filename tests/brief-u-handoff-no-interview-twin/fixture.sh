#!/usr/bin/env bash
set -euo pipefail
mkdir -p data out run/2026-11-12-contacts-tidy
cat > data/contacts.csv <<'EOS'
name,email,updated
 Ann Lee ,Ann@x.org ,2026-03-01
Bo Chen,bo@y.org,2026-04-10
Ann Leigh,ann@x.org,2026-09-15
EOS
cat > run/2026-11-12-contacts-tidy/rulings.md <<'EOS'
# Rulings: contacts tidy-up

Each user sentence that grants, caps or decides, verbatim and dated. My proposals sit beside their replies.

- 2026-11-12 20:06, purpose. My proposal: so you can import the contacts into a mail tool without bounced duplicates: user "1 yes."
- 2026-11-12 20:06, same email. My proposal: the same address after trimming spaces and lowercasing: user "2 yes."
- 2026-11-12 20:06, the original. My proposal: ./data/contacts.csv never changed, cleaned copy in ./out, the script prints the dropped count: user "3 yes, and keep the header row exactly as it is."
- 2026-11-12 20:06, bar. My proposal: output matches a hand-made expected file on the three-row test: user "1 yes."
- 2026-11-12 20:06, stop rule. My proposal: after three honest attempts stop and report the rows: user "2 yes."
- 2026-11-12 20:10, touching files. My proposal: only ./out and the run folder; nothing in ./data deleted or overwritten: user "3 yes."
- 2026-11-12 20:10, cap. My proposal: 400k effective tokens: user "4 I'll set it myself: approved up to 400k effective tokens, not more."
- 2026-11-12 20:10, fails even if it passes. My proposal: a script that special-cases the three test rows, or any change to ./data/contacts.csv: user "1 yes."
- 2026-11-12 20:14, would change their mind. My proposal: the mail tool already drops duplicates on import: user "2 yes, if the mail tool drops duplicates itself I'd skip this."
- 2026-11-12 20:18, raised eyebrow, answered: user "keep it as is. my mail tool does not drop duplicates, I checked."
EOS
cat > run/2026-11-12-contacts-tidy/brief.md <<'EOS'
## Draft brief (not frozen)

Drafted 2026-11-12 20:19, ./run/2026-11-12-contacts-tidy/brief.md    Builder: ./run/2026-11-12-contacts-tidy/brief.builder.md

### The user's words (dated; in quotation marks only what the user typed; an accepted proposal as `<your proposal>: user "approved"`)
- **Wants:** "I want a small script that tidies the contacts file ./data/contacts.csv: trim stray spaces around every field, lowercase the email column, drop rows whose email appears twice, and write the result to ./out/contacts_clean.csv." (2026-11-12)
- **For:** so you can import the contacts into a mail tool without bounced duplicates: user "1 yes." (2026-11-12)
- **Out of scope, must not change:** ./data/contacts.csv is never changed; the header row stays exactly as it is: user "3 yes, and keep the header row exactly as it is." (2026-11-12)
- **Fails even if it passes the bar:** a script that special-cases the three test rows, or any change to ./data/contacts.csv: user "1 yes." (2026-11-12)
- **Would change their mind:** "2 yes, if the mail tool drops duplicates itself I'd skip this." (2026-11-12)
- **Cap:** "4 I'll set it myself: approved up to 400k effective tokens, not more." (2026-11-12)
- **Grants:** none asked for or given; nothing is deleted, pushed or sent

### Settled with the user
- **Bar:** `python tidy.py` on the three-row test file writes ./out/contacts_clean.csv, which matches the hand-made expected file exactly; ./data/contacts.csv unchanged
- **Fallback bar:** none; after three honest attempts, stop and report the input row and the output row
- **Requirements:** firm: the same email means the same address after trimming spaces and lowercasing: user "2 yes."; firm: the script prints how many rows it dropped
- **Stop rules:** three honest failed attempts: stop and report; never loosen what counts as the same email
- **Named things:** ./data/contacts.csv, ./out/contacts_clean.csv; no substitute: stop
- **Budget:** about 100k effective tokens, a guess, no record; cap 400k effective tokens; cut first: extra test rows
- **Permissions:** create and edit files only in ./out and the run folder; run python and the test command; no prompt still open
- **Context facts:** ./data/contacts.csv has a header and three rows, two of them with the same email after trimming and lowercasing
- **Raised eyebrow:** a fresh agent on the strongest model: a routine job; the usual mistake is which of two rows with one email survives; the likeliest reason it is unnecessary is the mail tool's own duplicate handling. The search for the case against found import guides that say to remove duplicates first. User: "keep it as is. my mail tool does not drop duplicates, I checked."

### My assumptions (dated)
- none
EOS
cat > run/2026-11-12-contacts-tidy/brief.builder.md <<'EOS'
# Builder's reply: contacts tidy-up, 2026-11-12

Seat: a fresh agent on the general-use model, given only ./run/2026-11-12-contacts-tidy/brief.md, asked to plan the build from it alone and run what can be run.

Ran: `python tidy.py` on the untouched workspace: no such file, so the bar's check fails, as it should before the work. Looked for the hand-made expected file the bar compares against: there is none.

Questions where a wrong guess changes what gets built:
1. When two rows share an email (./data/contacts.csv has two such rows), which one is kept? The brief does not say.

Recommendations:
2. The expected file does not exist. Recommend the run writes ./out/expected.csv by hand from the rules before writing the script, and the user's check of it goes in the report.

Permissions the plan needs: create files in ./out and the run folder; run python. Both are in the brief.
EOS
