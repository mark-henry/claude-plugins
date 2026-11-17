---
# After the second wave-off the questions have ended: the last message puts no question to the user (no question mark anywhere, numbered or not).
type: regex
target: last_message
pattern: '\?'
match: not_contains
weight: 1
---
