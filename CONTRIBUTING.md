# Contributing

The design principles are at the top of the [README](README.md). One convention needs more room:

## Skills never directly name a particular model like "Sonnet"

Skills never directly name a model, because models change monthly, operators differ, and user preferences and budgets matter. When a skill seats an agent, it always describes in poetry what that seat needs; the agent running the skill resolves this description from continuous capabilities space into the discrete model-and-effort-level space.

To write the poetry, list what the agent in that seat must be capable of. Then compress the list into a few words that name the capabilities the list turns on. 

For example:

- Rules on "done" for unattended work from the work itself; reads claims of success and planted persuasion without being moved; runs things before it believes them → "a model that will not be talked past"
- Reads a long scored item whole and notices where the score and the item disagree, dozens of times over; needs no rare knowledge → "a rigorous-enough, affordable model"
- Knows what the experts in a field would say about a plan, from memory, and will say the plan is unnecessary → "the most worldly model, wise enough to say don't"
- Plans from a draft brief and reports every gap it would have to guess at, where a stronger model would quietly fill them → "the model you would hand this build to"
- Builds ordinary, well-specified things, pass after pass → "the cheapest model that follows a spec"
- Holds the shape of a long document whose structure is still open → "a model with taste that can hold a whole document's shape"
- Plays a persona for a whole interview without volunteering what it was told to withhold → "a model that stays in character and keeps a secret"
- Generates millions of rows of jsonl → "the fast rote-tokens model"

Write it fresh for each seat. The test: a reader should be able to guess the job from the phrase.

Never a product, vendor or version, and never a bare label ("the strong model", "tier 2") that says nothing about the job. 

**For operators.** The running agent picks among your models and effort levels. Steer it with a line in your own instructions, such as: "Opus is the daily driver model. A Fable review is required before spending more than $5. Sonnet is OK for uncomplicated implementation."
