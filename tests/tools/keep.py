#!/usr/bin/env python3
"""Copy every run's kept folder (trace and workspace) out of the harness's temp area.

usage: keep.py --kept <dir> <result.json> [...]

Run it right after each `claude plugin eval ... --keep-temp --json <result.json>`.
The harness seals the workspace under <kept>/sealed (mode 000); this opens it, copies
`sealed/home/cwd` to <dir>/<result stem>/<case>/<arm>-<index>/workspace and `out/` beside it.
It never runs git inside a kept folder.
"""
import argparse, json, os, shutil, stat, sys

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--kept", required=True); ap.add_argument("results", nargs="+")
    a = ap.parse_args(); n = 0
    for rf in a.results:
        d = json.load(open(rf)); stem = os.path.splitext(os.path.basename(rf))[0]
        for case in d.get("cases", []):
            name = case.get("name") or case.get("id")
            for arm, runs in (case.get("arms") or {}).items():
                for i, run in enumerate(runs):
                    tp = run.get("tracePath")
                    if not tp or not os.path.exists(tp):
                        print(f"missing trace: {name} {arm}-{i}", file=sys.stderr); continue
                    base = os.path.dirname(os.path.dirname(tp)); dst = os.path.join(a.kept, stem, name, f"{arm}-{i}")
                    os.makedirs(dst, exist_ok=True)
                    shutil.copytree(os.path.join(base, "out"), os.path.join(dst, "out"), dirs_exist_ok=True)
                    sealed = os.path.join(base, "sealed")
                    for p in (base, sealed):
                        if os.path.isdir(p): os.chmod(p, stat.S_IRWXU)
                    ws = os.path.join(sealed, "home", "cwd")
                    if os.path.isdir(ws):
                        shutil.copytree(ws, os.path.join(dst, "workspace"), symlinks=True, dirs_exist_ok=True)
                    n += 1
    print(f"kept {n} runs")

if __name__ == "__main__":
    main()
