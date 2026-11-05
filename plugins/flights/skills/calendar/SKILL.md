---
name: calendar
description: "Scrape the Google Flights price calendar (cheapest one-way fare per day across months, with stop and departure-time filters) via browser-use. Use when the user wants fares across many dates or \"which day is cheapest\". Not for round-trip date grids, itineraries or booking."
---

# Google Flights date-picker calendar

The calendar in the departure-date field shows one price per day for ~1 year, filtered by the active stops/times/passenger settings. It is the cheapest way to sweep many dates (one page load). One-way only; this is NOT the "Date grid" button (round-trip matrix).

Round-trip totals: this calendar stays the primary sweep tool. For true round-trip quotes use `flights-roundtrip-tfs` (on PATH from this plugin; tested only for 4 adults, SFO to MEX/CUN). Scope, verification, pricing nonstop returns, and editing a saved tfs for multi-city/open-jaw: `${CLAUDE_PLUGIN_ROOT}/skills/calendar/references/roundtrip.md`.

## Trust level of a calendar number
- A price is Google's cheapest-fare indication for that day under the active filters, for the passenger count in the search (1 adult unless the tfs says otherwise).
- Not a bookable quote for several seats, not a round-trip fare. The Times filter constrains departure time only (a 7pm flight can land after midnight).
- Re-quote shortlisted dates on a normal search page (real passenger count) before telling anyone to book.
- Days with no fare render without a price: record `null`, never 0.

## Steps (browser-use MCP, main thread, not a subagent)
1. `list_tabs()` first. Never reuse, navigate, or close the user's own Flights tab; open a NEW tab (`new_tab`) and close only tabs you created. Capture `target_id` and `switch_tab(target_id)` in every `browser_exec` call (the daemon's tab pointer is shared).
2. Build the URL. Google encodes search state in the `tfs` query parameter (base64url protobuf). `flights-tfs ORIGIN DEST DATE [--stops 0|1|2|any] [--dep 8-19|none] [--adults N]` generates one from IATA codes, e.g. `flights-tfs SFO MEX 2026-12-08`. It appends `&curr=USD&hl=en`.
   - Verified: MEX to CUN with default filters was byte-identical to the UI's URL; an SFO to MEX URL rendered with Nonstop and Times 8:00 AM to 8:00 PM selected.
   - Only the tested cases are known-good (one way, 1 adult, economy, airports and the one city id below). For anything else, configure filters in the UI once, copy the URL, and reuse it.
   - Do not claim any tfs field beyond those in "tfs fields" is understood.
3. Use explicit airport codes. Use MEX vs NLU deliberately: a city-level destination (e.g. Mexico City /m/04sqj) includes both airports, and the user's tab MEX-to-CUN results mixed NLU and MEX flights. Record which was used.
4. Run `fetch_calendar.py` through `browser_exec`: `SK = '${CLAUDE_PLUGIN_ROOT}/skills/calendar/scripts/'; exec(open(SK + 'fetch_calendar.py').read()); r = fetch_calendar(url, '2026-12-07', '2027-01-03')`. It opens a new tab, clicks the Departure input, waits, evaluates `extract_calendar.js`, presses Next only while the requested range is not fully priced, and closes its tab.
5. Export rows with this schema: `date,origin,destination,currency,passengers,trip_type,stops,departure_window,price,observed_at,source_url`. Fill origin/destination/currency/passengers/stops/window from what you configured and the returned `meta` (stops_chip, times_chip, passengers_label), not guesses. Dedup by ISO date (`data-iso`); the DOM holds ~365 consecutive days, so year rollover (2026-12 to 2027-01) is already in the ISO value. Keep `price` null when absent.

## Traps
- **Background tabs never load prices.** Cells exist but are empty (28 of 28 null) until Chrome treats the tab as focused. `fetch_calendar.py` wraps the wait in `Emulation.setFocusEmulationEnabled` (on, then off in `finally`); do the same by hand. Do not activate the tab.
- Prices load lazily per month window. If a range is partly null after waiting, click Next (`[role=dialog] [jsname=KpyLEe]`) and re-read. `jsname` values are minified and can drift; fall back to the button whose aria-label is "Next".
- The first `[role=dialog]` in the DOM can be a hidden duplicate; the extractor goes straight to `[role=gridcell][data-iso]`.
- Price text is in a cell child with aria-label like "74 US dollars" (visually "$74"). Cell innerText is `day|$price`; empty price means no fare. Take month and year from `data-iso` or the aria-label ("Wednesday, December 9, 2026"), never the visible header.
- `q=` natural-language URLs cannot express Nonstop plus a time window (a long query rendered a landing page). Use tfs or the UI.
- Persistence: Nonstop, Times (8 AM to 8 PM departure), one way, and passenger count all persisted when the tfs URL was reopened in a new tab. The calendar view itself is not in the URL; open it each time by clicking Departure.
- `curr=USD` was honored (labels say "US dollars"). Verify per run.
- Do not scrape per-day itineraries, hidden app state, or network traffic.

## tfs fields (verified by decode plus render)
From the UI-generated URL:
- Field 2 = 2 (one way).
- Leg field 2 = date string "2026-12-08".
- Leg field 5 = stops (0 nonstop).
- Leg fields 8/9 = 8/19 matched the Times panel text "8:00 AM to 8:00 PM", so the end value is the last included hour start.
- Leg fields 10/11 = 0/23 (arrival, shown as Anytime).
- Leg field 13 = origin, 14 = destination, each {type, id}: type 1 = airport code, 3 = Google city id.
- Outer field 8 = 1 appears once per adult (inferred from `--adults 1` only; multiple adults untested).
- Remaining constants (field 9, 14, 16, 19) are copied unchanged from the UI URL and not understood.

## Reference result (smoke, 2026-10-18)
- MEX to CUN, one way, Nonstop, departure 8 AM to 8 PM, 1 adult, USD: Dec 7 to Jan 3 priced for all 28 days (Dec 8 $64, Dec 9 $74, Jan 3 $118, matching the rendered calendar).
- SFO to MEX with a builder-made URL: Dec 7 to Jan 3 all 28 priced (Dec 8 $296, Dec 19 $1,030, Dec 31 and Jan 1 $296).
