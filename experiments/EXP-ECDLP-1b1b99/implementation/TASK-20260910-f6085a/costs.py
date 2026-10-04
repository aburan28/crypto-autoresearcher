"""Pure, fail-closed CM physical-cost ledger primitives.

This module deliberately knows nothing about certificates, launch authority, a
runtime, or scientific success.  Its inputs are already captured cost metadata
and caller-supplied endpoint/class tables; it validates their *shape* only.
"""
from __future__ import annotations

import csv
import io
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable, Mapping, Sequence

FIXTURES = ("I0F0", "I0F1", "I1F0", "I1F1", "I2F0", "I2F1")
ENDPOINTS = ("K0", "K1", "K2", "K3")
COORDINATES = (1, 2, 3)
SEEDS = (606101, 606103)
QS = (1, 16, 256, 4096)
SCOPES = {"global", "interval", "fixture", "kernel", "class", "endpoint_coordinate", "selection_stratum", "arm_workload", "timing_block", "block_repetition", "scaffolding"}
RESOURCE_PAIRS = (("CPU_nanoseconds", "CPU_unavailable_reason"), ("wall_nanoseconds", "wall_unavailable_reason"), ("process_group_peak_RSS_bytes", "RSS_unavailable_reason"), ("operation_counts", "operation_counts_unavailable_reason"))
COMMON = {"record_type", "raw_cost_row_id", "physical_event_id", "event_ordinal", "component", "phase", "status", "CPU_nanoseconds", "CPU_unavailable_reason", "wall_nanoseconds", "wall_unavailable_reason", "process_group_peak_RSS_bytes", "RSS_unavailable_reason", "operation_counts", "operation_counts_unavailable_reason", "capture_interval", "charge_kind", "source_leaf_ids", "scope"}
INDEX_BY_SCOPE = {
    "global": (), "interval": ("interval",), "fixture": ("fixture",), "kernel": ("fixture", "kernel"),
    "class": ("fixture", "class"), "endpoint_coordinate": ("fixture", "endpoint", "coordinate"),
    "selection_stratum": ("interval", "coordinate"), "arm_workload": ("fixture", "endpoint", "coordinate", "plane", "seed", "q", "arm"),
    "timing_block": ("fixture", "endpoint", "coordinate", "plane", "seed", "q", "arm", "block"),
    "block_repetition": ("fixture", "endpoint", "coordinate", "plane", "seed", "q", "arm", "block", "repetition"),
}

class CostError(ValueError): pass

def _integer(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise CostError(f"{label} must be an integer >= {minimum}")
    return value

def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out: raise CostError(f"duplicate JSON key: {key}")
        out[key] = value
    return out

def strict_json_loads(data: str | bytes) -> Any:
    """Parse canonical JSON input, rejecting duplicate keys and every float token."""
    def bad_float(_: str) -> None: raise CostError("float token is forbidden")
    try: return json.loads(data, object_pairs_hook=_no_duplicates, parse_float=bad_float, parse_constant=bad_float)
    except (json.JSONDecodeError, TypeError) as exc: raise CostError(f"invalid JSON: {exc}") from exc

def canonical_json(value: Any) -> bytes:
    """Canonical UTF-8 JSON; callers get no silently coerced floats or booleans."""
    def check(v: Any) -> None:
        if isinstance(v, float): raise CostError("float values are forbidden")
        if isinstance(v, Mapping):
            for k, x in v.items():
                if not isinstance(k, str): raise CostError("JSON object key is not text")
                check(x)
        elif isinstance(v, (list, tuple)):
            for x in v: check(x)
    check(value)
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

def parse_cost_csv(data: str | bytes, required_columns: Sequence[str]) -> list[dict[str, str]]:
    """Strict CSV reader retaining lexical values; duplicate/unknown columns fail."""
    text = data.decode("utf-8") if isinstance(data, bytes) else data
    try: reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
    except csv.Error as exc: raise CostError(f"malformed CSV: {exc}") from exc
    if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)): raise CostError("missing or duplicate CSV header")
    if tuple(reader.fieldnames) != tuple(required_columns): raise CostError("CSV header is not the frozen canonical order")
    rows: list[dict[str, str]] = []
    try:
        for row in reader:
            if None in row or any(v is None for v in row.values()): raise CostError("short or long CSV row")
            rows.append(dict(row))
    except csv.Error as exc: raise CostError(f"malformed CSV row: {exc}") from exc
    return rows

def _validate_axes(row: Mapping[str, Any]) -> None:
    scope = row.get("scope")
    if scope not in SCOPES: raise CostError("unknown scope")
    if scope == "scaffolding":
        if set(row) - COMMON - {"scaffold_kind", "owner"}: raise CostError("unknown scaffolding field")
        if not isinstance(row.get("scaffold_kind"), str) or not isinstance(row.get("owner"), Mapping): raise CostError("invalid scaffolding owner")
        return
    needed = set(INDEX_BY_SCOPE[scope]); allowed = COMMON | needed
    if set(row) - allowed: raise CostError("unknown or forbidden index field")
    if not needed <= set(row): raise CostError("missing scope index")
    if "fixture" in row and row["fixture"] not in FIXTURES: raise CostError("noncanonical fixture")
    if "endpoint" in row and row["endpoint"] not in ENDPOINTS: raise CostError("noncanonical endpoint")
    if "coordinate" in row and (_integer(row["coordinate"], "coordinate", 1) not in COORDINATES): raise CostError("noncanonical coordinate")
    if "interval" in row and row["interval"] not in ("I0", "I1", "I2"): raise CostError("noncanonical interval")
    if "fixture" in row and row["fixture"][:2] != row.get("interval", row["fixture"][:2]): raise CostError("fixture/interval conflict")
    if "plane" in row:
        if row["plane"] not in ("main", "selection"): raise CostError("unknown scientific plane")
        if row["plane"] == "selection" and (row.get("seed"), row.get("q")) != (606101, 256): raise CostError("selection must use fixed seed/q")
    for name, domain in (("seed", SEEDS), ("q", QS), ("block", range(7))):
        if name in row and row[name] not in domain: raise CostError(f"invalid {name}")
    if "repetition" in row: _integer(row["repetition"], "repetition", 1)
    if "arm" in row:
        _integer(row["arm"], "arm", 1)
        if row.get("plane") == "selection" and row["arm"] not in range(2, 8): raise CostError("selection arm outside 2..7")

def validate_raw_rows(rows: Sequence[Mapping[str, Any]], *, component_phases: Mapping[str, Iterable[str]] | None = None) -> list[dict[str, Any]]:
    """Validate typed raw leaves/rollups and physical capture identity.

    A result is a deep JSON round-trip copy.  It does not verify a certificate
    or claim a supplied endpoint/class table is arithmetically genuine.
    """
    out = [strict_json_loads(canonical_json(dict(row))) for row in rows]
    row_ids: set[str] = set(); events: set[str] = set(); logical: set[tuple[Any, ...]] = set(); spans: dict[str, list[tuple[int, int]]] = {}
    for row in out:
        if set(row) < COMMON or row.get("record_type") != "raw_cost": raise CostError("raw row lacks common closed fields")
        _integer(row["event_ordinal"], "event_ordinal")
        if not isinstance(row["raw_cost_row_id"], str) or not row["raw_cost_row_id"] or row["raw_cost_row_id"] in row_ids: raise CostError("duplicate raw_cost_row_id")
        row_ids.add(row["raw_cost_row_id"])
        if not isinstance(row["physical_event_id"], str) or not row["physical_event_id"]: raise CostError("invalid physical_event_id")
        if row["status"] not in ("complete", "partial", "failed", "below_resolution"): raise CostError("bad status")
        if row["charge_kind"] not in ("exclusive_leaf", "derived_rollup"): raise CostError("bad charge_kind")
        if not isinstance(row["source_leaf_ids"], list): raise CostError("source_leaf_ids is not a list")
        if len(row["source_leaf_ids"]) != len(set(row["source_leaf_ids"])): raise CostError("duplicate rollup source")
        _validate_axes(row)
        if component_phases is not None and row["component"] not in component_phases: raise CostError("unregistered component")
        if component_phases is not None and row["phase"] not in set(component_phases[row["component"]]): raise CostError("component/phase crosswalk violation")
        for value_name, reason_name in RESOURCE_PAIRS:
            value, reason = row[value_name], row[reason_name]
            if value is None:
                if not isinstance(reason, str): raise CostError(f"{value_name} missing reason")
            else:
                if reason is not None: raise CostError(f"{value_name} has value and reason")
                if value_name == "operation_counts":
                    if not isinstance(value, Mapping) or not value: raise CostError("invalid operation_counts")
                    for key, count in value.items():
                        if not isinstance(key, str): raise CostError("bad operation counter")
                        _integer(count, "operation count")
                else: _integer(value, value_name)
        interval = row["capture_interval"]
        if not isinstance(interval, Mapping) or set(interval) != {"stream_id", "process_group_id", "cpu_started_ns", "cpu_finished_ns", "wall_started_ns", "wall_finished_ns", "reason"}: raise CostError("capture_interval is not closed")
        if row["charge_kind"] == "derived_rollup":
            if any(row[x] is not None for x, _ in RESOURCE_PAIRS[:3]) or not row["source_leaf_ids"]: raise CostError("rollup must be nonchargeable and name leaves")
        else:
            if row["physical_event_id"] in events: raise CostError("duplicate exclusive physical_event_id")
            events.add(row["physical_event_id"])
            if row["status"] in ("complete", "below_resolution") and any(row[x] is None for x, _ in RESOURCE_PAIRS[:3]): raise CostError("complete leaf has unavailable physical resource")
            a, b = interval["cpu_started_ns"], interval["cpu_finished_ns"]
            if a is not None or b is not None:
                _integer(a, "capture start"); _integer(b, "capture finish")
                if b < a: raise CostError("capture clock ordering")
                spans.setdefault(str(interval["stream_id"]), []).append((a, b))
        key = tuple(row.get(x) for x in ("scope", "fixture", "endpoint", "coordinate", "plane", "seed", "q", "arm", "block", "repetition", "component", "phase", "event_ordinal"))
        if key in logical: raise CostError("duplicate logical capture key")
        logical.add(key)
    for stream, values in spans.items():
        for (_, end), (start, _) in zip(sorted(values), sorted(values)[1:]):
            if start < end: raise CostError(f"chargeable capture spans overlap in {stream}")
    leaves = {r["raw_cost_row_id"] for r in out if r["charge_kind"] == "exclusive_leaf"}
    for row in out:
        if row["charge_kind"] == "derived_rollup" and (not set(row["source_leaf_ids"]) <= leaves): raise CostError("rollup refers to non-leaf")
    return out

def canonical_targets(prefixes: Mapping[str, Sequence[str]], class_memberships: Mapping[str, Sequence[str]]) -> tuple[dict[str, tuple[dict[str, Any], ...]], dict[str, tuple[str, ...]]]:
    """Validate caller-provided target/context tables without certificate verification."""
    targets: dict[str, tuple[dict[str, Any], ...]] = {}
    for fixture, endpoints in prefixes.items():
        if fixture not in FIXTURES or tuple(endpoints) != ENDPOINTS: raise CostError("candidate-prefix table must name all canonical endpoints")
        targets[fixture] = tuple({"kind": "endpoint_coordinate", "fixture": fixture, "endpoint": endpoint, "coordinate": coordinate} for endpoint in ENDPOINTS for coordinate in COORDINATES)
    members: dict[str, tuple[str, ...]] = {}
    for fixture, values in class_memberships.items():
        if fixture not in targets or len(values) != 4 or set(values) != set(ENDPOINTS): raise CostError("class membership lacks four endpoint labels")
        members[fixture] = tuple(values)
    return targets, members

def allocate_equal(row: Mapping[str, Any], *, strategy_view: str, scenario: Mapping[str, Any], targets: Sequence[Mapping[str, Any]], reason_code: str) -> list[dict[str, Any]]:
    """Allocate one physical row by canonical integer remainder; never creates a value from null."""
    if row.get("charge_kind") != "exclusive_leaf": raise CostError("derived rollups have no edges")
    if not targets: raise CostError("allocation target missing")
    ordered = sorted((dict(t) for t in targets), key=lambda t: (FIXTURES.index(t.get("fixture", "I0F0")) if t.get("fixture") in FIXTURES else 99, ENDPOINTS.index(t.get("endpoint", "K0")) if t.get("endpoint") in ENDPOINTS else 99, t.get("coordinate", 0)))
    n = len(ordered); result: list[dict[str, Any]] = []
    for index, target in enumerate(ordered):
        edge = {"record_type": "allocation_edge", "raw_cost_row_id": row["raw_cost_row_id"], "weight": {"numerator": 1, "denominator": n}, "strategy_view": strategy_view, "scenario": dict(scenario), "target": target, "reason_code": reason_code}
        for source, dest, why in (("CPU_nanoseconds", "allocated_CPU_nanoseconds", "CPU_unavailable_reason"), ("wall_nanoseconds", "allocated_wall_nanoseconds", "wall_unavailable_reason")):
            value = row[source]
            edge[dest] = None if value is None else value // n + int(index < value % n)
            edge[dest.replace("nanoseconds", "unavailable_reason")] = row[why] if value is None else None
        result.append(edge)
    return result

def actual_campaign_accounting(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Sum each exclusive physical leaf once; allocation views never enter this total."""
    cpu = wall = 0; unresolved: list[str] = []; peak: int | None = None
    for row in rows:
        if row.get("charge_kind") != "exclusive_leaf": continue
        for field in ("CPU_nanoseconds", "wall_nanoseconds"):
            if row.get(field) is None: unresolved.append(f"{row.get('raw_cost_row_id')}:{field}")
        if row.get("CPU_nanoseconds") is not None: cpu += row["CPU_nanoseconds"]
        if row.get("wall_nanoseconds") is not None: wall += row["wall_nanoseconds"]
        rss = row.get("process_group_peak_RSS_bytes")
        if rss is not None: peak = rss if peak is None else max(peak, rss)
    return {"status": "unresolved" if unresolved else "valid", "CPU_nanoseconds": None if unresolved else cpu, "wall_nanoseconds": None if unresolved else wall, "known_CPU_lower_bound": cpu, "known_wall_lower_bound": wall, "peak_RSS_bytes": peak, "unresolved": unresolved}

def validate_allocation_edges(rows: Sequence[Mapping[str, Any]], edges: Sequence[Mapping[str, Any]]) -> None:
    """Check closed edge shape, exact weights, and each row/view/scenario reconciliation."""
    raw = {r["raw_cost_row_id"]: r for r in rows if r.get("charge_kind") == "exclusive_leaf"}
    grouped: dict[tuple[str, str, bytes], list[Mapping[str, Any]]] = {}
    for edge in edges:
        if edge.get("record_type") != "allocation_edge" or edge.get("raw_cost_row_id") not in raw: raise CostError("edge does not name an exclusive raw row")
        weight = edge.get("weight")
        if not isinstance(weight, Mapping): raise CostError("edge weight missing")
        n, d = _integer(weight.get("numerator"), "weight numerator", 1), _integer(weight.get("denominator"), "weight denominator", 1)
        if math.gcd(n, d) != 1: raise CostError("weight is not reduced")
        scenario = edge.get("scenario")
        if not isinstance(scenario, Mapping): raise CostError("edge scenario missing")
        key = (edge["raw_cost_row_id"], edge.get("strategy_view"), canonical_json(dict(scenario)))
        grouped.setdefault(key, []).append(edge)
    for (row_id, view, _), group in grouped.items():
        row = raw[row_id]; weight = sum((Fraction(e["weight"]["numerator"], e["weight"]["denominator"]) for e in group), Fraction())
        if weight != 1: raise CostError("allocation weights do not reconcile")
        for source, allocated, reason in (("CPU_nanoseconds", "allocated_CPU_nanoseconds", "allocated_CPU_unavailable_reason"), ("wall_nanoseconds", "allocated_wall_nanoseconds", "allocated_wall_unavailable_reason")):
            values = [e.get(allocated) for e in group]
            if row[source] is None:
                if any(v is not None or e.get(reason) != row[source + "_unavailable_reason"] for v, e in zip(values, group)): raise CostError("unavailable allocation did not propagate")
            elif any(not isinstance(v, int) or isinstance(v, bool) for v in values) or sum(values) != row[source]: raise CostError("allocated integer does not reconcile")
        if view == "actual_only_scaffolding" and (len(group) != 1 or group[0].get("target", {}).get("raw_cost_row_id") != row_id): raise CostError("actual-only edge must be one physical-owner copy")
    if set(raw) != {key[0] for key in grouped}: raise CostError("exclusive raw row has no allocation edge")
