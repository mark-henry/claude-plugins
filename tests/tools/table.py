#!/usr/bin/env python3
"""Build the results table from verdict rows.

usage: table.py --rows <verdicts.json> --kept <dir> --tests <tests dir>
                [--skip <stem> ...] [--readings <readings.json>] > results.md

--rows is the output of verdicts.py. --skip leaves out result files that predate a
case's current form. --readings is a JSON list of {"result", "case", "arm", "run",
"verdict", "note"}: a reader's verdict for one run, which replaces the script's
("broken?" stays unconfirmed, and is shown as such, until a reader rules).
Counts are runs. Twins report acted over runs. The process column reads the kept
workspace: run/plan.md, run/plan.attack.md (or a Skill call for check:attack), run/report.md.
"""
import argparse, collections, json, os

ORDER = ["haiku", "sonnet", "opus", "fable"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True); ap.add_argument("--kept", required=True)
    ap.add_argument("--tests", required=True); ap.add_argument("--skip", nargs="*", default=[])
    ap.add_argument("--readings")
    a = ap.parse_args()
    rows = [r for r in json.load(open(a.rows)) if r["result"] not in a.skip and r.get("kind")]
    readings = {(x["result"], x["case"], x["arm"], x["run"]): x for x in (json.load(open(a.readings)) if a.readings else [])}
    cell = collections.defaultdict(collections.Counter); proc = collections.defaultdict(collections.Counter)
    info = {}; notes = []
    for r in rows:
        k = (r["result"], r["case"], r["arm"], r["run"]); v = r["verdict"]
        if k in readings:
            notes.append(f"- `{r['case']}`, {r['model']}, {'with the plugin' if r['arm']=='with' else 'bare model'}, run `{r['result']}/{r['arm']}-{r['run']}`: script said {v}, reader says {readings[k]['verdict']}. {readings[k]['note']}")
            v = readings[k]["verdict"]
        elif v == "broken?":
            v = "broken (unread)"
        key = (r["case"], r["model"], r["arm"]); cell[key][v] += 1
        info[r["case"]] = (r.get("clause"), r["kind"])
        ws = os.path.join(a.kept, r["result"], r["case"], f"{r['arm']}-{r['run']}", "workspace", "run")
        p = proc[key]; p["n"] += 1
        p["plan"] += os.path.exists(os.path.join(ws, "plan.md"))
        p["attack"] += os.path.exists(os.path.join(ws, "plan.attack.md")) or bool(r["graders"].get("plan-attacked"))
        p["report"] += os.path.exists(os.path.join(ws, "report.md"))
    def fmt(key):
        c = cell.get(key)
        if not c: return "not run"
        n = sum(c.values()); kind = info[key[0]][1]
        if kind == "twin":
            s = f"acted {c.get('acted', 0)} of {n}"
        else:
            s = f"held {c.get('held', 0)} of {n}"
            for name in ("broken", "broken (unread)"):
                if c.get(name): s += f", **{name} {c[name]}**"
        for name in ("incomplete", "errored"):
            if c.get(name): s += f", {name} {c[name]}"
        return s
    def pfmt(key):
        p = proc.get(key)
        return f"{p['plan']}/{p['attack']}/{p['report']} of {p['n']}" if p else ""
    print("| Clause | Case | Kind | " + " | ".join(m.capitalize() for m in ORDER) + " | Bare Sonnet | Process on Sonnet (plan/attack/report) |")
    print("|---|---|---|" + "---|" * (len(ORDER) + 2))
    for case in sorted(info, key=lambda c: (info[c][0] or "", c)):
        clause, kind = info[case]
        print(f"| {clause} | `{case}` | {kind} | " + " | ".join(fmt((case, m, "with")) for m in ORDER)
              + f" | {fmt((case, 'sonnet', 'without'))} | {pfmt((case, 'sonnet', 'with'))} |")
    print(f"\nRuns counted: {len(rows)}.")
    if notes:
        print("\nReader's rulings that differ from the script:\n"); print("\n".join(notes))

if __name__ == "__main__":
    main()
