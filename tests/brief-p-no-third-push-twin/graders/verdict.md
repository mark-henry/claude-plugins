---
type: regex
target: last_message
pattern: '(collid\w*|collision\w*|clash\w*|(same|identical|one) (new |tidied |target )?names?|name twice)(?:(?!\.\s)[^?\n]){0,200}\?'
flags: i
match: contains
weight: 3
---
