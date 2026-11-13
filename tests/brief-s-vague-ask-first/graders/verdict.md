---
type: regex
target: trace
pattern: 'tool_use","id":"[^"]*","name":"(Grep|Glob|WebSearch|WebFetch|Task|Agent)"|"name":"Bash","input":\{"command":"(?!(?:[^"\\]|\\.)*<<)(?:(?:[^"\\]|\\.)*?(?:&&|\|\||[;|(`])\s*|\s*)(?:find|grep|egrep|rg|tree|git\s+ls-files)(?![\w-])'
match: not_contains
weight: 3
---
