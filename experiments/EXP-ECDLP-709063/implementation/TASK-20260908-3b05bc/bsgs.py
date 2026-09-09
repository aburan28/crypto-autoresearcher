"""Charged, fixed-buffer BSGS kernels for TASK-20260908-3b05bc.

These functions accept only public group data ``curve, P, Q, N`` plus the
caller-owned table buffer.  They neither accept nor inspect a known scalar.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isqrt
from typing import Any, Callable

from table import FixedPhysicalTable, LogicalPoint, ProgressCancelled, TableCounters


ProgressHook = Callable[[str, dict[str, int]], bool | None]


class SolverInputError(ValueError):
    """The caller did not supply a public finite-group BSGS input."""


@dataclass(frozen=True)
class OperationCounters:
    total_group_operations: int
    group_additions: int
    group_doublings: int
    negations: int
    baby: int
    scalar_precompute: int
    giant: int
    certificate: int


@dataclass(frozen=True)
class SolverResult:
    termination: str
    solution: int | None
    m: int
    slots: int
    capacity: int
    occupied: int
    operations: OperationCounters
    table: TableCounters
    reason: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "termination": self.termination,
            "solution": self.solution,
            "m": self.m,
            "slots": self.slots,
            "capacity": self.capacity,
            "occupied": self.occupied,
            "operations": asdict(self.operations),
            "table": asdict(self.table),
            "reason": self.reason,
        }


def _require_order(order: int) -> int:
    if type(order) is not int or order <= 0:
        raise SolverInputError("N must be a positive non-bool integer")
    return order


class CountingGroup:
    """A group-operation wrapper which charges every complete ``curve.add``."""

    def __init__(self, curve: Any, hook: ProgressHook | None = None) -> None:
        for attribute in ("add", "neg", "identity", "encode_point", "equals"):
            if not hasattr(curve, attribute):
                raise SolverInputError(f"complete group interface lacks {attribute}")
        self.curve = curve
        self.hook = hook
        self.total_group_operations = 0
        self.group_additions = 0
        self.group_doublings = 0
        self.negations = 0
        self.baby = 0
        self.scalar_precompute = 0
        self.giant = 0
        self.certificate = 0

    def _event(self, event: str) -> None:
        if self.hook is None:
            return
        state = asdict(self.snapshot())
        if self.hook(event, state) is False:
            raise ProgressCancelled(event)

    def add(self, left: Any, right: Any, component: str) -> Any:
        self._event(component)
        is_double = self.curve.equals(left, right)
        value = self.curve.add(left, right)
        self.total_group_operations += 1
        self.group_additions += 1
        if is_double:
            self.group_doublings += 1
        if component == "baby":
            self.baby += 1
        elif component == "scalar_precompute":
            self.scalar_precompute += 1
        elif component == "giant":
            self.giant += 1
        elif component == "certificate":
            self.certificate += 1
        else:
            raise SolverInputError(f"unknown charged component {component}")
        return value

    def neg(self, point: Any) -> Any:
        self._event("negation")
        self.negations += 1
        return self.curve.neg(point)

    def snapshot(self) -> OperationCounters:
        return OperationCounters(
            total_group_operations=self.total_group_operations,
            group_additions=self.group_additions,
            group_doublings=self.group_doublings,
            negations=self.negations,
            baby=self.baby,
            scalar_precompute=self.scalar_precompute,
            giant=self.giant,
            certificate=self.certificate,
        )


def left_to_right_scalar(group: CountingGroup, scalar: int, point: Any, component: str) -> Any:
    """The frozen left-to-right double-and-add convention.

    Zero returns the group identity without a call.  Negative scalars are a
    protocol-domain error rather than a request to negate and continue.
    """
    if type(scalar) is not int:
        raise SolverInputError("scalar must be a non-bool integer")
    if scalar < 0:
        raise SolverInputError("nonnegative scalar required")
    if scalar == 0:
        return group.curve.identity()
    result = point
    for digit in bin(scalar)[3:]:
        group._event("scalar_bit")
        result = group.add(result, result, component)
        if digit == "1":
            result = group.add(result, point, component)
    return result


def scalar_cost(scalar: int) -> int:
    """The independent closed-form count for the frozen scalar convention."""
    if type(scalar) is not int or scalar < 0:
        raise SolverInputError("scalar must be a nonnegative non-bool integer")
    if scalar == 0:
        return 0
    return scalar.bit_length() - 1 + scalar.bit_count() - 1


def _table_delta(before: TableCounters, after: TableCounters) -> TableCounters:
    return TableCounters(
        table_operations=after.table_operations - before.table_operations,
        hash_calls=after.hash_calls - before.hash_calls,
        hash_preimage_bytes=after.hash_preimage_bytes - before.hash_preimage_bytes,
        probes=after.probes - before.probes,
        bytes_read=after.bytes_read - before.bytes_read,
        bytes_written=after.bytes_written - before.bytes_written,
        occupied=after.occupied,
    )


def _result(
    termination: str,
    solution: int | None,
    table: FixedPhysicalTable,
    before: TableCounters,
    group: CountingGroup,
    m: int,
    reason: str = "",
) -> SolverResult:
    return SolverResult(
        termination=termination,
        solution=solution,
        m=m,
        slots=table.slots,
        capacity=table.capacity,
        occupied=table.occupied,
        operations=group.snapshot(),
        table=_table_delta(before, table.counters()),
        reason=reason,
    )


def _common_bsgs(
    curve: Any,
    P: Any,
    Q: Any,
    N: int,
    m: int,
    budget_bytes: int,
    table_buffer: bytearray,
    hook: ProgressHook | None,
) -> SolverResult:
    if type(m) is not int or m <= 0:
        raise SolverInputError("M must be a positive non-bool integer")
    table = FixedPhysicalTable(budget_bytes, table_buffer)
    before = table.counters()
    group = CountingGroup(curve, hook)
    try:
        baby = curve.identity()
        for j in range(m):
            if hook is not None and hook("baby_step", asdict(group.snapshot())) is False:
                raise ProgressCancelled("baby_step")
            inserted = table.insert(curve.encode_point(baby), j, hook=hook)
            if inserted.status == "CANCELLED":
                return _result("CANCELLED", None, table, before, group, m, "table hook")
            if inserted.status == "TABLE_FULL":
                return _result("INSTRUMENT_FAILURE", None, table, before, group, m, "early TABLE_FULL")
            if inserted.status == "COMPLETED_INVALID":
                return _result("COMPLETED_INVALID", None, table, before, group, m, "conflicting baby key")
            if j < m - 1:
                baby = group.add(baby, P, "baby")
        H = left_to_right_scalar(group, m, P, "scalar_precompute")
        G = Q
        blocks = (N + m - 1) // m
        for ell in range(blocks):
            if hook is not None and hook("giant_lookup", asdict(group.snapshot())) is False:
                raise ProgressCancelled("giant_lookup")
            found = table.lookup(curve.encode_point(G), hook=hook)
            if found.status == "CANCELLED":
                return _result("CANCELLED", None, table, before, group, m, "table hook")
            if found.status == "FOUND":
                candidate = (ell * m + int(found.exponent)) % N
                certificate = left_to_right_scalar(group, candidate, P, "certificate")
                if not curve.equals(certificate, Q):
                    return _result("COMPLETED_INVALID", None, table, before, group, m, "false table hit")
                return _result("SOLVED", candidate, table, before, group, m)
            if ell != blocks - 1:
                G = group.add(G, group.neg(H), "giant")
        return _result("NOT_FOUND", None, table, before, group, m, "complete public search exhausted")
    except ProgressCancelled as exc:
        return _result("CANCELLED", None, table, before, group, m, str(exc))


def solve_unbounded(
    curve: Any,
    P: Any,
    Q: Any,
    N: int,
    table_buffer: bytearray,
    hook: ProgressHook | None = None,
) -> SolverResult:
    """NULL 1: conventional BSGS using the same physical table representation."""
    _require_order(N)
    m = isqrt(N - 1) + 1
    slots = (10 * m + 6) // 7
    return _common_bsgs(curve, P, Q, N, m, 16 * slots, table_buffer, hook)


def solve_arm_a(
    curve: Any,
    P: Any,
    Q: Any,
    N: int,
    budget_bytes: int,
    table_buffer: bytearray,
    hook: ProgressHook | None = None,
) -> SolverResult:
    """Arm A: fixed-table feasibility cliff, refusing before H or solve work."""
    _require_order(N)
    probe = FixedPhysicalTable(budget_bytes, table_buffer)
    m = isqrt(N - 1) + 1
    if m > probe.capacity:
        empty = CountingGroup(curve, hook)
        return SolverResult(
            termination="CAPACITY_REFUSAL",
            solution=None,
            m=m,
            slots=probe.slots,
            capacity=probe.capacity,
            occupied=probe.occupied,
            operations=empty.snapshot(),
            table=TableCounters(0, 0, 0, 0, 0, 0, 0),
            reason="m exceeds fixed-table usable capacity",
        )
    return _common_bsgs(curve, P, Q, N, m, budget_bytes, table_buffer, hook)


def solve_arm_b(
    curve: Any,
    P: Any,
    Q: Any,
    N: int,
    budget_bytes: int,
    table_buffer: bytearray,
    hook: ProgressHook | None = None,
) -> SolverResult:
    """Arm B: memory-constrained BSGS with ``M=min(E,N)`` exactly."""
    _require_order(N)
    probe = FixedPhysicalTable(budget_bytes, table_buffer)
    if probe.capacity == 0:
        empty = CountingGroup(curve, hook)
        return SolverResult(
            termination="CAPACITY_REFUSAL",
            solution=None,
            m=0,
            slots=probe.slots,
            capacity=probe.capacity,
            occupied=probe.occupied,
            operations=empty.snapshot(),
            table=TableCounters(0, 0, 0, 0, 0, 0, 0),
            reason="positive Arm B requires positive usable capacity",
        )
    m = min(probe.capacity, N)
    return _common_bsgs(curve, P, Q, N, m, budget_bytes, table_buffer, hook)
