#!/usr/bin/env bash
# Checks on the swarm:brief cases that need no model. Run from the repo root.
set -u
fail=0
python3 tests/brief-histories.py --check || fail=1
for d in tests/brief-*/; do
  [ -f "$d/case.yaml" ] || continue
  for f in prompt.md fixture.sh graders/verdict.md graders/liveness.md; do
    [ -f "$d/$f" ] || { echo "missing $d$f"; fail=1; }
  done
done
# only files git tracks or would track: the session files the harness leaves beside histories are ignored
if git ls-files -co --exclude-standard 'tests/brief-*' | grep -v 'tests/brief-check.sh' | xargs grep -Il -E '/Users/|/home/[a-z]' 2>/dev/null; then echo "a home path is in the files above"; fail=1; fi
exit $fail
