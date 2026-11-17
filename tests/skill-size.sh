#!/bin/bash
# Plain test, no model: every plugins/*/skills/*/SKILL.md is under 20,000 characters.
# usage: bash tests/skill-size.sh   (from anywhere; exit 1 names each file at or over the limit)
cd "$(dirname "$0")/.." || exit 2
limit=20000; fail=0; n=0
for f in plugins/*/skills/*/SKILL.md; do
  [ -e "$f" ] || continue
  n=$((n + 1))
  chars=$(python3 -c 'import sys; print(len(open(sys.argv[1], encoding="utf-8").read()))' "$f")
  if [ "$chars" -ge "$limit" ]; then echo "FAIL $f: $chars characters (limit $limit)"; fail=1; fi
done
[ "$n" -gt 0 ] || { echo "FAIL no SKILL.md found"; exit 1; }
[ "$fail" -eq 0 ] && echo "ok: $n SKILL.md files, each under $limit characters"
exit $fail
