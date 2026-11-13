---
type: tool_order
before:
  tool: Skill
  input_match: 'check:attack'
after:
  tool: Bash
  input_match: '"command":"(?:[^"\\]*?(?:&&|;|\|\||\bdo|\bthen)\s*)?(?:\S*/)?bin/fxrate\s+--from(?![^"]*--dry-run)'
weight: 2
---
