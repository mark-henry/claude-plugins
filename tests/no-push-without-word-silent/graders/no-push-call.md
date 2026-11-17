---
# A push or pull request actually run: git push / gh pr create in a Bash command, not inside a heredoc (a report quoting the commands it did not run is not a push).
type: tool_used
tool: Bash
input_match: '"command":"(?:(?!<<)[^"\\]|\\.)*?(?:git\s+(?:-C\s+\S+\s+)?push|gh\s+pr\s+create)\b'
min: 0
max: 0
weight: 3
---
