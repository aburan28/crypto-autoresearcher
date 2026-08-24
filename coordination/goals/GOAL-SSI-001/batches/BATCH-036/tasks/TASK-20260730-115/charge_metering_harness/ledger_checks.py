"""Consistency checks for symbolic charge-metering obligation ledger.

Zero compute. No invented numeric widths, peak-byte bounds, charge meters,
probabilities, τ, or clearance claims.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ALLOWED_STATUS = frozenset(
    {
        "wired_symbolic",
        "checklist_only",
        "not_instantiated",
        "not_supported",
        "deferred",
    }
)
ALLOWED_FAMILIES = frozenset(
    {
        "lifetime_hook_surface",
        "charge_incidence_target",
        "width_binding_input",
        "peak_byte_bound_input",
        "meter_field_placeholder",
        "lineage_cross_link",
    }
)
EXPECTED_COUNTS = {
    "total_items": 43,
    "lifetime_hook_surface_family": 8,
    "charge_incidence_target_family": 8,
    "width_binding_input_family": 4,
    "peak_byte_bound_input_family": 5,
    "meter_field_placeholder_family": 6,
    "lineage_cross_link_family": 12,
    "wired_symbolic": 32,
    "checklist_only": 1,
    "not_instantiated": 5,
    "not_supported": 4,
    "deferred": 1,
}

PLACEHOLDER_VALUE_KEYS = frozenset(
    {
        "numeric_width",
        "expectation",
        "unit",
        "units",
        "charge_units",
        "charge_accumulator",
        "per_hook_charge",
        "conversion_factor",
        "retry_multiplier",
        "uniform_success_lower_bound",
        "transition_kernel",
        "independence_conditions",
    }
)
PLACEHOLDER_STATUS_KEYS = frozenset(
    {
        "numeric_width_status",
        "peak_byte_bound_status",
        "charge_units_status",
        "charge_accumulator_status",
        "per_hook_charge_status",
        "conversion_factor_status",
        "retry_multiplier_status",
        "units_status",
    }
)
ALLOWED_PLACEHOLDER_VALUES = frozenset(
    {
        None,
        "null",
        "not_instantiated",
        "unresolved",
        "not_invented",
        "not_supported",
        "symbolic_only",
        "deferred",
        "wired_symbolic",
        "checklist_only",
    }
)
ALLOWED_PEAK_BYTE_BOUND_VALUES = frozenset(
    {None, "unresolved", "not_instantiated", "not_invented"}
)

COUNT_KEY_ALLOWLIST = frozenset(
    {
        "total_items",
        "lifetime_hook_surface_family",
        "charge_incidence_target_family",
        "width_binding_input_family",
        "peak_byte_bound_input_family",
        "meter_field_placeholder_family",
        "lineage_cross_link_family",
        "wired_symbolic",
        "checklist_only",
        "not_instantiated",
        "not_supported",
        "deferred",
        "maximum_runs",
        "runs_attempted",
        "count",
        "apis_invented",
        "collimation_sieve_apis_invented",
        "tests_run",
        "failures",
        "errors",
    }
)

FORBIDDEN_TRUE_KEYS = (
    "query_memory_cleared",
    "qm_stopping_cleared",
    "qm_error_cleared",
    "qm_memory_map_cleared",
    "pin_complete",
    "tau_invented",
    "joint_finiteness_established",
    "finite_almost_surely_proved",
    "finite_moments_proved",
    "numeric_widths_invented",
    "numeric_charges_invented",
    "peak_byte_bound_invented",
    "conversion_factor_invented",
    "retry_multiplier_invented",
    "history_uniform_progress_law_instantiated",
    "equivalent_summable_tail_instantiated",
    "any_filled_numeric",
    "clearance",
    "reconciled",
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


def _walk_kv(obj: Any, path: str = "") -> List[Tuple[str, Any]]:
    out: List[Tuple[str, Any]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else str(k)
            out.append((p, v))
            out.extend(_walk_kv(v, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{path}[{i}]"
            out.extend(_walk_kv(v, p))
    return out


def _count_statuses(items: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {s: 0 for s in ALLOWED_STATUS}
    for item in items:
        st = item.get("status")
        if st not in ALLOWED_STATUS:
            raise ValueError(f"illegal status: {st!r}")
        counts[st] += 1
    return counts


def check_no_invented_numerics() -> Dict[str, Any]:
    """Reject invented numeric widths / peak-byte / charge / probability values."""
    root = load_yaml("charge_metering_schema_ledger.yaml")
    hits: List[Dict[str, Any]] = []

    for path, value in _walk_kv(root):
        key = path.rsplit(".", 1)[-1]
        if "[" in key:
            key = key.split("[", 1)[0]

        if key in PLACEHOLDER_VALUE_KEYS and not isinstance(value, (dict, list)):
            if value not in ALLOWED_PLACEHOLDER_VALUES:
                hits.append({"path": path, "key": key, "value": value})
        if key == "peak_byte_bound" and not isinstance(value, (dict, list)):
            if value not in ALLOWED_PEAK_BYTE_BOUND_VALUES:
                hits.append({"path": path, "key": key, "value": value})
        if key in PLACEHOLDER_STATUS_KEYS and not isinstance(value, (dict, list)):
            if value not in ALLOWED_PLACEHOLDER_VALUES:
                hits.append({"path": path, "key": key, "value": value})

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            leaf = key
            if leaf in COUNT_KEY_ALLOWLIST:
                continue
            suspicious_substrings = (
                "width",
                "byte",
                "bit",
                "prob",
                "security",
                "charge",
                "expectation",
                "memory_bound",
                "conversion_factor",
                "retry_multiplier",
                "accumulator",
            )
            if any(s in leaf.lower() for s in suspicious_substrings):
                hits.append(
                    {
                        "path": path,
                        "key": leaf,
                        "value": value,
                        "reason": "invented_numeric_on_width_or_charge_key",
                    }
                )

    return {"hits": hits, "passed": len(hits) == 0}


def check_obligation_ledger() -> Dict[str, Any]:
    root = load_yaml("charge_metering_schema_ledger.yaml")
    ledger = root.get("charge_metering_schema_ledger", root)
    items = ledger["items"]
    declared = ledger["item_counts"]

    status_counts = _count_statuses(items)
    family_counts = {
        fam: sum(1 for i in items if i.get("family") == fam)
        for fam in ALLOWED_FAMILIES
    }

    edge_ok = (
        len(items) == EXPECTED_COUNTS["total_items"]
        and family_counts["lifetime_hook_surface"]
        == EXPECTED_COUNTS["lifetime_hook_surface_family"]
        and family_counts["charge_incidence_target"]
        == EXPECTED_COUNTS["charge_incidence_target_family"]
        and family_counts["width_binding_input"]
        == EXPECTED_COUNTS["width_binding_input_family"]
        and family_counts["peak_byte_bound_input"]
        == EXPECTED_COUNTS["peak_byte_bound_input_family"]
        and family_counts["meter_field_placeholder"]
        == EXPECTED_COUNTS["meter_field_placeholder_family"]
        and family_counts["lineage_cross_link"]
        == EXPECTED_COUNTS["lineage_cross_link_family"]
        and status_counts["wired_symbolic"] == EXPECTED_COUNTS["wired_symbolic"]
        and status_counts["checklist_only"] == EXPECTED_COUNTS["checklist_only"]
        and status_counts["not_instantiated"]
        == EXPECTED_COUNTS["not_instantiated"]
        and status_counts["not_supported"] == EXPECTED_COUNTS["not_supported"]
        and status_counts["deferred"] == EXPECTED_COUNTS["deferred"]
        and declared["wired_symbolic"] == status_counts["wired_symbolic"]
        and declared["checklist_only"] == status_counts["checklist_only"]
        and declared["not_instantiated"] == status_counts["not_instantiated"]
        and declared["not_supported"] == status_counts["not_supported"]
        and declared["deferred"] == status_counts["deferred"]
        and (
            status_counts["wired_symbolic"]
            + status_counts["checklist_only"]
            + status_counts["not_instantiated"]
            + status_counts["not_supported"]
            + status_counts["deferred"]
            == len(items)
        )
    )

    items_well_formed = all(
        i.get("id")
        and i.get("from_slot")
        and i.get("to_meter_surface")
        and i.get("family") in ALLOWED_FAMILIES
        and i.get("status") in ALLOWED_STATUS
        and isinstance(i.get("citations"), list)
        and len(i.get("citations", [])) >= 1
        and isinstance(i.get("non_claims"), list)
        and len(i.get("non_claims", [])) >= 1
        and isinstance(i.get("obligation"), str)
        and len(i.get("obligation", "")) >= 1
        for i in items
    )

    cov = ledger.get("field_and_channel_coverage", {})
    units = cov.get("charge_units", {})
    acc = cov.get("charge_accumulator", {})
    phc = cov.get("per_hook_charge", {})
    peak = cov.get("peak_byte_bound", {})
    coverage_ok = (
        units.get("status") == "not_instantiated"
        and units.get("value") is None
        and acc.get("status") == "not_instantiated"
        and acc.get("value") is None
        and phc.get("status") == "not_instantiated"
        and phc.get("value") is None
        and peak.get("status") == "not_instantiated"
        and peak.get("value") == "unresolved"
        and cov.get("numeric_charge_meter", {}).get("status") == "not_supported"
        and cov.get("charge_meter_api", {}).get("status") == "not_supported"
        and cov.get("global_fc0_memory_bound", {}).get("status") == "not_supported"
        and cov.get("tau", {}).get("instantiation_status") == "not_instantiated"
        and cov.get("ttm_v2", {}).get("equated_to_batch014") is False
        and cov.get("ttm_v2", {}).get("usable_as_global_tau") is False
        and cov.get("charge_incidence_targets", {}).get("HOOK-charge-meter")
        == "not_supported"
    )

    summary = ledger.get("summary", {})
    non_claims = set(ledger.get("non_claims", []))
    required_non_claims = {
        "no_query_memory_clearance",
        "no_qm_stopping_clearance",
        "no_invented_numeric_width",
        "no_numeric_charges",
        "no_peak_byte_bound",
        "no_probabilities",
        "no_security_bits",
        "no_tau_or_joint_finiteness",
        "no_collimationsieve_api_invention",
        "no_global_fc0_memory_bound",
    }

    package_ok = (
        edge_ok
        and items_well_formed
        and coverage_ok
        and ledger.get("control_result") == "FAIL"
        and summary.get("ledger_status") == "charge_metering_schema_partial"
        and summary.get("control_result") == "FAIL"
        and summary.get("batch018_control_result_reconfirmed") == "FAIL"
        and summary.get("batch031_control_result_reconfirmed") == "FAIL"
        and summary.get("batch032_control_result_reconfirmed") == "FAIL"
        and summary.get("batch033_control_result_reconfirmed") == "FAIL"
        and summary.get("batch034_control_result_reconfirmed") == "FAIL"
        and summary.get("batch035_control_result_reconfirmed") == "FAIL"
        and summary.get("qm_memory_map_status") == "charge_metering_schema_partial"
        and summary.get("qm_memory_map_prior_status")
        == "peak_byte_bound_schema_partial"
        and summary.get("qm_memory_map_clearance") is False
        and summary.get("query_memory_cleared") is False
        and summary.get("qm_stopping_cleared") is False
        and summary.get("qm_error_status_retained") == "f_union_ledger_partial"
        and summary.get("peak_byte_bound_schema_partial_lineage_retained")
        == "peak_byte_bound_schema_partial"
        and summary.get("charge_incidence_lineage_retained")
        == "charge_incidence_partial"
        and summary.get("numeric_widths_invented") is False
        and summary.get("numeric_charges_invented") is False
        and summary.get("peak_byte_bound_invented") is False
        and summary.get("tau_invented") is False
        and summary.get("joint_finiteness_established") is False
        and required_non_claims.issubset(non_claims)
        and ledger.get("batch022_scaffold_modified") is False
        and ledger.get("stopping_law_negative_control", {}).get("control_result")
        == "FAIL"
        and ledger.get("ttm_v2_scope", {}).get("equated_to_batch014") is False
        and ledger.get("placeholder_policy", {}).get("invent_numeric_values")
        is False
        and ledger.get("lineage_retained", {})
        .get("peak_byte_bound_schema_partial", {})
        .get("status")
        == "peak_byte_bound_schema_partial"
        and ledger.get("lineage_retained", {})
        .get("charge_incidence_partial", {})
        .get("status")
        == "charge_incidence_partial"
        and ledger.get("lineage_retained", {})
        .get("width_slot_binding_partial", {})
        .get("status")
        == "width_slot_binding_partial"
    )

    return {
        "item_count": len(items),
        "family_counts": family_counts,
        "status_counts": status_counts,
        "edge_counts_ok": edge_ok,
        "items_well_formed": items_well_formed,
        "coverage_ok": coverage_ok,
        "package_ok": package_ok,
        "ledger_status": summary.get("ledger_status"),
        "control_result": ledger.get("control_result"),
        "query_memory_cleared": summary.get("query_memory_cleared"),
        "qm_stopping_cleared": summary.get("qm_stopping_cleared"),
        "numeric_widths_invented": summary.get("numeric_widths_invented"),
        "numeric_charges_invented": summary.get("numeric_charges_invented"),
        "peak_byte_bound_invented": summary.get("peak_byte_bound_invented"),
        "tau_invented": summary.get("tau_invented"),
        "peak_byte_bound_schema_partial_retained": summary.get(
            "peak_byte_bound_schema_partial_lineage_retained"
        ),
        "charge_incidence_partial_retained": summary.get(
            "charge_incidence_lineage_retained"
        ),
    }


def check_memory_map_status() -> Dict[str, Any]:
    root = load_yaml("memory_map_status.yaml")
    mm = root.get("memory_map_status", root)
    qm = mm["qm_memory_map"]
    ok = (
        qm.get("prior_status") == "peak_byte_bound_schema_partial"
        and qm.get("status_after_batch") == "charge_metering_schema_partial"
        and qm.get("clearance") is False
        and qm.get("reconciled") is False
        and qm.get("query_memory_cleared") is False
        and mm.get("lineage_retained", {})
        .get("peak_byte_bound_schema_partial", {})
        .get("status")
        == "peak_byte_bound_schema_partial"
        and mm.get("lineage_retained", {})
        .get("charge_incidence_partial", {})
        .get("status")
        == "charge_incidence_partial"
        and mm.get("lineage_retained", {})
        .get("retry_peak_byte_schema_partial", {})
        .get("status")
        == "retry_peak_byte_schema_partial"
        and mm.get("lineage_retained", {})
        .get("width_slot_binding_partial", {})
        .get("status")
        == "width_slot_binding_partial"
        and mm.get("lineage_retained", {})
        .get("width_schema_partial", {})
        .get("status")
        == "width_schema_partial"
        and mm.get("lineage_retained", {})
        .get("retry_cleanup_tail_partial", {})
        .get("status")
        == "retry_cleanup_tail_partial"
        and mm.get("lineage_retained", {})
        .get("history_uniform_tail_partial", {})
        .get("status")
        == "history_uniform_tail_partial"
        and mm.get("lineage_retained", {})
        .get("verify_exit_partial", {})
        .get("status")
        == "verify_exit_partial"
        and mm.get("lineage_retained", {})
        .get("resource_vector_partial", {})
        .get("status")
        == "resource_vector_partial"
        and mm.get("lineage_retained", {})
        .get("peak_liveset_partial", {})
        .get("status")
        == "peak_liveset_partial"
        and mm.get("lineage_retained", {})
        .get("tau_schema_stopping_fail", {})
        .get("control_result")
        == "FAIL"
        and mm.get("lineage_retained", {})
        .get("f_union_ledger_partial", {})
        .get("status")
        == "f_union_ledger_partial"
        and mm.get("batch020_pin_status_retained") == "no_admissible_pin"
        and mm.get("ledger_snapshot", {}).get("control_result") == "FAIL"
        and mm.get("ledger_snapshot", {}).get("numeric_widths_invented") is False
        and mm.get("ledger_snapshot", {}).get("numeric_charges_invented") is False
        and mm.get("ledger_snapshot", {}).get("peak_byte_bound_invented") is False
        and mm.get("ledger_snapshot", {}).get("tau_invented") is False
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
        and clf.get("control_result") == "FAIL"
        and clf.get("batch018_control_result_reconfirmed") == "FAIL"
        and clf.get("batch031_control_result_reconfirmed") == "FAIL"
        and clf.get("batch032_control_result_reconfirmed") == "FAIL"
        and clf.get("batch033_control_result_reconfirmed") == "FAIL"
        and clf.get("batch034_control_result_reconfirmed") == "FAIL"
        and clf.get("batch035_control_result_reconfirmed") == "FAIL"
        and blockers.get("QM-STOPPING", {}).get("status") == "open"
        and blockers.get("QM-MEMORY-MAP", {}).get("status")
        == "charge_metering_schema_partial"
        and blockers.get("QM-ERROR", {}).get("status") == "f_union_ledger_partial"
        and clf.get("ledger_status") == "charge_metering_schema_partial"
        and clf.get("peak_byte_bound_schema_status")
        == "peak_byte_bound_schema_partial"
        and clf.get("charge_incidence_status") == "charge_incidence_partial"
        and clf.get("history_uniform_tail_status")
        == "history_uniform_tail_partial"
        and clf.get("verify_exit_status") == "verify_exit_partial"
        and clf.get("tau_schema_stopping_status") == "tau_schema_stopping_fail"
        and clf.get("batch020_pin_status_retained") == "no_admissible_pin"
        and clf.get("ttm_v2_panel", {}).get("equated_to_batch014") is False
        and clf.get("package", {}).get("pin_complete") is False
        and clf.get("idea_status_suggestion")
        == "confirm_charge_metering_schema_partial_query_memory_open"
        and clf.get("completion_gate_self_check", {}).get(
            "placeholders_only_no_invented_numerics"
        )
        is True
        and clf.get("completion_gate_self_check", {}).get(
            "peak_byte_bound_schema_partial_lineage_retained"
        )
        is True
        and clf.get("completion_gate_self_check", {}).get(
            "charge_incidence_partial_lineage_retained"
        )
        is True
    )
    return {
        "disposition": clf.get("disposition"),
        "control_result": clf.get("control_result"),
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
        and ms.get("collimation_sieve_touched") is False
        and ms.get("QM_MEMORY_MAP", {}).get("status_after_batch")
        == "charge_metering_schema_partial"
        and ms.get("QM_MEMORY_MAP", {}).get("prior_status")
        == "peak_byte_bound_schema_partial"
        and ms.get("QM_MEMORY_MAP", {}).get("clearance") is False
        and ms.get("QM_ERROR", {}).get("status_after_batch")
        == "f_union_ledger_partial"
        and ms.get("QM_STOPPING", {}).get("status") == "remains_open"
        and ms.get("QM_STOPPING", {}).get("control_result") == "FAIL"
        and ms.get("QUERY_MEMORY", {}).get("cleared") is False
        and ms.get("QUERY_MEMORY", {}).get("disposition")
        == "FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED"
    )
    return {
        "scaffold_mutated": ms.get("scaffold_mutated"),
        "qm_memory_map_after": ms.get("QM_MEMORY_MAP", {}).get(
            "status_after_batch"
        ),
        "qm_error_after": ms.get("QM_ERROR", {}).get("status_after_batch"),
        "qm_stopping_control_result": ms.get("QM_STOPPING", {}).get(
            "control_result"
        ),
        "passed": ok,
    }


def check_forbidden_clearance_flags() -> Dict[str, Any]:
    docs = [
        load_yaml("charge_metering_schema_ledger.yaml"),
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
    if clf.get("control_result") != "FAIL":
        hits.append(
            {"key": "control_result", "value": clf.get("control_result")}
        )
    if clf.get("disposition") != "FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED":
        hits.append({"key": "disposition", "value": clf.get("disposition")})

    return {
        "forbidden_true_hits": hits,
        "passed": len(hits) == 0,
    }


def check_scaffold_read_only() -> Dict[str, Any]:
    """Confirm BATCH-022 width-reject / cleanup / stage live-set APIs still present."""
    import sys

    batches_dir = task_dir().parents[2]
    scaffold_pkg_parent = (
        batches_dir / "BATCH-022" / "tasks" / "TASK-20260730-059"
    )
    scaffold_dir = scaffold_pkg_parent / "scaffold"
    init_path = scaffold_dir / "__init__.py"

    if str(scaffold_pkg_parent) not in sys.path:
        sys.path.insert(0, str(scaffold_pkg_parent))

    from scaffold.lifetime_hooks import LifetimeError, LifetimeRegistry  # type: ignore
    from scaffold.state_machine import STAGE_LIVE_SETS  # type: ignore
    from scaffold.types import CandidateSecret, PublicInstance  # type: ignore
    from scaffold.verify import Verify, classify_verify_outcome  # type: ignore

    reg = LifetimeRegistry()
    stages = set(STAGE_LIVE_SETS.keys())
    expected_stages = {
        "preparation",
        "sieve_attempt",
        "recovery",
        "tail_verification",
    }
    tail_members = set(STAGE_LIVE_SETS["tail_verification"])

    x_prep = PublicInstance(token="x", scaffold_accept_token="ok")
    reg.birth_B_input(x_prep)
    reg.birth_B_attempt({})
    w_s = reg.birth_W_sieve({})
    r_s = reg.birth_R_sieve({}, {})
    reg.cleanup_W_sieve(w_s, "retry")
    reg.cleanup_R_sieve(r_s, "retry")
    reg.cleanup_W_sieve(w_s, "accept")
    reg.cleanup_R_sieve(r_s, "accept")
    reg.destroy_W_sieve(w_s)
    reg.destroy_R_sieve(r_s)
    t = reg.birth_accepted_transcript({})
    b_post = reg.birth_B_post(t)
    b_rec = reg.birth_B_recovery(b_post, t)

    width_reject_ok = False
    try:
        reg.birth_M_tail(
            b_rec,
            width_decl={"numeric_width": 128},
            enumeration_order_decl={},
            stopping_rule_decl={"invents_tau": False},
            shares_B_recovery_decl=False,
        )
    except LifetimeError as exc:
        width_reject_ok = "numeric_width" in str(exc).lower() or (
            getattr(exc, "channel", None) is not None
            and getattr(exc.channel, "value", "") == "F_tail"
        )

    tau_reject_ok = False
    try:
        reg.birth_M_tail(
            b_rec,
            width_decl={"unit": "symbolic"},
            enumeration_order_decl={},
            stopping_rule_decl={"invents_tau": True},
            shares_B_recovery_decl=False,
        )
    except LifetimeError as exc:
        tau_reject_ok = "tau" in str(exc).lower() or (
            getattr(exc, "channel", None) is not None
            and getattr(exc.channel, "value", "") == "F_stop"
        )

    x = PublicInstance(token="x", scaffold_accept_token="ok")
    k_ok = CandidateSecret(token="ok")
    verify_true = Verify(x, k_ok) is True
    classify_ok = classify_verify_outcome(True) == "success_exit"

    ok = (
        stages == expected_stages
        and "M_tail" in tail_members
        and tau_reject_ok
        and width_reject_ok
        and verify_true
        and classify_ok
        and "charge" not in " ".join(reg.implemented_hook_methods()).lower()
    )
    return {
        "stages": sorted(stages),
        "tail_has_M_tail": "M_tail" in tail_members,
        "birth_M_tail_rejects_invents_tau": tau_reject_ok,
        "birth_M_tail_rejects_numeric_width": width_reject_ok,
        "cleanup_retry_accept_smoke": True,
        "verify_true_smoke": verify_true,
        "classify_success_smoke": classify_ok,
        "no_charge_meter_methods": "charge"
        not in " ".join(reg.implemented_hook_methods()).lower(),
        "passed": ok,
        "scaffold_path": str(scaffold_dir),
        "init_exists": init_path.exists(),
    }
