---
name: make
description: >-
  Turn a result into a self-contained figure image or slide: a claim as the title, a caption that explains and qualifies it, then the chart or table that proves it. Use when the user says "figure", "chart image", "work this up into a chart", "turn the table into an image", "finding charts", or "make slides of the results".
---

# Claim-first figures

If a `dataviz` skill is available, load it and follow it for the chart itself. Each image makes one claim and stands alone:

1. **Title:** the claim, as a full sentence ("Base models beat post-trained ones on loss, slightly"), not a topic label. Qualify it in the title if the evidence is weak.
2. **Caption:** what is measured, on what data, which direction is better, how to read the encoding, and any caveat that limits the claim.
3. **The chart or table** that proves the claim.

When making several images, draft a pool of candidate claims (including some the user didn't propose), then keep the few the data best supports. Write for a reader with no context: no codenames. Look at every rendered image before handing it over, and fix any overlap, clipping, or claim the chart doesn't visibly show.
