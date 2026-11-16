#!/usr/bin/env bash
# Unit tests for arbiter-loop's ratchet: per-pass git snapshots, a worse pass rejected (after a rerun of the check)
# and reset before the next worker, the supervisor's status line, restore of the best pass at a failing exit.
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
# With a timestamp in $tmp/pin it sets score's mtime to it after writing (a same-size rewrite git sees only by content).
# It saves its stdin as stdin-k and what it found on disk as saw-k (a.txt / score / ig.log / new-* files).
# A score line "a b" makes the check report a the first time it sees that pass's files and b on a rerun.
cat > "$tmp/worker.sh" <<EOF
n=\$(( \$(cat "$tmp/n") + 1 )); echo \$n > "$tmp/n"
cat > "$tmp/stdin-\$n"
echo "\$(cat a.txt) / \$(cat score) / \$(cat ig.log) / \$(ls new-*.txt 2>/dev/null | tr '\n' ' ')" > "$tmp/saw-\$n"
sed -n "\${n}p" "$tmp/seq" > score
echo "pass \$n" > a.txt
echo "pass \$n" > "new-\$n.txt"
echo "pass \$n" > ig.log
[ -s "$tmp/pin" ] && touch -t "\$(cat "$tmp/pin")" score
[ "\$n" = "\$(cat "$tmp/forge")" ] && echo 0 > "$s/passes"
exit 0
EOF
cat > "$tmp/check.sh" <<EOF
p=\$(cat "\$LOOP_DIR/a.txt"); echo "\$p" >> "$tmp/checks"
set -- \$(cat "\$LOOP_DIR/score")
if [ "\$(grep -cxF "\$p" "$tmp/checks")" -gt 1 ] && [ -n "\${2:-}" ]; then r=\$2; else r=\$1; fi
echo "\$r" > "\$ARBITER_RESULT"
EOF
CHECK="bash '$tmp/check.sh'"
checks() { grep -cxF "pass $1" "$tmp/checks"; } # how many times the check ran on pass k's files
g() { git -C "$w" "$@"; }

# fresh <git|plain> <score per pass...>: a loop directory at baseline score 0, and the worker's sequence.
fresh() {
  local kind=$1; shift
  rm -rf "$w" "$s"; mkdir -p "$w"; echo go > "$tmp/prompt.md"
  printf '%s\n' "$@" > "$tmp/seq"; echo 0 > "$tmp/n"; echo 0 > "$tmp/forge"; : > "$tmp/pin"; : > "$tmp/checks"; rm -f "$tmp"/stdin-* "$tmp"/saw-*
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

echo "-- a same-size rewrite whose stat matches the user's racily clean index entry is still snapshotted"
# Deterministic stand-in for a rewrite in the same second as the index entry: score keeps size and mtime (ctime is
# not trusted), and the index is as new as the entry, so git itself compares content. A copy of the index that took
# the current time as its mtime would skip that comparison and snapshot the old score.
fresh git 3 5 2
g config core.trustctime false; touch -t 202001010000 "$w/score"; g add score; touch -t 202001010000 "$w/.git/index"
echo 202001010000 > "$tmp/pin"; before=$(user_state)
run STALL=100 "$loop" "$w" 3
t "hits the cap (exit 2)" "$code" 2
t "each pass's snapshot holds its score" "$(g show refs/arbiter/pass-1:score 2>/dev/null) $(g show refs/arbiter/pass-2:score 2>/dev/null) $(g show refs/arbiter/pass-3:score 2>/dev/null)" "3 5 2"
t "the best pass's files are restored" "$(cat "$w/a.txt") $(cat "$w/score")" "pass 2 5"
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

nl='
'
echo "-- a worse pass confirmed by the rerun is rejected and reset before the next worker"
fresh git 3 5 2 6
run STALL=100 "$loop" "$w" 4
t "hits the cap (exit 2)" "$code" 2
t "the next worker found the best pass's files, the ignored file as the rejected pass left it" "$(cat "$tmp/saw-4")" "pass 2 / 5 / pass 3 / new-1.txt new-2.txt "
t "the rejected ref still holds the rejected tree" "$(g show refs/arbiter/pass-3:a.txt 2>/dev/null) $(g show refs/arbiter/pass-3:score 2>/dev/null) $(g show refs/arbiter/pass-3:new-3.txt 2>/dev/null)" "pass 3 2 pass 3"
t "the rejected ref's message says it was rejected" "$(g log -1 --format=%s refs/arbiter/pass-3 2>/dev/null | grep -c rejected)" 1
t "the check ran twice on the worse pass" "$(checks 3)" 2
t "the check ran once on each pass that was not worse" "$(checks 1) $(checks 2) $(checks 4)" "1 1 1"
t "the log says the pass was rejected" "$(has "$s/loop.log" 'pass 3: rejected')" yes
t "the log says the files were reset" "$(grep -c 'pass 3: files reset to refs/arbiter/pass-2 before pass 4' "$s/loop.log")" 1
t "status on the first pass: pass number and cap only" "$(cat "$tmp/stdin-1")" "go${nl}${nl}Status from the supervisor: pass 1 of 4."
t "status after a kept pass" "$(cat "$tmp/stdin-3")" "go${nl}${nl}Status from the supervisor: pass 3 of 4. Best count so far 5 (pass 2). The last pass was kept (count 5)."
t "status after a rejected pass" "$(cat "$tmp/stdin-4")" "go${nl}${nl}Status from the supervisor: pass 4 of 4. Best count so far 5 (pass 2). The last pass was rejected (count 2); its tree is readable at refs/arbiter/pass-3; do not restore from it."
t "the frozen prompt file is byte-identical to the prompt" "$(cmp -s "$tmp/prompt.md" "$s/prompt.md" && echo same || echo differs) $(cat "$s/prompt.md")" "same go"
t "the last pass is the best, so nothing is restored at exit" "$(cat "$w/a.txt") $(g rev-parse -q --verify refs/arbiter/final >/dev/null && echo final || echo nofinal)" "pass 4 nofinal"
t "the user's index, HEAD and branch are unchanged" "$(user_state)" "$before"
t "the user's unstaged change is kept apart from the index" "$(g diff --cached --name-only)" staged.txt

echo "-- a worse pass not confirmed by the rerun is kept, and the log says the check disagreed"
fresh git 3 5 "2 5" 1
run STALL=100 "$loop" "$w" 4
t "the check ran twice on the worse-looking pass" "$(checks 3)" 2
t "the next worker found that pass's files" "$(cat "$tmp/saw-4")" "pass 3 / 2 5 / pass 3 / new-1.txt new-2.txt new-3.txt "
t "the log says the two counts disagreed" "$(grep -c 'pass 3: .*disagreed.*2.*5' "$s/loop.log")" 1
t "the pass is kept with the rerun's count" "$(cat "$tmp/stdin-4")" "go${nl}${nl}Status from the supervisor: pass 4 of 4. Best count so far 5 (pass 2). The last pass was kept (count 5)."
t "the kept pass's ref records the rerun's count and no rejection" "$(g log -1 --format=%s refs/arbiter/pass-3 2>/dev/null | grep -c '5 passing') $(g log -1 --format=%s refs/arbiter/pass-3 2>/dev/null | grep -c rejected)" "1 0"

echo "-- a tie with the best is kept"
fresh git 3 5 5
run STALL=100 "$loop" "$w" 3
t "hits the cap (exit 2)" "$code" 2
t "the check ran once on the tied pass" "$(checks 3)" 1
t "the tied pass's files stay" "$(cat "$w/a.txt") $(ls "$w"/new-3.txt 2>/dev/null | wc -l | tr -d ' ')" "pass 3 1"
t "no final ref is written" "$(g rev-parse -q --verify refs/arbiter/final >/dev/null && echo yes || echo no)" no
t "the log does not say rejected" "$(has "$s/loop.log" rejected)" no

echo "-- a passing exit after a rejected pass"
fresh git 3 1 done
run STALL=100 "$loop" "$w" 9
t "the worker after the rejected pass found the best pass's files" "$(cat "$tmp/saw-3")" "pass 1 / 3 / pass 2 / new-1.txt "

echo "-- the status line without git"
fresh plain 3 5 2 1
run STALL=100 "$loop" "$w" 4
t "the check ran twice on the worse pass" "$(checks 3)" 2
t "nothing is reset: the next worker found the rejected pass's files" "$(cat "$tmp/saw-4")" "pass 3 / 2 / pass 3 / new-1.txt new-2.txt new-3.txt "
t "the log says nothing was reset" "$(grep -c 'pass 3: .*nothing was reset' "$s/loop.log")" 1
t "status after a kept pass" "$(cat "$tmp/stdin-2")" "go${nl}${nl}Status from the supervisor: pass 2 of 4. Best count so far 3 (pass 1). The last pass was kept (count 3)."
t "status after a rejected pass gives counts only" "$(cat "$tmp/stdin-4")" "go${nl}${nl}Status from the supervisor: pass 4 of 4. Best count so far 5 (pass 2). The last pass was rejected (count 2)."

echo "-- a pass below the starting state is rejected and reset to it"
fresh git 2 1; echo 4 > "$w/score"
run STALL=2 "$loop" "$w" 9
t "stalls (exit 3)" "$code" 3
t "the starting state is snapshotted with its count" "$(g log -1 --format=%s refs/arbiter/baseline-0 2>/dev/null | grep -c '4 passing')" 1
t "the check ran twice on the first pass" "$(checks 1)" 2
t "the log says pass 1 was rejected against the baseline" "$(grep -c 'pass 1: rejected (2, below the best 4 of the baseline)' "$s/loop.log")" 1
t "the second worker found the starting files" "$(cat "$tmp/saw-2")" "base / 4 / pass 1 / "
t "the second worker is told the baseline is the best" "$(grep -c 'Best count so far 4 (the baseline). The last pass was rejected (count 2)' "$tmp/stdin-2")" 1
t "the starting score is on disk at exit" "$(cat "$w/score")" 4
t "the starting tracked file is on disk at exit" "$(cat "$w/a.txt")" base
t "no pass's untracked file is left" "$(ls "$w"/new-*.txt 2>/dev/null | wc -l | tr -d ' ')" 0
t "the user's branch, HEAD, index and refs are untouched" "$(user_state)" "$before"

[ "$fails" = 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
