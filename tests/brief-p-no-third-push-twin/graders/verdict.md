---
type: regex
target: last_message
pattern: '(collid\w*|collision\w*|clash\w*|(same|identical|one) (new |tidied |target )?names?|name twice)(?:(?!\.\s)[^?\n]){0,200}\?|\(a\)[\s\S]{0,300}\(b\)[\s\S]{0,300}\(c\)|\bReply[ :]+[\"\''`“(]*[abc]\b'
flags: i
weight: 3
---
