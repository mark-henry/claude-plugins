# Round-trip quotes (tested 2026-10-18)

The calendar workflow in SKILL.md (one-way) stays primary for sweeping many dates. For a true round-trip total, use `flights-roundtrip-tfs ORIGIN DEST OUT_DATE RET_DATE [--adults N]` (nonstop, departure 8AM-8PM on both legs) and open the URL in a NEW tab (never the user's).

## What was verified
- Scope: 4 adults, economy, USD, SFO to MEX and SFO to CUN, five 8-night outbound/return pairs in December. All 10 URLs rendered results.
- Rendered header showed Round trip / 4 / Economy, Nonstop and Times chips; one MEX pair matched the UI-built price.
- Times popup (checked once, on one MEX pair): Outbound departure 8:00 AM-8:00 PM; the hidden return range inputs read 8 and 20. The Return tab itself was not opened, and the other 9 URLs were not inspected.
- Prices are round-trip totals for all passengers (divide for per head), scraped from visible `li` rows after a ~6 s wait. Rows show outbound times only.

## Limits
- Return flight times not obtained: clicking a result did not open the return-selection page in the smoke run (main thread once saw "Oops, something went wrong"). Price = cheapest return passing the filter.
- Return-leg arrival time is unconstrained (arrival 0-23 on both legs); overnight arrivals on the return were not checked.
- Fares exclude bag fees; many United fares are basic (no carry-on).
- Field meanings beyond those in SKILL.md "tfs fields" are not understood; outer field 2 = 2 is what the UI emitted for this round-trip URL. Other passenger counts, cabins, origins untested.
