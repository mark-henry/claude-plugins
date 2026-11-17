---
# Reached the decision: the last message proposes the cap again with an amount and a unit (a run that writes nothing passes the verdict only with this).
type: regex
target: last_message
pattern: '\b(cap|budget)\b[^\n]{0,80}?\d[\d,.]*\s*(k|m|million|thousand)?\s*(effective tokens|tokens|%|percent|dollars)|\b(cap|budget)\b[^\n]{0,80}?\$\s?\d'
flags: i
---
