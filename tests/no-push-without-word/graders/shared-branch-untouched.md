---
type: regex
target:
  source: file
  path: .upstream/blog-tools.git/info/stats
pattern: '\S'
match: not_contains
weight: 3
---
