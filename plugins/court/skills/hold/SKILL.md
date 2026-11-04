---
name: hold
description: "Hold court: work through a backlog of the user's decisions one at a time. Present one small, self-contained item with the context needed to decide; record the ruling and act on it; then choose, with judgment, which item comes next. Works for any kind of item: PRs, design questions, emails, tasks, purchases, bugs. Use for \"hold court\", \"queue mode\", \"one at a time\", \"present them one by one\", \"next\", or whenever many things are waiting on the user's call."
---

# Holding court

The user is the judge. Items come before them one at a time. Each item arrives with everything needed to rule on it, the ruling is carried out, and the next item is called. The user should never have to remember earlier items, hold the whole docket in their head, or dig for context.

The skill doesn't care what the items are. It might be pull requests, open questions in a design, emails to answer, tasks to triage, purchases to approve, or findings from a review. Anything that waits on the user's judgment fits.

## The loop

1. **Choose the next item** (see "Choosing what comes next").
2. **Present it** (see "Presenting an item"). Present one item per message, and end with the decision you need.
3. **Take the ruling.** Possible answers:
   - **A decision** ("yes", "no", "yes but…", "approved", a choice): confirm in one line what will happen, then carry it out (see "Acting on rulings").
   - **A question about the item:** answer it, then ask for the decision again in one line.
   - **"Is there a better way?" or another request for rework:** send the rework off. The item goes back on the docket, and is presented again **in full** when the rework returns.
   - **"Next" without a decision:** defer the item. Bring it back later, in full.
   - **A new instruction that changes the rules** (a cap, a preference, "always do X"): adopt it for the rest of the session. Save it as a memory if it sounds durable.
4. **Present the next item**, unless the user is busy with something else or asked to pause. A ruling counts as "next". If nothing is ready, say so in one line and say what is being prepared.

Between rulings, background work keeps finishing: agent hand-backs, CI results, notifications. Report each one in a line or two at most. Remind the user which item is waiting on them ("#153 is still waiting on you"), but don't repeat the item. These events are never rulings. A notification is not consent.

## Presenting an item

Every presentation stands alone. Assume the user remembers nothing about it, even if they saw an earlier version ten minutes ago. When an item comes back reworked, present the whole current version: the original problem, what it does now, and what is left to decide. Never present only what changed.

Shape (adapt the headings to the kind of item):

- **A heading.** The item's name and what it does, in plain words. A position like "7 of 20" is optional. Use it only when the count is known and helps.
- **Background:** the minimum needed to understand the item. Define any jargon in a sentence, describing what the thing does, not just what it's called.
- **The problem or question:** what is wrong or open, with concrete evidence (an example input, a number, a quote).
- **What it does or what the options are:** the proposal, or two or three distinct options. Include any work already done to improve it, such as reviews, simplifications, or fixes found along the way.
- **The cost:** what the user gives up, what could break, what changes for them personally, and what remains uncertain.
- **Recommendation:** in bold, one line, with the reason. If it's genuinely the user's call (taste, private knowledge), say so and say why.

Keep each item small enough to decide in under a minute: aim for about 150 to 350 words. If an item is too big, split it into rulings that can be decided separately, and present the first. Ask in plain prose, never with a modal question tool.

## Choosing what comes next

Use judgment, not the order items arrived in. In rough priority:

1. **Ready beats pending.** Present only items in their final, decidable form. If an item is still being reworked, reviewed, or researched, present something else, and keep that preparation running in the background so the docket never stalls.
2. **Unblocking first.** Prefer an item whose ruling frees other work: it gates other items, it's needed before work can start, or an idle resource is waiting on it.
3. **Time-sensitive first.** Deadlines, expiring resources, someone else waiting.
4. **Keep context warm.** After a ruling, a closely related item is cheaper to decide next, because the user's head is already there.
5. **Cheap and clear before deep and murky,** when the user signals limited time. Hard items come when they have attention to spare.
6. **Related items together.** When one ruling settles several items, present them as one ("this answer also decides #111").

Track the docket privately. Don't show the whole list unless the user asks. A count is fine when it helps the user plan, but it's optional.

## Acting on rulings

- Carry out each ruling at once, in the background where possible, so the next item can be presented without waiting.
- Respect any concurrency caps the user has set. When at the cap, queue the approved work and start it when a slot frees. The ruling is already recorded; don't ask again.
- When the ruling is a "yes", do exactly what was approved. If carrying it out means expanding the scope, that's a new item for the docket.
- Report results as they land, in a line or two, and include anything surprising that the user should know.

## Keeping the docket durable

Long sessions get summarized and compacted. Keep the docket in a small file in the session's scratchpad: each item and its state (pending, in rework, ready, presented, ruled, carried out), plus the ruling and its outcome. Update it as you go. After a compaction, rebuild from that file, not from memory.

## When the docket is empty

Say so in one line. Mention anything still in flight (rulings being carried out, reworks pending). Offer whatever useful work comes next, without starting it.
