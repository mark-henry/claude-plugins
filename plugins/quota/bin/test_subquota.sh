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
    QUOTA_RESERVES="${RES-main@example.invalid=10}" QUOTA_FABLE_RESERVES="${FRES-main@example.invalid=10}" \
    QUOTA_SESSION_AUTH_DIR="$tmp/none" "$here/subquota" 2>&1
}
proposed() { # proposed <cred json>...  -> the "would rebalance" line, or "weights already match"
  local IFS=,; echo "{\"files\":[$*]}" > "$tmp/www/v0/management/auth-files"
  HOME="$tmp/home" QUOTA_PROXY_URL="http://127.0.0.1:$port" QUOTA_MANAGEMENT_KEY_FILE="$tmp/key" \
    QUOTA_RESERVES="${RES-main@example.invalid=10}" QUOTA_FABLE_RESERVES="${FRES-main@example.invalid=10}" \
    QUOTA_LOG="$tmp/log" "$here/subquota" --dry-run 2>&1 | tail -n 1
}
nt() { if [[ $2 != *"$3"* ]]; then echo "ok    $1"; else echo "FAIL  $1: unwanted \"$3\" in: $2"; fails=$((fails + 1)); fi; }
t() { if [[ $2 == *"$3"* ]]; then echo "ok    $1"; else echo "FAIL  $1: wanted \"$3\" in: $2"; fails=$((fails + 1)); fi; }

# Winner takes all. main keeps its last 10%, so its target runs down to 10%, not 0.
# Slack per account: side 20% used, 84h to reset: 80% vs 50% (+30, 0.36/h); main 14% used, 96h: 86% vs 61% (+25, 0.26/h).
out=$(proposed "$(cred side 1 0.20 84)" "$(cred main 1 0.14 96)")
t "both with slack: the most slack per hour to reset takes all" "$out" "side 1→100"
nt "both with slack: the other stays at the floor" "$out" "main 1→"

# side spent ahead of pace (21% left with 45h of 168h to go; even spend would leave 27%).
out=$(proposed "$(cred side 61 0.79 45)" "$(cred main 39 0.14 96)")
t "one ahead of pace: it drops to the floor" "$out" "side 61→1 "
t "one ahead of pace: the one with slack takes all" "$out" "main 39→100"
out=$(proposed "$(cred side 61 0.20 84)" "$(cred main 39 0.59 70)")
t "protected ahead of pace: the floor" "$out" "main 39→1 "
t "protected ahead of pace: the other takes all" "$out" "side 61→100"

# Both ahead (2026-11-18 bug: the protected account took everything). The least far ahead takes all.
# side 21% vs 27% (-6); main 30% vs 48% (-18).
out=$(proposed "$(cred side 1 0.79 45)" "$(cred main 100 0.70 70)")
t "both ahead: the least far ahead takes all" "$out" "side 1→100"
t "both ahead: the protected account does not take everything" "$out" "main 100→1 "
# side 10% vs 27% (-17); main 41% vs 48% (-7).
out=$(proposed "$(cred side 100 0.90 45)" "$(cred main 1 0.59 70)")
t "both ahead: the protected account wins when it is the least far ahead" "$out" "main 1→100"

# Urgency: slack about to be lost at a reset goes first. A: 16% left, resets in 2h (+15, 7.4/h);
# B: 91% left, resets in 5 days (+20, 0.16/h). B has more slack, A loses its slack soonest.
out=$(RES= FRES= proposed "$(cred a 1 0.84 2)" "$(cred b 100 0.09 120)")
t "urgency: the account about to lose its slack takes all" "$out" "a 1→100"
t "urgency: the one with more slack but days to go waits" "$out" "b 100→1 "

# An account with no quota reading (after a proxy restart) at weight 0 must not stay shut out.
out=$(proposed "$(cred side 0 none 0)" "$(cred main 100 0.14 96)")
t "no data at weight 0: a bigger floor, so it serves a request soon and can be read" "$out" "side 0→10 "

# A reserve is a last resort, not a wall: inside it the account loses to any account with slack,
# but stays in the pool, and takes everything once nothing else is left.
out=$(proposed "$(cred side 100 0.86 18)" "$(cred main 0 0.59 70)")
t "protected, behind its target but above the reserve: the floor, not zero" "$out" "main 0→1 "
out=$(proposed "$(cred side 100 0.86 18)" "$(cred main 10 0.92 70)")
t "protected, inside its last 10%: the floor while another account has slack" "$out" "main 10→1 "
out=$(proposed "$(cred side 100 1.00 18)" "$(cred main 10 0.92 70)")
t "protected, inside its last 10%: takes everything when nothing else is left" "$out" "main 10→100"

# Per-account reserves: each target runs down to that account's reserve.
out=$(RES="main@example.invalid=10,side@example.invalid=5" report "$(cred side 1 0.50 84)" "$(cred main 1 0.50 84)")
t "report: a second reserve shows" "$out" "side (weight 1): keeps 5%, 50% vs 5"
t "report: the first reserve shows" "$out" "main (weight 1): keeps 10%, 50% vs 55% (-5)"
out=$(RES="main@example.invalid=10" report "$(cred side 1 0.50 84)")
nt "report: no reserve, no note" "$out" "keeps"

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

# Two Fable reserves never hold each other: an account inside its own Fable reserve serves no one else.
out=$(FRES="main@example.invalid=10,side@example.invalid=10" proposed "$(cred side 50 0.40 84 0.95)" "$(cred main 50 0.40 84 0.95)")
nt "Fable reserve: two accounts inside their reserves: neither held" "$out" "Fable reserve"
out=$(FRES="main@example.invalid=10,side@example.invalid=10" proposed "$(cred side 50 0.40 84 0.30)" "$(cred main 50 0.40 84 0.95)")
t "Fable reserve: per account" "$out" "main Fable reserve held"

[ "$fails" = 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
