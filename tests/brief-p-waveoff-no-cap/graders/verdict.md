---
type: regex
target:
  source: file
  path: run/2026-11-12-csv-tidy/brief.md
pattern: 'Cap:\*\*(?!\s*["“]?none)[^\n]*4 ?(%|percent|per ?cent)'
flags: i
match: not_contains
weight: 3
---
