"""Consistency checks for symbolic numeric-width / peak-byte schema ledger.

Zero compute. No invented numeric widths, peak-byte bounds, probabilities,
τ, or clearance claims.
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
        "stage_member_width",
        "resource_vector_width",
        "peak_byte",
        "retry_conversion",
        "lineage_cross_link",
    }
)
EXPECTED_COUNTS = {
    "total_items": 25,
    "stage_member_width_family": 6,
    "resource_vector_width_family": 5,
    "peak_byte_family": 3,
    "retry_conversion_family": 3,
    "lineage_cross_link_family": 8,
    "wired_symbolic": 11,
    "checklist_only": 4,
    "not_instantiated": 6,
    "not_supported": 3,
    "deferred": 1,
}

# Keys whose values must not be invented numeric widths / bounds / probs.
PLACEHOLDER_VALUE_KEYS = frozenset(
    {
        "numeric_width",
        "expectation",
        "unit",
        "uniform_success_lower_bound",
        "transition_kernel",
        "independence_conditions",
    }
)
PLACEHOLDER_STATUS_KEYS = frozenset(
    {
        "numeric_width_status",
        "peak_byte_bound_status",
        "conversion_status",
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
    }
)
ALLOWED_PEAK_BYTE_BOUND_VALUES = frozenset(
    {None, "unresolved", "not_instantiated", "not_invented"}
)

# Integer/float values under these keys are ledger-edge cardinalities only.
COUNT_KEY_ALLOWLIST = frozenset(
    {
        "total_items",
        "stage_member_width_family",
        "resource_vector_width_family",
        "peak_byte_family",
        "retry_conversion_family",
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
    """Reject invented numeric widths / peak-byte / probability-like values."""
    root = load_yaml("numeric_width_schema_ledger.yaml")
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

        # Bare invented numerics on width/bound-ish keys.
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            leaf = key
            if leaf in COUNT_KEY_ALLOWLIST:
                continue
            # Commit / pin hex fragments are strings; reject other numerics.
            suspicious_substrings = (
                "width",
                "byte",
                "bit",
                "prob",
                "security",
                "charge",
                "expectation",
                "memory_bound",
            )
            if any(s in leaf.lower() for s in suspicious_substrings):
                hits.append(
                    {
                        "path": path,
                        "key": leaf,
                        "value": value,
                        "reason": "invented_numeric_on_width_or_bound_key",
                    }
                )

    return {"hits": hits, "passed": len(hits) == 0}


def check_obligation_ledger() -> Dict[str, Any]:
    root = load_yaml("numeric_width_schema_ledger.yaml")
    ledger = root.get("numeric_width_schema_ledger", root)
    items = ledger["items"]
    declared = ledger["item_counts"]

    status_counts = _count_statuses(items)
    family_counts = {
        fam: sum(1 for i in items if i.get("family") == fam)
        for fam in ALLOWED_FAMILIES
    }

    edge_ok = (
        len(items) == EXPECTED_COUNTS["total_items"]
        and family_counts["stage_member_width"]
        == EXPECTED_COUNTS["stage_member_width_family"]
        and family_counts["resource_vector_width"]
        == EXPECTED_COUNTS["resource_vector_width_family"]
        and family_counts["peak_byte"] == EXPECTED_COUNTS["peak_byte_family"]
        and family_counts["retry_conversion"]
        == EXPECTED_COUNTS["retry_conversion_family"]
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
        and i.get("from")
        and i.get("to")
        and i.get("family") in ALLOWED_FAMILIES
        and i.get("status") in ALLOWED_STATUS
        and isinstance(i.get("citations"), list)
        and len(i.get("citations", [])) >= 1
        and isinstance(i.get("non_claims"), list)
        and len(i.get("non_claims", [])) >= 1
        for i in items
    )

    cov = ledger.get("field_and_channel_coverage", {})
    rv = cov.get("resource_vector_numeric_widths", {})
    peak = cov.get("peak_byte_bound", {})
    coverage_ok = (
        all(rv.get(f) == "not_instantiated" for f in ("Q", "S", "P", "C", "H"))
        and peak.get("status") == "not_instantiated"
        and peak.get("value") == "unresolved"
        and cov.get("retry_to_peak_byte", {}).get("status") == "not_supported"
        and cov.get("tau", {}).get("instantiation_status") == "not_instantiated"
        and cov.get("ttm_v2", {}).get("equated_to_batch014") is False
        and cov.get("ttm_v2", {}).get("usable_as_global_tau") is False
    )

    summary = ledger.get("summary", {})
    non_claims = set(ledger.get("non_claims", []))
    required_non_claims = {
        "no_query_memory_clearance",
        "no_qm_stopping_clearance",
        "no_invented_numeric_width",
        "no_peak_byte_bound",
        "no_retry_to_peak_conversion",
        "no_probabilities",
        "no_security_bits",
        "no_tau_or_joint_finiteness",
        "no_collimationsieve_api_invention",
    }

    package_ok = (
        edge_ok
        and items_well_formed
        and coverage_ok
        and ledger.get("control_result") == "FAIL"
        and summary.get("ledger_status") == "width_schema_partial"
        and summary.get("control_result") == "FAIL"
        and summary.get("batch018_control_result_reconfirmed") == "FAIL"
        and summary.get("batch031_control_result_reconfirmed") == "FAIL"
        and summary.get("qm_memory_map_status") == "width_schema_partial"
        and summary.get("qm_memory_map_prior_status")
        == "history_uniform_tail_partial"
        and summary.get("qm_memory_map_clearance") is False
        and summary.get("query_memory_cleared") is False
        and summary.get("qm_stopping_cleared") is False
        and summary.get("qm_error_status_retained") == "f_union_ledger_partial"
        and summary.get("numeric_widths_invented") is False
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
        "peak_byte_bound_invented": summary.get("peak_byte_bound_invented"),
        "tau_invented": summary.get("tau_invented"),
    }


def check_memory_map_status() -> Dict[str, Any]:
    root = load_yaml("memory_map_status.yaml")
    mm = root.get("memory_map_status", root)
    qm = mm["qm_memory_map"]
    ok = (
        qm.get("prior_status") == "history_uniform_tail_partial"
        and qm.get("status_after_batch") == "width_schema_partial"
        and qm.get("clearance") is False
        and qm.get("reconciled") is False
        and qm.get("query_memory_cleared") is False
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
        and blockers.get("QM-STOPPING", {}).get("status") == "open"
        and blockers.get("QM-MEMORY-MAP", {}).get("status")
        == "width_schema_partial"
        and blockers.get("QM-ERROR", {}).get("status") == "f_union_ledger_partial"
        and clf.get("ledger_status") == "width_schema_partial"
        and clf.get("history_uniform_tail_status")
        == "history_uniform_tail_partial"
        and clf.get("verify_exit_status") == "verify_exit_partial"
        and clf.get("tau_schema_stopping_status") == "tau_schema_stopping_fail"
        and clf.get("batch020_pin_status_retained") == "no_admissible_pin"
        and clf.get("ttm_v2_panel", {}).get("equated_to_batch014") is False
        and clf.get("package", {}).get("pin_complete") is False
        and clf.get("idea_status_suggestion")
        == "confirm_width_schema_partial_query_memory_open"
        and clf.get("completion_gate_self_check", {}).get(
            "placeholders_only_no_invented_numerics"
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
        == "width_schema_partial"
        and ms.get("QM_MEMORY_MAP", {}).get("prior_status")
        == "history_uniform_tail_partial"
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
        load_yaml("numeric_width_schema_ledger.yaml"),
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
    """Confirm BATCH-022 width-reject / stage live-set APIs still present."""
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
        "verify_true_smoke": verify_true,
        "classify_success_smoke": classify_ok,
        "passed": ok,
        "scaffold_path": str(scaffold_dir),
        "init_exists": init_path.exists(),
    }
