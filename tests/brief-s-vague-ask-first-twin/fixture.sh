#!/usr/bin/env bash
set -euo pipefail
mkdir -p notes/archive scripts run/2026-11-12-tidy-notes
printf '# Standup, January\n\n- ship the parser\n- fix the date bug\n' > notes/standup-jan.md
printf '# Standup, January\n\n- ship the parser\n- fix the date bug\n' > "notes/Standup Jan (copy).md"
printf '# Reading list\n\n- a book about rivers\n- a book about bridges\n' > notes/reading-list.md
printf '# Reading list\n\n- a book about rivers\n- a book about bridges\n' > notes/READING-LIST.md
printf '# Trip ideas\n\n- the coast in spring\n' > notes/trip-ideas.md
printf 'buy stamps\ncall the plumber\n' > notes/todo.txt
printf '# Old plans\n\n- nothing here matters now\n' > notes/archive/plans-2023.md
cat > scripts/list_notes.sh <<'SH'
#!/usr/bin/env bash
# print every note file with its size
for f in notes/*; do [ -f "$f" ] && wc -c "$f"; done
SH
chmod +x scripts/list_notes.sh
printf '# Scratch\n\nA toy workspace for notes.\n' > README.md
printf '# Rulings\n\n(nothing recorded yet)\n' > run/2026-11-12-tidy-notes/rulings.md
