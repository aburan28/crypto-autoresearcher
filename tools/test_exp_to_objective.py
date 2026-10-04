"""tools/exp_to_objective.py: an experiment becomes an objective, a run a claim.

Everything runs against a synthetic repository in a temp directory so no
test touches the committed experiments, and nothing here needs a cairn
binary: `check` is the half of cairn's shape rules that can be held without
one, and the point of these tests is that a rendered objective clears it.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp_to_objective as e2o  # noqa: E402

REAL_REPO = Path(__file__).resolve().parents[1]

CHECKER = "def check(artifact):\n    return (True, 'ok')\n"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class Repo:
    """A tiny repository with one experiment, one run and the Stage 0 objective."""

    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write(self.root / "cairn/checkers/discrete_log.py", CHECKER)
        digest = hashlib.sha256(CHECKER.encode()).hexdigest()
        write(self.root / "cairn/objectives/discrete-log-reverification.json", json.dumps({
            "created_at": "2026-08-16T00:00:00+00:00",
            "funder": "crypto-autoresearcher",
            "goal": "STAGE0-independent-verification",
            "reward": 0,
            "statement": "stage 0",
            "verifier": {"kind": "certificate", "checker": "cairn/checkers/discrete_log.py",
                         "checker_sha256": digest, "entrypoint": "check"},
            "artifact_schema": {"type": "object", "required": ["curve", "P", "Q", "k"]},
        }))
        write(self.root / "experiments/EXP-ECDLP-aaaaaa/specification.yaml", yaml.safe_dump({
            "experiment": {
                "id": "EXP-ECDLP-aaaaaa",
                "hypothesis_id": "H-ECDLP-bbbbbb",
                "goal_id": "GOAL-ECDLP-cccccc",
                "title": "Planted-instance recovery at 20 bits",
                "objective": "Recover k on planted instances; " * 3,
                "claim_tier": "toy",
                "status": "approved",
                "frozen_at": "2026-09-01T12:00:00+00:00",
                "budget": {"wall_clock_seconds_per_run": 120},
            }
        }))
        write(self.root / "experiments/EXP-ECDLP-aaaaaa/runs/RUN-ECDLP-aaaaaa-1/manifest.yaml", yaml.safe_dump({
            "run": {
                "id": "RUN-ECDLP-aaaaaa-1",
                "experiment_id": "EXP-ECDLP-aaaaaa",
                "code": {"commit": "0" * 40, "dirty": False,
                         "command": "python3 -m driver.recover RUN-ECDLP-aaaaaa-1 --seed 7"},
                "timing": {"started_at": "2026-09-02T10:00:00Z"},
                "result": {
                    "certificate": {"kind": "discrete_log", "verified": True},
                    "metrics": {"instances_solved": 20, "all_controls_pass": True,
                                "wall_seconds": 3.5, "mean_steps": 1234.5, "label": "x"},
                },
            }
        }))
        write(self.root / "experiments/EXP-ECDLP-aaaaaa/runs/RUN-ECDLP-aaaaaa-1/certificate.json", json.dumps({
            "kind": "discrete_log",
            "statement": {"curve": {"p": 223, "a": 0, "b": 171}, "P": [105, 42], "Q": [81, 42], "k": 2},
        }))

    def cleanup(self) -> None:
        self.tmp.cleanup()


class RenderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)

    def test_a_certificate_experiment_pins_the_stage0_checker_and_names_the_experiment(self) -> None:
        objective, provenance = e2o.render(
            self.repo.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1", None, 0, None, None
        )
        self.assertEqual(objective["verifier"]["kind"], "certificate")
        self.assertEqual(objective["verifier"]["checker"], "cairn/checkers/discrete_log.py")
        self.assertEqual(objective["goal"], "GOAL-ECDLP-cccccc")
        self.assertEqual(objective["created_at"], "2026-09-01T12:00:00+00:00")
        self.assertEqual(objective["reward"], 0)
        self.assertIn("EXP-ECDLP-aaaaaa", objective["statement"])
        self.assertIn("claim tier toy", objective["statement"])
        self.assertIn("minted, not posted", objective["statement"])
        self.assertEqual(provenance["kind"], "certificate")
        self.assertEqual(provenance["certificate_kind"], "discrete_log")
        self.assertEqual(provenance["run"]["commit"], "0" * 40)
        self.assertEqual(e2o.check(objective, self.repo.root), [])

    def test_the_kind_is_inferred_from_the_run_and_a_pin_drift_is_refused(self) -> None:
        self.assertEqual(e2o.infer_kind({"certificate": {"kind": "none"}}, None), "replay")
        self.assertEqual(e2o.infer_kind({}, {"result": {"certificate": {"kind": "discrete_log"}}}), "certificate")
        (self.repo.root / "cairn/checkers/discrete_log.py").write_text("def check(a):\n    return (False, 'no')\n")
        with self.assertRaises(e2o.BridgeError) as caught:
            e2o.render(self.repo.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1", "certificate", 0, None, None)
        self.assertIn("drifted", str(caught.exception))

    def test_a_replay_pins_the_command_and_only_exact_non_time_like_metrics(self) -> None:
        objective, provenance = e2o.render(
            self.repo.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1", "replay", 0, None, None
        )
        verifier = objective["verifier"]
        self.assertEqual(verifier["kind"], "replay")
        self.assertEqual(verifier["command"], ["python3", "-m", "driver.recover", "RUN-ECDLP-aaaaaa-1", "--seed", "7"])
        self.assertEqual(verifier["reproducible_fields"], ["all_controls_pass", "instances_solved"])
        self.assertEqual(verifier["timeout_seconds"], 120)
        self.assertEqual(objective["artifact_schema"]["example"],
                         {"results": {"all_controls_pass": True, "instances_solved": 20}})
        refused = provenance["replay"]["refused_fields"]
        self.assertTrue(any(r.startswith("wall_seconds: time-like") for r in refused), refused)
        self.assertTrue(any(r.startswith("mean_steps: a float") for r in refused), refused)
        self.assertTrue(any(r.startswith("label: not an integer") for r in refused), refused)
        self.assertTrue(provenance["replay"]["replay_wrapper_required"])
        self.assertIn("replay_wrapper_required: true", objective["statement"])
        self.assertEqual(e2o.check(objective, self.repo.root), [])

        wrapped, provenance = e2o.render(
            self.repo.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1", "replay", 5000, None,
            "python3 tools/exp_replay.py RUN-ECDLP-aaaaaa-1",
        )
        self.assertEqual(wrapped["verifier"]["command"], ["python3", "tools/exp_replay.py", "RUN-ECDLP-aaaaaa-1"])
        self.assertFalse(provenance["replay"]["replay_wrapper_required"])
        self.assertEqual(wrapped["reward"], 5000)

    def test_a_replay_with_nothing_exact_to_pin_is_refused(self) -> None:
        manifest = self.repo.root / "experiments/EXP-ECDLP-aaaaaa/runs/RUN-ECDLP-aaaaaa-1/manifest.yaml"
        doc = yaml.safe_load(manifest.read_text())
        doc["run"]["result"]["metrics"] = {"wall_seconds": 3.5, "rate": 0.5}
        manifest.write_text(yaml.safe_dump(doc))
        with self.assertRaises(e2o.BridgeError) as caught:
            e2o.render(self.repo.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1", "replay", 0, None, None)
        self.assertIn("no metric survives", str(caught.exception))
        with self.assertRaises(e2o.BridgeError):
            e2o.render(self.repo.root, "EXP-ECDLP-aaaaaa", None, "replay", 0, None, None)

    def test_a_missing_experiment_is_a_refusal_not_a_traceback(self) -> None:
        with self.assertRaises(e2o.BridgeError):
            e2o.render(self.repo.root, "EXP-ECDLP-nope00", None, None, 0, None, None)


class ArtifactAndRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)

    def test_the_artifact_is_the_statement_the_run_kept(self) -> None:
        statement = e2o.artifact(self.repo.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1")
        self.assertEqual(statement["k"], 2)
        self.assertEqual(set(statement), {"curve", "P", "Q", "k"})

    def test_a_run_that_kept_no_statement_cannot_be_claimed(self) -> None:
        (self.repo.root / "experiments/EXP-ECDLP-aaaaaa/runs/RUN-ECDLP-aaaaaa-1/certificate.json").unlink()
        with self.assertRaises(e2o.BridgeError) as caught:
            e2o.artifact(self.repo.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1")
        self.assertIn("no statement is on disk", str(caught.exception))

    def test_a_replay_artifact_is_the_exact_metrics(self) -> None:
        manifest = self.repo.root / "experiments/EXP-ECDLP-aaaaaa/runs/RUN-ECDLP-aaaaaa-1/manifest.yaml"
        doc = yaml.safe_load(manifest.read_text())
        doc["run"]["result"]["certificate"] = {"kind": "none"}
        manifest.write_text(yaml.safe_dump(doc))
        self.assertEqual(
            e2o.artifact(self.repo.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1"),
            {"results": {"all_controls_pass": True, "instances_solved": 20}},
        )

    def test_a_record_block_carries_the_receipt_and_marks_a_non_settling_verdict(self) -> None:
        block = e2o.record_block("EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1", "sha256:o", "sha256:c",
                                 "accept", "http://node:8080", "sha256:h", True, "ab" * 32, "cairn",
                                 "2026-10-04T00:00:00+00:00")
        self.assertEqual(block["verdict"], "accept")
        self.assertTrue(block["settled"])
        self.assertEqual(block["checker_sha256"], "ab" * 32)
        self.assertNotIn("backs_direction", block)
        unavailable = e2o.record_block("EXP-ECDLP-aaaaaa", None, "sha256:o", "sha256:c", "unavailable",
                                       "http://node:8080", None, False, None, "cairn", None)
        self.assertIs(unavailable["backs_direction"], False)
        self.assertNotIn("run_id", unavailable)
        with self.assertRaises(e2o.BridgeError):
            e2o.record_block("EXP-ECDLP-aaaaaa", None, "o", "c", "maybe", "n", None, False, None, "cairn", None)


class CheckTests(unittest.TestCase):
    def test_check_finds_what_cairn_would_refuse(self) -> None:
        bad = {
            "created_at": "x", "funder": "f", "goal": "g", "statement": "s", "reward": 1,
            "verifier": {"kind": "replay", "command": [], "reproducible_fields": ["wall_time_ms"],
                         "timeout_seconds": 0, "cwd": "../elsewhere"},
        }
        problems = e2o.check(bad, None)
        self.assertTrue(any("non-empty array of strings" in p for p in problems), problems)
        self.assertTrue(any("time-like" in p for p in problems), problems)
        self.assertTrue(any("timeout_seconds" in p for p in problems), problems)
        self.assertTrue(any("inside the root" in p for p in problems), problems)
        self.assertEqual(e2o.check({"verifier": {"kind": "lean"}}, None)[-1],
                         "verifier.kind 'lean': this tool renders certificate and replay only")

    def test_the_committed_stage0_objectives_clear_the_check_against_the_real_tree(self) -> None:
        for name in ("discrete-log-reverification.json", "decomposition-reverification.json"):
            objective = json.loads((REAL_REPO / "cairn/objectives" / name).read_text())
            self.assertEqual(e2o.check(objective, REAL_REPO), [], name)


class CliTests(unittest.TestCase):
    def test_render_writes_the_objective_and_its_provenance_and_check_reads_it_back(self) -> None:
        repo = Repo()
        self.addCleanup(repo.cleanup)
        out = repo.root / "out/objective.json"
        code = e2o.main(["--repo", str(repo.root), "render", "--exp", "EXP-ECDLP-aaaaaa",
                         "--run", "RUN-ECDLP-aaaaaa-1", "--out", str(out)])
        self.assertEqual(code, 0)
        self.assertTrue(out.is_file())
        side = yaml.safe_load(out.with_suffix(".provenance.yaml").read_text())
        self.assertEqual(side["experiment_id"], "EXP-ECDLP-aaaaaa")
        self.assertEqual(len(side["specification"]["sha256"]), 64)
        self.assertEqual(e2o.main(["--repo", str(repo.root), "check", str(out)]), 0)
        self.assertEqual(e2o.main(["--repo", str(repo.root), "render", "--exp", "EXP-ECDLP-nope00"]), 2)


if __name__ == "__main__":
    unittest.main()
