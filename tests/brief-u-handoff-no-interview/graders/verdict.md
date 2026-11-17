---
# Broken if any Write, Edit or Bash call in the session writes a frozen brief (a Frozen brief heading or a "Frozen <date>" line), at any path. The fixture's empty brief.md is no longer what is read.
type: regex
target: trace
pattern: '"name":"(?:Write|Edit|MultiEdit|Bash)","input":\{[^\n]*?(#+ *Frozen brief|Frozen 20\d\d-)'
match: not_contains
weight: 3
---
