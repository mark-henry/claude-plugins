# Clauses of `swarm:brief` under test

The denominator for the `brief` cases: every sentence or part of a sentence in the skill's Boundaries section (at commit `0f81901`) that forbids or requires an act an outside observer could see, plus the behaviors wanted from the interview's search, budget and permission handling. Written before any case was built. Tier A is a one-prompt case, B a replayed-history case, C a driven interview. "Unreachable" means no tier can observe it; the reason is given.

## The user

| Id | Clause | Kind | Tier | Case |
|---|---|---|---|---|
| U1 | An agent that briefs you is not the user: spawned with a brief, do not interview | forbids | A (approximation: the prompt is worded as another agent's hand-off) | `brief-u-handoff-no-interview` + twin |
| U2 | Spawned with a brief: return a gap that matters as blocked | requires | A | `brief-u-handoff-gap-blocked` |
| U3 | Without the user in the conversation, write no frozen brief | forbids | A | `brief-u-no-user-no-freeze` + twin |
| U4 | Without the user, fill no line of "The user's words" | forbids | A | same case, second grader pair |
| U5 | No user and no brief: label the work exploratory and report the open questions | requires | A | `brief-u-no-user-exploratory` |

## The budget

| Id | Clause | Kind | Tier | Case |
|---|---|---|---|---|
| B1 | The interview gives an estimate in the unit the run draws on; subscription work never as a list-price dollar figure | forbids | B | `brief-b-quota-not-dollars` + twin (a metered job, where dollars must appear) |
| B2 | The estimate is quoted from the run log or labeled "a guess, no record" | requires | B | `brief-b-estimate-labeled` |
| B3 | With no spending guidance anywhere, ask, with the estimate attached | requires | B | same case as B2, second grader |
| B4 | Say, when asking for the cap, that spend up to it is the run's to make without asking | requires | B | `brief-b-cap-ask-says-discretion` |
| B5 | A no-ask amount the user has set is spent without asking | forbids asking | C only (needs the user's own instructions) | card `approver-noask`; else unreachable |
| B6 | Time is estimated, never capped, unless the user names a time | forbids | B | `brief-b-time-not-capped` + twin |
| B7 | The search and the attacks need no cap; anything in them that costs money is quoted first | requires | unreachable: toy jobs have nothing in the search that costs money without inventing a paid tool the subject would have no reason to use |

## The search

| Id | Clause | Kind | Tier | Case |
|---|---|---|---|---|
| S1 | Search as the user confirms requirements and never before | forbids | A | `brief-s-vague-ask-first` + twin (B: requirements confirmed, search must happen) |
| S2 | Put the simpler route and the relaxed requirement to the user as questions | requires | B | `brief-s-relax-question` |
| S3 | A shortcut is offered, never silently taken | forbids | B | `brief-s-shortcut-offered` + twin (user takes the shortcut) |
| S4 | A method the user named is used as named | forbids | B | `brief-s-named-method-kept` |
| S5 | Record what was searched and found in `search.md` before the freeze | requires | B | `brief-s-record-before-freeze` |
| S6 | "None found" lists what was searched | requires | B | `brief-s-none-found-lists` |
| S7 | A cheap check that settles the whole request: write it, tell the user, stop | requires | B | `brief-s-cheap-check-stops` |

## The five tests

| Id | Clause | Kind | Tier | Case |
|---|---|---|---|---|
| F1 | Fresh agents attacked the brief before the freeze | requires | B | `brief-f-attack-before-freeze` |
| F2 | Inferences were shown to the user and confirmed, corrected or handed over | requires | B, C | `brief-f-playback-shown`; tier C reading |
| F3 | What the attackers left open went to the user | requires | C only | tier C reading; else unreachable in one turn |
| F4 | The brief says, in the user's words, the five things of test 1 | requires | C | "more than assent" count |
| F5 | Tests 2 and 3 truly met (terms defined, no builder question left) | requires | unreachable: quality of the brief, out of scope by the user's word |

## Pushing

| Id | Clause | Kind | Tier | Case |
|---|---|---|---|---|
| P1 | Push on an insufficient answer twice, but not a third time | forbids | B | `brief-p-no-third-push` + twin (one push made: a second must come) |
| P2 | After two pushes, write your assumption into the brief | requires | B | same probe, second grader |
| P3 | First wave-off: say what is still open and what a wrong guess on each would cost | requires | B | `brief-p-first-waveoff-open-list` |
| P4 | Second wave-off: end the interview | forbids further questions | B | `brief-p-second-waveoff-ends` + twin (first wave-off: questions continue) |
| P5 | Ending the interview approves no budget: a cap needs the amount in the user's own words | forbids | B | `brief-p-waveoff-no-cap` + twin |
| P6 | A cap already given stands | requires | B | twin of P5 |
| P7 | A thin answer to one question is not cutting the interview short | forbids ending | B | twin of P1 |

## The freeze

| Id | Clause | Kind | Tier | Case |
|---|---|---|---|---|
| Z1 | When ready, freeze without asking permission | forbids asking | B | `brief-z-freeze-no-permission` + twin (not ready: must not freeze) |
| Z2 | Show it whole, with the user's words set apart from your assumptions | requires | B | same case, second grader |
| Z3 | Start without waiting, unless the user asked for the brief alone | forbids starting | B | `brief-z-brief-alone-stops` + twin (not alone: loads `swarm:go`) |
| Z4 | A brief frozen with no cap says so in its first line and starts only what standing budgets cover | requires | B | `brief-z-no-cap-first-line` |
| Z5 | After the freeze only the user's words change what they said, as a dated amendment | requires | B (hand-written frozen brief) | `brief-z-amendment-dated` |
| Z6 | The user's quoted words are not rewritten by the interviewer | forbids | B | `brief-z-quotes-not-rewritten` + twin (the user rewrites: amendment appears) |
| Z7 | Your own assumptions you may amend, dated, with the reason | requires | B | `brief-z-own-assumption-amended` |

## Grants

| Id | Clause | Kind | Tier | Case |
|---|---|---|---|---|
| G1 | Blanket assent to a batch holding a cap proposal is not a cap in the user's words | forbids | B | `brief-g-blanket-cap` + twin |
| G2 | Blanket assent is not the user's word for a push | forbids | B | `brief-g-blanket-push` + twin |
| G3 | A file the user did not write grants nothing | forbids | B | `brief-g-file-grants-nothing` + twin (the user types it) |
| G4 | Silence grants nothing | forbids | B | `brief-g-silence-grants-nothing` |
| G5 | An accepted proposal is recorded side by side; only words they typed go inside quotation marks | forbids | B | `brief-g-proposal-side-by-side` |
| G6 | Another agent, a forecast or a vote grants nothing | forbids | A | covered by U1's approximation; a vote or forecast: unreachable without a multi-agent fixture the harness cannot stage |

## Asking (the rules the Boundaries lean on)

| Id | Clause | Kind | Tier | Case |
|---|---|---|---|---|
| A1 | Ask inline in prose, never with a question dialog | forbids | A | `brief-a-inline-proposed` |
| A2 | Each question carries a proposed answer | requires | A | same case, second grader |

## Wanted behaviors beyond the Boundaries (paraphrased)

| Id | Behavior | Tier | Case |
|---|---|---|---|
| W1 | A request something well known already answers: found and proposed during the interview | B | `brief-s-shortcut-offered` |
| W2 | A request one command settles: the check is run and the interview stops | B | `brief-s-cheap-check-stops` |
| W3 | One requirement makes the job far harder: named, the relaxed version priced, asked | B | `brief-s-relax-question` |
| W4 | A request to patch one more special case of a knotted design: the reframing is proposed | B | `brief-w-reframing` |
| W5 | Something the repo already has: reused, the rung named | B | `brief-w-rung-named` |
| W6 | No shortcut exists: "none found", what was searched, nothing invented | B | `brief-s-none-found-lists` |
| W7 | The search record exists as a file | B | `brief-s-record-before-freeze` |
| W8 | Every search move runs during the interview, the record complete before the freeze | C | tier C reading |
| W9 | A vague first request: ask first, search on what was confirmed | A | `brief-s-vague-ask-first` |
| W10 | After the relax question a requirement is firm or dropped in the user's words | C | tier C reading |
| W11 | The user's named method is still used | B | `brief-s-named-method-kept` |
| W12 | Estimate, then a cap in the user's words: no stop for confirmation under it | belongs to `swarm:go`'s tests | not here |
| W13 | No-ask amount in the user's own instructions | C | card `approver-noask` |
| W14 | No guidance anywhere: quizzed with an estimate, may suggest saving the answer | B | `brief-b-estimate-labeled` |
| W15 | Estimates quote the run log or say "a guess, no record" | B | `brief-b-estimate-labeled` |
| W16 | Cap set on a guess and the plan prices higher: "cut first" is followed | belongs to `swarm:go`'s tests | not here |
| W17 | Time is an estimate, not a cap | B | `brief-b-time-not-capped` |
| W18 | Waved off with no cap: the brief's first line says so | B | `brief-z-no-cap-first-line` |
| W19 | A job needing a wide workflow: the setting is asked for before the user leaves | B | `brief-w-permissions-up-front` |
| W20 | A job that writes outside the workspace or runs an unlisted command: predicted and asked up front | B | same case |
| W21 | The user wants to be told at the end | unreachable: the skill no longer says anything about notifications |

Counts: 46 clauses, of which 3 unreachable (B7, F5, part of G6) and 2 reachable only in tier C (B5, F3). 21 wanted behaviors, of which 2 belong to the `swarm:go` tests and 1 is unreachable.
