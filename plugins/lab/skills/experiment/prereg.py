#!/usr/bin/env python3
"""Preregister an experiment, stamp each run, and check it against the standard lines of lab:experiment.

  prereg.py new    PATH                          write a template record (schema 2) to fill in
  prereg.py open   PATH                          validate; hash the frozen fields and the line-6 fields; hash arm data
  prereg.py stamp  OUT [options] -- CMD...       snapshot the tree under refs/lab/<run id>, write OUT/stamp.json
  prereg.py check  PATH | RUN_DIR...             lines 2, 3, 7, 8, 12 and the counted gate, from items.jsonl
  prereg.py parity PATH                          the arm comparison: arms differ only in `varies` (line 13)
  prereg.py ledger PATH RUN_DIR                  append one line each time the test split is scored (line 9)
  prereg.py quote  REPORT PATH|RUN_DIR...        every rate or a/b in REPORT carries a run id (line 10)
  prereg.py induct PATH                          vet an old record after the fact; never refuses, never edits it
  prereg.py close  PATH [--note TEXT]            observed per arm, status -> closed
  prereg.py ls     [DIR]                         records, and how well past predictions landed

Stdlib only; never contacts a tracker (its run id is a string). Exit 1 on a refusal, with one line per thing to
fix, naming the line of the skill it enforces. Records without "schema" (made before schema 2) are read as before
by close, ls and parity, and hashed exactly as before. The skill's SKILL.md says when each command runs.

A run folder holds stamp.json (written by `stamp` at launch) and items.jsonl (written by the harness): one JSON
object per line with id, arm, unit, score (number or null) and status (ok, error, empty, truncated, parse_failure).
Arms named floor:<name> are trivial policies scored on the same items (line 12).
"""
from __future__ import annotations

import argparse, collections, datetime, hashlib, json, os, random, re, shlex, socket, statistics, subprocess, sys, tempfile
from pathlib import Path

IGNORED_ARGS = {"out", "max_usd", "dry_run", "max_connections"}
STATUSES = {"draft", "open", "closed", "abandoned", "exploratory"}

TEMPLATE = {
    "schema": 2,
    "question": "One sentence: what this comparison decides.",
    "bar": "plan.md#BAR_NAME, or 'none, exploratory'",
    "decision": "What we do if the bar passes, and if it fails.",
    "primary": {"metric": "... line 6: the one primary metric",
                "comparison": "... line 6: which arm minus which",
                "smallest_effect": "... line 6: a number, the smallest difference that would change the decision",
                "unit": "... line 5: the independent unit (document, task, user), as written in items.jsonl",
                "higher_is_better": True},
    "intended_n": "... line 2: items per arm",
    "failure_threshold": {"share": 0.05, "min_items": 2, "difference": 0.05},
    "varies": ["model"],
    "watched": ["."],
    "arms": {"untreated": {"out": "runs/untreated", "command": "...", "data": []},
             "treated": {"out": "runs/treated", "command": "...", "data": []}},
    "pilot": {"runs": [], "pass_at": 0.5},
    "scorer": {"command": "... line 3: e.g. python3 score.py {output}", "file": "...", "broken": "...", "good": "..."},
    "floors": {"runs": [], "none_reason": ""},
    "resample_seed": 20261115,
    "status": "draft",
}


def sh(*cmd, cwd=None):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    except OSError:      # git not installed, or cwd missing: the same as a failed call
        return None
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


FROZEN2 = FROZEN + ("schema", "primary", "intended_n", "failure_threshold", "pilot", "scorer", "floors", "resample_seed",
                    "units_differ_reason")


def frozen_part(rec):
    """Hash of the fields frozen at open. Schema-less records hash exactly the keys they always did."""
    keep = {k: rec[k] for k in (FROZEN2 if rec.get("schema") == 2 else FROZEN) if k in rec}
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


def open_v1(a, rec):
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
    git = launch.get("git") or (load(out / "git.json") if (out / "git.json").exists() else
                                (load(out / "stamp.json") if (out / "stamp.json").exists() else {}))
    if not git.get("commit") and (out / "stamp.json").exists():
        # a schema-2 stamp keeps the commit it ran on in snapshot.head (HEAD at launch, as git.json's commit was) and
        # its uncommitted tracked files in snapshot.dirty; its command line is at the top level
        st = load(out / "stamp.json")
        snap = st.get("snapshot") if isinstance(st.get("snapshot"), dict) else {}
        head = snap.get("head")
        git = {**git, "commit": head if head and head != NA else None, "dirty": snap.get("dirty") or [],
               "argv": git.get("argv") or st.get("argv")}
    files = {f.name: sha(f) for f in sorted(out.glob("*.jsonl")) if f.name in ("real.jsonl", "zero.jsonl", "instances.jsonl")}
    mtime = (out / "launch.json").stat().st_mtime if (out / "launch.json").exists() else None
    args = launch.get("args") or args_from_argv([a for a in git.get("argv") or [] if a != "--"])
    return args, git, files, mtime


def parity_v1(a, rec):
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


def close_v1(a, rec):
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


# ---------------------------------------------------------------------------------------------------------------
# Schema 2: the standard checks. Old records (no "schema") take the *_v1 paths above, unchanged.

ITEM_STATUSES = ("ok", "error", "empty", "truncated", "parse_failure")
LARGE_BYTES = 5 * 1024 * 1024      # a file over this is listed in the snapshot by sha256, not stored
RESAMPLES = 2000
DETECT_Z = 2.8                     # two-sided alpha 0.05, power 0.8
LINE8_SHOWN = 10                   # per-item pass rates printed; check.json holds them all
LINE6 = ("metric", "comparison", "smallest_effect", "unit")
NA = "n/a"


def full_sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def placeholder(v):
    return v is None or v == "" or (isinstance(v, str) and v.startswith("..."))


def line6_missing(rec):
    p = rec.get("primary") or {}
    miss = [f for f in LINE6 if placeholder(p.get(f))]
    se = p.get("smallest_effect")
    if "smallest_effect" not in miss and not (isinstance(se, (int, float)) and not isinstance(se, bool) and se > 0):
        miss.append("smallest_effect")
    return miss


def line6_part(rec):
    if line6_missing(rec):
        return None
    p = rec["primary"]
    return hashlib.sha256(json.dumps({k: p[k] for k in LINE6}, sort_keys=True).encode()).hexdigest()[:16]


def repo_root(cwd="."):
    r = sh("git", "rev-parse", "--show-toplevel", cwd=cwd)
    return Path(r) if r else None


def rec_root(path):
    return repo_root(Path(path).resolve().parent) or Path(".")


def data_facts(path):
    b = Path(path).read_bytes()
    return {"sha256": hashlib.sha256(b).hexdigest(), "lines": b.count(b"\n") + (1 if b and not b.endswith(b"\n") else 0), "bytes": len(b)}


def check_data(entries, root, arm):
    """Line 13: recompute each declared data file; refuse a mismatch with what the record holds. Returns filled entries."""
    out = []
    if not isinstance(entries, (list, type(None))):
        die(f"line 13: arm {arm}: data must be a list of file paths or {{\"path\": ...}} objects")
    for e in entries or []:
        if isinstance(e, str):      # a bare path is the same as {"path": path}
            e = {"path": e}
        if not isinstance(e, dict) or not isinstance(e.get("path"), str):
            die(f"line 13: arm {arm}: data entry {e!r} is neither a file path nor an object with a \"path\"")
        p = root / e["path"]
        if not p.is_file():
            die(f"line 13: arm {arm}: data file {e['path']} is missing")
        facts = data_facts(p)
        for k in ("sha256", "lines", "bytes"):
            if k in e and e[k] != facts[k]:
                die(f"line 13: arm {arm}: {e['path']} {k} is {facts[k]}, the record says {e[k]}; restore the file or write a new record")
        out.append({**e, **facts})
    return out


def scorer_declared(rec):
    sc = rec.get("scorer")
    return isinstance(sc, dict) and not any(placeholder(sc.get(k)) for k in ("command", "file", "broken", "good"))


def run_scorer(sc, root):
    """Line 3: the scorer must fail the broken output and pass the known-good one. Returns (result, problems)."""
    probs, res = [], {}
    def passes(f):
        cmd = sc["command"]
        cmd = cmd.replace("{output}", shlex.quote(f)) if "{output}" in cmd else f"{cmd} {shlex.quote(f)}"
        return subprocess.run(cmd, shell=True, cwd=root, capture_output=True, timeout=600).returncode == 0
    for k in ("file", "broken", "good"):
        if not (root / sc[k]).is_file():
            probs.append(f"line 3: scorer {k} {sc[k]} is missing")
    if probs:
        return {"error": probs}, probs
    res["scorer_sha256"] = full_sha(root / sc["file"])
    res["broken_passed"], res["good_passed"] = passes(sc["broken"]), passes(sc["good"])
    if res["broken_passed"]:
        probs.append(f"line 3: the scorer passed the broken output {sc['broken']}; it cannot tell a broken output from a good one")
    if not res["good_passed"]:
        probs.append(f"line 3: the scorer failed the known-good output {sc['good']}")
    return res, probs


def read_items(folder, probs):
    p = Path(folder) / "items.jsonl"
    if not p.is_file():
        probs.append(f"{p}: missing; the harness writes one row per item (id, arm, unit, score, status)")
        return []
    out = []
    for k, line in enumerate(p.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            probs.append(f"line 2: {p}:{k} is not JSON"); continue
        miss = [f for f in ("id", "arm", "unit", "score", "status") if f not in r]
        if miss:
            probs.append(f"line 2: {p}:{k} lacks {', '.join(miss)}"); continue
        if r["status"] not in ITEM_STATUSES:
            probs.append(f"line 2: {p}:{k} status {r['status']!r} is not one of {', '.join(ITEM_STATUSES)}"); continue
        if r["status"] == "ok" and not (isinstance(r["score"], (int, float)) and not isinstance(r["score"], bool)):
            probs.append(f"line 2: {p}:{k} has status ok but score {r['score']!r}; an ok row carries a number"); continue
        out.append(r)
    return out


def mean_ok(rows):
    xs = [r["score"] for r in rows if r["status"] == "ok"]
    return sum(xs) / len(xs) if xs else None


def fmt(x):
    return "-" if x is None else f"{x:.3f}"


def pilot_folders(rec, root):
    """The record's pilot run folders, each once: a folder named twice (however spelled) is one run."""
    out, seen = [], set()
    for run in (rec.get("pilot") or {}).get("runs") or []:
        key = (root / run).resolve()
        if key not in seen:
            seen.add(key)
            out.append(run)
    return out


def pilot_rows(rec, root, probs):
    return [[r for r in read_items(root / run, probs) if not str(r["arm"]).startswith("floor:")]
            for run in pilot_folders(rec, root)]


def pilot_gate(rec, root):
    """Counted needs two distinct baseline pilot runs, each stamped, with different run ids."""
    named = (rec.get("pilot") or {}).get("runs") or []
    folders = pilot_folders(rec, root)
    probs = []
    if len(folders) < len(named):
        probs.append(f"line 7: pilot.runs names the same folder more than once ({', '.join(named)}); a folder is one pilot run")
    ids = {}
    for f in folders:
        st = load_stamp(root / f)
        if st is None:
            probs.append(f"line 7: pilot run {f} has no stamp.json; stamp each pilot run at launch")
        else:
            ids.setdefault(st.get("run_id"), []).append(f)
    for rid, fs in ids.items():
        if len(fs) > 1:
            probs.append(f"line 7: pilot runs {', '.join(fs)} share run id {rid}; two pilot runs are two launches")
    if len(ids) < 2:
        probs.append(f"line 7: counted needs two distinct stamped baseline pilot runs with different run ids; found {len(ids)}")
    return probs


def declared_deterministic(rec):
    """pilot.deterministic: the reason the harness gives the same score on a rerun, or None when not declared."""
    v = (rec.get("pilot") or {}).get("deterministic")
    return v.strip() if isinstance(v, str) and v.strip() else None


def few(xs, k=3):
    return ", ".join(map(str, sorted(xs, key=str)[:k])) + (" ..." if len(xs) > k else "")


def line7(rec, runs, arm_units=None, first_arm=None):
    """SE of the mean paired difference between the first two baseline pilot runs, resampling units. None if < 2 runs.
    Its "problems" make it degenerate: identical scores on every shared item (a copied file, unless pilot.deterministic
    is declared), fewer than two units, or pilots that do not cover the first arm's units (arm_units, at check) or
    intended_n items (at stamp, before any arm has items)."""
    if len(runs) < 2:
        return None
    a = {r["id"]: r for r in runs[0] if r["status"] == "ok"}
    b = {r["id"]: r for r in runs[1] if r["status"] == "ok"}
    by_unit = {}
    shared = sorted(set(a) & set(b), key=str)
    for i in shared:
        by_unit.setdefault(a[i]["unit"], []).append(a[i]["score"] - b[i]["score"])
    units = sorted(by_unit, key=str)
    if not units:
        return None
    rng = random.Random(rec.get("resample_seed", 0))
    means = []
    for _ in range(RESAMPLES):
        ds = [x for u in [rng.choice(units) for _ in units] for x in by_unit[u]]
        means.append(sum(ds) / len(ds))
    se = statistics.stdev(means)
    det, probs = declared_deterministic(rec), []
    differ = sum(1 for i in shared if a[i]["score"] != b[i]["score"])
    if det and differ:
        probs.append(f"pilot.deterministic is declared, but the two pilot runs differ on {differ} items")
    elif not det and not differ:
        probs.append("the two pilot runs give identical scores on every shared item: a copied run is not a second run "
                     "(if the harness is deterministic, declare pilot.deterministic with the reason)")
    if len(units) < 2:
        probs.append(f"the pilot runs share ok items in {len(units)} unit; the SE needs at least two")
    for k, rows in enumerate(runs[:2], 1):
        if arm_units is not None:
            pu = {str(r["unit"]) for r in rows}
            if pu != arm_units:
                probs.append(f"pilot run {k} covers {len(pu)} units, arm {first_arm} {len(arm_units)}; the pilots cover "
                             f"the arms' units (missing: {few(arm_units - pu) or 'none'}; extra: {few(pu - arm_units) or 'none'})")
        elif real_n(rec.get("intended_n")) and len({r["id"] for r in rows}) < rec["intended_n"]:
            probs.append(f"pilot run {k} covers {len({r['id'] for r in rows})} items, fewer than intended_n "
                         f"{rec['intended_n']}; the pilots score the items the counted arms will")
    return {"se": se, "detectable": DETECT_Z * se, "units": len(units), "pairs": sum(map(len, by_unit.values())),
            "differing_items": differ, "deterministic": det, "problems": probs}


def line7_text(l7, rec):
    eff = (rec.get("primary") or {}).get("smallest_effect")
    if l7 is None:
        return "line 7: fewer than two baseline pilot runs with shared ok items: no detectable difference; the run is exploratory"
    head = (f"line 7: SE {l7['se']:.4f}, detectable difference {l7['detectable']:.4f} (smallest effect {eff}) "
            f"over {l7['units']} units: ")
    if l7.get("problems"):
        return head + "does not hold: " + "; ".join(l7["problems"]) + "; the run is exploratory"
    if l7.get("deterministic"):
        return head + (f"holds by declaration: pilot.deterministic ({l7['deterministic']}); the reruns agree on every "
                       f"item, so no run-to-run noise was measured and the detectable difference is zero by that declaration")
    holds = isinstance(eff, (int, float)) and l7["detectable"] <= eff
    return head + ("holds" if holds else "does not hold; the run is exploratory")


def line7_holds(l7, rec):
    eff = (rec.get("primary") or {}).get("smallest_effect")
    if l7 is None or l7.get("problems"):
        return False
    return bool(l7.get("deterministic")) or (isinstance(eff, (int, float)) and l7["detectable"] <= eff)


def line8(rec, runs):
    pass_at = (rec.get("pilot") or {}).get("pass_at", 0.5)
    order, tally = [], {}
    for rows in runs:
        for r in rows:
            if r["status"] != "ok":
                continue
            if r["id"] not in tally:
                order.append(r["id"]); tally[r["id"]] = [0, 0]
            tally[r["id"]][0] += r["score"] >= pass_at
            tally[r["id"]][1] += 1
    saturated = lambda i: tally[i][0] in (0, tally[i][1])
    lines = [f"  {i} {tally[i][0]}/{tally[i][1]}" for i in sorted(order, key=lambda i: not saturated(i))]
    at0 = sum(1 for i in order if tally[i][0] == 0)
    at1 = sum(1 for i in order if tally[i][0] == tally[i][1])
    summary = (f"line 8: {len(order)} items over {len(runs)} baseline pilot runs; {at0} at 0, {at1} at 1, "
               f"{len(order) - at0 - at1} in between")
    return {"items": len(order), "at_0": at0, "at_1": at1, "rates": {i: tally[i] for i in order}}, lines, summary


def line2(by_arm, arms, intended, thr, probs):
    """Scored n equals intended n; failure shares under the threshold and equal across arms."""
    share, min_items = thr.get("share", 0.05), thr.get("min_items", 2)
    diff = thr.get("difference", share)
    res = {}
    for arm in arms:
        rs = by_arm.get(arm, [])
        ids = [r["id"] for r in rs]
        dup = sorted({i for i in ids if ids.count(i) > 1}, key=str)
        if dup:
            probs.append(f"line 2: arm {arm} has duplicate ids in items.jsonl: {', '.join(map(str, dup[:5]))}")
        n = len(rs)
        fails = collections.Counter(r["status"] for r in rs if r["status"] != "ok")
        k = sum(fails.values())
        res[arm] = {"n": n, "failures": dict(fails), "share": k / n if n else None}
        print(f"line 2: {arm} n {n}" + (f" of {intended} intended" if intended is not None else "") +
              f", failures {k}" + (f" ({k / n:.1%}: " + ", ".join(f"{s} {c}" for s, c in sorted(fails.items())) + ")" if k else ""))
        if intended is not None and n != intended:
            probs.append(f"line 2: arm {arm} scored {n} items, intended {intended}; find the missing or extra items")
        if n and k / n > share and k >= min_items:
            probs.append(f"line 2: arm {arm} failure share {k / n:.1%} ({', '.join(f'{s} {c}' for s, c in sorted(fails.items()))}) "
                         f"exceeds {share:.1%}; fix the harness or raise failure_threshold.share in the record")
    if intended is None and len({res[a]['n'] for a in arms}) > 1:
        probs.append("line 2: arms scored different numbers of items: " + ", ".join(f"{a} {res[a]['n']}" for a in arms))
    for i, x in enumerate(arms):
        for y in arms[i + 1:]:
            sx, sy = res[x]["share"], res[y]["share"]
            kx, ky = sum(res[x]["failures"].values()), sum(res[y]["failures"].values())
            if sx is not None and sy is not None and abs(sx - sy) > diff and abs(kx - ky) >= min_items:
                probs.append(f"line 2: failure rates differ between {x} ({sx:.1%}) and {y} ({sy:.1%}) by more than {diff:.1%}")
    return res


def line12(by_arm, arms, rec):
    floors = sorted(a for a in by_arm if str(a).startswith("floor:"))
    means = {a: mean_ok(by_arm.get(a, [])) for a in list(arms) + floors}
    beside = ", ".join(f"{a} {fmt(means[a])}" for a in arms)
    if floors:
        print("line 12: " + "; ".join(f"{f} {fmt(means[f])}" for f in floors) + f" beside {beside}")
    else:
        reason = (rec.get("floors") or {}).get("none_reason") if rec else ""
        print(f"line 12: no floor arm{f' ({reason})' if reason else ''}; {beside}")
    return floors, means


def real_n(v):
    return isinstance(v, int) and not isinstance(v, bool) and v > 0


def coverage_problems(rec, by_arm, arms, floors):
    """Every arm (floors included) scores the same set of unit ids, and of item ids where the record's unit is the
    item, unless the record declares units_differ_reason. Duplicate ids within an arm are line 2's own refusal."""
    reason = rec.get("units_differ_reason")
    if isinstance(reason, str) and reason.strip():
        return []
    unit = str((rec.get("primary") or {}).get("unit", "")).strip().lower()
    fields = [("unit", "unit ids")] + ([("id", "item ids")] if unit in ("item", "items", "id") else [])
    probs, names = [], list(arms) + list(floors)
    for field, label in fields:
        s0 = {str(r[field]) for r in by_arm.get(names[0], [])}
        for other in names[1:]:
            s1 = {str(r[field]) for r in by_arm.get(other, [])}
            if s0 != s1:
                probs.append(f"line 2: arms {names[0]} and {other} score different {label} (only in {names[0]}: "
                             f"{few(s0 - s1) or 'none'}; only in {other}: {few(s1 - s0) or 'none'}); every arm scores the "
                             f"same set, or the record declares units_differ_reason")
    return probs


def counted_problems(rec, stamps, l7, floors, means, arms, root, line3_ran, by_arm=None):
    """The counted gate: a real intended n, a scorer whose line-3 check ran, every arm stamped against this record's
    line-6 hash, two distinct stamped pilot runs and line 7 holds, a floor sits under the best arm. A refusal by any
    line `check` runs also denies the label; the caller adds those."""
    probs = []
    if len(arms) < 2:
        probs.append(f"counted needs at least two arms to compare; the record has {len(arms)} ({', '.join(arms)}); "
                     f"a single arm against the bar is exploratory")
    probs += coverage_problems(rec, by_arm or {}, arms, floors)
    if not real_n(rec.get("intended_n")):
        probs.append(f"line 2: counted needs a whole number intended_n; the record has {rec.get('intended_n', 'none')!r}")
    if not line3_ran:
        probs.append("line 3: counted needs a declared scorer (scorer.command, file, broken, good) whose check passes; none is declared")
    probs += pilot_gate(rec, root)
    l6 = line6_part(rec)
    if rec.get("status") == "exploratory" or not l6 or (rec.get("opened") or {}).get("line6_sha256") != l6:
        probs.append("line 6: the record opened exploratory or without hashed line-6 fields (metric, comparison, smallest effect, unit)")
    for arm, st in stamps.items():
        r = st.get("record")
        if st.get("label") != "counted" or not isinstance(r, dict) or r.get("line6_sha256") != l6:
            probs.append(f"line 6: counted needs every arm stamped --counted against this record's line-6 hash; {arm}'s stamp is not")
    if not line7_holds(l7, rec):
        if l7 is None:
            probs.append("line 7: no detectable difference from two baseline pilot runs")
        elif l7.get("problems"):
            probs += [f"line 7: {p}" for p in l7["problems"]]
        else:
            probs.append(f"line 7: detectable difference {l7['detectable']:.4f} exceeds the smallest effect {rec['primary']['smallest_effect']}")
    if not floors and not (rec.get("floors") or {}).get("none_reason"):
        probs.append("line 12: no floor:<name> arm in items.jsonl and no floors.none_reason in the record")
    hib = (rec.get("primary") or {}).get("higher_is_better", True)
    scored = [means[a] for a in arms if means.get(a) is not None]
    if scored:
        best = max(scored) if hib else min(scored)
        for f in floors:
            m = means[f]
            if m is not None and (m >= best if hib else m <= best):
                probs.append(f"line 12: {f} scores {fmt(m)}, reaching the best arm's {fmt(best)}")
    return probs


def finish(probs, ok_msg=None):
    for p in probs:
        print(f"refused: {p}", file=sys.stderr)
    if ok_msg and not probs:
        print(ok_msg)
    sys.exit(1 if probs else 0)


def cmd_new(a):
    p = Path(a.path)
    if p.exists():
        die(f"{p} exists")
    p.parent.mkdir(parents=True, exist_ok=True)
    save(p, TEMPLATE)
    print(f"wrote {p}; fill it in, then `prereg.py open {p}`")


def cmd_open(a):
    rec = load(a.path)
    if rec.get("schema") != 2:
        return open_v1(a, rec)
    if rec.get("opened"):
        die(f"already opened {rec['opened']['utc']}; its fields are frozen. Write a new record with \"parent\": \"{a.path}\"")
    for f in ("question", "bar"):
        if rec.get(f) == TEMPLATE[f]:
            die(f"{f} is still the template's placeholder; write the real one")
    for arm, spec in (rec.get("arms") or {}).items():
        if isinstance(spec, dict) and placeholder(spec.get("command")):
            die(f"arm {arm}: command is still the template's placeholder; write the real launch command")
    for f in ("question", "arms"):
        if not rec.get(f):
            die(f"missing {f}")
    for arm, spec in rec["arms"].items():
        if "reused" in spec and not spec["reused"].get("reason"):
            die(f"arm {arm} reuses a run; say why in reused.reason")
    if placeholder(rec.get("intended_n")):
        rec.pop("intended_n", None)
    root = rec_root(a.path)
    for arm, spec in rec["arms"].items():
        if spec.get("data"):
            spec["data"] = check_data(spec["data"], root, arm)
    missing = line6_missing(rec)
    causes = []
    if rec.get("status") == "exploratory":
        causes.append("status is \"exploratory\"")
    if str(rec.get("bar", "")).startswith("none"):
        causes.append(f"bar is {rec['bar']!r}")
    if missing:
        causes.append(f"line 6: primary.{', primary.'.join(missing)} not set")
    exploratory = bool(causes)
    if causes:
        print(f"{'; '.join(causes)}; opened exploratory: these runs cannot be counted")
    state, diff = git_state(Path(a.path).parent)
    if diff:
        dp = Path(a.path).with_suffix(".diff")
        dp.write_text(diff)
        state["diff_file"] = dp.name
    rec["opened"] = {"utc": now(), "host": socket.gethostname(), "frozen_sha256": frozen_part(rec),
                     "line6_sha256": line6_part(rec) or NA, **state}
    rec["status"] = "exploratory" if exploratory else "open"
    save(a.path, rec)
    print(f"opened {a.path} at {(state.get('commit') or '?')[:8]}; " +
          ("exploratory: its numbers cannot pass or fail a bar or pick an arm." if exploratory else
           "stamp each arm with --record and --counted at launch; `check` decides whether it earns the label counted."))


def snapshot(root, out, run_id):
    """Commit the working tree (tracked + untracked, .gitignore respected) under refs/lab/<run id> with a temporary
    index: the user's index and working tree are never touched. Files over 5 MB not already in HEAD are listed, not stored."""
    ref = "refs/lab/" + re.sub(r"[^A-Za-z0-9._-]", "-", run_id).strip(".-")
    if sh("git", "rev-parse", "--verify", "--quiet", ref, cwd=root):
        die(f"{ref} exists; a stamp is never overwritten: use a new --run-id")
    head = sh("git", "rev-parse", "--verify", "--quiet", "HEAD", cwd=root)
    try:
        out_rel = Path(out).resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        out_rel = None
    def ls(*args):
        r = subprocess.run(["git", "ls-files", "-z", *args], cwd=root, capture_output=True, text=True)
        return [f for f in r.stdout.split("\0") if f and not (out_rel and (f == out_rel or f.startswith(out_rel + "/")))]
    tracked = set(ls())
    untracked = ls("-o", "--exclude-standard")
    modified = set((subprocess.run(["git", "diff", "--name-only", "-z", "HEAD"], cwd=root, capture_output=True, text=True).stdout
                    if head else "").split("\0")) - {""}
    large, skip = [], []
    for f in sorted(tracked | set(untracked)):
        p = root / f
        if p.is_file() and not p.is_symlink() and p.stat().st_size > LARGE_BYTES:
            large.append({"path": f, "sha256": full_sha(p), "bytes": p.stat().st_size})
            if f not in tracked or f in modified:
                skip.append(f)
    with tempfile.TemporaryDirectory() as td:
        env = {**os.environ, "GIT_INDEX_FILE": os.path.join(td, "index")}
        g = lambda *c, extra_env=None, **kw: subprocess.run(["git", *c], cwd=root, env={**env, **(extra_env or {})},
                                                             capture_output=True, text=True, check=True, **kw).stdout.strip()
        if head:
            g("read-tree", head)
        # Name each file to add rather than excluding paths: git refuses (exit 1) any pathspec, exclude ones included,
        # that touches an ignored path on disk, as when the run folder sits under an ignored, existing runs/.
        keep = lambda f: f and f not in skip and not (out_rel and (f == out_rel or f.startswith(out_rel + "/")))
        names = sorted({f for f in (g("ls-files", "-z").split("\0") + g("ls-files", "-z", "-o", "--exclude-standard").split("\0"))
                        if keep(f)})
        if names:      # an empty pathspec list would mean "add everything"
            g("add", "-A", "--pathspec-from-file=-", "--pathspec-file-nul", input="\0".join(names),
              extra_env={"GIT_LITERAL_PATHSPECS": "1"})
        tree = g("write-tree")
        env.update(GIT_AUTHOR_NAME="prereg.py stamp", GIT_AUTHOR_EMAIL="lab@localhost",
                   GIT_COMMITTER_NAME="prereg.py stamp", GIT_COMMITTER_EMAIL="lab@localhost")
        commit = g("commit-tree", tree, *(["-p", head] if head else []), "-m", f"lab snapshot {run_id}")
        g("update-ref", ref, commit, "0" * 40)
    dirty = sorted(modified)
    return {"ref": ref, "commit": commit, "head": head or NA, "dirty": dirty, "untracked": untracked, "large_files": large}


def packages(a):
    if a.image:
        return {"image": a.image}
    try:
        import importlib.metadata as md
        dists = sorted({f"{d.metadata['Name']}=={d.version}" for d in md.distributions() if d.metadata["Name"]})
    except Exception:
        dists = NA
    return {"python": sys.version.split()[0], "distributions": dists}


def cmd_stamp(a):
    out = Path(a.out_dir)
    argv = a.argv
    if (out / "stamp.json").exists():
        die(f"{out / 'stamp.json'} exists; a stamp is never overwritten: stamp a new run folder")
    root = repo_root() or Path(".")
    rec, rec_info, data = None, NA, []
    if a.record:
        rec = load(a.record)
        if rec.get("schema") != 2:
            die(f"{a.record} has no schema: an old record; `induct` it, or write a new one with `new`")
        if not rec.get("opened"):
            die(f"{a.record} was never opened; `open` it before any run")
        if frozen_part(rec) != rec["opened"]["frozen_sha256"]:
            die(f"{a.record} changed after open; restore it or write a new record")
        if a.arm not in rec.get("arms", {}):
            die(f"--arm must name one of the record's arms: {', '.join(rec.get('arms', {}))}")
        data = check_data(rec["arms"][a.arm].get("data"), rec_root(a.record), a.arm)
        rec_info = {"path": a.record, "sha256": full_sha(a.record), "frozen_sha256": rec["opened"]["frozen_sha256"],
                    "line6_sha256": rec["opened"].get("line6_sha256", NA)}
    if a.counted:
        if rec is None:
            die("line 6: --counted needs --record, an opened record whose line-6 fields were hashed; stamp without --counted to run exploratory")
        l6 = line6_part(rec)
        if rec.get("status") == "exploratory" or not l6 or rec["opened"].get("line6_sha256") != l6:
            die("line 6: the record opened without hashed line-6 fields (metric, comparison, smallest effect, unit); "
                "stamp without --counted to run exploratory")
        if (out / "items.jsonl").is_file() and (out / "items.jsonl").stat().st_size:
            die(f"{out / 'items.jsonl'} already holds scored items: a counted stamp comes before scoring. "
                f"Stamp a new, empty run folder")
        if len(rec.get("arms") or {}) < 2:
            die("counted needs at least two arms to compare; this record has one. Stamp without --counted to run exploratory")
        probs = []
        l7 = line7(rec, pilot_rows(rec, rec_root(a.record), probs))
        if not line7_holds(l7, rec):
            die(line7_text(l7, rec) + "; stamp without --counted to run exploratory")
    # each file once: a --data file the record already lists (or one given twice) is not added again
    seen = {(rec_root(a.record) / e["path"]).resolve() for e in data}
    for d in a.data or []:
        if Path(d).resolve() not in seen:
            seen.add(Path(d).resolve())
            data.append({"path": d, **data_facts(d)})
    run_id = a.run_id or f"{out.name}-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    config = NA
    if a.config:
        try:
            values = json.loads(Path(a.config).read_text())
        except ValueError:
            values = NA
        config = {"path": a.config, "sha256": full_sha(a.config), "values": values}
    snap = snapshot(root, out, run_id) if repo_root() else NA
    stamp = {"schema": 2, "run_id": run_id, "tracker_run_id": a.run_id or NA, "utc": now(), "host": socket.gethostname(),
             "argv": argv, "arm": a.arm or NA, "label": "counted" if a.counted else "exploratory", "record": rec_info,
             "config": config,
             "model": {"id": a.model or NA, "revision": a.model_revision or NA, "tokenizer_revision": a.tokenizer_revision or NA,
                       "date": a.model_date or NA},
             "data": data or NA, "seeds": a.seed or NA, "packages": packages(a),
             "lab_inputs_sha256": full_sha(root / "lab-inputs.md") if (root / "lab-inputs.md").is_file() else NA,
             "snapshot": snap}
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "stamp.json", "x") as f:
        f.write(json.dumps(stamp, indent=2) + "\n")
    if snap == NA:
        print("warning: not a git repository: no snapshot of the code was taken", file=sys.stderr)
    elif snap["dirty"] or snap["untracked"]:
        print(f"warning: uncommitted code ({len(snap['dirty'])} modified, {len(snap['untracked'])} untracked); "
              f"{snap['ref']} holds it, but commit your code", file=sys.stderr)
    print(f"stamped {out} as {run_id} ({stamp['label']})" + (f" at {snap['commit'][:8]}" if snap != NA else ""))


def load_stamp(folder):
    p = Path(folder) / "stamp.json"
    return load(p) if p.is_file() else None


def cmd_check(a):
    probs = []
    if len(a.sources) == 1 and Path(a.sources[0]).is_file():
        return check_record(a.sources[0])
    by_arm, ids = {}, []
    for src in a.sources:
        st = load_stamp(src)
        if st is None:
            probs.append(f"line 10: {src} has no stamp.json; stamp the run at launch (`prereg.py stamp {src} -- <command>`)")
            continue
        print(f"run {st['run_id']}: {src}")
        for r in read_items(src, probs):
            by_arm.setdefault(r["arm"], []).append(r)
    arms = [x for x in by_arm if not str(x).startswith("floor:")]
    line2(by_arm, arms, None, {}, probs)
    print("line 3: no record, so no scorer declared; not checked")
    line12(by_arm, arms, None)
    print("label: exploratory")
    finish(probs)


def check_record(path):
    rec = load(path)
    if rec.get("schema") != 2:
        die(f"{path} has no schema: an old record; `induct` it")
    if not rec.get("opened"):
        die(f"{path} was never opened")
    if frozen_part(rec) != rec["opened"]["frozen_sha256"]:
        die(f"{path} changed after open; restore it or write a new record")
    root = rec_root(path)
    inputs = judged_inputs(rec, root)
    probs, stamps, by_arm = [], {}, {}
    arms = list(rec["arms"])
    folders = [(arm, spec["out"]) for arm, spec in rec["arms"].items()] + [(None, f) for f in (rec.get("floors") or {}).get("runs") or []]
    for arm, folder in folders:
        if arm is not None:
            st = load_stamp(root / folder)
            if st is None:
                probs.append(f"line 10: arm {arm} has no stamp.json in {folder}; stamp each run at launch")
            else:
                stamps[arm] = st
                print(f"run {st['run_id']}: {arm} ({st.get('label')})")
        for r in read_items(root / folder, probs):
            if r["arm"] not in rec["arms"] and not str(r["arm"]).startswith("floor:"):
                probs.append(f"line 2: {folder}/items.jsonl names arm {r['arm']!r}, neither a record arm nor floor:<name>")
                continue
            by_arm.setdefault(r["arm"], []).append(r)
    result = {"utc": now(), "record_frozen_sha256": rec["opened"]["frozen_sha256"]}
    result["line2"] = line2(by_arm, arms, rec.get("intended_n"), rec.get("failure_threshold") or {}, probs)
    if scorer_declared(rec):
        res, p3 = run_scorer(rec["scorer"], root)
        probs += p3
        result["line3"] = res
        if not p3:
            print(f"line 3: the scorer fails {rec['scorer']['broken']} and passes {rec['scorer']['good']}; "
                  f"{rec['scorer']['file']} sha256 {res['scorer_sha256'][:16]}")
    else:
        result["line3"] = "not declared"
        print("line 3: no scorer declared in the record; not checked")
    runs = pilot_rows(rec, root, probs)
    l7 = line7(rec, runs, {str(r["unit"]) for r in by_arm.get(arms[0], [])} if arms else set(), arms[0] if arms else None)
    result["line7"] = l7
    print(line7_text(l7, rec))
    out = Path(path).with_suffix(".check.json")
    if runs:
        res8, lines, summary = line8(rec, runs)
        result["line8"] = res8
        print(f"line 8: per-item pass rates over {len(runs)} baseline pilot runs (pass at {(rec.get('pilot') or {}).get('pass_at', 0.5)}),"
              f" saturated items first, at most {LINE8_SHOWN}:")
        print("\n".join(lines[:LINE8_SHOWN]))
        if len(lines) > LINE8_SHOWN:
            print(f"  ... {len(lines) - LINE8_SHOWN} more")
        print(summary)
        print(f"line 8: every item's pass rate is in {out} under line8.rates")
    floors, means = line12(by_arm, arms, rec)
    result["line12"] = {"floors": floors, "means": means}
    label = "exploratory"
    if any(st.get("label") == "counted" for st in stamps.values()):
        line3_ran = isinstance(result["line3"], dict) and "scorer_sha256" in result["line3"]
        cp = counted_problems(rec, {a: stamps.get(a, {}) for a in arms}, l7, floors, means, arms, root, line3_ran, by_arm)
        earlier = len(probs)
        probs += [f"{p} (counted refused; the run stands as exploratory)" for p in cp]
        label = "counted" if not probs else "exploratory"
        if label != "counted":
            print(f"counted refused: {len(cp)} counted-gate requirement(s) unmet and {earlier} other refusal(s); each is listed on stderr")
    pending = None
    if label == "counted":
        pending = parity_problem(path, rec, root, inputs)
        if pending:
            label = PENDING
    result["label"], result["refusals"], result["inputs"] = label, probs, inputs
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"label: {label}" + (f" ({pending})" if pending else ""))
    finish(probs)


def flat(d, prefix):
    if not isinstance(d, dict):
        return {prefix: d}
    out = {}
    for k, v in d.items():
        out.update(flat(v, f"{prefix}.{k}"))
    return out


def features(st):
    f = dict(args_from_argv(st.get("argv") or []))
    f.update(flat(st["config"]["values"], "config") if isinstance(st.get("config"), dict) else {"config": st.get("config")})
    f.update(flat(st.get("model") or {}, "model"))
    f["seeds"] = st.get("seeds")
    f["packages"] = st.get("packages")
    data = st.get("data")
    f["data"] = sorted(e["sha256"] for e in data) if isinstance(data, list) else data
    return f


def own_marks(f, arm, out, root):
    """Features with the arm's own name and its own out folder (or a path under it) replaced by marks, so two arms that
    differ there by construction compare equal. Another arm's name or folder is left as written."""
    outs = {os.path.normpath(out), str((root / out).resolve())}
    def mark(v):
        if isinstance(v, list):
            return [mark(x) for x in v]
        if not isinstance(v, str) or not v:
            return v
        if v == arm:
            return "<arm>"
        p = str(Path(v).resolve()) if os.path.isabs(v) else os.path.normpath(v)
        for o in outs:
            if p == o or p.startswith(o + os.sep):
                return "<out>" + p[len(o):]
        return v
    return {k: mark(v) for k, v in f.items()}


def parity_v2(a, rec):
    root = rec_root(a.path)
    inputs = judged_inputs(rec, root)
    varies = set(rec.get("varies", [])) | IGNORED_ARGS
    allowed = lambda k: k in varies or any(k.startswith(v + ".") for v in varies)
    stamps, problems, notes = {}, [], []
    for arm, spec in rec["arms"].items():
        st = load_stamp(root / spec["out"])
        if st is None:
            problems.append(f"line 13: arm {arm} has no stamp.json in {spec['out']}: nothing to compare")
        else:
            stamps[arm] = st
            if isinstance(st.get("data"), list):
                for e in st["data"]:
                    extra = {k: v for k, v in e.items() if k not in ("path", "sha256", "lines", "bytes")}
                    notes.append(f"line 13: {arm} data {e['path']} sha256 {e['sha256'][:16]}, {e['lines']} lines" +
                                 (f", {json.dumps(extra, sort_keys=True)}" if extra else ""))
    names = list(stamps)
    skip = [spec["out"] for spec in rec["arms"].values()] + list((rec.get("pilot") or {}).get("runs") or []) + \
        list((rec.get("floors") or {}).get("runs") or [])
    rp = Path(a.path).resolve()
    try:
        rel = rp.relative_to(root.resolve())
        skip.append(rel.with_suffix("").as_posix() + ".*")
    except ValueError:
        pass
    watched = rec.get("watched") or ["."]
    for other in names[1:]:
        ref = names[0]
        f0, f1 = features(stamps[ref]), features(stamps[other])
        m0 = own_marks(f0, ref, rec["arms"][ref]["out"], root)
        m1 = own_marks(f1, other, rec["arms"][other]["out"], root)
        for key in sorted(set(f0) | set(f1)):
            if not allowed(key) and plain(m0.get(key)) != plain(m1.get(key)):
                problems.append(f"line 13: {key}: {ref}={f0.get(key)!r} {other}={f1.get(key)!r} (not in varies)")
        s0, s1 = stamps[ref].get("snapshot"), stamps[other].get("snapshot")
        if not isinstance(s0, dict) or not isinstance(s1, dict):
            problems.append(f"line 13: no snapshot for {ref if not isinstance(s0, dict) else other}: code parity unverifiable")
            continue
        changed = sh("git", "diff", "--name-only", s0["commit"], s1["commit"], "--", *watched,
                     *[f":(top,exclude,glob){p}" if p.endswith(".*") else f":(top,exclude){p}" for p in skip], cwd=root)
        if changed is None:
            problems.append(f"line 13: could not compare the snapshots {s0['ref']} and {s1['ref']}")
            continue
        big0 = {x["path"]: x["sha256"] for x in s0.get("large_files", [])}
        big1 = {x["path"]: x["sha256"] for x in s1.get("large_files", [])}
        changed = changed.splitlines() + [p for p in sorted(set(big0) | set(big1)) if big0.get(p) != big1.get(p)
                                          and not any(p == s or p.startswith(s.rstrip("/") + "/") for s in skip)]
        if changed and not allowed("code"):
            problems.append(f"line 13: code differs between the {ref} and {other} snapshots: {', '.join(changed)}")
        else:
            notes.append(f"code identical across {ref}/{other} snapshots" if not changed else f"code differs (declared): {', '.join(changed)}")
    for n in notes:
        print(f"  ok    {n}")
    for p in problems:
        print(f"  FAIL  {p}")
    print("parity: " + ("PASS" if not problems else f"FAIL ({len(problems)})"))
    parity_path(a.path).write_text(json.dumps({
        "utc": now(), "pass": not problems, "problems": problems,
        "record_frozen_sha256": (rec.get("opened") or {}).get("frozen_sha256", NA),
        "run_ids": {arm: st.get("run_id") for arm, st in stamps.items()}, "inputs": inputs}, indent=2) + "\n")
    cp = Path(a.path).with_suffix(".check.json")
    check = read_json(cp)
    if check and str(check.get("label", "")).startswith("counted") and not changed_inputs(check.get("inputs"), inputs):
        new = PENDING if problems else "counted"
        if check["label"] != new:
            check["label"] = new
            cp.write_text(json.dumps(check, indent=2) + "\n")
            print(f"check label now: {new} ({cp})")
    sys.exit(1 if problems else 0)


def parity_path(path):
    return Path(path).with_suffix(".parity.json")


PENDING = "counted, pending parity"
CLOSE_FIELDS = ("observed", "closed", "status")      # what `close` writes into the record after check and parity


def judged_inputs(rec, root):
    """sha256 of what check and parity judge: the record (less what close writes) and, for every arm, pilot and floor
    run folder, its items.jsonl and stamp.json ("absent" when missing). Stored in check.json and parity.json; quote and
    close recompute it. A plain hash: it catches stale or copied results, not a forger who recomputes it."""
    out = {"record": hashlib.sha256(json.dumps({k: v for k, v in rec.items() if k not in CLOSE_FIELDS},
                                               sort_keys=True).encode()).hexdigest()}
    folders = [spec["out"] for spec in (rec.get("arms") or {}).values()] + \
        list((rec.get("pilot") or {}).get("runs") or []) + list((rec.get("floors") or {}).get("runs") or [])
    for f in folders:
        for name in ("items.jsonl", "stamp.json"):
            p = root / f / name
            out[f"{os.path.normpath(f)}/{name}"] = full_sha(p) if p.is_file() else "absent"
    return out


def changed_inputs(old, new):
    """Keys whose hash differs; every key when old holds no hashes (an older or hand-made file)."""
    if not isinstance(old, dict):
        return sorted(new) or ["(no input hashes)"]
    return sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))


def stale_why(res, diff):
    return ("it holds no input hashes (an older prereg.py or a hand-made file), so nothing shows the files are unchanged"
            if not isinstance(res.get("inputs"), dict) else f"{few(diff, 4)} changed")


def read_json(p):
    try:
        return load(p) if Path(p).is_file() else None
    except ValueError:
        return None


def parity_problem(path, rec, root, inputs):
    """None when a passing parity result is on file for the arms, record and files as they are now; else why not."""
    pp = parity_path(path)
    res = read_json(pp)
    now_ids = {arm: (load_stamp(root / spec["out"]) or {}).get("run_id") for arm, spec in rec["arms"].items()}
    if res is None:
        return f"line 13: no parity result on file for {path}; run `prereg.py parity {path}`"
    if not res.get("pass"):
        return f"line 13: the parity result for {path} failed ({pp}); the arms differ beyond `varies`"
    if res.get("run_ids") != now_ids or res.get("record_frozen_sha256") != (rec.get("opened") or {}).get("frozen_sha256", NA):
        return f"line 13: {pp} was written for other stamps or another version of the record; rerun `prereg.py parity {path}`"
    diff = changed_inputs(res.get("inputs"), inputs)
    if diff:
        return f"line 13: {pp} is stale: {stale_why(res, diff)} since parity ran; rerun `prereg.py parity {path}`"
    return None


def result_gate(path, rec, root):
    """A record with an arm stamped counted (or a check that labeled it counted) is quoted or closed only while
    check.json and, if it says counted, a passing parity.json are on file and hash the files as they are now."""
    cp = Path(path).with_suffix(".check.json")
    check = read_json(cp)
    claimed = any((load_stamp(root / spec["out"]) or {}).get("label") == "counted" for spec in rec["arms"].values())
    if not claimed and not (check and str(check.get("label", "")).startswith("counted")):
        return []
    inputs = judged_inputs(rec, root)
    if check is None:
        return [f"line 13: {path} has arms stamped counted but no check result on file ({cp}); "
                f"run `prereg.py check {path}`, then `prereg.py parity {path}`"]
    probs = []
    diff = changed_inputs(check.get("inputs"), inputs)
    if diff:
        probs.append(f"{cp} is stale: {stale_why(check, diff)} since check ran; rerun `prereg.py check {path}` "
                     f"and `prereg.py parity {path}`")
    if str(check.get("label", "")).startswith("counted"):
        p = parity_problem(path, rec, root, inputs)
        if p:
            probs.append(p)
    return probs


def cmd_parity(a):
    rec = load(a.path)
    return parity_v2(a, rec) if rec.get("schema") == 2 else parity_v1(a, rec)


def cmd_close(a):
    rec = load(a.path)
    if rec.get("schema") != 2:
        return close_v1(a, rec)
    if not rec.get("opened"):
        die("never opened: these numbers have no record to be scored against. Report them as exploratory")
    if frozen_part(rec) != rec["opened"]["frozen_sha256"]:
        die("a frozen field changed after open; restore it or write a new record")
    root, probs, observed = rec_root(a.path), [], {}
    gate = result_gate(a.path, rec, root)
    if gate:
        finish(gate)
    for arm, spec in rec["arms"].items():
        rows = [r for r in read_items(root / spec["out"], probs) if r["arm"] == arm]
        observed[arm] = {"n": len(rows), "mean": mean_ok(rows)}
        print(f"  {arm:<12} n {len(rows)}  mean {fmt(observed[arm]['mean'])}")
    if probs:
        finish(probs)
    rec["observed"] = observed
    rec["closed"] = {"utc": now(), "hits": 0, "predictions": 0, "note": a.note or ""}
    if rec["status"] != "exploratory":
        rec["status"] = "closed"
    save(a.path, rec)
    print(f"closed {a.path}; `check` holds the lines, and a fresh agent signs off any number that leaves your hands.")


def stamp_ids(folder):
    st = load_stamp(folder)
    return {st.get("run_id"), st.get("tracker_run_id")} if st else set()


def ledger_path(path):
    return Path(path).with_suffix(".ledger.jsonl")


def cmd_ledger(a):
    st = load_stamp(a.run_dir)
    if st is None:
        die(f"line 9: {a.run_dir} has no stamp.json; stamp the test run at launch, then ledger it")
    cfg = st.get("config")
    row = {"utc": now(), "run_id": st["run_id"], "config_sha256": cfg["sha256"] if isinstance(cfg, dict) else NA}
    lp = ledger_path(a.path)
    with open(lp, "a") as f:
        f.write(json.dumps(row) + "\n")
    n = sum(1 for l in lp.read_text().splitlines() if l.strip())
    print(f"line 9: test split scored {n} time{'' if n == 1 else 's'} for {a.path} ({lp}); report the count with the pick")


NUMBER = re.compile(r"\d[\d.,]*\s?%|(?<![\w/.])\d+/\d+(?![\w/])")


def id_pattern(ids):
    """Run ids as whole tokens: not inside a longer word, hyphenated name or dotted name (run-1 is not in run-12,
    run-1.5 or my-run-1). A sentence's closing period or a comma after an id is fine."""
    alts = "|".join(re.escape(i) for i in sorted(ids, key=len, reverse=True))
    return re.compile(rf"(?<![\w-])(?<!\w\.)(?:{alts})(?![\w-])(?!\.\w)") if ids else None


def cmd_quote(a):
    ids, gate = set(), []
    for src in a.sources:
        p = Path(src)
        if p.is_dir():
            ids |= stamp_ids(p)
            continue
        rec, root = load(p), rec_root(p)
        if rec.get("schema") == 2:
            gate += result_gate(src, rec, root)
        for spec in (rec.get("arms") or {}).values():
            ids |= stamp_ids(root / spec["out"])
        for f in list((rec.get("pilot") or {}).get("runs") or []) + list((rec.get("floors") or {}).get("runs") or []):
            ids |= stamp_ids(root / f)
        lp = ledger_path(p)
        if lp.is_file():
            ids |= {json.loads(l).get("run_id") for l in lp.read_text().splitlines() if l.strip()}
    ids = {str(i) for i in ids if i and i != NA}
    pat = id_pattern(ids)
    bad = [(k, l) for k, l in enumerate(Path(a.report).read_text().splitlines(), 1)
           if NUMBER.search(l) and not (pat and pat.search(l))]
    for k, l in bad:
        print(f"refused: line 10: {a.report}:{k} quotes a number with no run id: {l.strip()}", file=sys.stderr)
    for g in gate:
        print(f"refused: {g}", file=sys.stderr)
    if not bad:
        print(f"quote: every rate and fraction in {a.report} carries a run id ({len(ids)} known)")
    sys.exit(1 if bad or gate else 0)


def cmd_induct(a):
    """Vet an old record after the fact. Never refuses, never edits the record; writes <record>.induct.json beside it."""
    res = {"utc": now(), "record": a.path, "written_before_scoring": "not established", "pilot_power": "not established"}
    try:
        res["record_sha256"] = full_sha(a.path)
        rec = load(a.path)
        root = rec_root(a.path)
        res["hash_intact"] = (frozen_part(rec) == rec["opened"]["frozen_sha256"]) if rec.get("opened") else "not established"
        res["arms"], per_item = {}, {}
        for arm, spec in (rec.get("arms") or {}).items():
            folder = root / spec.get("out", "")
            if not (folder / "items.jsonl").is_file():
                res["arms"][arm] = "not established (no items.jsonl)"
                continue
            probs = []
            rows = read_items(folder, probs)
            fails = collections.Counter(r["status"] for r in rows if r["status"] != "ok")
            res["arms"][arm] = {"n": len(rows), "failures": dict(fails), "mean": mean_ok(rows), "problems": probs}
            for r in rows:
                if r["status"] == "ok":
                    per_item.setdefault(r["id"], []).append(r["score"] >= 0.5)
        res["saturation"] = ({"items": len(per_item), "at_0": sum(1 for v in per_item.values() if not any(v)),
                              "at_1": sum(1 for v in per_item.values() if all(v)), "note": "across arms found, not baseline pilots"}
                             if per_item else "not established (no items.jsonl)")
        if scorer_declared(rec):
            res["scorer"] = run_scorer(rec["scorer"], root)[0]
        else:
            res["scorer"] = "not established (no scorer declared)"
    except Exception as e:      # induct never refuses: what it could not read is recorded
        res["error"] = f"{type(e).__name__}: {e}"
    out = Path(a.path).with_suffix(".induct.json")
    out.write_text(json.dumps(res, indent=2, default=str) + "\n")
    for k in ("hash_intact", "arms", "saturation", "scorer", "written_before_scoring", "pilot_power", "error"):
        if k in res:
            print(f"  {k}: {json.dumps(res[k], default=str)}")
    print(f"inducted {a.path} -> {out}; the record itself is unchanged")


def main(argv=None):
    os.environ["GIT_OPTIONAL_LOCKS"] = "0"      # read-only git calls never rewrite the user's index
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("new", "open", "parity", "induct"):
        sub.add_parser(name).add_argument("path")
    s = sub.add_parser("stamp")
    s.add_argument("out_dir")
    s.add_argument("--record", help="the opened schema-2 record this run belongs to")
    s.add_argument("--arm", help="which of the record's arms this run is")
    s.add_argument("--counted", action="store_true", help="claim the label counted (refused unless lines 6 and 7 hold)")
    s.add_argument("--run-id", help="the tracker's run id (MLflow, W&B, Inspect log); default: folder name + time")
    s.add_argument("--config", help="the effective configuration file (JSON is stored whole)")
    s.add_argument("--model"); s.add_argument("--model-revision"); s.add_argument("--tokenizer-revision")
    s.add_argument("--model-date", help="for an API model: the date the resolved model id was read")
    s.add_argument("--data", action="append", help="a data file read by the run (repeatable)")
    s.add_argument("--seed", action="append", help="a seed (repeatable)")
    s.add_argument("--image", help="image digest; else the running interpreter's package list is recorded")
    c = sub.add_parser("check")
    c.add_argument("sources", nargs="+", help="a schema-2 record, or one or more run folders (exploratory)")
    c = sub.add_parser("close")
    c.add_argument("path")
    c.add_argument("--note")
    l = sub.add_parser("ledger")
    l.add_argument("path"); l.add_argument("run_dir")
    q = sub.add_parser("quote")
    q.add_argument("report"); q.add_argument("sources", nargs="+")
    l = sub.add_parser("ls")
    l.add_argument("dir", nargs="?", default="prereg")
    argv = list(sys.argv[1:] if argv is None else argv)
    launch = []
    if argv[:1] == ["stamp"] and "--" in argv:      # everything after -- is the launch command, options included
        k = argv.index("--")
        argv, launch = argv[:k], argv[k + 1:]
    a = ap.parse_args(argv)
    a.argv = launch
    try:
        {"new": cmd_new, "open": cmd_open, "stamp": cmd_stamp, "parity": cmd_parity, "close": cmd_close, "ls": cmd_ls,
         "check": cmd_check, "ledger": cmd_ledger, "quote": cmd_quote, "induct": cmd_induct}[a.cmd](a)
    except subprocess.CalledProcessError as e:      # an unexpected git failure: one line with git's own message
        cmd = e.cmd if isinstance(e.cmd, (list, tuple)) else [str(e.cmd)]
        msg = [l.strip() for l in (e.stderr or e.stdout or "").splitlines() if l.strip() and not l.startswith("hint:")]
        die(f"{' '.join(map(str, cmd[:2]))} failed (exit {e.returncode}): {'; '.join(msg) or 'no message'}")


if __name__ == "__main__":
    main()
