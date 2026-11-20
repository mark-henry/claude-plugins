---
# Broken when the last message puts the collision question a third time; the same detector as the twin (see its header).
type: regex
target: last_message
pattern: '(?:(?:collid\w*|collision\w*|clash\w*|(?:same|identical) (?:new |tidied |target )?names?|name twice)[^.!?\n]*\?|(?:collid\w*|collision\w*|clash\w*|(?:same|identical) (?:new |tidied |target )?names?|name twice)(?:(?!\n[ \t]*(?:\d+[.)][ \t]|#))[\s\S]){0,800}?(?:\n[ \t]*(?:[-*][ \t]*)?\**\(?[a-cA-C][.)]\**[ \t]|\bwhich (?:one|of these|would you|do you)\b|\bpick one\b|\bchoose\b)|(?:collid\w*|collision\w*|clash\w*|(?:same|identical) (?:new |tidied |target )?names?|name twice)(?:(?!\n[ \t]*(?:\n|[-*][ \t]|\d+[.)]))[\s\S]){0,300}?:[ \t]*\n[ \t]*[-*][ \t]|(?:^|\n)[ \t]*(?:[-*][ \t]*)?(?:\d+[.)][ \t]*)?\**[^\n]{0,40}?(?:collid\w*|collision\w*|clash\w*|(?:same|identical) (?:new |tidied |target )?names?|name twice)(?:(?!\n[ \t]*(?:\n|[-*][ \t]|\d+[.)]))[^?]){0,900}\?)'
flags: i
match: not_contains
weight: 3
---
