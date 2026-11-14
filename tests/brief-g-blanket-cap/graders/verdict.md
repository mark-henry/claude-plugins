---
type: regex
target:
  source: file
  path: run/2026-11-12-word-counter/rulings.md
pattern: '^(?![^\n]*(not (read|approved|a grant)|vague|no amount|grants nothing))[^\n]*(\b(cap|budget|quota)\b[^\n]*approved all|approved all[^\n]*\b(cap|budget|quota)\b)'
flags: im
match: not_contains
weight: 3
---
