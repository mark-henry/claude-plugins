---
type: regex
target:
  source: file
  path: run/2026-11-12-merge-exports/rulings.md
pattern: '^(?![^\n]*(not (read|approved|a grant)|vague|no amount|grants nothing))[^\n]*user[^\n]*["“][^"“”\n]*exports-old'
flags: im
match: not_contains
weight: 3
---
