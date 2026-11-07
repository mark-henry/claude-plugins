---
name: make
description: "Turn a result into a self-contained figure or slide: the claim as title, a qualifying caption, then the chart or table that proves it. Use for \"figure\", \"chart image\", \"turn the table into an image\", \"make slides of the results\"."
---

# Claim-first figures

If a `dataviz` skill is available, load it and follow it for the chart itself. Each image makes one claim and stands alone:

1. **Title:** the claim, as a full sentence ("Base models beat post-trained ones on loss, slightly"), not a topic label. Qualify it in the title if the evidence is weak.
2. **Caption:** what is measured, on what data, which direction is better, how to read the encoding, and any caveat that limits the claim.
3. **The chart or table** that proves the claim.

When making several images, draft a pool of candidate claims (including some the user didn't propose), then keep the few the data best supports. Write for a reader with no context: no codenames. Look at every rendered image before handing it over, and fix any overlap, clipping, or claim the chart doesn't visibly show.

## Low-words mode

Use it when the reader will remember what's good and what's bad but won't replicate anything, such as a results update for a teammate or manager. It's not a paper. Ask which mode fits if the audience is unclear, and save full captions for records meant to be reproduced.

- **Prose asks, the chart answers.** The intro gives the question and how it's scored, with no numbers. A number in prose competes with the chart. Every result gets a small chart.
- **The axis says which way is good, in outcome words.** Write the arrow as the outcome ("training on thoughts made it worse →"), not a variable ("twin worse") or a unit. Usually one arrow toward the side that matters is enough. Put the label inside the chart so it scales with it, and drop any caption that only restates the axis.
- **Name a metric by what it checks on every item**, so the name fits all of them: "same key points", not "same ask" when most actions aren't asks. No codenames.
- **Lead with the story.** Open with a few short claims, one vivid line the reader will retell, and a small diagram for any mechanism, rather than a methods paragraph.
- **Examples serve the comparison the reader cares about.** Label them plainly ("High Score" / "Low Score"), and choose each one to show the contrast the eval exists for.
- **Cut scaffolding:** subtitles, "Audit:" labels and restated captions. A one-line verdict under the intro is enough.
