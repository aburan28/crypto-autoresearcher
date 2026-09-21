#!/usr/bin/env python3
"""Exact finite-field tensor-train runtime for target specialization.

This module is deliberately independent of the source compiler runtime.  It
accepts canonical, already-produced source tensor records and implements only
the target partition's weighted direct sum, exact two-sweep recompression, and
diagnostic evaluation operations.  It does not read manifests or artifacts.
"""
from __future__ import annotations

import hashlib
import json
import resource
import sys
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np

from tt_target_coefficients import general_basis_coefficients, trace_zero_coefficients


OPERATION_KEYS = (
    "adds",
    "subs",
    "muls",
    "squares",
    "inversions",
    "reductions",
    "comparisons",
    "hash_bytes",
    "copied_words",
)

TARGET_TRAFFIC_KEYS = (
    "registry_input",
    "coefficient_input",
    "allocation_zero_fill",
    "direct_sum_copy",
    "stage_a_input",
    "stage_a_output",
    "stage_b_input",
    "stage_b_output",
    "factor_input_copy",
    "pivot_scan",
    "row_normalization",
    "elimination",
    "factor_output",
    "transfer_propagation",
    "sweep_absorption",
    "core_emit",
    "advice_serialize",
    "advice_deserialize",
    "target_emit",
    "digest_read",
    "verifier_materialization",
    "artifact_serialize",
)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def stable_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _empty_operations() -> dict[str, int]:
    return {key: 0 for key in OPERATION_KEYS}


def _empty_traffic() -> dict[str, dict[str, int]]:
    return {key: {"reads": 0, "writes": 0} for key in TARGET_TRAFFIC_KEYS}


def _exact_int(value: Any, path: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{path} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{path} must be at least {minimum}")
    return value


class TargetResourceRefusal(RuntimeError):
    """A target operation exceeded a frozen resource or accounting gate."""

    def __init__(self, reason: str, detail: Mapping[str, Any]):
        self.reason = reason
        self.detail = dict(detail)
        super().__init__(f"{reason}: {self.detail}")


@dataclass(frozen=True)
class Core:
    data: np.ndarray

    @property
    def shape(self) -> tuple[int, int, int]:
        return tuple(int(value) for value in self.data.shape)  # type: ignore[return-value]

    @property
    def words(self) -> int:
        return int(self.data.size)


@dataclass(frozen=True)
class Tensor:
    name: str
    p: int
    B: int
    tag: str
    cores: tuple[Core, ...]

    @property
    def is_zero(self) -> bool:
        return self.tag == "canonical_zero"

    @property
    def ranks(self) -> tuple[int, int, int, int]:
        if self.is_zero:
            return (0, 0, 0, 0)
        return tuple(int(self.cores[index].shape[2]) for index in range(4))  # type: ignore[return-value]

    @property
    def words(self) -> int:
        return sum(core.words for core in self.cores)

    def canonical_record(self) -> dict[str, Any]:
        return {
            "B": self.B,
            "cores": [
                {
                    "shape": list(core.shape),
                    "values": [int(value) for value in core.data.flat],
                }
                for core in self.cores
            ],
            "name": self.name,
            "p": self.p,
            "ranks": list(self.ranks),
            "tag": self.tag,
        }


class TargetTTRuntime:
    """Target-only exact TT combiner with cumulative accounting."""

    def __init__(
        self,
        *,
        operation_caps: Mapping[str, int],
        traffic_cap_words: int,
        resource_gates: Mapping[str, int],
    ) -> None:
        self.operation_caps = {
            key: _exact_int(operation_caps[key], f"operation_caps.{key}", 0)
            for key in OPERATION_KEYS
        }
        self.traffic_cap_words = _exact_int(
            traffic_cap_words, "traffic_cap_words", 0
        )
        required_gates = (
            "maximum_local_matrix_words",
            "maximum_tt_object_words",
            "predicted_peak_live_field_words",
            "maximum_int64_dot_length",
            "maximum_int64_accumulator_bound",
            "signed_int64_maximum",
            "peak_rss_bytes",
        )
        self.resource_gates = {
            key: _exact_int(resource_gates[key], f"resource_gates.{key}", 0)
            for key in required_gates
        }
        self.operations = _empty_operations()
        self.traffic = _empty_traffic()
        self.events: list[dict[str, Any]] = []
        self.counts = {
            "artifact_serialization_events": 0,
            "imported_source_tensors": 0,
            "input_retention_events": 0,
            "target_coefficient_formations": 0,
            "target_disposals": 0,
            "target_linear_combinations": 0,
            "normalization_calls": 0,
            "two_sweep_factorizations": 0,
            "total_rank_factorizations": 0,
            "zero_results": 0,
        }
        self.maximum_local_matrix_words = 0
        self.maximum_tt_object_words = 0
        self.maximum_int64_dot_length = 0
        self.maximum_int64_accumulator_bound = 0
        self.peak_live_field_words = 0
        self.persistent_input_field_words = 0
        self.persistent_source_words = 0
        self.persistent_target_output_words = 0
        self.first_refusal: dict[str, Any] | None = None

    @property
    def logical_traffic_words(self) -> int:
        return sum(
            int(row["reads"]) + int(row["writes"])
            for row in self.traffic.values()
        )

    @property
    def persistent_field_words(self) -> int:
        return (
            self.persistent_input_field_words
            + self.persistent_source_words
            + self.persistent_target_output_words
        )

    def record_input_retention(self, field_words: int) -> None:
        """Meter decoded input field values retained throughout target compilation."""

        if self.events or self.persistent_field_words:
            raise AssertionError("target input retention must be the first runtime event")
        field_words = _exact_int(field_words, "input.field_words", 0)
        before_operations = dict(self.operations)
        before_traffic = self._traffic_snapshot(self.traffic)
        self._charge(copied_words=2 * field_words)
        self._charge_traffic(
            "advice_deserialize", reads=field_words, writes=field_words
        )
        self.persistent_input_field_words = field_words
        self._observe_live_words(field_words, "target_input_retention")
        self.counts["input_retention_events"] += 1
        self.events.append(
            {
                "field_words": field_words,
                "kind": "target_input_retention",
                "operation_vector": self._operation_delta(before_operations),
                "predicted_live_field_words": field_words,
                "traffic": self._traffic_delta(before_traffic),
            }
        )

    def _refuse(self, reason: str, detail: Mapping[str, Any]) -> None:
        if self.first_refusal is None:
            self.first_refusal = {"reason": reason, "detail": dict(detail)}
        raise TargetResourceRefusal(reason, detail)

    def _charge(self, **increments: int) -> None:
        for key, raw_increment in increments.items():
            if key not in self.operations:
                raise ValueError(f"unknown operation key {key!r}")
            increment = _exact_int(raw_increment, f"operation.{key}", 0)
            candidate = self.operations[key] + increment
            if candidate > self.operation_caps[key]:
                self._refuse(
                    "operation_cap",
                    {"key": key, "cap": self.operation_caps[key], "candidate": candidate},
                )
            self.operations[key] = candidate

    def _charge_traffic(self, bucket: str, *, reads: int = 0, writes: int = 0) -> None:
        if bucket not in self.traffic:
            raise ValueError(f"unknown traffic bucket {bucket!r}")
        reads = _exact_int(reads, f"traffic.{bucket}.reads", 0)
        writes = _exact_int(writes, f"traffic.{bucket}.writes", 0)
        candidate = self.logical_traffic_words + reads + writes
        if candidate > self.traffic_cap_words:
            self._refuse(
                "traffic_cap",
                {"bucket": bucket, "cap": self.traffic_cap_words, "candidate": candidate},
            )
        self.traffic[bucket]["reads"] += reads
        self.traffic[bucket]["writes"] += writes

    def _check_local_matrix(self, shape: Sequence[int], phase: str) -> None:
        words = int(np.prod(tuple(shape), dtype=np.int64))
        self.maximum_local_matrix_words = max(self.maximum_local_matrix_words, words)
        if words > self.resource_gates["maximum_local_matrix_words"]:
            self._refuse(
                "maximum_local_matrix_words",
                {"phase": phase, "shape": list(shape), "words": words},
            )

    def _check_tt_words(self, words: int, label: str) -> None:
        self.maximum_tt_object_words = max(self.maximum_tt_object_words, words)
        if words > self.resource_gates["maximum_tt_object_words"]:
            self._refuse(
                "maximum_tt_object_words",
                {"label": label, "words": words},
            )

    def _observe_live_words(self, words: int, phase: str) -> None:
        self.peak_live_field_words = max(self.peak_live_field_words, words)
        if words > self.resource_gates["predicted_peak_live_field_words"]:
            self._refuse(
                "predicted_peak_live_field_words",
                {"phase": phase, "words": words},
            )

    def _operation_delta(self, before: Mapping[str, int]) -> dict[str, int]:
        return {
            key: self.operations[key] - int(before[key]) for key in OPERATION_KEYS
        }

    def _traffic_delta(
        self, before: Mapping[str, Mapping[str, int]]
    ) -> dict[str, dict[str, int]]:
        return {
            key: {
                "reads": self.traffic[key]["reads"] - int(before[key]["reads"]),
                "writes": self.traffic[key]["writes"] - int(before[key]["writes"]),
            }
            for key in TARGET_TRAFFIC_KEYS
        }

    @staticmethod
    def _traffic_snapshot(
        traffic: Mapping[str, Mapping[str, int]],
    ) -> dict[str, dict[str, int]]:
        return {
            key: {"reads": int(row["reads"]), "writes": int(row["writes"])}
            for key, row in traffic.items()
        }

    def _assert_canonical_array(self, array: np.ndarray, p: int, label: str) -> None:
        if array.dtype != np.dtype(np.int64) or array.ndim > 3:
            raise AssertionError(f"{label} is not an int64 array of at most three dimensions")
        self._charge(comparisons=2 * int(array.size))
        self._charge_traffic("digest_read", reads=int(array.size))
        for raw_value in array.flat:
            value = int(raw_value)
            if value < 0 or value >= p:
                raise AssertionError(f"{label} contains a noncanonical field residue")

    @staticmethod
    def _immutable_array(values: np.ndarray, p: int) -> np.ndarray:
        result = np.array(values, dtype=np.int64, order="C", copy=True)
        if result.ndim != 3:
            raise ValueError("TT cores must be three-dimensional")
        for raw_value in result.flat:
            value = int(raw_value)
            if value < 0 or value >= p:
                raise ValueError("TT core contains a noncanonical field residue")
        result.flags.writeable = False
        return result

    @staticmethod
    def _freeze_owned_array(values: np.ndarray, p: int) -> np.ndarray:
        if (
            values.dtype != np.dtype(np.int64)
            or values.ndim != 3
            or not values.flags.c_contiguous
        ):
            raise ValueError("owned TT core is not a C-order int64 three-array")
        for raw_value in values.flat:
            value = int(raw_value)
            if value < 0 or value >= p:
                raise ValueError("owned TT core contains a noncanonical field residue")
        values.flags.writeable = False
        return values

    def tensor_from_record(
        self,
        record: Mapping[str, Any],
        *,
        expected_name: str | None = None,
    ) -> Tensor:
        """Import one canonical source-advice tensor without retaining aliases."""

        before_operations = dict(self.operations)
        before_traffic = self._traffic_snapshot(self.traffic)
        name = record.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("tensor.name must be a nonempty string")
        if expected_name is not None and name != expected_name:
            raise ValueError(f"tensor name {name!r} does not match {expected_name!r}")
        p = _exact_int(record.get("p"), "tensor.p", 2)
        B = _exact_int(record.get("B"), "tensor.B", 1)
        tag = record.get("tag")
        ranks_value = record.get("ranks")
        cores_value = record.get("cores")
        if not isinstance(ranks_value, list) or len(ranks_value) != 4:
            raise ValueError("tensor.ranks must contain four integers")
        recorded_ranks = tuple(
            _exact_int(value, f"tensor.ranks[{index}]", 0)
            for index, value in enumerate(ranks_value)
        )
        if not isinstance(cores_value, list):
            raise ValueError("tensor.cores must be a list")
        if tag == "canonical_zero":
            if recorded_ranks != (0, 0, 0, 0) or cores_value:
                raise ValueError("canonical zero has nonzero ranks or cores")
            tensor = Tensor(name, p, B, "canonical_zero", ())
        elif tag == "tt":
            if len(cores_value) != 5 or any(rank < 1 for rank in recorded_ranks):
                raise ValueError("nonzero tensor has invalid ranks or core count")
            boundaries = (1, *recorded_ranks, 1)
            cores: list[Core] = []
            for mode, raw_core in enumerate(cores_value):
                if not isinstance(raw_core, Mapping):
                    raise ValueError(f"tensor.cores[{mode}] must be an object")
                expected_shape = (boundaries[mode], B, boundaries[mode + 1])
                shape_value = raw_core.get("shape")
                if not isinstance(shape_value, list) or tuple(shape_value) != expected_shape:
                    raise ValueError(
                        f"tensor.cores[{mode}].shape does not match {expected_shape}"
                    )
                flat_values = raw_core.get("values")
                if not isinstance(flat_values, list) or len(flat_values) != int(
                    np.prod(expected_shape, dtype=np.int64)
                ):
                    raise ValueError(f"tensor.cores[{mode}].values has the wrong length")
                parsed = np.fromiter(
                    (
                        _exact_int(value, f"tensor.cores[{mode}].values", 0)
                        for value in flat_values
                    ),
                    dtype=np.int64,
                    count=len(flat_values),
                ).reshape(expected_shape)
                cores.append(Core(self._freeze_owned_array(parsed, p)))
            tensor = Tensor(name, p, B, "tt", tuple(cores))
            if tensor.ranks != recorded_ranks:
                raise AssertionError("imported tensor ranks changed during parsing")
        else:
            raise ValueError("tensor.tag must be 'tt' or 'canonical_zero'")
        self._check_tt_words(tensor.words, name)
        self._charge(comparisons=2 * tensor.words)
        self._charge_traffic("digest_read", reads=tensor.words)
        candidate_source_words = self.persistent_source_words + tensor.words
        predicted_live = self.persistent_input_field_words + candidate_source_words
        self._observe_live_words(predicted_live, "source_advice_import")
        self._charge(copied_words=2 * tensor.words)
        self._charge_traffic(
            "advice_deserialize", reads=tensor.words, writes=tensor.words
        )
        self.persistent_source_words = candidate_source_words
        self.counts["imported_source_tensors"] += 1
        self.events.append(
            {
                "kind": "source_advice_import",
                "name": name,
                "operation_vector": self._operation_delta(before_operations),
                "traffic": self._traffic_delta(before_traffic),
                "words": tensor.words,
                "persistent_source_words": self.persistent_source_words,
                "predicted_live_field_words": predicted_live,
            }
        )
        return tensor

    def tensor_from_cores(
        self,
        *,
        name: str,
        p: int,
        B: int,
        cores: Sequence[np.ndarray],
    ) -> Tensor:
        """Construct a canonical tensor for development controls and tests."""

        if len(cores) != 5:
            raise ValueError("a nonzero TT requires five cores")
        immutable = tuple(Core(self._immutable_array(core, p)) for core in cores)
        prior = 1
        for mode, core in enumerate(immutable):
            left, physical, right = core.shape
            if left != prior or physical != B or right < 1:
                raise ValueError(f"core {mode} does not satisfy TT boundaries")
            prior = right
        if prior != 1:
            raise ValueError("last TT core must have right boundary one")
        tensor = Tensor(name, p, B, "tt", immutable)
        self._check_tt_words(tensor.words, name)
        return tensor

    def _tensor_from_owned_cores(
        self,
        *,
        name: str,
        p: int,
        B: int,
        cores: Sequence[np.ndarray],
    ) -> Tensor:
        if len(cores) != 5:
            raise ValueError("a nonzero TT requires five owned cores")
        wrapped: list[Core] = []
        prior = 1
        for mode, core in enumerate(cores):
            if (
                core.dtype != np.dtype(np.int64)
                or core.ndim != 3
                or not core.flags.c_contiguous
            ):
                raise AssertionError("owned target core violates its dense-array certificate")
            left, physical, right = (int(value) for value in core.shape)
            if left != prior or physical != B or right < 1:
                raise ValueError(f"owned target core {mode} does not satisfy TT boundaries")
            core.flags.writeable = False
            wrapped.append(Core(core))
            prior = right
        if prior != 1:
            raise ValueError("last owned target core must have right boundary one")
        tensor = Tensor(name, p, B, "tt", tuple(wrapped))
        self._check_tt_words(tensor.words, name)
        return tensor

    @staticmethod
    def zero_tensor(*, name: str, p: int, B: int) -> Tensor:
        return Tensor(name, p, B, "canonical_zero", ())

    def _rank_factor(
        self,
        matrix: np.ndarray,
        *,
        p: int,
        phase: str,
        mode: int,
        target_label: str,
        current_tt_words: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        before_operations = dict(self.operations)
        before_traffic = self._traffic_snapshot(self.traffic)
        if matrix.ndim != 2 or matrix.dtype != np.dtype(np.int64):
            raise AssertionError("rank factorization requires an int64 matrix")
        self._assert_canonical_array(matrix, p, "rank-factor input")
        m, n = (int(matrix.shape[0]), int(matrix.shape[1]))
        words = m * n
        self._check_local_matrix((m, n), phase)
        maximum_rank = min(m, n)
        maximum_factor_words = m * maximum_rank + maximum_rank * n
        predicted_live = (
            self.persistent_field_words
            + current_tt_words
            + words
            + n
            + maximum_factor_words
        )
        self._observe_live_words(predicted_live, f"{target_label}:{phase}:{mode}:factor")
        self._charge(copied_words=2 * words)
        self._charge_traffic("factor_input_copy", reads=words, writes=words)
        work = np.array(matrix, dtype=np.int64, order="C", copy=True)
        row_temp = np.empty((n,), dtype=np.int64)
        pivot_columns: list[int] = []
        pivot_rows: list[int] = []
        used_rows: set[int] = set()
        pivot_scan_count = 0
        elimination_scan_count = 0
        elimination_nonzero_count = 0
        for column in range(n):
            chosen: int | None = None
            for row in range(m):
                if row in used_rows:
                    continue
                pivot_scan_count += 1
                self._charge(comparisons=1)
                self._charge_traffic("pivot_scan", reads=1)
                if int(work[row, column]) != 0:
                    chosen = row
                    break
            if chosen is None:
                continue
            pivot = int(work[chosen, column])
            inverse = pow(pivot, -1, p)
            self._charge(inversions=1, reductions=1, comparisons=1)
            self._charge(muls=n, reductions=n)
            self._charge_traffic("row_normalization", reads=2 * n, writes=2 * n)
            np.multiply(work[chosen, :], inverse, out=work[chosen, :])
            np.remainder(work[chosen, :], p, out=work[chosen, :])
            for row in range(m):
                if row == chosen:
                    continue
                elimination_scan_count += 1
                factor = int(work[row, column])
                self._charge(comparisons=1)
                self._charge_traffic("elimination", reads=1)
                if factor == 0:
                    continue
                elimination_nonzero_count += 1
                self._charge(muls=n, subs=n, reductions=2 * n)
                self._charge_traffic("elimination", reads=5 * n, writes=4 * n)
                np.multiply(work[chosen, :], factor, out=row_temp)
                np.remainder(row_temp, p, out=row_temp)
                np.subtract(work[row, :], row_temp, out=work[row, :])
                np.remainder(work[row, :], p, out=work[row, :])
            used_rows.add(chosen)
            pivot_columns.append(column)
            pivot_rows.append(chosen)
        rank = len(pivot_columns)
        factor_words = m * rank + rank * n
        self._charge(copied_words=2 * factor_words)
        self._charge_traffic("factor_output", reads=factor_words, writes=factor_words)
        left = np.empty((m, rank), dtype=np.int64)
        right = np.empty((rank, n), dtype=np.int64)
        for factor_column, source_column in enumerate(pivot_columns):
            left[:, factor_column] = matrix[:, source_column]
        for factor_row, source_row in enumerate(pivot_rows):
            right[factor_row, :] = work[source_row, :]
        self._assert_canonical_array(left, p, "rank-factor left output")
        self._assert_canonical_array(right, p, "rank-factor right output")
        certificate = {
            "current_tt_words": current_tt_words,
            "elimination_nonzero_count": elimination_nonzero_count,
            "elimination_scan_count": elimination_scan_count,
            "input_shape": [m, n],
            "left_shape": [m, rank],
            "mode": mode,
            "phase": phase,
            "pivot_columns": pivot_columns,
            "pivot_rows": pivot_rows,
            "pivot_scan_count": pivot_scan_count,
            "predicted_live_field_words": predicted_live,
            "rank": rank,
            "right_shape": [rank, n],
            "target_label": target_label,
        }
        certificate_payload = canonical_json_bytes(certificate)
        self._charge(hash_bytes=len(certificate_payload))
        self.counts["two_sweep_factorizations"] += 1
        self.counts["total_rank_factorizations"] += 1
        self.events.append(
            {
                "kind": "rank_factor",
                "mode": mode,
                "phase": phase,
                "target_label": target_label,
                "input_shape": [m, n],
                "rank": rank,
                "pivot_columns": pivot_columns,
                "pivot_rows": pivot_rows,
                "factor_digest_sha256": hashlib.sha256(certificate_payload).hexdigest(),
                "certificate": certificate,
                "operation_vector": self._operation_delta(before_operations),
                "traffic": self._traffic_delta(before_traffic),
                "predicted_live_field_words": predicted_live,
            }
        )
        return left, right

    def _matmul(
        self,
        left: np.ndarray,
        right: np.ndarray,
        *,
        p: int,
        current_tt_words: int,
        transient_words: int,
        target_label: str,
        phase: str,
        mode: int,
    ) -> np.ndarray:
        before_operations = dict(self.operations)
        before_traffic = self._traffic_snapshot(self.traffic)
        if left.ndim != 2 or right.ndim != 2 or left.shape[1] != right.shape[0]:
            raise AssertionError("sweep matrices do not join")
        self._assert_canonical_array(left, p, "sweep left input")
        self._assert_canonical_array(right, p, "sweep right input")
        inner = int(left.shape[1])
        products = int(left.shape[0]) * inner * int(right.shape[1])
        output_words = int(left.shape[0]) * int(right.shape[1])
        additions = output_words * max(inner - 1, 0)
        bound = inner * (p - 1) * (p - 1)
        self.maximum_int64_dot_length = max(self.maximum_int64_dot_length, inner)
        self.maximum_int64_accumulator_bound = max(
            self.maximum_int64_accumulator_bound, bound
        )
        if inner > self.resource_gates["maximum_int64_dot_length"]:
            self._refuse("maximum_int64_dot_length", {"inner": inner})
        if (
            bound > self.resource_gates["maximum_int64_accumulator_bound"]
            or bound >= self.resource_gates["signed_int64_maximum"]
        ):
            self._refuse("maximum_int64_accumulator_bound", {"bound": bound})
        predicted_live = (
            self.persistent_field_words
            + current_tt_words
            + transient_words
            + output_words
        )
        self._observe_live_words(
            predicted_live, f"{target_label}:{phase}:{mode}:absorption"
        )
        self._charge(
            muls=products,
            adds=additions,
            reductions=output_words,
            comparisons=4,
        )
        self._charge_traffic(
            "sweep_absorption",
            reads=2 * products + output_words,
            writes=2 * output_words,
        )
        output = np.matmul(left, right)
        np.remainder(output, p, out=output)
        self._assert_canonical_array(output, p, "sweep output")
        self.events.append(
            {
                "current_tt_words": current_tt_words,
                "field_modulus": p,
                "inner_dimension": inner,
                "kind": "sweep_absorption",
                "left_shape": [int(value) for value in left.shape],
                "mode": mode,
                "operation_vector": self._operation_delta(before_operations),
                "output_shape": [int(value) for value in output.shape],
                "phase": phase,
                "predicted_live_field_words": predicted_live,
                "right_shape": [int(value) for value in right.shape],
                "target_label": target_label,
                "transient_words": transient_words,
                "traffic": self._traffic_delta(before_traffic),
            }
        )
        return np.asarray(output, dtype=np.int64, order="C")

    def _normalize(
        self,
        cores: Sequence[np.ndarray],
        *,
        p: int,
        B: int,
        label: str,
    ) -> Tensor:
        self.counts["normalization_calls"] += 1
        mutable = cores if isinstance(cores, list) else list(cores)
        if not mutable:
            self.counts["zero_results"] += 1
            return self.zero_tensor(name=label, p=p, B=B)
        live_words = sum(int(core.size) for core in mutable)
        self._observe_live_words(
            self.persistent_field_words + live_words,
            f"{label}:target_normalization_input",
        )
        for mode in range(4):
            left_rank, _, right_rank = mutable[mode].shape
            matrix = mutable[mode].reshape(int(left_rank) * B, int(right_rank))
            left, right = self._rank_factor(
                matrix,
                p=p,
                phase="left_sweep",
                mode=mode,
                target_label=label,
                current_tt_words=sum(int(core.size) for core in mutable),
            )
            rank = int(left.shape[1])
            if rank == 0:
                self.counts["zero_results"] += 1
                return self.zero_tensor(name=label, p=p, B=B)
            mutable[mode] = left.reshape(int(left_rank), B, rank)
            neighbor = mutable[mode + 1]
            neighbor_right = int(neighbor.shape[2])
            current_tt_words = sum(int(core.size) for core in mutable)
            mutable[mode + 1] = self._matmul(
                right,
                neighbor.reshape(int(right_rank), B * neighbor_right),
                p=p,
                current_tt_words=current_tt_words,
                transient_words=int(matrix.size + right.size),
                target_label=label,
                phase="left_sweep",
                mode=mode,
            ).reshape(rank, B, neighbor_right)
            self._observe_live_words(
                self.persistent_field_words + sum(int(core.size) for core in mutable),
                f"{label}:left_sweep",
            )
            del matrix, left, right, neighbor
        for mode in range(4, 0, -1):
            left_rank, _, right_rank = mutable[mode].shape
            matrix = mutable[mode].reshape(int(left_rank), B * int(right_rank))
            left, right = self._rank_factor(
                matrix,
                p=p,
                phase="right_sweep",
                mode=mode,
                target_label=label,
                current_tt_words=sum(int(core.size) for core in mutable),
            )
            rank = int(left.shape[1])
            if rank == 0:
                self.counts["zero_results"] += 1
                return self.zero_tensor(name=label, p=p, B=B)
            mutable[mode] = right.reshape(rank, B, int(right_rank))
            neighbor = mutable[mode - 1]
            neighbor_left = int(neighbor.shape[0])
            current_tt_words = sum(int(core.size) for core in mutable)
            mutable[mode - 1] = self._matmul(
                neighbor.reshape(neighbor_left * B, int(left_rank)),
                left,
                p=p,
                current_tt_words=current_tt_words,
                transient_words=int(matrix.size + left.size),
                target_label=label,
                phase="right_sweep",
                mode=mode,
            ).reshape(neighbor_left, B, rank)
            self._observe_live_words(
                self.persistent_field_words + sum(int(core.size) for core in mutable),
                f"{label}:right_sweep",
            )
            del matrix, left, right, neighbor
        result = self._tensor_from_owned_cores(name=label, p=p, B=B, cores=mutable)
        return result

    def weighted_sum(
        self,
        tensors: Sequence[Tensor],
        coefficients: Sequence[int],
        *,
        label: str,
    ) -> Tensor:
        """Build and exactly recompress a target linear combination."""

        if not tensors or len(tensors) != len(coefficients):
            raise ValueError("weighted sum requires matching nonempty inputs")
        p = tensors[0].p
        B = tensors[0].B
        if any(tensor.p != p or tensor.B != B for tensor in tensors):
            raise ValueError("weighted-sum tensors do not share p and B")
        before_operations = dict(self.operations)
        before_traffic = self._traffic_snapshot(self.traffic)
        normalized_coefficients = tuple(
            _exact_int(value, f"coefficients[{index}]") % p
            for index, value in enumerate(coefficients)
        )
        self._charge(reductions=len(normalized_coefficients))
        self._charge_traffic("coefficient_input", reads=len(normalized_coefficients))
        term_records = [
            {
                "coefficient": coefficient,
                "core_words": [core.words for core in tensor.cores],
                "is_zero": tensor.is_zero,
                "name": tensor.name,
                "ranks": list(tensor.ranks),
            }
            for tensor, coefficient in zip(tensors, normalized_coefficients)
        ]
        active = [
            (tensor, coefficient)
            for tensor, coefficient in zip(tensors, normalized_coefficients)
            if not tensor.is_zero and coefficient != 0
        ]
        self.counts["target_linear_combinations"] += 1
        if not active:
            result = self._normalize((), p=p, B=B, label=label)
            self.events.append(
                {
                    "field_modulus": p,
                    "kind": "target_direct_sum",
                    "label": label,
                    "operation_vector": self._operation_delta(before_operations),
                    "physical_mode_size": B,
                    "predicted_live_field_words": self.persistent_field_words,
                    "raw_ranks": [0, 0, 0, 0],
                    "raw_words": 0,
                    "source_terms": term_records,
                    "traffic": self._traffic_delta(before_traffic),
                }
            )
            self.events.append(
                {
                    "kind": "target_linear_combination",
                    "label": label,
                    "coefficients": list(normalized_coefficients),
                    "raw_ranks": [0, 0, 0, 0],
                    "output_ranks": [0, 0, 0, 0],
                    "predicted_live_field_words": self.persistent_field_words,
                    "operation_vector": _empty_operations(),
                    "traffic": _empty_traffic(),
                }
            )
            return result
        raw_ranks = tuple(
            sum(tensor.ranks[cut] for tensor, _ in active) for cut in range(4)
        )
        boundaries = (1, *raw_ranks, 1)
        shapes = [
            (boundaries[mode], B, boundaries[mode + 1]) for mode in range(5)
        ]
        raw_words = sum(int(np.prod(shape, dtype=np.int64)) for shape in shapes)
        self._check_tt_words(raw_words, f"{label}:raw")
        predicted_direct_sum_live = self.persistent_field_words + raw_words
        self._observe_live_words(
            predicted_direct_sum_live, f"{label}:target_direct_sum_preallocation"
        )
        self._charge(copied_words=raw_words)
        self._charge_traffic("allocation_zero_fill", writes=raw_words)
        raw_cores = [np.zeros(shape, dtype=np.int64, order="C") for shape in shapes]
        left_offsets = [0] * 5
        right_offsets = [0] * 5
        for mode, destination_core in enumerate(raw_cores):
            for tensor, coefficient in active:
                source = tensor.cores[mode].data
                left_size, _, right_size = source.shape
                left_start = 0 if mode == 0 else left_offsets[mode]
                right_start = 0 if mode == 4 else right_offsets[mode]
                destination = destination_core[
                    left_start : left_start + int(left_size),
                    :,
                    right_start : right_start + int(right_size),
                ]
                if mode == 0 and coefficient != 1:
                    if coefficient == p - 1:
                        self._charge(subs=int(source.size), reductions=int(source.size))
                        np.subtract(0, source, out=destination)
                    else:
                        self._charge(muls=int(source.size), reductions=int(source.size))
                        np.multiply(source, coefficient, out=destination)
                    np.remainder(destination, p, out=destination)
                else:
                    self._charge(copied_words=2 * int(source.size))
                    destination[...] = source
                passes = 2 if mode == 0 and coefficient != 1 else 1
                self._charge_traffic(
                    "direct_sum_copy",
                    reads=passes * int(source.size),
                    writes=passes * int(source.size),
                )
                if mode > 0:
                    left_offsets[mode] += int(left_size)
                if mode < 4:
                    right_offsets[mode] += int(right_size)
        self.events.append(
            {
                "field_modulus": p,
                "kind": "target_direct_sum",
                "label": label,
                "operation_vector": self._operation_delta(before_operations),
                "physical_mode_size": B,
                "predicted_live_field_words": predicted_direct_sum_live,
                "raw_ranks": list(raw_ranks),
                "raw_words": raw_words,
                "source_terms": term_records,
                "traffic": self._traffic_delta(before_traffic),
            }
        )
        result = self._normalize(raw_cores, p=p, B=B, label=label)
        self.events.append(
            {
                "kind": "target_linear_combination",
                "label": label,
                "coefficients": list(normalized_coefficients),
                "raw_ranks": list(raw_ranks),
                "raw_words": raw_words,
                "output_ranks": list(result.ranks),
                "predicted_live_field_words": self.peak_live_field_words,
                "operation_vector": _empty_operations(),
                "traffic": _empty_traffic(),
            }
        )
        return result

    def derive_target_coefficients(
        self,
        *,
        label: str,
        kind: str,
        projective: Sequence[int],
        p: int,
        norm_n: int,
        frozen_coefficients: Sequence[int],
        trace_t: int | None = None,
    ) -> tuple[int, int, int, int, int, int]:
        """Derive and meter one frozen six-term target coefficient vector."""

        before_operations = dict(self.operations)
        before_traffic = self._traffic_snapshot(self.traffic)
        if kind == "trace_zero":
            expected_operations = {
                "adds": 1,
                "subs": 2,
                "muls": 7,
                "squares": 3,
                "reductions": 8,
                "comparisons": 17,
            }
            registry_reads = 4
        elif kind == "general_trace":
            if trace_t is None:
                raise ValueError("general-trace coefficient formation requires trace_t")
            expected_operations = {
                "adds": 4,
                "subs": 2,
                "muls": 12,
                "squares": 3,
                "reductions": 10,
                "comparisons": 17,
            }
            registry_reads = 5
        else:
            raise ValueError(f"unknown target coefficient kind {kind!r}")
        self._charge(**expected_operations)
        self._charge_traffic("registry_input", reads=registry_reads)
        self._charge_traffic("coefficient_input", writes=6)
        if kind == "trace_zero":
            coefficients = trace_zero_coefficients(projective, p, norm_n)
        else:
            coefficients = general_basis_coefficients(
                projective, p, int(trace_t), norm_n
            )
        if len(frozen_coefficients) != 6:
            raise ValueError("frozen target coefficient vector must have six entries")
        mismatch = False
        for observed, frozen in zip(coefficients, frozen_coefficients):
            if observed != frozen:
                mismatch = True
        if mismatch:
            raise ValueError(f"{label} frozen target coefficients changed")
        self.counts["target_coefficient_formations"] += 1
        self.events.append(
            {
                "coefficients": list(coefficients),
                "field_modulus": p,
                "kind": "target_coefficient_formation",
                "label": label,
                "operation_vector": self._operation_delta(before_operations),
                "projective": list(projective),
                "target_coefficient_kind": kind,
                "traffic": self._traffic_delta(before_traffic),
            }
        )
        return coefficients

    def record_artifact_digest(
        self,
        value: Any,
        *,
        label: str,
        field_words: int,
    ) -> str:
        """Serialize and hash one target artifact with a disjoint event."""

        field_words = _exact_int(field_words, "artifact.field_words", 0)
        payload = canonical_json_bytes(value) + b"\n"
        before_operations = dict(self.operations)
        before_traffic = self._traffic_snapshot(self.traffic)
        self._charge(copied_words=field_words, hash_bytes=len(payload))
        self._charge_traffic("artifact_serialize", reads=field_words)
        digest = hashlib.sha256(payload).hexdigest()
        self.counts["artifact_serialization_events"] += 1
        self.events.append(
            {
                "digest_sha256": digest,
                "field_words": field_words,
                "kind": "target_artifact_serialization",
                "label": label,
                "operation_vector": self._operation_delta(before_operations),
                "payload_bytes": len(payload),
                "serialization_passes": 1,
                "size_scan_passes": 0,
                "traffic": self._traffic_delta(before_traffic),
                "variant": "digest",
            }
        )
        return digest

    def record_output_serialization(
        self,
        *,
        label: str,
        field_words: int,
        size_scan_passes: int,
        serialization_passes: int,
    ) -> None:
        """Precharge deterministic size scans and full output serializations."""

        field_words = _exact_int(field_words, "output.field_words", 0)
        size_scan_passes = _exact_int(
            size_scan_passes, "output.size_scan_passes", 0
        )
        serialization_passes = _exact_int(
            serialization_passes, "output.serialization_passes", 0
        )
        before_operations = dict(self.operations)
        before_traffic = self._traffic_snapshot(self.traffic)
        self._charge(copied_words=serialization_passes * field_words)
        self._charge_traffic(
            "artifact_serialize",
            reads=(size_scan_passes + serialization_passes) * field_words,
        )
        self.counts["artifact_serialization_events"] += 1
        self.events.append(
            {
                "field_words": field_words,
                "kind": "target_artifact_serialization",
                "label": label,
                "operation_vector": self._operation_delta(before_operations),
                "serialization_passes": serialization_passes,
                "size_scan_passes": size_scan_passes,
                "traffic": self._traffic_delta(before_traffic),
                "variant": "output",
            }
        )

    def target_record(self, tensor: Tensor) -> dict[str, Any]:
        """Serialize one target tensor with a disjoint accounting event."""

        before_operations = dict(self.operations)
        before_traffic = self._traffic_snapshot(self.traffic)
        candidate_output_words = self.persistent_target_output_words + tensor.words
        predicted_live = (
            self.persistent_input_field_words
            + self.persistent_source_words
            + candidate_output_words
            + tensor.words
        )
        self._observe_live_words(predicted_live, f"{tensor.name}:target_emit")
        self._charge(copied_words=2 * tensor.words)
        self._charge_traffic(
            "target_emit", reads=tensor.words, writes=tensor.words
        )
        canonical = tensor.canonical_record()
        payload = canonical_json_bytes(canonical) + b"\n"
        self._charge(hash_bytes=len(payload))
        self._charge_traffic("digest_read", reads=tensor.words)
        digest = hashlib.sha256(payload).hexdigest()
        record = canonical | {
            "core_digest_sha256": digest,
            "word_count": tensor.words,
        }
        self.persistent_target_output_words = candidate_output_words
        self.events.append(
            {
                "core_digest_sha256": digest,
                "kind": "target_emit",
                "label": tensor.name,
                "operation_vector": self._operation_delta(before_operations),
                "persistent_target_output_words": self.persistent_target_output_words,
                "predicted_live_field_words": predicted_live,
                "traffic": self._traffic_delta(before_traffic),
                "payload_bytes": len(payload),
                "words": tensor.words,
            }
        )
        return record

    def record_target_disposal(self, tensor: Tensor) -> None:
        """Record release of target arrays after their canonical record is retained."""

        self.counts["target_disposals"] += 1
        self.events.append(
            {
                "kind": "target_disposal",
                "label": tensor.name,
                "operation_vector": _empty_operations(),
                "persistent_target_output_words": self.persistent_target_output_words,
                "predicted_live_field_words": self.persistent_field_words,
                "traffic": _empty_traffic(),
                "words": tensor.words,
            }
        )

    def evaluate(self, tensor: Tensor, indices: Sequence[int]) -> int:
        if len(indices) != 5:
            raise ValueError("TT evaluation requires five indices")
        if tensor.is_zero:
            return 0
        accumulator = np.array([1], dtype=np.int64)
        for mode, physical_index in enumerate(indices):
            index = _exact_int(physical_index, f"indices[{mode}]", 0)
            if index >= tensor.B:
                raise ValueError("TT evaluation index is out of range")
            core_slice = tensor.cores[mode].data[:, index, :]
            inner = int(core_slice.shape[0])
            products = int(core_slice.shape[1]) * inner
            self._charge(
                muls=products,
                adds=int(core_slice.shape[1]) * max(inner - 1, 0),
                reductions=int(core_slice.shape[1]),
            )
            accumulator = np.matmul(accumulator, core_slice)
            np.remainder(accumulator, tensor.p, out=accumulator)
        if accumulator.shape != (1,):
            raise AssertionError("TT evaluation did not reach a scalar")
        return int(accumulator[0])

    def rss_record(self) -> dict[str, Any]:
        raw_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        rss_bytes = int(raw_rss) if sys.platform == "darwin" else int(raw_rss) * 1024
        if rss_bytes > self.resource_gates["peak_rss_bytes"]:
            self._refuse(
                "peak_rss_bytes",
                {
                    "bytes": rss_bytes,
                    "cap": self.resource_gates["peak_rss_bytes"],
                },
            )
        return {
            "bytes": rss_bytes,
            "raw_ru_maxrss": int(raw_rss),
            "normalization": (
                "Darwin ru_maxrss is bytes"
                if sys.platform == "darwin"
                else "non-Darwin ru_maxrss is KiB multiplied by 1024"
            ),
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": "tt-target-runtime-ledger-v1",
            "operation_vector_order": list(OPERATION_KEYS),
            "operations": dict(self.operations),
            "operation_caps": dict(self.operation_caps),
            "traffic_bucket_order": list(TARGET_TRAFFIC_KEYS),
            "traffic": self.traffic,
            "logical_traffic_words": self.logical_traffic_words,
            "counts": dict(self.counts),
            "events": list(self.events),
            "resources": {
                "maximum_local_matrix_words": self.maximum_local_matrix_words,
                "maximum_tt_object_words": self.maximum_tt_object_words,
                "maximum_int64_dot_length": self.maximum_int64_dot_length,
                "maximum_int64_accumulator_bound": self.maximum_int64_accumulator_bound,
                "peak_live_field_words": self.peak_live_field_words,
                "persistent_input_field_words": self.persistent_input_field_words,
                "persistent_source_words": self.persistent_source_words,
                "persistent_target_output_words": self.persistent_target_output_words,
                "rss": self.rss_record(),
            },
            "first_refusal": self.first_refusal,
        }
