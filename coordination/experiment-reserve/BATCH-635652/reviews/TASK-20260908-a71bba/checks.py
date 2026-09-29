#!/usr/bin/env python3
"""Independent fixed source checks for TASK-20260908-a71bba.

This checker imports the delivered table and BSGS helpers, but never imports or
invokes the producer's tests and never invokes a rho solve.  Its only algebraic
objects are fixed synthetic cyclic groups.  The parent reserves the complete
case list before launching one worker and retains the worker process/logs.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import platform
import resource
import signal
import struct
import subprocess
import sys
import tempfile
import textwrap
import time
import traceback
from typing import Any, Callable


TASK_ID = "TASK-20260908-a71bba"
EXPERIMENT_ID = "EXP-ECDLP-709063"
AUTHORITY_COMMIT = "cfe0216c584d856f1602c09aefb55b69a1f4298e"
CLAIM_COMMIT = "7038c3f38f0a156558b8a343ef33f9f3b96aa2f4"
SOURCE_SNAPSHOT = "d8f64d928c8f6a28eed97eac70b741ad3232fbd5"
MEMORY_LIMIT_BYTES = 2 * 1024**3
AGGREGATE_LIMIT_SECONDS = 1800
PER_CASE_LIMIT_SECONDS = 10
MAXIMUM_CASES = 128

HERE = Path(__file__).resolve().parent


def _repo_root() -> Path:
    for candidate in (HERE, *HERE.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / "tools/research_dispatch.py").is_file():
            return candidate
    raise RuntimeError("repository root not found")


REPO = _repo_root()
SOURCE_DIR = REPO / "experiments/EXP-ECDLP-709063/implementation/TASK-20260908-7771f2"
ORIGINAL_DIR = REPO / "experiments/EXP-ECDLP-709063/implementation/TASK-20260908-3b05bc"
HANDOFF_PATH = REPO / "ledger/handoffs/TASK-20260908-a71bba.yaml"
PLAN_PATH = REPO / "coordination/experiment-reserve/BATCH-635652/review-plan-TASK-20260908-a71bba.yaml"
CONTRACT_PATH = REPO / "coordination/experiment-reserve/BATCH-635652/corrections/TASK-20260908-92d6dd/EXP-ECDLP-709063.yaml"
BASE_RHO = REPO / "harness/rho.py"
DERIVATIVE_RHO = SOURCE_DIR / "rho-corrected.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _ru_maxrss_bytes(value: int) -> int:
    return int(value) if sys.platform == "darwin" else int(value) * 1024


def expect_raises(
    expected: type[BaseException] | tuple[type[BaseException], ...],
    function: Callable[[], object],
) -> BaseException:
    label = expected.__name__ if isinstance(expected, type) else "|".join(item.__name__ for item in expected)
    try:
        value = function()
    except expected as exc:
        return exc
    except BaseException as exc:  # noqa: BLE001 - the exact unexpected type is evidence
        raise AssertionError(f"expected {label}, got {type(exc).__name__}: {exc}") from exc
    raise AssertionError(f"expected {label}, accepted {value!r}")


def load_yaml(path: Path) -> Any:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_target_modules() -> tuple[Any, Any]:
    table_path = SOURCE_DIR / "table.py"
    table_spec = importlib.util.spec_from_file_location("table", table_path)
    if table_spec is None or table_spec.loader is None:
        raise RuntimeError("could not construct table module spec")
    table_module = importlib.util.module_from_spec(table_spec)
    sys.modules["table"] = table_module
    table_spec.loader.exec_module(table_module)

    bsgs_path = SOURCE_DIR / "bsgs.py"
    bsgs_spec = importlib.util.spec_from_file_location("validation_target_bsgs_a71bba", bsgs_path)
    if bsgs_spec is None or bsgs_spec.loader is None:
        raise RuntimeError("could not construct BSGS module spec")
    bsgs_module = importlib.util.module_from_spec(bsgs_spec)
    sys.modules[bsgs_spec.name] = bsgs_module
    bsgs_spec.loader.exec_module(bsgs_module)
    return table_module, bsgs_module


@dataclass(frozen=True)
class Case:
    name: str
    function: Callable[[], None]


class FixedCyclicGroup:
    """Complete fixed Z/nZ test double with public call logs and trap secrets."""

    def __init__(self, order: int) -> None:
        self.order = order
        self.add_calls: list[tuple[int, int, int]] = []
        self.neg_calls: list[tuple[int, int]] = []
        self.encode_calls: list[int] = []
        self.equals_calls: list[tuple[int, int, bool]] = []

    @property
    def secret(self) -> int:
        raise AssertionError("solver accessed forbidden secret")

    @property
    def known_scalar(self) -> int:
        raise AssertionError("solver accessed forbidden known scalar")

    def identity(self) -> int:
        return 0

    def add(self, left: int, right: int) -> int:
        value = (left + right) % self.order
        self.add_calls.append((left, right, value))
        return value

    def neg(self, point: int) -> int:
        value = (-point) % self.order
        self.neg_calls.append((point, value))
        return value

    def equals(self, left: int, right: int) -> bool:
        value = left % self.order == right % self.order
        self.equals_calls.append((left, right, value))
        return value

    def encode_point(self, point: int) -> Any:
        self.encode_calls.append(point)
        if point % self.order == 0:
            return TABLE.LogicalPoint.infinity()
        value = point % self.order
        return TABLE.LogicalPoint.affine(value, value * value + 17)


class FalseHitGroup(FixedCyclicGroup):
    def __init__(self, order: int, false_point: int, aliases_to: int) -> None:
        super().__init__(order)
        self.false_point = false_point
        self.aliases_to = aliases_to

    def encode_point(self, point: int) -> Any:
        self.encode_calls.append(point)
        value = point % self.order
        if value == self.false_point:
            value = self.aliases_to
        if value == 0:
            return TABLE.LogicalPoint.infinity()
        return TABLE.LogicalPoint.affine(value, value * value + 17)


class NoHitEncodingGroup(FixedCyclicGroup):
    def __init__(self, order: int, baby_encoding_calls: int) -> None:
        super().__init__(order)
        self.baby_encoding_calls = baby_encoding_calls

    def encode_point(self, point: int) -> Any:
        call_index = len(self.encode_calls)
        self.encode_calls.append(point)
        if call_index < self.baby_encoding_calls:
            if point % self.order == 0:
                return TABLE.LogicalPoint.infinity()
            value = point % self.order
            return TABLE.LogicalPoint.affine(value, value * value + 17)
        value = 1000 + call_index
        return TABLE.LogicalPoint.affine(value, value * 3 + 1)


class HookLog:
    def __init__(self, cancel_event: str | None = None, occurrence: int = 1) -> None:
        self.cancel_event = cancel_event
        self.occurrence = occurrence
        self.events: list[tuple[str, dict[str, int]]] = []
        self.counts: Counter[str] = Counter()

    def __call__(self, name: str, state: dict[str, int]) -> bool:
        self.events.append((name, dict(state)))
        self.counts[name] += 1
        return not (name == self.cancel_event and self.counts[name] == self.occurrence)


class ScalarAdd:
    def __init__(self, modulus: int = 101) -> None:
        self.modulus = modulus
        self.calls: list[tuple[int | None, int | None, int | None]] = []

    def add(self, left: int | None, right: int | None) -> int | None:
        lval = 0 if left is None else left
        rval = 0 if right is None else right
        value = (lval + rval) % self.modulus
        result = None if value == 0 else value
        self.calls.append((left, right, result))
        return result


def independent_scalar_cost(scalar: int) -> int:
    if scalar == 0:
        return 0
    bits = f"{scalar:b}"
    return (len(bits) - 1) + bits[1:].count("1")


def expected_table_point(index: int) -> Any:
    return TABLE.LogicalPoint.affine(index + 1, (19 * index + 23) % (1 << 28))


def independent_hash_slot(point: Any, slots: int) -> int:
    if point.is_infinity:
        encoded = b"\x00"
    else:
        encoded = b"\x04" + point.x.to_bytes(4, "big") + point.y.to_bytes(4, "big")
    digest = hashlib.sha256(b"EXP-ECDLP-709063|table|v2" + encoded).digest()
    return int.from_bytes(digest[:8], "little") % slots


def bsgs_buffer_for_unbounded(order: int) -> bytearray:
    m = int((order - 1) ** 0.5) + 1
    while (m - 1) * (m - 1) >= order:
        m -= 1
    while m * m < order:
        m += 1
    slots = (10 * m + 6) // 7
    return bytearray(16 * slots)


def assert_solver_trace(result: Any, group: FixedCyclicGroup, hook: HookLog, order: int, scalar: int, m: int) -> None:
    giant = scalar // m
    expected = (m - 1) + independent_scalar_cost(m) + giant + independent_scalar_cost(scalar)
    assert result.termination == "SOLVED"
    assert result.solution == scalar
    assert result.m == m
    assert result.occupied == m
    assert result.operations.baby == m - 1
    assert result.operations.scalar_precompute == independent_scalar_cost(m)
    assert result.operations.giant == giant
    assert result.operations.certificate == independent_scalar_cost(scalar)
    assert result.operations.negations == giant
    assert result.operations.total_group_operations == expected
    assert result.operations.group_additions == len(group.add_calls) == expected
    assert result.operations.group_doublings == sum(1 for left, right, _ in group.add_calls if left == right)
    assert result.operations.negations == len(group.neg_calls)
    component_events = sum(hook.counts[name] for name in ("baby", "scalar_precompute", "giant", "certificate"))
    assert component_events == expected
    assert result.table.table_operations == m + giant + 1
    assert result.table.hash_calls == m + giant + 1
    assert result.table.bytes_written == 16 * m
    assert result.operations.total_group_operations == (
        result.operations.baby
        + result.operations.scalar_precompute
        + result.operations.giant
        + result.operations.certificate
    )


def rho_spans() -> tuple[bytes, bytes, int, int, int, int, bytes]:
    base = BASE_RHO.read_bytes()
    derivative = DERIVATIVE_RHO.read_bytes()
    marker = b"    def _count_mul(k_val: int, pt: Point) -> Point:"
    suffix_marker = b"\n\n    # Precompute the r branch steps"
    base_start = base.index(marker)
    base_end = base.index(suffix_marker, base_start)
    derivative_start = derivative.index(marker)
    derivative_end = derivative.index(suffix_marker, derivative_start)
    contract = load_yaml(CONTRACT_PATH)["protocol_amendment"]
    approved_text = contract["rho_baseline"]["prospective_scalar_amendment"]["replacement_python"]
    nested = textwrap.indent(approved_text.rstrip("\n"), "    ").encode("utf-8")
    return base, derivative, base_start, base_end, derivative_start, derivative_end, nested


def derivative_conforms(candidate: bytes) -> bool:
    base, _, base_start, base_end, _, _, nested = rho_spans()
    return candidate == base[:base_start] + nested + base[base_end:]


def rho_scalar_wrapper() -> Callable[[ScalarAdd, int, int], tuple[int | None, int]]:
    _, derivative, _, _, derivative_start, derivative_end, _ = rho_spans()
    span = derivative[derivative_start:derivative_end].decode("utf-8")
    wrapper = (
        "def exercise(E, k, pt):\n"
        "    total_ops = 0\n"
        + span
        + "\n    return _count_mul(k, pt), total_ops\n"
    )
    namespace: dict[str, object] = {"Point": object}
    exec(compile(wrapper, "<independent-rho-scalar-exercise>", "exec"), namespace)
    return namespace["exercise"]  # type: ignore[return-value]


def git_bytes(commit: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=REPO,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode:
        raise AssertionError(completed.stderr.decode("utf-8", errors="replace"))
    return completed.stdout


def git_text(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=REPO, check=False, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode:
        raise AssertionError(completed.stderr)
    return completed.stdout.strip()


def source_binding_rows() -> list[dict[str, str]]:
    return load_yaml(HANDOFF_PATH)["handoff"]["source_bindings"]


def build_cases() -> list[Case]:
    cases: list[Case] = []

    def add(name: str) -> Callable[[Callable[[], None]], Callable[[], None]]:
        def decorate(function: Callable[[], None]) -> Callable[[], None]:
            cases.append(Case(name, function))
            return function
        return decorate

    @add("logical-o-golden")
    def _() -> None:
        point = TABLE.LogicalPoint.infinity()
        raw = TABLE.encode_logical_point(point)
        assert raw == struct.pack("<BII", 0, 0, 0) and len(raw) == 9
        assert TABLE.decode_logical_point(raw) == point

    for index, (x, y) in enumerate(((1, 2), (0, 0), ((1 << 28) - 1, (1 << 28) - 2))):
        @add(f"logical-affine-golden-{index}")
        def _(x: int = x, y: int = y) -> None:
            point = TABLE.LogicalPoint.affine(x, y)
            raw = TABLE.encode_logical_point(point)
            assert raw == struct.pack("<BII", 1, x, y) and len(raw) == 9
            assert TABLE.decode_logical_point(raw) == point

    @add("hash-o-golden")
    def _() -> None:
        assert TABLE.encode_hash_preimage(TABLE.LogicalPoint.infinity()) == b"\x00"
        assert TABLE.decode_hash_preimage(b"\x00") == TABLE.LogicalPoint.infinity()

    for index, (x, y) in enumerate(((1, 2), (0x010203, 0x0A0B0C), ((1 << 28) - 1, 0))):
        @add(f"hash-affine-golden-{index}")
        def _(x: int = x, y: int = y) -> None:
            point = TABLE.LogicalPoint.affine(x, y)
            raw = b"\x04" + x.to_bytes(4, "big") + y.to_bytes(4, "big")
            assert TABLE.encode_hash_preimage(point) == raw
            assert TABLE.decode_hash_preimage(raw) == point

    for name, slot, expected in (
        ("empty", None, struct.pack("<IIII", 0, 0, 0, 0)),
        ("affine", (3, 4, 5, 1), struct.pack("<IIII", 3, 4, 5, 1)),
        ("o-zero", (0, 0, 0, 2), struct.pack("<IIII", 0, 0, 0, 2)),
        ("o-exp", (0, 0, 17, 2), struct.pack("<IIII", 0, 0, 17, 2)),
    ):
        @add(f"physical-{name}-golden")
        def _(slot: Any = slot, expected: bytes = expected) -> None:
            physical = TABLE.PhysicalSlot.empty() if slot is None else TABLE.PhysicalSlot(slot[3], slot[0], slot[1], slot[2])
            raw = TABLE.encode_physical_slot(physical)
            assert raw == expected and len(raw) == 16
            assert TABLE.decode_physical_slot(raw) == physical

    @add("physical-o-empty-distinct")
    def _() -> None:
        empty = TABLE.PhysicalSlot.empty()
        infinity = TABLE.PhysicalSlot.from_logical(TABLE.LogicalPoint.infinity(), 0)
        assert TABLE.encode_physical_slot(empty) != TABLE.encode_physical_slot(infinity)
        expect_raises(TABLE.TableValidationError, empty.logical_point)
        assert infinity.logical_point() == TABLE.LogicalPoint.infinity()

    for length in (0, 1, 8, 16):
        @add(f"logical-malformed-length-{length}")
        def _(length: int = length) -> None:
            expect_raises(TABLE.TableValidationError, lambda: TABLE.decode_logical_point(b"\x00" * length))

    for raw in (b"", b"\x00\x00", b"\x03" + b"\x00" * 8, b"\x04" + b"\x00" * 7):
        digest = sha256_bytes(raw)[:8]
        @add(f"hash-malformed-{digest}")
        def _(raw: bytes = raw) -> None:
            expect_raises(TABLE.TableValidationError, lambda: TABLE.decode_hash_preimage(raw))

    for length in (0, 15, 17):
        @add(f"physical-malformed-length-{length}")
        def _(length: int = length) -> None:
            expect_raises(TABLE.TableValidationError, lambda: TABLE.decode_physical_slot(b"\x00" * length))

    invalid_constructors: list[tuple[str, Callable[[], object]]] = [
        ("logical-reserved-tag", lambda: TABLE.LogicalPoint(2, 0, 0)),
        ("logical-noncanonical-o", lambda: TABLE.LogicalPoint(0, 1, 0)),
        ("logical-bool-tag", lambda: TABLE.LogicalPoint(True, 0, 0)),
        ("logical-bool-x", lambda: TABLE.LogicalPoint.affine(True, 0)),
        ("logical-negative", lambda: TABLE.LogicalPoint.affine(-1, 0)),
        ("logical-limit", lambda: TABLE.LogicalPoint.affine(1 << 28, 0)),
        ("physical-reserved-state", lambda: TABLE.PhysicalSlot(3, 0, 0, 0)),
        ("physical-noncanonical-empty", lambda: TABLE.PhysicalSlot(0, 0, 0, 1)),
        ("physical-noncanonical-o", lambda: TABLE.PhysicalSlot(2, 1, 0, 0)),
        ("physical-bool-state", lambda: TABLE.PhysicalSlot(True, 0, 0, 0)),
        ("physical-bool-exponent", lambda: TABLE.PhysicalSlot(1, 0, 0, True)),
        ("physical-limit", lambda: TABLE.PhysicalSlot(1, 0, 0, 1 << 28)),
    ]
    for name, function in invalid_constructors:
        @add(name)
        def _(function: Callable[[], object] = function) -> None:
            expect_raises(TABLE.TableValidationError, function)

    for name, function in (
        ("logical-encoder-wrong-domain", lambda: TABLE.encode_logical_point(TABLE.PhysicalSlot.empty())),
        ("hash-encoder-wrong-domain", lambda: TABLE.encode_hash_preimage(TABLE.PhysicalSlot.empty())),
        ("physical-encoder-wrong-domain", lambda: TABLE.encode_physical_slot(TABLE.LogicalPoint.infinity())),
    ):
        @add(name)
        def _(function: Callable[[], object] = function) -> None:
            expect_raises(TABLE.TableValidationError, function)

    # These three cases express the declared bytes-like decoder boundary.  The
    # current implementation is expected to fail them if bytes(raw) silently
    # treats an integer as a requested zero-filled length.
    @add("known-false-logical-integer-smuggling")
    def _() -> None:
        expect_raises((TypeError, TABLE.TableValidationError), lambda: TABLE.decode_logical_point(9))  # type: ignore[arg-type]

    @add("known-false-hash-bool-smuggling")
    def _() -> None:
        expect_raises((TypeError, TABLE.TableValidationError), lambda: TABLE.decode_hash_preimage(True))  # type: ignore[arg-type]

    @add("known-false-physical-integer-smuggling")
    def _() -> None:
        expect_raises((TypeError, TABLE.TableValidationError), lambda: TABLE.decode_physical_slot(16))  # type: ignore[arg-type]

    for budget, slots, capacity in ((8, 0, 0), (4096, 256, 179), (32768, 2048, 1433), (262144, 16384, 11468)):
        @add(f"capacity-{budget}-{slots}-{capacity}")
        def _(budget: int = budget, slots: int = slots, capacity: int = capacity) -> None:
            buffer = bytearray(16 * slots)
            table = TABLE.FixedPhysicalTable(budget, buffer)
            assert (table.slots, table.capacity, table.buffer_length, table.buffer_identity) == (slots, capacity, 16 * slots, id(buffer))

    @add("partial-budget-slack-valid")
    def _() -> None:
        buffer = bytearray(16)
        table = TABLE.FixedPhysicalTable(17, buffer)
        assert table.slots == 1 and table.capacity == 0 and table.buffer_length == 16

    for name, function in (
        ("constructor-partial-length", lambda: TABLE.FixedPhysicalTable(17, bytearray(17))),
        ("constructor-nonzero", lambda: TABLE.FixedPhysicalTable(16, bytearray(b"\x01" + b"\x00" * 15))),
        ("constructor-wrong-buffer", lambda: TABLE.FixedPhysicalTable(16, bytes(16))),
        ("constructor-bool-budget", lambda: TABLE.FixedPhysicalTable(True, bytearray())),
        ("constructor-negative-budget", lambda: TABLE.FixedPhysicalTable(-1, bytearray())),
    ):
        @add(name)
        def _(function: Callable[[], object] = function) -> None:
            expect_raises(TABLE.TableValidationError, function)

    @add("zero-slot-table-refusal")
    def _() -> None:
        buffer = bytearray()
        table = TABLE.FixedPhysicalTable(8, buffer)
        result = table.insert(TABLE.LogicalPoint.infinity(), 0)
        assert result.status == "TABLE_FULL"
        assert result.refusal and result.refusal["unchanged"] is True
        assert result.counters.hash_calls == result.counters.probes == result.counters.bytes_written == 0
        assert table.lookup(TABLE.LogicalPoint.infinity()).status == "NOT_FOUND"

    @add("slot-address-bounds")
    def _() -> None:
        table = TABLE.FixedPhysicalTable(32, bytearray(32))
        for value in (-1, 2, True):
            expect_raises(TABLE.TableValidationError, lambda value=value: table._offset(value))

    @add("forced-linear-collision-and-retention")
    def _() -> None:
        slots = 3
        buckets: dict[int, list[Any]] = defaultdict(list)
        for i in range(100):
            point = expected_table_point(i)
            buckets[independent_hash_slot(point, slots)].append(point)
        bucket, points = next((key, values) for key, values in buckets.items() if len(values) >= 2)
        first, second = points[:2]
        table = TABLE.FixedPhysicalTable(48, bytearray(48))
        first_result = table.insert(first, 4)
        second_result = table.insert(second, 9)
        assert first_result.status == second_result.status == "INSERTED"
        assert first_result.slot == bucket and second_result.slot == (bucket + 1) % slots
        assert table.lookup(first).exponent == 4 and table.lookup(second).exponent == 9
        assert table.counters().bytes_written == 32

    @add("duplicate-and-conflict-below-capacity")
    def _() -> None:
        table = TABLE.FixedPhysicalTable(80, bytearray(80))
        point = expected_table_point(3)
        assert table.insert(point, 7).status == "INSERTED"
        before = table.buffer_sha256(), table.occupied, table.counters().bytes_written
        assert table.insert(point, 7).status == "DUPLICATE"
        assert (table.buffer_sha256(), table.occupied, table.counters().bytes_written) == before
        conflict = table.insert(point, 8)
        assert conflict.status == "COMPLETED_INVALID" and conflict.refusal and conflict.refusal["unchanged"]
        assert (table.buffer_sha256(), table.occupied, table.counters().bytes_written) == before

    @add("table-full-priority-over-duplicate")
    def _() -> None:
        table = TABLE.FixedPhysicalTable(48, bytearray(48))
        first, second = expected_table_point(1), expected_table_point(2)
        assert table.insert(first, 1).status == "INSERTED"
        assert table.insert(second, 2).status == "INSERTED"
        before = table.counters(), table.buffer_sha256()
        result = table.insert(first, 99)
        after = table.counters(), table.buffer_sha256()
        assert result.status == "TABLE_FULL" and result.refusal and result.refusal["unchanged"]
        assert after[0].hash_calls == before[0].hash_calls
        assert after[0].probes == before[0].probes
        assert after[0].bytes_written == before[0].bytes_written and after[1] == before[1]

    for event in ("table_hash", "table_probe", "table_write"):
        @add(f"table-cancel-before-{event}")
        def _(event: str = event) -> None:
            buffer = bytearray(80)
            table = TABLE.FixedPhysicalTable(80, buffer)
            before = bytes(buffer)
            hook = HookLog(event)
            result = table.insert(expected_table_point(0), 0, hook)
            assert result.status == "CANCELLED" and result.refusal and result.refusal["unchanged"]
            assert bytes(buffer) == before and table.occupied == 0
            if event == "table_write":
                assert result.counters.probes == 1 and result.counters.bytes_read == 16 and result.counters.bytes_written == 0

    @add("caller-buffer-resize-blocked")
    def _() -> None:
        buffer = bytearray(80)
        table = TABLE.FixedPhysicalTable(80, buffer)
        assert table._buffer.obj is buffer and table.buffer_identity == id(buffer)
        expect_raises(BufferError, lambda: buffer.extend(b"\x00"))
        assert len(buffer) == table.buffer_length == 80

    @add("stale-external-reserved-state-rejected")
    def _() -> None:
        buffer = bytearray(80)
        table = TABLE.FixedPhysicalTable(80, buffer)
        point = expected_table_point(0)
        result = table.insert(point, 0)
        assert result.slot is not None
        offset = 16 * result.slot
        buffer[offset + 12:offset + 16] = struct.pack("<I", 3)
        expect_raises(TABLE.TableValidationError, lambda: table.lookup(point))

    @add("stale-external-canonical-zero-observed")
    def _() -> None:
        buffer = bytearray(80)
        table = TABLE.FixedPhysicalTable(80, buffer)
        point = expected_table_point(0)
        result = table.insert(point, 0)
        assert result.slot is not None and table.occupied == 1
        offset = 16 * result.slot
        buffer[offset:offset + 16] = b"\x00" * 16
        lookup = table.lookup(point)
        assert lookup.status == "NOT_FOUND" and table.occupied == 1

    @add("table-object-field-and-alias-inventory")
    def _() -> None:
        buffer = bytearray(80)
        table = TABLE.FixedPhysicalTable(80, buffer)
        expected = {
            "_budget_bytes", "_slots", "_buffer", "_buffer_identity", "_capacity", "_occupied",
            "_table_operations", "_hash_calls", "_hash_preimage_bytes", "_probes", "_bytes_read", "_bytes_written",
        }
        assert set(vars(table)) == expected
        assert isinstance(table._buffer, memoryview) and table._buffer.obj is buffer
        assert not any(isinstance(value, (dict, list, set)) for value in vars(table).values())

    @add("table-source-persistent-field-inventory")
    def _() -> None:
        tree = ast.parse((SOURCE_DIR / "table.py").read_text(encoding="utf-8"))
        assigned: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                        assigned.add(target.attr)
        expected = {
            "_budget_bytes", "_slots", "_buffer", "_buffer_identity", "_capacity", "_occupied",
            "_table_operations", "_hash_calls", "_hash_preimage_bytes", "_probes", "_bytes_read", "_bytes_written",
        }
        assert assigned == expected

    @add("hash-slot-golden-independent")
    def _() -> None:
        table = TABLE.FixedPhysicalTable(160, bytearray(160))
        for point in (TABLE.LogicalPoint.infinity(), expected_table_point(0), expected_table_point(9)):
            assert table._hash_slot(point, None) == independent_hash_slot(point, 10)

    for budget in (4096, 32768, 262144):
        @add(f"full-capacity-retention-eplus1-{budget}")
        def _(budget: int = budget) -> None:
            slots = budget // 16
            capacity = 7 * slots // 10
            buffer = bytearray(16 * slots)
            table = TABLE.FixedPhysicalTable(budget, buffer)
            for index in range(capacity):
                result = table.insert(expected_table_point(index), index)
                assert result.status == "INSERTED"
            before = (id(buffer), len(buffer), bytes(buffer), table.counters())
            refusal = table.insert(expected_table_point(capacity), capacity)
            after = (id(buffer), len(buffer), bytes(buffer), table.counters())
            assert refusal.status == "TABLE_FULL" and refusal.refusal and refusal.refusal["unchanged"]
            assert before[:3] == after[:3]
            assert after[3].occupied == capacity
            assert after[3].hash_calls == before[3].hash_calls
            assert after[3].probes == before[3].probes
            for index in range(capacity):
                found = table.lookup(expected_table_point(index))
                assert found.status == "FOUND" and found.exponent == index

    for scalar in (0, 1, 2, 13, 31):
        @add(f"bsgs-scalar-trace-{scalar}")
        def _(scalar: int = scalar) -> None:
            curve = FixedCyclicGroup(101)
            hook = HookLog()
            group = BSGS.CountingGroup(curve, hook)
            value = BSGS.left_to_right_scalar(group, scalar, 7, "certificate")
            assert value == (scalar * 7) % 101
            assert len(curve.add_calls) == independent_scalar_cost(scalar)
            assert group.snapshot().certificate == independent_scalar_cost(scalar)
            assert BSGS.scalar_cost(scalar) == independent_scalar_cost(scalar)

    for value in (-1, True, 1.5):
        @add(f"bsgs-scalar-invalid-{type(value).__name__}-{value}")
        def _(value: Any = value) -> None:
            group = BSGS.CountingGroup(FixedCyclicGroup(101))
            expect_raises(BSGS.SolverInputError, lambda: BSGS.left_to_right_scalar(group, value, 7, "certificate"))

    @add("counting-wrapper-o-doubling-negation")
    def _() -> None:
        curve = FixedCyclicGroup(11)
        group = BSGS.CountingGroup(curve)
        assert group.add(0, 3, "baby") == 3
        assert group.add(3, 3, "scalar_precompute") == 6
        assert group.neg(3) == 8
        snapshot = group.snapshot()
        assert snapshot.total_group_operations == snapshot.group_additions == 2
        assert snapshot.group_doublings == 1 and snapshot.negations == 1
        assert snapshot.baby == 1 and snapshot.scalar_precompute == 1

    normal_unbounded = ((3, 2), (5, 0), (5, 1), (17, 16), (19, 7), (31, 30))
    for order, scalar in normal_unbounded:
        @add(f"unbounded-trace-n{order}-k{scalar}")
        def _(order: int = order, scalar: int = scalar) -> None:
            curve = FixedCyclicGroup(order)
            hook = HookLog()
            result = BSGS.solve_unbounded(curve, 1, scalar, order, bsgs_buffer_for_unbounded(order), hook)
            m = __import__("math").isqrt(order - 1) + 1
            assert_solver_trace(result, curve, hook, order, scalar, m)

    for order, scalar, budget, should_solve in (
        (5, 4, 64, False),
        (5, 4, 80, True),
        (17, 16, 112, False),
        (17, 16, 128, True),
    ):
        @add(f"arm-a-n{order}-k{scalar}-c{budget}-{'solve' if should_solve else 'refuse'}")
        def _(order: int = order, scalar: int = scalar, budget: int = budget, should_solve: bool = should_solve) -> None:
            buffer = bytearray(16 * (budget // 16))
            before = bytes(buffer)
            curve = FixedCyclicGroup(order)
            hook = HookLog()
            result = BSGS.solve_arm_a(curve, 1, scalar, order, budget, buffer, hook)
            m = __import__("math").isqrt(order - 1) + 1
            if should_solve:
                assert_solver_trace(result, curve, hook, order, scalar, m)
            else:
                assert result.termination == "CAPACITY_REFUSAL"
                assert result.operations.total_group_operations == 0 and result.table.table_operations == 0
                assert bytes(buffer) == before and result.occupied == 0

    for order, scalar, budget in ((5, 4, 48), (5, 4, 80), (5, 4, 160), (17, 16, 80), (17, 16, 128)):
        @add(f"arm-b-trace-n{order}-k{scalar}-c{budget}")
        def _(order: int = order, scalar: int = scalar, budget: int = budget) -> None:
            capacity = 7 * (budget // 16) // 10
            m = min(capacity, order)
            curve = FixedCyclicGroup(order)
            hook = HookLog()
            result = BSGS.solve_arm_b(curve, 1, scalar, order, budget, bytearray(16 * (budget // 16)), hook)
            assert_solver_trace(result, curve, hook, order, scalar, m)

    @add("arm-b-zero-slot-refusal")
    def _() -> None:
        curve = FixedCyclicGroup(5)
        result = BSGS.solve_arm_b(curve, 1, 4, 5, 8, bytearray())
        assert result.termination == "CAPACITY_REFUSAL" and result.m == 0
        assert result.operations.total_group_operations == 0 and not curve.add_calls and not curve.neg_calls

    @add("false-hit-certificate-stops-invalid")
    def _() -> None:
        order, scalar = 17, 16
        curve = FalseHitGroup(order, false_point=scalar, aliases_to=1)
        result = BSGS.solve_unbounded(curve, 1, scalar, order, bsgs_buffer_for_unbounded(order), HookLog())
        assert result.termination == "COMPLETED_INVALID" and result.solution is None
        assert result.reason == "false table hit"
        assert result.operations.certificate == independent_scalar_cost(1) == 0

    @add("conflicting-baby-key-stops-invalid")
    def _() -> None:
        curve = FalseHitGroup(17, false_point=2, aliases_to=1)
        result = BSGS.solve_unbounded(curve, 1, 16, 17, bsgs_buffer_for_unbounded(17), HookLog())
        assert result.termination == "COMPLETED_INVALID" and result.reason == "conflicting baby key"
        assert result.operations.scalar_precompute == result.operations.giant == result.operations.certificate == 0

    @add("public-input-only-secret-traps")
    def _() -> None:
        curve = FixedCyclicGroup(17)
        result = BSGS.solve_unbounded(curve, 1, 11, 17, bsgs_buffer_for_unbounded(17), HookLog())
        assert result.termination == "SOLVED" and result.solution == 11

    @add("no-final-giant-addition-on-exhaustion")
    def _() -> None:
        order, m = 17, 5
        curve = NoHitEncodingGroup(order, baby_encoding_calls=m)
        result = BSGS.solve_unbounded(curve, 1, 16, order, bsgs_buffer_for_unbounded(order), HookLog())
        blocks = (order + m - 1) // m
        assert result.termination == "NOT_FOUND"
        assert result.operations.giant == blocks - 1 and result.operations.negations == blocks - 1

    @add("cancel-before-first-baby-work")
    def _() -> None:
        buffer = bsgs_buffer_for_unbounded(17)
        curve = FixedCyclicGroup(17)
        result = BSGS.solve_unbounded(curve, 1, 16, 17, buffer, HookLog("baby_step"))
        assert result.termination == "CANCELLED" and result.occupied == 0
        assert result.operations.total_group_operations == 0 and result.table.table_operations == 0
        assert not curve.add_calls and bytes(buffer) == b"\x00" * len(buffer)

    @add("cancel-before-scalar-operation-retains-baby")
    def _() -> None:
        order = 17
        curve = FixedCyclicGroup(order)
        hook = HookLog("scalar_precompute")
        result = BSGS.solve_unbounded(curve, 1, 16, order, bsgs_buffer_for_unbounded(order), hook)
        m = 5
        assert result.termination == "CANCELLED" and result.occupied == m
        assert result.operations.baby == m - 1 and result.operations.scalar_precompute == 0
        assert len(curve.add_calls) == m - 1

    @add("cancel-before-giant-operation-retains-negation")
    def _() -> None:
        order = 17
        curve = FixedCyclicGroup(order)
        result = BSGS.solve_unbounded(curve, 1, 16, order, bsgs_buffer_for_unbounded(order), HookLog("giant"))
        assert result.termination == "CANCELLED"
        assert result.operations.giant == 0 and result.operations.negations == 1
        assert len(curve.neg_calls) == 1

    @add("cancel-before-certificate-operation")
    def _() -> None:
        order, scalar = 17, 6
        curve = FixedCyclicGroup(order)
        result = BSGS.solve_unbounded(curve, 1, scalar, order, bsgs_buffer_for_unbounded(order), HookLog("certificate"))
        assert result.termination == "CANCELLED" and result.solution is None
        assert result.operations.certificate == 0

    for value in (0, -1, True):
        @add(f"solver-order-invalid-{type(value).__name__}-{value}")
        def _(value: Any = value) -> None:
            expect_raises(BSGS.SolverInputError, lambda: BSGS.solve_unbounded(FixedCyclicGroup(5), 1, 2, value, bytearray()))

    @add("solver-signatures-have-no-secret")
    def _() -> None:
        for function in (BSGS.solve_unbounded, BSGS.solve_arm_a, BSGS.solve_arm_b, BSGS._common_bsgs):
            names = set(inspect.signature(function).parameters)
            assert not names.intersection({"k", "secret", "known_scalar", "oracle"})

    @add("rho-exact-permitted-span-and-hashes")
    def _() -> None:
        base, derivative, base_start, base_end, derivative_start, derivative_end, nested = rho_spans()
        assert base_start == derivative_start == 2044
        assert base_end == 2580 and derivative_end == 2524
        assert derivative[derivative_start:derivative_end] == nested
        assert derivative == base[:base_start] + nested + base[base_end:]
        assert sha256_bytes(base) == "de952371bfa0513b4783e78012f7eddb1098ef2a1fef5bd9adc2b34e2a86bcc0"
        assert sha256_bytes(derivative) == "0d05b954593d1d6adeb8f0764eb0acda280f938f58cb453f1259fd0e61eaa233"

    @add("rho-outside-span-known-false-control")
    def _() -> None:
        candidate = bytearray(DERIVATIVE_RHO.read_bytes())
        candidate[3] ^= 1
        assert not derivative_conforms(bytes(candidate))

    @add("rho-wrong-inside-span-known-false-control")
    def _() -> None:
        candidate = DERIVATIVE_RHO.read_bytes().replace(b"k_val == 0", b"k_val == 1", 1)
        assert not derivative_conforms(candidate)

    @add("rho-binding-span-graph")
    def _() -> None:
        binding = json.loads((SOURCE_DIR / "solver-source-bindings.json").read_text(encoding="utf-8"))
        proof = binding["rho_scalar_derivative"]
        base, derivative, base_start, base_end, derivative_start, derivative_end, _ = rho_spans()
        assert proof["base_span"] == {"start_byte": base_start, "end_byte": base_end, "sha256": sha256_bytes(base[base_start:base_end])}
        assert proof["replacement_span"] == {"start_byte": derivative_start, "end_byte": derivative_end, "sha256": sha256_bytes(derivative[derivative_start:derivative_end])}
        assert proof["base_sha256"] == sha256_bytes(base)
        assert proof["derivative_sha256"] == sha256_bytes(derivative)
        assert proof["relative_imports_preserved"] is True and proof["full_rho_solve_called"] is False

    for scalar in (-1, 0, 1, 2, 13, 31):
        @add(f"rho-isolated-scalar-{scalar}")
        def _(scalar: int = scalar) -> None:
            exercise = rho_scalar_wrapper()
            curve = ScalarAdd(101)
            if scalar < 0:
                exc = expect_raises(ValueError, lambda: exercise(curve, scalar, 7))
                assert str(exc) == "nonnegative scalar required" and not curve.calls
            else:
                value, count = exercise(curve, scalar, 7)
                expected_value = None if scalar == 0 else (7 * scalar) % 101
                assert value == expected_value
                assert count == len(curve.calls) == independent_scalar_cost(scalar)

    @add("all-49-declared-source-bindings")
    def _() -> None:
        rows = source_binding_rows()
        assert len(rows) == 49
        for row in rows:
            path = REPO / row["path"]
            assert path.is_file() and sha256_path(path) == row["sha256"]

    @add("authority-claim-and-source-snapshot-graph")
    def _() -> None:
        assert git_text("show", "-s", "--format=%P", CLAIM_COMMIT) == AUTHORITY_COMMIT
        assert git_bytes(AUTHORITY_COMMIT, HANDOFF_PATH.relative_to(REPO).as_posix()) == HANDOFF_PATH.read_bytes()
        assert git_bytes(AUTHORITY_COMMIT, PLAN_PATH.relative_to(REPO).as_posix()) == PLAN_PATH.read_bytes()
        assert subprocess.run(["git", "merge-base", "--is-ancestor", SOURCE_SNAPSHOT, CLAIM_COMMIT], cwd=REPO).returncode == 0
        assert subprocess.run(["git", "merge-base", "--is-ancestor", CLAIM_COMMIT, "HEAD"], cwd=REPO).returncode == 0
        for path in (HANDOFF_PATH, PLAN_PATH, SOURCE_DIR / "table.py", SOURCE_DIR / "bsgs.py", DERIVATIVE_RHO):
            relative = path.relative_to(REPO).as_posix()
            assert git_bytes(CLAIM_COMMIT, relative) == path.read_bytes()

    @add("source-snapshot-binds-final-package")
    def _() -> None:
        snapshot = json.loads((REPO / "coordination/experiment-reserve/BATCH-635652/archives/TASK-20260908-77bb0a/snapshot.json").read_text())
        assert snapshot["parent_sha"] == "1f42ba69e2d9509f50364853c8ebcd60b4f3a159"
        for path, expected in snapshot["source_path_sha256"].items():
            live = (REPO / path).read_bytes()
            assert sha256_bytes(live) == expected
            assert git_bytes(SOURCE_SNAPSHOT, path) == live

    @add("kernel-bytes-preserved-from-failed-predecessor")
    def _() -> None:
        for name in ("table.py", "bsgs.py", "rho-corrected.py"):
            assert (ORIGINAL_DIR / name).read_bytes() == (SOURCE_DIR / name).read_bytes()

    @add("producer-release-hashes-complete")
    def _() -> None:
        release = json.loads((REPO / "coordination/experiment-reserve/BATCH-635652/claims/TASK-20260908-7771f2.1.release.json").read_text())
        assert release["outcome"] == "completed" and release["task_id"] == "TASK-20260908-7771f2"
        assert len(release["artifact_sha256"]) == 8
        for path, expected in release["artifact_sha256"].items():
            assert sha256_path(REPO / path) == expected

    @add("corrected-producer-all-320-outcomes")
    def _() -> None:
        receipt = json.loads((SOURCE_DIR / "check-receipt.json").read_text())
        assert receipt["accounting"] == {"complete_suites": 1, "failed": 0, "maximum_fixed_cases": 640, "passed": 320, "remaining": 320, "reruns": 0, "total_fixed_cases": 320}
        assert len(receipt["attempts"]) == 1
        inner = receipt["attempts"][0]["inner_receipt"]
        reserved = inner["case_reservation"]["cases"]
        cases320 = inner["worker"]["cases"]
        assert len(reserved) == len(cases320) == 320
        assert [(row["ordinal"], row["name"]) for row in reserved] == [(row["ordinal"], row["name"]) for row in cases320]
        assert [row["ordinal"] for row in cases320] == list(range(1, 321))
        assert len({row["name"] for row in cases320}) == 320
        assert Counter(row["status"] for row in cases320) == Counter({"passed": 320})
        for row in cases320:
            assert row["wall_seconds"] <= 10 and row["cpu_seconds"] >= 0 and row["rss_raw"] >= 0 and row["started_utc"].endswith("Z")

    @add("corrected-producer-inner-process-custody")
    def _() -> None:
        receipt = json.loads((SOURCE_DIR / "check-receipt.json").read_text())
        inner = receipt["attempts"][0]["inner_receipt"]
        handling = inner["process_handling"]
        assert inner["exit_code"] == 0 and inner["worker"]["failed"] == 0
        assert handling["full_popen_handle_retained"] and handling["terminal_observed"]
        assert handling["stdout_redirected_before_launch"] and handling["stderr_redirected_before_launch"]
        assert isinstance(handling["worker_pid"], int) and handling["poll_count_before_terminal"] >= 0
        assert inner["stdout"] == '{"executed": 320, "failed": 0, "reserved": 320}\n' and inner["stderr"] == ""

    @add("corrected-producer-outer-process-custody")
    def _() -> None:
        receipt = json.loads((SOURCE_DIR / "check-receipt.json").read_text())
        attempt = receipt["attempts"][0]
        outer = attempt["outer_process_custody"]
        assert outer["case_reservation"] == 320 and outer["maximum_cumulative"] == 640
        assert outer["initial_tool_result"]["session_id"] == 76113
        assert outer["polls"] and outer["polls"][-1]["exit_code"] == 0
        assert outer["started_utc"].endswith("UTC") and outer["ended_utc"].endswith("UTC")
        assert attempt["outer_stdout"] == "" and "maximum resident set size" in attempt["outer_stderr"]

    @add("producer-receipt-report-hash-acyclic")
    def _() -> None:
        receipt = json.loads((SOURCE_DIR / "check-receipt.json").read_text())
        inner_sources = receipt["attempts"][0]["inner_receipt"]["source_sha256"]
        assert set(inner_sources) == {"table.py", "bsgs.py", "rho-corrected.py", "tests.py", "solver-source-bindings.json"}
        for name, expected in inner_sources.items():
            assert sha256_path(SOURCE_DIR / name) == expected
        report = load_yaml(SOURCE_DIR / "implementation-report.yaml")["execution_report"]
        assert report["fixed_suite"]["receipt_sha256"] == sha256_path(SOURCE_DIR / "check-receipt.json")
        assert "implementation-report.yaml" not in inner_sources and "check-receipt.json" not in inner_sources
        binding = json.loads((SOURCE_DIR / "solver-source-bindings.json").read_text())
        assert binding["receipt_self_hash"] is None
        assert not {"implementation-report.yaml", "check-receipt.json"}.intersection(binding["task_source_sha256"])

    @add("historical-failure-custody-truthful")
    def _() -> None:
        original = json.loads((ORIGINAL_DIR / "check-receipt.json").read_text())
        cases320 = original["worker"]["cases"]
        assert len(cases320) == 320 and Counter(row["status"] for row in cases320) == Counter({"passed": 313, "failed": 7})
        assert original["exit_code"] == 1 and original["worker"]["failed"] == 7
        custody = json.loads((REPO / "coordination/experiment-reserve/admission-20260907/bsgs-first-kernel-delivery-custody.json").read_text())
        assert custody["fixed_case_executions"] == 320 and custody["passes"] == 313 and custody["failures"] == 7
        assert custody["worker_exit_code"] == 1 and custody["outer_terminal_exit_code"] is None
        assert "not reliable" in custody["outer_status_limitation"]

    @add("model-policy-native-assignment-boundary")
    def _() -> None:
        policies = load_yaml(REPO / "orchestration/model-policies.yaml")
        bindings = load_yaml(REPO / "orchestration/model-bindings.yaml")
        policy = policies["policies"]["review-adversarial"]
        assert policy["reasoning_effort"] == "xhigh" and policy["independent_session_required"] is True
        selected = bindings["bindings"]["openai"]["review-adversarial"]
        assert selected["model"] == "gpt-5.6-sol"
        assert "bedrock" not in json.dumps(selected).lower()

    @add("review-plan-joint-and-known-false-controls")
    def _() -> None:
        plan = load_yaml(PLAN_PATH)["review_plan"]
        assert len(plan["joints"]) == 1
        assert plan["joints"][0]["assigned_to"] == TASK_ID
        assert plan["proves_too_much"]["assigned_to"] == TASK_ID
        objects = " ".join(plan["proves_too_much"]["objects"])
        for token in ("Zero-slot", "Physical empty", "duplicate exponent", "ArmA", "secret/oracle", "extra byte", "cancellation"):
            assert token in objects
        assert plan["blind_rederivation"]["required"] is False

    assert len(cases) <= MAXIMUM_CASES, len(cases)
    assert len({case.name for case in cases}) == len(cases)
    return cases


class CaseTimeout(TimeoutError):
    pass


def _timeout_handler(_signum: int, _frame: object) -> None:
    raise CaseTimeout(f"case exceeded {PER_CASE_LIMIT_SECONDS}s")


def worker_payload() -> dict[str, object]:
    hard_limit: dict[str, object]
    try:
        before_limit = resource.getrlimit(resource.RLIMIT_AS)
        hard_ceiling = before_limit[1]
        desired_soft = MEMORY_LIMIT_BYTES if hard_ceiling == resource.RLIM_INFINITY else min(MEMORY_LIMIT_BYTES, hard_ceiling)
        resource.setrlimit(resource.RLIMIT_AS, (desired_soft, hard_ceiling))
        readback = resource.getrlimit(resource.RLIMIT_AS)
        hard_limit = {
            "attempted": True,
            "installed": readback[0] == MEMORY_LIMIT_BYTES,
            "before_bytes": list(before_limit),
            "readback_bytes": list(readback),
            "error": None,
        }
    except BaseException as exc:  # noqa: BLE001 - inability to enforce must be retained, not hidden
        hard_limit = {"attempted": True, "installed": False, "before_bytes": None, "readback_bytes": None, "error": f"{type(exc).__name__}: {exc}"}

    global TABLE, BSGS
    TABLE, BSGS = load_target_modules()
    cases = build_cases()
    started_utc = utc_now()
    started_wall = time.monotonic()
    started_cpu = time.process_time()
    outcomes: list[dict[str, object]] = []
    signal.signal(signal.SIGALRM, _timeout_handler)
    for ordinal, case in enumerate(cases, start=1):
        case_started_utc = utc_now()
        wall0 = time.monotonic()
        cpu0 = time.process_time()
        signal.setitimer(signal.ITIMER_REAL, PER_CASE_LIMIT_SECONDS)
        try:
            case.function()
            status, detail = "passed", ""
        except BaseException as exc:  # noqa: BLE001 - each exact failure is a retained result
            status = "failed"
            detail = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        usage = resource.getrusage(resource.RUSAGE_SELF)
        outcomes.append({
            "ordinal": ordinal,
            "name": case.name,
            "status": status,
            "detail": detail,
            "started_utc": case_started_utc,
            "wall_seconds": time.monotonic() - wall0,
            "cpu_seconds": time.process_time() - cpu0,
            "peak_rss_bytes": _ru_maxrss_bytes(usage.ru_maxrss),
        })
    finished_utc = utc_now()
    wall_seconds = time.monotonic() - started_wall
    cpu_seconds = time.process_time() - started_cpu
    counts = Counter(row["status"] for row in outcomes)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return {
        "schema": "crypto.autoresearch.independent_fixed_source_worker.v1",
        "task_id": TASK_ID,
        "scientific_runs": 0,
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "reserved_case_count": len(cases),
        "executed_case_count": len(outcomes),
        "passed": counts["passed"],
        "failed": counts["failed"],
        "wall_seconds": wall_seconds,
        "cpu_seconds": cpu_seconds,
        "peak_rss_bytes": _ru_maxrss_bytes(usage.ru_maxrss),
        "hard_memory_limit": hard_limit,
        "limits": {
            "per_case_wall_seconds": PER_CASE_LIMIT_SECONDS,
            "aggregate_wall_or_cpu_seconds": AGGREGATE_LIMIT_SECONDS,
            "maximum_workers": 1,
            "memory_limit_bytes": MEMORY_LIMIT_BYTES,
        },
        "cases": outcomes,
    }


def run_worker(output: Path) -> int:
    payload = worker_payload()
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"reserved": payload["reserved_case_count"], "executed": payload["executed_case_count"], "passed": payload["passed"], "failed": payload["failed"]}, sort_keys=True))
    return 0 if payload["failed"] == 0 else 1


def run_final(output: Path) -> int:
    names = [case.name for case in build_cases()]
    reservation = [{"ordinal": ordinal, "name": name} for ordinal, name in enumerate(names, start=1)]
    with tempfile.TemporaryDirectory(prefix="task-20260908-a71bba-") as temporary:
        temp = Path(temporary)
        worker_result = temp / "worker-result.json"
        stdout_path = temp / "worker.stdout.log"
        stderr_path = temp / "worker.stderr.log"
        command = [sys.executable, "-B", str(Path(__file__).resolve()), "--worker", str(worker_result)]
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        started_utc = utc_now()
        started_wall = time.monotonic()
        child_before = resource.getrusage(resource.RUSAGE_CHILDREN)
        with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
            process = subprocess.Popen(command, cwd=HERE, env=environment, stdout=stdout_handle, stderr=stderr_handle)
            worker_pid = process.pid
            poll_count = 0
            while process.poll() is None:
                poll_count += 1
                if time.monotonic() - started_wall > AGGREGATE_LIMIT_SECONDS:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    break
                time.sleep(0.005)
            exit_code = int(process.returncode)
        child_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        finished_utc = utc_now()
        wall_seconds = time.monotonic() - started_wall
        child_user = child_after.ru_utime - child_before.ru_utime
        child_system = child_after.ru_stime - child_before.ru_stime
        worker = json.loads(worker_result.read_text(encoding="utf-8")) if worker_result.exists() else None
        stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
        stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
        receipt = {
            "schema": "crypto.autoresearch.independent_fixed_source_inner_receipt.v1",
            "task_id": TASK_ID,
            "experiment_id": EXPERIMENT_ID,
            "kind": "independent_fixed_synthetic_source_conformance_only",
            "scientific_runs": 0,
            "command": command,
            "cwd": str(HERE),
            "started_utc": started_utc,
            "finished_utc": finished_utc,
            "exit_code": exit_code,
            "case_reservation": {"count": len(reservation), "cases": reservation},
            "process_handling": {
                "full_popen_handle_retained": True,
                "worker_pid": worker_pid,
                "poll_count_before_terminal": poll_count,
                "terminal_observed": process.returncode is not None,
                "stdout_redirected_before_launch": True,
                "stderr_redirected_before_launch": True,
            },
            "actual_telemetry": {
                "parent_wall_seconds": wall_seconds,
                "children_user_cpu_seconds": child_user,
                "children_system_cpu_seconds": child_system,
                "children_total_cpu_seconds": child_user + child_system,
                "children_peak_rss_bytes": _ru_maxrss_bytes(child_after.ru_maxrss),
                "per_case_timeout_seconds": PER_CASE_LIMIT_SECONDS,
                "aggregate_executed_check_wall_or_cpu_limit_seconds": AGGREGATE_LIMIT_SECONDS,
                "aggregate_wall_and_cpu_within_limit": wall_seconds <= AGGREGATE_LIMIT_SECONDS and (child_user + child_system) <= AGGREGATE_LIMIT_SECONDS,
                "maximum_workers_used": 1,
                "machine_memory_limit_bytes": MEMORY_LIMIT_BYTES,
            },
            "source_sha256": {
                "checks.py": sha256_path(Path(__file__).resolve()),
                "table.py": sha256_path(SOURCE_DIR / "table.py"),
                "bsgs.py": sha256_path(SOURCE_DIR / "bsgs.py"),
                "rho-corrected.py": sha256_path(SOURCE_DIR / "rho-corrected.py"),
                "solver-source-bindings.json": sha256_path(SOURCE_DIR / "solver-source-bindings.json"),
                "handoff": sha256_path(HANDOFF_PATH),
                "review_plan": sha256_path(PLAN_PATH),
                "effective_contract": sha256_path(CONTRACT_PATH),
            },
            "stdout": stdout,
            "stderr": stderr,
            "worker": worker,
            "limitations": [
                "No scientific curve, fixture, manifest, rho solve, Docker, runtime guard, RUN allocation, signature, key, or experiment pipeline was invoked.",
                "The fixed cyclic groups and malformed representations are source-component controls only.",
            ],
            "receipt_self_hash": None,
            "receipt_self_hash_note": "intentionally omitted to avoid self-reference",
        }
        output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return exit_code


def assemble(args: argparse.Namespace) -> int:
    inner = json.loads(Path(args.inner).read_text(encoding="utf-8"))
    initial = json.loads(args.initial_json)
    terminal = json.loads(args.terminal_json)
    cases = inner.get("worker", {}).get("cases", [])
    counts = Counter(row.get("status") for row in cases)
    attempt = {
        "attempt": 1,
        "inner_receipt": inner,
        "outer_process_custody": {
            "command": args.outer_command,
            "cwd": str(REPO),
            "started_utc": args.outer_started_utc,
            "ended_utc": args.outer_ended_utc,
            "case_reservation": inner["case_reservation"]["count"],
            "maximum_cumulative": 320,
            "initial_tool_result": initial,
            "terminal_result": terminal,
        },
        "outer_stdout": Path(args.outer_stdout).read_text(encoding="utf-8", errors="replace"),
        "outer_stderr": Path(args.outer_stderr).read_text(encoding="utf-8", errors="replace"),
    }
    attempts: list[dict[str, object]] = []
    if args.previous_receipt is not None:
        previous = json.loads(Path(args.previous_receipt).read_text(encoding="utf-8"))
        attempts.extend(previous["attempts"])
    attempt["attempt"] = len(attempts) + 1
    attempts.append(attempt)
    all_cases = [row for item in attempts for row in item["inner_receipt"].get("worker", {}).get("cases", [])]
    all_counts = Counter(row.get("status") for row in all_cases)
    receipt = {
        "schema": "crypto.autoresearch.independent_source_review_receipt.v1",
        "task_id": TASK_ID,
        "experiment_id": EXPERIMENT_ID,
        "scientific_runs": 0,
        "authority_commit": AUTHORITY_COMMIT,
        "published_claim_commit": CLAIM_COMMIT,
        "source_snapshot": SOURCE_SNAPSHOT,
        "case_accounting": {
            "maximum_fixed_cases": 320,
            "complete_suites": len(attempts),
            "reruns": len(attempts) - 1,
            "total_fixed_cases": len(all_cases),
            "passed": all_counts["passed"],
            "failed": all_counts["failed"],
            "remaining": 320 - len(all_cases),
            "complete_suite_limit": MAXIMUM_CASES,
        },
        "attempts": attempts,
        "inference": {
            "role": "validator",
            "requested_policy": "review-adversarial",
            "reasoning_effort": "xhigh",
            "resolved_model_id": "gpt-5.6-sol",
            "resolution_basis": "native independent session assignment; no fresh serving probe asserted",
            "model_verified_by_fresh_probe": False,
            "fallback_used": False,
            "degraded_requirements": [],
            "provider_contains_bedrock": False,
            "independent_session": True,
        },
        "receipt_self_hash": None,
        "receipt_self_hash_note": "Coordinator snapshot binds this receipt externally; no self-hash is asserted.",
    }
    Path(args.assemble).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--list", action="store_true")
    modes.add_argument("--worker", type=Path)
    modes.add_argument("--final", type=Path)
    modes.add_argument("--assemble", type=Path)
    parser.add_argument("--inner")
    parser.add_argument("--outer-stdout")
    parser.add_argument("--outer-stderr")
    parser.add_argument("--outer-command")
    parser.add_argument("--outer-started-utc")
    parser.add_argument("--outer-ended-utc")
    parser.add_argument("--initial-json")
    parser.add_argument("--terminal-json")
    parser.add_argument("--previous-receipt")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.list:
        global TABLE, BSGS
        TABLE, BSGS = load_target_modules()
        cases = build_cases()
        print(json.dumps({"count": len(cases), "names": [case.name for case in cases]}, indent=2))
        return 0
    if args.worker is not None:
        return run_worker(args.worker)
    if args.final is not None:
        return run_final(args.final)
    required = (args.inner, args.outer_stdout, args.outer_stderr, args.outer_command, args.outer_started_utc, args.outer_ended_utc, args.initial_json, args.terminal_json)
    if not all(value is not None for value in required):
        raise SystemExit("--assemble requires complete outer-custody arguments")
    return assemble(args)


if __name__ == "__main__":
    raise SystemExit(main())
