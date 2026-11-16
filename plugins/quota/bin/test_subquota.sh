#!/usr/bin/env bash
# Tests for subquota's rebalance policy. Run: bash plugins/quota/bin/test_subquota.sh
# Serves a fixture in place of CLIProxyAPI's management API and reads the weights --dry-run proposes.
set -uo pipefail
here=$(cd "$(dirname "$0")" && pwd)
tmp=$(mktemp -d); port=18$((RANDOM % 900 + 100))
mkdir -p "$tmp/www/v0/management" "$tmp/home"; echo k > "$tmp/key"
(cd "$tmp/www" && exec python3 -m http.server "$port" --bind 127.0.0.1 >/dev/null 2>&1) & srv=$!
trap 'kill $srv 2>/dev/null; wait $srv 2>/dev/null; rm -rf "$tmp"' EXIT
for _ in 1 2 3 4 5 6 7 8 9 10; do curl -s -o /dev/null "http://127.0.0.1:$port/" && break; sleep 0.2; done
now=$(date +%s); fails=0

cred() { # cred <name> <weight> <used fraction | none> <hours to reset> [<Fable used fraction> [rejected]]
  local sig='{}' mq='{}'
  [[ $3 != none ]] && sig="{\"Anthropic-Ratelimit-Unified-7d-Utilization\":\"$3\",\"Anthropic-Ratelimit-Unified-7d-Reset\":\"$((now + $4 * 3600))\"}"
  # Fable responses carry an extra weekly window, 7d_oi, which is the one that rejects Fable.
  [[ -n ${5:-} ]] && mq="{\"claude-fable-5-2\":{\"observed_at\":\"2026-01-01T00:00:00+00:00\",\"signals\":{\"Anthropic-Ratelimit-Unified-7d-Utilization\":\"$3\",\"Anthropic-Ratelimit-Unified-7d-Reset\":\"$((now + $4 * 3600))\",\"Anthropic-Ratelimit-Unified-7d_oi-Utilization\":\"$5\",\"Anthropic-Ratelimit-Unified-7d_oi-Reset\":\"$((now + $4 * 3600))\",\"Anthropic-Ratelimit-Unified-7d_oi-Status\":\"${6:-allowed}\"}}}"
  echo "{\"name\":\"$1.json\",\"provider\":\"claude\",\"auth_index\":\"$1\",\"email\":\"$1@example.invalid\",\"weight\":$2,\"quota\":{\"signals\":$sig,\"observed_at\":\"2026-01-01T00:00:00+00:00\"},\"model_quotas\":$mq}"
}
report() { # report <cred json>...  -> the plain report
  local IFS=,; echo "{\"files\":[$*]}" > "$tmp/www/v0/management/auth-files"
  HOME="$tmp/home" QUOTA_PROXY_URL="http://127.0.0.1:$port" QUOTA_MANAGEMENT_KEY_FILE="$tmp/key" \
    QUOTA_PROTECTED_EMAIL=main@example.invalid QUOTA_SESSION_AUTH_DIR="$tmp/none" "$here/subquota" 2>&1
}
proposed() { # proposed <cred json>...  -> the "would rebalance" line, or "weights already match"
  local IFS=,; echo "{\"files\":[$*]}" > "$tmp/www/v0/management/auth-files"
  HOME="$tmp/home" QUOTA_PROXY_URL="http://127.0.0.1:$port" QUOTA_MANAGEMENT_KEY_FILE="$tmp/key" \
    QUOTA_PROTECTED_EMAIL=main@example.invalid QUOTA_LOG="$tmp/log" "$here/subquota" --dry-run 2>&1 | tail -n 1
}
nt() { if [[ $2 != *"$3"* ]]; then echo "ok    $1"; else echo "FAIL  $1: unwanted \"$3\" in: $2"; fails=$((fails + 1)); fi; }
t() { if [[ $2 == *"$3"* ]]; then echo "ok    $1"; else echo "FAIL  $1: wanted \"$3\" in: $2"; fails=$((fails + 1)); fi; }

# Both accounts on pace: weights follow the burn rate each can afford (unchanged behavior).
out=$(proposed "$(cred side 1 0.20 84)" "$(cred main 1 0.14 96)")
t "on pace: the side account gets its share" "$out" "side 1→55"
t "on pace: the protected account gets its share" "$out" "main 1→45"

# The side account has spent ahead of pace (21% left with 45h of 168h to go; even spend would leave 27%).
out=$(proposed "$(cred side 61 0.79 45)" "$(cred main 39 0.14 96)")
t "ahead of pace: the account drops to the floor" "$out" "side 61→1 "
t "ahead of pace: the on-pace account takes the rest" "$out" "main 39→100"

# An account with no quota reading (after a proxy restart) at weight 0 must not stay shut out.
out=$(proposed "$(cred side 0 none 0)" "$(cred main 100 0.14 96)")
t "no data at weight 0: a bigger floor, so it serves a request soon and can be read" "$out" "side 0→10 "

# The protected account is saved for the web app: only its last 10% is a last resort. Short of that it
# follows the same pace rules as any account, so a point behind its target is the floor, not zero.
out=$(proposed "$(cred side 100 0.86 18)" "$(cred main 0 0.59 70)")
t "protected, behind its target but above the reserve: the floor, not zero" "$out" "main 0→1 "
out=$(proposed "$(cred side 100 0.86 18)" "$(cred main 10 0.92 70)")
t "protected, inside its last 10%: weight 0 while another account has headroom" "$out" "main 10→0"
out=$(proposed "$(cred side 100 1.00 18)" "$(cred main 10 0.92 70)")
t "protected, inside its last 10%: takes everything when nothing else is left" "$out" "main 10→100"

# An account with nothing left gets nothing.
out=$(proposed "$(cred side 30 1.00 45)" "$(cred main 70 0.14 96)")
t "nothing left: weight 0" "$out" "side 30→0"

# Fable. Weight 0 takes an account out of the proxy's pool, so a session whose account has hit its
# Fable cap gets "no auth candidates" instead of failing over. (2026-11-13: side has Fable rejected;
# main is protected, a point behind its target and well above its reserve, with Fable to spare.)
out=$(proposed "$(cred side 100 0.86 18 1.0 rejected)" "$(cred main 0 0.59 70 0.8)")
t "Fable blocked elsewhere: the account with Fable left stays in the pool" "$out" "main 0→1 "

out=$(report "$(cred side 100 0.86 18 1.0 rejected)" "$(cred main 0 0.59 70 0.8)")
t "report: Fable left per account" "$out" "Fable 20% left"
t "report: a blocked account says when Fable comes back" "$out" "Fable blocked, back in 18h"
t "report: says where Fable falls back to" "$out" "Fable blocked on side; its sessions fall back to main"
out=$(report "$(cred side 100 0.86 18 1.0 rejected)" "$(cred main 0 0.59 70 1.0 rejected)")
t "report: says when Fable is blocked everywhere" "$out" "Fable blocked on every account"

# Fable reserve: the protected account's last 10% of its Fable cap is a last resort too. Held by
# excluding Fable on that credential while another account can serve Fable; released otherwise.
held() { jq -c '.excluded_models = ["claude-fable-*"]' <<<"$1"; }
out=$(proposed "$(cred side 50 0.40 84 0.30)" "$(cred main 50 0.40 84 0.95)")
t "Fable reserve: held when the protected account is inside its last 10% of Fable" "$out" "main Fable reserve held"
out=$(report "$(cred side 50 0.40 84 0.30)" "$(held "$(cred main 50 0.40 84 0.95)")")
t "report: says the Fable reserve is held" "$out" "Fable reserve held: last resort only"
out=$(proposed "$(cred side 50 0.40 84 0.30)" "$(held "$(cred main 50 0.40 84 0.95)")")
nt "Fable reserve: already held, nothing to change" "$out" "Fable reserve"
out=$(proposed "$(cred side 50 0.40 84 1.0 rejected)" "$(held "$(cred main 50 0.40 84 0.95)")")
t "Fable reserve: released as the last resort when the other account is Fable-blocked" "$out" "main Fable reserve released"
out=$(proposed "$(cred side 50 0.40 84 0.995)" "$(cred main 50 0.40 84 0.95)")
nt "Fable reserve: not held when the other account is within 1% of its Fable cap" "$out" "Fable reserve"
out=$(proposed "$(cred side 50 0.40 84 0.30)" "$(cred main 50 0.40 84 0.50)")
nt "Fable reserve: not held above the last 10%" "$out" "Fable reserve"
out=$(proposed "$(cred side 50 0.40 84 0.30)" "$(jq -c '.excluded_models = ["claude-fable-*", "claude-haiku-*"]' <<<"$(cred main 50 0.40 84 0.50)")")
t "Fable reserve: released above the last 10%" "$out" "main Fable reserve released"
out=$(proposed "$(cred side 50 0.40 84 0.30)" "$(cred main 50 0.40 84)")
nt "Fable reserve: nothing held without a Fable reading" "$out" "Fable reserve"

# Holding Fable drops the credential's Fable reading (and it serves no Fable to renew it), so the hold
# runs on the reset time saved when it was set, instead of flapping open on "no reading".
saved() { mkdir -p "$tmp/home/.cache/quota"; echo "{\"main.json\": $((now + $1 * 3600))}" > "$tmp/home/.cache/quota/fable-holds.json"; }
saved 20
out=$(proposed "$(cred side 50 0.40 84 0.30)" "$(held "$(cred main 50 0.40 84)")")
nt "Fable reserve: held with no reading keeps holding until the saved reset" "$out" "Fable reserve"
out=$(proposed "$(cred side 50 0.40 84 1.0 rejected)" "$(held "$(cred main 50 0.40 84)")")
t "Fable reserve: held with no reading still released as the last resort" "$out" "main Fable reserve released"
saved -1
out=$(proposed "$(cred side 50 0.40 84 0.30)" "$(held "$(cred main 50 0.40 84)")")
t "Fable reserve: released once the saved reset has passed" "$out" "main Fable reserve released"
rm -f "$tmp/home/.cache/quota/fable-holds.json"
out=$(proposed "$(cred side 50 0.40 84 0.30)" "$(held "$(cred main 50 0.40 84)")")
t "Fable reserve: released with no reading and no saved reset" "$out" "main Fable reserve released"

[ "$fails" = 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
