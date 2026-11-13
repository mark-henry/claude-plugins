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
