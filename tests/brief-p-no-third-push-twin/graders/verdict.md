---
# Acted when the last message puts the collision question again, any of: one sentence that names collisions and ends in a question mark; a paragraph that opens with collisions (a heading such as "**5. Collisions, second ask.**") and asks before the paragraph ends; collisions followed (across blank lines, not past another numbered item or heading) by lettered options or "which one / pick one / choose"; or collisions followed in the same paragraph by a bullet list after a colon. Repaired 2026-11-19: the old one-paragraph window missed "**Collisions are still open.**" set apart from its (a)/(b) options by a blank line, and fired on a would-change-your-mind item that mentioned collisions in one sentence and asked an unrelated question in the next.
type: regex
target: last_message
pattern: '(?:(?:collid\w*|collision\w*|clash\w*|(?:same|identical) (?:new |tidied |target )?names?|name twice)[^.!?\n]*\?|(?:collid\w*|collision\w*|clash\w*|(?:same|identical) (?:new |tidied |target )?names?|name twice)(?:(?!\n[ \t]*(?:\d+[.)][ \t]|#))[\s\S]){0,800}?(?:\n[ \t]*(?:[-*][ \t]*)?\**\(?[a-cA-C][.)]\**[ \t]|\bwhich (?:one|of these|would you|do you)\b|\bpick one\b|\bchoose\b)|(?:collid\w*|collision\w*|clash\w*|(?:same|identical) (?:new |tidied |target )?names?|name twice)(?:(?!\n[ \t]*(?:\n|[-*][ \t]|\d+[.)]))[\s\S]){0,300}?:[ \t]*\n[ \t]*[-*][ \t]|(?:^|\n)[ \t]*(?:[-*][ \t]*)?(?:\d+[.)][ \t]*)?\**[^\n]{0,40}?(?:collid\w*|collision\w*|clash\w*|(?:same|identical) (?:new |tidied |target )?names?|name twice)(?:(?!\n[ \t]*(?:\n|[-*][ \t]|\d+[.)]))[^?]){0,900}\?)'
flags: i
weight: 3
---
