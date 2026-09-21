"""Consistency checks for symbolic global memory-bound obligation ledger.

Zero compute. No invented numeric widths, peak-byte bounds, charge meters,
global memory bounds, probabilities, τ, or clearance claims.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ALLOWED_STATUS = frozenset(
    {"wired_symbolic", "checklist_only", "not_instantiated", "not_supported", "deferred"}
)
ALLOWED_FAMILIES = frozenset(
    {
        "composition_surface",
        "charge_metering_feed",
        "peak_byte_bound_feed",
        "peak_liveset_feed",
        "global_bound_field_placeholder",
        "lineage_cross_link",
    }
)
EXPECTED_COUNTS = {
    "total_items": 42,
    "composition_surface_family": 8,
    "charge_metering_feed_family": 6,
    "peak_byte_bound_feed_family": 5,
    "peak_liveset_feed_family": 4,
    "global_bound_field_placeholder_family": 6,
    "lineage_cross_link_family": 13,
    "wired_symbolic": 28,
    "checklist_only": 1,
    "not_instantiated": 8,
    "not_supported": 4,
    "deferred": 1,
}

PLACEHOLDER_VALUE_KEYS = frozenset(
    {
        "numeric_width", "expectation", "unit", "units", "charge_units",
        "charge_accumulator", "per_hook_charge", "conversion_factor",
        "retry_multiplier", "composition_operator", "bound_units",
        "peak_aggregator", "uniform_success_lower_bound", "transition_kernel",
        "independence_conditions",
    }
)
ALLOWED_PLACEHOLDER_VALUES = frozenset(
    {
        None, "null", "not_instantiated", "unresolved", "not_invented",
        "not_supported", "symbolic_only", "deferred", "wired_symbolic", "checklist_only",
    }
)
ALLOWED_BOUND_VALUES = frozenset({None, "unresolved", "not_instantiated", "not_invented", "not_supported"})

FORBIDDEN_TRUE_KEYS = (
    "query_memory_cleared", "qm_stopping_cleared", "qm_error_cleared",
    "qm_memory_map_cleared", "pin_complete", "tau_invented",
    "joint_finiteness_established", "finite_almost_surely_proved",
    "finite_moments_proved", "numeric_widths_invented", "numeric_charges_invented",
    "peak_byte_bound_invented", "global_memory_bound_invented",
    "conversion_factor_invented", "retry_multiplier_invented",
    "history_uniform_progress_law_instantiated", "equivalent_summable_tail_instantiated",
    "any_filled_numeric", "clearance", "reconciled",
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


def _walk(obj: Any):
    yield obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def check_no_invented_numerics() -> Dict[str, Any]:
    hits = []
    for name in (
        "global_memory_bound_schema_ledger.yaml",
        "memory_map_status.yaml",
        "mutation_status.yaml",
        "classification.yaml",
    ):
        data = load_yaml(name)
        def visit(obj, path="$"):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    p = f"{path}.{k}"
                    if k in PLACEHOLDER_VALUE_KEYS and not isinstance(v, (dict, list)):
                        if isinstance(v, (int, float)) and not isinstance(v, bool):
                            hits.append({"path": p, "key": k, "value": v, "file": name})
                        elif v not in ALLOWED_PLACEHOLDER_VALUES:
                            hits.append({"path": p, "key": k, "value": v, "file": name})
                    if k in ("global_memory_bound", "peak_byte_bound") and not isinstance(v, (dict, list)):
                        if v not in ALLOWED_BOUND_VALUES:
                            hits.append({"path": p, "key": k, "value": v, "file": name})
                    if k in FORBIDDEN_TRUE_KEYS and v is True:
                        hits.append({"path": p, "key": k, "value": v, "file": name, "reason": "forbidden_true"})
                    visit(v, p)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    visit(v, f"{path}[{i}]")
        visit(data)
    return {"hits": hits, "passed": len(hits) == 0}


def check_obligation_ledger() -> Dict[str, Any]:
    data = load_yaml("global_memory_bound_schema_ledger.yaml")
    root = data["global_memory_bound_schema_ledger"]
    items = root["items"]
    fam_counts = {f: 0 for f in ALLOWED_FAMILIES}
    status_counts = {s: 0 for s in ALLOWED_STATUS}
    well = True
    for it in items:
        if it.get("family") not in ALLOWED_FAMILIES or it.get("status") not in ALLOWED_STATUS:
            well = False
        fam_counts[it["family"]] = fam_counts.get(it["family"], 0) + 1
        status_counts[it["status"]] = status_counts.get(it["status"], 0) + 1
        if it["family"] != "lineage_cross_link":
            if it.get("global_memory_bound_status") not in {"not_instantiated", "not_supported", "unresolved", "deferred"}:
                # wired items may still keep bound status not_instantiated
                if it.get("global_memory_bound") not in ALLOWED_BOUND_VALUES:
                    well = False
    edge_ok = (
        len(items) == EXPECTED_COUNTS["total_items"]
        and fam_counts["composition_surface"] == EXPECTED_COUNTS["composition_surface_family"]
        and fam_counts["charge_metering_feed"] == EXPECTED_COUNTS["charge_metering_feed_family"]
        and fam_counts["peak_byte_bound_feed"] == EXPECTED_COUNTS["peak_byte_bound_feed_family"]
        and fam_counts["peak_liveset_feed"] == EXPECTED_COUNTS["peak_liveset_feed_family"]
        and fam_counts["global_bound_field_placeholder"] == EXPECTED_COUNTS["global_bound_field_placeholder_family"]
        and fam_counts["lineage_cross_link"] == EXPECTED_COUNTS["lineage_cross_link_family"]
        and status_counts["wired_symbolic"] == EXPECTED_COUNTS["wired_symbolic"]
        and status_counts["checklist_only"] == EXPECTED_COUNTS["checklist_only"]
        and status_counts["not_instantiated"] == EXPECTED_COUNTS["not_instantiated"]
        and status_counts["not_supported"] == EXPECTED_COUNTS["not_supported"]
        and status_counts["deferred"] == EXPECTED_COUNTS["deferred"]
    )
    summary = root["summary"]
    package_ok = (
        summary.get("ledger_status") == "global_memory_bound_schema_partial"
        and summary.get("control_result") == "FAIL"
        and summary.get("query_memory_cleared") is False
        and summary.get("qm_stopping_cleared") is False
        and summary.get("global_memory_bound_invented") is False
        and summary.get("tau_invented") is False
        and summary.get("batch036_control_result_reconfirmed") == "FAIL"
        and root.get("batch022_scaffold_modified") is False
    )
    return {
        "edge_counts_ok": edge_ok,
        "items_well_formed": well,
        "item_count": len(items),
        "family_counts": fam_counts,
        "status_counts": status_counts,
        "package_ok": package_ok,
        "coverage_ok": True,
        "ledger_status": summary.get("ledger_status"),
        "control_result": summary.get("control_result"),
        "charge_metering_schema_partial_retained": summary.get("charge_metering_schema_partial_lineage_retained"),
        "peak_byte_bound_schema_partial_retained": summary.get("peak_byte_bound_schema_partial_lineage_retained"),
        "query_memory_cleared": summary.get("query_memory_cleared"),
        "qm_stopping_cleared": summary.get("qm_stopping_cleared"),
        "numeric_widths_invented": summary.get("numeric_widths_invented"),
        "numeric_charges_invented": summary.get("numeric_charges_invented"),
        "peak_byte_bound_invented": summary.get("peak_byte_bound_invented"),
        "global_memory_bound_invented": summary.get("global_memory_bound_invented"),
        "tau_invented": summary.get("tau_invented"),
    }


def check_memory_map_status() -> Dict[str, Any]:
    data = load_yaml("memory_map_status.yaml")["memory_map_status"]
    qm = data["qm_memory_map"]
    passed = (
        qm.get("prior_status") == "charge_metering_schema_partial"
        and qm.get("status_after_batch") == "global_memory_bound_schema_partial"
        and qm.get("clearance") is False
        and qm.get("query_memory_cleared") is False
        and qm.get("reconciled") is False
        and data["qm_stopping"]["control_result"] == "FAIL"
        and data["query_memory"]["disposition"] == "FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED"
    )
    return {
        "passed": passed,
        "prior_status": qm.get("prior_status"),
        "status_after_batch": qm.get("status_after_batch"),
        "clearance": qm.get("clearance"),
        "query_memory_cleared": qm.get("query_memory_cleared"),
    }


def check_classification() -> Dict[str, Any]:
    data = load_yaml("classification.yaml")["classification"]
    passed = (
        data.get("disposition") == "FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED"
        and data.get("control_result") == "FAIL"
        and data.get("non_extrapolation") is True
        and data["qm_statuses"]["QM_MEMORY_MAP"] == "global_memory_bound_schema_partial"
        and data["completion_gate_self_check"]["batch036_fail_reconfirmed"] is True
        and data["completion_gate_self_check"]["not_claimed_query_memory_clearance"] is True
    )
    return {"passed": passed, "disposition": data.get("disposition")}


def check_mutation_status() -> Dict[str, Any]:
    data = load_yaml("mutation_status.yaml")["mutation_status"]
    passed = (
        data["QM_MEMORY_MAP"]["status_after_batch"] == "global_memory_bound_schema_partial"
        and data["QM_STOPPING"]["control_result"] == "FAIL"
        and data["QUERY_MEMORY"]["cleared"] is False
        and data["batch020_pin_status_retained"] == "no_admissible_pin"
    )
    return {"passed": passed}


def check_forbidden_clearance_flags() -> Dict[str, Any]:
    report = check_no_invented_numerics()
    forbidden = [h for h in report["hits"] if h.get("reason") == "forbidden_true"]
    return {"passed": len(forbidden) == 0, "forbidden": forbidden}


def check_scaffold_read_only() -> Dict[str, Any]:
    data = load_yaml("global_memory_bound_schema_ledger.yaml")["global_memory_bound_schema_ledger"]
    passed = data.get("batch022_scaffold_modified") is False and data["scaffold_api_support"].get("global_fc0_memory_bound_api") is False
    return {"passed": passed, "batch022_scaffold_modified": data.get("batch022_scaffold_modified")}
