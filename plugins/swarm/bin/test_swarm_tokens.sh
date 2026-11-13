#!/usr/bin/env bash
# Tests for swarm-tokens. Run: bash plugins/swarm/bin/test_swarm_tokens.sh
set -uo pipefail
here=$(cd "$(dirname "$0")" && pwd)
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
fails=0
t() { if [ "$2" = "$3" ]; then echo "ok    $1"; else echo "FAIL  $1: wanted [$3], got [$2]"; fails=$((fails + 1)); fi; }
d=$tmp/subagents; mkdir -p "$d"
msg() { # msg <file> <message id> <model> <in> <cache_write> <cache_read> <out>
  printf '{"type":"assistant","message":{"id":"%s","model":"%s","usage":{"input_tokens":%s,"cache_creation_input_tokens":%s,"cache_read_input_tokens":%s,"output_tokens":%s}}}\n' "$2" "$3" "$4" "$5" "$6" "$7" >> "$d/$1"
}
meta() { printf '{"description":"%s"%s}\n' "$2" "${3:+,\"parentAgentId\":\"$3\"}" > "$d/agent-$1.meta.json"; }
echo '{"type":"user","message":{"content":"You are the driver of the tidy run"}}' > "$d/agent-aaa.jsonl"
meta aaa "Driver"; msg agent-aaa.jsonl m1 big 10 100 1000 20; msg agent-aaa.jsonl m1 big 10 100 1000 20; msg agent-aaa.jsonl m2 big 5 0 2000 30
meta bbb "Attacker" aaa; msg agent-bbb.jsonl m3 small 1 10 100 7
meta ccc "Helper" bbb; msg agent-ccc.jsonl m4 small 2 0 0 3
meta zzz "Unrelated"; msg agent-zzz.jsonl m5 big 999 999 999 999

out=$("$here/swarm-tokens" "$d" --agent aaa --json)
j() { python3 -c "import json,sys; d=json.load(sys.stdin); print($1)" <<< "$out"; }
t "a repeated message id is counted once" "$(j "d['agents']['aaa']['output']")" 50
t "own tokens exclude children" "$(j "d['agents']['aaa']['input']")" 15
t "the subtree adds every descendant" "$(j "d['subtree']['output']")" 60
t "an unrelated agent is left out" "$(j "'zzz' in d['agents']")" False
t "totals are kept per model" "$(j "d['by_model']['small']['output']")" 10
t "weighted counts input 1, cache write 1.25, cache read 0.1, output 5" "$(j "d['agents']['bbb']['weighted']")" 58.5
t "an agent is found by its description" "$("$here/swarm-tokens" "$d" --match attacker --json | python3 -c "import json,sys; print(sorted(json.load(sys.stdin)['agents']))")" "['bbb', 'ccc']"
t "or by the start of its first prompt" "$("$here/swarm-tokens" "$d" --match "driver of the tidy" --json | python3 -c "import json,sys; print(json.load(sys.stdin)['root'])")" aaa
t "the table names each agent" "$("$here/swarm-tokens" "$d" --agent aaa | grep -c 'Attacker')" 1
[ "$fails" = 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
