#!/usr/bin/env bash
# Supervisor for an oracle-gated agent loop (see SKILL.md).
# Each pass: a fresh agent reads PROMPT.md, then the supervisor (not the agent) runs the check.
#
# usage: AGENT_CMD='...' CHECK_CMD='...' run-loop.sh <loop-dir> [max-passes]
#   AGENT_CMD  required. Reads the prompt on stdin. Run it inside a sandbox if it bypasses permissions.
#   CHECK_CMD  required. Exit 0 when done; otherwise its last output line starts with the number passing.
#   STALL      passes without a new best before stopping (default 3).
# Stops on: check exit 0 (done, exit 0), max passes (exit 2), stall (exit 3), a STOP file in <loop-dir> (exit 4).
set -euo pipefail

dir=${1:?usage: run-loop.sh <loop-dir> [max-passes]}
cap=${2:-20}
stall=${STALL:-3}
: "${AGENT_CMD:?set AGENT_CMD}" "${CHECK_CMD:?set CHECK_CMD}"

cd "$dir"
[ -f PROMPT.md ] || { echo "no PROMPT.md in $dir" >&2; exit 1; }
mkdir -p logs
best=-1
flat=0

for ((i = 1; i <= cap; i++)); do
  if [ -f STOP ]; then echo "STOP file found before pass $i" | tee -a loop.log; exit 4; fi
  echo "pass $i start $(date -u +%FT%TZ)" >> loop.log
  # An agent that dies or exits nonzero is restarted by the next pass, not fatal.
  bash -c "$AGENT_CMD" < PROMPT.md > "logs/pass-$i.log" 2>&1 || echo "pass $i: agent exited $?" >> loop.log
  if out=$(bash -c "$CHECK_CMD" 2>&1); then
    echo "pass $i: check passed, done" | tee -a loop.log
    exit 0
  fi
  n=$(printf '%s\n' "$out" | tail -n 1 | grep -Eo '^[0-9]+' || true)
  n=${n:-0}
  echo "pass $i: $n passing" >> loop.log
  if [ "$n" -gt "$best" ]; then best=$n; flat=0; else flat=$((flat + 1)); fi
  if [ "$flat" -ge "$stall" ]; then echo "stalled: $stall passes without a new best ($best)" | tee -a loop.log; exit 3; fi
done
echo "hit max passes ($cap), best $best" | tee -a loop.log
exit 2
