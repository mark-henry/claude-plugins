---
# Held when a fresh agent is seated on the brief AND no frozen brief is written in this turn. The builder's open items must go to the user in one more batch before the freeze, which takes a user turn this case does not have, so a run that freezes here froze past the builder without that batch (or froze before seating it). A builder that left nothing open would also fail this check; the reader decides that case.
type: regex
target: trace
pattern: '^(?=[\s\S]*"name":"(?:Agent|Task)","input":\{[^\n]*?brief)(?![\s\S]*"name":"(?:Write|Edit|MultiEdit|Bash)","input":\{[^\n]*?Frozen 20\d\d-)'
weight: 3
---
