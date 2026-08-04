"""Consistency checks for symbolic Verify-exit / F_verify obligation ledger.

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
    {"success_exit", "f_verify_membership", "charge_routing"}
)
EXPECTED_COUNTS = {
    "total_items": 24,
    "success_exit_family": 7,
    "f_verify_membership_family": 6,
    "charge_routing_family": 11,
    "wired_symbolic": 17,
    "checklist_only": 1,
    "deferred": 1,
    "not_supported": 5,
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


def _count_statuses(items: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {s: 0 for s in ALLOWED_STATUS}
    for item in items:
        st = item.get("status")
        if st not in ALLOWED_STATUS:
            raise ValueError(f"illegal status: {st!r}")
        counts[st] += 1
    return counts


def check_obligation_ledger() -> Dict[str, Any]:
    root = load_yaml("verify_exit_obligation_ledger.yaml")
    ledger = root.get("verify_exit_obligation_ledger", root)
    items = ledger["items"]
    declared = ledger["item_counts"]

    status_counts = _count_statuses(items)
    family_counts = {
        "success_exit": sum(
            1 for i in items if i.get("family") == "success_exit"
        ),
        "f_verify_membership": sum(
            1 for i in items if i.get("family") == "f_verify_membership"
        ),
        "charge_routing": sum(
            1 for i in items if i.get("family") == "charge_routing"
        ),
    }

    edge_ok = (
        len(items) == EXPECTED_COUNTS["total_items"]
        and family_counts["success_exit"]
        == EXPECTED_COUNTS["success_exit_family"]
        and family_counts["f_verify_membership"]
        == EXPECTED_COUNTS["f_verify_membership_family"]
        and family_counts["charge_routing"]
        == EXPECTED_COUNTS["charge_routing_family"]
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
        and coverage.get("C", {}).get("has_wired_symbolic_route") is True
        and coverage.get("F_verify", {}).get("has_wired_symbolic_route") is True
        and coverage.get("success_exit", {}).get("has_wired_symbolic_route")
        is True
        and coverage.get("H", {}).get("numeric_charge") == "not_supported"
        and coverage.get("F_verify", {}).get("crypto_body") is False
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
        "no_crypto_Verify_body",
    }

    package_ok = (
        edge_ok
        and items_well_formed
        and coverage_ok
        and summary.get("ledger_status") == "verify_exit_partial"
        and summary.get("qm_memory_map_status") == "verify_exit_partial"
        and summary.get("prior_qm_memory_map_status")
        == "retry_cleanup_tail_partial"
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
        and required_non_claims.issubset(non_claims)
        and ledger.get("batch022_scaffold_modified") is False
        and ledger.get("stopping_law_negative_control", {}).get(
            "joint_finiteness_established"
        )
        is False
        and ledger.get("ttm_v2_scope", {}).get("equated_to_batch014") is False
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
    }


def check_memory_map_status() -> Dict[str, Any]:
    root = load_yaml("memory_map_status.yaml")
    mm = root.get("memory_map_status", root)
    qm = mm["qm_memory_map"]
    ok = (
        qm.get("prior_status") == "retry_cleanup_tail_partial"
        and qm.get("status_after_batch") == "verify_exit_partial"
        and qm.get("clearance") is False
        and qm.get("reconciled") is False
        and qm.get("query_memory_cleared") is False
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
        == "verify_exit_partial"
        and blockers.get("QM-ERROR", {}).get("status") == "f_union_ledger_partial"
        and clf.get("retry_cleanup_tail_status") == "retry_cleanup_tail_partial"
        and clf.get("charge_incidence_status") == "charge_incidence_partial"
        and clf.get("resource_vector_status") == "resource_vector_partial"
        and clf.get("batch020_pin_status_retained") == "no_admissible_pin"
        and clf.get("ttm_v2_panel", {}).get("equated_to_batch014") is False
        and clf.get("package", {}).get("pin_complete") is False
        and clf.get("idea_status_suggestion")
        == "confirm_verify_exit_partial_query_memory_open"
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
        == "verify_exit_partial"
        and ms.get("QM_MEMORY_MAP", {}).get("prior_status")
        == "retry_cleanup_tail_partial"
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
        load_yaml("verify_exit_obligation_ledger.yaml"),
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
    """Confirm BATCH-022 Verify / B_candidate / STAGE_LIVE_SETS still present."""
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
    from scaffold.types import CandidateSecret, PublicInstance  # type: ignore
    from scaffold.verify import (  # type: ignore
        Verify,
        VerificationFault,
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

    x = PublicInstance(token="x", scaffold_accept_token="ok")
    k_ok = CandidateSecret(token="ok")
    k_bad = CandidateSecret(token="no")
    verify_true = Verify(x, k_ok) is True
    verify_false = Verify(x, k_bad) is False
    classify_ok = classify_verify_outcome(True) == "success_exit"
    false_class = classify_verify_outcome(False)
    classify_false = (
        getattr(false_class, "value", None) == "F_verify"
        or str(false_class).endswith("F_verify")
    )

    has_b_candidate = all(
        hasattr(reg, name)
        for name in (
            "birth_B_candidate",
            "last_use_B_candidate",
            "cleanup_B_candidate",
            "destroy_B_candidate",
        )
    )
    has_verify_api = callable(Verify) and callable(classify_verify_outcome)
    fault_maps = VerificationFault.maps_to.value == "F_verify"

    ok = (
        stages == expected_stages
        and "B_candidate" in tail_members
        and has_b_candidate
        and has_verify_api
        and verify_true
        and verify_false
        and classify_ok
        and classify_false
        and fault_maps
        and "charge" not in " ".join(reg.implemented_hook_methods()).lower()
    )
    return {
        "stages": sorted(stages),
        "tail_has_B_candidate": "B_candidate" in tail_members,
        "has_b_candidate_hooks": has_b_candidate,
        "verify_true_smoke": verify_true,
        "verify_false_smoke": verify_false,
        "classify_success_smoke": classify_ok,
        "classify_f_verify_smoke": classify_false,
        "fault_maps_to_F_verify": fault_maps,
        "passed": ok,
        "scaffold_path": str(scaffold_dir),
        "init_exists": init_path.exists(),
    }
