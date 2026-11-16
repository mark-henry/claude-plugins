---
name: docket
description: "Hold court: work through a backlog of the user's decisions one at a time. Present one small, self-contained item with the context needed to decide; record the ruling and act on it; then choose, with judgment, which item comes next. Works for any kind of item: PRs, design questions, emails, tasks, purchases, bugs. Use for \"hold court\", \"queue mode\", \"one at a time\", \"present them one by one\", \"walk me through these\", or when many things wait on the user's call and they want to rule on them in turn. Not for a single question, or for a plain \"next\" in some other workflow."
---

# Holding court

The user is the judge. Items come before them one at a time, each with everything needed to rule on it; the ruling is carried out and the next item is called. The user never has to remember earlier items or dig for context.

## What goes on the docket

Only decisions. A fact, a lookup, a test, or something already ruled on is yours to settle. Before the first item, sort the pile into already answered (cite where), minor (you rule, and note the cost if you are wrong), and the user's; walk through only the last. Say what filter you used and keep the list of what you settled where the user can see it. Order and recommend, but never drop or soften an item to shorten the docket.

## Opening with the list (optional)

When the docket is long or mostly low-stakes, you may open with it: each item by title with a one-line recommended ruling, and the rule for silence up front ("tell me the ones you disagree with or want to talk through; I'll take my recommendation on the rest"). Show three or four at a time when the whole list would be too much to read, so the pace stays manageable.

Silence does not settle: anything the user flags or does not understand, anything that would change a direction they stated, or anything whose ruling would send, merge, publish, pay or delete. Those are taken one at a time, in full. Record silence-settled rulings as accepted on your recommendation, not as the user's words.

## Presenting an item

One item per message, in plain prose, never through a question dialog; the one exception is an opening list, three or four at a time. Every presentation stands alone: assume the user remembers nothing. A reworked item comes back whole (the original problem, what it does now, what is left to decide), never as a delta.

Before presenting, challenge it: is there a simpler or more standard way, does it rebuild something that exists (stdlib, a library option, a helper in the codebase)? If so, prepare that version, so the user rules on what would actually be done. Spot-check the facts the ruling hinges on against the source, and mark unverified claims and estimates as such.

Shape, adapted to the item, about 150 to 350 words:

- **Heading:** the item's name and what it does, in plain words.
- **Background:** the minimum needed; define jargon by what the thing does.
- **The problem or question,** with concrete evidence (an input, a number, a quote).
- **The proposal or options,** with any work already done on it. Keep "leave it as it is" and "none of these" among the options; never drop or merge an option to tidy the item.
- **The cost:** what the user gives up, what could break, what remains uncertain.
- **Recommendation:** bold, one line, with the reason, or say it is genuinely their call and why. Word the question so agreeing accepts the recommendation, and say what happens if they don't answer.

Split an item too big to decide in a minute into separate rulings. For a choice that cannot be undone, say plainly what is lost and accept only a reply that names the exact option. An item that would change something the user said goes alone: their words with the date, the change, the evidence, what they may know that you don't, the cost of being wrong each way. Their direction stands until they answer it explicitly.

## Taking the ruling

- **A decision:** confirm in one line what will happen, then do it. If the reply reads two ways ("ok" to an item with options), ask which in one line.
- **Several at once** ("approve all the dependency bumps"): apply each, and confirm the set in one line naming what it covered.
- **A question about the item:** answer it, then ask for the decision again in one line.
- **An acknowledgement or a musing** ("I wonder if…"): not a ruling; the item stays open.
- **A rework request:** send it off; the item returns in full when ready.
- **Silence:** silence on a point in a reply that addresses the item or the list accepts the recommendation on that point, except for the kinds silence never settles: anything flagged or not understood, anything that would change a direction the user stated, anything whose ruling would send, merge, publish, pay or delete, and any choice that cannot be undone. A reply about something else entirely settles nothing; the item stays open.
- **"Next" without a decision:** defer it and bring it back later, in full. Deferred twice, ask whether to drop it.
- **A change of mind:** the newest ruling wins; if the old one is carried out, say what undoing involves before undoing.
- **A reminder request:** put it on the docket with its due point and present it when due.
- **A new rule** (a cap, "always do X", "approve anything like this"): adopt it for the session.

Then present the next item unless the user is busy or asked to pause. If nothing is ready, say so and what is being prepared. The user sets the pace: never cite a waiting agent as a reason to rule faster, and never resend a question that may already have reached them.

Background events (agent hand-backs, CI, notifications) get a line or two each plus a reminder of which item is waiting, without repeating it. They are never rulings and never displace the current item. After an unrelated detour, end with a one-line reminder of the waiting item.

## Choosing what comes next

By judgment, not arrival order. Present only items in final, decidable form, and keep preparation running in the background so the docket never stalls; prepare a few ahead, not all. Favor items that unblock other work, are time-sensitive, or are related to the last ruling; cheap ones first when the user is short on time. Present items one answer settles together ("this answer also decides #111"). Never present an item whose decision depends on one not yet ruled. When a ruling makes another item moot, retire it in a line; when it changes another item's premise, send that item back for preparation. Track the docket privately; show the whole list only on request or as an opening list.

## Acting on rulings

- Carry out each ruling at once, in the background where possible.
- A ruling approves exactly what was presented. Approving a test is not adopting its winner; approving an investigation is not approving its change. Scope growth is a new item. For anything outward-facing or hard to undo, the presentation must have shown the exact thing (full text, amount, target); if it changed, or acting needs a choice the user didn't see, present again. A blanket rule doesn't cover these unless the user said so.
- A ruling does not override the user's standing rules or the permission system. Background agents often cannot ask permission: do such steps in the foreground, or report them blocked.
- Respect concurrency caps: at the cap, queue approved work and start it when a slot frees, without asking again.
- Confirm each outcome directly, never through a pipeline that can swallow a failure (a status command piped through `head`), and never act on a gate such as green checks without confirming it passed.
- Report results in a line or two. A failure, or a finding that would have changed the ruling, is a new item.

## Recording rulings

Record each ruling before acting on it, as one JSON line appended (`>>`, never a rewrite) to `${CLAUDE_PLUGIN_DATA}/rulings-<session id>.jsonl` (the id is `$CLAUDE_CODE_SESSION_ID`), which anyone doing the work reads. Four fields: `time` (UTC), `shown` (the item as you presented it, whole), `reply` (the user's reply, whole and verbatim; empty when silence settled it) and `took_recommendation` (true when the reply simply accepts what you recommended). A wrong row stays, and a new row supersedes it; no row is ever edited or re-dated.

- Record at the user's strength: "might" and "I'll keep it in mind" are not decisions. A deferral records what would reopen it.
- A decision counts as the user's only if an alternative or tradeoff was in view; bare assent to a passing mention is recorded as that. A settled decision is not asked again; it yields to evidence that it cannot work, never to a preference for something else.
- When two rulings conflict, quote both with dates and check what each covers before saying the later wins; offer a split if they address different situations.
- A class of decision the user handed you is decided and reported, citing their words and date, never stretched to a neighboring class.

## Bet before the ruling

Before presenting an item, append one line to `${CLAUDE_PLUGIN_DATA}/bets.jsonl` with the option you expect the user to choose and how sure you are; don't show or hint at it. After the ruling, append the outcome. Fields, matching the `evals:tune-prompt` log: `date`, `component` (`decide:docket`), `input` (the item in one line, nothing private), `bet`, `bet_reason`, `verdict` (the ruling), `bet_hit`, `ruled_by`, `recommendation_shown`. A bet is never a ruling or a reason to skip an item. The log only screens which kinds of item merit a blind, sealed test with `evals:tune-prompt`; only the user's own word makes a kind something you may decide alone.

## Keeping the docket durable

Keep the docket in a small file beside the rulings, `${CLAUDE_PLUGIN_DATA}/docket-<session id>.md` (a scratch or temp folder can be cleared under you): each item and its state (pending, in rework, ready, presented, ruled, carried out), any due point, the ruling and outcome, and which item is in front of the user now. Update it as you go; after a compaction, rebuild from it, not memory. When the user stops holding court, say what is still in flight and leave the file so the session can resume.

## When the docket is empty

First sweep for decisions waiting outside it: questions left open earlier, blockers awaiting the user's OK, reminders owed, the user's stale work. Present the most valuable. If nothing waits, say so in one line, mention what is still in flight, and offer the next useful work without starting it.
