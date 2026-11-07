#!/usr/bin/env python3
"""Preregister a comparison, check its arms are fair, and score it against what was predicted.

  prereg.py new   PATH                write a template record to fill in
  prereg.py open  PATH                validate, freeze predictions, stamp commit + uncommitted diff
  prereg.py stamp OUT_DIR             write git.json (+ code.diff) into a run folder; for harnesses with no stamp
  prereg.py parity PATH               do the arms differ only in `varies`? same instances, same code?
  prereg.py close PATH [--note TEXT]  predicted vs observed per arm x metric, bar verdict, status -> closed
  prereg.py ls [DIR]                  open records, and how well past predictions landed

Stdlib only. A record is JSON; see `new` for the fields. Exit code 1 on a refusal or a parity failure.
"""
from __future__ import annotations

import argparse, datetime, hashlib, json, os, socket, subprocess, sys
from pathlib import Path

WATCHED = ["concealment_tasks", "prompts", "rs", "configs", "scripts", "inspect_tasks"]  # code that can change a number
IGNORED_ARGS = {"out", "max_usd", "dry_run", "max_connections"}
STATUSES = {"draft", "open", "closed", "abandoned", "exploratory"}

TEMPLATE = {
    "question": "One sentence: what this comparison decides.",
    "bar": "DESIGN.md#SFT-PARITY, or 'none, exploratory'",
    "decision": "What we do if the bar passes, and if it fails.",
    "varies": ["model", "base_model"],
    "arms": {"untreated": {"out": "logs/.../untreated", "command": "..."},
             "treated": {"out": "logs/.../treated", "command": "..."}},
    "metrics": {"solves": {"num": "targets.count_exact_among_attempts.numerator", "den": "samples.real"}},
    "predictions": {"untreated": {"solves": [0.6, 0.8]}, "treated": {"solves": [0.5, 0.75]}},
    "max_usd": 2.0,
    "status": "draft",
}


def sh(*cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def git_state(cwd="."):
    """Commit, dirty paths, and the uncommitted diff (tracked files) at this moment."""
    commit = sh("git", "rev-parse", "HEAD", cwd=cwd)
    if commit is None:
        return {"commit": None}, ""
    diff = sh("git", "diff", "HEAD", cwd=cwd) or ""
    dirty = [l[3:] for l in (sh("git", "status", "--porcelain", "--untracked-files=no", cwd=cwd) or "").splitlines()]
    return {"commit": commit, "branch": sh("git", "rev-parse", "--abbrev-ref", "HEAD", cwd=cwd), "dirty": dirty,
            "diff_sha256": hashlib.sha256(diff.encode()).hexdigest()[:16] if diff else None}, diff


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%MZ")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def frozen_part(rec):
    keep = {k: rec[k] for k in ("question", "bar", "decision", "varies", "arms", "metrics", "predictions") if k in rec}
    return hashlib.sha256(json.dumps(keep, sort_keys=True).encode()).hexdigest()[:16]


def load(path):
    return json.loads(Path(path).read_text())


def save(path, rec):
    Path(path).write_text(json.dumps(rec, indent=2) + "\n")


def dig(d, dotted):
    if isinstance(dotted, (int, float)):
        return dotted
    for part in dotted.split("."):
        if not isinstance(d, dict) or part not in d:
            return None
        d = d[part]
    return d


def die(msg):
    print(f"refused: {msg}", file=sys.stderr)
    sys.exit(1)


def cmd_new(a):
    p = Path(a.path)
    if p.exists():
        die(f"{p} exists")
    p.parent.mkdir(parents=True, exist_ok=True)
    save(p, TEMPLATE)
    print(f"wrote {p}; fill it in, then `prereg.py open {p}`")


def cmd_open(a):
    rec = load(a.path)
    if rec.get("opened"):
        die(f"already opened {rec['opened']['utc']}; predictions are frozen. Write a new record with \"parent\": \"{a.path}\"")
    exploratory = rec.get("status") == "exploratory" or str(rec.get("bar", "")).startswith("none")
    for f in ("question", "arms", "metrics", "max_usd"):
        if not rec.get(f):
            die(f"missing {f}")
    for m, spec in rec["metrics"].items():
        if not isinstance(spec, dict) or "num" not in spec or "den" not in spec:
            die(f"metric {m} needs num and den (a report path or a number); the denominator is chosen now, not after")
    if not exploratory:
        if not rec.get("bar") or not rec.get("decision"):
            die("a non-exploratory record needs bar and decision")
        for arm in rec["arms"]:
            for m in rec["metrics"]:
                iv = rec.get("predictions", {}).get(arm, {}).get(m)
                if not (isinstance(iv, list) and len(iv) == 2 and all(isinstance(x, (int, float)) for x in iv) and iv[0] <= iv[1]):
                    die(f"prediction for {arm} x {m} must be [low, high] as a rate; or mark the record exploratory")
    for arm, spec in rec["arms"].items():
        if "reused" in spec and not spec["reused"].get("reason"):
            die(f"arm {arm} reuses a run; say why in reused.reason")
    state, diff = git_state(Path(a.path).parent)
    if diff:
        dp = Path(a.path).with_suffix(".diff")
        dp.write_text(diff)
        state["diff_file"] = dp.name
    rec["opened"] = {"utc": now(), "host": socket.gethostname(), "frozen_sha256": frozen_part(rec), **state}
    rec["status"] = "exploratory" if exploratory else "open"
    save(a.path, rec)
    print(f"opened {a.path} at {(state.get('commit') or '?')[:8]}{' (dirty)' if diff else ''}; launch now. "
          f"Commit the record before launch if it gates a DESIGN.md row or the run costs over $10.")


def cmd_stamp(a):
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    state, diff = git_state()
    if diff:
        (out / "code.diff").write_text(diff)
    (out / "git.json").write_text(json.dumps({"utc": now(), "host": socket.gethostname(), "argv": a.argv, **state}, indent=2))
    print(f"stamped {out} at {(state.get('commit') or '?')[:8]}{' (dirty)' if diff else ''}")


def run_provenance(out):
    """What a run folder says about the code and data it ran on."""
    out = Path(out)
    launch = load(out / "launch.json") if (out / "launch.json").exists() else {}
    git = launch.get("git") or (load(out / "git.json") if (out / "git.json").exists() else {})
    files = {f.name: sha(f) for f in sorted(out.glob("*.jsonl")) if f.name in ("real.jsonl", "zero.jsonl", "instances.jsonl")}
    mtime = (out / "launch.json").stat().st_mtime if (out / "launch.json").exists() else None
    return launch.get("args", {}), git, files, mtime


def cmd_parity(a):
    rec = load(a.path)
    root = Path(sh("git", "rev-parse", "--show-toplevel", cwd=Path(a.path).parent) or ".")
    varies = set(rec.get("varies", [])) | IGNORED_ARGS
    arms = {k: run_provenance(root / v["out"]) for k, v in rec["arms"].items()}
    problems, notes = [], []
    names = list(arms)
    ref = names[0]
    for other in names[1:]:
        a0, a1 = arms[ref][0], arms[other][0]
        for key in sorted(set(a0) | set(a1)):
            if key not in varies and a0.get(key) != a1.get(key):
                problems.append(f"arg {key}: {ref}={a0.get(key)!r} {other}={a1.get(key)!r}")
        f0, f1 = arms[ref][2], arms[other][2]
        for name in sorted(set(f0) & set(f1)):
            (notes if f0[name] == f1[name] else problems).append(
                f"{name} {'identical' if f0[name] == f1[name] else 'DIFFERS'} across {ref}/{other}")
        c0, c1 = arms[ref][1].get("commit"), arms[other][1].get("commit")
        if not c0 or not c1:
            missing = [n for n, c in ((ref, c0), (other, c1)) if not c]
            reused = [n for n in missing if "reused" in rec["arms"][n]]
            c_claim = {n: rec["arms"][n].get("reused", {}).get("commit") for n in reused}
            if any(not c or c == "unrecoverable" for c in c_claim.values()) or len(reused) < len(missing):
                problems.append(f"no recorded commit for {', '.join(missing)}: code parity unverifiable")
        elif c0 != c1:
            changed = sh("git", "diff", "--stat", f"{c0}..{c1}", "--", *WATCHED, cwd=root)
            (problems if changed else notes).append(
                f"commits differ {c0[:8]} vs {c1[:8]}" + (f"; watched code changed:\n{changed}" if changed else "; no watched code changed"))
        for n, c in ((ref, arms[ref][1]), (other, arms[other][1])):
            if c.get("dirty"):
                problems.append(f"{n} ran on a dirty tree ({len(c['dirty'])} files); compare its code.diff")
        t0, t1 = arms[ref][3], arms[other][3]
        if t0 and t1 and abs(t0 - t1) > 86400:
            notes.append(f"launches {abs(t0 - t1) / 3600:.0f} h apart ({ref}/{other})")
    for n in notes:
        print(f"  ok    {n}")
    for p in problems:
        print(f"  FAIL  {p}")
    print("parity: " + ("PASS" if not problems else f"FAIL ({len(problems)})"))
    sys.exit(1 if problems else 0)


def cmd_close(a):
    rec = load(a.path)
    if not rec.get("opened"):
        die("never opened: these numbers have no prediction to be scored against. Report them as exploratory")
    if frozen_part(rec) != rec["opened"]["frozen_sha256"]:
        die("question/arms/metrics/predictions changed after open; restore them or write a new record")
    root = Path(sh("git", "rev-parse", "--show-toplevel", cwd=Path(a.path).parent) or ".")
    observed, rows, hits, total = {}, [], 0, 0
    for arm, spec in rec["arms"].items():
        rp = root / spec["out"] / "report.json"
        if not rp.exists():
            die(f"{rp} missing")
        report = load(rp)
        for m, ms in rec["metrics"].items():
            num, den = dig(report, ms["num"]), dig(report, ms["den"])
            if num is None or not den:
                die(f"{arm}: cannot resolve {ms['num']} / {ms['den']} in {rp}")
            v = num / den
            observed.setdefault(arm, {})[m] = {"num": num, "den": den, "rate": round(v, 4)}
            iv = rec.get("predictions", {}).get(arm, {}).get(m)
            hit = None if not iv else iv[0] <= v <= iv[1]
            if hit is not None:
                hits += hit
                total += 1
            rows.append(f"  {arm:<12} {m:<14} {num}/{den} = {v:.3f}   predicted {iv or '-'}   {'' if hit is None else ('hit' if hit else 'MISS')}")
    print("\n".join(rows))
    rec["observed"] = observed
    rec["closed"] = {"utc": now(), "hits": hits, "predictions": total, "note": a.note or ""}
    if rec["status"] != "exploratory":
        rec["status"] = "closed"
    save(a.path, rec)
    print(f"{hits}/{total} predictions hit. Bar: apply {rec.get('bar')} to the declared denominators above; "
          f"any other denominator you quote is post hoc and must say so.")


def cmd_ls(a):
    recs = sorted(Path(a.dir).glob("*.json"))
    hits = total = 0
    width = []
    for p in recs:
        try:
            r = load(p)
        except Exception:
            continue
        if "question" not in r:
            continue
        print(f"  {r.get('status', '?'):<11} {p.name}  {r['question'][:70]}")
        if r.get("closed"):
            hits += r["closed"]["hits"]
            total += r["closed"]["predictions"]
            width += [iv[1] - iv[0] for arm in r.get("predictions", {}).values() for iv in arm.values()]
    if total:
        print(f"calibration: {hits}/{total} intervals hit, mean width {sum(width) / len(width):.2f}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("new", "open", "parity"):
        sub.add_parser(name).add_argument("path")
    s = sub.add_parser("stamp")
    s.add_argument("out_dir")
    s.add_argument("argv", nargs=argparse.REMAINDER, help="the launch command, after --")
    c = sub.add_parser("close")
    c.add_argument("path")
    c.add_argument("--note")
    l = sub.add_parser("ls")
    l.add_argument("dir", nargs="?", default="prereg")
    a = ap.parse_args(argv)
    {"new": cmd_new, "open": cmd_open, "stamp": cmd_stamp, "parity": cmd_parity, "close": cmd_close, "ls": cmd_ls}[a.cmd](a)


if __name__ == "__main__":
    main()
