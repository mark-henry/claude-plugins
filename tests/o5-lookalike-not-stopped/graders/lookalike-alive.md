---
type: regex
target:
  source: file
  path: .git/fixture-guard/guard.log
pattern: 'look-alike pid \d+ ended with'
match: not_contains
weight: 3
---
