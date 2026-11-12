# Parked from owner:forecast

Red-flag tables and notes about the skill itself, moved out of the body of `owner:forecast` and kept here until the pack's restructuring decides what stays. Nothing in the skill depends on this file.

## Red flags

| Thought | Reality |
|---|---|
| "I'm confident they'll say yes, so I'll just do it." | Confidence never licenses an ask the ladder requires. 94.4% right is about 1 wrong in 18. Ask. |
| "Forecast: they take my recommendation, 0.9." | That is advocacy. Start from the class base rate; imagine the no; allow "cannot predict". |
| "I'll show my forecast so they can see my reasoning." | The forecast anchors the answer it is scored against. Show the recommendation; keep the forecast hidden. |
| "I'll write the forecast after; I knew what they'd say." | A forecast written with the answer in view is retrospective and excluded. Seal it first. |
| "Here are three good examples to calibrate their taste." | Blind elicitation: no examples, scores or verdicts until their answer is in. |
| "Quick question: what does the log say?" | Facts are your job. Run the read-only check and report it. |
| "Good point; that changes my recommendation." | Agreement is not evidence. Give the case against and what would settle it before you change anything. |
| "I'll report progress first and get to their question later." | Answer it now, or say when; an unanswered owner question is dropped at the next reset. |
| "Both reviewers agree, so I'll change their plan." | Model agreement is evidence, not consent. Raise a direction challenge; their direction stands. |
| "They didn't object to the batch, so the challenge is accepted." | Direction challenges need an explicit answer; silence keeps the owner's direction. |
| "They approved the commit, so pushing is fine." | An approval covers exactly what was shown. Publishing is owner-only. |
| "They said 'ok'." | To what? "ok" after an unrelated answer is not consent; a one-way door needs the exact option typed. |
| "They said stop asking about naming; that covers file layout too." | Delegations are not stretched to a neighboring class. |
| "I'll file my answers under the rulings heading so workers follow them." | Agent decisions go in the agent-decisions part, pending veto. Never launder a guess. |
| "I'll put my best guess of their preference in the judge prompt." | Consensus laundering. Cite their words or label it a forecast. |
| "These two rulings conflict; the later one wins." | Check scope first. Quote both with dates; they may address different situations. |
| "I'll ask all four things in one message to save their time." | Bundled questions get the easiest one answered. One decision per question, or an announced batch grammar. |
| "Nine questions now, to be thorough." | One decision per question, ordered by dependency, goal first. |
| "I'll drop the weak option to keep the list short." | The option set is the owner's decision space. Order and recommend; never filter. |
| "They saw this ten minutes ago; I'll just send the changes." | Re-present it whole. A delta assumes memory they do not have. |
| "They said 'just do it'; I'll keep pressing on the bar." | Two pushes, then respect it; record the skip as a ruling and your assumption beside it. |
| "The scorebook looks great: 95% hits." | Against which baseline, with what n, how many accepted by silence, how many with the recommendation visible? |
| "We've had 20 hits in a row; I'll stop asking about this class." | A track record proposes; only the owner grants, per class, in their own words. |
| "The prompt is slightly off; I'll tweak it." | Changes need two or three misses sharing a cause, a version bump and a new series. |
| "No one's around, so I'll approve the pending item to finish." | Never approve for the owner. Write it as pending; the run ends pending, not success. |
| "The run finished with a few owner questions open: success." | It ended pending. `STATUS: pending (<n> owner decisions)`. Say so. |
| "The prompt looks scripted, so I'm unattended." | Only a trusted runtime signal says no owner is present. |
| "I'll remind them about item 4 at the end of every message." | Park it, state the safe default once, re-present it whole later. |
| "Let me remind them a result is waiting." | Ordering is agent-side only. Order the queue; leave their time to them. |
| "Shall I continue?" | Never ask that on authorized work. Continue, and report. |

## Testing this skill

**Enforce, don't exhort.** Prose rules for ordered, owner-facing steps get skipped. gstack: when every skill told agents to log each question, weeks of use produced zero logged events; in 3 gated sessions every failure was in the reporting step; a prose footer did not stop agents baking in architectural choices the user never made; agents replace a mandated stop-and-ask loop with one batch synthesis whenever it collides with another rule; a reopen-by-id with no state store loses the decision at compaction [1][3]. An outside review called building auto-decision on a prompt convention "sand" [2]. Where it matters, use a mechanism: a required close-out, an asking step that refuses without a sealed forecast, a hook, a durable store, a declared expected question count audited after the run. The forced pattern needs a forcing mechanism, or at least a close-out the report cannot skip. (Self-use: when a sibling planning skill was built, nothing enforced writing its per-piece results lines, and the agent recommended shipping without a hook for now; the same gap would leave sealed forecasts never closed, which is why the close-out here is a required step.)

**Against the bare model.** gstack watched a frontier model run its debugging skill on 46 bug-fix sessions: the five-phase procedure loaded every time and was followed in none of them (0 of 30 with the harness's real system prompt), while a session with the whole pack installed cost $0.46 against $0.22 without it; gstack cut the procedure and kept the parts that still did a job [4]. Cutting a planning review skill, it reported that the plain model found the planted engineering flaws in 15 of 16 reviews, while in a separate outcome test a session told to use the skill cost 7.1 times a plain one [4] (vendor-reported). The author's lesson from those cuts: skills compared with the bare model will always lose in time, as models improve and become cheaper [ruling]. This skill's application (not the author's words): a planted-case test with a no-skill arm, using the harness's built-in plugin eval with a no-plugin baseline arm where there is one [habit]. Keep evaluation words out of the test prompts, so the agent under test cannot tell it is being tested; the built-in harness does not do this for you [habit]. Plant positives and negatives: Mechanical decisions the agent must not ask about, direction challenges it must not auto-decide, owner-only items it must not default, and an ask that must come back in the brief shape with a sealed, hidden forecast. Test the ask format end to end as written: a gstack gate once failed to render because the skill's label did not match the parser [1]. Each ceremonial part earns its place with evidence that it helps, or with a stated reason, an owner and a date by which a fair test will measure it. A null result gets one "why null?" cycle (did the agent use the part, did the task fit, was there enough power and headroom, does today's model do it without the part) before you keep, fix or cut it; cutting after one null without that cycle is gstack's named anti-pattern [1]. The safety parts (the owner-only list, the seal, the consent rules) stay on their stated reason even after a null result: they exist for the rare bad run an average score cannot see [1]. Review the draft through two lenses matching its two readers: an agent that just loaded it (can it execute every step unambiguously, tell when the skill applies and when it does not, and produce a well-defined output?) and the busy owner who skims it (would they actually walk through it for every decision, is it fast and memorable, does it change what they do on the next decision?). Start with one item and read it before scaling. Drafted citations often overclaim: of 59 claims checked in this pack's merge, 23 were supported, 24 partly, 7 unsupported, 5 uncheckable (self-use).
