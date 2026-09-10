"""Closed CM cost context and deterministic allocation projections.

Input context is data, not proof of the corresponding mathematical certificates
or the timing/authority of a selection freeze. The full runner must establish
those facts independently before scientific admission.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import zip_longest
from typing import Any, Iterator

from costs import CostContract, CostError, CostLedger, canonical_json, strict_json_loads, validate_raw_semantics

FIXTURES = ("I0F0", "I0F1", "I1F0", "I1F1", "I2F0", "I2F1")
INTERVALS = ("I0", "I1", "I2")
ENDPOINTS = ("K0", "K1", "K2", "K3")
CLASSES = ("C0", "C1")
COORDINATES = (1, 2, 3)
SEEDS = (606101, 606103)
QS = (1, 16, 256, 4096)
VIEWS = ("scalar", "transport", "selection_score_candidate", "actual_only_scaffolding")


def require_keys(value: Any, keys: set[str], code: str) -> None:
    if type(value) is not dict or set(value) != keys:
        raise CostError(code)


def integer_in(value: Any, values: Any, code: str) -> None:
    if type(value) is not int or value not in values:
        raise CostError(code)


def target(fixture: str, endpoint: str, coordinate: int) -> dict[str, Any]:
    if fixture not in FIXTURES or endpoint not in ENDPOINTS:
        raise CostError("invalid_endpoint_target")
    integer_in(coordinate, COORDINATES, "invalid_target_coordinate")
    return {"kind": "endpoint_coordinate", "fixture": fixture, "endpoint": endpoint, "coordinate": coordinate}


def target_order(value: dict[str, Any]) -> tuple[int, int, int]:
    return (FIXTURES.index(value["fixture"]), ENDPOINTS.index(value["endpoint"]), value["coordinate"])


class AllocationContext:
    """A detached partial or complete context with fixed identities.

    Candidate ordinals retain explicitly supplied origins for each interval.
    They may be offsets in a global counter; they are never list indices.
    A context may omit an unresolved fixture's complete class partition and may
    omit selection winners not yet frozen. Missing data never changes split
    denominators or manufactures an endpoint.
    """

    def __init__(self, original: Any) -> None:
        data = strict_json_loads(canonical_json(original))
        require_keys(data, {"record_type", "candidate_origins", "candidate_trace", "class_memberships", "frozen_winners"}, "context_fields")
        if data["record_type"] != "cm_cost_context" or type(data["candidate_trace"]) is not list:
            raise CostError("context_type")
        self._raw = data
        require_keys(data["candidate_origins"], set(INTERVALS), "candidate_origin_fields")
        self._origins = data["candidate_origins"]
        for interval, origin in self._origins.items():
            if origin is not None and (type(origin) is not int or origin < 0):
                raise CostError("candidate_origin_domain", (interval,))
        self._traces: dict[str, list[dict[str, Any]]] = {key: [] for key in INTERVALS}
        self._candidate_rows: dict[tuple[str, int], dict[str, Any]] = {}
        self._accepted: dict[str, tuple[int, ...]] = {}
        for row in data["candidate_trace"]:
            require_keys(row, {"interval", "event_ordinal", "outcome"}, "candidate_trace_fields")
            interval = row["interval"]
            if interval not in INTERVALS or row["outcome"] not in ("accepted", "rejected", "unavailable"):
                raise CostError("candidate_trace_domain")
            origin = self._origins[interval]
            if origin is None:
                raise CostError("candidate_trace_without_declared_origin", (interval,))
            expected_ordinal = origin + len(self._traces[interval])
            integer_in(row["event_ordinal"], (expected_ordinal,), "candidate_prefix_missing_or_duplicate")
            self._traces[interval].append(row)
            self._candidate_rows[(interval, row["event_ordinal"])] = row
        for interval, rows in self._traces.items():
            if any(row["outcome"] == "unavailable" for row in rows[:-1]):
                raise CostError("candidate_selection_continues_after_unavailable", (interval,))
            accepted = tuple(row["event_ordinal"] for row in rows if row["outcome"] == "accepted")
            if len(accepted) > 2 or (len(accepted) == 2 and rows[-1]["event_ordinal"] != accepted[1]):
                raise CostError("work_after_second_fixture_acceptance", (interval,))
            self._accepted[interval] = accepted
        if type(data["class_memberships"]) is not dict:
            raise CostError("class_context_requires_object")
        self._classes: dict[str, dict[str, tuple[str, str]]] = {}
        for fixture, classes in data["class_memberships"].items():
            if fixture not in FIXTURES:
                raise CostError("noncanonical_fixture_context")
            ordinal = int(fixture[-1])
            if len(self._accepted[fixture[:2]]) <= ordinal:
                raise CostError("class_context_without_accepted_fixture", (fixture,))
            require_keys(classes, set(CLASSES), "class_partition_requires_two_named_classes")
            flattened: list[str] = []
            normalized = {}
            for name in CLASSES:
                members = classes[name]
                if type(members) is not list or len(members) != 2 or any(type(e) is not str or e not in ENDPOINTS for e in members):
                    raise CostError("class_requires_two_endpoint_labels", (fixture, name))
                flattened.extend(members)
                normalized[name] = tuple(sorted(members, key=ENDPOINTS.index))
            if len(set(flattened)) != 4 or set(flattened) != set(ENDPOINTS):
                raise CostError("classes_do_not_partition_four_labels", (fixture,))
            self._classes[fixture] = normalized
        if type(data["frozen_winners"]) is not list:
            raise CostError("winner_context_requires_array")
        self._winners: dict[tuple[str, int], int] = {}
        for row in data["frozen_winners"]:
            require_keys(row, {"interval", "coordinate", "arm"}, "winner_fields")
            if row["interval"] not in INTERVALS:
                raise CostError("winner_interval")
            integer_in(row["coordinate"], COORDINATES, "winner_coordinate")
            integer_in(row["arm"], range(2, 8), "winner_arm")
            key = (row["interval"], row["coordinate"])
            if key in self._winners:
                raise CostError("duplicate_selection_winner")
            if not all(f"{row['interval']}F{i}" in self._classes for i in (0, 1)):
                raise CostError("winner_without_complete_stratum_context")
            self._winners[key] = row["arm"]

    @property
    def fixtures_complete(self) -> bool:
        return set(self._classes) == set(FIXTURES) and all(len(values) == 2 for values in self._accepted.values())

    @property
    def selection_complete(self) -> bool:
        return len(self._winners) == 9

    def as_json(self) -> dict[str, Any]:
        return strict_json_loads(canonical_json(self._raw))

    def winner(self, interval: str, coordinate: int) -> int | None:
        return self._winners.get((interval, coordinate))

    def class_labels(self, fixture: str, class_id: str) -> tuple[str, str] | None:
        if fixture not in FIXTURES or class_id not in CLASSES:
            raise CostError("class_target_domain")
        return self._classes.get(fixture, {}).get(class_id)

    def candidate_fixture(self, interval: str, ordinal: int) -> str | None:
        if type(interval) is not str or type(ordinal) is not int or (interval, ordinal) not in self._candidate_rows:
            raise CostError("missing_candidate_join", (interval, ordinal))
        accepted = self._accepted[interval]
        if accepted and ordinal <= accepted[0]:
            return interval + "F0"
        if len(accepted) == 2 and ordinal <= accepted[1]:
            return interval + "F1"
        return None

    def fixture_targets(self, fixture: str) -> tuple[dict[str, Any], ...] | None:
        if fixture not in FIXTURES:
            raise CostError("fixture_target_domain")
        if fixture not in self._classes:
            return None
        return tuple(target(fixture, endpoint, coordinate) for endpoint in ENDPOINTS for coordinate in COORDINATES)

    def eligible_targets(self, row: dict[str, Any]) -> tuple[dict[str, Any], ...] | None:
        scope = row["scope"]
        if scope == "global":
            if not self.fixtures_complete:
                return None
            return tuple(t for fixture in FIXTURES for t in self.fixture_targets(fixture))
        if scope == "selection_stratum":
            fixtures = (row["interval"] + "F0", row["interval"] + "F1")
            if any(fixture not in self._classes for fixture in fixtures):
                return None
            return tuple(target(fixture, endpoint, row["coordinate"]) for fixture in fixtures for endpoint in ENDPOINTS)
        if scope == "interval":
            fixture = self.candidate_fixture(row["interval"], row["event_ordinal"])
            return None if fixture is None else self.fixture_targets(fixture)
        fixture = row.get("fixture")
        if scope == "fixture":
            return self.fixture_targets(fixture)
        if scope in ("kernel", "class", "endpoint_coordinate", "arm_workload", "timing_block", "block_repetition"):
            if fixture not in self._classes:
                return None
            if scope == "kernel":
                return tuple(target(fixture, row["kernel"], coordinate) for coordinate in COORDINATES)
            if scope == "class":
                labels = self.class_labels(fixture, row["class"])
                return tuple(target(fixture, endpoint, coordinate) for endpoint in labels for coordinate in COORDINATES)
            return (target(fixture, row["endpoint"], row["coordinate"]),)
        raise CostError("scope_has_no_endpoint_allocation", (scope,))


@dataclass(frozen=True)
class EdgeGroup:
    view: str
    scenario: dict[str, Any]
    targets: tuple[dict[str, Any], ...]
    reason: str


def _cold() -> Iterator[dict[str, Any]]:
    for q in QS:
        for seed in SEEDS:
            yield {"kind": "cold", "q": q, "seed": seed}


def _actual_only(row: dict[str, Any]) -> tuple[EdgeGroup, ...]:
    return (EdgeGroup("actual_only_scaffolding", {"kind": "actual_only"},
                      ({"kind": "physical_owner", "raw_cost_row_id": row["raw_cost_row_id"]},), "actual_only"),)


def expected_groups(contract: CostContract, row: dict[str, Any], context: AllocationContext) -> tuple[tuple[EdgeGroup, ...], tuple[str, ...]]:
    """Generate the exhaustive group set from a previously validated raw row."""
    if row["charge_kind"] == "derived_rollup":
        return (), ()
    family = contract.crosswalk[row["component"]]["family"]
    if family == "scaffolding":
        return _actual_only(row), ()
    if row["scope"] == "interval":
        context.candidate_fixture(row["interval"], row["event_ordinal"])
    missing = tuple(field for field in ("CPU_nanoseconds", "wall_nanoseconds") if row[field] is None)
    if missing:
        return _actual_only(row), tuple("unavailable_" + field for field in missing)
    targets = context.eligible_targets(row)
    if targets is None:
        return _actual_only(row), ("required_target_context_unavailable",)
    groups: list[EdgeGroup] = []
    if family == "shared":
        for view in ("scalar", "transport"):
            groups.extend(EdgeGroup(view, scenario, targets, "shared_setup") for scenario in _cold())
    elif family == "transport":
        groups.extend(EdgeGroup("transport", scenario, targets, "transport_setup") for scenario in _cold())
    elif family == "scalar":
        if row["component"] not in ("global_library_initialization", "baseline_selection_stratum_overhead"):
            raise CostError("non_leaf_scalar_component")
        groups.extend(EdgeGroup("scalar", scenario, targets, "selection_actual_spend") for scenario in _cold())
        if row["component"] == "global_library_initialization":
            groups.append(EdgeGroup("selection_score_candidate", {"kind": "selection_score", "candidate_arm": 7}, targets, "selection_score"))
    elif family == "arm_context":
        if row["plane"] == "selection":
            groups.extend(EdgeGroup("scalar", scenario, targets, "selection_actual_spend") for scenario in _cold())
            groups.append(EdgeGroup("selection_score_candidate", {"kind": "selection_score", "candidate_arm": row["arm"]}, targets, "selection_score"))
        else:
            if row["arm"] == 1:
                view = "transport"
            else:
                winner = context.winner(row["fixture"][:2], row["coordinate"])
                if winner is None:
                    return _actual_only(row), ("selection_winner_unavailable",)
                if row["arm"] != winner:
                    return _actual_only(row), ()
                view = "scalar"
            groups.append(EdgeGroup(view, {"kind": "cold", "q": row["q"], "seed": row["seed"]}, targets, "selected_main_work"))
    else:
        raise CostError("unknown_component_family")
    return tuple(groups), ()


def _split(value: int | None, count: int, index: int) -> int | None:
    return None if value is None else value // count + int(index < value % count)


def edges_from_groups(row: dict[str, Any], groups: tuple[EdgeGroup, ...]) -> Iterator[dict[str, Any]]:
    for group in groups:
        targets = group.targets if group.view == "actual_only_scaffolding" else tuple(sorted(group.targets, key=target_order))
        n = len(targets)
        if not n or len({canonical_json(t) for t in targets}) != n:
            raise CostError("empty_or_duplicate_expected_targets")
        for index, item in enumerate(targets):
            yield {
                "record_type": "allocation_edge", "raw_cost_row_id": row["raw_cost_row_id"],
                "weight": {"numerator": 1, "denominator": n},
                "allocated_CPU_nanoseconds": _split(row["CPU_nanoseconds"], n, index),
                "allocated_CPU_unavailable_reason": row["CPU_unavailable_reason"] if row["CPU_nanoseconds"] is None else None,
                "allocated_wall_nanoseconds": _split(row["wall_nanoseconds"], n, index),
                "allocated_wall_unavailable_reason": row["wall_unavailable_reason"] if row["wall_nanoseconds"] is None else None,
                "reason_code": group.reason, "strategy_view": group.view,
                "scenario": dict(group.scenario), "target": dict(item),
            }


def iter_expected_edges(ledger: CostLedger, context: AllocationContext) -> Iterator[dict[str, Any]]:
    for row in ledger.iter_rows():
        groups, _ = expected_groups(ledger.contract, row, context)
        yield from edges_from_groups(row, groups)


def iter_allocation_issues(ledger: CostLedger, context: AllocationContext) -> Iterator[dict[str, Any]]:
    for row in ledger.iter_rows():
        _, issues = expected_groups(ledger.contract, row, context)
        if issues:
            yield {"raw_cost_row_id": row["raw_cost_row_id"], "reasons": list(issues)}


def validate_allocation_edges(ledger: CostLedger, context: AllocationContext, actual: Iterator[dict[str, Any]]) -> dict[str, Any]:
    """Require the exact complete canonical stream, not merely supplied sums."""
    sentinel = object()
    count = 0
    for expected, supplied in zip_longest(iter_expected_edges(ledger, context), actual, fillvalue=sentinel):
        if expected is sentinel or supplied is sentinel:
            raise CostError("missing_or_extra_allocation_edge", (count,))
        checked = ledger.contract.validate_record_shape(supplied)
        if checked["record_type"] != "allocation_edge" or canonical_json(checked) != canonical_json(expected):
            raise CostError("allocation_edge_or_order_mismatch", (count,))
        count += 1
    issues = sum(1 for _ in iter_allocation_issues(ledger, context))
    return {"edges_checked": count, "exact_group_and_integer_reconciliation": True,
            "unresolved_row_count": issues, "fixture_context_complete": context.fixtures_complete,
            "selection_context_complete": context.selection_complete,
            "scientific_admission": False}


def iter_operation_allocations(ledger: CostLedger, context: AllocationContext) -> Iterator[dict[str, Any]]:
    """Derived operation-count view; never an extra physical charge or CSV row."""
    for row in ledger.iter_rows():
        groups, _ = expected_groups(ledger.contract, row, context)
        for group in groups:
            targets = group.targets if group.view == "actual_only_scaffolding" else tuple(sorted(group.targets, key=target_order))
            for index, item in enumerate(targets):
                counts = row["operation_counts"]
                yield {"raw_cost_row_id": row["raw_cost_row_id"], "strategy_view": group.view,
                       "scenario": dict(group.scenario), "target": dict(item),
                       "allocated_operation_counts": None if counts is None else {key: _split(value, len(targets), index) for key, value in counts.items()},
                       "unavailable_reason": row["operation_counts_unavailable_reason"] if counts is None else None,
                       "scope": "derived allocation of supplied observations"}
