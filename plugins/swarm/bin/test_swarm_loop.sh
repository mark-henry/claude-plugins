#!/usr/bin/env bash
# Tests for swarm-loop. Run: bash plugins/swarm/bin/test_swarm_loop.sh
set -uo pipefail
here=$(cd "$(dirname "$0")" && pwd)
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
fails=0
t() { if [ "$2" = "$3" ]; then echo "ok    $1"; else echo "FAIL  $1: wanted $3, got $2"; fails=$((fails + 1)); fi; }

# A loop whose check never passes: each agent pass appends one line to runs.txt.
new_loop() { rm -rf "$tmp/w" "$tmp/w.swarm-loop" "$tmp/runs.txt"; mkdir -p "$tmp/w"; echo go > "$tmp/w/PROMPT.md"; : > "$tmp/runs.txt"; }
launch() { # launch <cap>; sets code
  AGENT_CMD="echo \"agent run \$(wc -l < '$tmp/runs.txt' | tr -d ' ')\"; echo x >> '$tmp/runs.txt'" \
  CHECK_CMD='echo 0; exit 1' STALL=100 "$here/swarm-loop" "$tmp/w" "$1" > /dev/null 2>&1; code=$?
}
runs() { wc -l < "$tmp/runs.txt" | tr -d ' '; }

new_loop
launch 2
t "first launch stops at the cap" "$code" 2
t "first launch ran two passes" "$(runs)" 2

launch 2
t "relaunch at the same cap exits 2" "$code" 2
t "relaunch at the same cap runs no agent" "$(runs)" 2
t "relaunch leaves pass 1's log alone" "$(cat "$tmp/w.swarm-loop/logs/pass-1.log")" "agent run 0"

launch 3
t "raising the cap by one runs one more pass" "$(runs)" 3
t "the new pass is numbered after the old ones" "$(cat "$tmp/w.swarm-loop/logs/pass-3.log" 2>/dev/null)" "agent run 2"

new_loop
AGENT_CMD=true CHECK_CMD='echo 0; exit 1' FINAL_CMD='echo held-out-1' STALL=100 "$here/swarm-loop" "$tmp/w" 1 > /dev/null 2>&1
AGENT_CMD=true CHECK_CMD='echo 0; exit 1' FINAL_CMD='echo held-out-2' STALL=100 "$here/swarm-loop" "$tmp/w" 2 > /dev/null 2>&1
t "each launch keeps its own final log" "$(cat "$tmp/w.swarm-loop/logs"/final-*.log | tr '\n' ' ')" "held-out-1 held-out-2 "

[ "$fails" = 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
