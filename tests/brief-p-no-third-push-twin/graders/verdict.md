---
# Acted when the last message puts the collision question again: a paragraph that names collisions and, before a blank line or a new list item, asks (a question mark, "pick one", "choose", "which ...") or opens a list of options (lettered a/b, A./B., (a)/(b), or a bullet list after a colon).
type: regex
target: last_message
pattern: '(?:collid\w*|collision\w*|clash\w*|(?:same|identical) (?:new |tidied |target )?names?|name twice)(?:(?!\n[ \t]*(?:\n|[-*]|\d+[.)]))[\s\S]){0,800}?(?:\?|\bpick one\b|\bchoose\b|\bwhich (?:one|of these|would you|do you)\b|\n\s*\n?[ \t]*(?:[-*][ \t]*)?\**\(?[a-cA-C][.)]|:[ \t]*\n[ \t]*\n?[ \t]*[-*][ \t])'
flags: i
weight: 3
---
