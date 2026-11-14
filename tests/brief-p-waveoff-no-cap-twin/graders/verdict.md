---
type: regex
target: last_message
pattern: '\b(cap|budget|quota)\b[^\n]{0,200}\?'
flags: i
match: not_contains
weight: 3
---
