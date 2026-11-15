#!/usr/bin/env python3
"""Tests for prereg.py. Run: python3 test_prereg.py"""
import hashlib, json, re, shutil, subprocess, sys, tempfile, unittest
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
        self.assertEqual(json.loads((d / "logs" / "untreated" / "git.json").read_text())["dirty"], ["code.py"])


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


if __name__ == "__main__":
    unittest.main()
