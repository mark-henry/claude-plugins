#!/usr/bin/env bash
# Unit tests for plugins/afk/bin/afk-done (not a `claude plugin eval` case). Run: bash tests/afk-done.sh
set -uo pipefail
done_=${AFK_DONE:-$(cd "$(dirname "$0")/.." && pwd)/plugins/afk/bin/afk-done}
tmp=$(cd "$(mktemp -d)" && pwd -P); trap 'chmod -R u+w "$tmp" 2>/dev/null; rm -rf "$tmp"' EXIT
fails=0
t() { if [ "$2" = "$3" ]; then echo "ok    $1"; else echo "FAIL  $1: wanted $3, got $2"; fails=$((fails + 1)); fi; }
run() { "$done_" "$@" > "$tmp/out" 2> "$tmp/err"; code=$?; }
fresh() { chmod -R u+w "$tmp" 2>/dev/null; rm -rf "$tmp/r" "$tmp/d"; mkdir -p "$tmp/r" "$tmp/d"; }

echo "-- the report must exist"
fresh; run "$tmp/r" "$tmp/d/runs.md" "2026-01-01 | job | 1M of 2M | 1h | done"
t "no report.md is refused" "$code" 1
t "... and nothing is logged" "$([ -e "$tmp/d/runs.md" ] && echo yes || echo no)" no
t "... and the refusal names the file" "$(grep -c 'report.md' "$tmp/err")" 1
fresh; : > "$tmp/r/report.md"; run "$tmp/r" "$tmp/d/runs.md" "line"
t "an empty report.md is refused" "$code" 1

echo "-- a report that exists is logged and its status line printed"
fresh; printf 'pending, 2 decisions waiting\n\nbody\n' > "$tmp/r/report.md"
run "$tmp/r" "$tmp/d/runs.md" "2026-01-01 | job | 1M of 2M | 1h | pending"
t "exits 0" "$code" 0
t "prints the report's first line" "$(head -n 1 "$tmp/out")" "pending, 2 decisions waiting"
t "appends the line" "$(tail -n 1 "$tmp/d/runs.md")" "2026-01-01 | job | 1M of 2M | 1h | pending"
run "$tmp/r" "$tmp/d/runs.md" "second"
t "a second call appends, never rewrites" "$(wc -l < "$tmp/d/runs.md" | tr -d ' ')" 2
printf '\n\n# Report\n\ndone\n' > "$tmp/r/report.md"; run "$tmp/r" "$tmp/d/runs.md" "third"
t "the status line is the first line with text, heading marks dropped" "$(head -n 1 "$tmp/out")" "Report"

echo "-- the exchange row"
fresh; echo done > "$tmp/r/report.md"
run "$tmp/r" "$tmp/d/runs.md" "line" --exchange "| opus | 1.2M | 41% | 38% |"
t "--exchange writes exchange.md beside runs.md" "$(tail -n 1 "$tmp/d/exchange.md")" "| opus | 1.2M | 41% | 38% |"

echo "-- a log that cannot be written does not lose the report"
fresh; echo done > "$tmp/r/report.md"; chmod a-w "$tmp/d"
run "$tmp/r" "$tmp/d/runs.md" "line"
t "exits 0" "$code" 0
t "still prints the status line" "$(head -n 1 "$tmp/out")" "done"
t "says the log was not written" "$(grep -c 'not written' "$tmp/out")" 1
t "... and no shell error leaks" "$(wc -c < "$tmp/err" | tr -d ' ')" 0
fresh; echo done > "$tmp/r/report.md"; run "$tmp/r" "$tmp/d/new/sub/runs.md" "line"
t "creates the log's folder when it can" "$(tail -n 1 "$tmp/d/new/sub/runs.md" 2>/dev/null)" "line"

echo "-- usage"
run; t "no arguments exits 2" "$code" 2

[ "$fails" = 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
