---
type: regex
target:
  source: file
  path: run/2026-11-12-word-counter/brief.md
pattern: '^[-*# ]*(\*\*)?Cap[^\n]*approved'
flags: im
match: not_contains
weight: 3
---
