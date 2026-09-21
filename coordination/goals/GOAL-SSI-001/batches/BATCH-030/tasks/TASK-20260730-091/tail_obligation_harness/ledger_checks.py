"""Consistency checks for symbolic history-uniform / summable-tail ledger.

Zero compute. No numeric widths, charges, probabilities, τ, or clearance claims.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ALLOWED_STATUS = frozenset(
    {"wired_symbolic", "checklist_only", "not_supported", "deferred"}
)
ALLOWED_FAMILIES = frozenset(
    {
        "history_uniform_tail",
        "f_stop_f_tail_membership",
        "charge_routing_link",
    }
)
EXPECTED_COUNTS = {
    "total_items": 24,
    "history_uniform_tail_family": 7,
    "f_stop_f_tail_membership_family": 7,
    "charge_routing_link_family": 10,
    "wired_symbolic": 14,
    "checklist_only": 3,
    "deferred": 1,
    "not_supported": 6,
}
FORBIDDEN_TRUE_KEYS = (
    "query_memory_cleared",
    "qm_stopping_cleared",
    "qm_error_cleared",
    "qm_memory_map_cleared",
    "pin_complete",
    "tau_invented",
    "joint_finiteness_established",
    "history_uniform_progress_law_instantiated",
    "equivalent_summable_tail_instantiated",
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


def _count_statuses(items: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {s: 0 for s in ALLOWED_STATUS}
    for item in items:
        st = item.get("status")
        if st not in ALLOWED_STATUS:
            raise ValueError(f"illegal status: {st!r}")
        counts[st] += 1
    return counts


def check_obligation_ledger() -> Dict[str, Any]:
    root = load_yaml("history_uniform_tail_ledger.yaml")
    ledger = root.get("history_uniform_tail_ledger", root)
    items = ledger["items"]
    declared = ledger["item_counts"]

    status_counts = _count_statuses(items)
    family_counts = {
        "history_uniform_tail": sum(
            1 for i in items if i.get("family") == "history_uniform_tail"
        ),
        "f_stop_f_tail_membership": sum(
            1 for i in items if i.get("family") == "f_stop_f_tail_membership"
        ),
        "charge_routing_link": sum(
            1 for i in items if i.get("family") == "charge_routing_link"
        ),
    }

    edge_ok = (
        len(items) == EXPECTED_COUNTS["total_items"]
        and family_counts["history_uniform_tail"]
        == EXPECTED_COUNTS["history_uniform_tail_family"]
        and family_counts["f_stop_f_tail_membership"]
        == EXPECTED_COUNTS["f_stop_f_tail_membership_family"]
        and family_counts["charge_routing_link"]
        == EXPECTED_COUNTS["charge_routing_link_family"]
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

    coverage = ledger.get("field_and_channel_coverage", {})
    coverage_ok = (
        coverage.get("H", {}).get("has_wired_symbolic_route") is True
        and coverage.get("F_tail", {}).get("has_wired_symbolic_route") is True
        and coverage.get("F_stop", {}).get("has_wired_symbolic_or_checklist_route")
        is True
        and coverage.get("history_uniform_progress_law", {}).get("instantiated")
        is False
        and coverage.get("equivalent_summable_tail", {}).get("instantiated")
        is False
        and coverage.get("H", {}).get("numeric_charge") == "not_supported"
        and coverage.get("verify_exit_lineage", {}).get("clears_stopping") is False
    )

    summary = ledger.get("summary", {})
    non_claims = set(ledger.get("non_claims", []))
    required_non_claims = {
        "no_query_memory_clearance",
        "no_tau_or_joint_finiteness",
        "no_history_uniform_proof",
        "no_summable_tail_proof",
        "no_numeric_widths",
        "no_numeric_charges",
        "no_peak_byte_bound",
        "no_probabilities",
        "no_crypto_Verify_body",
    }

    package_ok = (
        edge_ok
        and items_well_formed
        and coverage_ok
        and summary.get("ledger_status") == "history_uniform_tail_partial"
        and summary.get("qm_memory_map_status") == "history_uniform_tail_partial"
        and summary.get("prior_qm_memory_map_status") == "verify_exit_partial"
        and summary.get("verify_exit_lineage_retained") == "verify_exit_partial"
        and summary.get("retry_cleanup_tail_lineage_retained")
        == "retry_cleanup_tail_partial"
        and summary.get("charge_incidence_lineage_retained")
        == "charge_incidence_partial"
        and summary.get("resource_vector_lineage_retained")
        == "resource_vector_partial"
        and summary.get("query_memory_cleared") is False
        and summary.get("qm_stopping_cleared") is False
        and summary.get("qm_error_status_retained") == "f_union_ledger_partial"
        and summary.get("numeric_charges_invented") is False
        and summary.get("crypto_verify_implemented") is False
        and summary.get("history_uniform_progress_law_instantiated") is False
        and summary.get("equivalent_summable_tail_instantiated") is False
        and summary.get("tau_invented") is False
        and required_non_claims.issubset(non_claims)
        and ledger.get("batch022_scaffold_modified") is False
        and ledger.get("stopping_law_negative_control", {}).get(
            "joint_finiteness_established"
        )
        is False
        and ledger.get("stopping_law_negative_control", {}).get(
            "history_uniform_progress_law_instantiated"
        )
        is False
        and ledger.get("ttm_v2_scope", {}).get("equated_to_batch014") is False
        and ledger.get("ttm_v2_scope", {}).get("usable_as_global_tau") is False
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
        "query_memory_cleared": summary.get("query_memory_cleared"),
        "qm_stopping_cleared": summary.get("qm_stopping_cleared"),
        "numeric_charges_invented": summary.get("numeric_charges_invented"),
        "crypto_verify_implemented": summary.get("crypto_verify_implemented"),
        "tau_invented": summary.get("tau_invented"),
    }


def check_memory_map_status() -> Dict[str, Any]:
    root = load_yaml("memory_map_status.yaml")
    mm = root.get("memory_map_status", root)
    qm = mm["qm_memory_map"]
    ok = (
        qm.get("prior_status") == "verify_exit_partial"
        and qm.get("status_after_batch") == "history_uniform_tail_partial"
        and qm.get("clearance") is False
        and qm.get("reconciled") is False
        and qm.get("query_memory_cleared") is False
        and mm.get("lineage_retained", {})
        .get("verify_exit_partial", {})
        .get("status")
        == "verify_exit_partial"
        and mm.get("lineage_retained", {})
        .get("retry_cleanup_tail_partial", {})
        .get("status")
        == "retry_cleanup_tail_partial"
        and mm.get("lineage_retained", {})
        .get("charge_incidence_partial", {})
        .get("status")
        == "charge_incidence_partial"
        and mm.get("lineage_retained", {})
        .get("resource_vector_partial", {})
        .get("status")
        == "resource_vector_partial"
        and mm.get("lineage_retained", {})
        .get("f_union_ledger_partial", {})
        .get("status")
        == "f_union_ledger_partial"
        and mm.get("batch020_pin_status_retained") == "no_admissible_pin"
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
        == "history_uniform_tail_partial"
        and blockers.get("QM-ERROR", {}).get("status") == "f_union_ledger_partial"
        and clf.get("verify_exit_status") == "verify_exit_partial"
        and clf.get("retry_cleanup_tail_status") == "retry_cleanup_tail_partial"
        and clf.get("charge_incidence_status") == "charge_incidence_partial"
        and clf.get("resource_vector_status") == "resource_vector_partial"
        and clf.get("batch020_pin_status_retained") == "no_admissible_pin"
        and clf.get("ttm_v2_panel", {}).get("equated_to_batch014") is False
        and clf.get("package", {}).get("pin_complete") is False
        and clf.get("idea_status_suggestion")
        == "confirm_history_uniform_tail_partial_query_memory_open"
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
        == "history_uniform_tail_partial"
        and ms.get("QM_MEMORY_MAP", {}).get("prior_status")
        == "verify_exit_partial"
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
        load_yaml("history_uniform_tail_ledger.yaml"),
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
    """Confirm BATCH-022 F_stop/F_tail / M_tail / Verify APIs still present."""
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
    from scaffold.verify import (  # type: ignore
        Verify,
        classify_verify_outcome,
    )

    reg = LifetimeRegistry()
    stages = set(STAGE_LIVE_SETS.keys())
    expected_stages = {
        "preparation",
        "sieve_attempt",
        "recovery",
        "tail_verification",
    }
    tail_members = set(STAGE_LIVE_SETS["tail_verification"])

    has_channel_notes = all(
        hasattr(reg, name)
        for name in ("note_stopping_breach", "note_tail_exhaustion", "birth_M_tail")
    )
    f_stop = reg.note_stopping_breach()
    f_tail = reg.note_tail_exhaustion()
    stop_ok = getattr(f_stop, "value", None) == "F_stop" or str(f_stop).endswith(
        "F_stop"
    )
    tail_ok = getattr(f_tail, "value", None) == "F_tail" or str(f_tail).endswith(
        "F_tail"
    )

    # Minimal path to live B_recovery, then confirm birth_M_tail rejects
    # numeric_width / invents_tau (no τ invented).
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
        and has_channel_notes
        and stop_ok
        and tail_ok
        and tau_reject_ok
        and width_reject_ok
        and verify_true
        and classify_ok
        and "charge" not in " ".join(reg.implemented_hook_methods()).lower()
    )
    return {
        "stages": sorted(stages),
        "tail_has_M_tail": "M_tail" in tail_members,
        "has_channel_notes": has_channel_notes,
        "note_stopping_breach_F_stop": stop_ok,
        "note_tail_exhaustion_F_tail": tail_ok,
        "birth_M_tail_rejects_invents_tau": tau_reject_ok,
        "birth_M_tail_rejects_numeric_width": width_reject_ok,
        "verify_true_smoke": verify_true,
        "classify_success_smoke": classify_ok,
        "passed": ok,
        "scaffold_path": str(scaffold_dir),
        "init_exists": init_path.exists(),
    }
