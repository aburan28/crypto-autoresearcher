"""Consistency checks for symbolic stage↔resource charge-incidence ledger.

Zero compute. No numeric widths, charges, probabilities, τ, or clearance claims.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ALLOWED_INCIDENCE = frozenset(
    {"wired_symbolic", "checklist_only", "not_supported", "deferred"}
)
REQUIRED_FIELDS = ("Q", "S", "P", "C", "H")
EXPECTED_COUNTS = {
    "stage_slot_edges": 15,
    "lifetime_hook_edges": 13,
    "wired_symbolic": 18,
    "checklist_only": 7,
    "deferred": 1,
    "not_supported": 2,
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


def _count_statuses(edges: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {s: 0 for s in ALLOWED_INCIDENCE}
    for e in edges:
        st = e.get("incidence_status")
        if st not in ALLOWED_INCIDENCE:
            raise ValueError(f"illegal incidence_status: {st!r}")
        counts[st] += 1
    return counts


def check_charge_incidence_ledger() -> Dict[str, Any]:
    root = load_yaml("charge_incidence_ledger.yaml")
    ledger = root.get("charge_incidence_ledger", root)
    slot_edges = ledger["stage_slot_incidence_edges"]
    hook_edges = ledger["lifetime_hook_incidence_edges"]
    declared = ledger["incidence_counts"]

    slot_counts = _count_statuses(slot_edges)
    hook_counts = _count_statuses(hook_edges)
    combined = {
        k: slot_counts[k] + hook_counts[k] for k in ALLOWED_INCIDENCE
    }

    edge_ok = (
        len(slot_edges) == EXPECTED_COUNTS["stage_slot_edges"]
        and len(hook_edges) == EXPECTED_COUNTS["lifetime_hook_edges"]
        and combined["wired_symbolic"] == EXPECTED_COUNTS["wired_symbolic"]
        and combined["checklist_only"] == EXPECTED_COUNTS["checklist_only"]
        and combined["deferred"] == EXPECTED_COUNTS["deferred"]
        and combined["not_supported"] == EXPECTED_COUNTS["not_supported"]
        and declared["wired_symbolic"] == combined["wired_symbolic"]
        and declared["checklist_only"] == combined["checklist_only"]
        and declared["deferred"] == combined["deferred"]
        and declared["not_supported"] == combined["not_supported"]
        and (
            combined["wired_symbolic"]
            + combined["checklist_only"]
            + combined["deferred"]
            + combined["not_supported"]
            == len(slot_edges) + len(hook_edges)
        )
    )

    # Every edge has required fields and non_claims.
    edges_well_formed = all(
        e.get("from_object")
        and e.get("to_field") in REQUIRED_FIELDS
        and e.get("incidence_status") in ALLOWED_INCIDENCE
        and isinstance(e.get("citations"), list)
        and isinstance(e.get("non_claims"), list)
        and len(e.get("non_claims", [])) >= 1
        for e in slot_edges + hook_edges
    )

    coverage = ledger.get("field_coverage", {})
    coverage_ok = all(
        coverage.get(f, {}).get("has_wired_symbolic_edge") is True
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
    }

    package_ok = (
        edge_ok
        and edges_well_formed
        and coverage_ok
        and summary.get("charge_incidence_status") == "charge_incidence_partial"
        and summary.get("qm_memory_map_status") == "charge_incidence_partial"
        and summary.get("resource_vector_lineage_retained") == "resource_vector_partial"
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
        "slot_edge_count": len(slot_edges),
        "hook_edge_count": len(hook_edges),
        "combined_status_counts": combined,
        "edge_counts_ok": edge_ok,
        "edges_well_formed": edges_well_formed,
        "coverage_ok": coverage_ok,
        "package_ok": package_ok,
        "charge_incidence_status": summary.get("charge_incidence_status"),
        "query_memory_cleared": summary.get("query_memory_cleared"),
        "qm_stopping_cleared": summary.get("qm_stopping_cleared"),
        "numeric_charges_invented": summary.get("numeric_charges_invented"),
    }


def check_memory_map_status() -> Dict[str, Any]:
    root = load_yaml("memory_map_status.yaml")
    mm = root.get("memory_map_status", root)
    qm = mm["qm_memory_map"]
    ok = (
        qm.get("prior_status") == "resource_vector_partial"
        and qm.get("status_after_batch") == "charge_incidence_partial"
        and qm.get("clearance") is False
        and qm.get("reconciled") is False
        and qm.get("query_memory_cleared") is False
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
        == "charge_incidence_partial"
        and blockers.get("QM-ERROR", {}).get("status") == "f_union_ledger_partial"
        and clf.get("resource_vector_status") == "resource_vector_partial"
        and clf.get("batch020_pin_status_retained") == "no_admissible_pin"
        and clf.get("ttm_v2_panel", {}).get("equated_to_batch014") is False
        and clf.get("package", {}).get("pin_complete") is False
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
        load_yaml("charge_incidence_ledger.yaml"),
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

    # task_dir = .../batches/BATCH-027/tasks/TASK-20260730-079
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
    ok = (
        len(required) == 12
        and len(methods) == 48  # 12 hooks × 4 methods
        and stages == expected_stages
        and "charge" not in " ".join(methods).lower()
    )
    return {
        "required_hook_count": len(required),
        "implemented_method_count": len(methods),
        "stages": sorted(stages),
        "passed": ok,
        "scaffold_path": str(scaffold_dir),
        "init_exists": init_path.exists(),
    }
