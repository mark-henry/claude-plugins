#!/usr/bin/env python3
"""Preregister an experiment, stamp each run, and check it against the standard lines of lab:experiment.

  prereg.py new    PATH                          write a template record (schema 2) to fill in
  prereg.py open   PATH                          validate; hash the frozen fields and the line-6 fields; hash arm data
  prereg.py stamp  OUT [options] -- CMD...       snapshot the tree under refs/lab/<run id>, write OUT/stamp.json
  prereg.py run    OUT [options] -- CMD...       stamp, then run CMD (output streamed, its exit code returned); a
                                                 non-zero exit with no outputs is a failed launch: the folder is
                                                 freed and the same command retries the same run id as attempt 2
                   --outputs GLOB                (run) outputs are files matching GLOB under OUT, written since launch
                   --arms a,b,c                  (stamp or run) one command writing OUT/a, OUT/b, OUT/c: a stamp each,
                                                 one launch id, run ids <launch id>-<arm>
  prereg.py check  PATH | RUN_DIR...             lines 2, 3, 7, 8, 12 and the counted gate, from items.jsonl
  prereg.py parity PATH                          the arm comparison: arms differ only in `varies` (line 13)
  prereg.py ledger PATH RUN_DIR                  append one line each time the test split is scored (line 9)
  prereg.py quote  REPORT PATH|RUN_DIR...        every rate or a/b in REPORT carries a run id (line 10)
  prereg.py induct PATH                          vet an old record after the fact; never refuses, never edits it
  prereg.py close  PATH [--note TEXT]            observed per arm, status -> closed
  prereg.py note   RUN_ID FINDING [--changes T]  append a one-sentence finding for a run to runs.jsonl
  prereg.py ls     [QUERY | DIR]                 runs.jsonl newest first with findings, filtered by QUERY; with no
                                                 runs.jsonl (or given a DIR), records and how past predictions landed
  prereg.py backfill DIR                         seed runs.jsonl from the stamps and records already under DIR

Stdlib only; never contacts a tracker (its run id is a string). Exit 1 on a refusal, with one line per thing to
fix, naming the line of the skill it enforces. Records without "schema" (made before schema 2) are read as before
by close, ls and parity, and hashed exactly as before. A run is counted or it is not: stamps and check results carry
a boolean `counted`; ones written before it carry a `label` string and are read as before. stamp, run and close
append one line each to runs.jsonl at the repository root (the run ledger: append-only, one write per line). The
skill's SKILL.md says when each command runs. `prereg.py --version` prints VERSION, bumped only on a breaking change;
stamps, opened records and check results carry it as `tool_version`, and a file from a newer version is refused.

A run folder holds stamp.json (written by `stamp` at launch) and items.jsonl (written by the harness): one JSON
object per line with id, arm, unit, score (number or null) and status (ok, error, empty, truncated, parse_failure).
Arms named floor:<name> are trivial policies scored on the same items (line 12). A score outside the record's
primary.range [lo, hi], or not finite, is a failed item (out_of_range, non_finite_score).
"""
from __future__ import annotations

import argparse, collections, datetime, glob, hashlib, json, math, os, random, re, shlex, socket, statistics, subprocess, sys, tempfile, threading, time
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
                "range": "... line 2: [lo, hi], the scores the metric can take; a score outside is a failed item",
                "higher_is_better": True},
    "intended_n": "... line 2: items per arm",
    "failure_threshold": {"share": 0.05, "min_items": 2, "difference": 0.05},
    "varies": ["model"],
    "watched": ["."],
    "arms": {"untreated": {"out": "runs/untreated", "command": "...", "data": []},
             "treated": {"out": "runs/treated", "command": "...", "data": []}},
    "pilot": {"runs": [], "pass_at": 0.5, "noise_from": "runs"},
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


VERSION = 1      # bump on a BREAKING change (a stamp, record or check result an older prereg.py would misread)


def load(path):
    d = json.loads(Path(path).read_text())
    made = max(d.get("tool_version") or 0, (d.get("opened") or {}).get("tool_version") or 0) if isinstance(d, dict) else 0
    if made > VERSION:
        print(f"refused: {path} was written by a newer prereg.py (version {made}; this is {VERSION}): update the lab "
              f"plugin", file=sys.stderr)
        sys.exit(1)
    return d


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
    q = a.query
    if q is not None and Path(q).is_dir():
        return records_ls(q)
    rows = read_ledger(ledger_root())
    if not rows:
        if q is not None:
            print(f"no {LEDGER} at {ledger_root()}: nothing to search; the records in prereg/ follow")
        if not records_ls("prereg"):
            print(f"no runs yet: no {LEDGER} at {ledger_root()} and no records in prereg/")
        return
    ledger_ls(rows, q, a.limit)


def pretty_utc(u):
    m = re.fullmatch(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})Z", str(u or ""))
    return f"{m[1]}-{m[2]}-{m[3]} {m[4]}:{m[5]}Z" if m else str(u or "?")


def ledger_ls(rows, query, limit):
    """Runs newest first, each with its findings (notes, exit codes, closes of a record it belongs to); records
    with no stamped run as their own entries. QUERY filters: every word of it, case-insensitively, somewhere in the fields shown."""
    entries, by_run = [], {}
    for r in rows:
        if r.get("kind") in ("run", "record"):
            prev = by_run.get(r.get("run_id")) if r.get("kind") == "run" and r.get("run_id") else None
            if prev and (r.get("attempt") or 1) > 1:      # a retry after a failed launch: the same run, its newest stamp
                prev["row"], prev["attempts"] = r, max(prev["attempts"], r["attempt"])
                continue
            e = {"row": r, "findings": [], "attempts": r.get("attempt") or 1, "failed": []}
            entries.append(e)
            if r.get("run_id"):
                by_run.setdefault(r["run_id"], e)
    for r in rows:
        k = r.get("kind")
        if k == "note" and r.get("run_id") in by_run:
            by_run[r["run_id"]]["findings"].append(f"finding: {r.get('finding', '')}" +
                                                   (f" (changes: {r['changes']})" if r.get("changes") else ""))
        elif k == "exit" and r.get("run_id") in by_run and r.get("launch_failed"):
            by_run[r["run_id"]]["failed"].append(r)
        elif k == "exit" and r.get("run_id") in by_run and r.get("exit_code") != 0:
            by_run[r["run_id"]]["findings"].append(f"exit code {r.get('exit_code')}")
        elif k == "close":
            text_ = f"closed {r.get('record')}: {r.get('result', '')}"
            for rid in r.get("run_ids") or []:
                if rid in by_run:
                    by_run[rid]["findings"].append(text_)
            for e in entries:
                if e["row"].get("kind") == "record" and e["row"].get("record") == r.get("record"):
                    e["findings"].append(text_)
    for e in entries:      # failed launches are attempts of their run, not runs of their own
        if e["failed"]:
            e["findings"].insert(0, attempts_text(e["attempts"], e["failed"]))
    def text(e):
        r = e["row"]
        return " ".join(str(r.get(f) or "") for f in ("run_id", "question", "command", "folder", "record")) + \
            " " + " ".join(e["findings"])
    if query:      # every word of the query, in any order, case-insensitive
        words = query.lower().split()
        entries = [e for e in entries if all(w in text(e).lower() for w in words)]
    order = {id(e): k for k, e in enumerate(entries)}      # within one minute, later lines are newer
    entries.sort(key=lambda e: (str(e["row"].get("utc") or ""), order[id(e)]), reverse=True)
    for e in entries[:limit]:
        r = e["row"]
        if r.get("kind") == "record":
            print(f"{pretty_utc(r.get('utc'))}  record {r.get('record')}  ({r.get('status', '?')}; no stamped run)")
        else:
            last_failed = any((f.get("attempt") or 1) == e["attempts"] for f in e["failed"])
            print(f"{pretty_utc(r.get('utc'))}  {r.get('run_id')}  counted: {str(bool(r.get('counted'))).lower()}  "
                  f"{r.get('folder') or ''}" + ("  LAUNCH FAILED, nothing scored" if last_failed else ""))
        what = r.get("question") or r.get("command")
        if what:
            print(f"    {what[:160]}")
        for f in e["findings"]:
            print(f"    {f}")
    if len(entries) > limit:
        print(f"... {len(entries) - limit} older; --limit N shows more")
    if not entries:
        print(f"no run in {LEDGER} matches {query!r}" if query else f"{LEDGER} holds no runs")


def attempts_text(attempts, failed):
    """One finding line for a run with failed launches: how many attempts, which failed, and the last stderr line of
    the first failure (where a traceback names its error)."""
    ns = sorted({f.get("attempt") or 1 for f in failed})
    first = min(failed, key=lambda f: f.get("attempt") or 1)
    cause = ([l for l in first.get("stderr_tail") or [] if l.strip()] or ["no stderr"])[-1].strip()[:200]
    if attempts == 1:
        return f"launch failed (exit {first.get('exit_code')}): {cause}"
    which = "first" if ns == [1] else "all" if len(ns) == attempts else "attempts " + ", ".join(map(str, ns))
    return f"{attempts} attempts, {which} failed at launch: {cause}"


def cmd_note(a):
    root = ledger_root()
    known = {r.get("run_id") for r in read_ledger(root) if r.get("kind") == "run"}
    if a.run_id not in known:
        die(f"{a.run_id} is not a run id in {root / LEDGER}: a run with no stamp has no run id, and its numbers are "
            f"not quoted; `prereg.py ls` lists the run ids")
    append_ledger(root, {"kind": "note", "utc": now(), "run_id": a.run_id, "finding": a.finding, "changes": a.changes})
    print(f"noted for {a.run_id} in {root / LEDGER}")


def cmd_backfill(a):
    """Seed runs.jsonl from what is already on disk under DIR: one run line per stamp.json (oldest first), one
    record line per record in prereg/ that no stamp names, and one close line per closed record. Run ids and
    records already in the ledger are skipped, so it can be rerun. Lines carry "backfilled": true."""
    base = Path(a.dir).resolve()
    root = ledger_root(base)
    have = read_ledger(root)
    seen_runs = {r.get("run_id") for r in have if r.get("kind") == "run"}
    seen_recs = {r.get("record") for r in have if r.get("kind") in ("record", "close")}
    skip_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__"}
    new, named = [], set()
    for p in sorted(base.rglob("stamp.json")):
        if skip_dirs & set(p.relative_to(base).parts):
            continue
        try:
            st = load(p)
        except (ValueError, OSError):
            continue
        if not isinstance(st, dict) or not st.get("run_id"):
            continue
        rp = st.get("record_repo_path") if st.get("record_repo_path") not in (None, NA) else None
        if rp:
            named.add(rp)
        if st["run_id"] in seen_runs:
            continue
        seen_runs.add(st["run_id"])
        rec = read_json(root / rp) if rp else None
        new.append({"kind": "run", "utc": st.get("utc"), "run_id": st["run_id"], "counted": stamp_counted(st),
                    "command": command_text(st.get("argv") or []), "record": rp,
                    "question": (rec or {}).get("question"), "folder": repo_rel(str(p.parent), root),
                    "launch_id": st.get("launch_id"), "backfilled": True})
    for p in sorted((base / "prereg").glob("*.json")) if (base / "prereg").is_dir() else []:
        rec = read_json(p)
        if not isinstance(rec, dict) or "question" not in rec or not isinstance(rec.get("arms"), dict):
            continue
        rel = repo_rel(str(p), root)
        if rel in seen_recs:
            continue
        opened = (rec.get("opened") or {}).get("utc")
        if rel not in named:
            new.append({"kind": "record", "utc": opened, "record": rel, "question": rec["question"],
                        "status": rec.get("status"), "backfilled": True})
        if rec.get("closed"):
            obs = rec.get("observed") or {}
            result = "; ".join(f"{arm} {observed_text(o)}" for arm, o in obs.items() if isinstance(o, dict))
            run_ids = [(load_stamp(root / spec.get("out", "")) or {}).get("run_id")
                       for spec in rec["arms"].values() if isinstance(spec, dict)]
            new.append({"kind": "close", "utc": rec["closed"].get("utc"), "record": rel, "question": rec["question"],
                        "run_ids": [r for r in run_ids if r], "result": result, "backfilled": True})
    new.sort(key=lambda r: str(r.get("utc") or ""))
    for r in new:
        append_ledger(root, r)
    kinds = collections.Counter(r["kind"] for r in new)
    print(f"backfilled {root / LEDGER}: " + (", ".join(f"{n} {k}" for k, n in sorted(kinds.items())) or "nothing new"))


def observed_text(o):
    """One arm's observed result: schema 2 {n, mean}, or an old record's {metric: {num, den, rate}}."""
    if "n" in o:
        return f"n {o['n']} mean {fmt(o.get('mean'))}"
    return ", ".join(f"{m} {v.get('num')}/{v.get('den')}" for m, v in o.items() if isinstance(v, dict))


def records_ls(dir):
    """Print the records in dir; returns how many it listed."""
    recs = sorted(Path(dir).glob("*.json"))
    hits = total = listed = 0
    width = []
    for p in recs:
        try:
            r = load(p)
        except Exception:
            continue
        if "question" not in r:
            continue
        listed += 1
        print(f"  {r.get('status', '?'):<11} {p.name}  {r['question'][:70]}")
        if r.get("closed"):
            hits += r["closed"]["hits"]
            total += r["closed"]["predictions"]
            width += [iv[1] - iv[0] for arm in r.get("predictions", {}).values() for iv in arm.values()]
    if total:
        print(f"calibration: {hits}/{total} intervals hit, mean width {sum(width) / len(width):.2f}")
    return listed


# ---------------------------------------------------------------------------------------------------------------
# Schema 2: the standard checks. Old records (no "schema") take the *_v1 paths above, unchanged.

ITEM_STATUSES = ("ok", "error", "empty", "truncated", "parse_failure")
NON_FINITE = "non_finite_score"      # given by read_items to an ok row whose score is NaN or infinite
OUT_OF_RANGE = "out_of_range"        # given by read_items to an ok row whose score is outside primary.range
DET_LABEL = " (deterministic harness declared)"      # appended to a counted label that rests on pilot.deterministic
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


RESCORE = ("; fix the scorer, then stamp the arms again in new run folders and score them again with the fixed "
           "scorer: scores from the old one are not evidence")


def scorer_sha(rec, root):
    """sha256 of the declared scorer file as it is now; None when no scorer is declared or the file is missing."""
    if not scorer_declared(rec):
        return None
    p = root / rec["scorer"]["file"]
    return full_sha(p) if p.is_file() else None


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
        probs.append(f"line 3: the scorer passed the broken output {sc['broken']}; it cannot tell a broken output from a good one"
                     f"{RESCORE}")
    if not res["good_passed"]:
        probs.append(f"line 3: the scorer failed the known-good output {sc['good']}{RESCORE}")
    return res, probs


def score_range(rec):
    """primary.range as (lo, hi) when it is two finite numbers with lo <= hi; else None (absent or malformed)."""
    v = ((rec or {}).get("primary") or {}).get("range")
    if (isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool)
                                                     and math.isfinite(x) for x in v) and v[0] <= v[1]):
        return v[0], v[1]
    return None


def read_items(folder, probs, rng=None):
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
        if r["status"] == "ok" and not math.isfinite(r["score"]):
            r = {**r, "status": NON_FINITE}      # NaN or infinite: a failed item, counted in line 2, never in a mean
        elif r["status"] == "ok" and rng and not rng[0] <= r["score"] <= rng[1]:
            r = {**r, "status": OUT_OF_RANGE}    # outside primary.range: a failed item, as a non-finite score is
        out.append(r)
    return out


def mean_ok(rows):
    xs = [r["score"] for r in rows if r["status"] == "ok"]
    return sum(xs) / len(xs) if xs else None


def finite(x):
    return x is None or math.isfinite(x)


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
    return [[r for r in read_items(root / run, probs, score_range(rec)) if not str(r["arm"]).startswith("floor:")]
            for run in pilot_folders(rec, root)]


ITEM_UNITS_MIN = 100      # line 7 by item noise needs about this many units in the run


def noise_from_items(rec):
    """pilot.noise_from: "items" (one pilot; the independent unit is an item) or "runs" (two pilots; the default)."""
    return (rec.get("pilot") or {}).get("noise_from") == "items"


def pilot_gate(rec, root):
    """Counted needs two distinct baseline pilot runs, each stamped, with different run ids; one, when the noise comes
    from the items (pilot.noise_from "items")."""
    named = (rec.get("pilot") or {}).get("runs") or []
    folders = pilot_folders(rec, root)
    probs = []
    if noise_from_items(rec):
        for f in folders:
            if load_stamp(root / f) is None:
                probs.append(f"line 7: pilot run {f} has no stamp.json; stamp the pilot run at launch")
        if not folders:
            probs.append("line 7: pilot.noise_from is \"items\", and counted needs one stamped pilot run on the real "
                         "items, listed in pilot.runs; none is listed")
        return probs
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


def stamp_seeds(st):
    """A stamp's seeds as a sorted tuple, or None when it records none."""
    s = (st or {}).get("seeds")
    return tuple(sorted(map(str, s))) if isinstance(s, list) and s else None


def seed_word(s):
    return "no seed" if s is None else f"seed {', '.join(s)}"


def deterministic_seed_problems(pilot_stamps, arm_stamps):
    """pilot.deterministic, checked where the stamps can check it. Pilots stamped with different seeds that still agree
    support the declaration. Otherwise every stamp, pilots and counted arms, records the same seed or none: arms run on
    a seed the pilots never used contradict a harness said to have no randomness, as does a seed on one pilot only."""
    ps = [stamp_seeds(st) for st in pilot_stamps[:2]]
    if len(ps) == 2 and None not in ps and ps[0] != ps[1]:
        return []
    probs = []
    if len(ps) == 2 and ps[0] != ps[1]:
        probs.append(f"pilot.deterministic is declared, but one pilot stamp records {seed_word(ps[0])} and the other "
                     f"{seed_word(ps[1])}; rerun the pilots with different seeds and stamp each with --seed")
    shared = ps[0] if ps else None
    for arm, st in arm_stamps.items():
        s = stamp_seeds(st)
        if s != shared:
            probs.append(f"pilot.deterministic is declared, but the pilots ran with {seed_word(shared)} and arm {arm} "
                         f"with {seed_word(s)}: a harness that takes seeds is not shown deterministic that way; rerun the "
                         f"pilots with two different seeds, or stamp the arms with the pilots' seed")
    return probs


def few(xs, k=3):
    return ", ".join(map(str, sorted(xs, key=str)[:k])) + (" ..." if len(xs) > k else "")


def line7_items(rec, runs, arm_units=None, first_arm=None):
    """Line 7 when the independent unit is an item (pilot.noise_from "items"): one pilot run gives the spread of unit
    mean scores; the SE of a difference between two arms of n units each is sqrt(2) * sd / sqrt(n) (unpaired, so
    conservative). n is the first arm's unit count at check, or intended_n projected to units at stamp. Needs about
    100 units in the run, and pilot units that the arms score."""
    if not runs:
        return None
    rows = [r for r in runs[0] if r["status"] == "ok"]
    by_unit = {}
    for r in rows:
        by_unit.setdefault(str(r["unit"]), []).append(r["score"])
    if not by_unit:
        return None
    means = [sum(v) / len(v) for v in by_unit.values()]
    probs = []
    if arm_units is not None:
        n = len(arm_units)
        extra = set(by_unit) - arm_units
        if extra:
            probs.append(f"the pilot scores units arm {first_arm} does not ({few(extra)}); the pilot runs on the real items")
    else:
        n_items = rec.get("intended_n")
        n = round(n_items * len(by_unit) / len(rows)) if real_n(n_items) and rows else 0
    if len(means) < 2:
        probs.append(f"the pilot has ok items in {len(means)} unit; the SE needs at least two")
    if n < ITEM_UNITS_MIN:
        probs.append(f"the run has about {n} units, fewer than {ITEM_UNITS_MIN}: item noise alone does not estimate "
                     f"the difference; set pilot.noise_from to \"runs\" in a new record and run two pilots")
    sd = statistics.stdev(means) if len(means) > 1 else 0.0
    se = math.sqrt(2) * sd / math.sqrt(n) if n else float("inf")
    return {"se": se, "detectable": DETECT_Z * se, "units": len(means), "run_units": n, "pairs": len(rows),
            "differing_items": None, "deterministic": None, "noise_from": "items", "problems": probs}


def noise(rec, runs, arm_units=None, first_arm=None):
    return (line7_items if noise_from_items(rec) else line7)(rec, runs, arm_units, first_arm)


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
        probs.append("the two pilot runs give identical scores on every shared item: rerun the pilots with different "
                     "seeds (a copied run, or a rerun on the same seed, is not a second run); only for a harness with no "
                     "randomness at all, declare pilot.deterministic with the reason")
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
        if noise_from_items(rec):
            return "line 7: no stamped pilot run with ok items: no detectable difference; the run is not counted"
        return "line 7: fewer than two baseline pilot runs with shared ok items: no detectable difference; the run is not counted"
    if l7.get("noise_from") == "items":
        head = (f"line 7: SE {l7['se']:.4f}, detectable difference {l7['detectable']:.4f} (smallest effect {eff}) from "
                f"item noise: {l7['units']} units in one pilot, projected to {l7['run_units']} units per arm, unpaired: ")
    else:
        head = (f"line 7: SE {l7['se']:.4f}, detectable difference {l7['detectable']:.4f} (smallest effect {eff}) "
                f"over {l7['units']} units: ")
    if l7.get("problems"):
        return head + "does not hold: " + "; ".join(l7["problems"]) + "; the run is not counted"
    if l7.get("deterministic"):
        return head + (f"holds by declaration: pilot.deterministic ({l7['deterministic']}); the reruns agree on every "
                       f"item, so no run-to-run noise was measured and the detectable difference is zero by that declaration")
    holds = isinstance(eff, (int, float)) and l7["detectable"] <= eff
    return head + ("holds" if holds else "does not hold; the run is not counted")


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
               f"{len(order) - at0 - at1} in between" +
               ("; with one pilot run every item reads 0 or 1, so saturation is not measured" if len(runs) == 1 else ""))
    return {"items": len(order), "at_0": at0, "at_1": at1, "rates": {i: tally[i] for i in order}}, lines, summary


def line2(by_arm, arms, intended, thr, probs, dup_hint=""):
    """Scored n equals intended n; failure shares under the threshold and equal across arms."""
    share, min_items = thr.get("share", 0.05), thr.get("min_items", 2)
    diff = thr.get("difference", share)
    res = {}
    for arm in arms:
        rs = by_arm.get(arm, [])
        ids = [r["id"] for r in rs]
        dup = sorted({i for i in ids if ids.count(i) > 1}, key=str)
        if dup:
            probs.append(f"line 2: arm {arm} has duplicate ids in items.jsonl: {', '.join(map(str, dup[:5]))}{dup_hint}")
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
    """Every arm (floors included) scores the same set of item ids and the same set of unit ids, whatever the record
    calls its unit, unless the record declares units_differ_reason. Duplicate ids within an arm are line 2's own refusal."""
    reason = rec.get("units_differ_reason")
    if isinstance(reason, str) and reason.strip():
        return []
    fields = [("id", "item ids"), ("unit", "unit ids")]
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


def violated_for_counted(rec, by_arm, arms, floors, means):
    """Line-2 violations that only a counted claim checks: arms scoring different items or units, a non-finite mean.
    Unlike the counted gate's other refusals, they block quote and close too: the comparison itself is broken."""
    probs = coverage_problems(rec, by_arm, arms, floors)
    for a in list(arms) + list(floors):
        if not finite(means.get(a)):
            probs.append(f"line 2: arm {a}'s mean score is {means[a]}, not a finite number; find the rows whose scores "
                         f"overflow and fix the harness or the metric")
    return probs


def repo_rel(path, root, base=None):
    """A record path relative to the repository root (posix), or its absolute path outside it. A relative path is
    read against base (the current directory when None)."""
    p = Path(path) if os.path.isabs(path) else Path(base or os.getcwd()) / path
    try:
        return p.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return p.resolve().as_posix()


def stamp_record_problems(rec, path, root, stamps):
    """A counted stamp belongs to the record it was stamped under: same file, same frozen hash. Runs stamped under
    another record (an abandoned one, a copy) are not this record's runs. The scorer that scored them is the one
    line 3 tests now: a scorer changed since a stamp means its arm was scored by another scorer."""
    probs, here, frozen = [], repo_rel(path, root), (rec.get("opened") or {}).get("frozen_sha256")
    sc_now = scorer_sha(rec, root)
    for arm, st in stamps.items():
        if not stamp_counted(st):
            continue
        r = st.get("record") if isinstance(st.get("record"), dict) else {}
        # a stamp from before record_repo_path: its path was given relative to where stamp ran, usually the root
        there = st.get("record_repo_path") or (repo_rel(r["path"], root, root) if isinstance(r.get("path"), str) else None)
        if there != here or r.get("frozen_sha256") != frozen:
            probs.append(f"line 6: arm {arm}'s counted stamp was made under record {there or 'none'} (frozen hash "
                         f"{r.get('frozen_sha256') or 'none'}), not {here} (frozen hash {frozen}): stamp and run the arms "
                         f"again under this record")
        if scorer_declared(rec):
            then = (st.get("scorer") or {}).get("sha256") if isinstance(st.get("scorer"), dict) else None
            if then != sc_now:
                probs.append(f"line 3: the scorer {rec['scorer']['file']} is not the one arm {arm} was stamped with "
                             f"(sha256 {(then or 'not recorded')[:16]} at stamp, {(sc_now or 'missing')[:16]} now); line 3 "
                             f"tests the scorer as it is now, not the one that scored: stamp the arms again and score them "
                             f"again with this scorer")
    return probs


def counted_problems(rec, stamps, l7, floors, means, arms, root, line3_ran, by_arm=None, path=None):
    """The counted gate: a real intended n and a declared primary.range, a scorer whose line-3 check ran and that
    scored the arms, every arm stamped under this record (path and frozen hash) against its line-6 hash, two distinct
    stamped pilot runs and line 7 holds, a floor with scored items sits under the best arm, the record not abandoned.
    A refusal by any line `check` runs, and violated_for_counted, also deny the label; the caller adds those."""
    probs = []
    if score_range(rec) is None:
        v = (rec.get("primary") or {}).get("range")
        probs.append(f"line 2: counted needs primary.range, [lo, hi], the scores the metric can take "
                     f"({'absent' if v is None else f'the record has {v!r}'}); declare it. primary is frozen at open, so "
                     f"a record opened without it needs a new record that declares it")
    if rec.get("status") == "abandoned":
        probs.append("the record's status is \"abandoned\": an abandoned record is never counted; start a new record")
    if len(arms) < 2:
        probs.append(f"counted needs at least two arms to compare; the record has {len(arms)} ({', '.join(arms)}); "
                     f"a single arm against the bar is not counted")
    if not real_n(rec.get("intended_n")):
        probs.append(f"line 2: counted needs a whole number intended_n; the record has {rec.get('intended_n', 'none')!r}")
    if not line3_ran:
        probs.append("line 3: counted needs a declared scorer (scorer.command, file, broken, good) whose check passes; none is declared")
    probs += pilot_gate(rec, root)
    if path is not None:
        probs += stamp_record_problems(rec, path, root, stamps)
    l6 = line6_part(rec)
    if rec.get("status") == "exploratory" or not l6 or (rec.get("opened") or {}).get("line6_sha256") != l6:
        probs.append("line 6: the record opened exploratory or without hashed line-6 fields (metric, comparison, smallest effect, unit)")
    for arm, st in stamps.items():
        r = st.get("record")
        if not stamp_counted(st) or not isinstance(r, dict) or r.get("line6_sha256") != l6:
            probs.append(f"line 6: counted needs every arm stamped --counted against this record's line-6 hash; {arm}'s stamp is not")
    if not line7_holds(l7, rec):
        if l7 is None:
            probs.append("line 7: no detectable difference from " +
                         ("a stamped pilot run" if noise_from_items(rec) else "two baseline pilot runs"))
        elif l7.get("problems"):
            probs += [f"line 7: {p}" for p in l7["problems"]]
        else:
            probs.append(f"line 7: detectable difference {l7['detectable']:.4f} exceeds the smallest effect {rec['primary']['smallest_effect']}")
    reason = (rec.get("floors") or {}).get("none_reason")
    if not floors and not reason:
        probs.append("line 12: no floor:<name> arm in items.jsonl and no floors.none_reason in the record")
    elif not floors and not (isinstance(reason, str) and len(reason.split()) >= 4):
        probs.append(f"line 12: no floor:<name> arm in items.jsonl, and floors.none_reason {reason!r} is not a reason; "
                     f"a reason is needed: a sentence of at least four words saying why no trivial policy can be scored, "
                     f"or score one as floor:<name>")
    for f in floors:
        if means.get(f) is None:
            n = len((by_arm or {}).get(f, []))
            probs.append(f"line 12: {f} has no scored item ({n} rows, none ok); a floor needs at least one scored item, "
                         f"and its mean is over scored items: fix the floor's run and score it again")
    hib = (rec.get("primary") or {}).get("higher_is_better", True)
    scored = [means[a] for a in arms if means.get(a) is not None and finite(means[a])]
    if scored:
        best = max(scored) if hib else min(scored)
        for f in floors:
            m = means[f]
            if m is not None and finite(m) and (m >= best if hib else m <= best):
                probs.append(f"line 12: {f} scores {fmt(m)}, reaching the best arm's {fmt(best)}")
    return probs


def finish(probs, ok_msg=None):
    for p in probs:
        print(f"refused: {p}", file=sys.stderr)
    if ok_msg and not probs:
        print(ok_msg)
    sys.exit(1 if probs else 0)


LEDGER = "runs.jsonl"


def command_text(argv):
    if not argv:
        return ""
    return argv[0] if len(argv) == 1 else shlex.join(argv)


def append_ledger(root, row):
    """Append one line to <root>/runs.jsonl in a single O_APPEND write, so concurrent writers never interleave
    within a line and nothing already written is ever rewritten."""
    line = (json.dumps({k: v for k, v in row.items() if v is not None}, ensure_ascii=False) + "\n").encode()
    fd = os.open(Path(root) / LEDGER, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, line)
    finally:
        os.close(fd)


def read_ledger(root):
    p = Path(root) / LEDGER
    out = []
    if p.is_file():
        for line in p.read_text().splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if isinstance(r, dict):
                out.append(r)
    return out


def ledger_root(cwd="."):
    return repo_root(cwd) or Path(cwd).resolve()


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
    rec["opened"] = {"utc": now(), "host": socket.gethostname(), "tool_version": VERSION, "frozen_sha256": frozen_part(rec),
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
        return [f for f in r.stdout.split("\0") if f and f != LEDGER
                and not (out_rel and (f == out_rel or f.startswith(out_rel + "/")))]
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
        # the run ledger is not code: it changes with every stamp, so it stays as HEAD has it
        keep = lambda f: f and f not in skip and f != LEDGER and not (out_rel and (f == out_rel or f.startswith(out_rel + "/")))
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


def stamp_counted(st):
    """Whether a stamp claims counted: its boolean `counted`, or, for a stamp written before the boolean existed,
    its label string ("counted" or "exploratory")."""
    st = st or {}
    return st["counted"] if isinstance(st.get("counted"), bool) else st.get("label") == "counted"


def opened_record(path):
    rec = load(path)
    if rec.get("schema") != 2:
        die(f"{path} has no schema: an old record; `induct` it, or write a new one with `new`")
    if not rec.get("opened"):
        die(f"{path} was never opened; `open` it before any run")
    if frozen_part(rec) != rec["opened"]["frozen_sha256"]:
        die(f"{path} changed after open; restore it or write a new record")
    return rec


UNCOUNTED = "stamp without --counted to run it uncounted"


def stamp_plan(a, rec):
    """[(folder, arm, under_record)]: one entry, or one per --arms name in OUT/<name>. With --record, every name is
    one of the record's arms, except names starting "floor", which are stamped as plain runs (line 12)."""
    if not a.arms:
        if rec is not None and a.arm not in rec.get("arms", {}):
            die(f"--arm must name one of the record's arms: {', '.join(rec.get('arms', {}))}")
        return [(Path(a.out_dir), a.arm, rec is not None)]
    if a.arm:
        die("give --arm or --arms, not both")
    names = [n.strip() for n in a.arms.split(",") if n.strip()]
    if not names or len(set(names)) < len(names):
        die(f"--arms {a.arms!r}: name each arm once, comma-separated")
    plan = []
    for n in names:
        folder, under = Path(a.out_dir) / n, rec is not None and not n.startswith("floor")
        if under:
            if n not in rec.get("arms", {}):
                die(f"--arms: {n} is not one of the record's arms ({', '.join(rec.get('arms', {}))}); a floor arm's "
                    f"name starts with \"floor\"")
            want = (rec_root(a.record) / rec["arms"][n]["out"]).resolve()
            if folder.resolve() != want:
                die(f"--arms writes {folder}, but the record's arm {n} has out {rec['arms'][n]['out']}: check would "
                    f"not find it; make the record's out folders <OUT>/<arm>")
        plan.append((folder, n, under))
    return plan


def do_stamp(a):
    """Stamp every folder in the plan (each checked before any is written) and append each to the run ledger.
    Returns [(folder, stamp)]."""
    argv = a.argv
    root = repo_root() or Path(".")
    rec = opened_record(a.record) if a.record else None
    plan = stamp_plan(a, rec)
    for folder, _, _ in plan:
        if (folder / "stamp.json").exists():
            held = (read_json(folder / "stamp.json") or {}).get("run_id")
            die(f"{folder / 'stamp.json'} exists{f' (run {held})' if held else ''}; a stamp is never overwritten: "
                f"launch into a new run folder with a new --run-id. To continue a run that crashed after writing "
                f"outputs, resume it with the harness's own command; its stamp and run id stand")
    # a folder freed by a failed launch (stamp.failed-<n>.json, no stamp.json) is retried as the same run, attempt n+1
    earlier = [(n, read_json(p) or {}) for folder, _, _ in plan for n, p in failed_stamps(folder)]
    attempt = max((n for n, _ in earlier), default=0) + 1
    retried = {st.get("launch_id") for _, st in earlier}
    if len(retried) > 1 or None in retried:
        die(f"the failed launches on file under {a.out_dir} are not attempts of one run "
            f"({', '.join(sorted(map(str, retried)))}): launch into a new run folder")
    retried = retried.pop() if retried else None
    if retried and a.run_id and a.run_id != retried:
        die(f"{a.out_dir} holds {attempt - 1} failed launch attempt(s) of run {retried}: retry it with --run-id "
            f"{retried} (or no --run-id), or launch {a.run_id} into a new run folder")
    tracker_id = a.run_id or next((st.get("tracker_run_id") for _, st in earlier if st.get("tracker_run_id") not in (None, NA)), None)
    if a.counted:
        if rec is None:
            die(f"line 6: --counted needs --record, an opened record whose line-6 fields were hashed; {UNCOUNTED}")
        l6 = line6_part(rec)
        if rec.get("status") == "exploratory" or not l6 or rec["opened"].get("line6_sha256") != l6:
            die(f"line 6: the record opened without hashed line-6 fields (metric, comparison, smallest effect, unit); "
                f"{UNCOUNTED}")
        for folder, _, under in plan:
            if under and (folder / "items.jsonl").is_file() and (folder / "items.jsonl").stat().st_size:
                die(f"{folder / 'items.jsonl'} already holds scored items: a counted stamp comes before scoring. "
                    f"Stamp a new, empty run folder")
        if len(rec.get("arms") or {}) < 2:
            die(f"counted needs at least two arms to compare; this record has one. {UNCOUNTED[0].upper()}{UNCOUNTED[1:]}")
        l7 = noise(rec, pilot_rows(rec, rec_root(a.record), []))
        if not line7_holds(l7, rec):
            die(line7_text(l7, rec) + f"; {UNCOUNTED}")
    rec_info, scorer = NA, NA
    if rec is not None:
        rec_info = {"path": a.record, "sha256": full_sha(a.record), "frozen_sha256": rec["opened"]["frozen_sha256"],
                    "line6_sha256": rec["opened"].get("line6_sha256", NA)}
        sc = scorer_sha(rec, rec_root(a.record))
        scorer = {"file": rec["scorer"]["file"], "sha256": sc} if sc else NA
    datas = {}
    for folder, arm, under in plan:
        data = check_data(rec["arms"][arm].get("data"), rec_root(a.record), arm) if under else []
        # each file once: a --data file the record already lists (or one given twice) is not added again
        seen = {(rec_root(a.record) / e["path"]).resolve() for e in data}
        for d in a.data or []:
            if Path(d).resolve() not in seen:
                seen.add(Path(d).resolve())
                data.append({"path": d, **data_facts(d)})
        datas[folder] = data
    launch_id = retried or a.run_id or f"{Path(a.out_dir).name}-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    config = NA
    if a.config:
        try:
            values = json.loads(Path(a.config).read_text())
        except ValueError:
            values = NA
        config = {"path": a.config, "sha256": full_sha(a.config), "values": values}
    snap = snapshot(root, Path(a.out_dir), launch_id) if repo_root() else NA
    done = []
    for folder, arm, under in plan:
        run_id = f"{launch_id}-{arm}" if a.arms else launch_id
        counted = bool(a.counted and under)
        stamp = {"schema": 2, "tool_version": VERSION, "run_id": run_id, "tracker_run_id": tracker_id or NA, "launch_id": launch_id, "utc": now(),
                 "host": socket.gethostname(), "argv": argv, "arm": arm or NA, "counted": counted,
                 "record": rec_info if under else NA,
                 "record_repo_path": repo_rel(a.record, rec_root(a.record)) if under else NA,
                 "scorer": scorer if under else NA, "config": config,
                 "model": {"id": a.model or NA, "revision": a.model_revision or NA,
                           "tokenizer_revision": a.tokenizer_revision or NA, "date": a.model_date or NA},
                 "data": datas[folder] or NA, "seeds": a.seed or NA, "packages": packages(a),
                 "lab_inputs_sha256": full_sha(root / "lab-inputs.md") if (root / "lab-inputs.md").is_file() else NA,
                 "snapshot": snap}
        if attempt > 1:      # absent on a first attempt: a stamp without it reads as attempt 1
            stamp["attempt"] = attempt
        folder.mkdir(parents=True, exist_ok=True)
        with open(folder / "stamp.json", "x") as f:
            f.write(json.dumps(stamp, indent=2) + "\n")
        append_ledger(root, {"kind": "run", "utc": stamp["utc"], "run_id": run_id, "counted": counted,
                             "command": command_text(argv), "record": stamp["record_repo_path"] if under else None,
                             "question": rec.get("question") if under else None,
                             "folder": repo_rel(str(folder), root), "launch_id": launch_id,
                             "attempt": attempt if attempt > 1 else None})
        print(f"stamped {folder} as {run_id} (counted: {str(counted).lower()})" +
              (f" at {snap['commit'][:8]}" if snap != NA else "") +
              (f", attempt {attempt} (attempt {attempt - 1} failed at launch)" if attempt > 1 else ""))
        done.append((folder, stamp))
    if snap == NA:
        print("warning: not a git repository: no snapshot of the code was taken", file=sys.stderr)
    return done


def cmd_stamp(a):
    do_stamp(a)


FAILED_STAMP = re.compile(r"stamp\.failed-(\d+)\.json")
TAIL_LINES, TAIL_BYTES = 5, 16384      # how much of the launch command's stderr a failed launch keeps
ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b[@-_]")


def failed_stamps(folder):
    """[(n, path)] for the stamp.failed-<n>.json files in a run folder: its launches that failed, oldest first."""
    folder = Path(folder)
    found = [(int(m[1]), p) for p in (folder.iterdir() if folder.is_dir() else []) if (m := FAILED_STAMP.fullmatch(p.name))]
    return sorted(found)


def attempt_of(st):
    a = (st or {}).get("attempt")
    return a if isinstance(a, int) and not isinstance(a, bool) and a > 1 else 1


def is_stamp_file(p, folder=None):
    return (folder is None or p.parent == Path(folder)) and (p.name == "stamp.json" or bool(FAILED_STAMP.fullmatch(p.name)))


def has_outputs(a, folders, since):
    """Whether the launch left anything behind. By default: any file in a run folder besides its stamps (items.jsonl
    included; empty directories are nothing). With --outputs: any file matching a glob, read against OUT, written
    since the launch began (so outputs kept in a shared folder count only when this launch wrote them)."""
    if a.outputs:
        for g in a.outputs:
            for m in glob.glob(os.path.join(a.out_dir, g), recursive=True):
                p = Path(m)
                if p.is_file() and not is_stamp_file(p) and p.stat().st_mtime >= since - 2:
                    return True
        return False
    for folder in folders:
        for p in Path(folder).rglob("*"):
            if not p.is_dir() and not is_stamp_file(p, folder) and p.name != ".DS_Store":
                return True
    return False


def run_streaming(argv):
    """Run the launch command with this process's stdin and stdout. Its stderr is copied on as it arrives, through a
    pseudo-terminal when ours is a terminal (so progress bars and colors stay) and a pipe otherwise, and the last of
    it is kept. Returns (exit code, the last few stderr lines). A command given as one string is run by the shell."""
    shell = len(argv) == 1
    master = slave = None
    try:
        if sys.stderr.isatty():
            import fcntl, pty, termios
            master, slave = pty.openpty()
            try:      # our terminal's size, and no newline translation of its own: the real terminal does that
                fcntl.ioctl(slave, termios.TIOCSWINSZ, fcntl.ioctl(sys.stderr.fileno(), termios.TIOCGWINSZ, b"\0" * 8))
                attrs = termios.tcgetattr(slave)
                attrs[1] &= ~termios.OPOST
                termios.tcsetattr(slave, termios.TCSANOW, attrs)
            except (OSError, termios.error):
                pass
    except (ImportError, OSError, ValueError):      # no pty here: a pipe does
        master = slave = None
    try:
        p = subprocess.Popen(argv[0] if shell else argv, shell=shell, stderr=subprocess.PIPE if slave is None else slave)
    except OSError as e:
        for fd in (master, slave):
            if fd is not None:
                os.close(fd)
        msg = f"prereg.py run: could not start {argv[0]}: {e}"
        print(msg, file=sys.stderr)
        return 127, [msg]
    if slave is not None:
        os.close(slave)
    fd, kept = (p.stderr.fileno() if master is None else master), bytearray()
    def pump():
        while True:
            try:
                chunk = os.read(fd, 65536)
            except OSError:      # a pty reads as an error once the command has closed it
                return
            if not chunk:
                return
            try:
                if hasattr(sys.stderr, "buffer"):
                    sys.stderr.buffer.write(chunk)
                else:
                    sys.stderr.write(chunk.decode("utf-8", "replace"))
                sys.stderr.flush()
            except (OSError, ValueError):
                pass
            kept.extend(chunk)
            del kept[:-TAIL_BYTES]
    t = threading.Thread(target=pump, daemon=True)
    t.start()
    try:
        rc = p.wait()
    except KeyboardInterrupt:
        try:
            p.wait(timeout=0.25)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
        rc = 130
    t.join(timeout=5)      # a child that outlives the command may hold stderr open: do not wait for it
    if master is not None:
        os.close(master)
    lines = [l.rstrip()[:300] for l in re.split(r"[\r\n]+", ANSI.sub("", bytes(kept).decode("utf-8", "replace")))]
    return rc, [l for l in lines if l.strip()][-TAIL_LINES:]


def free_failed_launch(root, done, rc):
    """A launch that failed before writing anything is an attempt, not a run: keep its snapshot under
    <ref>.failed-<n> (freeing the run id's ref) and its stamp as stamp.failed-<n>.json (freeing the folder), so the
    same command retries the same run id. Returns False, changing nothing, when the snapshot ref cannot be moved."""
    snap, n = done[0][1].get("snapshot"), attempt_of(done[0][1])
    kept_ref = None
    if isinstance(snap, dict):
        kept_ref = f"{snap['ref']}.failed-{n}"
        if sh("git", "update-ref", kept_ref, snap["commit"], "0" * 40, cwd=root) is None:
            return False
        if sh("git", "update-ref", "-d", snap["ref"], snap["commit"], cwd=root) is None:
            sh("git", "update-ref", "-d", kept_ref, snap["commit"], cwd=root)
            return False
    for folder, st in done:
        st = {**st, "launch_failed": {"utc": now(), "exit_code": rc}}
        if kept_ref:
            st["snapshot"] = {**snap, "ref": kept_ref}
        with open(folder / f"stamp.failed-{n}.json", "x") as f:
            f.write(json.dumps(st, indent=2) + "\n")
        (folder / "stamp.json").unlink()
    return True


def cmd_run(a):
    """Stamp, then run the command with this process's stdin, stdout and stderr; exit with its exit code. A non-zero
    exit that left no outputs is a failed launch: recorded in the ledger with the end of its stderr, and the folder
    and run id are freed for a retry. A non-zero exit with outputs is a failed run: its stamp stands."""
    if not a.argv:
        die("run needs a command after --")
    began = time.time()
    done = do_stamp(a)
    sys.stdout.flush()
    rc, tail = run_streaming(a.argv)
    root = repo_root() or Path(".")
    failed = rc != 0 and not has_outputs(a, [folder for folder, _ in done], began) and free_failed_launch(root, done, rc)
    n = attempt_of(done[0][1])
    for _, st in done:
        append_ledger(root, {"kind": "exit", "utc": now(), "run_id": st["run_id"], "exit_code": rc,
                             **({"launch_failed": True, "attempt": n, "stderr_tail": tail} if failed else {})})
    if failed:
        sys.stdout.flush()
        print(f"prereg.py run: launch failed (exit {rc}), nothing scored; rerun the same command to retry as attempt {n + 1}",
              file=sys.stderr)
    sys.exit(rc)


def load_stamp(folder):
    p = Path(folder) / "stamp.json"
    return load(p) if p.is_file() else None


def failed_hint(folder):
    n = len(failed_stamps(folder))
    return f" ({n} launch attempt(s) failed here and nothing was scored: rerun the launch command to retry)" if n else ""


def cmd_check(a):
    probs = []
    if len(a.sources) == 1 and Path(a.sources[0]).is_file():
        return check_record(a.sources[0])
    by_arm, ids = {}, []
    for src in a.sources:
        st = load_stamp(src)
        if st is None:
            probs.append(f"line 10: {src} has no stamp.json; stamp the run at launch (`prereg.py stamp {src} -- <command>`)"
                         + failed_hint(src))
            continue
        print(f"run {st['run_id']}: {src}" + (f" (attempt {attempt_of(st)})" if attempt_of(st) > 1 else ""))
        for r in read_items(src, probs):
            by_arm.setdefault(r["arm"], []).append(r)
    arms = [x for x in by_arm if not str(x).startswith("floor:")]
    hint = ("; each folder given is one run, so ids repeat across them: check each run folder on its own"
            if len(a.sources) > 1 else "")
    line2(by_arm, arms, None, {}, probs, hint)
    print("line 3: no record, so no scorer declared; not checked")
    line12(by_arm, arms, None)
    print("counted: false (run folders without a record are never counted)")
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
                probs.append(f"line 10: arm {arm} has no stamp.json in {folder}; stamp each run at launch"
                             + failed_hint(root / folder))
            else:
                stamps[arm] = st
                print(f"run {st['run_id']}: {arm} (stamped counted: {str(stamp_counted(st)).lower()}"
                      + (f"; attempt {attempt_of(st)}" if attempt_of(st) > 1 else "") + ")")
        for r in read_items(root / folder, probs, score_range(rec)):
            if r["arm"] not in rec["arms"] and not str(r["arm"]).startswith("floor:"):
                probs.append(f"line 2: {folder}/items.jsonl names arm {r['arm']!r}, neither a record arm nor floor:<name>")
                continue
            by_arm.setdefault(r["arm"], []).append(r)
    result = {"utc": now(), "tool_version": VERSION, "record_frozen_sha256": rec["opened"]["frozen_sha256"]}
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
    probs += data_drift(rec, root)
    runs = pilot_rows(rec, root, probs)
    l7 = noise(rec, runs, {str(r["unit"]) for r in by_arm.get(arms[0], [])} if arms else set(), arms[0] if arms else None)
    if l7 and l7.get("deterministic") and not l7["differing_items"]:
        l7["problems"] += deterministic_seed_problems([load_stamp(root / f) for f in pilot_folders(rec, root)], stamps)
    result["line7"] = l7
    print(line7_text(l7, rec))
    if declared_deterministic(rec):
        print(f"warning: line 7 rests on the pilot.deterministic declaration ({declared_deterministic(rec)}), not on "
              f"measured run-to-run noise; if the harness has any randomness, the declaration is false")
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
    print_after_open(rec)
    gate_ok = False
    line_refusals = list(probs)
    if any(stamp_counted(st) for st in stamps.values()):
        line3_ran = isinstance(result["line3"], dict) and "scorer_sha256" in result["line3"]
        probs += violated_for_counted(rec, by_arm, arms, floors, means)
        line_refusals = list(probs)
        cp = counted_problems(rec, {a: stamps.get(a, {}) for a in arms}, l7, floors, means, arms, root, line3_ran, by_arm,
                              path=path)
        earlier = len(probs)
        probs += [f"{p} (counted refused; the run stands, not counted)" for p in cp]
        gate_ok = not probs
        if not gate_ok:
            print(f"counted refused: {len(cp)} counted-gate requirement(s) unmet and {earlier} other refusal(s); each is listed on stderr")
    pending = parity_problem(path, rec, root, inputs) if gate_ok else None
    det = declared_deterministic(rec) if gate_ok and l7 and l7.get("deterministic") else None
    # line_refusals: lines violated (quote and close refuse while any stands); refusals: those plus the counted gate's
    result.update(counted=gate_ok and not pending, pending_parity=bool(pending), deterministic=det, refusals=probs,
                  line_refusals=line_refusals, inputs=inputs)
    result["verdict_sha256"] = verdict_sha(result)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(counted_line(result, pending))
    finish(probs)


def counted_line(res, pending=None):
    if res["counted"]:
        return "counted: true" + (" (deterministic harness declared)" if res.get("deterministic") else "")
    return "counted: false" + (f" (pending parity: {pending})" if res.get("pending_parity") else "")


def print_after_open(rec):
    """Harness fixes landed after open (record field after_open): each printed, so a reader sees them."""
    ao = rec.get("after_open")
    if not ao:
        return
    entries = ao if isinstance(ao, list) else [ao]
    print(f"after open: {len(entries)} change(s) landed after the record was opened:")
    for e in entries:
        if isinstance(e, dict):
            print(f"  {e.get('commit') or '(no commit named)'}: {e.get('change') or e.get('note') or json.dumps(e)}")
        else:
            print(f"  {e}")


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
    problems += data_drift(rec, root)
    names = list(stamps)
    skip = [spec["out"] for spec in rec["arms"].values()] + list((rec.get("pilot") or {}).get("runs") or []) + \
        list((rec.get("floors") or {}).get("runs") or []) + [LEDGER]
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
    if check and check_gate_passed(check) and not changed_inputs(check.get("inputs"), inputs) \
            and check.get("verdict_sha256") == verdict_sha(check):
        new = {"counted": not problems, "pending_parity": bool(problems)}
        if "label" in check:      # a check.json written before the boolean: rewritten in the new form
            det = declared_deterministic(rec) if DET_LABEL in check["label"] else None
            check = {k: v for k, v in check.items() if k != "label"}
            check["deterministic"] = det
        if any(check.get(k) != v for k, v in new.items()) or "verdict_sha256" not in check:
            check.update(new)
            check["verdict_sha256"] = verdict_sha(check)
            cp.write_text(json.dumps(check, indent=2) + "\n")
            print(f"check now: {counted_line(check)} ({cp})")
    sys.exit(1 if problems else 0)


def parity_path(path):
    return Path(path).with_suffix(".parity.json")


PENDING = "counted, pending parity"      # the label an older check.json gave a run that passed all but parity


def check_gate_passed(check):
    """Whether check.json says the counted gate passed (parity aside): its counted or pending_parity boolean, or,
    in a file written before the boolean, a label starting "counted"."""
    if isinstance(check.get("counted"), bool):
        return check["counted"] or bool(check.get("pending_parity"))
    return str(check.get("label", "")).startswith("counted")
CLOSE_FIELDS = ("observed", "closed", "status")      # what `close` writes into the record after check and parity


def judged_folders(rec):
    return [spec["out"] for spec in (rec.get("arms") or {}).values()] + \
        list((rec.get("pilot") or {}).get("runs") or []) + list((rec.get("floors") or {}).get("runs") or [])


def data_path(root, path):
    return Path(path) if os.path.isabs(path) else root / path


def declared_data(rec, root):
    """(who, path, recorded sha256) for every data file the record's arms list and every judged stamp recorded."""
    out = []
    for arm, spec in (rec.get("arms") or {}).items():
        entries = spec.get("data") if isinstance(spec, dict) else None
        for e in entries if isinstance(entries, list) else []:
            e = {"path": e} if isinstance(e, str) else e
            if isinstance(e, dict) and isinstance(e.get("path"), str):
                out.append((f"the record (arm {arm})", e["path"], e.get("sha256")))
    for f in judged_folders(rec):
        st = load_stamp(root / f)
        for e in (st or {}).get("data") if isinstance((st or {}).get("data"), list) else []:
            if isinstance(e, dict) and isinstance(e.get("path"), str):
                out.append((f"the stamp in {f}", e["path"], e.get("sha256")))
    return out


def data_drift(rec, root):
    """Line 13 after launch: each data file the record or a stamp recorded, rehashed now; a difference is refused."""
    probs, now_sha = [], {}
    for who, path, recorded in declared_data(rec, root):
        p = data_path(root, path)
        if p not in now_sha:
            now_sha[p] = full_sha(p) if p.is_file() else None
        if now_sha[p] is None:
            probs.append(f"line 13: data file {path}, recorded by {who}, is missing; restore it")
        elif recorded and now_sha[p] != recorded:
            probs.append(f"line 13: data file {path} changed after {who} recorded it (sha256 {recorded[:16]}, now "
                         f"{now_sha[p][:16]}); restore it, or rerun on the new data in new run folders under a new record")
    return probs


def judged_inputs(rec, root):
    """sha256 of what check and parity judge: the record (less what close writes); for every arm, pilot and floor
    run folder, its items.jsonl and stamp.json ("absent" when missing); every data file the record or those stamps
    list; the declared scorer file. Stored in check.json and parity.json; quote and close recompute it. A plain hash:
    it catches stale or copied results, not a forger who recomputes it."""
    out = {"record": hashlib.sha256(json.dumps({k: v for k, v in rec.items() if k not in CLOSE_FIELDS},
                                               sort_keys=True).encode()).hexdigest()}
    for f in judged_folders(rec):
        for name in ("items.jsonl", "stamp.json"):
            p = root / f / name
            out[f"{os.path.normpath(f)}/{name}"] = full_sha(p) if p.is_file() else "absent"
    for _, path, _ in declared_data(rec, root):
        p = data_path(root, path)
        out[f"data:{os.path.normpath(path)}"] = full_sha(p) if p.is_file() else "absent"
    if scorer_declared(rec):
        out[f"scorer:{os.path.normpath(rec['scorer']['file'])}"] = scorer_sha(rec, root) or "absent"
    return out


def verdict_sha(check):
    """Hash of check.json's verdict: counted (or, in a file written before the boolean, its label) and line refusals
    with the judged-file hashes. quote and close recompute it, so a hand-edited verdict or refusal list is refused.
    Not forgery-proof: anyone can recompute it."""
    keys = ("label",) if "label" in check else ("counted", "pending_parity", "deterministic")
    keep = {k: check.get(k) for k in keys + ("line_refusals", "inputs")}
    return hashlib.sha256(json.dumps(keep, sort_keys=True).encode()).hexdigest()


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
    """(refusals, counted now). A schema-2 record, counted or not, is quoted or closed only while check.json is on
    file, hashes the files as they are now, carries its own verdict hash, and records no violated line; and, if its
    counted gate passed, a passing parity.json is current too. Counted is true only when all of that holds. An unmet
    counted gate alone (power, pilots, floors) leaves a quotable result that is not counted."""
    cp = Path(path).with_suffix(".check.json")
    check = read_json(cp)
    claimed = any(stamp_counted(load_stamp(root / spec["out"])) for spec in rec["arms"].values())
    inputs = judged_inputs(rec, root)
    if check is None:
        return [(f"line 13: {path} has arms stamped counted but no check result on file ({cp}); "
                 f"run `prereg.py check {path}`, then `prereg.py parity {path}`") if claimed else
                (f"no check result on file for {path} ({cp}): run `prereg.py check {path}`; its numbers are quoted "
                 f"or closed only after check refuses no line")], False
    probs = []
    diff = changed_inputs(check.get("inputs"), inputs)
    if diff:
        probs.append(f"{cp} is stale: {stale_why(check, diff)} since check ran; rerun `prereg.py check {path}` "
                     f"and `prereg.py parity {path}`")
    if check.get("verdict_sha256") != verdict_sha(check):
        probs.append(f"{cp}: its verdict (counted, line refusals, file hashes) does not match its verdict hash: the file "
                     f"was edited by hand or written by an older prereg.py; rerun `prereg.py check {path}`")
    lines = check.get("line_refusals")
    if lines:
        probs += [f"check refused this line, so nothing from {path} is quoted or closed until it is fixed and "
                  f"`prereg.py check {path}` passes it: {p}" for p in lines]
    passed = check_gate_passed(check)
    if passed:
        if rec.get("status") == "abandoned":
            probs.append(f"{path} is abandoned but {cp} says counted; rerun `prereg.py check {path}`")
        p = parity_problem(path, rec, root, inputs)
        if p:
            probs.append(p)
    return probs, passed and not probs


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
    gate, counted = result_gate(a.path, rec, root)
    if gate:
        finish(gate)
    for arm, spec in rec["arms"].items():
        rows = [r for r in read_items(root / spec["out"], probs, score_range(rec)) if r["arm"] == arm]
        observed[arm] = {"n": len(rows), "mean": mean_ok(rows)}
        print(f"  {arm:<12} n {len(rows)}  mean {fmt(observed[arm]['mean'])}")
    if probs:
        finish(probs)
    rec["observed"] = observed
    rec["closed"] = {"utc": now(), "hits": 0, "predictions": 0, "note": a.note or ""}
    if rec["status"] not in ("exploratory", "abandoned"):      # an abandoned record stays abandoned
        rec["status"] = "closed"
    save(a.path, rec)
    run_ids = [(load_stamp(root / spec["out"]) or {}).get("run_id") for spec in rec["arms"].values()]
    append_ledger(root, {"kind": "close", "utc": rec["closed"]["utc"], "record": repo_rel(a.path, root),
                         "question": rec.get("question"), "run_ids": [r for r in run_ids if r], "counted": counted,
                         "result": "; ".join(f"{arm} n {o['n']} mean {fmt(o['mean'])}" for arm, o in observed.items())
                                   + (f" ({a.note})" if a.note else "")})
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


COUNTED_WORD = re.compile(r"(?<![Nn]ot )\bcounted\b", re.IGNORECASE)      # "not counted" is always allowed


def cmd_quote(a):
    ids, gate, counted, old = set(), [], [], False
    for src in a.sources:
        p = Path(src)
        if p.is_dir():
            ids |= stamp_ids(p)
            counted.append(False)
            if stamp_counted(load_stamp(p)):
                gate.append(f"{src} carries a counted stamp: quote it through its record (`prereg.py quote {a.report} "
                            f"<record>`), which requires a current check and parity; a run folder alone is not counted")
            continue
        rec, root = load(p), rec_root(p)
        if rec.get("schema") == 2:
            g, c = result_gate(src, rec, root)
            gate += g
            counted.append(c)
        else:
            old = True      # an old record is quoted exactly as before: no verdict to compare the word with
        for spec in (rec.get("arms") or {}).values():
            ids |= stamp_ids(root / spec["out"])
        for f in list((rec.get("pilot") or {}).get("runs") or []) + list((rec.get("floors") or {}).get("runs") or []):
            ids |= stamp_ids(root / f)
        lp = ledger_path(p)
        if lp.is_file():
            ids |= {json.loads(l).get("run_id") for l in lp.read_text().splitlines() if l.strip()}
    ids = {str(i) for i in ids if i and i != NA}
    pat = id_pattern(ids)
    text = Path(a.report).read_text().splitlines()
    bad = [(k, l) for k, l in enumerate(text, 1) if NUMBER.search(l) and not (pat and pat.search(l))]
    for k, l in bad:
        print(f"refused: line 10: {a.report}:{k} quotes a number with no run id: {l.strip()}", file=sys.stderr)
    if not old and not all(counted):
        for k, l in enumerate(text, 1):
            if COUNTED_WORD.search(l):
                gate.append(f"{a.report}:{k} says counted, but the run is not counted ({', '.join(a.sources)}): "
                            f"say it is not counted, or earn counted (check passes, then parity): {l.strip()}")
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


def stamp_args(s):
    s.add_argument("out_dir", help="the run folder; with --arms, the parent of one folder per arm")
    s.add_argument("--record", help="the opened schema-2 record this run belongs to")
    s.add_argument("--arm", help="which of the record's arms this run is")
    s.add_argument("--arms", help="comma-separated arms one command writes, each into OUT/<arm>; names starting "
                                  "\"floor\" are stamped as plain runs")
    s.add_argument("--counted", action="store_true", help="claim counted (refused unless lines 6 and 7 hold)")
    s.add_argument("--run-id", help="the tracker's run id (MLflow, W&B, Inspect log); default: folder name + time")
    s.add_argument("--config", help="the effective configuration file (JSON is stored whole)")
    s.add_argument("--model"); s.add_argument("--model-revision"); s.add_argument("--tokenizer-revision")
    s.add_argument("--model-date", help="for an API model: the date the resolved model id was read")
    s.add_argument("--data", action="append", help="a data file read by the run (repeatable)")
    s.add_argument("--seed", action="append", help="a seed (repeatable)")
    s.add_argument("--image", help="image digest; else the running interpreter's package list is recorded")


def main(argv=None):
    os.environ["GIT_OPTIONAL_LOCKS"] = "0"      # read-only git calls never rewrite the user's index
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"prereg.py {VERSION}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("new", "open", "parity", "induct"):
        sub.add_parser(name).add_argument("path")
    for name in ("stamp", "run"):
        sp = sub.add_parser(name)
        stamp_args(sp)
        if name == "run":
            sp.add_argument("--outputs", action="append", metavar="GLOB",
                            help="what counts as output when the command exits non-zero: a file matching GLOB (read "
                                 "against OUT; repeatable) written since launch. Default: any file in the run folder "
                                 "besides its stamp. No output means a failed launch, and the folder is freed for a retry")
    n = sub.add_parser("note")
    n.add_argument("run_id"); n.add_argument("finding")
    n.add_argument("--changes", help="what the finding changed: a decision, a plan, a later run")
    b = sub.add_parser("backfill")
    b.add_argument("dir")
    c = sub.add_parser("check")
    c.add_argument("sources", nargs="+", help="a schema-2 record, or one or more run folders (never counted)")
    c = sub.add_parser("close")
    c.add_argument("path")
    c.add_argument("--note")
    l = sub.add_parser("ledger")
    l.add_argument("path"); l.add_argument("run_dir")
    q = sub.add_parser("quote")
    q.add_argument("report"); q.add_argument("sources", nargs="+")
    l = sub.add_parser("ls")
    l.add_argument("query", nargs="?", help="a search string over runs.jsonl; or a directory of records (as before)")
    l.add_argument("--limit", type=int, default=30)
    argv = list(sys.argv[1:] if argv is None else argv)
    launch = []
    if argv[:1] in (["stamp"], ["run"]) and "--" in argv:      # everything after -- is the launch command, options included
        k = argv.index("--")
        argv, launch = argv[:k], argv[k + 1:]
    a = ap.parse_args(argv)
    a.argv = launch
    try:
        {"new": cmd_new, "open": cmd_open, "stamp": cmd_stamp, "parity": cmd_parity, "close": cmd_close, "ls": cmd_ls,
         "check": cmd_check, "ledger": cmd_ledger, "quote": cmd_quote, "induct": cmd_induct, "run": cmd_run,
         "note": cmd_note, "backfill": cmd_backfill}[a.cmd](a)
    except subprocess.CalledProcessError as e:      # an unexpected git failure: one line with git's own message
        cmd = e.cmd if isinstance(e.cmd, (list, tuple)) else [str(e.cmd)]
        msg = [l.strip() for l in (e.stderr or e.stdout or "").splitlines() if l.strip() and not l.startswith("hint:")]
        die(f"{' '.join(map(str, cmd[:2]))} failed (exit {e.returncode}): {'; '.join(msg) or 'no message'}")


if __name__ == "__main__":
    main()
