---
name: reframe
description: "Before spending on a problem, look for what makes it unnecessary or smaller: something that already does it, a cheap check that settles it, a reframing that cuts the knot, the first lazy rung that holds, or the one requirement that carries most of the cost. Use for \"/decide:reframe\", \"reframe this\", \"is there a shortcut?\", \"has this been done before?\", \"gordian\", \"ponytail this\", \"dummy check\", \"am I overcomplicating this?\", \"what if we relax a requirement?\", before building, buying or researching anything sizable, and whenever a design keeps growing special cases. Not for improving a proposal as it stands (decide:improve), not for finding what is wrong with it (check:attack), and not for a whole-codebase simplification audit (gordian:cut)."
---

# Reframe

Every other tool here holds the question fixed and works on answers. This one works on the question. It is the only move that can make the work disappear, so it goes first, and it is cheap: a few searches and one or two fresh agents. Invoking it is the go-ahead.

It needs the requirements. If what the user wants is still unclear, ask first: a shortcut found for a guessed requirement is a shortcut to the wrong place.

## The five moves

Try each, in this order, and stop at the first that settles the matter.

1. **Something already does it, or someone already knows.** Here, in this codebase or these notes, or elsewhere: a library, a platform feature, a published answer, the user's own earlier work. Search the web before you reason or measure: "does the internet know?" is the cheapest move there is and the one most often skipped. Search on independent angles; queries that leave the machine use generic terms only. A found answer must apply at this scale, and a bounded search does not prove absence.
2. **A cheap check settles it.** A test, a lookup, a benchmark, a bisect, one small experiment. Run it; do not reason about what it would show.
3. **A reframing cuts the knot.** When a design keeps needing one more special case, ask what single change to the framing would make the cases the same case. State the knot in one sentence first.
4. **The lazy ladder.** Stop at the first rung that holds and name it: does this need to exist; already in this codebase; in the standard library; a native platform feature; an installed dependency; one line; only then the minimum that works plus one small test. Lazy about the solution, never about reading the code first, and never by cutting validation, error handling, security or accessibility.
5. **One requirement carries most of the cost.** Say which, what dropping or loosening it buys, and what it would lose.

For anything costly, give moves 1 and 3 to fresh agents who have not seen your approach: you are anchored on it. Give them the requirements and the facts, never your design.

## What comes back

One of four things, said plainly:

- **Done already:** what exists, where, and what adopting it takes.
- **Settled:** the check that ran and its output.
- **A smaller question:** the reframing or the rung, and what is left to do.
- **A question for the user:** the requirement to relax, what it buys, what it costs.

Or **none found**, with what was searched, so nobody searches it again.

A shortcut is offered, never silently taken. A method the user named is used as named, and a requirement the user stated is theirs to relax: put it to them as a question, with your recommendation. What you may take without asking is a route that meets every stated requirement more simply.
