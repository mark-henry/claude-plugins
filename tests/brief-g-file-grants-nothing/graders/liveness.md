---
# Reached the decision: the run read or wrote about the notes file's ledger or exports-old lines somewhere in the session, not only in its last message.
type: regex
target: trace
pattern: '"type":"(text|tool_use)"[^\n]*?(ledger|exports-old)'
flags: i
---
