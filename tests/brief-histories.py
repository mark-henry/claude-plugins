#!/usr/bin/env python3
"""Rebuild each brief case's history.jsonl from its hand-written history.src.jsonl.

A replayed conversation only tests the skill if the skill's text is in it, the way it is
after a real `/afk:interview`. This script inserts, after the first user record of every
`tests/brief-*/history.src.jsonl`, the records a skill load leaves behind, using the
CURRENT text of plugins/afk/skills/interview/SKILL.md. Run it after every edit to that skill:

    python3 tests/brief-histories.py          # rewrite every history.jsonl
    python3 tests/brief-histories.py --check  # exit 1 if any history.jsonl is stale
"""
import glob, json, os, re, sys, uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "plugins", "afk", "skills", "interview", "SKILL.md")


def skill_body():
    text = open(SKILL).read()
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S).lstrip("\n")
    text = text.replace("${CLAUDE_PLUGIN_DATA}", "/plugin-data/afk")
    return "Base directory for this skill: /plugins/afk/skills/interview\n\n" + text


def build(src_path):
    recs = [json.loads(l) for l in open(src_path) if l.strip()]
    first, rest = recs[0], recs[1:]
    assert first["type"] == "user", src_path
    base = {k: first[k] for k in ("sessionId", "cwd", "userType", "version", "timestamp") if k in first}
    ns = uuid.UUID(first["uuid"])
    ids = [str(uuid.uuid5(ns, n)) for n in ("call", "result", "body")]
    call = dict(base, type="assistant", isSidechain=False, parentUuid=first["uuid"], uuid=ids[0], message={
        "id": "msg_skill_load", "type": "message", "role": "assistant", "model": "claude-sonnet-4-5",
        "content": [{"type": "tool_use", "id": "toolu_skill_load", "name": "Skill", "input": {"skill": "afk:interview"}}],
        "stop_reason": "tool_use", "usage": {"input_tokens": 0, "output_tokens": 0}})
    result = dict(base, type="user", isSidechain=False, parentUuid=ids[0], uuid=ids[1], message={
        "role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_skill_load", "content": "Launching skill: afk:interview"}]})
    body = dict(base, type="user", isSidechain=False, isMeta=True, parentUuid=ids[1], uuid=ids[2], message={
        "role": "user", "content": [{"type": "text", "text": skill_body()}]})
    if rest:
        rest[0] = dict(rest[0], parentUuid=ids[2])
    return "".join(json.dumps(r) + "\n" for r in [first, call, result, body] + rest)


def main():
    check = "--check" in sys.argv
    stale = []
    for src in sorted(glob.glob(os.path.join(ROOT, "tests", "brief-*", "history.src.jsonl"))):
        out = os.path.join(os.path.dirname(src), "history.jsonl")
        want = build(src)
        have = open(out).read() if os.path.exists(out) else None
        if have != want:
            stale.append(os.path.relpath(out, ROOT))
            if not check:
                open(out, "w").write(want)
    if check and stale:
        print("stale, rerun tests/brief-histories.py:\n  " + "\n  ".join(stale))
        sys.exit(1)
    print(("checked" if check else "wrote") + f": {len(stale)} changed")


if __name__ == "__main__":
    main()
