---
name: last-night
description: >-
  Infer last night's bedtime and wake time from the Mac's lid/display power log
  (pmset), with Chrome history as a cross-check, then compare against or fill
  the daily note's [asleep:: ] [wake:: ] fields. Use when the user asks when
  they slept or woke, says "fill in sleep" or "check my sleep fields", or when
  starting a morning session and the daily note's sleep fields are empty.
---

# Last night's sleep from the lid log

macOS only (needs `pmset -g log` and, optionally, the local Chrome profile). Daily notes are `$DAILY_NOTES_DIR/YYYY-MM-DD.md` (default `~/Documents/daily-notes`).

```bash
lidsleep                    # report for today
lidsleep --fill             # write empty fields only
lidsleep --date 2026-09-17
lidsleep --json
```

**How it decides.** Only `Display is turned on/off` notifications count as human activity. DarkWakes, maintenance sleeps and `Wake Requests` lines are ignored (the Mac wakes itself every ~15 min all night). Bedtime is the display off that starts the longest off→on gap between 18:00 yesterday and noon today; wake is the display on that ends it. Both are rounded to 15 min and written as `asleep` in 12h without am/pm (`1030` = 10:30pm, `0100` = 1am, `0000` = midnight) and `wake` as `HHMM`.

Chrome (`Default/History`, copied first because the live file is locked) gives the last visit before close, the first after open, and anything *during* the gap. Google Calendar's `autorel=1` self-refresh is filtered out. A real visit during the gap means an external monitor or phone-like use, so trust the lid less that night.

**Flow.**
1. Run without `--fill`. Read the status line: `match`, `differs`, `empty`, or `no field`.
2. `empty` → rerun with `--fill`. It only replaces literal `[asleep:: ]` / `[wake:: ]`; it never overwrites a value the user typed.
3. `differs` → report both values in one line and leave the note alone. The user's own number wins; the lid is a lower bound on bedtime and an upper bound on wake (they may read on a phone after closing the lid, or lie in bed before opening it). Only offer to change it if the gap is large (> 1 h) or the note looks like a template default.
4. Mention the closed-for hours only if they change something (a short night, or a mismatch with other evening fields).

**Gotchas.** `pmset -g log` keeps roughly a week; `--date` older than that returns nothing. Multi-day trips with the lid shut make the "longest gap" span days; the gap must end on the requested date, but check the closed-for figure for sanity. If Chrome's History path moves (profile rename), edit `CHROME_HISTORY` at the top of the script.
