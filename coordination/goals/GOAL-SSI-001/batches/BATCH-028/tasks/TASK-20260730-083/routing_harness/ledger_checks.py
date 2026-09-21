"""Consistency checks for symbolic retry/cleanup residual-tail routing ledger.

Zero compute. No numeric widths, charges, probabilities, τ, or clearance claims.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ALLOWED_ROUTE_STATUS = frozenset(
    {"wired_symbolic", "checklist_only", "not_supported", "deferred"}
)
ALLOWED_FAMILIES = frozenset({"retry_cleanup", "residual_tail"})
REQUIRED_FIELDS = ("Q", "S", "P", "C", "H")
EXPECTED_COUNTS = {
    "total_routes": 28,
    "retry_cleanup_family": 20,
    "residual_tail_family": 8,
    "wired_symbolic": 17,
    "checklist_only": 7,
    "deferred": 1,
    "not_supported": 3,
}
FORBIDDEN_TRUE_KEYS = (
    "query_memory_cleared",
    "qm_stopping_cleared",
    "qm_error_cleared",
    "qm_memory_map_cleared",
    "pin_complete",
    "tau_invented",
    "joint_finiteness_established",
)


def task_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def load_yaml(name: str) -> Dict[str, Any]:
    path = task_dir() / name
    text = path.read_text(encoding="utf-8")
    if yaml is None:
        raise RuntimeError("PyYAML required to load ledger artifacts")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"{name}: expected mapping at root")
    return data


def _walk(obj: Any) -> List[Any]:
    out: List[Any] = [obj]
    if isinstance(obj, dict):
        for v in obj.values():
            out.extend(_walk(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(_walk(v))
    return out


def _count_statuses(routes: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {s: 0 for s in ALLOWED_ROUTE_STATUS}
    for r in routes:
        st = r.get("route_status")
        if st not in ALLOWED_ROUTE_STATUS:
            raise ValueError(f"illegal route_status: {st!r}")
        counts[st] += 1
    return counts


def check_routing_ledger() -> Dict[str, Any]:
    root = load_yaml("retry_cleanup_tail_routing.yaml")
    ledger = root.get("retry_cleanup_tail_routing", root)
    routes = ledger["routes"]
    declared = ledger["route_counts"]

    status_counts = _count_statuses(routes)
    family_counts = {
        "retry_cleanup": sum(
            1 for r in routes if r.get("route_family") == "retry_cleanup"
        ),
        "residual_tail": sum(
            1 for r in routes if r.get("route_family") == "residual_tail"
        ),
    }

    edge_ok = (
        len(routes) == EXPECTED_COUNTS["total_routes"]
        and family_counts["retry_cleanup"]
        == EXPECTED_COUNTS["retry_cleanup_family"]
        and family_counts["residual_tail"]
        == EXPECTED_COUNTS["residual_tail_family"]
        and status_counts["wired_symbolic"] == EXPECTED_COUNTS["wired_symbolic"]
        and status_counts["checklist_only"] == EXPECTED_COUNTS["checklist_only"]
        and status_counts["deferred"] == EXPECTED_COUNTS["deferred"]
        and status_counts["not_supported"] == EXPECTED_COUNTS["not_supported"]
        and declared["wired_symbolic"] == status_counts["wired_symbolic"]
        and declared["checklist_only"] == status_counts["checklist_only"]
        and declared["deferred"] == status_counts["deferred"]
        and declared["not_supported"] == status_counts["not_supported"]
        and (
            status_counts["wired_symbolic"]
            + status_counts["checklist_only"]
            + status_counts["deferred"]
            + status_counts["not_supported"]
            == len(routes)
        )
    )

    routes_well_formed = all(
        r.get("id")
        and r.get("from")
        and r.get("to")
        and r.get("route_family") in ALLOWED_FAMILIES
        and r.get("route_status") in ALLOWED_ROUTE_STATUS
        and isinstance(r.get("citations"), list)
        and len(r.get("citations", [])) >= 1
        and isinstance(r.get("non_claims"), list)
        and len(r.get("non_claims", [])) >= 1
        for r in routes
    )

    coverage = ledger.get("field_and_channel_coverage", {})
    coverage_ok = all(
        coverage.get(f, {}).get("has_wired_symbolic_route") is True
        and coverage.get(f, {}).get("numeric_charge") == "not_supported"
        for f in REQUIRED_FIELDS
    )

    summary = ledger.get("summary", {})
    non_claims = set(ledger.get("non_claims", []))
    required_non_claims = {
        "no_query_memory_clearance",
        "no_tau_or_joint_finiteness",
        "no_numeric_widths",
        "no_numeric_charges",
        "no_peak_byte_bound",
        "no_probabilities",
        "no_retry_to_peak_conversion",
    }

    package_ok = (
        edge_ok
        and routes_well_formed
        and coverage_ok
        and summary.get("routing_status") == "retry_cleanup_tail_partial"
        and summary.get("qm_memory_map_status") == "retry_cleanup_tail_partial"
        and summary.get("charge_incidence_lineage_retained")
        == "charge_incidence_partial"
        and summary.get("resource_vector_lineage_retained")
        == "resource_vector_partial"
        and summary.get("query_memory_cleared") is False
        and summary.get("qm_stopping_cleared") is False
        and summary.get("qm_error_status_retained") == "f_union_ledger_partial"
        and summary.get("numeric_charges_invented") is False
        and required_non_claims.issubset(non_claims)
        and ledger.get("batch022_scaffold_modified") is False
        and ledger.get("stopping_law_negative_control", {}).get(
            "joint_finiteness_established"
        )
        is False
        and ledger.get("ttm_v2_scope", {}).get("equated_to_batch014") is False
    )

    return {
        "route_count": len(routes),
        "family_counts": family_counts,
        "status_counts": status_counts,
        "edge_counts_ok": edge_ok,
        "routes_well_formed": routes_well_formed,
        "coverage_ok": coverage_ok,
        "package_ok": package_ok,
        "routing_status": summary.get("routing_status"),
        "query_memory_cleared": summary.get("query_memory_cleared"),
        "qm_stopping_cleared": summary.get("qm_stopping_cleared"),
        "numeric_charges_invented": summary.get("numeric_charges_invented"),
    }


def check_memory_map_status() -> Dict[str, Any]:
    root = load_yaml("memory_map_status.yaml")
    mm = root.get("memory_map_status", root)
    qm = mm["qm_memory_map"]
    ok = (
        qm.get("prior_status") == "charge_incidence_partial"
        and qm.get("status_after_batch") == "retry_cleanup_tail_partial"
        and qm.get("clearance") is False
        and qm.get("reconciled") is False
        and qm.get("query_memory_cleared") is False
        and mm.get("lineage_retained", {})
        .get("charge_incidence_partial", {})
        .get("status")
        == "charge_incidence_partial"
        and mm.get("lineage_retained", {})
        .get("resource_vector_partial", {})
        .get("status")
        == "resource_vector_partial"
    )
    return {
        "prior_status": qm.get("prior_status"),
        "status_after_batch": qm.get("status_after_batch"),
        "clearance": qm.get("clearance"),
        "query_memory_cleared": qm.get("query_memory_cleared"),
        "passed": ok,
    }


def check_classification() -> Dict[str, Any]:
    root = load_yaml("classification.yaml")
    clf = root.get("classification", root)
    blockers = {b["id"]: b for b in clf.get("named_blockers", [])}
    ok = (
        clf.get("disposition") == "FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED"
        and clf.get("non_extrapolation") is True
        and blockers.get("QM-STOPPING", {}).get("status") == "open"
        and blockers.get("QM-MEMORY-MAP", {}).get("status")
        == "retry_cleanup_tail_partial"
        and blockers.get("QM-ERROR", {}).get("status") == "f_union_ledger_partial"
        and clf.get("charge_incidence_status") == "charge_incidence_partial"
        and clf.get("resource_vector_status") == "resource_vector_partial"
        and clf.get("batch020_pin_status_retained") == "no_admissible_pin"
        and clf.get("ttm_v2_panel", {}).get("equated_to_batch014") is False
        and clf.get("package", {}).get("pin_complete") is False
        and clf.get("idea_status_suggestion")
        == "confirm_retry_cleanup_tail_partial_query_memory_open"
    )
    return {
        "disposition": clf.get("disposition"),
        "qm_stopping": blockers.get("QM-STOPPING", {}).get("status"),
        "qm_memory_map": blockers.get("QM-MEMORY-MAP", {}).get("status"),
        "qm_error": blockers.get("QM-ERROR", {}).get("status"),
        "non_extrapolation": clf.get("non_extrapolation"),
        "passed": ok,
    }


def check_mutation_status() -> Dict[str, Any]:
    root = load_yaml("mutation_status.yaml")
    ms = root.get("mutation_status", root)
    ok = (
        ms.get("scaffold_mutated") is False
        and ms.get("batch022_scaffold_modified") is False
        and ms.get("QM_MEMORY_MAP", {}).get("status_after_batch")
        == "retry_cleanup_tail_partial"
        and ms.get("QM_MEMORY_MAP", {}).get("prior_status")
        == "charge_incidence_partial"
        and ms.get("QM_ERROR", {}).get("status_after_batch")
        == "f_union_ledger_partial"
        and ms.get("QM_STOPPING", {}).get("status") == "remains_open"
        and ms.get("QUERY_MEMORY", {}).get("cleared") is False
    )
    return {
        "scaffold_mutated": ms.get("scaffold_mutated"),
        "qm_memory_map_after": ms.get("QM_MEMORY_MAP", {}).get("status_after_batch"),
        "qm_error_after": ms.get("QM_ERROR", {}).get("status_after_batch"),
        "passed": ok,
    }


def check_forbidden_clearance_flags() -> Dict[str, Any]:
    docs = [
        load_yaml("retry_cleanup_tail_routing.yaml"),
        load_yaml("memory_map_status.yaml"),
        load_yaml("classification.yaml"),
        load_yaml("mutation_status.yaml"),
    ]
    hits: List[Dict[str, Any]] = []
    for doc in docs:
        for node in _walk(doc):
            if not isinstance(node, dict):
                continue
            for key in FORBIDDEN_TRUE_KEYS:
                if node.get(key) is True:
                    hits.append({"key": key, "value": True})

    clf = docs[2].get("classification", docs[2])
    if clf.get("disposition") == "FC0_PIN_COMPLETE_FOR_LATER_NUMERIC_REVIEW":
        hits.append({"key": "disposition", "value": clf.get("disposition")})

    return {
        "forbidden_true_hits": hits,
        "passed": len(hits) == 0,
    }


def check_scaffold_read_only() -> Dict[str, Any]:
    """Confirm BATCH-022 LifetimeRegistry still exposes expected hook methods."""
    import sys

    batches_dir = task_dir().parents[2]
    scaffold_pkg_parent = (
        batches_dir / "BATCH-022" / "tasks" / "TASK-20260730-059"
    )
    scaffold_dir = scaffold_pkg_parent / "scaffold"
    init_path = scaffold_dir / "__init__.py"

    if str(scaffold_pkg_parent) not in sys.path:
        sys.path.insert(0, str(scaffold_pkg_parent))

    from scaffold.lifetime_hooks import LifetimeRegistry  # type: ignore
    from scaffold.state_machine import STAGE_LIVE_SETS  # type: ignore

    reg = LifetimeRegistry()
    required = list(LifetimeRegistry.REQUIRED_HOOK_IDS)
    methods = reg.implemented_hook_methods()
    stages = set(STAGE_LIVE_SETS.keys())
    expected_stages = {
        "preparation",
        "sieve_attempt",
        "recovery",
        "tail_verification",
    }

    # Mode-explicit cleanup and F_stop / F_tail controls must remain present.
    has_mode_cleanups = all(
        hasattr(reg, name)
        for name in ("cleanup_W_sieve", "cleanup_R_sieve", "cleanup_B_sieve")
    )
    has_channel_notes = all(
        hasattr(reg, name)
        for name in ("note_stopping_breach", "note_tail_exhaustion", "birth_M_tail")
    )

    ok = (
        len(required) == 12
        and len(methods) == 48  # 12 hooks × 4 methods
        and stages == expected_stages
        and has_mode_cleanups
        and has_channel_notes
        and "charge" not in " ".join(methods).lower()
    )
    return {
        "required_hook_count": len(required),
        "implemented_method_count": len(methods),
        "stages": sorted(stages),
        "has_mode_cleanups": has_mode_cleanups,
        "has_channel_notes": has_channel_notes,
        "passed": ok,
        "scaffold_path": str(scaffold_dir),
        "init_exists": init_path.exists(),
    }
