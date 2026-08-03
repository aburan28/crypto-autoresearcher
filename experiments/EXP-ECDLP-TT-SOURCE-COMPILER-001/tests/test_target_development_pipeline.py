from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = EXPERIMENT_DIR / "src"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

import build_tt_source_candidate_bundle as bundle_builder  # noqa: E402
import compile_tt_target_advice as producer  # noqa: E402
import verify_tt_target_advice as verifier  # noqa: E402
from audit_tt_target_closure import audit_closures  # noqa: E402


class TargetDevelopmentPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.target = json.loads(
            (EXPERIMENT_DIR / "target-instance-manifest-v1.json").read_text(
                encoding="utf-8"
            )
        )["target_manifest"]

    def test_producer_and_independent_verifier_derive_the_same_25_jobs(self) -> None:
        produced = producer.build_schedule(self.target)
        independently_derived = verifier.expected_schedule(self.target)

        self.assertEqual(len(produced), 25)
        self.assertEqual(len(independently_derived), 25)
        self.assertEqual(
            [job.target_cell_id for job in produced],
            [job.target_cell_id for job in independently_derived],
        )
        self.assertEqual(
            [job.coefficients for job in produced],
            [job.coefficients for job in independently_derived],
        )
        self.assertEqual(
            sum(job.kind == "general_trace_control" for job in produced),
            6,
        )
        self.assertEqual(
            sum(job.kind != "general_trace_control" for job in produced),
            19,
        )

    def test_target_verifier_is_independent_of_producer_helpers(self) -> None:
        source = (SOURCE_DIR / "verify_tt_target_advice.py").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("import compile_tt_target_advice", source)
        self.assertNotIn("import tt_target_runtime", source)
        self.assertNotIn("import tt_target_coefficients", source)

    def test_target_producer_closure_has_no_verifier_or_mutation_import(self) -> None:
        producer_source = (SOURCE_DIR / "compile_tt_target_advice.py").read_text(
            encoding="utf-8"
        )
        runtime_source = (SOURCE_DIR / "tt_target_runtime.py").read_text(
            encoding="utf-8"
        )
        closure = producer_source + runtime_source

        self.assertNotIn("verify_tt_target_advice", closure)
        self.assertNotIn("run_tt_target_development_mutations", closure)
        self.assertNotIn("check_tt_target_order_invariance", closure)
        self.assertNotIn("from itertools import", closure)
        self.assertNotIn("repeat=5", closure)

    def test_artifact_digest_includes_the_canonical_trailing_newline(self) -> None:
        value = {"candidate": [1, 2, 3]}

        self.assertEqual(
            producer.artifact_digest(value),
            bundle_builder.artifact_digest(value),
        )
        self.assertNotEqual(
            producer.artifact_digest(value),
            bundle_builder.stable_digest(value),
        )

    def test_exact_json_size_preflight_handles_self_referential_width(self) -> None:
        value = {
            "payload": [0, 17, "quoted\"value", {"ascii": True}],
            "summary": {"serialized_bytes": 0},
        }

        self.assertEqual(
            producer.canonical_json_size(value),
            len(producer.canonical_json_bytes(value)),
        )
        expected = producer.stabilize_serialized_size(value)
        self.assertEqual(
            expected,
            len(producer.canonical_json_bytes(value)) + 1,
        )

    def test_development_entrypoints_never_authorize_artifact_freeze(self) -> None:
        entrypoints = (
            "build_tt_source_candidate_bundle.py",
            "compile_tt_target_advice.py",
            "verify_tt_target_advice.py",
            "run_tt_target_development_mutations.py",
            "check_tt_target_order_invariance.py",
        )

        for name in entrypoints:
            with self.subTest(name=name):
                source = (SOURCE_DIR / name).read_text(encoding="utf-8")
                self.assertIn('"artifact_freeze_authorized": False', source)

    def test_target_static_closures_are_exact_and_disjoint(self) -> None:
        report = audit_closures(
            SOURCE_DIR,
            SOURCE_DIR / "compile_tt_target_advice.py",
            SOURCE_DIR / "verify_tt_target_advice.py",
        )

        self.assertTrue(report["valid"])
        self.assertEqual(
            report["producer"]["files"],
            [
                "compile_tt_target_advice.py",
                "tt_target_coefficients.py",
                "tt_target_runtime.py",
            ],
        )
        self.assertEqual(report["verifier"]["files"], ["verify_tt_target_advice.py"])
        self.assertEqual(report["violations"], [])

    def test_numeric_rank_replay_is_included_in_verifier_meter(self) -> None:
        caps = {key: 1_000_000 for key in verifier.OPERATION_KEYS}
        meter = verifier.Meter(caps, 1_000_000, 1_000_000)

        replay = verifier.replay_rank_factor(
            [[1, 2], [2, 4]],
            5,
            meter,
            live_base=7,
        )

        self.assertEqual(replay.rank, 1)
        self.assertEqual(meter.operations["inversions"], 1)
        self.assertEqual(meter.operations["muls"], 4)
        self.assertEqual(meter.operations["subs"], 2)
        self.assertEqual(meter.operations["reductions"], 5)
        self.assertEqual(meter.operations["copied_words"], 24)
        self.assertEqual(meter.traffic_words, 37)
        self.assertEqual(meter.peak_live_words, 29)


if __name__ == "__main__":
    unittest.main()
