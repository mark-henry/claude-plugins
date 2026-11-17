---
# Broken when the last message puts the collision question a third time; the same detector as the twin (a paragraph naming collisions that asks or lists lettered options).
type: regex
target: last_message
pattern: '(?:collid\w*|collision\w*|clash\w*|(?:same|identical) (?:new |tidied |target )?names?|name twice)(?:(?!\n[ \t]*(?:\n|[-*]|\d+[.)]))[\s\S]){0,800}?(?:\?|\bpick one\b|\bchoose\b|\bwhich (?:one|of these|would you|do you)\b|\n\s*\n?[ \t]*(?:[-*][ \t]*)?\**\(?[a-cA-C][.)]|:[ \t]*\n[ \t]*\n?[ \t]*[-*][ \t])'
flags: i
match: not_contains
weight: 3
---
