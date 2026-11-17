#!/usr/bin/env python3
"""Run one whole `afk:interview` interview between a confined subject session and a
scripted stand-in user.

    drive.py <card.json> --model sonnet --out <dir> [--max-turns 20] [--turn-timeout 900]
    drive.py --raw-turn <workspace> --model haiku --prompt <text>   (one subject turn, stream to stdout;
                                                                      used by confine-check.sh)

Standard library only. The subject is the real binary with the proxy environment set by hand
and the settings file next to this script; the stand-in is the same binary with no tools, no
plugins and a system prompt built from the card (standin.md).
"""
import argparse
import json
import os
import re
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
HOME = Path(os.environ.get("HOME", str(Path.home())))
CLAUDE = HOME / ".local" / "bin" / "claude"
WS_ROOT = Path("/private/tmp/brief-tests-ws")
SETTINGS = HERE / "subject-settings.json"
SUBJECT_TOOLS = "Read,Write,Edit,Glob,Grep,Skill,Agent,Bash"
FIRST_TURN_SUFFIX = " I keep runs in ./run/ and this run's folder is ./run/job/. I only want the brief, do not start the work."


def base_env():
    env = dict(os.environ)
    for k in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"):
        env.pop(k, None)
    env["HTTPS_PROXY"] = "http://127.0.0.1:8318"
    env["NODE_EXTRA_CA_CERTS"] = str(HOME / ".mitmproxy" / "mitmproxy-ca-cert.pem")
    env["CLAUDE_MITM"] = "1"
    return env


def subject_env(ws):
    env = base_env()
    # Tried CLAUDE_CODE_TMPDIR, CLAUDE_TMPDIR and TMPDIR pointing inside the workspace: the shell's
    # bookkeeping file still goes to the per-user temp folder (see the handback), so they are not set.
    return env


def subject_cmd(prompt, model, session_id, resume):
    cmd = [str(CLAUDE), "-p", prompt,
           "--restricted", "--tools", SUBJECT_TOOLS,
           "--permission-prompts", "none", "--permission-mode", "acceptEdits",
           "--strict-mcp-config",
           "--plugin-dir", str(REPO / "plugins" / "afk"),
           "--settings", str(SETTINGS),
           "--model", model,
           "--output-format", "stream-json", "--verbose"]
    cmd += ["--resume", session_id] if resume else ["--session-id", session_id]
    return cmd


def standin_cmd(prompt, session_id, resume, system_prompt):
    cmd = [str(CLAUDE), "-p", prompt,
           "--restricted", "--tools", "",
           "--permission-prompts", "none",
           "--strict-mcp-config",
           "--model", "sonnet",
           "--output-format", "json",
           "--system-prompt", system_prompt]
    cmd += ["--resume", session_id] if resume else ["--session-id", session_id]
    return cmd


def run_with_timeout(cmd, env, cwd, timeout):
    """Run cmd, stdin /dev/null; kill the whole process group on timeout.
    Returns (stdout, stderr, returncode, timed_out)."""
    with open(os.devnull, "rb") as devnull:
        p = subprocess.Popen(cmd, env=env, cwd=str(cwd), stdin=devnull,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             start_new_session=True, text=True)
        try:
            out, err = p.communicate(timeout=timeout)
            return out, err, p.returncode, False
        except subprocess.TimeoutExpired:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            out, err = p.communicate()
            return out or "", err or "", -9, True


def parse_stream(text):
    recs = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            recs.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return recs


def last_result(recs):
    for r in reversed(recs):
        if r.get("type") == "result":
            return r
    return None


def tool_names(recs):
    top, sub = [], []
    for r in recs:
        if r.get("type") != "assistant":
            continue
        for b in (r.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                (sub if r.get("parent_tool_use_id") else top).append(b.get("name"))
    return {"top_level": top, "subagent": sub}


def add_usage(total, usage):
    for model, d in (usage or {}).items():
        t = total.setdefault(model, {})
        for k, v in d.items():
            if isinstance(v, (int, float)):
                t[k] = t.get(k, 0) + v


DRAFT_RE = re.compile(
    r"(?i)(\bnot\s+(yet\s+)?frozen\b|\bunfrozen\b|\bis\s+(still\s+)?(a\s+)?draft\b|\bstatus\W+draft\b|^\W*draft\b|\bdraft\s+only\b)")


def find_frozen(ws):
    """Return paths of brief.md files under ws/run that count as frozen."""
    frozen = []
    for p in sorted((ws / "run").rglob("brief.md")):
        try:
            lines = p.read_text(errors="replace").splitlines()
        except OSError:
            continue
        heading = next((l for l in lines if l.lstrip().startswith("#")), "")
        if "frozen brief" not in heading.lower():
            continue
        if any(DRAFT_RE.search(l) for l in lines):
            continue
        frozen.append(p)
    return frozen


def search_exists(ws):
    return any((ws / "run").rglob("search.md"))


def build_standin_prompt(card):
    tpl = (HERE / "standin.md").read_text()
    body, _, temps = tpl.partition("=== TEMPERAMENTS ===")
    sections = {}
    parts = re.split(r"^--- (\w+) ---\s*$", temps, flags=re.M)
    for i in range(1, len(parts), 2):
        sections[parts[i]] = parts[i + 1].strip()
    rules = sections[card["temperament"]]
    rules = rules.replace("{{THIN_TOPIC}}", card.get("thin_topic", ""))
    facts = "\n".join("- " + f for f in card["facts"])
    out = (body.strip()
           .replace("{{REQUEST}}", card["request"])
           .replace("{{FACTS}}", facts)
           .replace("{{PLANT_FACT}}", card["plant"]["fact"])
           .replace("{{PLANT_TOKEN}}", card["plant"]["token"])
           .replace("{{TEMPERAMENT_RULES}}", rules))
    assert "{{" not in out, "unfilled placeholder"
    return out


def make_workspace():
    WS_ROOT.mkdir(parents=True, exist_ok=True)
    base = WS_ROOT / secrets.token_hex(4)
    ws = base / "ws"
    ws.mkdir(parents=True)
    return base, ws


def raw_turn(args):
    ws = Path(args.raw_turn).resolve()
    out, err, rc, timed_out = run_with_timeout(
        subject_cmd(args.prompt, args.model, str(uuid.uuid4()), False),
        subject_env(ws), ws, args.turn_timeout)
    sys.stdout.write(out)
    if err.strip():
        sys.stderr.write(err)
    return 124 if timed_out else rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("card", nargs="?")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--out")
    ap.add_argument("--max-turns", type=int, default=20)
    ap.add_argument("--turn-timeout", type=int, default=900)
    ap.add_argument("--raw-turn", help="workspace dir: run one subject turn with the driver's flags and print its stream")
    ap.add_argument("--prompt", help="with --raw-turn")
    args = ap.parse_args()
    if args.raw_turn:
        return raw_turn(args)
    if not args.card or not args.out:
        ap.error("card and --out are required")

    card = json.loads(Path(args.card).read_text())
    out_dir = Path(args.out).resolve()
    (out_dir / "turns").mkdir(parents=True, exist_ok=True)
    base, ws = make_workspace()
    for rel, content in card["files"].items():
        p = ws / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    (ws / "run").mkdir()
    standin_dir = Path(tempfile.mkdtemp(prefix="standin-", dir=str(WS_ROOT)))
    standin_prompt = build_standin_prompt(card)

    subj_id, stand_id = str(uuid.uuid4()), str(uuid.uuid4())
    transcript = []
    per_turn_tools = []
    subj_usage, stand_usage = {}, {}
    subj_cost = stand_cost = 0.0
    outcome, detail = "error", ""
    user_turns = 0
    search_before_freeze = None
    t0 = time.time()
    user_text = "/afk:interview " + card["request"] + FIRST_TURN_SUFFIX
    senv = subject_env(ws)
    benv = base_env()
    frozen_paths = []

    while True:
        user_turns += 1
        transcript.append({"role": "user", "text": user_text})
        search_before = search_exists(ws)
        out, err, rc, timed_out = run_with_timeout(
            subject_cmd(user_text, args.model, subj_id, user_turns > 1), senv, ws, args.turn_timeout)
        (out_dir / "turns" / f"subject-{user_turns}.jsonl").write_text(out)
        if err.strip():
            (out_dir / "turns" / f"subject-{user_turns}.stderr").write_text(err)
        recs = parse_stream(out)
        res = last_result(recs)
        per_turn_tools.append({"turn": user_turns, **tool_names(recs)})
        if res:
            subj_cost += res.get("total_cost_usd") or 0.0
            add_usage(subj_usage, res.get("modelUsage"))
        text = (res or {}).get("result") or ""
        transcript.append({"role": "assistant", "text": text})
        if timed_out:
            outcome, detail = "timeout", f"subject turn {user_turns} exceeded {args.turn_timeout}s"
            break
        if res is None or res.get("is_error"):
            outcome, detail = "error", f"subject turn {user_turns}: rc={rc} result={'none' if res is None else res.get('subtype')} stderr={err.strip()[:300]}"
            break
        frozen_paths = find_frozen(ws)
        if frozen_paths:
            outcome = "frozen"
            search_before_freeze = search_before
            break
        if user_turns >= args.max_turns:
            outcome = "did_not_freeze"
            break
        sprompt = "The interviewer says:\n" + text
        sout, serr, src, stimed = run_with_timeout(
            standin_cmd(sprompt, stand_id, user_turns > 1, standin_prompt), benv, standin_dir, 300)
        (out_dir / "turns" / f"standin-{user_turns}.json").write_text(sout)
        try:
            sres = json.loads(sout)
        except json.JSONDecodeError:
            sres = {}
        stand_cost += sres.get("total_cost_usd") or 0.0
        add_usage(stand_usage, sres.get("modelUsage"))
        user_text = (sres.get("result") or "").strip()
        if stimed or not user_text or sres.get("is_error"):
            outcome, detail = "error", f"stand-in failed after subject turn {user_turns}: rc={src} stderr={serr.strip()[:300]}"
            transcript.append({"role": "user", "text": "(stand-in produced no reply)"})
            break

    wall = round(time.time() - t0, 1)
    (out_dir / "transcript.json").write_text(json.dumps(transcript, indent=2))
    shutil.rmtree(out_dir / "ws", ignore_errors=True)
    shutil.copytree(ws, out_dir / "ws", ignore=shutil.ignore_patterns(".cctmp"), symlinks=True)

    token = card["plant"]["token"].lower()
    brief_text = "\n".join(p.read_text(errors="replace") for p in frozen_paths).lower()
    result = {
        "card": card["name"],
        "model": args.model,
        "outcome": outcome,
        "detail": detail,
        "user_turns_sent": user_turns,
        "wall_seconds": wall,
        "search_md_exists": search_exists(ws),
        "search_md_existed_before_freezing_turn": search_before_freeze,
        "plant_token": card["plant"]["token"],
        "plant_token_in_frozen_brief": (token in brief_text) if frozen_paths else None,
        "frozen_brief_paths": [str(p.relative_to(ws)) for p in frozen_paths],
        "tools_per_subject_turn": per_turn_tools,
        "subject": {"total_cost_usd": round(subj_cost, 4), "modelUsage": subj_usage},
        "standin": {"total_cost_usd": round(stand_cost, 4), "modelUsage": stand_usage},
        "workspace": str(ws),
    }
    (out_dir / "result.json").write_text(json.dumps(result, indent=2))
    shutil.rmtree(standin_dir, ignore_errors=True)
    print(json.dumps({k: result[k] for k in ("card", "model", "outcome", "detail", "user_turns_sent", "wall_seconds",
                                              "plant_token_in_frozen_brief")}))
    return 0 if outcome == "frozen" else 1


if __name__ == "__main__":
    sys.exit(main())
