"""Consistency checks for symbolic Q/S/P/C(+H) resource-vector ledger.

Zero compute. No numeric widths, probabilities, τ, or clearance claims.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:  # pragma: no cover - stdlib fallback not expected in-repo
    yaml = None  # type: ignore

ALLOWED_FIELD_STATUS = frozenset({"filled", "symbolic_only", "not_instantiated"})
REQUIRED_FIELDS = ("Q", "S", "P", "C", "H")
EXPECTED_FIELD_STATUS = {
    "Q": "symbolic_only",
    "S": "symbolic_only",
    "P": "not_instantiated",
    "C": "not_instantiated",
    "H": "not_instantiated",
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


def check_resource_vector_ledger() -> Dict[str, Any]:
    root = load_yaml("qspc_resource_vector_ledger.yaml")
    ledger = root.get("qspc_resource_vector_ledger", root)
    fields = ledger["fields"]
    results: List[Dict[str, Any]] = []

    for fid in REQUIRED_FIELDS:
        f = fields[fid]
        status = f.get("status")
        jf = f.get("joint_finiteness_established")
        nw = f.get("numeric_width")
        ok = (
            status in ALLOWED_FIELD_STATUS
            and status == EXPECTED_FIELD_STATUS[fid]
            and jf is False
            and nw == "not_invented"
        )
        results.append(
            {
                "field": fid,
                "status": status,
                "joint_finiteness_established": jf,
                "numeric_width": nw,
                "passed": ok,
            }
        )

    joint = ledger.get("joint_summary", {})
    non_claims = set(ledger.get("non_claims", []))
    required_non_claims = {
        "no_query_memory_clearance",
        "no_tau_or_joint_finiteness",
        "no_numeric_widths",
        "no_peak_byte_bound",
        "no_probabilities",
    }

    summary = ledger.get("summary", {})
    package_ok = (
        joint.get("joint_finiteness_established") is False
        and joint.get("tau_invented") is False
        and joint.get("numeric_widths_invented") is False
        and joint.get("any_field_filled_numeric") is False
        and summary.get("resource_vector_status") == "resource_vector_partial"
        and summary.get("query_memory_cleared") is False
        and summary.get("qm_stopping_cleared") is False
        and summary.get("qm_error_status_retained") == "f_union_ledger_partial"
        and required_non_claims.issubset(non_claims)
        and ledger.get("batch022_scaffold_modified") is False
        and all(r["passed"] for r in results)
    )

    return {
        "checks": results,
        "all_field_checks_passed": all(r["passed"] for r in results),
        "package_ok": package_ok,
        "resource_vector_status": summary.get("resource_vector_status"),
        "query_memory_cleared": summary.get("query_memory_cleared"),
        "qm_stopping_cleared": summary.get("qm_stopping_cleared"),
        "tau_invented": joint.get("tau_invented"),
        "numeric_widths_invented": joint.get("numeric_widths_invented"),
        "joint_finiteness_established": joint.get("joint_finiteness_established"),
    }


def check_memory_map_status() -> Dict[str, Any]:
    root = load_yaml("memory_map_status.yaml")
    mm = root.get("memory_map_status", root)
    qm = mm["qm_memory_map"]
    ok = (
        qm.get("prior_status") == "peak_liveset_partial"
        and qm.get("status_after_batch") == "resource_vector_partial"
        and qm.get("clearance") is False
        and qm.get("reconciled") is False
        and qm.get("query_memory_cleared") is False
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
        and blockers.get("QM-MEMORY-MAP", {}).get("status") == "resource_vector_partial"
        and blockers.get("QM-ERROR", {}).get("status") == "f_union_ledger_partial"
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


def check_forbidden_clearance_flags() -> Dict[str, Any]:
    """Ensure forbidden clearance / invention flags are not true anywhere."""
    docs = [
        load_yaml("qspc_resource_vector_ledger.yaml"),
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
            # Also reject literal clearance claim strings if present as booleans
            if node.get("clearance") is True and "qm_memory_map" in str(node).lower():
                hits.append({"key": "clearance", "value": True})

    # Explicit: disposition must not be PIN_COMPLETE
    clf = docs[2].get("classification", docs[2])
    if clf.get("disposition") == "FC0_PIN_COMPLETE_FOR_LATER_NUMERIC_REVIEW":
        hits.append({"key": "disposition", "value": clf.get("disposition")})

    return {
        "forbidden_true_hits": hits,
        "passed": len(hits) == 0,
    }


def check_mutation_status() -> Dict[str, Any]:
    root = load_yaml("mutation_status.yaml")
    ms = root.get("mutation_status", root)
    ok = (
        ms.get("scaffold_mutated") is False
        and ms.get("batch022_scaffold_modified") is False
        and ms.get("QM_MEMORY_MAP", {}).get("status_after_batch")
        == "resource_vector_partial"
        and ms.get("QM_ERROR", {}).get("status_after_batch") == "f_union_ledger_partial"
        and ms.get("QM_STOPPING", {}).get("status") == "remains_open"
        and ms.get("QUERY_MEMORY", {}).get("cleared") is False
    )
    return {
        "scaffold_mutated": ms.get("scaffold_mutated"),
        "qm_memory_map_after": ms.get("QM_MEMORY_MAP", {}).get("status_after_batch"),
        "qm_error_after": ms.get("QM_ERROR", {}).get("status_after_batch"),
        "passed": ok,
    }
