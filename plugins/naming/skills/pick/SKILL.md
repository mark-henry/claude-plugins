---
name: pick
description: "Choose a good name for something that travels (a module, command, eval, metric, config key, branch, task, product, feature, document): state its job, list the siblings it must not be confused with, brainstorm widely, test the candidates against the classic rules, recommend one. Use for \"name this\", \"better name\", \"rename\", \"I'm getting lost among these names\", or before committing a name that other people or code will use."
---

# Picking a name

A name is the first thing a reader learns about a thing, and often the only thing. A good name lets a newcomer guess what the thing does, and tells it apart from everything nearby. Phil Karlton's joke ("There are only two hard things in computer science: cache invalidation and naming things") lasts because it's true.

## Why models name badly, and the fix for each

- **The most likely word wins.** The first word that comes to mind is the most generic one, and generic names are the ones that collide (`data`, `manager`, `handler`, `utils`, `pairwise`, `semantic`). *Fix:* generate many candidates before judging any.
- **Mechanism over role.** Models name how a thing works (`pairwise`, `llm_judge`, `batch_runner`) instead of what it's for. A mechanism is shared by many things, while a role is usually unique. *Fix:* name the question the thing answers or the job it does.
- **No check against siblings.** A name is good only relative to its neighbors. *Fix:* list the siblings first, and test every candidate against them.
- **Committing to the first candidate.** *Fix:* never ship candidate #1 without at least ten rivals.
- **Qualifier pile-up.** `SemanticPairwiseJudgedComparisonScorer` stacks every concept instead of choosing among them. *Fix:* include only the concepts that distinguish it (step 3 below).

## Signals that a rename is due

- **Its owner had to ask what it is.** That's a bug report, not a matter of taste. One question is enough.
- **Two siblings keep getting confused.** That confusion often means the boundary between them is drawn wrong, not just the names (see step 2).
- **Nobody can say what it measures or produces.** Then it's a design problem that shows up as a naming problem. Settle the design first. Sometimes the fix is a better baseline or a different arm, not a new word.

## Procedure

1. **State the job in one sentence**, in terms of the question the thing answers or the outcome it produces, not its implementation. Name the audience: a newcomer reading code? a user at a CLI? a teammate scanning a task list? Most names should work for someone arriving with no context. Explain it in plain words before naming it: if the sentence won't come, the job isn't settled, so stop and settle it.
2. **List the siblings:** the other names in the same namespace, or in the reader's head, that this one must be distinguishable from. Include things that sound similar, things that use the same mechanism, and the thing's own parts (a frame vs its methods; a family vs a member). If two layers share one name, that is often the real problem: split them (e.g. the contest frame vs the method that decides each contest). When two siblings share the same math, find the axis that separates them: often the *role* (the model as judge vs as actor; where vs what), and put that axis in the names. Siblings that share their items or inputs should share a stem (`spot-the-original`, `spot-the-original by consequence`).
3. **Choose the concepts first, then the words** (Feitelson's three-step model). Of everything true about the thing, which one or two concepts would let a reader pick it out of the sibling list? Leave the rest for the docstring.
4. **Brainstorm 10–15 candidates in deliberately different styles:**
   - literal (what it does, plainly);
   - domain word (the term its users already say: Evans's *ubiquitous language*);
   - concrete metaphor that carries the mechanism (a "lookalike contest": you see the original, then decide which entrant looks more like it; "tombstone", "watermark", "lease", "quarantine");
   - question form (what it answers: `closer`, `which_first`);
   - verb phrase for actions, noun phrase for things;
   - a short form for code and a long form for docs.
   A good metaphor is memorable and almost impossible to confuse with a sibling, and it is almost never the first idea. Look for one.
5. **Test each serious candidate:**
   - **Guessable:** would a newcomer guess roughly what it does from the name alone?
   - **Distinct:** could it be confused with any sibling? Say the two names aloud together.
   - **True:** does it promise anything the thing doesn't do, or hide something it does? (Martin's *avoid disinformation*; Arnaoudova's linguistic antipatterns: a `get` that does work, an `is_x` that returns a non-boolean, a singular name holding a collection, a "check" that changes state.)
   - **The metaphor is literally true:** check every implication of a metaphor against the mechanism. A "lineup" implies that candidates are compared side by side. If each one is scored alone, the metaphor is false, however catchy it is.
   - **Says what changes the reading:** if how the items were chosen, or who judges, changes how a reader should take the numbers (curated vs sampled, a fixed ruler vs self-judged), the name says so.
   - **Role, not mechanism:** would it still fit if the implementation changed?
   - **Searchable and pronounceable:** can you grep for it without false hits, and say it in a meeting?
   - **Right length for its scope** (Kernighan and Pike): the farther a name travels, the more specific it must be. `i` is fine in a three-line loop; a public module needs a real name.
   - **Consistent:** one word per concept across the codebase (Martin). If siblings say `fetch`, don't say `retrieve`; if `retrieve` means something else, don't use it for this.
   - **Survives the rename test:** in six months, does the name still make sense when read in a log line, a CLI listing or a stack trace, away from the code that defines it?
6. **Recommend.** Give the top 2–3 with one line each on why, pick one, and give its long form (for docs and conversation) and short form (for code, files, flags). If the rename would touch existing code, say what moves: modules, flags, file names, saved results, docs. Clear beats clever: brainstorm jokes freely, but ship the name a newcomer can guess, even if it's long. Have the owner lock the choice explicitly, and record it.

## When no name fits, or the old one is already in use

- **Split it, delete it, or move a name.** A thing that won't take a name may be two things (split them and name each), or redundant once looked at alone (delete it rather than name it). A good name rejected for one thing may fit a sibling exactly: reassign it rather than throw it away.
- **Rename before results are keyed to the name.** Sealed datasets, metric keys, saved results and dashboards all freeze a name. Before any exist, a rename is cheap, so do it now.
- **After that, put up a sign.** Accept old names only through one alias table: old name, new name, date, what still depends on it, and the condition for deleting it. Add a check that reports, for each alias, whether anything still uses the old name, and a test that no old name is accepted outside the table.

## Conventions worth keeping

- **Classes and records are nouns; functions are verbs; booleans read as assertions** (`is_held_out`, `has_reply`); **collections are plural.**
- **Don't encode type or scope** in the name (`str_name`, `m_count`, `IThing`) unless the language community does.
- **Avoid noise words** that add no distinction: `data`, `info`, `object`, `manager`, `helper`, `util`, `new`, `my`, `2`. `ProductInfo` vs `ProductData` is not a distinction.
- **Avoid abbreviations a newcomer can't expand**, except ones the whole field uses (`id`, `url`, `http`).
- **Name for the reader, not the writer.** Writer's names ("v2", "fixed", "new_approach", "final") describe the history of making the thing, which the reader doesn't share.
- **A hard-to-name thing is often two things,** or a thing whose job isn't settled yet. If no candidate survives the tests, go back to step 1.

## Sources

- Robert C. Martin, *Clean Code* (2008), ch. 2 "Meaningful Names" (Tim Ottinger's rules): intention-revealing, avoid disinformation, meaningful distinctions, pronounceable, searchable, one word per concept.
- Brian Kernighan and Rob Pike, *The Practice of Programming* (1999), ch. 1: descriptive names for globals, short names for locals; be consistent.
- Eric Evans, *Domain-Driven Design* (2003): ubiquitous language.
- Dror Feitelson et al., "How Developers Choose Names" (IEEE TSE, 2022): selecting concepts, choosing words, constructing the name. Most disagreement is at the first step.
- Venera Arnaoudova et al., "Linguistic Antipatterns" (2013, 2016): names that contradict the behavior.
- Felienne Hermans, *The Programmer's Brain* (2021), ch. 8: names as the main cue readers use to build a mental model; name molds.
