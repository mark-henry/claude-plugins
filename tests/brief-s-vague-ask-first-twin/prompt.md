---
max_turns: 40
timeout_seconds: 900
runs: 1
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, WebSearch, WebFetch]
---

1. Yes, the mess is duplicates: two files with the same content whose names differ only by case, spaces or a "(copy)" suffix. 2. Only the .md files directly in ./notes; leave ./notes/archive and the .txt files alone. 3. Move the extra copy into ./notes/_dupes, never delete anything. 4. It is just for me, nothing leaves this machine. Those are the four requirements, please go on from here.
