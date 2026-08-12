from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path
from typing import Any


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]


def load_json(name: str) -> dict[str, Any]:
    with (EXPERIMENT_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256(name: str) -> str:
    return hashlib.sha256((EXPERIMENT_DIR / name).read_bytes()).hexdigest()


class ProtocolFreezeTests(unittest.TestCase):
    def test_implementation_is_approved_but_execution_is_unplanned(self) -> None:
        experiment = load_json("specification.json")["experiment"]

        self.assertEqual(experiment["status"], "approved")
        self.assertTrue(experiment["approved_by"])
        self.assertNotIn("execution_plan", experiment)

    def test_current_protocol_records_have_implementation_only_status(self) -> None:
        records = {
            "source-instance-manifest-v1.json": "source_manifest",
            "source-execution-matrix-v2.json": "source_execution_matrix",
            "target-instance-manifest-v1.json": "target_manifest",
            "control-manifest-v1.json": "control_manifest",
            "execution-matrix-v4.json": "execution_matrix",
            "mutation-manifest-v4.json": "mutation_manifest",
        }

        for name, root_key in records.items():
            with self.subTest(name=name):
                self.assertEqual(
                    load_json(name)[root_key]["status"],
                    "approved_for_implementation",
                )

    def test_source_matrix_binding_and_full_matrix_bindings_match_bytes(self) -> None:
        source_matrix = load_json("source-execution-matrix-v2.json")[
            "source_execution_matrix"
        ]
        self.assertEqual(
            source_matrix["bindings"]["source_manifest_sha256"],
            sha256("source-instance-manifest-v1.json"),
        )

        full_bindings = load_json("execution-matrix-v4.json")["execution_matrix"][
            "bindings"
        ]
        bound_files = {
            "source_manifest_sha256": "source-instance-manifest-v1.json",
            "source_execution_matrix_sha256": "source-execution-matrix-v2.json",
            "target_manifest_sha256": "target-instance-manifest-v1.json",
            "control_manifest_sha256": "control-manifest-v1.json",
            "mutation_manifest_sha256": "mutation-manifest-v4.json",
            "accounting_model_sha256": "accounting-model-v4.md",
        }

        for binding, name in bound_files.items():
            with self.subTest(binding=binding):
                self.assertEqual(full_bindings[binding], sha256(name))

    def test_source_visible_records_contain_no_target_schedule_or_delta(self) -> None:
        source_manifest = load_json("source-instance-manifest-v1.json")[
            "source_manifest"
        ]
        redaction = source_manifest["redaction_invariant"]
        self.assertEqual(redaction["target_records"], 0)
        self.assertEqual(redaction["target_coordinates"], 0)
        self.assertEqual(redaction["target_digests"], 0)
        self.assertEqual(redaction["target_labels"], 0)

        source_matrix = load_json("source-execution-matrix-v2.json")[
            "source_execution_matrix"
        ]
        serialized = json.dumps(source_matrix, sort_keys=True)
        forbidden_fields = (
            "target_partition_delta",
            "campaign_counts_per_baseline_path",
            "target_linear_combinations",
            "target_tensor_records",
            "trace_zero_target_tensors",
            "general_trace_target_tensors",
        )
        for field in forbidden_fields:
            with self.subTest(field=field):
                self.assertNotIn(f'"{field}"', serialized)

    def test_source_and_target_factorization_counts_reconcile(self) -> None:
        matrix = load_json("execution-matrix-v4.json")["execution_matrix"]
        phases = matrix["factorization_phase_reconciliation"]
        source = phases["source_partition"]
        target = phases["target_partition_delta"]
        campaign = phases["campaign_total"]
        fields = (
            "normalization_calls_upper_bound",
            "streamed_prefix_factorizations_upper_bound",
            "two_sweep_factorizations_upper_bound",
            "total_rank_factorizations_upper_bound",
        )

        for field in fields:
            with self.subTest(field=field):
                self.assertEqual(source[field] + target[field], campaign[field])

        source_visible = load_json("source-execution-matrix-v2.json")[
            "source_execution_matrix"
        ]["source_partition_counts"]
        self.assertEqual(
            source_visible["source_normalization_calls_upper_bound"],
            source["normalization_calls_upper_bound"],
        )
        self.assertEqual(
            source_visible["source_streamed_prefix_factorizations_upper_bound"],
            source["streamed_prefix_factorizations_upper_bound"],
        )
        self.assertEqual(
            source_visible["source_two_sweep_factorizations_upper_bound"],
            source["two_sweep_factorizations_upper_bound"],
        )
        self.assertEqual(
            source_visible["source_total_rank_factorizations_upper_bound"],
            source["total_rank_factorizations_upper_bound"],
        )


if __name__ == "__main__":
    unittest.main()
