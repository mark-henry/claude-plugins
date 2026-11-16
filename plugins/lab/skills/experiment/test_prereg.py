#!/usr/bin/env python3
"""Tests for prereg.py. Run: python3 test_prereg.py"""
import hashlib, json, os, random, re, shutil, statistics, subprocess, sys, tempfile, unittest
from pathlib import Path

PREREG = Path(__file__).with_name("prereg.py")


def run(cwd, *args):
    return subprocess.run([sys.executable, str(PREREG), *args], cwd=cwd, capture_output=True, text=True)


def repo_with_arms(launch_args=None, argv=None):
    """A git repo with a record and two arm folders. launch_args: {arm: args} writes launch.json; otherwise only a stamp,
    which holds the command line when argv: {arm: [tokens]} is given."""
    d = Path(tempfile.mkdtemp())
    sh = lambda *c: subprocess.run(c, cwd=d, check=True, capture_output=True)
    sh("git", "init", "-q"); sh("git", "config", "user.email", "t@example.com"); sh("git", "config", "user.name", "t")
    (d / "code.py").write_text("x = 1\n"); sh("git", "add", "."); sh("git", "commit", "-qm", "init")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()
    for arm in ("untreated", "treated"):
        out = d / "logs" / arm; out.mkdir(parents=True)
        git = {"commit": commit, "dirty": []}
        if argv:
            git["argv"] = argv[arm]
        if launch_args is None:
            (out / "git.json").write_text(json.dumps(git))
        else:
            (out / "launch.json").write_text(json.dumps({"args": launch_args[arm], "git": git}))
    (d / "prereg").mkdir()
    rec = {"question": "q", "varies": ["model"], "metrics": {"m": {"num": 1, "den": 2}}, "max_usd": 1,
           "arms": {a: {"out": f"logs/{a}", "command": "c"} for a in ("untreated", "treated")}}
    (d / "prereg" / "r.json").write_text(json.dumps(rec))
    return d


class Parity(unittest.TestCase):
    def test_fails_when_no_launch_args_were_recorded(self):
        # Stamped run folders hold a commit but no launch args: nothing shows the arms differ only in `varies`.
        d = repo_with_arms(launch_args=None)
        r = run(d, "parity", "prereg/r.json")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("no launch args", r.stdout)

    def test_stamped_command_lines_are_compared(self):
        same = repo_with_arms(argv={"untreated": ["train.py", "--model", "a", "--seed=1"], "treated": ["train.py", "--model", "b", "--seed=1"]})
        self.assertEqual(run(same, "parity", "prereg/r.json").returncode, 0)
        differ = repo_with_arms(argv={"untreated": ["train.py", "--model", "a", "--seed=1"], "treated": ["train.py", "--model", "b", "--seed=2"]})
        r = run(differ, "parity", "prereg/r.json")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("arg seed", r.stdout)

    def test_passes_when_args_differ_only_in_varies(self):
        d = repo_with_arms({"untreated": {"model": "a", "seed": 1}, "treated": {"model": "b", "seed": 1}})
        r = run(d, "parity", "prereg/r.json")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_fails_when_an_undeclared_arg_differs(self):
        d = repo_with_arms({"untreated": {"model": "a", "seed": 1}, "treated": {"model": "b", "seed": 2}})
        r = run(d, "parity", "prereg/r.json")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("arg seed", r.stdout)


    def test_launch_args_and_a_stamped_command_compare_by_value(self):
        # one arm's args come from launch.json (typed), the other's from a stamped command line (strings)
        d = repo_with_arms({"untreated": {"model": "a", "seed": 1}, "treated": {"model": "b", "seed": 1}})
        out = d / "logs" / "treated"
        git = json.loads((out / "launch.json").read_text())["git"]
        (out / "launch.json").unlink()
        (out / "git.json").write_text(json.dumps({**git, "argv": ["--model", "b", "--seed", "1"]}))
        r = run(d, "parity", "prereg/r.json")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_fails_when_the_code_diff_between_commits_cannot_be_computed(self):
        d = repo_with_arms({"untreated": {"model": "a"}, "treated": {"model": "b"}})
        lj = d / "logs" / "treated" / "launch.json"
        j = json.loads(lj.read_text()); j["git"]["commit"] = "0" * 40; lj.write_text(json.dumps(j))
        r = run(d, "parity", "prereg/r.json")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("could not compare", r.stdout)


class Freeze(unittest.TestCase):
    def test_close_refuses_when_the_stated_mechanism_was_edited_after_open(self):
        d = repo_with_arms({"untreated": {"model": "a"}, "treated": {"model": "b"}})
        rp = d / "prereg" / "r.json"
        rec = json.loads(rp.read_text())
        rec.update(status="exploratory", mechanism="the treatment helps on long items", surprises=["a gain on short items"])
        rp.write_text(json.dumps(rec))
        self.assertEqual(run(d, "open", "prereg/r.json").returncode, 0)
        for arm in ("untreated", "treated"):
            (d / "logs" / arm / "report.json").write_text("{}")
        rec = json.loads(rp.read_text()); rec["mechanism"] = "the treatment helps on short items"; rp.write_text(json.dumps(rec))
        r = run(d, "close", "prereg/r.json")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("changed after open", r.stdout + r.stderr)


class Open(unittest.TestCase):
    def test_open_says_to_pin_before_treated_output_and_names_no_cost_threshold(self):
        # A record for a counted run is pinned before any treated output, at any cost: never "commit it with the results".
        d = repo_with_arms({"untreated": {"model": "a"}, "treated": {"model": "b"}})
        rp = d / "prereg" / "r.json"
        rec = json.loads(rp.read_text())
        rec.update(bar="plan.md#BAR_M", decision="d", predictions={a: {"m": [0.1, 0.9]} for a in ("untreated", "treated")})
        rp.write_text(json.dumps(rec))
        r = run(d, "open", "prereg/r.json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("pin the record", r.stdout)
        self.assertIn("before a treated arm produces output", r.stdout)
        self.assertNotIn("$10", r.stdout)


class Placeholders(unittest.TestCase):
    def test_open_refuses_the_untouched_template_and_names_each_placeholder_field(self):
        d = repo_with_arms({"untreated": {}, "treated": {}})
        self.assertEqual(run(d, "new", "prereg/t.json").returncode, 0)
        rp = d / "prereg" / "t.json"
        r = run(d, "open", "prereg/t.json")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("question", r.stderr)
        rec = json.loads(rp.read_text()); rec["question"] = "does the treatment raise solves?"; rp.write_text(json.dumps(rec))
        r = run(d, "open", "prereg/t.json")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("bar", r.stderr)
        rec["bar"] = "plan.md#BAR_SOLVES"; rp.write_text(json.dumps(rec))
        r = run(d, "open", "prereg/t.json")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("command", r.stderr)
        self.assertIn("untreated", r.stderr)
        for arm in rec["arms"].values():
            arm["command"] = "python train.py"
        rp.write_text(json.dumps(rec))
        self.assertEqual(run(d, "open", "prereg/t.json").returncode, 0)

    def test_close_refusal_names_every_frozen_field(self):
        d = repo_with_arms({"untreated": {"model": "a"}, "treated": {"model": "b"}})
        rp = d / "prereg" / "r.json"
        rec = json.loads(rp.read_text()); rec["status"] = "exploratory"; rp.write_text(json.dumps(rec))
        self.assertEqual(run(d, "open", "prereg/r.json").returncode, 0)
        rec = json.loads(rp.read_text()); rec["varies"] = ["model", "seed"]; rp.write_text(json.dumps(rec))
        r = run(d, "close", "prereg/r.json")
        self.assertEqual(r.returncode, 1, r.stdout)
        for field in ("question", "bar", "decision", "varies", "watched", "arms", "metrics", "predictions", "mechanism", "surprises"):
            self.assertIn(field, r.stderr)


class Stamp(unittest.TestCase):
    def test_dirty_paths_are_recorded_whole(self):
        d = repo_with_arms({"untreated": {}, "treated": {}})
        (d / "code.py").write_text("x = 2\n")
        run(d, "stamp", "logs/untreated")
        # rewritten for schema 2: the stamp is stamp.json, its dirty list under "snapshot" (brief: "stamp: records a
        # snapshot of the working tree as a commit under refs/lab/<run id>")
        self.assertEqual(json.loads((d / "logs" / "untreated" / "stamp.json").read_text())["snapshot"]["dirty"], ["code.py"])


OLD = Path(__file__).with_name("fixtures") / "old"   # records and run folders written by the untouched script
OLD_RECORDS = ("draft", "explore", "counted", "closed", "abandoned")


def old_copy():
    """A fresh git repo holding a copy of the old fixtures, so a command that writes cannot touch the originals."""
    d = Path(tempfile.mkdtemp())
    shutil.copytree(OLD / "repo", d, dirs_exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=d, check=True)
    return d


def tree(d):
    """Every file under d except .git, with run times blanked (close writes the time it ran)."""
    out = {}
    for p in sorted(d.rglob("*")):
        if p.is_file() and ".git" not in p.relative_to(d).parts:
            out[str(p.relative_to(d))] = re.sub(r'"utc": "\d{8}T\d{4}Z"', '"utc": "T"', p.read_text())
    return out


class OldRecords(unittest.TestCase):
    """Records made by the untouched script (fixtures/old/prereg_v1.py, byte-identical to it) read exactly as before."""

    def same_as_v1(self, *args):
        old, new = old_copy(), old_copy()
        r0 = subprocess.run([sys.executable, str(OLD / "prereg_v1.py"), *args], cwd=old, capture_output=True, text=True)
        r1 = run(new, *args)
        self.assertEqual((r1.returncode, r1.stdout, r1.stderr), (r0.returncode, r0.stdout, r0.stderr), args)
        self.assertEqual(tree(new), tree(old), args)
        return r1

    def test_close_on_old_records_matches_the_untouched_script(self):
        for name in OLD_RECORDS:
            self.same_as_v1("close", f"prereg/{name}.json", "--note", "again")
        self.assertEqual(self.same_as_v1("close", "prereg/counted.json").returncode, 0)

    def test_parity_on_old_records_matches_the_untouched_script(self):
        for name in OLD_RECORDS[1:]:
            self.same_as_v1("parity", f"prereg/{name}.json")
        self.assertEqual(self.same_as_v1("parity", "prereg/closed.json").returncode, 0)

    def test_ls_on_old_records_matches_the_untouched_script(self):
        r = self.same_as_v1("ls", "prereg")
        self.assertIn("calibration: 2/2", r.stdout)

    def test_the_reference_copy_is_the_untouched_script(self):
        self.assertEqual(hashlib.sha256((OLD / "prereg_v1.py").read_bytes()).hexdigest()[:16], "316feab368dad35e")


# ---------------------------------------------------------------------------------------------------------------
# Schema 2: the standard checks. Everything below uses invented toy data only.

PILOT = Path(__file__).with_name("fixtures") / "pilot"   # hand-built: 6 items, 3 units, 3 baseline runs
BIG = 5 * 1024 * 1024 + 1


def git(d, *a):
    env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}      # so `git status` here never refreshes the index itself
    return subprocess.run(["git", *a], cwd=d, env=env, check=True, capture_output=True, text=True).stdout.strip()


def full_sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def lab_repo():
    d = Path(tempfile.mkdtemp())
    git(d, "init", "-q"); git(d, "config", "user.email", "t@example.com"); git(d, "config", "user.name", "t")
    (d / ".gitignore").write_text("ignored.log\n")
    (d / "train.py").write_text("lr = 1\n")
    (d / "score.py").write_text("import sys\nsys.exit(0 if open(sys.argv[1]).read().strip() == 'good' else 1)\n")
    (d / "lenient.py").write_text("import sys\nsys.exit(0)\n")
    (d / "good.txt").write_text("good\n"); (d / "broken.txt").write_text("garbage\n")
    git(d, "add", "."); git(d, "commit", "-qm", "init")
    return d


def write_items(d, out, rows):
    p = d / out
    p.mkdir(parents=True, exist_ok=True)
    with open(p / "items.jsonl", "a") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)


def rows(arm, scores, statuses=None, unit=lambda k: f"u{k}"):
    st = statuses or ["ok"] * len(scores)
    return [{"id": f"i{k}", "arm": arm, "unit": unit(k), "score": None if st[k] != "ok" else s, "status": st[k]}
            for k, s in enumerate(scores)]


def record(d, **over):
    """A schema-2 record for a two-arm toy. Line-6 fields set, so it opens as a counted record."""
    rec = {"schema": 2, "question": "Does model b score higher than model a on the toy set?", "bar": "plan.md#BAR_TOY",
           "decision": "use b if it clears the bar",
           "primary": {"metric": "mean score", "comparison": "treated minus untreated", "smallest_effect": 0.2, "unit": "item"},
           "intended_n": 40, "varies": ["model"],
           "arms": {"untreated": {"out": "runs/untreated", "command": "python train.py --model a"},
                    "treated": {"out": "runs/treated", "command": "python train.py --model b"}},
           "pilot": {"runs": ["runs/pilot1", "runs/pilot2"]}, "floors": {"none_reason": ""}, "resample_seed": 7}
    rec.update(over)
    (d / "prereg").mkdir(exist_ok=True)
    (d / "prereg" / "r.json").write_text(json.dumps(rec, indent=2))
    return "prereg/r.json"


def quiet_pilots(d, n=40, identical=False):
    """Two stamped baseline pilot runs that disagree on one item of n: a detectable difference far under 0.2.
    identical: they agree on every item, as a deterministic harness's would."""
    a = [k % 2 for k in range(n)]
    b = list(a)
    if not identical:
        b[0] = 1 - b[0]
    for k in (1, 2):
        r = run(d, "stamp", f"runs/pilot{k}", "--run-id", f"toy-pilot{k}", "--", "python", "train.py", "--model", "a")
        assert r.returncode == 0, r.stdout + r.stderr
    write_items(d, "runs/pilot1", rows("untreated", a)); write_items(d, "runs/pilot2", rows("untreated", b))


SCORER = {"command": "python3 score.py {output}", "file": "score.py", "broken": "broken.txt", "good": "good.txt"}


def noisy_pilots(d, n=10):
    write_items(d, "runs/pilot1", rows("untreated", [k % 2 for k in range(n)]))
    write_items(d, "runs/pilot2", rows("untreated", [(k + 1) % 2 for k in range(n)]))


def counted_toy(d, floor=0.0, n=40, identical_pilots=False, **over):
    """Record opened with a scorer, stamped quiet pilots, both arms stamped counted, items written with a constant floor."""
    over.setdefault("intended_n", n)
    over.setdefault("scorer", SCORER)
    rp = record(d, **over)
    quiet_pilots(d, n, identical=identical_pilots)
    assert run(d, "open", rp).returncode == 0
    for arm, model in (("untreated", "a"), ("treated", "b")):
        r = run(d, "stamp", f"runs/{arm}", "--record", rp, "--arm", arm, "--counted", "--run-id", f"toy-{arm}",
                "--", "python", "train.py", "--model", model)
        assert r.returncode == 0, r.stdout + r.stderr
    write_items(d, "runs/untreated", rows("untreated", [k % 2 for k in range(n)]))
    write_items(d, "runs/treated", rows("treated", [1 if k % 4 else 0 for k in range(n)]))
    if floor is not None:
        write_items(d, "runs/untreated", rows("floor:constant", [floor] * n))
    return rp


def ref_line7(run1, run2, seed, resamples=2000):
    """Independent reference: SE of the mean paired difference, resampling units with replacement."""
    load_rows = lambda p: {r["id"]: r for r in map(json.loads, Path(p).read_text().splitlines()) if r["status"] == "ok"}
    a, b = load_rows(run1), load_rows(run2)
    by_unit = {}
    for i in sorted(set(a) & set(b)):
        by_unit.setdefault(a[i]["unit"], []).append(a[i]["score"] - b[i]["score"])
    units = sorted(by_unit)
    rng = random.Random(seed)
    means = []
    for _ in range(resamples):
        ds = [x for u in [rng.choice(units) for _ in units] for x in by_unit[u]]
        means.append(sum(ds) / len(ds))
    se = statistics.stdev(means)
    return se, 2.8 * se


class NewRecord(unittest.TestCase):
    def test_new_writes_a_schema_2_record_with_the_line_6_fields(self):
        d = lab_repo()
        self.assertEqual(run(d, "new", "prereg/t.json").returncode, 0)
        rec = json.loads((d / "prereg" / "t.json").read_text())
        self.assertEqual(rec["schema"], 2)
        self.assertEqual(set(rec["primary"]) >= {"metric", "comparison", "smallest_effect", "unit"}, True)
        self.assertIn("resample_seed", rec)

    def test_open_hashes_the_line_6_fields_and_opens_exploratory_without_them(self):
        d = lab_repo()
        rp = record(d)
        r = run(d, "open", rp)
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads((d / rp).read_text())
        self.assertEqual(rec["status"], "open")
        self.assertRegex(rec["opened"]["line6_sha256"], r"^[0-9a-f]{16}$")
        d2 = lab_repo()
        rp2 = record(d2, primary={"metric": "mean score", "comparison": "treated minus untreated", "unit": "item"})
        r = run(d2, "open", rp2)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("line 6", r.stdout)
        self.assertEqual(json.loads((d2 / rp2).read_text())["status"], "exploratory")

    def test_open_names_the_field_that_made_the_record_exploratory(self):
        d = lab_repo()
        rp = record(d, bar="none, exploratory")
        r = run(d, "open", rp)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads((d / rp).read_text())["status"], "exploratory")
        cause = [l for l in r.stdout.splitlines() if "bar" in l and "none, exploratory" in l]
        self.assertEqual(len(cause), 1, r.stdout)
        d2 = lab_repo()
        rp2 = record(d2, primary={"metric": "mean score", "comparison": "treated minus untreated", "unit": "item"})
        r = run(d2, "open", rp2)
        cause = [l for l in r.stdout.splitlines() if "smallest_effect" in l]
        self.assertEqual(len(cause), 1, r.stdout)


class StampV2(unittest.TestCase):
    def test_stamp_records_every_field_of_a_known_repository_state(self):
        d = lab_repo()
        (d / "data.jsonl").write_text('{"x": 1}\n{"x": 2}\n{"x": 3}\n')
        (d / "config.json").write_text(json.dumps({"lr": 0.1, "batch": 8}))
        (d / "lab-inputs.md").write_text("- remote model org/m at rev1\n")
        rp = record(d, arms={"untreated": {"out": "runs/untreated", "command": "python train.py --model a", "data": [{"path": "data.jsonl"}]},
                             "treated": {"out": "runs/treated", "command": "python train.py --model b", "data": [{"path": "data.jsonl"}]}})
        self.assertEqual(run(d, "open", rp).returncode, 0)
        (d / "train.py").write_text("lr = 2\n")             # tracked, modified
        (d / "new.py").write_text("print('new')\n")         # untracked: inside the snapshot
        (d / "ignored.log").write_text("noise\n")           # ignored: outside the snapshot
        (d / "big.bin").write_bytes(b"\0" * BIG)            # over 5 MB: listed by sha256, not stored
        index_before = (d / ".git" / "index").read_bytes()
        status_before = git(d, "status", "--porcelain", "-uall")
        r = run(d, "stamp", "runs/treated", "--record", rp, "--arm", "treated", "--run-id", "mlflow-abc123",
                "--config", "config.json", "--model", "org/m", "--model-revision", "rev1", "--tokenizer-revision", "tok1",
                "--seed", "1", "--seed", "2", "--image", "sha256:feed", "--", "python", "train.py", "--model", "b")
        self.assertEqual(r.returncode, 0, r.stderr)
        status_after = [l for l in git(d, "status", "--porcelain", "-uall").splitlines() if l != "?? runs/treated/stamp.json"]
        self.assertEqual(status_after, status_before.splitlines())     # only the stamp itself is new
        self.assertEqual((d / ".git" / "index").read_bytes(), index_before)
        warnings = [l for l in r.stderr.splitlines() if l.strip()]
        self.assertEqual(len(warnings), 1, r.stderr)
        self.assertIn("uncommitted", warnings[0])
        s = json.loads((d / "runs" / "treated" / "stamp.json").read_text())
        rec = json.loads((d / rp).read_text())
        self.assertEqual(s["schema"], 2)
        self.assertEqual(s["run_id"], "mlflow-abc123")
        self.assertEqual(s["tracker_run_id"], "mlflow-abc123")
        self.assertEqual(s["argv"], ["python", "train.py", "--model", "b"])
        self.assertEqual(s["arm"], "treated")
        self.assertEqual(s["label"], "exploratory")
        self.assertRegex(s["utc"], r"^\d{8}T\d{4}Z$")
        self.assertTrue(s["host"])
        self.assertEqual(s["record"], {"path": rp, "sha256": full_sha(d / rp), "frozen_sha256": rec["opened"]["frozen_sha256"],
                                       "line6_sha256": rec["opened"]["line6_sha256"]})
        self.assertEqual(s["config"], {"path": "config.json", "sha256": full_sha(d / "config.json"), "values": {"lr": 0.1, "batch": 8}})
        self.assertEqual(s["model"], {"id": "org/m", "revision": "rev1", "tokenizer_revision": "tok1", "date": "n/a"})
        self.assertEqual(s["data"], [{"path": "data.jsonl", "sha256": full_sha(d / "data.jsonl"), "lines": 3, "bytes": len((d / "data.jsonl").read_bytes())}])
        self.assertEqual(s["seeds"], ["1", "2"])
        self.assertEqual(s["packages"], {"image": "sha256:feed"})
        self.assertEqual(s["lab_inputs_sha256"], full_sha(d / "lab-inputs.md"))
        snap = s["snapshot"]
        self.assertEqual(snap["ref"], "refs/lab/mlflow-abc123")
        self.assertEqual(git(d, "rev-parse", "refs/lab/mlflow-abc123"), snap["commit"])
        self.assertEqual(snap["head"], git(d, "rev-parse", "HEAD"))
        self.assertEqual(snap["dirty"], ["train.py"])
        self.assertIn("new.py", snap["untracked"])
        files = git(d, "ls-tree", "-r", "--name-only", snap["commit"]).splitlines()
        self.assertIn("new.py", files)
        self.assertIn("lab-inputs.md", files)
        self.assertNotIn("ignored.log", files)
        self.assertNotIn("big.bin", files)
        self.assertEqual(git(d, "show", f"{snap['commit']}:train.py"), "lr = 2")
        self.assertEqual(snap["large_files"], [{"path": "big.bin", "sha256": full_sha(d / "big.bin"), "bytes": BIG}])

    def test_fields_that_do_not_apply_are_written_na(self):
        d = lab_repo()
        r = run(d, "stamp", "runs/toy", "--", "python", "toy.py")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stderr.strip(), "")                     # clean tree: no warning
        s = json.loads((d / "runs" / "toy" / "stamp.json").read_text())
        for k in ("record", "config", "data", "seeds", "lab_inputs_sha256", "tracker_run_id", "arm"):
            self.assertEqual(s[k], "n/a", k)
        self.assertEqual(s["model"], {"id": "n/a", "revision": "n/a", "tokenizer_revision": "n/a", "date": "n/a"})
        self.assertEqual(s["label"], "exploratory")
        self.assertEqual(git(d, "rev-parse", s["snapshot"]["ref"]), s["snapshot"]["commit"])

    def test_a_second_stamp_is_refused_and_the_first_kept(self):
        d = lab_repo()
        self.assertEqual(run(d, "stamp", "runs/a", "--run-id", "r1", "--", "python", "train.py").returncode, 0)
        first = (d / "runs" / "a" / "stamp.json").read_text()
        r = run(d, "stamp", "runs/a", "--run-id", "r2", "--", "python", "train.py", "--other")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("stamp.json exists", r.stderr)
        self.assertEqual((d / "runs" / "a" / "stamp.json").read_text(), first)
        r = run(d, "stamp", "runs/b", "--run-id", "r1", "--", "python", "train.py")   # same run id: the ref exists
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("refs/lab/r1", r.stderr)

    def test_line_13_stamp_refuses_data_that_differs_from_the_record(self):
        d = lab_repo()
        (d / "data.jsonl").write_text('{"x": 1}\n{"x": 2}\n')
        arms = {a: {"out": f"runs/{a}", "command": f"python train.py --model {m}", "data": [{"path": "data.jsonl"}]}
                for a, m in (("untreated", "a"), ("treated", "b"))}
        rp = record(d, arms=arms)
        self.assertEqual(run(d, "open", rp).returncode, 0)
        self.assertEqual(run(d, "stamp", "runs/untreated", "--record", rp, "--arm", "untreated", "--", "x").returncode, 0)
        (d / "data.jsonl").write_text('{"x": 1}\n{"x": 2}\n{"x": 3}\n')
        r = run(d, "stamp", "runs/treated", "--record", rp, "--arm", "treated", "--", "x")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("line 13", r.stderr)
        self.assertIn("data.jsonl", r.stderr)


    def test_a_data_file_given_to_stamp_and_listed_in_the_record_is_recorded_once(self):
        d = lab_repo()
        (d / "data.jsonl").write_text('{"x": 1}\n')
        (d / "extra.jsonl").write_text('{"y": 1}\n')
        arms = {a: {"out": f"runs/{a}", "command": f"python train.py --model {m}", "data": ["data.jsonl"]}
                for a, m in (("untreated", "a"), ("treated", "b"))}
        rp = record(d, arms=arms)
        self.assertEqual(run(d, "open", rp).returncode, 0)
        r = run(d, "stamp", "runs/untreated", "--record", rp, "--arm", "untreated", "--data", "data.jsonl",
                "--data", "./data.jsonl", "--data", "extra.jsonl", "--data", "extra.jsonl", "--", "x")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads((d / "runs" / "untreated" / "stamp.json").read_text())["data"]
        self.assertEqual([e["path"] for e in data], ["data.jsonl", "extra.jsonl"])


class CountedGate(unittest.TestCase):
    def test_stamp_refuses_counted_without_hashed_line_6_fields(self):
        d = lab_repo()
        rp = record(d, primary={"metric": "mean score", "comparison": "treated minus untreated", "unit": "item"})
        quiet_pilots(d)
        self.assertEqual(run(d, "open", rp).returncode, 0)
        r = run(d, "stamp", "runs/untreated", "--record", rp, "--arm", "untreated", "--counted", "--", "x")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("line 6", r.stderr)
        self.assertIn("exploratory", r.stderr)
        r = run(d, "stamp", "runs/untreated", "--record", rp, "--arm", "untreated", "--", "x")   # may go ahead as exploratory
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_stamp_refuses_counted_when_line_7_fails(self):
        d = lab_repo()
        rp = record(d, intended_n=10)
        noisy_pilots(d)
        self.assertEqual(run(d, "open", rp).returncode, 0)
        r = run(d, "stamp", "runs/untreated", "--record", rp, "--arm", "untreated", "--counted", "--", "x")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("line 7", r.stderr)

    def test_counted_toy_earns_the_label(self):
        d = lab_repo()
        rp = counted_toy(d)
        r = run(d, "check", rp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("label: counted", r.stdout)

    def test_check_refuses_counted_when_a_stamp_lacks_the_record_hash(self):
        d = lab_repo()
        rp = record(d)
        quiet_pilots(d)
        self.assertEqual(run(d, "open", rp).returncode, 0)
        self.assertEqual(run(d, "stamp", "runs/untreated", "--record", rp, "--arm", "untreated", "--counted", "--", "x").returncode, 0)
        self.assertEqual(run(d, "stamp", "runs/treated", "--", "x").returncode, 0)    # stamped with no record
        write_items(d, "runs/untreated", rows("untreated", [k % 2 for k in range(40)]) + rows("floor:constant", [0] * 40))
        write_items(d, "runs/treated", rows("treated", [1] * 40))
        r = run(d, "check", rp)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("counted", r.stderr)
        self.assertIn("line 6", r.stderr)
        self.assertNotIn("label: counted", r.stdout)

    def test_check_refuses_counted_when_the_record_changed_after_the_stamps(self):
        d = lab_repo()
        rp = counted_toy(d)
        rec = json.loads((d / rp).read_text()); rec["primary"]["smallest_effect"] = 0.01; (d / rp).write_text(json.dumps(rec))
        r = run(d, "check", rp)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("changed", r.stderr)

    def test_line_12_refuses_counted_with_no_floor_and_no_reason(self):
        d = lab_repo()
        rp = counted_toy(d, floor=None)
        r = run(d, "check", rp)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("line 12", r.stderr)
        d2 = lab_repo()
        rp2 = counted_toy(d2, floor=None, floors={"none_reason": "no trivial policy can emit this output format"})
        r = run(d2, "check", rp2)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("label: counted", r.stdout)

    def test_line_12_refuses_counted_when_a_floor_reaches_the_best_arm(self):
        d = lab_repo()
        rp = counted_toy(d, floor=1.0)
        r = run(d, "check", rp)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("line 12", r.stderr)
        self.assertIn("floor:constant", r.stderr)

    def test_line_12_prints_each_floor_beside_each_arm(self):
        d = lab_repo()
        rp = counted_toy(d, floor=0.25)
        r = run(d, "check", rp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        line = next(l for l in r.stdout.splitlines() if l.startswith("line 12"))
        self.assertIn("floor:constant 0.250", line)
        self.assertIn("untreated 0.500", line)
        self.assertIn("treated 0.750", line)


class Line2(unittest.TestCase):
    def toy(self, untreated, treated, **over):
        d = lab_repo()
        rp = record(d, intended_n=10, floors={"none_reason": "toy"}, pilot={"runs": []}, **over)
        self.assertEqual(run(d, "open", rp).returncode, 0)
        for arm in ("untreated", "treated"):
            self.assertEqual(run(d, "stamp", f"runs/{arm}", "--record", rp, "--arm", arm, "--", "x").returncode, 0)
        write_items(d, "runs/untreated", untreated); write_items(d, "runs/treated", treated)
        return run(d, "check", rp)

    def test_accepts_full_n_and_no_failures(self):
        r = self.toy(rows("untreated", [1] * 10), rows("treated", [0] * 10))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("label: exploratory", r.stdout)

    def test_refuses_when_scored_n_differs_from_intended_n(self):
        r = self.toy(rows("untreated", [1] * 10), rows("treated", [0] * 9))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("line 2", r.stderr)
        self.assertIn("treated", r.stderr)

    def test_refuses_a_failure_share_over_the_threshold(self):
        st = ["ok"] * 7 + ["parse_failure"] * 3
        r = self.toy(rows("untreated", [1] * 10), rows("treated", [0] * 10, st))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("line 2", r.stderr)
        self.assertIn("parse_failure", r.stdout + r.stderr)

    def test_refuses_equal_failure_rates_that_both_exceed_the_share(self):
        # both arms fail 3 of 10: the difference check is silent, so only the share check can refuse
        st = ["ok"] * 7 + ["parse_failure"] * 3
        r = self.toy(rows("untreated", [1] * 10, st), rows("treated", [0] * 10, st))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("exceeds", r.stderr)
        self.assertNotIn("differ", r.stderr)

    def test_one_failure_is_under_the_two_item_minimum(self):
        st = ["ok"] * 9 + ["error"]
        r = self.toy(rows("untreated", [1] * 10), rows("treated", [0] * 10, st))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_refuses_failure_rates_that_differ_between_arms(self):
        st = ["ok"] * 7 + ["truncated"] * 3
        r = self.toy(rows("untreated", [1] * 10), rows("treated", [0] * 10, st),
                     failure_threshold={"share": 0.5, "min_items": 2, "difference": 0.1})
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("line 2", r.stderr)
        self.assertIn("differ", r.stderr)

    def test_refuses_a_malformed_items_row(self):
        bad = rows("treated", [0] * 10); bad[3]["status"] = "fine"
        r = self.toy(rows("untreated", [1] * 10), bad)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("items.jsonl", r.stderr)


class Line3(unittest.TestCase):
    def toy(self, scorer):
        d = lab_repo()
        rp = record(d, intended_n=10, floors={"none_reason": "toy"}, pilot={"runs": []},
                    scorer={"command": f"python3 {scorer} {{output}}", "file": scorer, "broken": "broken.txt", "good": "good.txt"})
        self.assertEqual(run(d, "open", rp).returncode, 0)
        for arm in ("untreated", "treated"):
            self.assertEqual(run(d, "stamp", f"runs/{arm}", "--record", rp, "--arm", arm, "--", "x").returncode, 0)
            write_items(d, f"runs/{arm}", rows(arm, [1] * 10))
        return d, rp, run(d, "check", rp)

    def test_accepts_a_scorer_that_fails_broken_and_passes_good_and_records_its_hash(self):
        d, rp, r = self.toy("score.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("line 3", r.stdout)
        res = json.loads((d / "prereg" / "r.check.json").read_text())
        self.assertEqual(res["line3"]["scorer_sha256"], full_sha(d / "score.py"))

    def test_refuses_a_scorer_that_passes_the_broken_output(self):
        d, rp, r = self.toy("lenient.py")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("line 3", r.stderr)
        self.assertIn("broken", r.stderr)


class Lines7And8(unittest.TestCase):
    def pilot_toy(self, runs):
        d = lab_repo()
        for k, p in enumerate(runs):
            shutil.copytree(p, d / "runs" / f"pilot{k + 1}")
        rp = record(d, intended_n=6, floors={"none_reason": "toy"}, resample_seed=11,
                    pilot={"runs": [f"runs/pilot{k + 1}" for k in range(len(runs))]})
        self.assertEqual(run(d, "open", rp).returncode, 0)
        for arm in ("untreated", "treated"):
            self.assertEqual(run(d, "stamp", f"runs/{arm}", "--record", rp, "--arm", arm, "--", "x").returncode, 0)
            write_items(d, f"runs/{arm}", rows(arm, [1, 0, 1, 0, 1, 0]))
        return d, run(d, "check", rp)

    def test_line_7_prints_the_se_and_detectable_difference_of_the_fixture(self):
        d, r = self.pilot_toy([PILOT / "run1", PILOT / "run2", PILOT / "run3"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        se, dd = ref_line7(PILOT / "run1" / "items.jsonl", PILOT / "run2" / "items.jsonl", 11)
        self.assertGreater(se, 0)
        self.assertIn(f"line 7: SE {se:.4f}, detectable difference {dd:.4f} (smallest effect 0.2)", r.stdout)

    def test_line_7_is_zero_when_the_pilot_runs_agree(self):
        d, r = self.pilot_toy([PILOT / "run1", PILOT / "run1"])
        self.assertIn("line 7: SE 0.0000, detectable difference 0.0000", r.stdout)

    def test_line_8_prints_per_item_pass_rates_and_the_counts_at_0_and_1(self):
        d, r = self.pilot_toy([PILOT / "run1", PILOT / "run2", PILOT / "run3"])
        out = r.stdout.splitlines()
        for item, rate in (("i0", "3/3"), ("i1", "0/3"), ("i2", "2/3"), ("i3", "1/3"), ("i4", "3/3"), ("i5", "0/3")):
            self.assertIn(f"  {item} {rate}", out)
        self.assertIn("line 8: 6 items over 3 baseline pilot runs; 2 at 0, 2 at 1, 2 in between", out)


class ArmComparison(unittest.TestCase):
    def two_arms(self, varies=("model",), config=({"lr": 0.1}, {"lr": 0.1}), between=None, data=None):
        d = lab_repo()
        arms = {a: {"out": f"runs/{a}", "command": f"python train.py --model {m}"} for a, m in (("untreated", "a"), ("treated", "b"))}
        if data:
            for (a, spec), text in zip(arms.items(), data):
                (d / f"{a}.jsonl").write_text(text)
                spec["data"] = [{"path": f"{a}.jsonl"}]
        rp = record(d, varies=list(varies), arms=arms)
        self.assertEqual(run(d, "open", rp).returncode, 0)
        (d / "train.py").write_text("lr = 3\n")      # the same uncommitted change under both arms
        for arm, cfg in zip(("untreated", "treated"), config):
            (d / f"{arm}.config.json").write_text(json.dumps(cfg))
        for arm, model in (("untreated", "a"), ("treated", "b")):
            r = run(d, "stamp", f"runs/{arm}", "--record", rp, "--arm", arm, "--config", f"{arm}.config.json",
                    "--", "python", "train.py", "--model", model)
            self.assertEqual(r.returncode, 0, r.stderr)
            if between and arm == "untreated":
                between(d)
        return d, run(d, "parity", rp)

    def test_accepts_arms_that_differ_only_in_declared_keys_on_a_dirty_tree(self):
        d, r = self.two_arms()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("parity: PASS", r.stdout)

    def test_refuses_an_undeclared_configuration_difference(self):
        d, r = self.two_arms(config=({"lr": 0.1}, {"lr": 0.2}))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("config.lr", r.stdout)
        d, r = self.two_arms(varies=("model", "config.lr"), config=({"lr": 0.1}, {"lr": 0.2}))
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_refuses_code_that_changed_between_the_arms_snapshots(self):
        d, r = self.two_arms(between=lambda d: (d / "train.py").write_text("lr = 4\n"))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("train.py", r.stdout)

    def test_line_13_refuses_undeclared_data_differences(self):
        d, r = self.two_arms(data=('{"x": 1}\n', '{"x": 1}\n{"x": 2}\n'))
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("line 13", r.stdout)
        d, r = self.two_arms(varies=("model", "data"), data=('{"x": 1}\n', '{"x": 1}\n{"x": 2}\n'))
        self.assertEqual(r.returncode, 0, r.stdout)

    def own_label_toy(self, extra):
        """Both arms launched with their own label and out folder as values; extra(arm) appends further args."""
        d = lab_repo()
        rp = record(d)
        self.assertEqual(run(d, "open", rp).returncode, 0)
        for arm, model in (("untreated", "a"), ("treated", "b")):
            r = run(d, "stamp", f"runs/{arm}", "--record", rp, "--arm", arm, "--", "python", "train.py", "--model", model,
                    "--arm", arm, "--out", f"runs/{arm}", "--save-dir", f"./runs/{arm}/", "--log", f"runs/{arm}/log.txt",
                    f"runs/{arm}", *extra(arm))
            self.assertEqual(r.returncode, 0, r.stderr)
        return run(d, "parity", rp)

    def test_the_arms_own_label_and_out_folder_are_never_a_difference(self):
        r = self.own_label_toy(lambda arm: [])
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("parity: PASS", r.stdout)

    def test_other_differences_are_still_refused_beside_the_arms_own_label(self):
        r = self.own_label_toy(lambda arm: ["--lr", "1" if arm == "untreated" else "2"])
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("lr", r.stdout)
        fails = [l for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
        self.assertEqual(len(fails), 1, r.stdout)
        # an arm writing into the other arm's folder is a difference, not its own folder
        r = self.own_label_toy(lambda arm: ["--save-to", "runs/treated" if arm == "untreated" else "runs/untreated"])
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("save_to", r.stdout)

    def test_refuses_an_arm_with_no_stamp(self):
        d, r = self.two_arms()
        (d / "runs" / "treated" / "stamp.json").unlink()
        r = run(d, "parity", "prereg/r.json")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("stamp", r.stdout)


class Ledger(unittest.TestCase):
    def test_each_test_scoring_adds_exactly_one_line_and_never_rewrites(self):
        d = lab_repo()
        rp = record(d)
        self.assertEqual(run(d, "open", rp).returncode, 0)
        (d / "cfg.json").write_text('{"temperature": 0}')
        self.assertEqual(run(d, "stamp", "runs/test1", "--run-id", "test-run-1", "--config", "cfg.json", "--", "x").returncode, 0)
        self.assertEqual(run(d, "stamp", "runs/test2", "--run-id", "test-run-2", "--config", "cfg.json", "--", "x").returncode, 0)
        lp = d / "prereg" / "r.ledger.jsonl"
        r = run(d, "ledger", rp, "runs/test1")
        self.assertEqual(r.returncode, 0, r.stderr)
        first = lp.read_text()
        self.assertEqual(len(first.splitlines()), 1)
        row = json.loads(first)
        self.assertEqual((row["run_id"], row["config_sha256"]), ("test-run-1", full_sha(d / "cfg.json")))
        self.assertRegex(row["utc"], r"^\d{8}T\d{4}Z$")
        self.assertIn("scored 1 time", r.stdout)
        r = run(d, "ledger", rp, "runs/test2")
        self.assertTrue(lp.read_text().startswith(first))
        self.assertEqual(len(lp.read_text().splitlines()), 2)
        self.assertIn("scored 2 times", r.stdout)


class Quote(unittest.TestCase):
    def test_refuses_a_number_with_no_run_id_and_prints_the_line(self):
        d = lab_repo()
        rp = counted_toy(d)
        (d / "report.md").write_text("# Toy\n\nTreated 30/40 vs untreated 20/40 (toy-treated, toy-untreated).\n"
                                     "That is a gain of 25%.\nNo numbers on this line.\n")
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("That is a gain of 25%.", r.stderr)
        self.assertIn("line 10", r.stderr)
        self.assertNotIn("30/40", r.stderr)

    def test_accepts_numbers_that_carry_a_run_id_from_the_record_or_the_ledger(self):
        d = lab_repo()
        rp = counted_toy(d)
        # a counted-stamped record is quoted only with a current check and parity on file (check.json can't be skipped)
        self.assertEqual(run(d, "check", rp).returncode, 0)
        self.assertEqual(run(d, "parity", rp).returncode, 0)
        self.assertEqual(run(d, "stamp", "runs/test1", "--run-id", "test-run-9", "--", "x").returncode, 0)
        self.assertEqual(run(d, "ledger", rp, "runs/test1").returncode, 0)
        (d / "report.md").write_text("Treated 30/40 (toy-treated); a gain of 25% (toy-untreated).\nOn test, 71% (test-run-9).\n"
                                     "Dated 2026/11/15, no rate here.\n")
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class Induct(unittest.TestCase):
    def test_induct_never_refuses_never_edits_and_marks_what_cannot_be_shown(self):
        d = old_copy()
        for name in OLD_RECORDS:
            before = (d / "prereg" / f"{name}.json").read_bytes()
            r = run(d, "induct", f"prereg/{name}.json")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual((d / "prereg" / f"{name}.json").read_bytes(), before)
            res = json.loads((d / "prereg" / f"{name}.induct.json").read_text())
            self.assertEqual(res["written_before_scoring"], "not established")
            self.assertEqual(res["pilot_power"], "not established")
            self.assertEqual(res["hash_intact"], name != "draft" or "not established")
        self.assertEqual(json.loads((d / "prereg" / "closed.induct.json").read_text())["hash_intact"], True)

    def test_induct_reports_a_broken_hash_and_items_it_finds_without_refusing(self):
        d = old_copy()
        rp = d / "prereg" / "closed.json"
        rec = json.loads(rp.read_text()); rec["question"] = "edited later"; rp.write_text(json.dumps(rec, indent=2))
        write_items(d, "logs/closed/untreated", rows("untreated", [1, 0, 1, 1], ["ok", "ok", "ok", "error"]))
        r = run(d, "induct", "prereg/closed.json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        res = json.loads((d / "prereg" / "closed.induct.json").read_text())
        self.assertEqual(res["hash_intact"], False)
        self.assertEqual(res["arms"]["untreated"]["n"], 4)
        self.assertEqual(res["arms"]["untreated"]["failures"], {"error": 1})
        self.assertEqual(res["arms"]["treated"], "not established (no items.jsonl)")
        self.assertEqual(res["scorer"], "not established (no scorer declared)")


class CountedNeedsEveryLine(unittest.TestCase):
    """The label counted is never printed or written while a line was skipped or refused."""

    def assertNotCounted(self, d, r, *named):
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("label: counted", r.stdout)
        self.assertIn("label: exploratory", r.stdout)
        self.assertEqual(json.loads((d / "prereg" / "r.check.json").read_text())["label"], "exploratory")
        for n in named:
            self.assertIn(n, r.stdout + r.stderr)

    def test_a_pilot_folder_named_twice_is_not_two_pilot_runs(self):
        d = lab_repo()
        rp = record(d, intended_n=40, scorer=SCORER, pilot={"runs": ["runs/pilot1", "./runs/pilot1/"]})
        quiet_pilots(d, 40)
        self.assertEqual(run(d, "open", rp).returncode, 0)
        r = run(d, "stamp", "runs/untreated", "--record", rp, "--arm", "untreated", "--counted", "--", "x")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("line 7", r.stderr)
        self.assertIn("fewer than two", r.stderr)

    def test_counted_needs_a_stamp_in_each_pilot_run(self):
        d = lab_repo()
        rp = counted_toy(d)
        (d / "runs" / "pilot2" / "stamp.json").unlink()
        self.assertNotCounted(d, run(d, "check", rp), "runs/pilot2")

    def test_counted_needs_pilot_runs_with_different_run_ids(self):
        d = lab_repo()
        rp = counted_toy(d)
        shutil.copy(d / "runs" / "pilot1" / "stamp.json", d / "runs" / "pilot2" / "stamp.json")
        self.assertNotCounted(d, run(d, "check", rp), "toy-pilot1")

    def test_counted_needs_a_declared_scorer(self):
        d = lab_repo()
        rp = counted_toy(d, scorer=None)
        self.assertNotCounted(d, run(d, "check", rp), "line 3", "scorer")

    def test_counted_needs_a_real_intended_n(self):
        d = lab_repo()
        rp = counted_toy(d, intended_n="... line 2: items per arm")
        self.assertNotCounted(d, run(d, "check", rp), "intended_n")

    def test_a_line_2_refusal_leaves_the_label_exploratory_in_the_printout_and_the_file(self):
        d = lab_repo()
        rp = counted_toy(d)
        write_items(d, "runs/treated", rows("treated", [1]))      # a 41st row, a duplicate id
        self.assertNotCounted(d, run(d, "check", rp), "line 2")

    def test_quote_refuses_a_counted_label_with_no_passing_parity_on_file(self):
        d = lab_repo()
        rp = counted_toy(d)
        self.assertIn("label: counted", run(d, "check", rp).stdout)
        (d / "report.md").write_text("Treated 30/40 (toy-treated).\n")
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("parity", r.stderr)
        self.assertEqual(run(d, "parity", rp).returncode, 0)
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_quote_refuses_a_counted_label_whose_parity_failed(self):
        d = lab_repo()
        rp = counted_toy(d)
        self.assertIn("label: counted", run(d, "check", rp).stdout)
        (d / "train.py").write_text("lr = 9\n")
        self.assertEqual(run(d, "stamp", "runs/elsewhere", "--run-id", "toy-other", "--", "x").returncode, 0)
        st = json.loads((d / "runs" / "treated" / "stamp.json").read_text())
        st["snapshot"] = json.loads((d / "runs" / "elsewhere" / "stamp.json").read_text())["snapshot"]
        (d / "runs" / "treated" / "stamp.json").write_text(json.dumps(st))
        self.assertEqual(run(d, "parity", rp).returncode, 1)
        (d / "report.md").write_text("Treated 30/40 (toy-treated).\n")
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("parity", r.stderr)


class QuoteTokens(unittest.TestCase):
    def test_a_run_id_matches_only_as_a_whole_token(self):
        d = lab_repo()
        self.assertEqual(run(d, "stamp", "runs/t", "--run-id", "t", "--", "x").returncode, 0)
        (d / "bad.md").write_text("It scored 73% overall.\n")
        r = run(d, "quote", "bad.md", "runs/t")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("73%", r.stderr)
        (d / "good.md").write_text("It scored 73% overall (t).\nRun t: 3/4.\n")
        r = run(d, "quote", "good.md", "runs/t")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_a_run_id_inside_a_longer_run_id_is_not_that_run_id(self):
        d = lab_repo()
        self.assertEqual(run(d, "stamp", "runs/a", "--run-id", "run-1", "--", "x").returncode, 0)
        (d / "r.md").write_text("Scored 40% (run-12).\nScored 41% (run-1.5).\nScored 42% (my-run-1).\n")
        r = run(d, "quote", "r.md", "runs/a")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(len([l for l in r.stderr.splitlines() if "line 10" in l]), 3, r.stderr)


class OldRecordNewStamp(unittest.TestCase):
    def test_old_record_parity_reads_the_commit_from_a_new_stamp(self):
        d = repo_with_arms(argv={"untreated": ["train.py", "--model", "a", "--seed=1"], "treated": ["train.py", "--model", "b", "--seed=1"]})
        (d / "logs" / "treated" / "git.json").unlink()
        self.assertEqual(run(d, "stamp", "logs/treated", "--", "train.py", "--model", "b", "--seed=1").returncode, 0)
        r = run(d, "parity", "prereg/r.json")
        self.assertNotIn("no recorded commit", r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("parity: PASS", r.stdout)


class Line8Brief(unittest.TestCase):
    def test_line_8_prints_the_count_and_at_most_ten_ids(self):
        d = lab_repo()
        for k in (1, 2):
            write_items(d, f"runs/pilot{k}", rows("untreated", [1] * 30))
        rp = record(d, intended_n=30, floors={"none_reason": "toy"})
        self.assertEqual(run(d, "open", rp).returncode, 0)
        for arm in ("untreated", "treated"):
            self.assertEqual(run(d, "stamp", f"runs/{arm}", "--record", rp, "--arm", arm, "--", "x").returncode, 0)
            write_items(d, f"runs/{arm}", rows(arm, [1] * 30))
        r = run(d, "check", rp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        per_item = [l for l in r.stdout.splitlines() if re.match(r"^  i\d+ \d+/\d+$", l)]
        self.assertLessEqual(len(per_item), 10, r.stdout)
        self.assertIn("line 8: 30 items over 2 baseline pilot runs; 0 at 0, 30 at 1, 0 in between", r.stdout)
        self.assertIn("prereg/r.check.json", r.stdout)
        self.assertEqual(len(json.loads((d / "prereg" / "r.check.json").read_text())["line8"]["rates"]), 30)


class Exploratory(unittest.TestCase):
    def test_a_one_arm_toy_needs_only_stamp_and_check(self):
        d = lab_repo()
        self.assertEqual(run(d, "stamp", "runs/toy", "--", "python", "toy.py").returncode, 0)
        write_items(d, "runs/toy", rows("toy", [1, 0, 1, 1, 0]))
        r = run(d, "check", "runs/toy")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("label: exploratory", r.stdout)
        self.assertIn("toy 0.600", r.stdout)

    def test_check_refuses_an_unstamped_run_folder(self):
        d = lab_repo()
        write_items(d, "runs/toy", rows("toy", [1, 0]))
        r = run(d, "check", "runs/toy")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("stamp", r.stderr)


def ignore(d, *patterns):
    """Add .gitignore patterns and commit them, as a project that keeps its runs out of git would."""
    with open(d / ".gitignore", "a") as f:
        f.writelines(p + "\n" for p in patterns)
    git(d, "add", ".gitignore"); git(d, "commit", "-qm", "ignore runs")


class IgnoredRunFolders(unittest.TestCase):
    """Run folders under an ignored path that already exists (`runs/` in .gitignore, an earlier run in it)."""

    def assertClean(self, r):
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_a_second_stamp_into_an_ignored_existing_parent(self):
        d = lab_repo(); ignore(d, "runs/")
        self.assertClean(run(d, "stamp", "runs/try1", "--", "python", "toy.py"))
        (d / "train.py").write_text("lr = 2\n")
        r = run(d, "stamp", "runs/try2", "--", "python", "toy.py")
        self.assertClean(r)
        snap = json.loads((d / "runs" / "try2" / "stamp.json").read_text())["snapshot"]
        self.assertEqual(git(d, "show", f"{snap['commit']}:train.py"), "lr = 2")
        self.assertEqual(git(d, "ls-tree", "-r", "--name-only", snap["commit"]).count("runs/"), 0)

    def test_a_second_stamp_with_a_record_into_an_ignored_existing_parent(self):
        d = lab_repo(); ignore(d, "runs/")
        rp = record(d)
        self.assertClean(run(d, "open", rp))
        for arm in ("untreated", "treated"):
            self.assertClean(run(d, "stamp", f"runs/{arm}", "--record", rp, "--arm", arm, "--", "python", "train.py"))

    def test_counted_path_with_ignored_arm_folders_and_side_files(self):
        # the pilots already sit under the ignored runs/ before the first stamp; the record's side files are ignored too
        d = lab_repo(); ignore(d, "runs/", "prereg/*.check.json", "prereg/*.ledger.jsonl")
        rp = record(d, intended_n=40, scorer=SCORER)
        quiet_pilots(d, 40)
        self.assertClean(run(d, "open", rp))
        for arm, model in (("untreated", "a"), ("treated", "b")):
            self.assertClean(run(d, "stamp", f"runs/{arm}", "--record", rp, "--arm", arm, "--counted",
                                 "--run-id", f"toy-{arm}", "--", "python", "train.py", "--model", model))
        write_items(d, "runs/untreated", rows("untreated", [k % 2 for k in range(40)]))
        write_items(d, "runs/treated", rows("treated", [1 if k % 4 else 0 for k in range(40)]))
        write_items(d, "runs/untreated", rows("floor:constant", [0.0] * 40))
        r = run(d, "check", rp)
        self.assertClean(r)
        self.assertIn("label: counted", r.stdout)
        r = run(d, "parity", rp)
        self.assertClean(r)
        self.assertIn("parity: PASS", r.stdout)
        self.assertClean(run(d, "stamp", "runs/test1", "--run-id", "test-run-1", "--", "x"))
        self.assertClean(run(d, "ledger", rp, "runs/test1"))

    def test_a_data_entry_may_be_a_bare_path_and_a_bad_one_is_refused(self):
        d = lab_repo(); ignore(d, "runs/")
        (d / "items.jsonl").write_text('{"x": 1}\n')
        arms = {a: {"out": f"runs/{a}", "command": f"python train.py --model {m}", "data": ["items.jsonl"]}
                for a, m in (("untreated", "a"), ("treated", "b"))}
        rp = record(d, arms=arms)
        self.assertClean(run(d, "open", rp))
        self.assertEqual(json.loads((d / rp).read_text())["arms"]["treated"]["data"][0]["lines"], 1)
        self.assertClean(run(d, "stamp", "runs/untreated", "--record", rp, "--arm", "untreated", "--", "x"))
        arms["treated"]["data"] = [7]
        rp = record(d, arms=arms)
        r = run(d, "open", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("data entry 7", r.stderr)

    def test_an_unexpected_git_error_is_a_one_line_refusal(self):
        d = lab_repo()
        (d / ".git" / "refs" / "lab").write_text("not a directory\n")      # update-ref cannot create refs/lab/<id>
        r = run(d, "stamp", "runs/try1", "--run-id", "x1", "--", "x")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(len(r.stderr.strip().splitlines()), 1, r.stderr)
        self.assertRegex(r.stderr, r"^refused: git ")


def rewrite_items(d, out, rows_):
    p = d / out / "items.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in rows_))


def read_rows(d, out):
    return [json.loads(l) for l in (d / out / "items.jsonl").read_text().splitlines() if l.strip()]


class JudgeRound5(unittest.TestCase):
    """Defects an independent judge found by running the tool, and checks that had no test."""

    assertNotCounted = CountedNeedsEveryLine.assertNotCounted

    def report(self, d, text="Treated 30/40 (toy-treated).\n"):
        (d / "report.md").write_text(text)

    def counted_and_quotable(self, **over):
        d = lab_repo()
        rp = counted_toy(d, **over)
        self.assertEqual(run(d, "check", rp).returncode, 0)
        self.assertEqual(run(d, "parity", rp).returncode, 0)
        self.report(d)
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return d, rp

    # 1. arms scoring different items with the same n
    def test_arms_scoring_different_items_with_the_same_n_are_not_counted(self):
        d = lab_repo()
        rp = counted_toy(d)
        shifted = [{**r, "id": f"i{k + 1}", "unit": f"u{k + 1}"} for k, r in enumerate(read_rows(d, "runs/treated"))]
        rewrite_items(d, "runs/treated", shifted)       # still 40 rows: i1..i40 against untreated's i0..i39
        r = run(d, "check", rp)
        self.assertNotCounted(d, r, "line 2")
        self.assertRegex(r.stderr, r"\b(i0|u0|i40|u40)\b")

    def test_different_items_per_arm_are_counted_when_the_record_declares_them(self):
        d = lab_repo()
        rp = counted_toy(d, units_differ_reason="treated is scored on a rotated copy of the toy set")
        shifted = [{**r, "id": f"i{k + 1}", "unit": f"u{k + 1}"} for k, r in enumerate(read_rows(d, "runs/treated"))]
        rewrite_items(d, "runs/treated", shifted)
        r = run(d, "check", rp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("label: counted", r.stdout)

    # 2. stale results
    def test_quote_and_close_refuse_after_an_arm_items_file_is_cut(self):
        d, rp = self.counted_and_quotable()
        p = d / "runs" / "treated" / "items.jsonl"
        p.write_text("".join(p.read_text().splitlines(keepends=True)[:-3]))
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("runs/treated/items.jsonl", r.stderr)
        r = run(d, "close", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("runs/treated/items.jsonl", r.stderr)
        self.assertNotIn("closed", json.loads((d / rp).read_text()))

    def test_quote_refuses_a_hand_made_parity_file_without_the_real_hashes(self):
        d = lab_repo()
        rp = counted_toy(d)
        self.assertEqual(run(d, "check", rp).returncode, 0)
        rec = json.loads((d / rp).read_text())
        (d / "prereg" / "r.parity.json").write_text(json.dumps({
            "utc": "20261115T0000Z", "pass": True, "problems": [],
            "record_frozen_sha256": rec["opened"]["frozen_sha256"],
            "run_ids": {"untreated": "toy-untreated", "treated": "toy-treated"}}))
        self.report(d)
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("parity", r.stderr)

    def test_quote_and_close_refuse_a_counted_stamped_record_with_no_check_on_file(self):
        d, rp = self.counted_and_quotable()
        (d / "prereg" / "r.check.json").unlink()
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("check", r.stderr)
        self.assertEqual(run(d, "close", rp).returncode, 1)

    # 3. degenerate line 7
    def test_copied_pilot_items_do_not_make_line_7_hold(self):
        d = lab_repo()
        rp = counted_toy(d)
        shutil.copy(d / "runs" / "pilot1" / "items.jsonl", d / "runs" / "pilot2" / "items.jsonl")
        r = run(d, "check", rp)
        self.assertNotCounted(d, r, "line 7", "identical")
        self.assertIn("does not hold", next(l for l in r.stdout.splitlines() if l.startswith("line 7")))
        d2 = lab_repo()
        rp2 = record(d2, intended_n=40, scorer=SCORER)
        quiet_pilots(d2, 40, identical=True)
        self.assertEqual(run(d2, "open", rp2).returncode, 0)
        r = run(d2, "stamp", "runs/untreated", "--record", rp2, "--arm", "untreated", "--counted", "--", "x")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("identical", r.stderr)

    def test_one_item_pilots_do_not_make_line_7_hold(self):
        d = lab_repo()
        rp = counted_toy(d)
        for k in (1, 2):
            rewrite_items(d, f"runs/pilot{k}", rows("untreated", [k - 1]))      # i0 only, scores 0 and 1
        self.assertNotCounted(d, run(d, "check", rp), "line 7", "pilot")
        d2 = lab_repo()
        rp2 = record(d2, intended_n=40, scorer=SCORER)
        for k in (1, 2):
            self.assertEqual(run(d2, "stamp", f"runs/pilot{k}", "--run-id", f"p{k}", "--", "x").returncode, 0)
        write_items(d2, "runs/pilot1", rows("untreated", [0])); write_items(d2, "runs/pilot2", rows("untreated", [0.01]))
        self.assertEqual(run(d2, "open", rp2).returncode, 0)
        r = run(d2, "stamp", "runs/untreated", "--record", rp2, "--arm", "untreated", "--counted", "--", "x")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("line 7", r.stderr)

    def test_a_declared_deterministic_harness_reports_a_zero_detectable_difference_by_declaration(self):
        d = lab_repo()
        rp = counted_toy(d, identical_pilots=True,
                         pilot={"runs": ["runs/pilot1", "runs/pilot2"], "deterministic": "toy harness: no sampling, no seed"})
        r = run(d, "check", rp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("label: counted", r.stdout)
        line = next(l for l in r.stdout.splitlines() if l.startswith("line 7"))
        self.assertIn("deterministic", line)
        self.assertIn("holds", line)

    # 4. a single arm; a counted stamp after scoring
    def test_a_single_arm_record_is_not_counted(self):
        d = lab_repo()
        rp = record(d, intended_n=40, scorer=SCORER,
                    arms={"untreated": {"out": "runs/untreated", "command": "python train.py --model a"}})
        quiet_pilots(d, 40)
        self.assertEqual(run(d, "open", rp).returncode, 0)
        r = run(d, "stamp", "runs/untreated", "--record", rp, "--arm", "untreated", "--counted", "--", "x")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("two arms", r.stderr)
        self.assertEqual(run(d, "stamp", "runs/untreated", "--record", rp, "--arm", "untreated", "--", "x").returncode, 0)
        sp = d / "runs" / "untreated" / "stamp.json"
        st = json.loads(sp.read_text()); st["label"] = "counted"; sp.write_text(json.dumps(st))   # check's own gate
        write_items(d, "runs/untreated", rows("untreated", [k % 2 for k in range(40)]) + rows("floor:constant", [0] * 40))
        self.assertNotCounted(d, run(d, "check", rp), "two arms")

    def test_a_counted_stamp_into_a_folder_with_scored_items_is_refused(self):
        d = lab_repo()
        rp = record(d, intended_n=40, scorer=SCORER)
        quiet_pilots(d, 40)
        self.assertEqual(run(d, "open", rp).returncode, 0)
        write_items(d, "runs/untreated", rows("untreated", [k % 2 for k in range(40)]))
        r = run(d, "stamp", "runs/untreated", "--record", rp, "--arm", "untreated", "--counted", "--", "x")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("items.jsonl", r.stderr)
        self.assertFalse((d / "runs" / "untreated" / "stamp.json").exists())

    # 5. counted pending parity
    def test_check_says_pending_parity_until_a_current_parity_passes(self):
        d = lab_repo()
        rp = counted_toy(d)
        r = run(d, "check", rp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("label: counted, pending parity", r.stdout)
        self.assertEqual(json.loads((d / "prereg" / "r.check.json").read_text())["label"], "counted, pending parity")
        self.assertEqual(run(d, "parity", rp).returncode, 0)
        self.assertEqual(json.loads((d / "prereg" / "r.check.json").read_text())["label"], "counted")
        r = run(d, "check", rp)
        self.assertIn("label: counted", r.stdout)
        self.assertNotIn("pending", r.stdout)

    # 7. checks that had no test
    def test_line_3_refuses_a_scorer_that_fails_the_known_good_output(self):
        d = lab_repo()
        (d / "strict.py").write_text("import sys\nsys.exit(1)\n")
        rp = record(d, intended_n=10, floors={"none_reason": "toy"}, pilot={"runs": []},
                    scorer={"command": "python3 strict.py {output}", "file": "strict.py", "broken": "broken.txt", "good": "good.txt"})
        self.assertEqual(run(d, "open", rp).returncode, 0)
        for arm in ("untreated", "treated"):
            self.assertEqual(run(d, "stamp", f"runs/{arm}", "--record", rp, "--arm", arm, "--", "x").returncode, 0)
            write_items(d, f"runs/{arm}", rows(arm, [1] * 10))
        r = run(d, "check", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("line 3", r.stderr)
        self.assertIn("known-good", r.stderr)

    def test_line_2_refuses_a_duplicate_id_at_the_intended_n(self):
        d = lab_repo()
        rp = record(d, intended_n=10, floors={"none_reason": "toy"}, pilot={"runs": []})
        self.assertEqual(run(d, "open", rp).returncode, 0)
        for arm in ("untreated", "treated"):
            self.assertEqual(run(d, "stamp", f"runs/{arm}", "--record", rp, "--arm", arm, "--", "x").returncode, 0)
        dup = rows("treated", [0] * 10); dup[9] = {**dup[0]}
        write_items(d, "runs/untreated", rows("untreated", [1] * 10)); write_items(d, "runs/treated", dup)
        r = run(d, "check", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("duplicate", r.stderr)
        self.assertIn("i0", r.stderr)

    def test_check_refuses_counted_when_line_7_fails_after_the_stamps(self):
        d = lab_repo()
        rp = counted_toy(d)
        rewrite_items(d, "runs/pilot2", rows("untreated", [(k + 1) % 2 for k in range(40)]))   # now every item disagrees
        self.assertNotCounted(d, run(d, "check", rp), "line 7", "exceeds")

    def test_quote_refuses_a_parity_result_for_other_run_ids_or_another_record_version(self):
        for field, value in (("run_ids", {"untreated": "toy-untreated", "treated": "someone-else"}),
                             ("record_frozen_sha256", "0" * 16)):
            d, rp = self.counted_and_quotable()
            pp = d / "prereg" / "r.parity.json"
            res = json.loads(pp.read_text()); res[field] = value; pp.write_text(json.dumps(res))
            r = run(d, "quote", "report.md", rp)
            self.assertEqual(r.returncode, 1, (field, r.stdout + r.stderr))
            self.assertIn("parity", r.stderr)


def det_toy(d, pilot_seeds, arm_seeds):
    """A counted toy whose record declares pilot.deterministic: identical pilots stamped with pilot_seeds (None: no
    --seed), both arms stamped counted with arm_seeds."""
    rp = record(d, intended_n=40, scorer=SCORER,
                pilot={"runs": ["runs/pilot1", "runs/pilot2"], "deterministic": "toy harness: no sampling at all"})
    for k, s in zip((1, 2), pilot_seeds):
        r = run(d, "stamp", f"runs/pilot{k}", "--run-id", f"toy-pilot{k}", *(["--seed", s] if s else []),
                "--", "python", "train.py", "--model", "a")
        assert r.returncode == 0, r.stdout + r.stderr
        write_items(d, f"runs/pilot{k}", rows("untreated", [k2 % 2 for k2 in range(40)]))
    assert run(d, "open", rp).returncode == 0
    for (arm, model), s in zip((("untreated", "a"), ("treated", "b")), arm_seeds):
        r = run(d, "stamp", f"runs/{arm}", "--record", rp, "--arm", arm, "--counted", "--run-id", f"toy-{arm}",
                *(["--seed", s] if s else []), "--", "python", "train.py", "--model", model)
        assert r.returncode == 0, r.stdout + r.stderr
    write_items(d, "runs/untreated", rows("untreated", [k % 2 for k in range(40)]) + rows("floor:constant", [0.0] * 40))
    write_items(d, "runs/treated", rows("treated", [1 if k % 4 else 0 for k in range(40)]))
    return rp


class JudgeRound6(unittest.TestCase):
    """Defects the third independent judge found by running the tool."""

    assertNotCounted = CountedNeedsEveryLine.assertNotCounted

    def quotable(self, **over):
        d = lab_repo()
        rp = counted_toy(d, **over)
        self.assertEqual(run(d, "check", rp).returncode, 0)
        self.assertEqual(run(d, "parity", rp).returncode, 0)
        (d / "report.md").write_text("Treated 30/40 (toy-treated).\n")
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return d, rp

    # 1. item ids are compared whatever the unit is called
    def test_an_arm_with_a_swapped_item_id_is_not_counted_when_the_unit_is_not_the_item(self):
        d = lab_repo()
        rp = counted_toy(d, primary={"metric": "mean score", "comparison": "treated minus untreated",
                                     "smallest_effect": 0.2, "unit": "document"})
        rs = read_rows(d, "runs/treated"); rs[0]["id"] = "zzz"         # same units, same n, one id swapped
        rewrite_items(d, "runs/treated", rs)
        r = run(d, "check", rp)
        self.assertNotCounted(d, r, "line 2", "zzz")
        self.assertIn("item ids", r.stderr)

    # 2. non-finite scores
    def test_a_nan_score_is_a_failed_item_that_never_enters_a_mean(self):
        d = lab_repo()
        rp = counted_toy(d)
        rs = read_rows(d, "runs/treated")
        for k in range(3):
            rs[k]["score"] = float("nan")
        rs[3]["score"] = float("inf")
        rewrite_items(d, "runs/treated", rs)
        r = run(d, "check", rp)
        self.assertNotCounted(d, r, "line 2", "non_finite_score 4")
        line12 = next(l for l in r.stdout.splitlines() if l.startswith("line 12"))
        self.assertNotIn("nan", line12)
        self.assertNotIn("inf", line12)

    def test_a_non_finite_arm_mean_is_not_counted(self):
        d = lab_repo()
        rp = counted_toy(d)
        rs = read_rows(d, "runs/treated")
        for r_ in rs:
            r_["score"] = 1e308                                     # each finite; their sum overflows
        rewrite_items(d, "runs/treated", rs)
        self.assertNotCounted(d, run(d, "check", rp), "finite")

    # 3. quote and close read check's verdict
    def test_quote_and_close_refuse_while_check_refuses_a_line(self):
        d = lab_repo()
        rp = counted_toy(d)
        rs = read_rows(d, "runs/treated")
        for k in range(3):
            rs[k].update(status="parse_failure", score=None)
        rewrite_items(d, "runs/treated", rs)
        self.assertEqual(run(d, "check", rp).returncode, 1)
        run(d, "parity", rp)
        (d / "report.md").write_text("Treated 27/40 (toy-treated).\n")
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("line 2", r.stderr)
        r = run(d, "close", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("line 2", r.stderr)
        self.assertNotIn("closed", json.loads((d / rp).read_text()))

    def test_quote_refuses_the_word_counted_unless_the_label_is_counted(self):
        d = lab_repo()
        rp = counted_toy(d, floor=1.0)              # a floor reaches the best arm: the run stands as exploratory
        self.assertEqual(run(d, "check", rp).returncode, 1)
        self.assertEqual(json.loads((d / "prereg" / "r.check.json").read_text())["label"], "exploratory")
        self.assertEqual(run(d, "parity", rp).returncode, 0)
        (d / "report.md").write_text("Exploratory: treated 30/40 (toy-treated).\n")
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        (d / "report.md").write_text("Treated 30/40 (toy-treated).\nThis run is Counted.\n")
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("report.md:2", r.stderr)
        self.assertIn("exploratory", r.stderr)
        d2 = lab_repo()
        rp2 = counted_toy(d2)
        self.assertEqual(run(d2, "check", rp2).returncode, 0)     # counted, pending parity
        (d2 / "report.md").write_text("Counted: treated 30/40 (toy-treated).\n")
        r = run(d2, "quote", "report.md", rp2)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(run(d2, "parity", rp2).returncode, 0)
        r = run(d2, "quote", "report.md", rp2)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_quote_of_a_counted_stamped_run_folder_asks_for_the_record(self):
        d, rp = self.quotable()
        r = run(d, "quote", "report.md", "runs/treated")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("runs/treated", r.stderr)
        self.assertIn("record", r.stderr)
        (d / "report.md").write_text("Counted: 3/4 (toy-pilot1).\n")    # an exploratory folder never says counted
        r = run(d, "quote", "report.md", "runs/pilot1")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("counted", r.stderr)

    def test_quote_and_close_refuse_a_stale_check_while_parity_is_current(self):
        d, rp = self.quotable()
        with open(d / "runs" / "treated" / "items.jsonl", "a") as f:
            f.write("\n")                                       # the judged file changes after check
        self.assertEqual(run(d, "parity", rp).returncode, 0)    # parity now hashes the new file; check does not
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("r.check.json is stale", r.stderr)
        self.assertNotIn("parity.json", r.stderr)
        r = run(d, "close", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("r.check.json is stale", r.stderr)

    def test_quote_and_close_refuse_a_hand_edited_check_label(self):
        d = lab_repo()
        rp = counted_toy(d, floor=1.0)
        self.assertEqual(run(d, "check", rp).returncode, 1)
        self.assertEqual(run(d, "parity", rp).returncode, 0)
        cp = d / "prereg" / "r.check.json"
        res = json.loads(cp.read_text()); res["label"] = "counted"; res["refusals"] = []; cp.write_text(json.dumps(res))
        (d / "report.md").write_text("Counted: treated 30/40 (toy-treated).\n")
        r = run(d, "quote", "report.md", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("verdict", r.stderr)
        r = run(d, "close", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("verdict", r.stderr)

    # 4. pilot.deterministic
    def test_identical_pilots_are_told_to_rerun_with_different_seeds_first(self):
        d = lab_repo()
        rp = counted_toy(d)
        shutil.copy(d / "runs" / "pilot1" / "items.jsonl", d / "runs" / "pilot2" / "items.jsonl")
        r = run(d, "check", rp)
        msg = next(l for l in r.stderr.splitlines() if "identical" in l)
        self.assertIn("different seeds", msg)
        self.assertIn("no randomness", msg)
        self.assertLess(msg.index("different seeds"), msg.index("pilot.deterministic"))

    def test_a_deterministic_declaration_contradicted_by_seeds_is_not_counted(self):
        for pilots, arms in (((None, None), ("1", "1")), (("1", "1"), ("2", "2")), (("1", None), (None, None))):
            d = lab_repo()
            rp = det_toy(d, pilots, arms)
            self.assertNotCounted(d, run(d, "check", rp), "line 7", "seed")

    def test_a_deterministic_declaration_consistent_with_seeds_is_counted(self):
        for pilots, arms in (((None, None), (None, None)), (("3", "3"), ("3", "3")), (("1", "2"), ("5", "5"))):
            d = lab_repo()
            rp = det_toy(d, pilots, arms)
            r = run(d, "check", rp)
            self.assertEqual(r.returncode, 0, (pilots, arms, r.stdout + r.stderr))
            self.assertIn("label: counted", r.stdout)

    # 5. smaller
    def test_an_abandoned_record_is_not_counted(self):
        d = lab_repo()
        rp = counted_toy(d)
        rec = json.loads((d / rp).read_text()); rec["status"] = "abandoned"; (d / rp).write_text(json.dumps(rec))
        self.assertNotCounted(d, run(d, "check", rp), "abandoned")

    def test_floors_none_reason_must_be_a_sentence(self):
        d = lab_repo()
        rp = counted_toy(d, floor=None, floors={"none_reason": "n/a"})
        r = run(d, "check", rp)
        self.assertNotCounted(d, r, "line 12", "none_reason")
        self.assertIn("reason", r.stderr)
        d2 = lab_repo()
        rp2 = counted_toy(d2, floor=None, floors={"none_reason": "no trivial policy applies"})
        self.assertIn("label: counted", run(d2, "check", rp2).stdout)

    def test_check_and_parity_refuse_a_data_file_edited_after_the_stamps(self):
        d = lab_repo()
        (d / "data.jsonl").write_text('{"x": 1}\n{"x": 2}\n')
        arms = {a: {"out": f"runs/{a}", "command": f"python train.py --model {m}", "data": ["data.jsonl"]}
                for a, m in (("untreated", "a"), ("treated", "b"))}
        rp = counted_toy(d, arms=arms)
        self.assertEqual(run(d, "check", rp).returncode, 0)
        self.assertEqual(run(d, "parity", rp).returncode, 0)
        (d / "data.jsonl").write_text('{"x": 1}\n{"x": 3}\n')
        r = run(d, "check", rp)
        self.assertNotCounted(d, r, "line 13", "data.jsonl")
        r = run(d, "parity", rp)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("data.jsonl", r.stdout)
        (d / "report.md").write_text("Treated 30/40 (toy-treated).\n")
        self.assertEqual(run(d, "quote", "report.md", rp).returncode, 1)


if __name__ == "__main__":
    unittest.main()
