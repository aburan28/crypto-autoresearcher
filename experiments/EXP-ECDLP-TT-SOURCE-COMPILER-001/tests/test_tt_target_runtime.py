from __future__ import annotations

import json
import sys
import unittest
from itertools import product
from pathlib import Path

import numpy as np


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = EXPERIMENT_DIR / "src"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from tt_target_runtime import TargetResourceRefusal, TargetTTRuntime  # noqa: E402


def runtime(**gate_overrides: int) -> TargetTTRuntime:
    matrix = json.loads(
        (EXPERIMENT_DIR / "execution-matrix-v4.json").read_text(encoding="utf-8")
    )["execution_matrix"]
    gates = dict(matrix["resource_gates"])
    gates.update(gate_overrides)
    return TargetTTRuntime(
        operation_caps=matrix["partition_operation_caps"]["target_generator"],
        traffic_cap_words=matrix["partition_traffic_caps_words"]["target_generator"],
        resource_gates=gates,
    )


def rank_one(
    engine: TargetTTRuntime,
    name: str,
    vectors: list[list[int]],
    p: int = 239,
):
    B = len(vectors[0])
    return engine.tensor_from_cores(
        name=name,
        p=p,
        B=B,
        cores=[np.asarray(vector, dtype=np.int64).reshape(1, B, 1) for vector in vectors],
    )


def outer_value(vectors: list[list[int]], indices: tuple[int, ...], p: int) -> int:
    value = 1
    for vector, index in zip(vectors, indices):
        value = value * vector[index] % p
    return value


class TargetRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.p = 239
        self.left_vectors = [
            [1, 2, 4],
            [3, 5, 7],
            [11, 13, 17],
            [19, 23, 29],
            [31, 37, 41],
        ]
        self.right_vectors = [
            [2, 3, 5],
            [7, 11, 13],
            [17, 19, 23],
            [29, 31, 37],
            [41, 43, 47],
        ]

    def test_input_retention_is_first_persistent_runtime_state(self) -> None:
        engine = runtime()

        engine.record_input_retention(17)

        snapshot = engine.snapshot()
        self.assertEqual(snapshot["resources"]["persistent_input_field_words"], 17)
        self.assertEqual(snapshot["resources"]["peak_live_field_words"], 17)
        self.assertEqual(snapshot["events"][0]["kind"], "target_input_retention")
        self.assertEqual(snapshot["operations"]["copied_words"], 34)
        self.assertEqual(snapshot["logical_traffic_words"], 34)
        with self.assertRaisesRegex(AssertionError, "first runtime event"):
            engine.record_input_retention(1)

    def test_weighted_sum_matches_every_dense_value_and_uses_eight_factors(self) -> None:
        engine = runtime()
        left = rank_one(engine, "left", self.left_vectors)
        right = rank_one(engine, "right", self.right_vectors)
        result = engine.weighted_sum((left, right), (3, -2), label="weighted")
        record = engine.target_record(result)
        snapshot = engine.snapshot()

        for indices in product(range(3), repeat=5):
            expected = (
                3 * outer_value(self.left_vectors, indices, self.p)
                - 2 * outer_value(self.right_vectors, indices, self.p)
            ) % self.p
            self.assertEqual(engine.evaluate(result, indices), expected)

        self.assertEqual(result.ranks, (2, 2, 2, 2))
        self.assertEqual(record["word_count"], result.words)
        self.assertEqual(snapshot["counts"]["normalization_calls"], 1)
        self.assertEqual(snapshot["counts"]["two_sweep_factorizations"], 8)
        self.assertEqual(snapshot["counts"]["total_rank_factorizations"], 8)
        event_operations = {key: 0 for key in snapshot["operations"]}
        event_traffic = {
            key: {"reads": 0, "writes": 0} for key in snapshot["traffic"]
        }
        for event in snapshot["events"]:
            if "operation_vector" not in event:
                continue
            for key, value in event["operation_vector"].items():
                event_operations[key] += value
            for key, row in event["traffic"].items():
                event_traffic[key]["reads"] += row["reads"]
                event_traffic[key]["writes"] += row["writes"]
        self.assertEqual(event_operations, snapshot["operations"])
        self.assertEqual(event_traffic, snapshot["traffic"])

    def test_cancellation_returns_canonical_zero(self) -> None:
        engine = runtime()
        tensor = rank_one(engine, "source", self.left_vectors)
        result = engine.weighted_sum((tensor, tensor), (1, -1), label="cancelled")

        self.assertTrue(result.is_zero)
        self.assertEqual(result.ranks, (0, 0, 0, 0))
        self.assertEqual(result.cores, ())
        self.assertTrue(
            all(engine.evaluate(result, indices) == 0 for indices in product(range(3), repeat=5))
        )
        self.assertGreater(engine.snapshot()["counts"]["two_sweep_factorizations"], 0)

    def test_right_sweep_removes_rank_hidden_by_a_common_suffix(self) -> None:
        engine = runtime()
        shared_suffix = self.left_vectors[1:]
        first = rank_one(
            engine,
            "first",
            [[1, 2, 4], *shared_suffix],
        )
        second = rank_one(
            engine,
            "second",
            [[5, 8, 13], *shared_suffix],
        )
        result = engine.weighted_sum((first, second), (1, 1), label="suffix-sum")

        self.assertEqual(result.ranks, (1, 1, 1, 1))
        factor_events = [
            event for event in engine.snapshot()["events"] if event["kind"] == "rank_factor"
        ]
        self.assertEqual(len(factor_events), 8)
        self.assertEqual(factor_events[0]["phase"], "left_sweep")
        self.assertEqual(factor_events[0]["rank"], 2)
        self.assertEqual(factor_events[4]["phase"], "right_sweep")
        self.assertEqual(factor_events[4]["rank"], 1)

    def test_import_is_copying_strict_and_source_inputs_are_immutable(self) -> None:
        producer = runtime()
        original = rank_one(producer, "X2", self.left_vectors)
        record = original.canonical_record()
        consumer = runtime()
        imported = consumer.tensor_from_record(record, expected_name="X2")
        before = imported.canonical_record()

        result = consumer.weighted_sum((imported,), (7,), label="scaled-X2")

        self.assertEqual(imported.canonical_record(), before)
        self.assertTrue(all(not core.data.flags.writeable for core in imported.cores))
        for indices in product(range(3), repeat=5):
            self.assertEqual(
                consumer.evaluate(result, indices),
                7 * outer_value(self.left_vectors, indices, self.p) % self.p,
            )
        self.assertEqual(consumer.snapshot()["counts"]["imported_source_tensors"], 1)

    def test_all_zero_coefficients_take_the_canonical_zero_path(self) -> None:
        engine = runtime()
        tensor = rank_one(engine, "source", self.left_vectors)
        result = engine.weighted_sum((tensor,), (0,), label="zero-coefficient")

        self.assertTrue(result.is_zero)
        self.assertEqual(engine.snapshot()["counts"]["normalization_calls"], 1)
        self.assertEqual(engine.snapshot()["counts"]["two_sweep_factorizations"], 0)

    def test_target_coefficient_formation_has_a_disjoint_exact_event(self) -> None:
        engine = runtime()
        frozen = (1, 194, 175, 0, 162, 232)

        observed = engine.derive_target_coefficients(
            label="C08:random_unique:Q00",
            kind="trace_zero",
            projective=(142, 114, 1),
            p=self.p,
            norm_n=232,
            frozen_coefficients=frozen,
        )

        self.assertEqual(observed, frozen)
        event = engine.snapshot()["events"][0]
        self.assertEqual(event["kind"], "target_coefficient_formation")
        self.assertEqual(
            event["operation_vector"],
            {
                "adds": 1,
                "subs": 2,
                "muls": 7,
                "squares": 3,
                "inversions": 0,
                "reductions": 8,
                "comparisons": 17,
                "hash_bytes": 0,
                "copied_words": 0,
            },
        )
        self.assertEqual(event["traffic"]["registry_input"]["reads"], 4)
        self.assertEqual(event["traffic"]["coefficient_input"]["writes"], 6)

    def test_noncanonical_source_record_is_rejected(self) -> None:
        producer = runtime()
        tensor = rank_one(producer, "X2", self.left_vectors)
        record = tensor.canonical_record()
        record["cores"][0]["values"][0] = self.p

        with self.assertRaisesRegex(ValueError, "noncanonical"):
            runtime().tensor_from_record(record, expected_name="X2")

    def test_local_matrix_gate_refuses_before_factorization(self) -> None:
        engine = runtime(maximum_local_matrix_words=2)
        tensor = rank_one(engine, "source", self.left_vectors)

        with self.assertRaises(TargetResourceRefusal) as caught:
            engine.weighted_sum((tensor,), (1,), label="refused")

        self.assertEqual(caught.exception.reason, "maximum_local_matrix_words")
        self.assertEqual(
            engine.snapshot()["first_refusal"]["reason"],
            "maximum_local_matrix_words",
        )

    def test_raw_allocation_preflight_includes_persistent_source_advice(self) -> None:
        producer = runtime()
        left_record = rank_one(producer, "left", self.left_vectors).canonical_record()
        right_record = rank_one(producer, "right", self.right_vectors).canonical_record()
        engine = runtime(predicted_peak_live_field_words=50)
        left = engine.tensor_from_record(left_record, expected_name="left")
        right = engine.tensor_from_record(right_record, expected_name="right")

        with self.assertRaises(TargetResourceRefusal) as caught:
            engine.weighted_sum((left, right), (1, 1), label="liveness-tripwire")

        self.assertEqual(caught.exception.reason, "predicted_peak_live_field_words")
        self.assertEqual(caught.exception.detail["words"], 78)
        self.assertEqual(
            caught.exception.detail["phase"],
            "liveness-tripwire:target_direct_sum_preallocation",
        )
        self.assertEqual(
            [event["kind"] for event in engine.snapshot()["events"]],
            ["source_advice_import", "source_advice_import"],
        )

    def test_dense_kernel_rejects_noncanonical_int64_operand(self) -> None:
        engine = runtime()
        malformed = np.asarray([[2**40]], dtype=np.int64)
        canonical = np.asarray([[1]], dtype=np.int64)

        with self.assertRaisesRegex(AssertionError, "noncanonical"):
            engine._matmul(  # noqa: SLF001 - mutation control for the kernel boundary
                malformed,
                canonical,
                p=self.p,
                current_tt_words=0,
                transient_words=0,
                target_label="noncanonical-control",
                phase="test",
                mode=0,
            )

    def test_production_runtime_contains_no_five_tuple_iterator(self) -> None:
        source = (SOURCE_DIR / "tt_target_runtime.py").read_text(encoding="utf-8")

        self.assertNotIn("from itertools import", source)
        self.assertNotIn("repeat=5", source)
        self.assertNotIn("def dense_values", source)
        self.assertNotIn(".min(", source)
        self.assertNotIn(".max(", source)

    def test_normalizer_takes_ownership_of_the_raw_core_list(self) -> None:
        engine = runtime()
        raw_cores = [
            np.asarray(vector, dtype=np.int64).reshape(1, 3, 1)
            for vector in self.left_vectors
        ]
        original_cores = tuple(raw_cores)

        result = engine._normalize(  # noqa: SLF001 - ownership/liveness control
            raw_cores,
            p=self.p,
            B=3,
            label="ownership-control",
        )

        self.assertEqual(
            [id(core.data) for core in result.cores],
            [id(core) for core in raw_cores],
        )
        self.assertTrue(
            all(
                core is not original
                for core in raw_cores
                for original in original_cores
            )
        )

    def test_six_source_b5_target_control(self) -> None:
        p = 3947
        B = 5
        engine = runtime()
        sources = []
        vectors_by_source: list[list[list[int]]] = []
        for source_index in range(6):
            vectors = [
                [
                    (1 + source_index * 17 + mode * 11 + physical * 7) % p
                    for physical in range(B)
                ]
                for mode in range(5)
            ]
            vectors_by_source.append(vectors)
            sources.append(rank_one(engine, f"source-{source_index}", vectors, p=p))
        coefficients = (1, 3, 5, 7, 11, 13)
        result = engine.weighted_sum(sources, coefficients, label="six-source-B5")

        for indices in product(range(B), repeat=5):
            expected = sum(
                coefficient * outer_value(vectors, indices, p)
                for coefficient, vectors in zip(coefficients, vectors_by_source)
            ) % p
            self.assertEqual(engine.evaluate(result, indices), expected)
        factors = [
            event for event in engine.snapshot()["events"] if event["kind"] == "rank_factor"
        ]
        direct = next(
            event
            for event in engine.snapshot()["events"]
            if event["kind"] == "target_direct_sum"
        )
        self.assertEqual(len(factors), 8)
        self.assertEqual(direct["raw_ranks"], [6, 6, 6, 6])
        self.assertEqual(direct["raw_words"], 600)


if __name__ == "__main__":
    unittest.main()
