# Parked from pipeline:run

Red-flag tables and notes about the skill itself, moved out of the body of `pipeline:run` and kept here until the pack's restructuring decides what stays. Nothing in the skill depends on this file.

## Red flags

Scan this table mid-task. Rows repeat rules stated elsewhere on purpose; keep them even so.

| Thought | Reality |
|---|---|
| "This one is simple, I'll skip the pipeline." | Simple jobs buy the check tier: three lines, the result and a log line. There is no exit. |
| "A quick vote among agents will settle this factual question." | A vote measures agreement, not correctness. Run the test, the lookup or the computation. |
| "I'll ask the user what they've seen." | That is not prior art. Search. |
| "The interview can wait; I'll infer requirements." | An agent left alone cannot ask; gaps become wrong guesses. Lock the spec, or write Assumptions and label the run exploratory. |
| "The interview means the idea is right." | It establishes intent, not truth. Attack the premise and the test design. |
| "I know what the human means." | Write the most likely reading down, state it in the report, offer the cheap alternative. Ask only where a slip would flip the meaning. |
| "Nobody has done this before." | You have not searched. "Nothing found" means "within this search". |
| "The human said X, so X is settled." | Settled means a tradeoff was raised and the human chose with it in view. An unexamined directive gets exactly one evidence-backed challenge. |
| "They approved it" (and they did not, in so many words). | An agent never settles its own recommendation or invents approval. Record your choice as your call. |
| "The plan is good, I'll start the fan-out." | Not before the attack and the go-ahead. |
| "I'll tell the reviewer the plan already chose X, so it won't flag it." | Never tell a reviewer what not to flag. Triage afterwards. |
| "The reviewer found twelve things, fix them all." | Reviewers always find something. Validate decision-changing flags with a second fresh agent, grade by effect, then act. |
| "One agent playing three judges gives three opinions." | One context is one sample. Independence is a property of execution, not of the lens. |
| "All five voters agreed, so it's right." | Same-model voters share errors. Spot-check unanimous items; agreement cannot corroborate an inherited premise. |
| "The worker reported done." | A hand-back is a claim. Read the artifact, run the check. |
| "I'll paste the conversation into the brief so it has context." | Pass paths, not history. A worker knows nothing; write facts for a stranger. |
| "I'll leave the model unset, it'll inherit something sensible." | Name the model on every dispatch (Models). |
| "Requested model isn't available; the next one is close enough." | Stop and ask. Never substitute. |
| "The run launched, so I can report the result." | A launch receipt is not a result. Wait for every terminal outcome. |
| "It's probably finished by now; I'll report it." | Never predict or report a background worker's result before it arrives. |
| "Scorer is read-only, that's enough." | Hidden, not read-only. Agents edit and game what they can see. |
| "I can mark unavailable as zero." | That invents evidence. Keep the missing or error status. |
| "Let me just retry with a bigger budget." | Stop incomplete at the cap. Never retry to make room. |
| "Let me revise it once more, it'll be better." | Revision can make it worse. No self-revision without an external signal; end any chain in a blind pick that includes the original. |
| "Debate will get the agents to the truth." | On 2023-2024 models, a majority vote over independent samples beat debate at a matched number of responses [5] and matched or beat it with fewer calls [6]. A relay of fresh challengers is not debate. |
| "I'll fix the findings while I review." | Review reports; fixing is a separate step, and fixes get verified. |
| "I'll self-check my candidates before the judge sees them." | No agent filters its own candidates before the verdict-holder sees them. |
| "Agreed?" "Yes, agreed." | Treat your own fast agreement as suspect: give the case for and against. |
| "This change nobody accounts for must be a worker's mess, I'll clean it up." | It may be the human's. Preserve it and stop. |
| "The scrubber passed, it's safe to publish." | A separate auditor reads what the scrubber missed, then the human gives the word. |
| "I can push; the commits are ready." | Publishing is the human's word. |
| "Done, apart from a couple of open decisions." | A non-empty "needs your decision" list is never success. |
| "I'll mention the idea as a side note." | Apply improvements; attached ideas get dropped. |
| "I'll report the aggregate, it looks great." | A too-good result gets a leak check and a stratified read of the outputs first. |
| "I'll keep going until it's perfect." | Stop the moment the check passes; agents drift into busywork after. |
| "This step feels useful." | A step that has never shown benefit gets an owner and a date to measure it. |
| "I met the literal template." | Meet the purpose it protects. Empty ceremony and loopholes fail the gate. |
| "The tools improved themselves, so they work." | Bootstrapping is not evidence on outside jobs. |

## Agent conduct

- **Self-supervision language is deliberate.** This skill uses iron laws with their rationalisations, a red-flag table, "evidence before claims", "rulings, not stalls" and a spirit-over-letter clause because agents that know a rule skip it under pressure and rationalise doing so [31], and, in another pack's framing, capable models left alone plan thinly, review shallowly and write nothing down [33]. [31] reserves this form for discipline failures; for missing or wrong-shaped output it uses required template fields and positive recipes, and finds prohibitions there backfire. Persuasion wording (authority, commitment) more than doubled a small model's compliance with objectionable user requests (GPT-4o-mini, 33 to 72 percent over 28,000 conversations) [44]; that it carries over to skill text is a public pack's extrapolation, untested [31]. Follow them as written. Keep the red-flag table even where rows repeat rules: it is what an agent scans mid-task.

## Maintaining this skill

The structure is deliberate and survived a blind-judged merge of three drafts (in an earlier three-draft bake-off, the artifact-first draft won because it alone specified the contents of every handoff file [habit]): one top table (stage, handoff file, hard gate, neighbour); numbered, file-named stage headings, each with a receives/produces card and a closing Gate line (gates are repeated at the stage, not only in the table); a red-flag table; each neighbour gets one line at the moment it applies. Keep the stage table, iron laws and red flags near the top, because hosts may truncate the tail. The description is the real router: it carries the users' own trigger words, says "use when", names the siblings to use instead, and does not summarise the workflow, because agents that read a workflow summary may follow it instead of reading the body [31]; over-broad triggers are dropped, and trigger phrases are checked for collisions with sibling and built-in descriptions before the description is locked. Include the ecosystem terms that accurately name the job (council, jury, grill or interview me, ralph, bakeoff) so searches find it, and none for work the skill does not do. Length is not managed yet: cut only what is trivially obvious; overlap with sibling skills is expected and is factored out in a later integration pass, which also gives each rule one owner (stated in full once, cited elsewhere).
