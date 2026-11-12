#!/bin/bash
# Tests for subquota's report notes, against a stub management API serving synthetic accounts.
# Run: plugins/quota/tests/test_subquota.sh
set -euo pipefail

subquota=$(cd "$(dirname "$0")/.." && pwd)/bin/subquota
tmp=$(mktemp -d)
server=
trap '{ kill "$server" && wait "$server"; } 2>/dev/null || true; rm -rf "$tmp"' EXIT

mkdir -p "$tmp/home" "$tmp/www/v0/management"
echo test-key >"$tmp/key"
port=$(python3 -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')
python3 -m http.server "$port" --bind 127.0.0.1 --directory "$tmp/www" >/dev/null 2>&1 &
server=$!
for _ in $(seq 50); do curl -s -o /dev/null "http://127.0.0.1:$port/" && break; sleep 0.1; done

now=$(date +%s)
# account <name> <% used> <hours until the weekly reset>
account() {
  jq -nc --arg n "$1" --argjson used "$2" --argjson reset "$((now + $3 * 3600))" \
    --arg seen "$(date -u -r "$now" +%Y-%m-%dT%H:%M:%S+00:00)" '
    {name: $n, provider: "claude", auth_index: $n, email: "\($n)@example.com", weight: 50,
     quota: {observed_at: $seen, signals: {
       "Anthropic-Ratelimit-Unified-7d-Utilization": ($used / 100 | tostring),
       "Anthropic-Ratelimit-Unified-7d-Reset": ($reset | tostring)}}}'
}
report() { # report <account json>...
  printf '%s\n' "$@" | jq -sc '{files: .}' >"$tmp/www/v0/management/auth-files"
  HOME=$tmp/home QUOTA_PROXY_URL=http://127.0.0.1:$port QUOTA_MANAGEMENT_KEY_FILE=$tmp/key \
    QUOTA_SESSION_AUTH_DIR=$tmp/none "$subquota"
}

fails=0
expect() { # expect <name> <output> <fixed string that must appear>
  if grep -qF -- "$3" <<<"$2"; then echo "ok   $1"; else echo "FAIL $1: wanted '$3' in:"; sed 's/^/     /' <<<"$2"; fails=$((fails + 1)); fi
}
refute() { # refute <name> <output> <fixed string that must not appear>
  if grep -qF -- "$3" <<<"$2"; then echo "FAIL $1: unwanted '$3' in:"; sed 's/^/     /' <<<"$2"; fails=$((fails + 1)); else echo "ok   $1"; fi
}

# Half the week left (84h). spender: 45% left vs 50% (-5). even: 50% vs 50% (0). saver: 70% vs 50% (+20).
out=$(report "$(account spender 55 84)" "$(account even 50 84)" "$(account saver 30 84)")
expect "names accounts at or over pace, with their slack" "$out" "At or over pace: claude spender (-5), claude even (0)."
expect "asks for a mention in the first reply" "$out" "first reply"
refute "leaves out accounts with slack" "$(grep -F 'over pace' <<<"$out" || true)" "saver"

out=$(report "$(account saver 30 84)" "$(account thrifty 10 84)")
refute "says nothing when every account has slack" "$out" "over pace"
refute "asks for no mention when every account has slack" "$out" "first reply"

exit $((fails > 0))
