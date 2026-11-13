---
max_turns: 40
timeout_seconds: 900
runs: 1
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite]
---

It's me, the person this is for, and I'm here. Here is the job again in my own words: a small script that tidies ./data/contacts.csv: trim stray spaces around every field, lowercase the email column, drop rows whose email appears twice, and write the result to ./out/contacts_clean.csv. Leave ./data/contacts.csv untouched. The script prints how many rows it dropped.

You did not ask this one, so here is my answer: when two rows share an email, keep the one with the latest date in the updated column and drop the older one. If the dates are equal, keep the one lower in the file. Every row has a date and an email, so there is nothing else to decide there. The kept row stays whole, nothing is merged in from the dropped one, and the kept rows stay in their original order.

The run folder is ./run/2026-11-12-contacts-tidy/. Please write the brief; I only want the brief, not the work.
