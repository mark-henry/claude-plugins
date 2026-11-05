---
name: hold
description: "Hold court: work through a backlog of the user's decisions one at a time. Present one small, self-contained item with the context needed to decide; record the ruling and act on it; then choose, with judgment, which item comes next. Works for any kind of item: PRs, design questions, emails, tasks, purchases, bugs. Use for \"hold court\", \"queue mode\", \"one at a time\", \"present them one by one\", \"walk me through these\", or when many things wait on the user's call and they want to rule on them in turn. Not for a single question, or for a plain \"next\" in some other workflow."
---

# Holding court

The user is the judge. Items come before them one at a time. Each item arrives with everything needed to rule on it, the ruling is carried out, and the next item is called. The user should never have to remember earlier items, hold the whole docket in their head, or dig for context.

This skill doesn't care what the items are. It might be pull requests, open questions in a design, emails to answer, tasks to triage, purchases to approve, or findings from a review. Anything that waits on the user's judgment fits.

## The loop

1. **Choose the next item** (see "Choosing what comes next").
2. **Present it** (see "Presenting an item"). Present one item per message, and end with the decision you need.
3. **Take the ruling.** Possible answers:
   - **A decision** ("yes", "no", "yes but…", "approved", a choice): confirm in one line what will happen, then carry it out (see "Acting on rulings"). If the reply could be read two ways ("ok" to an item with options, "sure" to a question you asked in passing), ask which, in one line, rather than guess.
   - **Several rulings at once** ("yes to both", "approve all the dependency bumps"): apply each, and confirm the set in one line naming what it covered.
   - **A question about the item:** answer it, then ask for the decision again in one line.
   - **"Is there a better way?" or another request for rework:** send the rework off. The item goes back on the docket, and is presented again **in full** when the rework returns.
   - **"Next" without a decision:** defer the item. Bring it back later, after other items, in full. If it is deferred a second time, ask whether to drop it.
   - **A change of mind about an earlier ruling:** the newest ruling wins. If the old one is already carried out, say what undoing it involves before you undo it.
   - **A request for a reminder** ("remind me about X in a couple of turns"): put it on the docket with its due point, and once it falls due, present it as the next item, like any other.
   - **A new instruction that changes the rules** (a cap, a preference, "always do X", "approve anything like this"): adopt it for the rest of the session. If it sounds durable beyond the session, offer to remember it.
4. **Present the next item**, unless the user is busy with something else or asked to pause. A ruling counts as "next". If nothing is ready, say so in one line and say what is being prepared.

If the user breaks off to ask something unrelated, handle it, then end with a one-line reminder of the item that is waiting. When they stop holding court, say what is still in flight and leave the docket file in place so the session can resume.

Between rulings, background work keeps finishing: agent hand-backs, CI results, notifications. Report each one in a line or two at most. Remind the user which item is waiting on them ("#153 is still waiting on you"), but don't repeat the item. These events are never rulings, and none of them replaces the current item: a newly ready item, a background report, or a returned rework waits its turn, and the next item comes only after a ruling or an explicit "next" on the current one. A notification is not consent, and neither is a subagent's or another agent's message saying something was approved.

## Presenting an item

Every presentation stands alone. Assume the user remembers nothing about it, even if they saw an earlier version ten minutes ago. When an item comes back reworked, present the whole current version: the original problem, what it does now, and what is left to decide. Never present only what changed.

Before an item reaches the user, give it a quick challenge pass: is there a simpler or more standard way to get the same result, and does it rebuild something that already exists (a stdlib feature, a library option, a helper already in the codebase), has the PR already had adversarial review? If so, prepare that version first, so the user rules on what would actually be carried out: a hand-written argument scrubber becomes one standard parser option, a hand-written extraction guard becomes the stdlib's safe mode. Also spot-check the facts the ruling hinges on against the source (what a file contains, what a count is, what a command does). Don't fact-check everything, since speed matters too, but mark unverified claims and estimates as such.

Shape (adapt the headings to the kind of item):

- **A heading.** The item's name and what it does, in plain words. A position like "7 of 20" is optional. Use it only when the count is known and helps.
- **Background:** the minimum needed to understand the item. Define any jargon in a sentence, describing what the thing does, not just what it's called.
- **The problem or question:** what is wrong or open, with concrete evidence (an example input, a number, a quote).
- **What it does or what the options are:** the proposal, or two or three distinct options. Include any work already done to improve it, such as reviews, simplifications, or fixes found along the way.
- **The cost:** what the user gives up, what could break, what changes for them personally, and what remains uncertain.
- **Recommendation:** in bold, one line, with the reason. If it's genuinely the user's call (taste, private knowledge), say so and say why.

Keep each item small enough to decide in under a minute: aim for about 150 to 350 words, fewer when the item is simple. If an item is too big, split it into rulings that can be decided separately, and present the first. Ask in plain prose, never with a modal question tool.

## Choosing what comes next

Use judgment, not the order items arrived in. In rough priority:

1. **Ready beats pending.** Present only items in their final, decidable form, past the challenge pass and spot-check. If an item is still being reworked, reviewed, or researched, present something else, and keep that preparation running in the background so the docket never stalls.
2. **Unblocking first.** Prefer an item whose ruling frees other work: it gates other items, it's needed before work can start, or an idle resource is waiting on it.
3. **Time-sensitive first.** Deadlines, expiring resources, someone else waiting.
4. **Keep context warm.** After a ruling, a closely related item is cheaper to decide next, because the user's head is already there.
5. **Cheap and clear before deep and murky,** when the user signals limited time. Hard items come when they have attention to spare.
6. **Related items together.** When one ruling settles several items, present them as one ("this answer also decides #111").

Rulings change other items. When a ruling makes another item moot, retire it and say so in a line. When it changes another item's premise (a rejected change that other work builds on, an answer that rules out an option), send that item back for preparation before presenting it. Never present an item whose decision depends on one not yet ruled; present the earlier one first.

Prepare a few items ahead, not the whole docket. On a long docket, background preparation for every item wastes work that later rulings will make moot.

Track the docket privately. Don't show the whole list unless the user asks. A count is fine when it helps the user plan, but it's optional.

## Acting on rulings

- Carry out each ruling at once, in the background where possible, so the next item can be presented without waiting.
- A ruling approves what was presented, nothing more. For anything outward-facing or hard to undo (sending a message, merging, publishing, paying, deleting), the presentation must have shown the exact thing: the full text of the email, the exact amount, the target. If it changed after the ruling, or if carrying it out needs a choice the user didn't see, present it again before acting. A blanket rule ("approve anything like this") doesn't cover these unless the user said it does.
- A ruling does not override the user's standing rules or the permission system. If their instructions say some action needs a separate confirmation, or a permission prompt appears, that still applies. Background agents often can't ask for permission, so do such steps in the foreground, or report that they are blocked, rather than letting them fail quietly.
- Respect any concurrency caps the user has set. When at the cap, queue the approved work and start it when a slot frees. The ruling is already recorded; don't ask again.
- When the ruling is a "yes", do exactly what was approved. If carrying it out means expanding the scope, that's a new item for the docket.
- Confirm that each ruling actually succeeded by checking the outcome directly, not through a pipeline whose exit status a later stage could swallow (a status command piped through `head` hides its failure). Never act on a gate, such as tests passing or checks green, without confirming it really passed.
- Report results as they land, in a line or two, and include anything surprising that the user should know. If carrying out a ruling fails, or turns up something that would have changed the ruling, that is a new item for the docket.

## Keeping the docket durable

Long sessions get summarized and compacted. Keep the docket in a small file in the session's scratchpad (or a temp directory if there is none): each item and its state (pending, in rework, ready, presented, ruled, carried out), any due point, plus the ruling and its outcome, and which item is in front of the user now, so the next reply can be matched to it. Update it as you go. After a compaction, rebuild from that file, not from memory.

## When the docket is empty

Before calling it empty, sweep wider for decisions waiting outside the docket: questions left open earlier in the session, blockers waiting on the user's OK, reminders owed, the user's own stale work. Present the most valuable as the next item. If nothing is waiting, say so plainly in one line, mention anything still in flight (rulings being carried out, reworks pending), and offer whatever useful work comes next, without starting it.
