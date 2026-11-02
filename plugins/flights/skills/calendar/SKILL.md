---
name: calendar
description: Pull the Google Flights date-picker price calendar (cheapest fare for every departure day across consecutive months) for a one-way route with Nonstop and departure-time filters, via the browser-use MCP. Use whenever the user wants fares across many dates, "which day is cheapest", a price calendar or a holiday sweep, or wants a configured Google Flights calendar scraped into rows, even without saying "calendar". Not for the Date grid (round-trip matrix), not for itineraries or booking.
---

# Google Flights date-picker calendar

The calendar in the departure-date field shows one price per day for roughly a year, filtered by whatever stops/times/passenger settings are active. It is the cheapest way to sweep many dates (one page load instead of one per date). One-way only here; this is NOT the "Date grid" button (round-trip matrix).

Round-trip totals: the calendar here is one-way and remains the primary sweep tool. For true round-trip quotes use `flights-roundtrip-tfs` (on PATH from this plugin; tested only for 4 adults, SFO to MEX/CUN); scope, verification and limits (return times not retrieved) are in `${CLAUDE_PLUGIN_ROOT}/skills/calendar/references/roundtrip.md`.

## Trust level of a calendar number
A calendar price is Google's cheapest-fare indication for that day under the active filters, for the passenger count in the search (1 adult unless the tfs says otherwise). It is not a bookable quote for several seats, not a round-trip fare, and the Times filter constrains the departure time only (a flight leaving 7pm can land after midnight). Re-quote the shortlisted dates on a normal search page (with the real passenger count) before telling anyone to book. Days with no fare render without a price: record `null`, never 0.

## Steps (browser-use MCP, main thread, not a subagent)
1. `list_tabs()` first. Never reuse, navigate, or close the user's own Flights tab; open a NEW tab (`new_tab`) and close only tabs you created. Capture `target_id` and `switch_tab(target_id)` in every `browser_exec` call (the daemon's tab pointer is shared).
2. Build the URL. Google encodes the search state in the `tfs` query parameter (base64url protobuf). `flights-tfs ORIGIN DEST DATE [--stops 0|1|2|any] [--dep 8-19|none] [--adults N]` generates one for IATA airport codes; its output for Mexico City to Cancun with the default filters was byte-identical to the one the UI produced, and an SFO to MEX URL it produced rendered with Nonstop and Times 8:00 AM to 8:00 PM selected. Example: `flights-tfs SFO MEX 2026-12-08`. Append `&curr=USD&hl=en` (the script does). Only the cases tested are known-good (one way, 1 adult, economy, airports and the one city id below). For anything else, configure the filters in the UI once, copy the resulting URL, and reuse it. Do not claim any tfs field beyond the ones listed in "tfs fields" is understood.
3. Use explicit airport codes. Use MEX vs NLU deliberately: a city-level destination (e.g. Mexico City /m/04sqj) includes both airports, and the user's tab MEX-to-CUN results mixed NLU and MEX flights. Record which was used.
4. Run `fetch_calendar.py` through `browser_exec`: `SK = '${CLAUDE_PLUGIN_ROOT}/skills/calendar/scripts/'; exec(open(SK + 'fetch_calendar.py').read()); r = fetch_calendar(url, '2026-12-07', '2027-01-03')`. It opens a new tab, clicks the Departure input, waits, evaluates `extract_calendar.js`, presses Next only while the requested range is not fully priced, and closes its tab.
5. Export rows with this schema: `date,origin,destination,currency,passengers,trip_type,stops,departure_window,price,observed_at,source_url`. Fill origin/destination/currency/passengers/stops/window from what you configured and the returned `meta` (stops_chip, times_chip, passengers_label), not from guesses. Dedup by ISO date (`data-iso`); the DOM holds ~365 consecutive days so year rollover (2026-12 to 2027-01) is already in the ISO value. Keep `price` null when absent.

## Traps (all hit while building this)
- **Background tabs never load prices.** Cells exist in the DOM but are empty (28 of 28 null) until Chrome treats the tab as focused. `fetch_calendar.py` wraps the wait in `Emulation.setFocusEmulationEnabled` (on, then off in `finally`); do the same by hand. Do not activate the tab.
- Prices are lazy per month window; if a range is partly null after waiting, click Next (`[role=dialog] [jsname=KpyLEe]`) and re-read. `jsname` values are minified and can drift; fall back to the button whose aria-label is "Next".
- The first `[role=dialog]` in the DOM can be a hidden duplicate; the extractor goes straight to `[role=gridcell][data-iso]` and skips the dialog lookup.
- Price text is in a cell child with aria-label like "74 US dollars" and visually "$74". Cell innerText is `day|$price`, empty price means no fare. Month and year come from `data-iso` or the aria-label ("Wednesday, December 9, 2026"), never from the visible header.
- `q=` natural-language URLs cannot express Nonstop plus a time window (a long query rendered a landing page). Use tfs or the UI.
- Persistence: Nonstop, Times (8 AM to 8 PM departure), one way, and passenger count all persisted when the tfs URL was reopened in a new tab. The calendar view itself is not in the URL; open it each time by clicking Departure.
- Currency: `curr=USD` was honored; the page shows "US dollars" in labels. Verify per run.
- Do not scrape per-day itineraries, hidden app state, or network traffic.

## tfs fields (verified by decode plus render)
Decoded from the UI-generated URL: field 2 = 2 (one way); leg date string "2026-12-08" (leg field 2); leg field 5 = stops (0 nonstop); leg fields 8/9 = 8/19 which matched the Times panel text "8:00 AM to 8:00 PM", so the end value is the last included hour start; leg fields 10/11 = 0/23 (arrival, shown as Anytime); leg field 13 = origin and 14 = destination as {type, id} with type 1 = airport code, 3 = Google city id; outer field 8 = 1 appears once per adult (inferred from the builder working with --adults 1 only; multiple adults untested). The remaining constants (field 9, 14, 16, 19) are copied unchanged from the UI URL and not understood.

## Reference result (smoke, 2026-10-18)
MEX to CUN, one way, Nonstop, departure 8 AM to 8 PM, 1 adult, USD: Dec 7 to Jan 3 priced for all 28 days (Dec 8 $64, Dec 9 $74, Jan 3 $118, matching the rendered calendar). SFO to MEX with a builder-made URL: Dec 7 to Jan 3 all 28 priced (Dec 8 $296, Dec 19 $1,030, Dec 31 and Jan 1 $296).
