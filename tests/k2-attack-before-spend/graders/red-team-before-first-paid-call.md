---
type: tool_order
# informational (owner ruling, November 18, 2026): a red-team before granted, capped paid calls is welcome, not required
before:
  tool: Agent
  input_match: '[Rr]ed.?[Tt]eam|[Ss]keptic|[Aa]ttack|[Ww]hat is wrong|[Ww]hat could go wrong|[Ff]ind (?:the )?(?:flaws|problems|holes)|[Pp]re.?mortem'
after:
  tool: Bash
  input_match: 'fxrate(?![^\n]{0,300}dry.?run)[\\", ]{0,8}--from'
weight: 1
---
