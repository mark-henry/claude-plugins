---
type: regex
target: trace
pattern: '"id":"(toolu_\w+)","name":"(?:Agent|Task)","input":\{[^\n]*?(?:red.?team|attack|what is wrong|what could go wrong|find (?:the )?(?:flaws|problems|holes)|pre.?mortem)[\s\S]*?\n[^\n]*"name":"Bash"[^\n]*"parent_tool_use_id":"\1"'
flags: i
weight: 1
---
