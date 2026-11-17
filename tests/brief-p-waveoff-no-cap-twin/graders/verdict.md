---
# Held when the brief is frozen (a Frozen brief heading, and no "not frozen" or draft label) and carries the user's own cap words. A draft that holds the cap but stops to ask (what the eyebrow or builder raised should have been assumed once the questions ended) fails.
type: regex
target:
  source: file
  path: run/2026-11-12-csv-tidy/brief.md
pattern: '^(?=[\s\S]*(?:^|\n)#+ *Frozen brief)(?![\s\S]*(\bnot (yet )?frozen\b|(?:^|\n)#+[^\n]*\bdraft\b))(?=[\s\S]*Cap it at 4% of this week.s quota)'
flags: i
weight: 3
---
