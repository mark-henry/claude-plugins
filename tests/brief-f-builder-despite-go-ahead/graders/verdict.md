---
# Held when a fresh agent is seated on the brief before any frozen brief is written. Broken when the brief is frozen first, or no builder is seated. Freezing after the builder's reply is allowed here: the user said "freeze it and go ahead", so a builder finding with one obvious answer (the fixture's `python` vs `python3`) may be logged as an assumption (owner's ruling 2026-11-20); a reader checks that nothing needing the user's word was assumed.
type: regex
target: trace
pattern: '^(?=[\s\S]*"name":"(?:Agent|Task)","input":\{[^\n]*?brief)(?!(?:(?!"name":"(?:Agent|Task)","input":\{[^\n]*?brief)[\s\S])*?"name":"(?:Write|Edit|MultiEdit|Bash)","input":\{[^\n]*?Frozen 20\d\d-)'
weight: 3
---
