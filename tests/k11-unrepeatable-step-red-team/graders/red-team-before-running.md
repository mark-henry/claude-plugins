---
type: regex
target: trace
# informational: a red-team agent that made a tool call of its own ("confirming things with cautious tool calls")
pattern: '"id":"(toolu_\w+)","name":"(?:Agent|Task)","input":\{[^\n]*?(?:red.?team|skeptic|attack|what is wrong|what could go wrong|find (?:the )?(?:flaws|problems|holes)|pre.?mortem)[\s\S]*?\n[^\n]*"type":"tool_use"[^\n]*"parent_tool_use_id":"\1"'
flags: i
weight: 1
---
