#!/usr/bin/env python3
"""Design-time unit tests for this experiment's run.py and check.py.

Not a trial and not a run record. Every output is written to a fresh
temporary directory outside the repository and deleted afterwards. The test
plays the supervisor's part: it writes command.txt and environment.json as
tools/experiment_execution.py does before launch, runs the driver and then
passes the driver's manifest through the real complete_manifest (no stub),
then tools/validate_ledger.py check_run via manifest_schema_errors. Finally it
evaluates every runbook assertion on the design-time outputs with
tools/runbook.py check_assertion, and plants defects that the assertions must
catch.

Run from the repository root:
    python3 -m unittest -v experiments/<EXP>/implementation/test_unit.py
"""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP_DIR = HERE.parent
REPO = EXP_DIR.parents[1]
sys.path.insert(0, str(REPO / "tools"))

import yaml  # noqa: E402
from experiment_execution import complete_manifest, manifest_schema_errors  # noqa: E402
from runbook import check_assertion  # noqa: E402

PLAN_REL = f"experiments/{EXP_DIR.name}/trial-plan.json"
PLAN = json.loads((REPO / PLAN_REL).read_text(encoding="utf-8"))
RUNBOOK = yaml.safe_load((EXP_DIR / "runbook.yaml").read_text(encoding="utf-8"))
STEP = next(step for step in RUNBOOK["steps"] if step["kind"] == "trials")


def head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True,
                          check=True).stdout.strip()


def launch(trial: dict, root: Path) -> tuple[Path, dict]:
    """Do what tools/experiment_execution.py execute_trial does around the
    driver, in a scratch directory, and complete the manifest."""
    run_dir = root / trial["run_id"]
    run_dir.mkdir()
    argv = [arg.replace("{run_dir}", str(run_dir)) for arg in trial["argv"]]
    checker = [arg.replace("{run_dir}", str(run_dir)) for arg in trial["check_argv"]]
    authority = {"commit": head(), "owner": "design-time-unit-test", "epoch": 1}
    started = datetime.now(timezone.utc).isoformat()
    (run_dir / "command.txt").write_text(json.dumps(argv) + "\n", encoding="utf-8")
    (run_dir / "environment.json").write_text(json.dumps({
        "python": sys.version, "platform": sys.platform,
        "source_sha256": PLAN["source_sha256"], "specification_sha256": PLAN["specification_sha256"],
        "commit": authority["commit"], "runtime_lock": PLAN.get("runtime_lock"),
        "runtime_lock_sha256": PLAN.get("runtime_lock_sha256")}), encoding="utf-8")
    with (run_dir / "stdout.log").open("w") as out, (run_dir / "stderr.log").open("w") as err:
        code = subprocess.run([sys.executable, *argv[1:]], cwd=REPO, stdout=out, stderr=err,
                              check=False, timeout=60).returncode
    if code != 0:
        raise AssertionError(f"driver exit {code}: {(run_dir / 'stderr.log').read_text()}")
    finished = datetime.now(timezone.utc).isoformat()
    digest = hashlib.sha256((REPO / PLAN_REL).read_bytes()).hexdigest()
    completion = complete_manifest(run_dir, PLAN, PLAN_REL, digest, trial, authority, argv,
                                   checker, started, finished)
    return run_dir, completion


def assertions_for(trial_id: str) -> list[tuple[str, dict]]:
    items = [(block["path"], item) for block in STEP["validity"]["files"]
             for item in block.get("assertions", [])]
    items += [(block["path"], item) for block in STEP["by_trial"][trial_id]["files"]
              for item in block.get("assertions", [])]
    return items


def failed(run_dir: Path, trial: dict, files: dict | None = None) -> list[str]:
    unit = {"trial_id": trial["id"], "run_id": trial["run_id"]}
    data = files or {name: json.loads((run_dir / name).read_text(encoding="utf-8"))
                     for name in ("raw-result.json", "manifest.yaml")}
    out = []
    for name, item in assertions_for(trial["id"]):
        ok, detail = check_assertion(item, data[name], unit=unit)
        if not ok:
            out.append(f"{name}: {detail}")
    return out


class DesignTimeOutputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(tempfile.mkdtemp(prefix=f"{EXP_DIR.name}-unit-"))
        assert REPO not in cls.root.parents, "scratch directory must be outside the repository"
        cls.units = {trial["id"]: (trial, *launch(trial, cls.root)) for trial in PLAN["trials"]}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_manifest_written_whole_by_driver(self):
        for trial_id, (_, _, completion) in self.units.items():
            with self.subTest(trial=trial_id):
                self.assertEqual(completion["action"], "unchanged",
                                 "complete_manifest had to add keys: the driver wrote a stub")

    def test_check_run_zero_errors(self):
        for trial_id, (_, run_dir, _) in self.units.items():
            with self.subTest(trial=trial_id):
                self.assertEqual(manifest_schema_errors(run_dir / "manifest.yaml"), [])

    def test_attack_claimed_false_everywhere(self):
        for trial_id, (_, run_dir, _) in self.units.items():
            with self.subTest(trial=trial_id):
                raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
                body = yaml.safe_load((run_dir / "manifest.yaml").read_text(encoding="utf-8"))["run"]
                self.assertIs(raw["attack_claimed"], False)
                self.assertIs(body["attack_claimed"], False)
                self.assertEqual(body["result"]["certificate"]["kind"], "none")

    def test_checker_exits_zero(self):
        for trial_id, (trial, run_dir, _) in self.units.items():
            with self.subTest(trial=trial_id):
                checker = [arg.replace("{run_dir}", str(run_dir)) for arg in trial["check_argv"]]
                result = subprocess.run([sys.executable, *checker[1:]], cwd=REPO, capture_output=True,
                                        text=True, check=False)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_every_runbook_assertion_holds(self):
        for trial_id, (trial, run_dir, _) in self.units.items():
            with self.subTest(trial=trial_id):
                self.assertEqual(failed(run_dir, trial), [])

    def test_controls_are_listed_and_negative_controls_fail_the_prediction(self):
        controls = STEP["controls"]
        self.assertTrue(controls)
        negatives = [t for t in controls if t.startswith("ctl-neg-")]
        self.assertGreaterEqual(len(negatives), 1)
        flag = "exact_match" if "exact_match" in json.dumps(STEP["by_trial"]) else "matches_preregistered"
        for trial_id in negatives:
            with self.subTest(trial=trial_id):
                raw = json.loads((self.units[trial_id][1] / "raw-result.json").read_text(encoding="utf-8"))
                self.assertIs(raw[flag], False, "a planted negative control matched the prediction")
        primary = next(t["id"] for t in PLAN["trials"] if t["id"] not in controls)
        raw = json.loads((self.units[primary][1] / "raw-result.json").read_text(encoding="utf-8"))
        self.assertIs(raw[flag], True)

    def test_planted_defects_are_caught(self):
        """A control or primary output carrying another unit's values must fail
        its own assertions: each negative control's raw result is checked
        against the primary's assertions and vice versa, and a flipped
        attack_claimed fails the common assertions."""
        controls = STEP["controls"]
        primary_id = next(t["id"] for t in PLAN["trials"] if t["id"] not in controls)
        p_trial, p_dir, _ = self.units[primary_id]
        p_files = {name: json.loads((p_dir / name).read_text(encoding="utf-8"))
                   for name in ("raw-result.json", "manifest.yaml")}
        for trial_id in controls:
            trial, run_dir, _ = self.units[trial_id]
            c_files = {name: json.loads((run_dir / name).read_text(encoding="utf-8"))
                       for name in ("raw-result.json", "manifest.yaml")}
            with self.subTest(primary_values_under=trial_id):
                swapped = copy.deepcopy(p_files)
                swapped["raw-result.json"].update(trial_id=trial["id"], run_id=trial["run_id"])
                swapped["manifest.yaml"]["run"].update(id=trial["run_id"], trial_id=trial["id"])
                self.assertNotEqual(failed(run_dir, trial, swapped), [])
            if trial_id.startswith("ctl-neg-"):
                with self.subTest(negative_values_under_primary=trial_id):
                    swapped = copy.deepcopy(c_files)
                    swapped["raw-result.json"].update(trial_id=p_trial["id"], run_id=p_trial["run_id"])
                    swapped["manifest.yaml"]["run"].update(id=p_trial["run_id"], trial_id=p_trial["id"])
                    self.assertNotEqual(failed(p_dir, p_trial, swapped), [])
        flipped = copy.deepcopy(p_files)
        flipped["raw-result.json"]["attack_claimed"] = True
        self.assertNotEqual(failed(p_dir, p_trial, flipped), [])

    def test_replay_pointers_are_deterministic(self):
        """Two scratch executions agree on every replay pointer (the A/A check an audit replays)."""
        root = Path(tempfile.mkdtemp(prefix=f"{EXP_DIR.name}-replay-"))
        try:
            pointers = [p for item in STEP["replay"]["compare"] for p in item["pointers"]]
            for trial in PLAN["trials"]:
                with self.subTest(trial=trial["id"]):
                    again, _ = launch(trial, root)
                    first = json.loads((self.units[trial["id"]][1] / "raw-result.json").read_text())
                    second = json.loads((again / "raw-result.json").read_text())
                    for pointer in pointers:
                        key = pointer.lstrip("/")
                        self.assertEqual(first.get(key, "absent"), second.get(key, "absent"), pointer)
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
