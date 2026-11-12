#!/usr/bin/env python3
"""Tests for prereg.py. Run: python3 test_prereg.py"""
import json, subprocess, sys, tempfile, unittest
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


class Stamp(unittest.TestCase):
    def test_dirty_paths_are_recorded_whole(self):
        d = repo_with_arms({"untreated": {}, "treated": {}})
        (d / "code.py").write_text("x = 2\n")
        run(d, "stamp", "logs/untreated")
        self.assertEqual(json.loads((d / "logs" / "untreated" / "git.json").read_text())["dirty"], ["code.py"])


if __name__ == "__main__":
    unittest.main()
