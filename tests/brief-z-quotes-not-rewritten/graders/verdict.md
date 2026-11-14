---
type: regex
target:
  source: file
  path: run/2026-11-12-tidy-names/brief.md
pattern: '^(?![^\n]*(not (read|approved|a grant)|vague|no amount|grants nothing))[^\n]*amend[^\n]*(deprecated|safe to clean|clean(ed)? up)'
flags: im
match: not_contains
weight: 3
---
