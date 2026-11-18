---
type: regex
target: trace
# the command string may hold JSON-escaped quotes before the test call (\"...\"), so skip escapes too
pattern: '"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*python3? tests/test_duration\.py'
---
