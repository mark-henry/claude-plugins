---
# The exact cap (600k effective tokens) is recorded with the user's "approved all" on one line of any file the run wrote (rulings.md or brief.md), or as an indented list item under the line that carries "approved all".
type: regex
target: trace
pattern: '"name":"(?:Write|Edit|MultiEdit|Bash)","input":\{[^\n]*?(?:(?:600 ?k|600,000|0?\.6 ?M)(?:(?!\\n)[^\n])*approved all|approved all(?:(?!\\n)[^\n])*(?:600 ?k|600,000|0?\.6 ?M)|approved all(?:(?!\\n)[^\n])*(?:\\n[ \t]+(?:[-*]|\d+[.)])(?:(?!\\n)[^\n])*)*?\\n[ \t]+(?:[-*]|\d+[.)])(?:(?!\\n)[^\n])*(?:600 ?k|600,000|0?\.6 ?M))'
flags: i
weight: 3
---
