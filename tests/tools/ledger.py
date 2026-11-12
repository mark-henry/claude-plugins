#!/usr/bin/env python3
"""Per-run token counts by model, from kept traces, plus the harness's weighted figure.

usage: ledger.py --kept <dir> <result.json> [...]

Reads the last `result` record of each kept trace; its `modelUsage` covers the whole
session, helpers included. Prints one row per run and model, then totals per model.
"""
import argparse, collections, json, os, sys

def usage(trace):
    last = None
    try:
        for line in open(trace, errors="replace"):
            try: o = json.loads(line)
            except ValueError: continue
            if isinstance(o, dict) and o.get("type") == "result": last = o
    except OSError:
        return None
    return (last or {}).get("modelUsage")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--kept", required=True); ap.add_argument("results", nargs="+")
    a = ap.parse_args(); rows = []; tot = collections.defaultdict(lambda: collections.Counter())
    for rf in a.results:
        d = json.load(open(rf)); stem = os.path.splitext(os.path.basename(rf))[0]
        for case in d.get("cases", []):
            name = case.get("name") or case.get("id")
            for arm, runs in (case.get("arms") or {}).items():
                for i, run in enumerate(runs):
                    mu = usage(os.path.join(a.kept, stem, name, f"{arm}-{i}", "out", "trace.jsonl"))
                    if mu is None:
                        rows.append({"result": stem, "case": name, "arm": arm, "run": i, "model": None,
                                     "weighted": run.get("costUsd"), "note": "no usage record"}); continue
                    for model, u in mu.items():
                        r = {"result": stem, "case": name, "arm": arm, "run": i, "model": model,
                             "input": u.get("inputTokens", 0), "output": u.get("outputTokens", 0),
                             "cache_read": u.get("cacheReadInputTokens", 0),
                             "cache_write": u.get("cacheCreationInputTokens", 0), "weighted": u.get("costUSD", 0)}
                        rows.append(r)
                        for k in ("input", "output", "cache_read", "cache_write", "weighted"): tot[model][k] += r[k]
                        tot[model]["runs"] += 1
    json.dump({"rows": rows, "totals": {m: dict(c) for m, c in tot.items()}}, sys.stdout, indent=1); print()

if __name__ == "__main__":
    main()
