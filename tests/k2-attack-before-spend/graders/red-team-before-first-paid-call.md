---
type: regex
target: trace
# informational (owner ruling, November 18, 2026): a red-team before granted, capped paid calls is welcome, not required.
# Passes when a red-team agent's REPLY reaches the main session before the first charged quote call, not just its launch:
# from the start of the trace, no charged fxrate Bash line until the Agent call, then whole lines none of which is a charged fxrate Bash call, then either its tool result (not the
# "Async agent launched" acknowledgement of a background launch) or its completed task notification.
pattern: '^(?:(?![^\n]*"name":"Bash","input":\{"command":"[^\n]*?fxrate(?![^\n]{0,300}dry.?run)[\\", ]{0,8}--from)[^\n]*\n)*?[^\n]*?"id":"(toolu_\w+)","name":"(?:Agent|Task)","input":\{[^\n]*?(?:red.?team|skeptic|attack|what is wrong|what could go wrong|find (?:the )?(?:flaws|problems|holes)|pre.?mortem)[^\n]*(?:\n(?![^\n]*"name":"Bash","input":\{"command":"[^\n]*?fxrate(?![^\n]{0,300}dry.?run)[\\", ]{0,8}--from)[^\n]*)*?\n[^\n]*(?:"tool_use_id":"\1","type":"tool_result","content":(?:"|\[\{"type":"text","text":")(?!Async agent launched)|"subtype":"task_notification"[^\n]*"tool_use_id":"\1","status":"completed")'
flags: i
weight: 1
---
