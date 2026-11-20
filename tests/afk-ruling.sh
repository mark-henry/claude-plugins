#!/usr/bin/env bash
# Unit tests for plugins/afk/bin/afk-ruling (not a `claude plugin eval` case). Run: bash tests/afk-ruling.sh
set -uo pipefail
bin=${AFK_RULING:-$(cd "$(dirname "$0")/.." && pwd)/plugins/afk/bin/afk-ruling}
tmp=$(cd "$(mktemp -d)" && pwd -P); trap 'rm -rf "$tmp"' EXIT
fails=0
t() { if [ "$2" = "$3" ]; then echo "ok    $1"; else echo "FAIL  $1: wanted $3, got $2"; fails=$((fails + 1)); fi; }
run() { "$bin" "$@" > "$tmp/out" 2> "$tmp/err"; code=$?; }
f=$tmp/run/rulings.md

echo "-- appends, never rewrites"
mkdir -p "$tmp/run"; printf '# Rulings\n\n- 2026-01-01, purpose: user "1 yes."\n' > "$f"
run "$f" "cap" 'cap: 500k effective tokens, approved'
t "exits 0" "$code" 0
t "the earlier line survives, undated anew" "$(grep -c '^- 2026-01-01, purpose: user "1 yes."$' "$f")" 1
t "one line added" "$(wc -l < "$f" | tr -d ' ')" 4
t "the user's words are kept verbatim in quotes" "$(tail -n 1 "$f" | grep -c 'user "cap: 500k effective tokens, approved"$')" 1
t "the line carries today's date and the topic" "$(tail -n 1 "$f" | grep -c "^- $(date +%Y-%m-%d) [0-9][0-9]:[0-9][0-9], cap: ")" 1
t "prints the line it wrote" "$(cat "$tmp/out")" "$(tail -n 1 "$f")"

echo "-- a proposal sits beside the reply"
run "$f" "push" 'approved' --proposal 'push branch `x` and open a pull request against `main`'
t "proposal then the user's word" "$(tail -n 1 "$f" | grep -c 'push. My proposal: push branch `x` and open a pull request against `main`: user "approved"$')" 1

echo "-- awkward text is kept as typed"
run "$f" "bar" 'it'"'"'s "fine" at 95% & $HOME\n'
t "quotes, percent, dollar and backslash survive" "$(tail -n 1 "$f" | grep -cF 'user "it'"'"'s "fine" at 95% & $HOME\n"')" 1

echo "-- a missing file is started, its folder made"
run "$tmp/new/sub/rulings.md" "wants" 'tidy the csv'
t "exits 0" "$code" 0
t "one ruling line" "$(grep -c '^- ' "$tmp/new/sub/rulings.md")" 1

echo "-- refusals"
before=$(wc -l < "$f"); run "$f" "cap" ''
t "empty words are refused" "$code" 1
t "... and nothing is written" "$(wc -l < "$f")" "$before"
run "$f" "cap" "$(printf 'two\nlines')"
t "words are kept on one line (newline becomes a space)" "$(tail -n 1 "$f" | grep -c 'user "two lines"$')" 1
run; t "no arguments exits 2" "$code" 2
run "$f" "cap"; t "missing words exits 2" "$code" 2

[ "$fails" = 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
