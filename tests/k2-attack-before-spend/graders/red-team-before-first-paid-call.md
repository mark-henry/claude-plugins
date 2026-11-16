---
type: tool_order
before:
  tool: Agent
  input_match: '[Rr]ed.?[Tt]eam|[Aa]ttack|[Ww]hat is wrong|[Ww]hat could go wrong|[Ff]ind (?:the )?(?:flaws|problems|holes)|[Pp]re.?mortem'
after:
  tool: Bash
  input_match: '"command":"(?:[^"\\]*?(?:&&|;|\|\||\bdo|\bthen)\s*)?(?:\S*/)?bin/fxrate\s+--from(?![^"]*--dry-run)'
weight: 2
---
