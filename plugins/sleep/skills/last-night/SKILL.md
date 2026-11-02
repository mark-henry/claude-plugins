---
name: last-night
description: "Infer last night's bedtime and wake time from the Mac lid log, cross-checked with Chrome history. Use when the user asks when they slept or woke."
---

# Last night's sleep from the lid log

macOS only (needs `pmset -g log` and, optionally, the local Chrome profile). Read-only.

```bash
lidsleep                    # the night ending today
lidsleep --date 2026-09-17
lidsleep --json             # for scripts that record the times somewhere
```

**How it decides.** Only `Display is turned on/off` notifications count as human activity. DarkWakes, maintenance sleeps and `Wake Requests` lines are ignored (the Mac wakes itself every ~15 min all night). Bedtime is the display off that starts the longest off→on gap between 18:00 yesterday and noon today; wake is the display on that ends it.

Chrome (`Default/History`, copied first because the live file is locked) gives the last visit before close, the first after open, and anything *during* the gap. Google Calendar's `autorel=1` self-refresh is filtered out.

**Reading it.** The lid is a lower bound on bedtime and an upper bound on wake: people read on a phone after closing the lid, or lie in bed before opening it. A real Chrome visit during the gap means an external monitor or similar, so trust the lid less that night. If the user has their own record of the night, theirs wins.

**Gotchas.** `pmset -g log` keeps roughly a week; `--date` older than that returns nothing. Multi-day trips with the lid shut make the "longest gap" span days; the gap must end on the requested date, but check the closed-for figure for sanity. If Chrome's History path moves (profile rename), edit `CHROME_HISTORY` at the top of the script.
