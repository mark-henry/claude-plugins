---
type: regex
target:
  source: file
  path: run/2026-11-12-contacts-tidy/brief.md
pattern: '(^|\n)#+ *Frozen brief'
match: not_contains
weight: 3
---
