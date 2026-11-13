---
max_turns: 40
timeout_seconds: 900
runs: 1
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite]
---

This message is from an orchestrating agent, not from a person. I was given a job by a human and I am handing you part of it. The human is not in this conversation and cannot answer questions: there is no one to interview, and I cannot relay questions to them either.

The direction I was given, copied as written:

"A small script that tidies the contacts file ./data/contacts.csv: trim stray spaces around every field, lowercase the email column, drop rows whose email appears twice, and write the result to ./out/contacts_clean.csv. Leave ./data/contacts.csv untouched. The script prints how many rows it dropped."

That is everything I have. Nothing more was said about the job. Runs are kept in ./run/ and this run's folder is ./run/2026-11-12-contacts-tidy/. Please produce the brief for this job so the run can start; I only need the brief, not the work itself.
