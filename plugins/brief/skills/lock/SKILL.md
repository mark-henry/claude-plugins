---
name: lock
description: "Interview the user until a goal and its success bar are locked: every term defined, every number with a denominator, the threat named, a fallback bar if it's impossible, and hard constraints separated from preferences. Use for \"lock the brief\", \"interview me\", before any costly run, experiment or multi-agent workflow, or when another skill (e.g. diverge:design) asks for a locked brief."
---

# Lock the brief

Help the user figure out what they actually want, then write it down so precisely that someone with no context could build against it and an adversary couldn't game it. You are the interviewer. Ask inline in prose, never with a question modal.

What they want is often not what they first asked for. Every vagueness left in the brief gets built into everything downstream: agents spend their effort guessing at it, and evaluators grade against their own guess.

**The user is biased toward stopping early.** They know what they mean, so their own bar looks finished to them. Your job is to go further than they would. Stop only when you are certain nothing is left: every term is defined, every number has a denominator, and you can't think of a result that would satisfy the bar's letter while missing its point. A user saying "that's fine" is not that point.

Read the request and any stated bars critically, and attack even slight ambiguity or human shortcuts in them. Ask inline in prose, a few questions at a time, each with your proposed answer so "yes" is a valid reply. Typical attacks:

- **Denominators and scope.** Out of what? Over which population, split, condition or time window?
- **Definitions.** Every key term in the bar ("shortcut", "valid", "clean") gets an operational definition, plus its borderline cases.
- **Units of aggregation.** Is the bar averaged over arms, conditions, seeds or instances, and should it be? Averaging a measured arm with a control arm halves the effect and can force designs the user never wanted. Name the unit the bar is computed over.
- **Composite answers.** If an answer has several parts (several items, several steps), is the bar scored per part or per whole? A per-whole rate is roughly the per-part rate raised to the number of parts, so it silently penalizes or rewards designs by how many parts they have.
- **The miss model.** When the honest or baseline policy gets it wrong, how does it miss: symmetric noise, one-sided, or systematic? A bar calibrated on symmetric misses breaks when misses lean one way.
- **Bar or proxy?** Is the number the goal itself, or a stand-in for something that could be measured directly?
- **Which threat or failure?** What happens now vs. what could happen later under pressure (training, scale, adversaries)? A bar that holds today and fails under optimization is the commonest miss.
- **Letter vs. point.** Construct a design that would pass the bar while defeating its purpose. If you can, the bar isn't done.
- **Fixed points.** What must the fix leave unchanged (comparability with past results, interfaces, cost ceilings)?
- **What would change the user's mind.** What result would make them drop the problem or the bar?
- **If it's impossible.** What's the fallback bar? Decide it now, before the disappointment, so the judge can report against it.

**Consider an outside critique of the locked bar.** For a costly run or a bar with many moving parts, have a strong model (e.g. Fable) attack the drafted bar before you lock it: rank its holes and propose rewording. It isn't always needed; skip it when the bar is simple or the run is cheap. If you use it, strip any solution examples from its rewording before they reach the brief.

## Output: the locked brief

When you are certain, write the brief in the conversation under the heading `## Locked brief`, and say the user can interrupt to change it. Other skills look for that heading.

- **Goal.** One or two sentences: what the user actually wants, which may differ from what they first asked for.
- **Bar.** The success criterion, every key term defined with its borderline cases, how it is measured (population, split, n, command or procedure), and anything the user explicitly left open, marked open.
- **Fallback bar.** What counts as success if the bar proves impossible.
- **Constraints.** True hard limits only: spend, files that must not change, data-handling rules, fixed points. Preferences stated as constraints prune options, so leave them out or mark them as preferences.
- **Context facts.** Measurements and what was tried, without diagnosis or candidate fixes.

Keep solution examples out of the bar. State the property, never an example of meeting it: an example becomes the obvious answer for everyone downstream.

Don't read other sessions' transcripts about this problem to fill gaps; measure from the source or ask the user.
