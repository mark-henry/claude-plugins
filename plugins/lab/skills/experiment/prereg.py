#!/usr/bin/env python3
"""Preregister a comparison, check its arms are fair, and score it against what was predicted.

  prereg.py new   PATH                write a template record to fill in
  prereg.py open  PATH                validate, freeze predictions, stamp commit + uncommitted diff
  prereg.py stamp OUT_DIR             write git.json (+ code.diff) into a run folder; for harnesses with no stamp
  prereg.py parity PATH               do the arms differ only in `varies`? same instances, same code?
  prereg.py close PATH [--note TEXT]  predicted vs observed per arm x metric, status -> closed (apply the bar yourself)
  prereg.py ls [DIR]                  open records, and how well past predictions landed

Stdlib only. A record is JSON; see `new` for the fields. Exit code 1 on a refusal or a parity failure.
The tool of the lab:experiment skill: its SKILL.md ("The record and its tool") says when each command runs,
and its checks.md what each does and does not show.
"""
from __future__ import annotations

import argparse, datetime, hashlib, json, os, socket, subprocess, sys
from pathlib import Path

IGNORED_ARGS = {"out", "max_usd", "dry_run", "max_connections"}
STATUSES = {"draft", "open", "closed", "abandoned", "exploratory"}

TEMPLATE = {
    "question": "One sentence: what this comparison decides.",
    "bar": "plan.md#BAR_NAME, or 'none, exploratory'",
    "decision": "What we do if the bar passes, and if it fails.",
    "varies": ["model", "base_model"],
    "arms": {"untreated": {"out": "logs/.../untreated", "command": "..."},
             "treated": {"out": "logs/.../treated", "command": "..."}},
    "metrics": {"solves": {"num": "targets.count_exact_among_attempts.numerator", "den": "samples.real"}},
    "predictions": {"untreated": {"solves": [0.6, 0.8]}, "treated": {"solves": [0.5, 0.75]}},
    "mechanism": "Why you expect that: a point estimate, where the gain should concentrate, where the control should tie.",
    "surprises": ["A named result that would surprise you."],
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
    # sh() strips the output, so the first line may have lost its leading status space: split, don't slice
    dirty = [l.split(maxsplit=1)[1] for l in (sh("git", "status", "--porcelain", "--untracked-files=no", cwd=cwd) or "").splitlines() if len(l.split(maxsplit=1)) == 2]
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


FROZEN = ("question", "bar", "decision", "varies", "watched", "arms", "metrics", "predictions", "mechanism", "surprises")


def frozen_part(rec):
    keep = {k: rec[k] for k in FROZEN if k in rec}
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
    # the untouched template is not a record: refuse the fields it wrote, by name
    for f in ("question", "bar"):
        if rec.get(f) == TEMPLATE[f]:
            die(f"{f} is still the template's placeholder; write the real one")
    for arm, spec in (rec.get("arms") or {}).items():
        if isinstance(spec, dict) and spec.get("command") == "...":
            die(f"arm {arm}: command is still the template's placeholder; write the real launch command")
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
    print(f"opened {a.path} at {(state.get('commit') or '?')[:8]}{' (dirty)' if diff else ''}; "
          + ("exploratory: its numbers cannot pass or fail a bar or pick an arm." if exploratory else
             "pin the record (commit it, or have a script log its hash) before a treated arm produces output "
             "on the items the counted run scores."))


def cmd_stamp(a):
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    state, diff = git_state()
    if diff:
        (out / "code.diff").write_text(diff)
    (out / "git.json").write_text(json.dumps({"utc": now(), "host": socket.gethostname(), "argv": a.argv, **state}, indent=2))
    print(f"stamped {out} at {(state.get('commit') or '?')[:8]}{' (dirty)' if diff else ''}")


def args_from_argv(argv):
    """Launch args recovered from a stamped command line: --key value, --key=value, --flag; the rest are positional."""
    args, pos, i = {}, [], 0
    while i < len(argv):
        tok = argv[i]
        if tok.startswith("--") and len(tok) > 2:
            key, eq, val = tok[2:].partition("=")
            if not eq and i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                val, i = argv[i + 1], i + 1
            args[key.replace("-", "_")] = val if (eq or val) else True
        else:
            pos.append(tok)
        i += 1
    if pos:
        args["_positional"] = pos
    return args


def plain(v):
    """A launch arg as text, so a typed launch.json value and a stamped command-line string compare by value."""
    return v if v is None or isinstance(v, (dict, list)) else str(v)


def run_provenance(out):
    """What a run folder says about the code and data it ran on."""
    out = Path(out)
    launch = load(out / "launch.json") if (out / "launch.json").exists() else {}
    git = launch.get("git") or (load(out / "git.json") if (out / "git.json").exists() else {})
    files = {f.name: sha(f) for f in sorted(out.glob("*.jsonl")) if f.name in ("real.jsonl", "zero.jsonl", "instances.jsonl")}
    mtime = (out / "launch.json").stat().st_mtime if (out / "launch.json").exists() else None
    args = launch.get("args") or args_from_argv([a for a in git.get("argv") or [] if a != "--"])
    return args, git, files, mtime


def cmd_parity(a):
    rec = load(a.path)
    root = Path(sh("git", "rev-parse", "--show-toplevel", cwd=Path(a.path).parent) or ".")
    varies = set(rec.get("varies", [])) | IGNORED_ARGS
    # paths whose code can change a number: the record's, else the repo's prereg/config.json, else the whole repo
    cfg = root / "prereg" / "config.json"
    watched = rec.get("watched") or (load(cfg).get("watched") if cfg.exists() else None) or ["."]
    arms = {k: run_provenance(root / v["out"]) for k, v in rec["arms"].items()}
    problems, notes, warns = [], [], []
    names = list(arms)
    ref = names[0]
    for other in names[1:]:
        a0, a1 = arms[ref][0], arms[other][0]
        no_args = [n for n, args in ((ref, a0), (other, a1)) if not args]
        if no_args:
            problems.append(f"no launch args recorded for {', '.join(no_args)} (no launch.json args, no stamped command): "
                            f"nothing shows the arms differ only in `varies`; diff their commands by hand")
        for key in sorted(set(a0) | set(a1)):
            if key not in varies and plain(a0.get(key)) != plain(a1.get(key)):
                problems.append(f"arg {key}: {ref}={a0.get(key)!r} {other}={a1.get(key)!r}")
        f0, f1 = arms[ref][2], arms[other][2]
        if not set(f0) & set(f1):
            warns.append(f"no instance files found in both {ref} and {other} (real.jsonl, zero.jsonl, instances.jsonl): item parity not checked")
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
        else:
            for w in watched:
                if w != "." and not any(sh("git", "rev-parse", "--verify", "--quiet", f"{c}:{w}", cwd=root) for c in (c0, c1)):
                    problems.append(f"watched path {w!r} exists at neither {c0[:8]} nor {c1[:8]}: nothing was checked there")
            if c0 != c1:
                changed = sh("git", "diff", "--stat", f"{c0}..{c1}", "--", *watched, cwd=root)
                if changed is None:
                    problems.append(f"could not compare watched code between {c0[:8]} and {c1[:8]} (git diff failed; are both commits in this repo?)")
                else:
                    hint = " (whole repo watched; name the code paths in the record's `watched` or in prereg/config.json)" if watched == ["."] else ""
                    (problems if changed else notes).append(
                        f"commits differ {c0[:8]} vs {c1[:8]}" + (f"; watched code changed{hint}:\n{changed}" if changed else "; no watched code changed"))
        for n, c in ((ref, arms[ref][1]), (other, arms[other][1])):
            if c.get("dirty"):
                problems.append(f"{n} ran on a dirty tree ({len(c['dirty'])} files); compare its code.diff")
        t0, t1 = arms[ref][3], arms[other][3]
        if t0 and t1 and abs(t0 - t1) > 86400:
            notes.append(f"launches {abs(t0 - t1) / 3600:.0f} h apart ({ref}/{other})")
    for n in notes:
        print(f"  ok    {n}")
    for w in warns:
        print(f"  warn  {w}")
    for p in problems:
        print(f"  FAIL  {p}")
    print("parity: " + ("PASS" if not problems else f"FAIL ({len(problems)})"))
    sys.exit(1 if problems else 0)


def cmd_close(a):
    rec = load(a.path)
    if not rec.get("opened"):
        die("never opened: these numbers have no prediction to be scored against. Report them as exploratory")
    if frozen_part(rec) != rec["opened"]["frozen_sha256"]:
        die(f"a frozen field ({', '.join(FROZEN[:-1])} or {FROZEN[-1]}) changed after open; restore it or write a new record")
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
