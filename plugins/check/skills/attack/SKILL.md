---
name: attack
description: "Send a fresh agent that has not seen your reasoning to find what is wrong with a plan, a brief or a piece of finished work before anyone relies on it or spends on it. It returns findings and changes nothing. Use for \"/check:attack\", \"attack this\", \"have agents attack the plan before we spend\", \"red-team it\", \"pre-mortem\", \"find what's wrong with this\", \"get a fresh review of this\", \"subject it to <model> review\", before any plan spends, and after a task or a rewrite, before the work is merged, reported or built on. Not for a property a script or test can check: run that."
---

# Attack before you rely on it

Seat two fresh agents, blind to each other and to this conversation, on the general-use model. One alone when the thing is cheap to redo. Never three, the numbers don't support it. With no way to spawn an agent, say so: your own pass is not an attack.

Give each the thing at a fixed hash, what it runs on (checker, data, tests, diff, logs) and the standard word for word. Leave out your diagnosis and your favorite. Never say what not to flag; you filter afterwards.

Ask each: "Find what is wrong with this. Change nothing. Run what can be run before you judge. Under each finding paste the command and its output, or the lines you read, and mark it RAN or READ. A claim you cannot back that way, leave out."

Pool both replies in `<thing>.attack.md`: in the run folder when there is one, otherwise in your scratch folder, and not inside a repository unless the user asks. You label every finding there, in writing: `FIXED`, `DECLINED`, `REFUTED` (you reran it and it did not reproduce), or `TO_USER` (it says one of the user's decisions will not work, or costs more than they knew). Rerun before you act on one. Report one line per finding with its label.
