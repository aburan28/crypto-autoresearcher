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
                "approved_by": "coordinator",
                "approval_decision": "DEC-20260901-aaaaaa",
                "execution_authorized_decision": "DEC-20260901-aaaaaa",
                "frozen": True,
                "frozen_at": "2026-09-01T12:00:00+00:00",
                "budget": {"wall_clock_seconds_per_run": 120},
            }
        }))
        write(self.root / "ledger/decisions/DEC-20260901-aaaaaa.yaml", yaml.safe_dump({
            "coordinator_decision": {
                "id": "DEC-20260901-aaaaaa", "decided_by": "coordinator",
                "decision": "approve", "target_ids": ["EXP-ECDLP-aaaaaa"],
                "official_transitions": {"execution_authorized_stages": [0]},
            }
        }))
        write(self.root / "experiments/EXP-ECDLP-aaaaaa/runs/RUN-ECDLP-aaaaaa-1/manifest.yaml", yaml.safe_dump({
            "run": {
                "id": "RUN-ECDLP-aaaaaa-1",
                "experiment_id": "EXP-ECDLP-aaaaaa",
                "stage": 0,
                "status": "completed_valid",
                "code": {"commit": "0" * 40, "dirty": False,
                         "command": "python3 -m driver.recover RUN-ECDLP-aaaaaa-1 --seed 7"},
                "timing": {"started_at": "2026-09-02T10:00:00Z"},
                "result": {
                    "valid": True,
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
        self.assertEqual(provenance["approval"]["experiment"]["id"], "DEC-20260901-aaaaaa")
        self.assertEqual(e2o.check(objective, self.repo.root), [])

    def test_a_bare_approval_date_becomes_a_date_time_cairn_accepts(self) -> None:
        # The first objective rendered from a committed experiment cleared
        # `check` and was refused at `post`: approved_at is a bare date in
        # nearly every specification, and cairn wants a full date-time.
        spec = self.repo.root / "experiments/EXP-ECDLP-aaaaaa/specification.yaml"
        doc = yaml.safe_load(spec.read_text())
        del doc["experiment"]["frozen_at"]
        doc["experiment"]["approved_at"] = "2026-07-27"
        spec.write_text(yaml.safe_dump(doc))
        objective, provenance = e2o.render(self.repo.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1", None, 0, None, None)
        self.assertEqual(objective["created_at"], "2026-07-27T00:00:00+00:00")
        self.assertEqual(provenance["created_at_source"], "specification.approved_at")
        self.assertTrue(e2o.rfc3339_ok(objective["created_at"]))
        self.assertFalse(e2o.rfc3339_ok("2026-07-27"))
        self.assertEqual(e2o.normalise_ts("2026-07-27T10:00:00Z"), "2026-07-27T10:00:00+00:00")
        self.assertEqual(e2o.normalise_ts("2026-07-27T12:30:00+02:00"), "2026-07-27T10:30:00+00:00")
        with self.assertRaises(e2o.BridgeError):
            e2o.normalise_ts("last tuesday")
        problems = e2o.check({**objective, "created_at": "2026-07-27"}, self.repo.root)
        self.assertTrue(any("RFC 3339" in p for p in problems), problems)

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
        with self.assertRaisesRegex(e2o.BridgeError, "malformed experiment id"):
            e2o.load_spec(self.repo.root, "../ledger")

    def test_publication_refuses_missing_or_mismatched_coordinator_decision(self) -> None:
        spec_path = self.repo.root / "experiments/EXP-ECDLP-aaaaaa/specification.yaml"
        doc = yaml.safe_load(spec_path.read_text())
        doc["experiment"]["frozen"] = False
        spec_path.write_text(yaml.safe_dump(doc))
        with self.assertRaisesRegex(e2o.BridgeError, "approved, frozen"):
            e2o.render(self.repo.root, "EXP-ECDLP-aaaaaa", None, None, 0, None, None)
        doc["experiment"]["frozen"] = True
        spec_path.write_text(yaml.safe_dump(doc))
        decision_path = self.repo.root / "ledger/decisions/DEC-20260901-aaaaaa.yaml"
        decision = yaml.safe_load(decision_path.read_text())
        decision["coordinator_decision"]["target_ids"] = ["EXP-OTHER"]
        decision_path.write_text(yaml.safe_dump(decision))
        with self.assertRaisesRegex(e2o.BridgeError, "does not approve"):
            e2o.render(self.repo.root, "EXP-ECDLP-aaaaaa", None, None, 0, None, None)


class ArtifactAndRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)

    def test_the_artifact_is_the_statement_the_run_kept(self) -> None:
        statement = e2o.artifact(self.repo.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1")
        self.assertEqual(statement["k"], 2)
        self.assertEqual(set(statement), {"curve", "P", "Q", "k"})

    def test_witnesses_are_found_in_the_shapes_committed_runs_keep(self) -> None:
        run_dir = self.repo.root / "experiments/EXP-ECDLP-aaaaaa/runs/RUN-ECDLP-aaaaaa-1"
        (run_dir / "certificate.json").unlink()
        curve = {"p": 223, "a": 0, "b": 171}
        # EXP-DTREE-001's shape: a `certificates` list of {kind, statement, verified},
        # and the same rows again under `raw`, which must not double-count.
        rows = [
            {"kind": "discrete_log", "verified": True,
             "statement": {"curve": curve, "P": [105, 42], "Q": [81, 42], "k": 2}},
            {"kind": "discrete_log", "verified": True,
             "statement": {"curve": curve, "P": [105, 42], "Q": [105, 181], "k": 4}},
        ]
        write(run_dir / "raw-result.json", json.dumps({"certificates": rows, "raw": {"rows": rows},
                                                        "metrics": {"k": 7, "P": 1, "Q": 2}}))
        # EXP-ECDLP-612fb1's shape: flat {P, Q, k} rows under one top-level curve,
        # plus a row that lacks a field and is therefore not a witness.
        write(run_dir / "certificates.json", json.dumps({
            "curve": {**curve, "N": 240, "field_bits": 8},
            "certificates": [
                {"kind": "discrete_log", "P": [105, 42], "Q": [81, 42], "k": 2, "verified": True},
                {"kind": "discrete_log", "P": [105, 42], "Q": [12, 34], "k": 9, "verified": False},
                {"kind": "discrete_log", "P": [105, 42], "k": 3},
            ],
        }))
        kept = e2o.witnesses(self.repo.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1")
        self.assertEqual([w["statement"]["k"] for w in kept], [2, 4, 9])
        self.assertEqual(kept[0]["source"], "raw-result.json.certificates[0]")
        self.assertEqual(kept[2]["source"], "certificates.json.certificates[1]")
        self.assertEqual(kept[2]["statement"]["curve"], curve)
        self.assertIs(kept[2]["verified"], False)
        self.assertEqual(e2o.artifact(self.repo.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1", 1)["k"], 4)
        with self.assertRaises(e2o.BridgeError) as caught:
            e2o.artifact(self.repo.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1", 3)
        self.assertIn("out of range", str(caught.exception))
        # The sidecar, when present, comes first.
        write(run_dir / "certificate.json", json.dumps({
            "kind": "discrete_log",
            "statement": {"curve": curve, "P": [105, 42], "Q": [1, 1], "k": 5},
        }))
        self.assertEqual(e2o.artifact(self.repo.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1")["k"], 5)

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

    def test_a_record_block_names_the_witness_the_claim_carried(self) -> None:
        block = e2o.record_block("EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1", "sha256:o", "sha256:c",
                                 "accept", "http://127.0.0.1:8787", None, True, None, "cairn",
                                 "2026-10-04T00:00:00+00:00", witness="raw-result.json.certificates[0]")
        self.assertEqual(block["witness"], "raw-result.json.certificates[0]")
        self.assertNotIn("backs_direction", block)

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
