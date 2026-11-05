# Round-trip quotes (tested 2026-10-18)

The calendar workflow in SKILL.md (one-way) stays primary for sweeping many dates. For a true round-trip total, use `flights-roundtrip-tfs ORIGIN DEST OUT_DATE RET_DATE [--adults N]` (nonstop, departure 8AM-8PM on both legs) and open the URL in a NEW tab (never the user's).

## What was verified
- Scope: 4 adults, economy, USD, SFO to MEX and SFO to CUN, five 8-night outbound/return pairs in December. All 10 URLs rendered results.
- Rendered header showed Round trip / 4 / Economy, Nonstop and Times chips; one MEX pair matched the UI-built price.
- Times popup (checked once, on one MEX pair): Outbound departure 8:00 AM-8:00 PM; the hidden return range inputs read 8 and 20. The Return tab itself was not opened, and the other 9 URLs were not inspected.
- Prices are round-trip totals for all passengers (divide for per head), scraped from visible `li` rows after a ~6 s wait. Rows show outbound times only.

## Limits
- The first price on a round-trip or multi-city page pairs that outbound with the cheapest return, often a one-stop flight landing near midnight: the Nonstop filter does not restrict the return list. Headline prices understated real nonstop itineraries by $30-165 a head (Oct 2026). To price nonstop returns, click the outbound card with `click_at_xy` at the center of its `getBoundingClientRect()` (JS `element.click()` does nothing; one earlier attempt hit "Oops, something went wrong"), then read the return `li` rows, which show entire-trip totals for all passengers. Rows tagged "Separate tickets" are two one-ways. Keep the focus-emulation wrapper around every wait.
- Return-leg arrival time is unconstrained (arrival 0-23 on both legs); overnight arrivals on the return were not checked.
- Fares exclude bag fees; many United fares are basic (no carry-on).
- Field meanings beyond those in SKILL.md "tfs fields" are not understood; outer field 2 = 2 is what the UI emitted for this round-trip URL. Other passenger counts, cabins, origins untested.

## Searches the builders can't express (multi-city, open-jaw, other filters)
Configure one search in the Google Flights UI (or reuse a saved one), then base64url-decode its `tfs=` value and byte-replace the dates (`b"2026-12-29"`) and airport codes (`b"\x03MEX"` to `b"\x03CUN"`). Assert each target occurs exactly once, re-encode, and append `&hl=en&curr=USD`. Passenger count, Nonstop, departure window, and round trip vs multi-city/open-jaw all survived this edit across dozens of 4-adult open-jaw searches (Oct 2026). Natural-language `q=` URLs can't express nonstop plus a time window, multi-city, or more than 1 adult.
