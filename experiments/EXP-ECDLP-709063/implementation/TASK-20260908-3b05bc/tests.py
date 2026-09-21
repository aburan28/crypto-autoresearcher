"""Reserved fixed-source conformance suite for TASK-20260908-3b05bc.

This is a source-component checker.  Its group is a fixed finite cyclic test
double, never an elliptic-curve generator or an experiment instance.  The
``--final`` parent redirects its worker's stdout and stderr *before* launch,
retains the full Popen handle, polls it to a terminal state, and writes the
only execution receipt allowed by the handoff.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import ast
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tempfile
import time
from typing import Callable

from bsgs import (
    CountingGroup,
    SolverInputError,
    left_to_right_scalar,
    scalar_cost,
    solve_arm_a,
    solve_arm_b,
    solve_unbounded,
)
from table import (
    AFFINE,
    EMPTY,
    INFINITY,
    FixedPhysicalTable,
    LogicalPoint,
    PhysicalSlot,
    TableValidationError,
    decode_hash_preimage,
    decode_logical_point,
    decode_physical_slot,
    encode_hash_preimage,
    encode_logical_point,
    encode_physical_slot,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
BASE_RHO = REPO / "harness" / "rho.py"
DERIVATIVE_RHO = HERE / "rho-corrected.py"
BINDINGS = HERE / "solver-source-bindings.json"
RECEIPT = HERE / "check-receipt.json"
UINT28 = 1 << 28


class CheckFailure(AssertionError):
    pass


def check(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def expect_raises(exc_type: type[BaseException], action: Callable[[], object]) -> None:
    try:
        action()
    except exc_type:
        return
    except BaseException as exc:  # pragma: no cover - carried to receipt if it happens
        raise CheckFailure(f"expected {exc_type.__name__}, saw {type(exc).__name__}") from exc
    raise CheckFailure(f"expected {exc_type.__name__}")


@dataclass(frozen=True)
class Case:
    name: str
    action: Callable[[], None]


class FixedCyclicGroup:
    """Complete, fixed synthetic group whose log records actual add calls."""

    def __init__(self, order: int, misencode: dict[int, int] | None = None) -> None:
        self.order = order
        self.calls: list[tuple[int, int]] = []
        self.neg_calls: list[int] = []
        self._misencode = dict(misencode or {})

    def identity(self) -> int:
        return 0

    def add(self, left: int, right: int) -> int:
        self.calls.append((left, right))
        return (left + right) % self.order

    def neg(self, point: int) -> int:
        self.neg_calls.append(point)
        return (-point) % self.order

    def equals(self, left: int, right: int) -> bool:
        return left == right

    def encode_point(self, point: int) -> LogicalPoint:
        encoded = self._misencode.get(point, point)
        return LogicalPoint.affine(encoded, 0)


class OracleSecretGroup(FixedCyclicGroup):
    @property
    def oracle_secret(self) -> int:
        raise CheckFailure("solver read forbidden oracle secret")


class ScalarAdd:
    def __init__(self, order: int) -> None:
        self.order = order
        self.calls: list[tuple[int | None, int | None]] = []

    def add(self, left: int | None, right: int | None) -> int | None:
        self.calls.append((left, right))
        if left is None:
            return right
        if right is None:
            return left
        return (left + right) % self.order


POINTS = (
    LogicalPoint.infinity(),
    LogicalPoint.affine(0, 0),
    LogicalPoint.affine(1, 2),
    LogicalPoint.affine(2, 1),
    LogicalPoint.affine(3, 5),
    LogicalPoint.affine(7, 11),
    LogicalPoint.affine(13, 17),
    LogicalPoint.affine(19, 23),
    LogicalPoint.affine(31, 37),
    LogicalPoint.affine(41, 43),
    LogicalPoint.affine(257, 263),
    LogicalPoint.affine(4093, 4091),
    LogicalPoint.affine(65521, 7),
    LogicalPoint.affine(1 << 20, (1 << 20) - 1),
    LogicalPoint.affine(UINT28 - 2, UINT28 - 3),
    LogicalPoint.affine(UINT28 - 1, UINT28 - 1),
)
EXACT_CAPACITIES = ((8, 0, 0), (4096, 256, 179), (32768, 2048, 1433), (262144, 16384, 11468))
ORDERS = (5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101)
VECTORS = tuple((order, max(2, order - 1)) for order in ORDERS)
SECOND_VECTORS = tuple((order, ((order // 2) + 1) % order or 1) for order in ORDERS)
SCALARS = (0, 1, 2, 3, 4, 5, 6, 7, 8, 15, 16, 31, 32, 37, 63, 64)


def fixed_point(index: int) -> LogicalPoint:
    """A deterministic encoded fixture object, not a generated curve point."""
    if type(index) is not int or index < 0 or index >= UINT28 - 1:
        raise CheckFailure("fixed point index outside declared fixture domain")
    return LogicalPoint.affine(index + 1, (3 * index + 7) % UINT28)


def buffer_for_budget(budget: int) -> bytearray:
    return bytearray(16 * (budget // 16))


def expected_bsgs_cost(m: int, target: int) -> int:
    return (m - 1) + scalar_cost(m) + (target // m) + scalar_cost(target)


def check_logical_roundtrip(point: LogicalPoint) -> None:
    raw = encode_logical_point(point)
    check(len(raw) == 9, "logical encoding must be nine bytes")
    check(decode_logical_point(raw) == point, "logical roundtrip mismatch")


def check_hash_roundtrip(point: LogicalPoint) -> None:
    raw = encode_hash_preimage(point)
    check(len(raw) == (1 if point.is_infinity else 9), "hash-preimage length mismatch")
    check(decode_hash_preimage(raw) == point, "hash-preimage roundtrip mismatch")


def check_physical_roundtrip(point: LogicalPoint, exponent: int) -> None:
    record = PhysicalSlot.from_logical(point, exponent)
    raw = encode_physical_slot(record)
    check(len(raw) == 16, "physical slot must be 16 bytes")
    decoded = decode_physical_slot(raw)
    check(decoded == record, "physical slot roundtrip mismatch")
    check(decoded.logical_point() == point, "physical logical projection mismatch")


def check_exact_capacity(budget: int, slots: int, capacity: int) -> None:
    table = FixedPhysicalTable(budget, buffer_for_budget(budget))
    check((table.slots, table.capacity, table.buffer_length) == (slots, capacity, 16 * slots), "capacity mismatch")


def check_e_plus_one(budget: int, expected_capacity: int) -> None:
    raw = buffer_for_budget(budget)
    table = FixedPhysicalTable(budget, raw)
    identity = table.buffer_identity
    for index in range(expected_capacity):
        inserted = table.insert(fixed_point(index), index)
        check(inserted.status == "INSERTED", f"fixed insert {index} failed")
    before = table.buffer_sha256()
    result = table.insert(fixed_point(expected_capacity), expected_capacity)
    check(result.status == "TABLE_FULL", "E+1 must refuse before a write")
    check(result.refusal is not None and result.refusal["unchanged"] is True, "E+1 buffer changed")
    check(table.buffer_identity == identity and table.buffer_length == 16 * table.slots, "buffer identity/length changed")
    check(table.buffer_sha256() == before and table.occupied == expected_capacity, "E+1 occupancy changed")
    for index in range(expected_capacity):
        found = table.lookup(fixed_point(index))
        check(found.status == "FOUND" and found.exponent == index, "retained lookup failed after E+1")


def check_duplicate_and_conflict(budget: int) -> None:
    table = FixedPhysicalTable(budget, buffer_for_budget(budget))
    point = fixed_point(3)
    check(table.insert(point, 4).status == "INSERTED", "initial insert failed")
    duplicate = table.insert(point, 4)
    check(duplicate.status == "DUPLICATE" and table.occupied == 1, "duplicate changed occupancy")
    before = table.buffer_sha256()
    conflict = table.insert(point, 5)
    check(conflict.status == "COMPLETED_INVALID", "conflicting exponent was accepted")
    check(conflict.refusal is not None and conflict.refusal["unchanged"] is True, "conflict changed buffer")
    check(table.buffer_sha256() == before and table.occupied == 1, "conflict changed table state")


def check_forced_collision(budget: int) -> None:
    table = FixedPhysicalTable(budget, buffer_for_budget(budget))
    check(table.capacity >= 2, "collision fixture needs two usable entries")
    buckets: dict[int, list[LogicalPoint]] = {}
    for point in POINTS[:8]:
        slot = int.from_bytes(sha256(b"EXP-ECDLP-709063|table|v2" + encode_hash_preimage(point)).digest()[:8], "little") % table.slots
        buckets.setdefault(slot, []).append(point)
    pair = next((values[:2] for values in buckets.values() if len(values) >= 2), None)
    check(pair is not None, "fixed pigeonhole collision fixture did not collide")
    first, second = pair
    check(table.insert(first, 1).status == "INSERTED", "collision first insert failed")
    check(table.insert(second, 2).status == "INSERTED", "collision second insert failed")
    check(table.lookup(first).exponent == 1 and table.lookup(second).exponent == 2, "collision lookup failed")


def check_table_lookup(index: int) -> None:
    table = FixedPhysicalTable(256, buffer_for_budget(256))
    point = fixed_point(index)
    check(table.insert(point, index).status == "INSERTED", "lookup fixture insert failed")
    found = table.lookup(point)
    absent = table.lookup(fixed_point(index + 100))
    check(found.status == "FOUND" and found.exponent == index, "present lookup failed")
    check(absent.status == "NOT_FOUND", "absent lookup falsely found")


def check_single_insert(point: LogicalPoint) -> None:
    table = FixedPhysicalTable(256, buffer_for_budget(256))
    result = table.insert(point, 1)
    check(result.status == "INSERTED", "single fixed point insertion failed")
    check(result.counters.bytes_written == 16, "one physical insertion must write exactly one slot")
    found = table.lookup(point)
    check(found.status == "FOUND" and found.exponent == 1, "single fixed point did not remain readable")


def check_budget_slack(budget: int) -> None:
    table = FixedPhysicalTable(budget, buffer_for_budget(budget))
    check(table.buffer_length == 16 * (budget // 16), "budget slack was represented as a slot")
    check(table.slots == budget // 16, "slot count is not floor(C/16)")


def check_arm_b_full_capacity(order: int, target: int) -> None:
    group = OracleSecretGroup(order)
    result = solve_arm_b(group, 1, target, order, 4096, buffer_for_budget(4096))
    check(result.m == order, "Arm B must use M=N when E>N")
    check(result.termination == "SOLVED" and result.solution == target, "full-capacity Arm B solve failed")
    check(result.operations.total_group_operations == expected_bsgs_cost(order, target), "full-capacity Arm B count mismatch")
    check(len(group.calls) == result.operations.total_group_operations, "full-capacity call log mismatch")


def check_unbounded(order: int, target: int) -> None:
    group = OracleSecretGroup(order)
    from math import isqrt
    m_int = isqrt(order - 1) + 1
    slots = (10 * m_int + 6) // 7
    result = solve_unbounded(group, 1, target, order, bytearray(16 * slots))
    check(result.termination == "SOLVED" and result.solution == target, "unbounded public solve failed")
    expected = expected_bsgs_cost(m_int, target)
    check(result.operations.total_group_operations == expected, "unbounded formula count mismatch")
    check(len(group.calls) == expected, "call log disagrees with charged operations")
    check(result.operations.baby == m_int - 1, "baby construction charged an unused update")
    check(result.operations.total_group_operations == result.operations.baby + result.operations.scalar_precompute + result.operations.giant + result.operations.certificate, "component sum mismatch")


def check_arm_b(order: int, target: int) -> None:
    budget = 80  # S=5, E=3: explicitly below sqrt(N) for most fixed vectors.
    group = OracleSecretGroup(order)
    result = solve_arm_b(group, 1, target, order, budget, buffer_for_budget(budget))
    m = min(3, order)
    check(result.m == m, "Arm B did not use min(E,N)")
    check(result.termination == "SOLVED" and result.solution == target, "Arm B public solve failed")
    expected = expected_bsgs_cost(m, target)
    check(result.operations.total_group_operations == expected, "Arm B formula count mismatch")
    check(len(group.calls) == expected, "Arm B call log mismatch")


def check_scalar(scalar: int) -> None:
    group_impl = FixedCyclicGroup(101)
    group = CountingGroup(group_impl)
    point = left_to_right_scalar(group, scalar, 1, "certificate")
    check(point == scalar % 101, "left-to-right scalar result mismatch")
    check(group.total_group_operations == scalar_cost(scalar), "scalar formula mismatch")
    check(len(group_impl.calls) == scalar_cost(scalar), "scalar call log mismatch")


def check_arm_a_refusal() -> None:
    group = OracleSecretGroup(101)
    result = solve_arm_a(group, 1, 37, 101, 8, bytearray())
    check(result.termination == "CAPACITY_REFUSAL", "Arm A failed to refuse zero capacity")
    check(result.operations.total_group_operations == 0 and not group.calls, "Arm A did work before refusal")


def check_arm_b_m_greater_half() -> None:
    group = OracleSecretGroup(7)
    result = solve_arm_b(group, 1, 6, 7, 4096, buffer_for_budget(4096))
    check(result.m == 7 and result.m > 7 // 2, "Arm B did not exercise M>N/2")
    check(result.termination == "SOLVED" and result.solution == 6, "M>N/2 solve failed")


def check_last_giant_block() -> None:
    group = OracleSecretGroup(101)
    result = solve_arm_b(group, 1, 100, 101, 48, buffer_for_budget(48))
    check(result.m == 2, "last-block fixture capacity mismatch")
    check(result.termination == "SOLVED" and result.solution == 100, "last giant block not covered")
    check(result.operations.giant == 50, "extra or missing giant addition at final block")


def check_bad_certificate() -> None:
    # Q=25 is not in the baby range 0..3, but its fixed table encoding aliases 0.
    group = OracleSecretGroup(101, misencode={25: 0})
    result = solve_arm_b(group, 1, 25, 101, 112, buffer_for_budget(112))
    check(result.termination == "COMPLETED_INVALID" and result.solution is None, "false hit was not invalidated")
    check(result.operations.giant == 0, "false hit continued after invalid certificate")


def check_negative_scalar_rejected() -> None:
    group = CountingGroup(FixedCyclicGroup(101))
    expect_raises(SolverInputError, lambda: left_to_right_scalar(group, -1, 1, "certificate"))
    check(group.total_group_operations == 0, "negative scalar performed an operation")


def check_table_cancellation(event: str) -> None:
    table = FixedPhysicalTable(256, buffer_for_budget(256))
    before = table.buffer_sha256()
    result = table.insert(fixed_point(1), 1, hook=lambda name, _state: False if name == event else True)
    check(result.status == "CANCELLED", f"table did not cancel at {event}")
    check(table.buffer_sha256() == before, "cancelled table operation wrote buffer")


def check_bsgs_cancellation(event: str) -> None:
    group = OracleSecretGroup(101)
    result = solve_arm_b(group, 1, 37, 101, 112, buffer_for_budget(112), hook=lambda name, _state: False if name == event else True)
    check(result.termination == "CANCELLED", f"BSGS did not cancel at {event}")
    check(result.operations.total_group_operations == result.operations.baby + result.operations.scalar_precompute + result.operations.giant + result.operations.certificate, "cancelled component sum mismatch")


def derivative_span(source: str) -> tuple[int, int, str]:
    start = source.index("    def _count_mul(")
    end = source.index("\n\n    # Precompute", start)
    return start, end, source[start:end]


def expected_derivative_span() -> str:
    body = """def _count_mul(k_val: int, pt: Point) -> Point:
    nonlocal total_ops
    if k_val < 0:
        raise ValueError(\"nonnegative scalar required\")
    if k_val == 0:
        return None
    result_pt = pt
    for digit in bin(k_val)[3:]:
        result_pt = E.add(result_pt, result_pt)
        total_ops += 1
        if digit == \"1\":
            result_pt = E.add(result_pt, pt)
            total_ops += 1
    return result_pt"""
    return "\n".join("    " + line for line in body.splitlines())


def check_derivative_only_span() -> None:
    base = BASE_RHO.read_text(encoding="utf-8")
    derivative = DERIVATIVE_RHO.read_text(encoding="utf-8")
    b_start, b_end, _ = derivative_span(base)
    d_start, d_end, d_span = derivative_span(derivative)
    check(b_start == d_start, "derivative prefix boundary moved")
    check(d_span == expected_derivative_span(), "derivative scalar span differs from approved replacement")
    check(base[:b_start] == derivative[:d_start], "bytes before scalar span changed")
    check(base[b_end:] == derivative[d_end:], "bytes after scalar span changed")
    check(derivative == base[:b_start] + d_span + base[b_end:], "derivative has a second byte change")


def check_derivative_parse_compile() -> None:
    source = DERIVATIVE_RHO.read_text(encoding="utf-8")
    ast.parse(source, filename=str(DERIVATIVE_RHO))
    compile(source, str(DERIVATIVE_RHO), "exec")


def scalar_wrapper() -> Callable[[ScalarAdd, int, int], tuple[int | None, int]]:
    source = DERIVATIVE_RHO.read_text(encoding="utf-8")
    _, _, span = derivative_span(source)
    nested = "\n".join("    " + line for line in span.splitlines())
    wrapper_source = "def exercise(E, k, pt):\n    total_ops = 0\n" + nested + "\n    return _count_mul(k, pt), total_ops\n"
    namespace: dict[str, object] = {"Point": object}
    exec(compile(wrapper_source, "<rho-count-mul-exercise>", "exec"), namespace)
    return namespace["exercise"]  # type: ignore[return-value]


def check_derivative_scalar_zero() -> None:
    add = ScalarAdd(101)
    point, count = scalar_wrapper()(add, 0, 1)
    check(point is None and count == 0 and not add.calls, "rho zero scalar branch charged work")


def check_derivative_scalar_positive() -> None:
    add = ScalarAdd(101)
    point, count = scalar_wrapper()(add, 37, 1)
    check(point == 37 and count == scalar_cost(37), "rho positive scalar body is not left-to-right")
    check(len(add.calls) == scalar_cost(37), "rho scalar E.add call accounting mismatch")


def check_derivative_scalar_negative() -> None:
    add = ScalarAdd(101)
    expect_raises(ValueError, lambda: scalar_wrapper()(add, -1, 1))
    check(not add.calls, "rho negative scalar performed an addition")


def check_derivative_loader_context() -> None:
    spec = importlib.util.spec_from_file_location("harness.rho_corrected_task_3b05bc", DERIVATIVE_RHO)
    check(spec is not None and spec.loader is not None, "package-context loader unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        check(hasattr(module, "solve"), "derivative module did not load in harness package context")
    finally:
        sys.modules.pop(spec.name, None)


def check_binding(path_name: str) -> None:
    bindings = json.loads(BINDINGS.read_text(encoding="utf-8"))
    entry = bindings["bound_files"][path_name]
    actual = sha256((REPO / path_name).read_bytes()).hexdigest()
    check(actual == entry["sha256"], f"source binding mismatch for {path_name}")


def check_physical_manual(index: int) -> None:
    exponent = (index * 17) % (UINT28 - 1)
    state = INFINITY if index % 3 == 0 else AFFINE
    record = PhysicalSlot(state, 0 if state == INFINITY else index + 1, 0 if state == INFINITY else index + 2, exponent)
    check(decode_physical_slot(encode_physical_slot(record)) == record, "manual physical slot mismatch")


def check_hash_domain(point: LogicalPoint) -> None:
    preimage = encode_hash_preimage(point)
    frozen_digest = sha256(b"EXP-ECDLP-709063|table|v2" + preimage).digest()
    check(len(frozen_digest) == 32 and frozen_digest != sha256(preimage).digest(), "hash domain separation missing")


def check_invalid_logical(raw: bytes) -> None:
    expect_raises(TableValidationError, lambda: decode_logical_point(raw))


def check_invalid_hash(raw: bytes) -> None:
    expect_raises(TableValidationError, lambda: decode_hash_preimage(raw))


def check_invalid_physical(raw: bytes) -> None:
    expect_raises(TableValidationError, lambda: decode_physical_slot(raw))


def build_cases() -> list[Case]:
    cases: list[Case] = []
    add = lambda name, action: cases.append(Case(name, action))

    for index, point in enumerate(POINTS):
        add(f"logical-roundtrip-{index}", lambda point=point: check_logical_roundtrip(point))
        add(f"hash-roundtrip-{index}", lambda point=point: check_hash_roundtrip(point))
        add(f"physical-roundtrip-{index}", lambda point=point, index=index: check_physical_roundtrip(point, index))

    invalid_logical = (b"", b"\x00" * 8, b"\x02" + b"\x00" * 8, b"\x00\x01" + b"\x00" * 7, b"\x01" + UINT28.to_bytes(4, "little") + b"\x00" * 4, b"\x01" + b"\x00" * 4 + UINT28.to_bytes(4, "little"), b"\x00" + b"\x00" * 3 + b"\x01" + b"\x00" * 4, b"\x01" * 10)
    invalid_hash = (b"", b"\x04", b"\x00\x00", b"\x05" + b"\x00" * 8, b"\x04" + b"\x00" * 7, b"\x04" + UINT28.to_bytes(4, "big") + b"\x00" * 4, b"\x04" + b"\x00" * 4 + UINT28.to_bytes(4, "big"), b"\x00" * 9)
    invalid_physical = (b"", b"\x00" * 15, b"\x00" * 17, (1).to_bytes(4, "little") + b"\x00" * 12, b"\x00" * 12 + (3).to_bytes(4, "little"), (1).to_bytes(4, "little") + b"\x00" * 8 + (2).to_bytes(4, "little"), UINT28.to_bytes(4, "little") + b"\x00" * 8 + (1).to_bytes(4, "little"), b"\x00" * 4 + UINT28.to_bytes(4, "little") + b"\x00" * 4 + (1).to_bytes(4, "little"), b"\x00" * 8 + UINT28.to_bytes(4, "little") + (2).to_bytes(4, "little"), b"\x00" * 12 + (0xFFFFFFFF).to_bytes(4, "little"))
    for index, raw in enumerate(invalid_logical):
        add(f"invalid-logical-{index}", lambda raw=raw: check_invalid_logical(raw))
    for index, raw in enumerate(invalid_hash):
        add(f"invalid-hash-{index}", lambda raw=raw: check_invalid_hash(raw))
    for index, raw in enumerate(invalid_physical):
        add(f"invalid-physical-{index}", lambda raw=raw: check_invalid_physical(raw))

    invalid_type_actions = (
        lambda: LogicalPoint.affine(True, 0),
        lambda: LogicalPoint.affine(0, False),
        lambda: PhysicalSlot(AFFINE, True, 0, 0),
        lambda: PhysicalSlot(AFFINE, 0, False, 0),
        lambda: PhysicalSlot(AFFINE, 0, 0, True),
        lambda: FixedPhysicalTable(True, bytearray()),
        lambda: FixedPhysicalTable(16, bytes(16)),
        lambda: FixedPhysicalTable(16, bytearray(15)),
    )
    for index, action in enumerate(invalid_type_actions):
        add(f"invalid-type-or-buffer-{index}", lambda action=action: expect_raises(TableValidationError, action))

    for budget, slots, capacity in EXACT_CAPACITIES:
        add(f"exact-capacity-{budget}", lambda budget=budget, slots=slots, capacity=capacity: check_exact_capacity(budget, slots, capacity))
    for budget, _slots, capacity in EXACT_CAPACITIES[1:]:
        add(f"e-plus-one-retained-{budget}", lambda budget=budget, capacity=capacity: check_e_plus_one(budget, capacity))
        add(f"duplicate-conflict-{budget}", lambda budget=budget: check_duplicate_and_conflict(budget))
    for budget in (64, 80, 112):
        add(f"forced-linear-collision-{budget}", lambda budget=budget: check_forced_collision(budget))
    for index in range(24):
        add(f"retained-and-absent-lookup-{index}", lambda index=index: check_table_lookup(index))

    for order, target in VECTORS:
        add(f"unbounded-public-{order}-{target}", lambda order=order, target=target: check_unbounded(order, target))
    for order, target in VECTORS:
        add(f"arm-b-public-{order}-{target}", lambda order=order, target=target: check_arm_b(order, target))
    for scalar in SCALARS:
        add(f"left-to-right-scalar-{scalar}", lambda scalar=scalar: check_scalar(scalar))

    edge_actions: tuple[tuple[str, Callable[[], None]], ...] = (
        ("arm-a-refusal", check_arm_a_refusal),
        ("arm-b-m-greater-half", check_arm_b_m_greater_half),
        ("last-giant-block", check_last_giant_block),
        ("bad-certificate-stops", check_bad_certificate),
        ("negative-scalar-rejected", check_negative_scalar_rejected),
        ("logical-o-not-empty", lambda: check(encode_logical_point(LogicalPoint.infinity()) != encode_physical_slot(PhysicalSlot.empty()), "logical O equals physical empty")),
        ("hash-o-not-empty", lambda: check(encode_hash_preimage(LogicalPoint.infinity()) != encode_physical_slot(PhysicalSlot.empty()), "hash O equals physical empty")),
        ("physical-o-not-empty", lambda: check(encode_physical_slot(PhysicalSlot(INFINITY, 0, 0, 0)) != encode_physical_slot(PhysicalSlot.empty()), "physical O equals empty")),
        ("zero-slot-insert-refusal", lambda: check(FixedPhysicalTable(8, bytearray()).insert(LogicalPoint.infinity(), 0).status == "TABLE_FULL", "zero slot insert did not refuse")),
        ("zero-slot-no-table-bytes", lambda: check(FixedPhysicalTable(8, bytearray()).buffer_length == 0, "C=8 allocated physical table bytes")),
        ("no-partial-slot-buffer", lambda: expect_raises(TableValidationError, lambda: FixedPhysicalTable(31, bytearray(31)))),
        ("nonzero-new-buffer-refused", lambda: expect_raises(TableValidationError, lambda: FixedPhysicalTable(16, bytearray(b"\x01" + b"\x00" * 15)))),
    )
    for name, action in edge_actions:
        add(name, action)

    for event in ("table_hash", "table_probe", "table_write"):
        add(f"table-hook-{event}", lambda event=event: check_table_cancellation(event))
    for event in ("baby_step", "baby", "scalar_bit", "scalar_precompute", "giant_lookup", "giant", "negation"):
        add(f"bsgs-hook-{event}", lambda event=event: check_bsgs_cancellation(event))

    derivative_actions: tuple[tuple[str, Callable[[], None]], ...] = (
        ("rho-derivative-only-span", check_derivative_only_span),
        ("rho-derivative-parse-compile", check_derivative_parse_compile),
        ("rho-derivative-scalar-zero", check_derivative_scalar_zero),
        ("rho-derivative-scalar-positive", check_derivative_scalar_positive),
        ("rho-derivative-scalar-negative", check_derivative_scalar_negative),
        ("rho-derivative-package-loader", check_derivative_loader_context),
    )
    for name, action in derivative_actions:
        add(name, action)

    for source_path in ("harness/rho.py", "harness/toycurve.py", "harness/walk.py"):
        add(f"source-binding-{source_path}", lambda source_path=source_path: check_binding(source_path))
    for index in range(12):
        add(f"manual-physical-slot-{index}", lambda index=index: check_physical_manual(index))
    for point in POINTS[:8]:
        add(f"hash-domain-{point.tag}-{point.x}-{point.y}", lambda point=point: check_hash_domain(point))
    for order, target in SECOND_VECTORS:
        add(f"unbounded-second-vector-{order}-{target}", lambda order=order, target=target: check_unbounded(order, target))
    for order, target in SECOND_VECTORS:
        add(f"arm-b-second-vector-{order}-{target}", lambda order=order, target=target: check_arm_b(order, target))

    for index, point in enumerate(POINTS):
        add(f"single-fixed-point-insert-{index}", lambda point=point: check_single_insert(point))
    for budget in (0, 1, 7, 8, 15, 16, 17, 31):
        add(f"budget-slack-{budget}", lambda budget=budget: check_budget_slack(budget))
    for order, target in VECTORS[:6]:
        add(f"arm-b-full-capacity-{order}-{target}", lambda order=order, target=target: check_arm_b_full_capacity(order, target))

    # The next explicit controls leave the final reserved suite at exactly 320 cases.
    parser_actions: tuple[tuple[str, Callable[[], None]], ...] = (
        ("table-source-parse", lambda: compile((HERE / "table.py").read_text(encoding="utf-8"), str(HERE / "table.py"), "exec")),
        ("bsgs-source-parse", lambda: compile((HERE / "bsgs.py").read_text(encoding="utf-8"), str(HERE / "bsgs.py"), "exec")),
        ("tests-source-parse", lambda: compile(HERE.read_text(encoding="utf-8") if False else Path(__file__).read_text(encoding="utf-8"), str(Path(__file__)), "exec")),
        ("slot-size-constant", lambda: check(len(encode_physical_slot(PhysicalSlot.empty())) == 16, "slot size drifted")),
        ("logical-size-constant", lambda: check(len(encode_logical_point(LogicalPoint.infinity())) == 9, "logical size drifted")),
        ("affine-hash-size-constant", lambda: check(len(encode_hash_preimage(LogicalPoint.affine(1, 2))) == 9, "hash size drifted")),
        ("o-hash-size-constant", lambda: check(len(encode_hash_preimage(LogicalPoint.infinity())) == 1, "O hash size drifted")),
        ("table-counter-typed", lambda: check(all(type(value) is int for value in FixedPhysicalTable(16, buffer_for_budget(16)).counters().__dict__.values()), "table counters are not integer typed")),
    )
    for name, action in parser_actions:
        add(name, action)

    check(len(cases) == 320, f"frozen final suite must contain 320 cases, got {len(cases)}")
    return cases


def run_worker(result_path: Path) -> int:
    cases = build_cases()
    started = time.time()
    mono_started = time.monotonic_ns()
    records: list[dict[str, object]] = []
    failures = 0
    for ordinal, case in enumerate(cases, start=1):
        before_cpu = time.process_time_ns()
        before_wall = time.monotonic_ns()
        status = "passed"
        detail = ""
        try:
            case.action()
        except BaseException as exc:  # retain all terminal failures and continue the reserved suite
            status = "failed"
            detail = f"{type(exc).__name__}: {exc}"
            failures += 1
        after_wall = time.monotonic_ns()
        after_cpu = time.process_time_ns()
        wall_seconds = (after_wall - before_wall) / 1_000_000_000
        if wall_seconds > 10 and status == "passed":
            status = "failed"
            detail = "resource_exhaustion: fixed per-case wall limit exceeded"
            failures += 1
        usage = resource.getrusage(resource.RUSAGE_SELF)
        records.append({
            "ordinal": ordinal,
            "name": case.name,
            "status": status,
            "detail": detail,
            "started_utc": utc_now(started + (before_wall - mono_started) / 1_000_000_000),
            "wall_seconds": wall_seconds,
            "cpu_seconds": (after_cpu - before_cpu) / 1_000_000_000,
            "rss_raw": usage.ru_maxrss,
        })
    finished = time.time()
    payload = {
        "schema": "crypto.autoresearch.fixed_source_worker.v1",
        "reserved_case_count": 320,
        "executed_case_count": len(records),
        "passed": len(records) - failures,
        "failed": failures,
        "started_utc": utc_now(started),
        "finished_utc": utc_now(finished),
        "wall_seconds": finished - started,
        "cpu_seconds": time.process_time(),
        "peak_rss_raw": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "rss_unit": "bytes" if platform.system() == "Darwin" else "kilobytes",
        "cases": records,
        "limits": {
            "per_case_wall_seconds": 10,
            "maximum_case_wall_seconds": max(record["wall_seconds"] for record in records),
            "aggregate_wall_or_cpu_seconds": 1800,
        },
    }
    result_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"reserved": 320, "executed": len(records), "failed": failures}, sort_keys=True))
    return 0 if failures == 0 else 1


def utc_now(epoch: float | None = None) -> str:
    stamp = time.gmtime(time.time() if epoch is None else epoch)
    return time.strftime("%Y-%m-%dT%H:%M:%S", stamp) + f".{int(((time.time() if epoch is None else epoch) % 1) * 1_000_000):06d}Z"


def run_final(receipt_path: Path) -> int:
    cases = build_cases()
    reservation = [{"ordinal": ordinal, "name": case.name} for ordinal, case in enumerate(cases, start=1)]
    with tempfile.TemporaryDirectory(prefix="task-20260908-3b05bc-") as temporary:
        temp = Path(temporary)
        worker_result = temp / "worker-result.json"
        stdout_path = temp / "worker.stdout.log"
        stderr_path = temp / "worker.stderr.log"
        command = [sys.executable, str(Path(__file__).resolve()), "--worker", str(worker_result)]
        started_epoch = time.time()
        started_monotonic = time.monotonic_ns()
        child_usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
        with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
            # Redirection is established before Popen creates the worker process.
            process = subprocess.Popen(command, stdout=stdout_handle, stderr=stderr_handle, cwd=str(HERE))
            worker_pid = process.pid
            poll_count = 0
            while process.poll() is None:
                poll_count += 1
                time.sleep(0.005)
            exit_code = process.wait()
        child_usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        finished_epoch = time.time()
        worker_payload = json.loads(worker_result.read_text(encoding="utf-8")) if worker_result.exists() else None
        child_cpu_seconds = (child_usage_after.ru_utime - child_usage_before.ru_utime) + (child_usage_after.ru_stime - child_usage_before.ru_stime)
        aggregate_within_limit = (finished_epoch - started_epoch) <= 1800 and child_cpu_seconds <= 1800
        source_files = ["table.py", "bsgs.py", "rho-corrected.py", "tests.py", "solver-source-bindings.json", "implementation-report.yaml", "README.md"]
        receipt = {
            "schema": "crypto.autoresearch.fixed_source_check_receipt.v1",
            "task_id": "TASK-20260908-3b05bc",
            "experiment_id": "EXP-ECDLP-709063",
            "kind": "fixed_synthetic_source_conformance_only",
            "scientific_runs": 0,
            "case_reservation": {"reserved_before_launch": True, "count": 320, "cases": reservation},
            "command": command,
            "cwd": str(HERE),
            "started_utc": utc_now(started_epoch),
            "finished_utc": utc_now(finished_epoch),
            "exit_code": exit_code,
            "process_handling": {"worker_pid": worker_pid, "stdout_redirected_before_launch": True, "stderr_redirected_before_launch": True, "full_popen_handle_retained": True, "poll_count_before_terminal": poll_count, "terminal_observed": process.returncode is not None},
            "stdout": stdout_path.read_text(encoding="utf-8", errors="replace"),
            "stderr": stderr_path.read_text(encoding="utf-8", errors="replace"),
            "worker": worker_payload,
            "actual_telemetry": {
                "parent_wall_seconds": finished_epoch - started_epoch,
                "children_user_cpu_seconds": child_usage_after.ru_utime - child_usage_before.ru_utime,
                "children_system_cpu_seconds": child_usage_after.ru_stime - child_usage_before.ru_stime,
                "children_total_cpu_seconds": child_cpu_seconds,
                "children_peak_rss_raw": child_usage_after.ru_maxrss,
                "rss_unit": "bytes" if platform.system() == "Darwin" else "kilobytes",
                "maximum_workers_used": 1,
                "per_case_timeout_seconds": 10,
                "aggregate_executed_check_wall_or_cpu_limit_seconds": 1800,
                "machine_memory_limit_gib": 2,
                "hard_limit_setup": "not attempted; observed RSS is diagnostic only and asserts no hard guard enforcement",
                "aggregate_wall_and_cpu_within_limit": aggregate_within_limit,
            },
            "source_sha256": {name: sha256((HERE / name).read_bytes()).hexdigest() for name in source_files if (HERE / name).is_file()},
            "receipt_self_hash": None,
            "receipt_self_hash_note": "intentionally omitted to avoid self-reference",
            "limitations": ["No scientific runner, curve instance, rho solve, manifest, RUN allocation, performance result, or Linux guard was invoked."],
        }
        receipt_path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0 if exit_code == 0 and worker_payload is not None and worker_payload["failed"] == 0 and aggregate_within_limit else 1


def main(argv: list[str]) -> int:
    if len(argv) >= 3 and argv[1] == "--worker":
        return run_worker(Path(argv[2]))
    if len(argv) >= 3 and argv[1] == "--final":
        return run_final(Path(argv[2]))
    raise SystemExit(f"usage: {Path(argv[0]).name} --worker RESULT.json | --final RECEIPT.json")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
