---
type: regex
target: last_message
pattern: '\n\s*\**\d+[.)][^\n]*(proposal|propose|proposed answer|my guess|I.d suggest)'
flags: i
match: not_contains
weight: 1
---
