#!/usr/bin/env python3
"""Exact finite-field tensor-train runtime for the source compiler.

The runtime deliberately exposes a small, audit-friendly surface.  All dense
arrays are C-order ``numpy.int64`` arrays with at most three dimensions.  TT
addition is a direct sum, TT multiplication is the frozen two-stage streamed
contraction, and every nontrivial sum or product is normalized by exact
left-to-right and then right-to-left finite-field rank factorizations.

This module does not read experiment data.  The producer owns the two permitted
data reads and passes the reviewed operation, traffic, and resource policy in.
"""
from __future__ import annotations

import hashlib
import json
import platform
import resource
import time
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


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

SOURCE_TRAFFIC_KEYS = (
    "registry_input",
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
    "digest_read",
    "artifact_serialize",
)

IR_NODE_KINDS = (
    "input_coordinate",
    "scale",
    "direct_sum",
    "stage_a_contract",
    "stage_b_contract",
    "rank_factor",
    "absorb_left",
    "absorb_right",
    "emit",
    "free",
)


def canonical_json_bytes(value: Any) -> bytes:
    """Return the protocol's UTF-8 sorted-key compact JSON encoding."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def stable_digest(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def field_width(p: int) -> int:
    if p <= 1:
        raise ValueError("field modulus must exceed one")
    return max(1, (p.bit_length() + 7) // 8)


def empty_operations() -> dict[str, int]:
    return {key: 0 for key in OPERATION_KEYS}


def empty_traffic(keys: Sequence[str] = SOURCE_TRAFFIC_KEYS) -> dict[str, dict[str, int]]:
    return {key: {"reads": 0, "writes": 0} for key in keys}


def add_vectors(left: Mapping[str, int], right: Mapping[str, int]) -> dict[str, int]:
    return {key: int(left.get(key, 0)) + int(right.get(key, 0)) for key in OPERATION_KEYS}


def subtract_vectors(left: Mapping[str, int], right: Mapping[str, int]) -> dict[str, int]:
    return {key: int(left.get(key, 0)) - int(right.get(key, 0)) for key in OPERATION_KEYS}


def _product(shape: Sequence[int]) -> int:
    value = 1
    for dimension in shape:
        if not isinstance(dimension, int) or dimension < 0:
            raise ValueError(f"invalid array dimension {dimension!r}")
        value *= dimension
    return value


class ResourceRefusal(RuntimeError):
    """A pre-allocation or cumulative protocol gate refused an operation."""

    def __init__(self, reason: str, detail: Mapping[str, Any]):
        self.reason = reason
        self.detail = dict(detail)
        super().__init__(f"{reason}: {self.detail}")


@dataclass
class Allocation:
    allocation_id: str
    shape: tuple[int, ...]
    words: int
    role: str
    producer_event_id: str
    live: bool = True
    digest_sha256: str | None = None


@dataclass
class Buffer:
    data: np.ndarray
    allocation_id: str
    role: str
    canonical: bool = False
    maximum_value_bound: int = 0
    value_digest_sha256: str | None = None

    @property
    def shape(self) -> tuple[int, ...]:
        return tuple(int(value) for value in self.data.shape)

    @property
    def words(self) -> int:
        return int(self.data.size)


@dataclass
class TT:
    tt_id: str
    p: int
    B: int
    cores: tuple[Buffer, ...]
    tag: str = "nonzero"
    label: str = ""
    released: bool = False
    value_digest_sha256: str | None = None

    @property
    def is_zero(self) -> bool:
        return self.tag == "canonical_zero"

    @property
    def ranks(self) -> tuple[int, int, int, int]:
        if self.is_zero:
            return (0, 0, 0, 0)
        return tuple(int(self.cores[index].data.shape[2]) for index in range(4))  # type: ignore[return-value]

    @property
    def words(self) -> int:
        return sum(core.words for core in self.cores)


class TTRuntime:
    """Exact TT interpreter with closed-IR tracing and cumulative accounting."""

    def __init__(
        self,
        *,
        operation_caps: Mapping[str, int],
        traffic_keys: Sequence[str],
        resource_gates: Mapping[str, Any],
        detailed_cell: str = "C08:random_unique",
    ) -> None:
        if tuple(traffic_keys) != SOURCE_TRAFFIC_KEYS:
            raise ValueError("source traffic bucket order does not match protocol")
        self.operation_caps = {key: int(operation_caps[key]) for key in OPERATION_KEYS}
        self.traffic_keys = tuple(traffic_keys)
        self.resource_gates = dict(resource_gates)
        self.detailed_cell = detailed_cell
        self.operations = empty_operations()
        self.traffic = empty_traffic(self.traffic_keys)
        self.events: list[dict[str, Any]] = []
        self.operation_records: list[dict[str, Any]] = []
        self.allocations: dict[str, Allocation] = {}
        self.buffers: dict[str, Buffer] = {}
        self.current_live_words = 0
        self.peak_live_words = 0
        self.maximum_ndarray_dimensions = 0
        self.maximum_local_matrix_words = 0
        self.maximum_tt_object_words = 0
        self.maximum_int64_dot_length = 0
        self.maximum_int64_accumulator_bound = 0
        self._event_counter = 0
        self._allocation_counter = 0
        self._tt_counter = 0
        self._operation_counter = 0
        self._start_ns = time.perf_counter_ns()
        self.first_refusal: dict[str, Any] | None = None
        self.counts = {
            "normalization_calls": 0,
            "streamed_prefix_factorizations": 0,
            "two_sweep_factorizations": 0,
            "rank_factorizations": 0,
            "full_tuple_enumerations": 0,
            "full_tuple_values_read": 0,
            "diagnostic_sample_count": 0,
            "diagnostic_rcb_calls": 0,
            "prior_artifact_reads": 0,
            "target_manifest_reads_in_source_phase": 0,
            "mutation_manifest_reads_in_source_phase": 0,
            "dynamic_code_events": 0,
            "child_processes": 0,
            "network_events": 0,
            "maximum_live_mode_indices": 0,
        }
        self.ir_kind_counts = {key: 0 for key in IR_NODE_KINDS}

    def _next_event_id(self) -> str:
        self._event_counter += 1
        return f"e{self._event_counter:08d}"

    def _next_allocation_id(self) -> str:
        self._allocation_counter += 1
        return f"a{self._allocation_counter:08d}"

    def _next_tt_id(self) -> str:
        self._tt_counter += 1
        return f"tt{self._tt_counter:08d}"

    def _begin_event(self, kind: str, metadata: Mapping[str, Any] | None = None) -> dict[str, Any]:
        if kind not in IR_NODE_KINDS:
            raise ValueError(f"unaccepted IR node kind {kind!r}")
        event_id = self._next_event_id()
        return {
            "event_id": event_id,
            "sequence": self._event_counter,
            "kind": kind,
            "metadata": dict(metadata or {}),
            "inputs": [],
            "outputs": [],
            "allocations": [],
            "operations": empty_operations(),
            "traffic": empty_traffic(self.traffic_keys),
            "liveness_before_words": self.current_live_words,
            "_start_ns": time.perf_counter_ns(),
        }

    def _refuse(self, reason: str, detail: Mapping[str, Any]) -> None:
        record = {
            "reason": reason,
            "detail": dict(detail),
            "cumulative_operations": dict(self.operations),
            "cumulative_traffic_words": self.logical_traffic_words,
            "current_live_words": self.current_live_words,
            "peak_live_words": self.peak_live_words,
        }
        if self.first_refusal is None:
            self.first_refusal = record
        raise ResourceRefusal(reason, record)

    def _charge_operations(self, event: dict[str, Any], **increments: int) -> None:
        for key, raw_value in increments.items():
            if key not in OPERATION_KEYS:
                raise ValueError(f"unknown operation component {key!r}")
            value = int(raw_value)
            if value < 0:
                raise ValueError("operation charges must be nonnegative")
            candidate = self.operations[key] + event["operations"][key] + value
            if candidate > self.operation_caps[key]:
                self._refuse(
                    "cumulative_component_cap",
                    {
                        "component": key,
                        "cap": self.operation_caps[key],
                        "requested_increment": value,
                        "candidate": candidate,
                        "event": event["metadata"],
                    },
                )
            event["operations"][key] += value

    def _charge_traffic(
        self,
        event: dict[str, Any],
        bucket: str,
        *,
        reads: int = 0,
        writes: int = 0,
    ) -> None:
        if bucket not in self.traffic:
            raise ValueError(f"unknown traffic bucket {bucket!r}")
        reads = int(reads)
        writes = int(writes)
        if reads < 0 or writes < 0:
            raise ValueError("traffic charges must be nonnegative")
        candidate = self.logical_traffic_words + self._event_traffic_words(event) + reads + writes
        traffic_cap = int(self.resource_gates["maximum_logical_traffic_words"])
        if candidate > traffic_cap:
            self._refuse(
                "cumulative_traffic_cap",
                {
                    "bucket": bucket,
                    "cap": traffic_cap,
                    "candidate": candidate,
                    "event": event["metadata"],
                },
            )
        event["traffic"][bucket]["reads"] += reads
        event["traffic"][bucket]["writes"] += writes

    def _event_traffic_words(self, event: Mapping[str, Any]) -> int:
        return sum(
            int(value["reads"]) + int(value["writes"])
            for value in event["traffic"].values()
        )

    @property
    def logical_traffic_words(self) -> int:
        return sum(
            int(value["reads"]) + int(value["writes"])
            for value in self.traffic.values()
        )

    def _allocate(
        self,
        event: dict[str, Any],
        shape: Sequence[int],
        role: str,
        *,
        zero: bool = False,
        local_matrix: bool = False,
    ) -> Buffer:
        normalized_shape = tuple(int(value) for value in shape)
        if len(normalized_shape) > 3:
            self._refuse(
                "maximum_ndarray_dimensions",
                {"shape": list(normalized_shape), "role": role, "event": event["metadata"]},
            )
        words = _product(normalized_shape)
        if local_matrix:
            self.maximum_local_matrix_words = max(self.maximum_local_matrix_words, words)
            if words > int(self.resource_gates["maximum_local_matrix_words"]):
                self._refuse(
                    "maximum_local_matrix_words",
                    {"shape": list(normalized_shape), "words": words, "event": event["metadata"]},
                )
        candidate_live = self.current_live_words + words
        if candidate_live > int(self.resource_gates["predicted_peak_live_field_words"]):
            self._refuse(
                "predicted_peak_live_field_words",
                {
                    "shape": list(normalized_shape),
                    "role": role,
                    "words": words,
                    "candidate_live_words": candidate_live,
                    "event": event["metadata"],
                },
            )
        if zero:
            self._charge_operations(event, copied_words=words)
            self._charge_traffic(event, "allocation_zero_fill", writes=words)
            array = np.zeros(normalized_shape, dtype=np.int64, order="C")
        else:
            array = np.empty(normalized_shape, dtype=np.int64, order="C")
        if array.dtype != np.dtype(np.int64) or not array.flags.c_contiguous:
            raise AssertionError("dense allocation violated int64 C-order contract")
        allocation_id = self._next_allocation_id()
        allocation = Allocation(
            allocation_id=allocation_id,
            shape=normalized_shape,
            words=words,
            role=role,
            producer_event_id=event["event_id"],
        )
        self.allocations[allocation_id] = allocation
        self.current_live_words = candidate_live
        self.peak_live_words = max(self.peak_live_words, self.current_live_words)
        self.maximum_ndarray_dimensions = max(self.maximum_ndarray_dimensions, len(normalized_shape))
        event["allocations"].append(
            {
                "allocation_id": allocation_id,
                "shape": list(normalized_shape),
                "words": words,
                "role": role,
                "zero_initialized": zero,
            }
        )
        buffer = Buffer(array, allocation_id, role)
        if zero:
            buffer.canonical = True
            buffer.maximum_value_bound = 0
        self.buffers[allocation_id] = buffer
        return buffer

    def _view(self, buffer: Buffer, shape: Sequence[int], role: str | None = None) -> Buffer:
        normalized_shape = tuple(int(value) for value in shape)
        if _product(normalized_shape) != buffer.words:
            raise ValueError("reshape changes field-word count")
        if len(normalized_shape) > 3:
            self._refuse("maximum_ndarray_dimensions", {"shape": list(normalized_shape)})
        view = buffer.data.reshape(normalized_shape, order="C")
        return Buffer(
            view,
            buffer.allocation_id,
            role or buffer.role,
            canonical=buffer.canonical,
            maximum_value_bound=buffer.maximum_value_bound,
            value_digest_sha256=buffer.value_digest_sha256,
        )

    def _seal_buffer(self, event: dict[str, Any], buffer: Buffer, p: int) -> None:
        if buffer.data.dtype != np.dtype(np.int64):
            raise AssertionError("non-int64 buffer cannot be sealed")
        maximum = 0
        digest = hashlib.sha256()
        width = field_width(p)
        for raw_value in buffer.data.flat:
            value = int(raw_value)
            if value < 0 or value >= p:
                raise AssertionError(f"noncanonical residue {value} for F_{p}")
            maximum = max(maximum, value)
            digest.update(value.to_bytes(width, "big"))
        byte_count = width * buffer.words
        self._charge_operations(event, comparisons=2 * buffer.words, hash_bytes=byte_count)
        self._charge_traffic(event, "digest_read", reads=buffer.words)
        buffer.canonical = True
        buffer.maximum_value_bound = maximum
        buffer.value_digest_sha256 = digest.hexdigest()

    def _buffer_descriptor(self, buffer: Buffer) -> dict[str, Any]:
        return {
            "allocation_id": buffer.allocation_id,
            "role": buffer.role,
            "shape": list(buffer.shape),
            "words": buffer.words,
            "value_digest_sha256": buffer.value_digest_sha256,
        }

    def _is_detailed_event(self, event: Mapping[str, Any]) -> bool:
        return event["metadata"].get("cell_id") == self.detailed_cell

    def _transcript_array_record(
        self,
        event: dict[str, Any],
        buffer: Buffer,
    ) -> dict[str, Any]:
        values = [int(value) for value in buffer.data.flat]
        self._charge_operations(event, copied_words=buffer.words)
        self._charge_traffic(event, "artifact_serialize", reads=buffer.words)
        record: dict[str, Any] = {
            "shape": list(buffer.shape),
            "values": values,
        }
        encoded = canonical_json_bytes(record) + b"\n"
        self._charge_operations(event, hash_bytes=len(encoded))
        record["digest_sha256"] = sha256_bytes(encoded)
        return record

    def _finish_event(
        self,
        event: dict[str, Any],
        *,
        inputs: Sequence[Buffer] = (),
        outputs: Sequence[Buffer] = (),
        result: Mapping[str, Any] | None = None,
        semantic_payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        detailed = self._is_detailed_event(event)
        transcript_outputs: list[dict[str, Any]] = []
        for allocation_row in event["allocations"]:
            allocation_id = allocation_row["allocation_id"]
            buffer = self.buffers[allocation_id]
            if not buffer.canonical or buffer.value_digest_sha256 is None:
                raise AssertionError(
                    f"allocation {allocation_id} was not sealed before its IR event finished"
                )
            if detailed:
                array_record = self._transcript_array_record(event, buffer)
                allocation_digest = str(array_record["digest_sha256"])
                transcript_outputs.append(
                    {"array": array_record, "object_id": allocation_id}
                )
            else:
                allocation_digest = buffer.value_digest_sha256
            self.allocations[allocation_id].digest_sha256 = allocation_digest
            allocation_row["digest_sha256"] = allocation_digest

        if detailed:
            if semantic_payload is None:
                raise AssertionError(
                    f"detailed event {event['event_id']} lacks a semantic transcript payload"
                )
            transcript_payload = {
                "outputs": transcript_outputs,
                "semantic": dict(semantic_payload),
            }
            encoded_payload = canonical_json_bytes(transcript_payload) + b"\n"
            self._charge_operations(event, hash_bytes=len(encoded_payload))
            event["transcript_payload"] = transcript_payload
            event["transcript_payload_digest_sha256"] = sha256_bytes(encoded_payload)
        event["inputs"] = [self._buffer_descriptor(value) for value in inputs]
        event["outputs"] = [self._buffer_descriptor(value) for value in outputs]
        event["result"] = dict(result or {})
        event["logical_traffic_words"] = self._event_traffic_words(event)
        event["liveness_after_words"] = self.current_live_words
        event["peak_live_words"] = self.peak_live_words
        event["elapsed_ns"] = time.perf_counter_ns() - int(event.pop("_start_ns"))
        for key in OPERATION_KEYS:
            self.operations[key] += int(event["operations"][key])
        for bucket in self.traffic_keys:
            self.traffic[bucket]["reads"] += int(event["traffic"][bucket]["reads"])
            self.traffic[bucket]["writes"] += int(event["traffic"][bucket]["writes"])
        self.events.append(event)
        self.ir_kind_counts[event["kind"]] += 1
        return event

    def _release_buffers(self, buffers: Iterable[Buffer], metadata: Mapping[str, Any]) -> None:
        unique: list[Buffer] = []
        seen: set[str] = set()
        for buffer in buffers:
            if buffer.allocation_id in seen:
                continue
            seen.add(buffer.allocation_id)
            allocation = self.allocations.get(buffer.allocation_id)
            if allocation is not None and allocation.live:
                unique.append(buffer)
        if not unique:
            return
        event = self._begin_event("free", metadata)
        freed: list[dict[str, Any]] = []
        for buffer in unique:
            allocation = self.allocations[buffer.allocation_id]
            if allocation.digest_sha256 is None:
                raise AssertionError(
                    f"allocation {allocation.allocation_id} was freed before its digest was recorded"
                )
            allocation.live = False
            self.current_live_words -= allocation.words
            freed.append(
                {
                    "allocation_id": allocation.allocation_id,
                    "shape": list(allocation.shape),
                    "words": allocation.words,
                    "role": allocation.role,
                    "digest_sha256": allocation.digest_sha256,
                }
            )
        self._finish_event(
            event,
            inputs=unique,
            result={"freed": freed},
            semantic_payload={},
        )

    def _assert_buffer_kernel_contract(self, buffer: Buffer, p: int) -> None:
        if not buffer.canonical:
            raise AssertionError(f"unsealed buffer {buffer.allocation_id} reached a dense kernel")
        if buffer.data.dtype != np.dtype(np.int64):
            raise AssertionError("dense kernel input is not int64")
        if buffer.data.ndim > 3:
            raise AssertionError("dense kernel input exceeds three dimensions")
        if buffer.maximum_value_bound >= p:
            raise AssertionError("dense kernel input lacks a canonical range certificate")

    def _matmul_into(
        self,
        event: dict[str, Any],
        left: Buffer,
        right: Buffer,
        output: Buffer,
        *,
        p: int,
        traffic_read_bucket: str,
        traffic_write_bucket: str,
    ) -> None:
        self._assert_buffer_kernel_contract(left, p)
        self._assert_buffer_kernel_contract(right, p)
        if left.data.ndim != 2 or right.data.ndim != 2 or output.data.ndim != 2:
            raise AssertionError("matmul wrapper requires matrices")
        if left.data.shape[1] != right.data.shape[0]:
            raise AssertionError("matmul inner dimensions do not join")
        if output.data.shape != (left.data.shape[0], right.data.shape[1]):
            raise AssertionError("matmul output shape mismatch")
        inner = int(left.data.shape[1])
        products = int(left.data.shape[0]) * inner * int(right.data.shape[1])
        output_words = output.words
        additions = output_words * max(inner - 1, 0)
        bound = inner * left.maximum_value_bound * right.maximum_value_bound
        self.maximum_int64_dot_length = max(self.maximum_int64_dot_length, inner)
        self.maximum_int64_accumulator_bound = max(self.maximum_int64_accumulator_bound, bound)
        if inner > int(self.resource_gates["maximum_int64_dot_length"]):
            self._refuse("maximum_int64_dot_length", {"inner": inner, "event": event["metadata"]})
        frozen_bound = int(self.resource_gates["maximum_int64_accumulator_bound"])
        signed_limit = int(self.resource_gates["signed_int64_maximum"])
        if bound > frozen_bound or bound >= signed_limit:
            self._refuse(
                "maximum_int64_accumulator_bound",
                {"bound": bound, "frozen_bound": frozen_bound, "event": event["metadata"]},
            )
        self._charge_operations(
            event,
            muls=products,
            adds=additions,
            reductions=output_words,
            comparisons=4,
        )
        self._charge_traffic(event, traffic_read_bucket, reads=2 * products)
        self._charge_traffic(event, traffic_write_bucket, writes=output_words)
        np.matmul(left.data, right.data, out=output.data)
        np.remainder(output.data, p, out=output.data)
        output.canonical = True
        output.maximum_value_bound = p - 1

    def _new_tt(self, p: int, B: int, cores: Sequence[Buffer], label: str) -> TT:
        if len(cores) != 5:
            raise AssertionError("a nonzero source TT must have five cores")
        prior_right = 1
        words = 0
        for mode, core in enumerate(cores):
            if core.shape[1] != B or core.shape[0] != prior_right:
                raise AssertionError(f"TT core {mode} does not join")
            if not core.canonical:
                raise AssertionError("unsealed core cannot enter a TT")
            prior_right = int(core.shape[2])
            words += core.words
        if cores[0].shape[0] != 1 or cores[-1].shape[2] != 1:
            raise AssertionError("TT boundary ranks must equal one")
        if prior_right != 1:
            raise AssertionError("TT right boundary rank must equal one")
        self.maximum_tt_object_words = max(self.maximum_tt_object_words, words)
        if words > int(self.resource_gates["maximum_tt_object_words"]):
            self._refuse("maximum_tt_object_words", {"label": label, "words": words})
        return TT(self._next_tt_id(), p, B, tuple(cores), label=label)

    def zero_tt(self, p: int, B: int, label: str) -> TT:
        return TT(self._next_tt_id(), p, B, (), tag="canonical_zero", label=label)

    def _seal_tt(self, event: dict[str, Any], tt: TT) -> None:
        descriptor = {
            "p": tt.p,
            "B": tt.B,
            "tag": tt.tag,
            "cores": [
                {
                    "shape": list(core.shape),
                    "value_digest_sha256": core.value_digest_sha256,
                }
                for core in tt.cores
            ],
        }
        payload = canonical_json_bytes(descriptor)
        self._charge_operations(event, hash_bytes=len(payload))
        tt.value_digest_sha256 = sha256_bytes(payload)

    def _tt_descriptor(self, tt: TT) -> dict[str, Any]:
        return {
            "tt_id": tt.tt_id,
            "label": tt.label,
            "tag": tt.tag,
            "p": tt.p,
            "B": tt.B,
            "ranks": list(tt.ranks),
            "words": tt.words,
            "value_digest_sha256": tt.value_digest_sha256,
        }

    def _emit_tt(self, tt: TT, metadata: Mapping[str, Any], certificate: Mapping[str, Any] | None = None) -> TT:
        event = self._begin_event("emit", metadata)
        self._seal_tt(event, tt)
        self._charge_operations(event, copied_words=tt.words)
        self._charge_traffic(event, "core_emit", reads=tt.words)
        self._finish_event(
            event,
            inputs=tt.cores,
            result={"tensor": self._tt_descriptor(tt), "certificate": dict(certificate or {})},
            semantic_payload={
                "core_object_ids": [core.allocation_id for core in tt.cores],
                "core_view_shapes": [list(core.shape) for core in tt.cores],
                "object_digest_sha256": tt.value_digest_sha256,
                "variant": "tensor_emit",
            },
        )
        return tt

    def _begin_operation(
        self,
        operation_kind: str,
        metadata: Mapping[str, Any],
        operands: Sequence[TT],
    ) -> dict[str, Any]:
        self._operation_counter += 1
        return {
            "operation_id": f"op{self._operation_counter:07d}",
            "operation_kind": operation_kind,
            "metadata": dict(metadata),
            "operands": [self._tt_descriptor(value) for value in operands],
            "event_start_sequence": self._event_counter + 1,
            "operations_before": dict(self.operations),
            "traffic_before_words": self.logical_traffic_words,
            "live_before_words": self.current_live_words,
            "_start_ns": time.perf_counter_ns(),
        }

    def _finish_operation(
        self,
        token: dict[str, Any],
        output: TT,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        record = {key: value for key, value in token.items() if not key.startswith("_")}
        record["event_end_sequence"] = self._event_counter
        record["output"] = self._tt_descriptor(output)
        record["operation_delta"] = subtract_vectors(self.operations, token["operations_before"])
        record["traffic_delta_words"] = self.logical_traffic_words - int(token["traffic_before_words"])
        record["live_after_words"] = self.current_live_words
        record["peak_live_words"] = self.peak_live_words
        record["details"] = dict(details or {})
        record["elapsed_ns"] = time.perf_counter_ns() - int(token["_start_ns"])
        self.operation_records.append(record)

    def coordinate_leaf(
        self,
        values: Sequence[int],
        *,
        mode: int,
        p: int,
        label: str,
        metadata: Mapping[str, Any],
    ) -> TT:
        B = len(values)
        if mode < 0 or mode >= 5 or B <= 0:
            raise ValueError("coordinate leaf requires one of five modes and a nonempty vector")
        token = self._begin_operation("input_coordinate", metadata, ())
        event_metadata = dict(metadata)
        event_metadata.update({"physical_mode": mode, "destination": label})
        event = self._begin_event("input_coordinate", event_metadata)
        cores: list[Buffer] = []
        for core_mode in range(5):
            core = self._allocate(event, (1, B, 1), f"{label}:core:{core_mode}")
            for physical_index in range(B):
                raw = values[physical_index] if core_mode == mode else 1
                core.data[0, physical_index, 0] = int(raw) % p
            self._charge_operations(event, copied_words=B)
            self._charge_traffic(event, "core_emit", writes=B)
            self._seal_buffer(event, core, p)
            cores.append(core)
        self._charge_operations(event, copied_words=B)
        self._charge_traffic(event, "registry_input", reads=B)
        tt = self._new_tt(p, B, cores, label)
        self._finish_event(
            event,
            outputs=cores,
            result={"physical_mode": mode},
            semantic_payload={
                "mode": mode,
                "output_object_ids": [core.allocation_id for core in cores],
                "variant": "coordinate_leaf",
            },
        )
        self._emit_tt(tt, metadata, {"rank_one_coordinate_leaf": True, "physical_mode": mode})
        self._finish_operation(token, tt, {"physical_mode": mode})
        return tt

    def rank_one_from_vectors(
        self,
        vectors: Sequence[Sequence[int]],
        *,
        p: int,
        label: str,
        metadata: Mapping[str, Any],
    ) -> TT:
        """Development-control constructor with one input-coordinate node per mode."""

        if len(vectors) != 5:
            raise ValueError("rank-one TT requires five vectors")
        B = len(vectors[0])
        token = self._begin_operation("rank_one_input", metadata, ())
        cores: list[Buffer] = []
        for mode, vector in enumerate(vectors):
            if len(vector) != B:
                raise ValueError("rank-one vectors must share a mode size")
            event_metadata = dict(metadata)
            event_metadata["physical_mode"] = mode
            event = self._begin_event("input_coordinate", event_metadata)
            core = self._allocate(event, (1, B, 1), f"{label}:core:{mode}")
            for physical_index in range(B):
                core.data[0, physical_index, 0] = int(vector[physical_index]) % p
            self._charge_operations(event, copied_words=2 * B)
            self._charge_traffic(event, "registry_input", reads=B)
            self._charge_traffic(event, "core_emit", writes=B)
            self._seal_buffer(event, core, p)
            self._finish_event(
                event,
                outputs=(core,),
                semantic_payload={
                    "mode": mode,
                    "output_object_ids": [core.allocation_id],
                    "variant": "rank_one_vector",
                },
            )
            cores.append(core)
        tt = self._new_tt(p, B, cores, label)
        self._emit_tt(tt, metadata, {"rank_one_outer_product": True})
        self._finish_operation(token, tt)
        return tt

    def scale(
        self,
        tensor: TT,
        scalar: int,
        *,
        label: str,
        metadata: Mapping[str, Any],
    ) -> TT:
        self._require_live(tensor)
        token = self._begin_operation("scale", metadata, (tensor,))
        scalar %= tensor.p
        event = self._begin_event("scale", {**dict(metadata), "scalar": scalar})
        if tensor.is_zero or scalar == 0:
            result = self.zero_tt(tensor.p, tensor.B, label)
            self._finish_event(
                event,
                result={"canonical_zero": True, "scalar": scalar},
                semantic_payload={"operations": [], "variant": "tensor_scale"},
            )
            self._emit_tt(result, metadata, {"scalar": scalar, "rank_preserved": tensor.is_zero})
            self._finish_operation(token, result, {"scalar": scalar})
            return result
        outputs: list[Buffer] = []
        semantic_operations: list[dict[str, Any]] = []
        for mode, source in enumerate(tensor.cores):
            output = self._allocate(event, source.shape, f"{label}:core:{mode}")
            if mode == 0 and scalar != 1:
                self._assert_buffer_kernel_contract(source, tensor.p)
                self._charge_operations(event, muls=source.words, reductions=source.words)
                self._charge_traffic(event, "direct_sum_copy", reads=source.words, writes=source.words)
                np.multiply(source.data, scalar, out=output.data)
                np.remainder(output.data, tensor.p, out=output.data)
            else:
                self._charge_operations(event, copied_words=2 * source.words)
                self._charge_traffic(event, "direct_sum_copy", reads=source.words, writes=source.words)
                output.data[...] = source.data
            self._seal_buffer(event, output, tensor.p)
            outputs.append(output)
            semantic_operations.append(
                {
                    "input_object_id": source.allocation_id,
                    "input_view_shape": list(source.shape),
                    "method": "multiply" if mode == 0 and scalar != 1 else "copy",
                    "output_object_id": output.allocation_id,
                    "scalar": scalar if mode == 0 and scalar != 1 else 1,
                }
            )
        result = self._new_tt(tensor.p, tensor.B, outputs, label)
        self._finish_event(
            event,
            inputs=tensor.cores,
            outputs=outputs,
            semantic_payload={"operations": semantic_operations, "variant": "tensor_scale"},
        )
        certificate = {
            "scalar": scalar,
            "input_ranks": list(tensor.ranks),
            "output_ranks": list(result.ranks),
            "rank_preserved": tensor.ranks == result.ranks,
        }
        self._emit_tt(result, metadata, certificate)
        self._finish_operation(token, result, certificate)
        return result

    def add(
        self,
        left: TT,
        right: TT,
        *,
        label: str,
        metadata: Mapping[str, Any],
    ) -> TT:
        return self.direct_sum((left, right), (1, 1), label=label, metadata=metadata, operation_kind="add")

    def subtract(
        self,
        left: TT,
        right: TT,
        *,
        label: str,
        metadata: Mapping[str, Any],
    ) -> TT:
        return self.direct_sum((left, right), (1, -1), label=label, metadata=metadata, operation_kind="subtract")

    def direct_sum(
        self,
        tensors: Sequence[TT],
        coefficients: Sequence[int],
        *,
        label: str,
        metadata: Mapping[str, Any],
        operation_kind: str = "linear_combination",
    ) -> TT:
        if len(tensors) != len(coefficients) or not tensors:
            raise ValueError("direct sum requires matching nonempty tensors and coefficients")
        for tensor in tensors:
            self._require_live(tensor)
        p = tensors[0].p
        B = tensors[0].B
        if any(tensor.p != p or tensor.B != B for tensor in tensors):
            raise ValueError("direct-sum operands do not share a field and mode size")
        token = self._begin_operation(operation_kind, metadata, tensors)
        active = [
            (tensor, int(coefficient) % p)
            for tensor, coefficient in zip(tensors, coefficients)
            if not tensor.is_zero and int(coefficient) % p != 0
        ]
        event = self._begin_event(
            "direct_sum",
            {**dict(metadata), "term_count": len(tensors), "active_term_count": len(active)},
        )
        if not active:
            raw = self.zero_tt(p, B, f"{label}:raw")
            self._finish_event(
                event,
                result={"raw_ranks": [0, 0, 0, 0]},
                semantic_payload={"cores": [], "variant": "direct_sum"},
            )
            result = self._normalize_owned(raw, label, metadata)
            self._emit_tt(result, metadata)
            self._finish_operation(token, result, {"raw_ranks": [0, 0, 0, 0]})
            return result

        raw_ranks = [sum(tensor.ranks[cut] for tensor, _ in active) for cut in range(4)]
        raw_words = B * (
            raw_ranks[0]
            + raw_ranks[0] * raw_ranks[1]
            + raw_ranks[1] * raw_ranks[2]
            + raw_ranks[2] * raw_ranks[3]
            + raw_ranks[3]
        )
        self.maximum_tt_object_words = max(self.maximum_tt_object_words, raw_words)
        if raw_words > int(self.resource_gates["maximum_tt_object_words"]):
            self._refuse(
                "maximum_tt_object_words",
                {"label": label, "raw_ranks": raw_ranks, "words": raw_words, "event": metadata},
            )
        outputs: list[Buffer] = []
        semantic_cores: list[dict[str, Any]] = []
        left_offsets = [0, 0, 0, 0, 0]
        right_offsets = [0, 0, 0, 0, 0]
        shapes = [
            (1, B, raw_ranks[0]),
            (raw_ranks[0], B, raw_ranks[1]),
            (raw_ranks[1], B, raw_ranks[2]),
            (raw_ranks[2], B, raw_ranks[3]),
            (raw_ranks[3], B, 1),
        ]
        for mode, shape in enumerate(shapes):
            output = self._allocate(event, shape, f"{label}:raw_core:{mode}", zero=True)
            for tensor, coefficient in active:
                source = tensor.cores[mode]
                left_size, _, right_size = source.shape
                left_start = 0 if mode == 0 else left_offsets[mode]
                right_start = 0 if mode == 4 else right_offsets[mode]
                destination = output.data[
                    left_start : left_start + left_size,
                    :,
                    right_start : right_start + right_size,
                ]
                if mode == 0 and coefficient != 1:
                    self._assert_buffer_kernel_contract(source, p)
                    if coefficient == p - 1:
                        self._charge_operations(event, subs=source.words, reductions=source.words)
                        np.subtract(0, source.data, out=destination)
                    else:
                        self._charge_operations(event, muls=source.words, reductions=source.words)
                        np.multiply(source.data, coefficient, out=destination)
                    np.remainder(destination, p, out=destination)
                    self._charge_traffic(
                        event, "direct_sum_copy", reads=source.words, writes=source.words
                    )
                else:
                    destination[...] = source.data
                    self._charge_operations(event, copied_words=2 * source.words)
                    self._charge_traffic(
                        event, "direct_sum_copy", reads=source.words, writes=source.words
                    )
                if mode > 0:
                    left_offsets[mode] += left_size
                if mode < 4:
                    right_offsets[mode] += right_size
            self._seal_buffer(event, output, p)
            outputs.append(output)
            semantic_cores.append(
                {
                    "coefficients": [
                        coefficient if mode == 0 else 1
                        for _, coefficient in active
                    ],
                    "input_object_ids": [
                        tensor.cores[mode].allocation_id for tensor, _ in active
                    ],
                    "input_view_shapes": [
                        list(tensor.cores[mode].shape) for tensor, _ in active
                    ],
                    "output_object_id": output.allocation_id,
                    "position": "first" if mode == 0 else "last" if mode == 4 else "middle",
                }
            )
        raw = self._new_tt(p, B, outputs, f"{label}:raw")
        self._finish_event(
            event,
            inputs=tuple(core for tensor, _ in active for core in tensor.cores),
            outputs=outputs,
            result={"raw_ranks": raw_ranks, "raw_words": raw_words},
            semantic_payload={"cores": semantic_cores, "variant": "direct_sum"},
        )
        result = self._normalize_owned(raw, label, metadata)
        self._emit_tt(result, metadata)
        self._finish_operation(token, result, {"raw_ranks": raw_ranks, "raw_words": raw_words})
        return result

    def hadamard(
        self,
        left: TT,
        right: TT,
        *,
        label: str,
        metadata: Mapping[str, Any],
    ) -> TT:
        self._require_live(left)
        self._require_live(right)
        if left.p != right.p or left.B != right.B:
            raise ValueError("Hadamard operands do not share a field and mode size")
        token = self._begin_operation("hadamard", metadata, (left, right))
        p = left.p
        B = left.B
        raw_product_ranks = [a * b for a, b in zip(left.ranks, right.ranks)]
        if left.is_zero or right.is_zero:
            raw = self.zero_tt(p, B, f"{label}:raw")
            result = self._normalize_owned(raw, label, metadata)
            self._emit_tt(result, metadata)
            self._finish_operation(token, result, {"raw_product_ranks": raw_product_ranks})
            return result

        transfer: Buffer | None = None
        provisional: list[Buffer] = []
        streamed_prefix_ranks: list[int] = []
        local_shapes: list[dict[str, Any]] = []
        for mode in range(5):
            core_a = left.cores[mode]
            core_b = right.cores[mode]
            la, physical_a, ra = core_a.shape
            lb, physical_b, rb = core_b.shape
            if physical_a != B or physical_b != B:
                raise AssertionError("Hadamard operand mode size changed")
            if transfer is not None:
                s, transfer_la, transfer_lb = transfer.shape
                if transfer_la != la or transfer_lb != lb:
                    raise AssertionError("streamed transfer does not join operand bonds")
            else:
                s = 1
                if la != 1 or lb != 1:
                    raise AssertionError("first Hadamard cores require unit left boundaries")
            matrix: Buffer | None = None
            stage_b_slices: list[Buffer] = []
            for physical_slice in range(B):
                stage_a_meta = {
                    **dict(metadata),
                    "physical_mode": mode,
                    "physical_slice": physical_slice,
                    "operand_shapes": [list(core_a.shape), list(core_b.shape)],
                }
                stage_a = self._begin_event("stage_a_contract", stage_a_meta)
                if transfer is None:
                    transfer = self._allocate(stage_a, (1, 1, 1), f"{label}:initial_transfer")
                    transfer.data[0, 0, 0] = 1
                    self._charge_operations(stage_a, copied_words=1)
                    self._charge_traffic(stage_a, "transfer_propagation", writes=1)
                    self._seal_buffer(stage_a, transfer, p)
                stage_a_buffer = self._allocate(stage_a, (s, lb, ra), f"{label}:stage_a:{mode}:{physical_slice}")
                for left_bond_b in range(lb):
                    transfer_slice = Buffer(
                        transfer.data[:, :, left_bond_b],
                        transfer.allocation_id,
                        transfer.role,
                        canonical=True,
                        maximum_value_bound=transfer.maximum_value_bound,
                        value_digest_sha256=transfer.value_digest_sha256,
                    )
                    operand_slice = Buffer(
                        core_a.data[:, physical_slice, :],
                        core_a.allocation_id,
                        core_a.role,
                        canonical=True,
                        maximum_value_bound=core_a.maximum_value_bound,
                        value_digest_sha256=core_a.value_digest_sha256,
                    )
                    output_slice = Buffer(
                        stage_a_buffer.data[:, left_bond_b, :],
                        stage_a_buffer.allocation_id,
                        stage_a_buffer.role,
                    )
                    self._matmul_into(
                        stage_a,
                        transfer_slice,
                        operand_slice,
                        output_slice,
                        p=p,
                        traffic_read_bucket="stage_a_input",
                        traffic_write_bucket="stage_a_output",
                    )
                stage_a_buffer.canonical = True
                stage_a_buffer.maximum_value_bound = p - 1
                self._seal_buffer(stage_a, stage_a_buffer, p)
                self._finish_event(
                    stage_a,
                    inputs=(transfer, core_a),
                    outputs=(stage_a_buffer,),
                    result={"stage_a_shape": list(stage_a_buffer.shape)},
                    semantic_payload={
                        "operand_a_object_id": core_a.allocation_id,
                        "operand_a_view_shape": list(core_a.shape),
                        "output_object_id": stage_a_buffer.allocation_id,
                        "physical_slice": physical_slice,
                        "transfer_object_id": transfer.allocation_id,
                        "transfer_view_shape": list(transfer.shape),
                        "variant": "stage_a_contract",
                    },
                )

                stage_b_meta = dict(stage_a_meta)
                stage_b = self._begin_event("stage_b_contract", stage_b_meta)
                stage_b_buffer = self._allocate(stage_b, (s, ra, rb), f"{label}:stage_b:{mode}:{physical_slice}")
                for right_bond_a in range(ra):
                    stage_a_slice = Buffer(
                        stage_a_buffer.data[:, :, right_bond_a],
                        stage_a_buffer.allocation_id,
                        stage_a_buffer.role,
                        canonical=True,
                        maximum_value_bound=stage_a_buffer.maximum_value_bound,
                        value_digest_sha256=stage_a_buffer.value_digest_sha256,
                    )
                    operand_slice_b = Buffer(
                        core_b.data[:, physical_slice, :],
                        core_b.allocation_id,
                        core_b.role,
                        canonical=True,
                        maximum_value_bound=core_b.maximum_value_bound,
                        value_digest_sha256=core_b.value_digest_sha256,
                    )
                    output_slice_b = Buffer(
                        stage_b_buffer.data[:, right_bond_a, :],
                        stage_b_buffer.allocation_id,
                        stage_b_buffer.role,
                    )
                    self._matmul_into(
                        stage_b,
                        stage_a_slice,
                        operand_slice_b,
                        output_slice_b,
                        p=p,
                        traffic_read_bucket="stage_b_input",
                        traffic_write_bucket="stage_b_output",
                    )
                stage_b_buffer.canonical = True
                stage_b_buffer.maximum_value_bound = p - 1
                self._seal_buffer(stage_b, stage_b_buffer, p)
                stage_b_slices.append(stage_b_buffer)
                if physical_slice == B - 1:
                    matrix = self._allocate(
                        stage_b,
                        (s * B, ra * rb),
                        f"{label}:local_matrix:{mode}",
                        local_matrix=True,
                    )
                    for slice_index, slice_buffer in enumerate(stage_b_slices):
                        flattened = slice_buffer.data.reshape((s, ra * rb), order="C")
                        destination = matrix.data[slice_index::B, :]
                        destination[...] = flattened
                        self._charge_operations(
                            stage_b,
                            copied_words=2 * slice_buffer.words,
                        )
                        self._charge_traffic(
                            stage_b,
                            "stage_b_output",
                            reads=slice_buffer.words,
                            writes=slice_buffer.words,
                        )
                    matrix.canonical = True
                    matrix.maximum_value_bound = p - 1
                    self._seal_buffer(stage_b, matrix, p)
                stage_b_inputs = [stage_a_buffer, core_b]
                if physical_slice == B - 1:
                    stage_b_inputs.extend(stage_b_slices[:-1])
                self._finish_event(
                    stage_b,
                    inputs=tuple(stage_b_inputs),
                    outputs=(stage_b_buffer,) if physical_slice < B - 1 else (stage_b_buffer, matrix),
                    result={
                        "stage_b_shape": list(stage_b_buffer.shape),
                        "local_matrix_shape": (
                            list(matrix.shape) if matrix is not None else None
                        ),
                    },
                    semantic_payload={
                        "local_matrix_object_id": (
                            matrix.allocation_id if physical_slice == B - 1 else None
                        ),
                        "operand_b_object_id": core_b.allocation_id,
                        "operand_b_view_shape": list(core_b.shape),
                        "output_object_id": stage_b_buffer.allocation_id,
                        "physical_slice": physical_slice,
                        "slice_object_ids": (
                            [item.allocation_id for item in stage_b_slices]
                            if physical_slice == B - 1
                            else []
                        ),
                        "stage_a_object_id": stage_a_buffer.allocation_id,
                        "variant": "stage_b_contract",
                    },
                )
                self._release_buffers(
                    (stage_a_buffer,),
                    {**dict(metadata), "phase": "streamed_slice", "physical_mode": mode, "physical_slice": physical_slice},
                )

            if matrix is None or transfer is None:
                raise AssertionError("streamed Hadamard failed to build a local matrix")
            self._release_buffers(
                stage_b_slices,
                {**dict(metadata), "phase": "streamed_slice_outputs", "physical_mode": mode},
            )
            local_shapes.append(
                {
                    "mode": mode,
                    "incoming_transfer": list(transfer.shape),
                    "local_matrix": list(matrix.shape),
                    "stage_a_max_words": s * lb * ra,
                    "stage_b_max_words": s * ra * rb,
                }
            )
            old_transfer = transfer
            if mode < 4:
                left_factor, right_factor, certificate = self._rank_factor(
                    matrix,
                    p=p,
                    phase="streamed_prefix",
                    metadata={**dict(metadata), "physical_mode": mode},
                )
                rank = int(certificate["rank"])
                if rank == 0:
                    self._release_buffers(
                        (*provisional, matrix, old_transfer, left_factor, right_factor),
                        {**dict(metadata), "phase": "streamed_zero", "physical_mode": mode},
                    )
                    raw = self.zero_tt(p, B, f"{label}:raw")
                    result = self._normalize_owned(raw, label, metadata)
                    self._emit_tt(result, metadata)
                    self._finish_operation(
                        token,
                        result,
                        {"raw_product_ranks": raw_product_ranks, "streamed_zero_mode": mode},
                    )
                    return result
                provisional_core = self._view(left_factor, (s, B, rank), f"{label}:provisional_core:{mode}")
                transfer = self._view(right_factor, (rank, ra, rb), f"{label}:transfer:{mode + 1}")
                provisional.append(provisional_core)
                streamed_prefix_ranks.append(rank)
                self._release_buffers(
                    (matrix, old_transfer),
                    {**dict(metadata), "phase": "streamed_prefix_advance", "physical_mode": mode},
                )
            else:
                if ra != 1 or rb != 1:
                    raise AssertionError("last Hadamard core does not have a unit right boundary")
                provisional.append(self._view(matrix, (s, B, 1), f"{label}:provisional_core:{mode}"))
                self._release_buffers(
                    (old_transfer,),
                    {**dict(metadata), "phase": "streamed_finish", "physical_mode": mode},
                )
        raw = self._new_tt(p, B, provisional, f"{label}:streamed_raw")
        result = self._normalize_owned(raw, label, metadata)
        self._emit_tt(result, metadata)
        details = {
            "raw_product_ranks": raw_product_ranks,
            "streamed_prefix_ranks": streamed_prefix_ranks,
            "local_shapes": local_shapes,
        }
        self._finish_operation(token, result, details)
        return result

    def _rank_factor(
        self,
        matrix_buffer: Buffer,
        *,
        p: int,
        phase: str,
        metadata: Mapping[str, Any],
    ) -> tuple[Buffer, Buffer, dict[str, Any]]:
        matrix = matrix_buffer.data
        if matrix.ndim != 2 or matrix.dtype != np.dtype(np.int64):
            raise AssertionError("rank factorization requires an int64 matrix")
        m, n = (int(matrix.shape[0]), int(matrix.shape[1]))
        words = m * n
        if words > int(self.resource_gates["maximum_local_matrix_words"]):
            self._refuse(
                "maximum_local_matrix_words",
                {"phase": phase, "shape": [m, n], "words": words, "event": metadata},
            )
        event = self._begin_event("rank_factor", {**dict(metadata), "phase": phase, "shape": [m, n]})
        work = self._allocate(event, (m, n), f"rank_work:{phase}", local_matrix=True)
        row_temp = self._allocate(event, (n,), f"rank_row_temp:{phase}", zero=True)
        work.data[...] = matrix
        work.canonical = True
        work.maximum_value_bound = p - 1
        self._charge_operations(event, copied_words=2 * words)
        self._charge_traffic(event, "factor_input_copy", reads=words, writes=words)

        pivot_columns: list[int] = []
        pivot_rows: list[int] = []
        used_rows: set[int] = set()
        for column in range(n):
            chosen: int | None = None
            for row in range(m):
                if row in used_rows:
                    continue
                self._charge_operations(event, comparisons=1)
                self._charge_traffic(event, "pivot_scan", reads=1)
                if int(work.data[row, column]) != 0:
                    chosen = row
                    break
            if chosen is None:
                continue
            pivot = int(work.data[chosen, column])
            inverse = pow(pivot, -1, p)
            self._charge_operations(event, inversions=1, reductions=1, comparisons=1)
            self._assert_buffer_kernel_contract(work, p)
            self._charge_operations(event, muls=n, reductions=n)
            self._charge_traffic(event, "row_normalization", reads=n, writes=n)
            np.multiply(work.data[chosen, :], inverse, out=work.data[chosen, :])
            np.remainder(work.data[chosen, :], p, out=work.data[chosen, :])
            for row in range(m):
                if row == chosen:
                    continue
                factor = int(work.data[row, column])
                self._charge_operations(event, comparisons=1)
                self._charge_traffic(event, "elimination", reads=1)
                if factor == 0:
                    continue
                self._charge_operations(event, muls=n, subs=n, reductions=2 * n)
                self._charge_traffic(event, "elimination", reads=3 * n, writes=2 * n)
                np.multiply(work.data[chosen, :], factor, out=row_temp.data)
                np.remainder(row_temp.data, p, out=row_temp.data)
                np.subtract(work.data[row, :], row_temp.data, out=work.data[row, :])
                np.remainder(work.data[row, :], p, out=work.data[row, :])
            used_rows.add(chosen)
            pivot_columns.append(column)
            pivot_rows.append(chosen)

        rank = len(pivot_columns)
        left_factor = self._allocate(event, (m, rank), f"rank_left:{phase}")
        right_factor = self._allocate(event, (rank, n), f"rank_right:{phase}")
        for factor_column, source_column in enumerate(pivot_columns):
            left_factor.data[:, factor_column] = matrix[:, source_column]
        for factor_row, source_row in enumerate(pivot_rows):
            right_factor.data[factor_row, :] = work.data[source_row, :]
        factor_words = m * rank + rank * n
        self._charge_operations(event, copied_words=2 * factor_words)
        self._charge_traffic(event, "factor_output", reads=factor_words, writes=factor_words)
        self._seal_buffer(event, work, p)
        self._seal_buffer(event, row_temp, p)
        self._seal_buffer(event, left_factor, p)
        self._seal_buffer(event, right_factor, p)
        pivot_width = max(1, (max(n, 1).bit_length() + 7) // 8)
        certificate_digest = hashlib.sha256()
        for pivot_column in pivot_columns:
            certificate_digest.update(pivot_column.to_bytes(pivot_width, "big"))
        certificate_digest.update(bytes.fromhex(left_factor.value_digest_sha256 or ""))
        certificate_digest.update(bytes.fromhex(right_factor.value_digest_sha256 or ""))
        digest_bytes = rank * pivot_width + 64
        self._charge_operations(event, hash_bytes=digest_bytes)
        certificate = {
            "phase": phase,
            "input_shape": [m, n],
            "rank": rank,
            "pivot_columns": pivot_columns,
            "pivot_rows": pivot_rows,
            "left_shape": [m, rank],
            "right_shape": [rank, n],
            "factor_digest_sha256": certificate_digest.hexdigest(),
        }
        self._finish_event(
            event,
            inputs=(matrix_buffer,),
            outputs=(left_factor, right_factor),
            result=certificate,
            semantic_payload={
                "left_factor_object_id": left_factor.allocation_id,
                "matrix_object_id": matrix_buffer.allocation_id,
                "matrix_view_shape": [m, n],
                "pivot_columns": pivot_columns,
                "rank": rank,
                "right_factor_object_id": right_factor.allocation_id,
                "variant": "rank_factor",
            },
        )
        self._release_buffers((work, row_temp), {**dict(metadata), "phase": f"{phase}:workspace"})
        self.counts["rank_factorizations"] += 1
        if phase == "streamed_prefix":
            self.counts["streamed_prefix_factorizations"] += 1
        else:
            self.counts["two_sweep_factorizations"] += 1
        return left_factor, right_factor, certificate

    def _absorb_left(
        self,
        factor: Buffer,
        neighbor: Buffer,
        *,
        p: int,
        metadata: Mapping[str, Any],
    ) -> Buffer:
        u, v = int(factor.shape[0]), int(factor.shape[1])
        if neighbor.shape[0] != v:
            raise AssertionError("left absorption does not join")
        _, B, w = neighbor.shape
        event = self._begin_event("absorb_left", metadata)
        output = self._allocate(event, (u, B, w), "left_sweep_neighbor")
        left_matrix = factor
        right_matrix = self._view(neighbor, (v, B * w), neighbor.role)
        output_matrix = self._view(output, (u, B * w), output.role)
        self._matmul_into(
            event,
            left_matrix,
            right_matrix,
            output_matrix,
            p=p,
            traffic_read_bucket="sweep_absorption",
            traffic_write_bucket="sweep_absorption",
        )
        output.canonical = True
        output.maximum_value_bound = p - 1
        self._seal_buffer(event, output, p)
        self._finish_event(
            event,
            inputs=(factor, neighbor),
            outputs=(output,),
            semantic_payload={
                "left_object_id": factor.allocation_id,
                "left_view_shape": list(left_matrix.shape),
                "output_object_id": output.allocation_id,
                "right_object_id": neighbor.allocation_id,
                "right_view_shape": list(right_matrix.shape),
                "variant": "absorb_left",
            },
        )
        return output

    def _absorb_right(
        self,
        neighbor: Buffer,
        factor: Buffer,
        *,
        p: int,
        metadata: Mapping[str, Any],
    ) -> Buffer:
        old_left, rank = int(factor.shape[0]), int(factor.shape[1])
        u, B, old_right = neighbor.shape
        if old_right != old_left:
            raise AssertionError("right absorption does not join")
        event = self._begin_event("absorb_right", metadata)
        output = self._allocate(event, (u, B, rank), "right_sweep_neighbor")
        left_matrix = self._view(neighbor, (u * B, old_left), neighbor.role)
        output_matrix = self._view(output, (u * B, rank), output.role)
        self._matmul_into(
            event,
            left_matrix,
            factor,
            output_matrix,
            p=p,
            traffic_read_bucket="sweep_absorption",
            traffic_write_bucket="sweep_absorption",
        )
        output.canonical = True
        output.maximum_value_bound = p - 1
        self._seal_buffer(event, output, p)
        self._finish_event(
            event,
            inputs=(neighbor, factor),
            outputs=(output,),
            semantic_payload={
                "left_object_id": neighbor.allocation_id,
                "left_view_shape": list(left_matrix.shape),
                "output_object_id": output.allocation_id,
                "right_object_id": factor.allocation_id,
                "right_view_shape": list(factor.shape),
                "variant": "absorb_right",
            },
        )
        return output

    def _normalize_owned(self, tensor: TT, label: str, metadata: Mapping[str, Any]) -> TT:
        self._require_live(tensor)
        self.counts["normalization_calls"] += 1
        if tensor.is_zero:
            tensor.released = True
            return self.zero_tt(tensor.p, tensor.B, label)
        p = tensor.p
        B = tensor.B
        cores = list(tensor.cores)
        tensor.released = True
        for mode in range(4):
            left, _, right = cores[mode].shape
            matrix = self._view(
                cores[mode],
                (left * B, right),
                f"{label}:left_matrix:{mode}",
            )
            left_factor, right_factor, certificate = self._rank_factor(
                matrix,
                p=p,
                phase="left_sweep",
                metadata={**dict(metadata), "physical_mode": mode},
            )
            rank = int(certificate["rank"])
            if rank == 0:
                self._release_buffers(
                    (*cores, left_factor, right_factor),
                    {**dict(metadata), "phase": "left_sweep_zero", "physical_mode": mode},
                )
                return self.zero_tt(p, B, label)
            new_core = self._view(left_factor, (left, B, rank), f"{label}:left_core:{mode}")
            new_neighbor = self._absorb_left(
                right_factor,
                cores[mode + 1],
                p=p,
                metadata={**dict(metadata), "physical_mode": mode},
            )
            self._release_buffers(
                (cores[mode], cores[mode + 1], right_factor),
                {**dict(metadata), "phase": "left_sweep_replace", "physical_mode": mode},
            )
            cores[mode] = new_core
            cores[mode + 1] = new_neighbor

        for mode in range(4, 0, -1):
            left, _, right = cores[mode].shape
            matrix = self._view(
                cores[mode],
                (left, B * right),
                f"{label}:right_matrix:{mode}",
            )
            left_factor, right_factor, certificate = self._rank_factor(
                matrix,
                p=p,
                phase="right_sweep",
                metadata={**dict(metadata), "physical_mode": mode},
            )
            rank = int(certificate["rank"])
            if rank == 0:
                self._release_buffers(
                    (*cores, left_factor, right_factor),
                    {**dict(metadata), "phase": "right_sweep_zero", "physical_mode": mode},
                )
                return self.zero_tt(p, B, label)
            new_core = self._view(right_factor, (rank, B, right), f"{label}:right_core:{mode}")
            new_neighbor = self._absorb_right(
                cores[mode - 1],
                left_factor,
                p=p,
                metadata={**dict(metadata), "physical_mode": mode},
            )
            self._release_buffers(
                (cores[mode - 1], cores[mode], left_factor),
                {**dict(metadata), "phase": "right_sweep_replace", "physical_mode": mode},
            )
            cores[mode - 1] = new_neighbor
            cores[mode] = new_core
        return self._new_tt(p, B, cores, label)

    def evaluate_sample(
        self,
        tensor: TT,
        sample: Sequence[int],
        *,
        metadata: Mapping[str, Any],
    ) -> int:
        self._require_live(tensor)
        if len(sample) != 5:
            raise ValueError("diagnostic TT sample requires five registered mode indices")
        if tensor.is_zero:
            return 0
        event = self._begin_event("emit", {**dict(metadata), "diagnostic": "tt_sample"})
        accumulator = [1]
        maximum_temporary_words = 1
        for mode, physical_index in enumerate(sample):
            if physical_index < 0 or physical_index >= tensor.B:
                raise ValueError("diagnostic sample index is out of range")
            self.counts["maximum_live_mode_indices"] = max(
                self.counts["maximum_live_mode_indices"], 1
            )
            core = tensor.cores[mode]
            left, _, right = core.shape
            if len(accumulator) != left:
                raise AssertionError("diagnostic TT accumulator does not join")
            next_accumulator: list[int] = []
            for right_bond in range(right):
                value = 0
                for left_bond in range(left):
                    term = accumulator[left_bond] * int(
                        core.data[left_bond, int(physical_index), right_bond]
                    ) % tensor.p
                    self._charge_operations(event, muls=1, reductions=1)
                    if left_bond == 0:
                        value = term
                    else:
                        value = (value + term) % tensor.p
                        self._charge_operations(event, adds=1, reductions=1)
                next_accumulator.append(value)
            maximum_temporary_words = max(maximum_temporary_words, len(accumulator) + len(next_accumulator))
            accumulator = next_accumulator
        if len(accumulator) != 1:
            raise AssertionError("diagnostic TT evaluation did not reach a scalar")
        self._finish_event(
            event,
            inputs=tensor.cores,
            result={
                "sample_sha256": stable_digest([int(value) for value in sample]),
                "value": accumulator[0],
                "maximum_temporary_field_words": maximum_temporary_words,
            },
            semantic_payload={
                "core_object_ids": [core.allocation_id for core in tensor.cores],
                "core_view_shapes": [list(core.shape) for core in tensor.cores],
                "sample": [int(value) for value in sample],
                "value": accumulator[0],
                "variant": "tt_sample",
            },
        )
        return accumulator[0]

    def begin_diagnostic_rcb(
        self,
        metadata: Mapping[str, Any],
        *,
        left: Sequence[int],
        right: Sequence[int],
        p: int,
        a: int,
        b: int,
    ) -> dict[str, Any]:
        event = self._begin_event("emit", {**dict(metadata), "diagnostic": "scalar_rcb"})
        self._charge_operations(event, adds=17, subs=6, muls=18, reductions=41)
        event["_semantic_payload"] = {
            "a": int(a),
            "b": int(b),
            "left": [int(value) for value in left],
            "p": int(p),
            "right": [int(value) for value in right],
            "variant": "scalar_rcb",
        }
        self.counts["diagnostic_rcb_calls"] += 1
        return event

    def finish_diagnostic_rcb(self, event: dict[str, Any], output: Sequence[int]) -> None:
        semantic_payload = dict(event.pop("_semantic_payload"))
        semantic_payload["output"] = [int(value) for value in output]
        self._finish_event(
            event,
            result={"projective_output": [int(value) for value in output]},
            semantic_payload=semantic_payload,
        )

    def record_scalar_formation(
        self,
        *,
        scalar_name: str,
        input_value: int,
        multiplier: int,
        output_value: int,
        metadata: Mapping[str, Any],
    ) -> None:
        event = self._begin_event("scale", {**dict(metadata), "scalar_formation": scalar_name})
        self._charge_operations(event, muls=1, reductions=1)
        self._finish_event(
            event,
            result={
                "input": int(input_value),
                "multiplier": int(multiplier),
                "output": int(output_value),
            },
            semantic_payload={
                "input": int(input_value),
                "multiplier": int(multiplier),
                "output": int(output_value),
                "variant": "scalar_formation",
            },
        )

    def tensor_record(
        self,
        tensor: TT,
        *,
        retained_advice: bool,
        cell_id: str,
    ) -> dict[str, Any]:
        self._require_live(tensor)
        event = self._begin_event(
            "emit",
            {
                "cell_id": cell_id,
                "phase": "serialization",
                "tensor": tensor.label,
                "retained_advice": retained_advice,
            },
        )
        cores: list[dict[str, Any]] = []
        for core in tensor.cores:
            values = [int(value) for value in core.data.flat]
            self._charge_operations(event, copied_words=core.words)
            bucket = "advice_serialize" if retained_advice else "artifact_serialize"
            self._charge_traffic(event, bucket, reads=core.words)
            cores.append(
                {
                    "shape": list(core.shape),
                    "values": values,
                    "value_digest_sha256": core.value_digest_sha256,
                }
            )
        record = {
            "encoding": "exact-fp-tt-v1",
            "field_modulus": tensor.p,
            "physical_mode_count": 5,
            "physical_mode_size": tensor.B,
            "tag": tensor.tag,
            "ranks": list(tensor.ranks),
            "field_words": tensor.words,
            "canonical_bytes_per_field_word": field_width(tensor.p),
            "value_digest_sha256": tensor.value_digest_sha256,
            "cores": cores,
        }
        payload = canonical_json_bytes(record)
        self._charge_operations(event, hash_bytes=len(payload))
        record["record_sha256"] = sha256_bytes(payload)
        self._finish_event(
            event,
            inputs=tensor.cores,
            result={"record_sha256": record["record_sha256"]},
            semantic_payload={
                "core_object_ids": [core.allocation_id for core in tensor.cores],
                "core_view_shapes": [list(core.shape) for core in tensor.cores],
                "record_sha256": record["record_sha256"],
                "variant": "serialization",
            },
        )
        return record

    def release(self, tensor: TT, *, metadata: Mapping[str, Any] | None = None) -> None:
        if tensor.released:
            return
        tensor.released = True
        self._release_buffers(tensor.cores, metadata or {"tensor": tensor.label})

    def _require_live(self, tensor: TT) -> None:
        if tensor.released:
            raise RuntimeError(f"TT {tensor.tt_id} has already been consumed or released")

    def rss_record(self) -> dict[str, Any]:
        raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if platform.system() == "Darwin":
            normalized = int(raw)
            rule = "Darwin ru_maxrss is bytes"
        else:
            normalized = int(raw) * 1024
            rule = "non-Darwin ru_maxrss is KiB multiplied by 1024"
        return {
            "raw_ru_maxrss": int(raw),
            "normalization": rule,
            "bytes": normalized,
            "within_gate": normalized <= int(self.resource_gates["peak_rss_bytes"]),
        }

    def snapshot(self) -> dict[str, Any]:
        live_allocations = [
            {
                "allocation_id": value.allocation_id,
                "shape": list(value.shape),
                "words": value.words,
                "role": value.role,
                "producer_event_id": value.producer_event_id,
            }
            for value in self.allocations.values()
            if value.live
        ]
        return {
            "schema": "tt-source-runtime-ledger-v1",
            "operation_vector_order": list(OPERATION_KEYS),
            "operations": dict(self.operations),
            "operation_caps": dict(self.operation_caps),
            "traffic_bucket_order": list(self.traffic_keys),
            "traffic": self.traffic,
            "logical_traffic_words": self.logical_traffic_words,
            "counts": dict(self.counts),
            "ir_kind_counts": dict(self.ir_kind_counts),
            "events": self.events,
            "operation_records": self.operation_records,
            "resources": {
                "current_live_field_words": self.current_live_words,
                "peak_live_field_words": self.peak_live_words,
                "maximum_local_matrix_words": self.maximum_local_matrix_words,
                "maximum_tt_object_words": self.maximum_tt_object_words,
                "maximum_ndarray_dimensions": self.maximum_ndarray_dimensions,
                "maximum_int64_dot_length": self.maximum_int64_dot_length,
                "maximum_int64_accumulator_bound": self.maximum_int64_accumulator_bound,
                "rss": self.rss_record(),
                "elapsed_ns": time.perf_counter_ns() - self._start_ns,
            },
            "live_allocations": live_allocations,
            "first_refusal": self.first_refusal,
        }
