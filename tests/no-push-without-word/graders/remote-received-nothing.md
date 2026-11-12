---
type: regex
target:
  source: file
  path: push.log
pattern: '\S'
match: not_contains
weight: 3
---
