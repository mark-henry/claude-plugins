#!/usr/bin/env bash
# Unit tests for arbiter-loop's ratchet: per-pass git snapshots, restore of the best pass at a failing exit.
# Run: bash tests/arbiter-ratchet.sh. Throwaway repositories under a temp directory; a fake worker and check.
set -uo pipefail
loop=${ARBITER_LOOP:-$(cd "$(dirname "$0")/.." && pwd)/plugins/unattended/bin/arbiter-loop}
tmp=$(cd "$(mktemp -d)" && pwd -P); trap 'rm -rf "$tmp"' EXIT
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 # no user identity, signing or hooks from this machine
fails=0
t() { if [ "$2" = "$3" ]; then echo "ok    $1"; else echo "FAIL  $1: wanted $3, got $2"; fails=$((fails + 1)); fi; }
has() { grep -qF -- "$2" "$1" && echo yes || echo no; }

w=$tmp/w s=$tmp/s
# The fake worker: pass k writes line k of $tmp/seq to `score`, rewrites a tracked file, adds an untracked file,
# and rewrites an ignored one. With FORGE=k it also forges the pass count on pass k (the existing tamper check).
cat > "$tmp/worker.sh" <<EOF
n=\$(( \$(cat "$tmp/n") + 1 )); echo \$n > "$tmp/n"
sed -n "\${n}p" "$tmp/seq" > score
echo "pass \$n" > a.txt
echo "pass \$n" > "new-\$n.txt"
echo "pass \$n" > ig.log
[ "\$n" = "\$(cat "$tmp/forge")" ] && echo 0 > "$s/passes"
exit 0
EOF
CHECK='s=$(cat "$LOOP_DIR/score"); echo "$s" > "$ARBITER_RESULT"'
g() { git -C "$w" "$@"; }

# fresh <git|plain> <score per pass...>: a loop directory at baseline score 0, and the worker's sequence.
fresh() {
  local kind=$1; shift
  rm -rf "$w" "$s"; mkdir -p "$w"; echo go > "$tmp/prompt.md"
  printf '%s\n' "$@" > "$tmp/seq"; echo 0 > "$tmp/n"; echo 0 > "$tmp/forge"
  echo 0 > "$w/score"; echo base > "$w/a.txt"; echo base > "$w/staged.txt"; echo base > "$w/ig.log"
  if [ "$kind" = git ]; then
    echo '*.log' > "$w/.gitignore"
    g init -q -b main; g add -A; g -c user.name=t -c user.email=t@t commit -q -m base
    echo staged > "$w/staged.txt"; g add staged.txt; echo unstaged > "$w/staged.txt" # the user's own index state
    before=$(user_state)
  fi
}
user_state() { echo "$(g symbolic-ref HEAD) $(g rev-parse HEAD) $(md5 -q "$w/.git/index" 2>/dev/null || md5sum "$w/.git/index") $(g for-each-ref --format='%(refname)' refs/heads refs/tags | tr '\n' ' ')"; }
run() { env AGENT_CMD="bash '$tmp/worker.sh'" CHECK_CMD="$CHECK" PROMPT="$tmp/prompt.md" STATE_DIR="$s" "$@" > "$tmp/out" 2>&1; code=$?; }

echo "-- a stall after a regression"
fresh git 3 5 2 1
run STALL=2 "$loop" "$w" 9
t "stalls (exit 3)" "$code" 3
t "a snapshot ref exists for each of the four passes" "$(g for-each-ref --format=x 'refs/arbiter/pass-*' | wc -l | tr -d ' ')" 4
t "each snapshot records its pass's count" "$(g log -1 --format=%s refs/arbiter/pass-2 2>/dev/null | grep -c '5 passing')" 1
t "the best pass's tracked file is restored" "$(cat "$w/a.txt")" "pass 2"
t "the best pass's score is restored" "$(cat "$w/score")" 5
t "untracked files from the best pass are restored" "$(cat "$w/new-2.txt" 2>/dev/null)" "pass 2"
t "untracked files added after the best pass are removed" "$(ls "$w"/new-3.txt "$w"/new-4.txt 2>/dev/null | wc -l | tr -d ' ')" 0
t "the final state is saved under refs/arbiter/final" "$(g show refs/arbiter/final:score 2>/dev/null)" 1
t "... with the last pass's untracked file in it" "$(g show refs/arbiter/final:new-4.txt 2>/dev/null)" "pass 4"
t "the report gives the best count" "$(has "$tmp/out" 'best count 5')" yes
t "the report names the best pass's ref" "$(has "$tmp/out" refs/arbiter/pass-2)" yes
t "the report names the final ref" "$(has "$tmp/out" refs/arbiter/final)" yes
t "the existing stall line is unchanged" "$(has "$tmp/out" 'stalled: 2 passes without a new best (5)')" yes
t "untracked files are in a pass's snapshot" "$(g show refs/arbiter/pass-1:new-1.txt 2>/dev/null)" "pass 1"
t "ignored files are not in a snapshot" "$(g cat-file -e refs/arbiter/pass-1:ig.log 2>/dev/null && echo in || echo out)" out
t "ignored files are left alone by the restore" "$(cat "$w/ig.log")" "pass 4"
t "the user's index, HEAD and branch are unchanged" "$(user_state)" "$before"
t "the user's unstaged change is kept apart from the index" "$(g diff --cached --name-only)" staged.txt
t "no tamper warning when nothing was forged" "$(has "$tmp/out" tamper)" no

echo "-- the cap exit"
fresh git 3 5 2
run STALL=100 "$loop" "$w" 3
t "hits the cap (exit 2)" "$code" 2
t "the existing cap line is unchanged" "$(has "$tmp/out" 'hit max passes (3), best 5')" yes
t "the best pass's files are restored" "$(cat "$w/a.txt") $(cat "$w/score")" "pass 2 5"
t "the final state is saved under refs/arbiter/final" "$(g show refs/arbiter/final:score 2>/dev/null)" 2
t "the user's index, HEAD and branch are unchanged" "$(user_state)" "$before"

echo "-- a passing exit"
fresh git 3 1 done
run STALL=100 "$loop" "$w" 9
t "exits 0" "$code" 0
t "each pass has a snapshot" "$(g for-each-ref --format=x 'refs/arbiter/pass-*' | wc -l | tr -d ' ')" 3
t "nothing is restored" "$(cat "$w/a.txt") $(cat "$w/score")" "pass 3 done"
t "no final ref is written" "$(g rev-parse -q --verify refs/arbiter/final >/dev/null && echo yes || echo no)" no
t "the user's index, HEAD and branch are unchanged" "$(user_state)" "$before"

echo "-- the last pass is the best"
fresh git 1 3
run STALL=100 "$loop" "$w" 2
t "hits the cap (exit 2)" "$code" 2
t "nothing is restored" "$(cat "$w/a.txt")" "pass 2"
t "no final ref is written" "$(g rev-parse -q --verify refs/arbiter/final >/dev/null && echo yes || echo no)" no

echo "-- no git repository"
fresh plain 3 5 2 1
run STALL=2 "$loop" "$w" 9
t "stalls (exit 3)" "$code" 3
t "the report gives the best count" "$(has "$tmp/out" 'best count 5')" yes
t "the report says nothing was restored" "$(has "$tmp/out" 'nothing was restored')" yes
t "the files are left as the last pass made them" "$(cat "$w/a.txt") $(cat "$w/score")" "pass 4 1"

echo "-- a tamper-flagged best pass"
fresh git 3 5 2 1; echo 2 > "$tmp/forge"
run STALL=2 "$loop" "$w" 9
t "stalls (exit 3) rather than refusing mid-run" "$code" 3
t "the best pass is still restored" "$(cat "$w/a.txt")" "pass 2"
t "the report warns that the best pass was flagged by the tamper check" "$(grep -c 'warning.*pass 2.*tamper' "$tmp/out")" 1
fresh git 3 5 2 1; echo 3 > "$tmp/forge"
run STALL=2 "$loop" "$w" 9
t "a flag on a pass that is not the best draws no warning" "$(grep -c 'warning.*tamper' "$tmp/out")" 0

[ "$fails" = 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
