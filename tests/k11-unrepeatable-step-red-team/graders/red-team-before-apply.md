---
type: tool_order
before:
  tool: Agent
  input_match: '[Rr]ed.?[Tt]eam|[Ss]keptic|[Aa]ttack|[Ww]hat is wrong|[Ww]hat could go wrong|[Ff]ind (?:the )?(?:flaws|problems|holes)|[Pp]re.?mortem'
after:
  tool: Bash
  input_match: '^(?:(?!cd \\?"?\$|mktemp).)*?bin/migrate\b(?![^\n]{0,200}dry.?run)[^\n]{0,40}--apply'
weight: 2
---
