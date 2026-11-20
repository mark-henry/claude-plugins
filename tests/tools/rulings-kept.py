#!/usr/bin/env python3
"""Did every rulings.md line the fixture wrote survive the run unchanged?

usage: rulings-kept.py [--tests tests] [--rev <git rev>] <kept dir> [...]

Each <kept dir> is searched for run folders `<case>/<arm>-<i>/workspace/` (keep.py's layout,
`<kept>/<result stem>/<case>/<arm>-<i>/`). For each run, the case's fixture.sh is run in a
scratch folder to get the rulings.md file(s) it wrote under run/; every non-blank line of each
must still be in the run's final file of the same path, unchanged and in the same order
(new lines may sit anywhere between them). afk:interview records rulings only by appending
(`afk-ruling`), so a run that overwrote, rewrote or re-dated a fixture line is red.

--rev reads fixture.sh from that git revision instead of the working tree: use the revision
the runs were made at, or every changed fixture line reads as lost.

Prints one row per run: green (k/k kept, and how many lines were added), red (the first lost
line), or none (the fixture writes no rulings.md). Exits 1 if any run is red.
"""
import argparse, glob, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_cache = {}


def fixture_rulings(tests, case, rev):
    """{relative path: text} of every rulings.md the case's fixture writes under run/."""
    key = (case, rev)
    if key in _cache:
        return _cache[key]
    if rev:
        rel = os.path.relpath(os.path.join(tests, case, "fixture.sh"), ROOT)
        src = subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{rel}"], capture_output=True, text=True)
        if src.returncode:
            _cache[key] = None
            return None
        script = src.stdout
    else:
        p = os.path.join(tests, case, "fixture.sh")
        if not os.path.exists(p):
            _cache[key] = None
            return None
        script = open(p).read()
    out = {}
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["bash", "-c", script], cwd=d, capture_output=True, text=True)
        for f in glob.glob(os.path.join(d, "run", "**", "rulings.md"), recursive=True):
            out[os.path.relpath(f, d)] = open(f, errors="replace").read()
    _cache[key] = out
    return out


def check(orig, final):
    """(kept, total, first lost line or None, lines added)"""
    want = [l for l in orig.splitlines() if l.strip()]
    have = final.splitlines()
    i = 0
    for l in have:
        if i < len(want) and l == want[i]:
            i += 1
    added = len([l for l in have if l.strip()]) - i
    return i, len(want), (want[i] if i < len(want) else None), added


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tests", default=os.path.join(ROOT, "tests"))
    ap.add_argument("--rev")
    ap.add_argument("kept", nargs="+")
    a = ap.parse_args()
    red = 0
    runs = sorted({os.path.dirname(w) for k in a.kept for w in glob.glob(os.path.join(k, "**", "workspace"), recursive=True)})
    for run in runs:
        case = os.path.basename(os.path.dirname(run))
        name = f"{case}/{os.path.basename(run)}"
        fx = fixture_rulings(a.tests, case, a.rev)
        if not fx:
            print(f"none   {name}")
            continue
        for rel, orig in sorted(fx.items()):
            p = os.path.join(run, "workspace", rel)
            final = open(p, errors="replace").read() if os.path.exists(p) else ""
            k, n, lost, added = check(orig, final)
            if lost is None:
                print(f"green  {name}  {rel}: {k}/{n} fixture lines kept, {added} added")
            else:
                red += 1
                what = "file missing" if not os.path.exists(p) else f"first lost: {lost[:100]!r}"
                print(f"red    {name}  {rel}: {k}/{n} kept, {what}")
    sys.exit(1 if red else 0)


if __name__ == "__main__":
    main()
