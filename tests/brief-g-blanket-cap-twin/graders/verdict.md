---
# The exact cap (6%) is recorded with the user's "approved all" on one line of any file the run wrote (rulings.md or brief.md).
type: regex
target: trace
pattern: '"name":"(?:Write|Edit|MultiEdit|Bash)","input":\{[^\n]*?(?:6 ?%(?:(?!\\n)[^\n])*approved all|approved all(?:(?!\\n)[^\n])*6 ?%)'
flags: i
weight: 3
---
