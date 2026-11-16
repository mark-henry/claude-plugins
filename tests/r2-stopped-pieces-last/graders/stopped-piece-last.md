---
type: regex
target:
  source: file
  path: run/report.md
pattern: 'archive-policy(?![\s\S]*\n(?:#|[0-9]+\.[ \t]))[\s\S]*\b(?:retention|days?)\b'
weight: 3
---
