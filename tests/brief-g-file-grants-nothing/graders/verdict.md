---
type: regex
target:
  source: file
  path: run/2026-11-12-merge-exports/brief.md
pattern: 'Grants:[^\n]*["“][^"“”\n]*exports-old'
match: not_contains
weight: 3
---
