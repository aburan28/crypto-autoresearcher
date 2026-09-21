from __future__ import annotations

import json
import sys
import unittest
from itertools import product
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = EXPERIMENT_DIR / "src"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from tt_source_runtime import SOURCE_TRAFFIC_KEYS, TTRuntime  # noqa: E402
from compile_tt_source_advice import normalized_runtime_ledgers  # noqa: E402
from verify_tt_source_advice import (  # noqa: E402
    CellSpec,
    replay_transcript_payload,
    sha256_value,
)


def runtime() -> TTRuntime:
    matrix = json.loads(
        (EXPERIMENT_DIR / "source-execution-matrix-v2.json").read_text(
            encoding="utf-8"
        )
    )["source_execution_matrix"]
    return TTRuntime(
        operation_caps=matrix["source_partition_operation_cap"],
        traffic_keys=SOURCE_TRAFFIC_KEYS,
        resource_gates=matrix["resource_gates"],
    )


def outer_value(vectors: list[list[int]], indices: tuple[int, ...], p: int) -> int:
    value = 1
    for vector, index in zip(vectors, indices):
        value = value * vector[index] % p
    return value


class SourceRuntimeTests(unittest.TestCase):
    def test_rank_one_add_hadamard_and_cancellation(self) -> None:
        p = 239
        left_vectors = [
            [1, 2, 4],
            [3, 5, 7],
            [11, 13, 17],
            [19, 23, 29],
            [31, 37, 41],
        ]
        right_vectors = [
            [2, 3, 5],
            [7, 11, 13],
            [17, 19, 23],
            [29, 31, 37],
            [41, 43, 47],
        ]
        engine = runtime()
        left = engine.rank_one_from_vectors(
            left_vectors,
            p=p,
            label="left",
            metadata={"cell_id": "CTL-RANK1-B3", "gate": "left"},
        )
        right = engine.rank_one_from_vectors(
            right_vectors,
            p=p,
            label="right",
            metadata={"cell_id": "CTL-RANK1-B3", "gate": "right"},
        )
        summed = engine.add(
            left,
            right,
            label="sum",
            metadata={"cell_id": "CTL-RANK1-ADD-PRODUCT-B3", "gate": "sum"},
        )
        multiplied = engine.hadamard(
            left,
            right,
            label="product",
            metadata={"cell_id": "CTL-RANK1-ADD-PRODUCT-B3", "gate": "product"},
        )
        cancelled = engine.direct_sum(
            (left, left),
            (1, -1),
            label="cancelled",
            metadata={"cell_id": "CTL-CANCEL-TO-ZERO-B3", "gate": "cancel"},
        )

        self.assertEqual(left.ranks, (1, 1, 1, 1))
        self.assertEqual(right.ranks, (1, 1, 1, 1))
        self.assertEqual(summed.ranks, (2, 2, 2, 2))
        self.assertEqual(multiplied.ranks, (1, 1, 1, 1))
        self.assertTrue(cancelled.is_zero)

        for indices in product(range(3), repeat=5):
            expected_left = outer_value(left_vectors, indices, p)
            expected_right = outer_value(right_vectors, indices, p)
            metadata = {
                "cell_id": "CTL-RANK1-ADD-PRODUCT-B3",
                "gate": "exhaustive_sample",
            }
            self.assertEqual(
                engine.evaluate_sample(left, indices, metadata=metadata),
                expected_left,
            )
            self.assertEqual(
                engine.evaluate_sample(summed, indices, metadata=metadata),
                (expected_left + expected_right) % p,
            )
            self.assertEqual(
                engine.evaluate_sample(multiplied, indices, metadata=metadata),
                expected_left * expected_right % p,
            )

        self.assertEqual(engine.counts["normalization_calls"], 3)
        self.assertEqual(engine.counts["streamed_prefix_factorizations"], 4)
        self.assertEqual(
            engine.counts["rank_factorizations"],
            engine.counts["streamed_prefix_factorizations"]
            + engine.counts["two_sweep_factorizations"],
        )

        for tensor in (left, right, summed, multiplied, cancelled):
            engine.release(tensor, metadata={"cell_id": "GLOBAL", "gate": "test_cleanup"})
        self.assertEqual(engine.snapshot()["resources"]["current_live_field_words"], 0)

    def test_complete_two_sweep_reduces_common_prefix_rank(self) -> None:
        p = 239
        shared = [1, 2, 4]
        left_vectors = [
            shared,
            [3, 5, 7],
            [11, 13, 17],
            [19, 23, 29],
            [31, 37, 41],
        ]
        right_vectors = [
            shared,
            [43, 47, 53],
            [59, 61, 67],
            [71, 73, 79],
            [83, 89, 97],
        ]
        engine = runtime()
        left = engine.rank_one_from_vectors(
            left_vectors,
            p=p,
            label="prefix-left",
            metadata={"cell_id": "CTL-COMMON-PREFIX-SUM-B3", "gate": "left"},
        )
        right = engine.rank_one_from_vectors(
            right_vectors,
            p=p,
            label="prefix-right",
            metadata={"cell_id": "CTL-COMMON-PREFIX-SUM-B3", "gate": "right"},
        )
        result = engine.add(
            left,
            right,
            label="prefix-sum",
            metadata={"cell_id": "CTL-COMMON-PREFIX-SUM-B3", "gate": "sum"},
        )
        self.assertEqual(result.ranks, (1, 2, 2, 2))

        for tensor in (left, right, result):
            engine.release(tensor, metadata={"cell_id": "GLOBAL", "gate": "test_cleanup"})
        self.assertEqual(engine.snapshot()["resources"]["current_live_field_words"], 0)

    def test_normalized_c08_transcript_replays_every_runtime_event(self) -> None:
        p = 239
        left_vectors = [
            [1, 2, 4],
            [3, 5, 7],
            [11, 13, 17],
            [19, 23, 29],
            [31, 37, 41],
        ]
        right_vectors = [
            [2, 3, 5],
            [7, 11, 13],
            [17, 19, 23],
            [29, 31, 37],
            [41, 43, 47],
        ]
        engine = runtime()
        metadata = {"cell_id": "C08:random_unique", "gate": "transcript_test"}
        left = engine.rank_one_from_vectors(
            left_vectors,
            p=p,
            label="transcript-left",
            metadata=metadata,
        )
        right = engine.rank_one_from_vectors(
            right_vectors,
            p=p,
            label="transcript-right",
            metadata=metadata,
        )
        summed = engine.add(
            left,
            right,
            label="transcript-sum",
            metadata=metadata,
        )
        product_tt = engine.hadamard(
            left,
            right,
            label="transcript-product",
            metadata=metadata,
        )
        engine.evaluate_sample(product_tt, (0, 1, 2, 1, 0), metadata=metadata)
        engine.tensor_record(product_tt, retained_advice=False, cell_id="C08:random_unique")
        for tensor in (left, right, summed, product_tt):
            engine.release(tensor, metadata=metadata)

        snapshot = engine.snapshot()
        events, allocations, ledger, transcript = normalized_runtime_ledgers(snapshot)
        transcript_map = {row["node_id"]: row for row in transcript}
        objects = {}
        spec = CellSpec(
            cell_id="C08:random_unique",
            curve_id="C08",
            registry="random_unique",
            p=p,
            a=40,
            b=78,
            B=3,
            points=(),
            primary=True,
            mode_scalars=(1, 1, 1, 1, 1),
        )
        arithmetic_keys = (
            "adds",
            "subs",
            "muls",
            "squares",
            "inversions",
            "reductions",
            "comparisons",
        )
        for event in events:
            row = transcript_map[event["node_id"]]
            replayed, outputs = replay_transcript_payload(
                event["kind"],
                row["payload"],
                spec,
                f"test.transcript.{event['node_id']}",
                objects,
            )
            self.assertEqual(set(outputs), {item["object_id"] for item in event["outputs"]})
            output_map = {item["object_id"]: item for item in event["outputs"]}
            for object_id, array in outputs.items():
                self.assertEqual(output_map[object_id]["shape"], list(array.shape))
                self.assertEqual(
                    output_map[object_id]["digest_sha256"],
                    sha256_value(array.record()),
                )
                objects[object_id] = array
            for key in arithmetic_keys:
                self.assertEqual(event["operation_vector"][key], replayed[key])
            for object_id in event["freed_object_ids"]:
                objects.pop(object_id, None)

        self.assertEqual(objects, {})
        self.assertEqual(ledger["operation_vector"], snapshot["operations"])
        allocated_ids = {
            row["object_id"] for row in allocations if row["event"] == "allocate"
        }
        freed_ids = {
            row["object_id"] for row in allocations if row["event"] == "free"
        }
        self.assertEqual(allocated_ids, freed_ids)


if __name__ == "__main__":
    unittest.main()
