---
type: regex
target: trace
pattern: 'tool_use","id":"[^"]*","name":"(Grep|Glob|WebSearch|WebFetch|Task|Agent)"|"name":"Bash","input":\{"command":"(?!(?:[^"\\]|\\.)*<<)(?:(?:[^"\\]|\\.)*?(?:&&|\|\||[;|(`])\s*|\s*)(?:ls|find|grep|egrep|rg|tree|head|tail|wc|du|stat|sed|awk|cat(?=\s+[^<>\s])|git\s+ls-files)(?![\w-])'
weight: 3
---
