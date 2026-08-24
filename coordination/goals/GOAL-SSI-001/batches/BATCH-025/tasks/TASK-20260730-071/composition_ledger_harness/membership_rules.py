"""Symbolic membership rules for F = ⋃ F_* (recovery_spec / BATCH-024).

Set-theoretic / checklist only. No probabilities, security bits, or τ.
"""

from __future__ import annotations

from typing import Any, Dict, FrozenSet, List, Set

# Seven path-justified recovery_spec constituents (BATCH-024).
CONSTITUENTS: tuple[str, ...] = (
    "F_input",
    "F_oracle",
    "F_cleanup",
    "F_stop",
    "F_recovery",
    "F_tail",
    "F_verify",
)

COMMON_F = "F"

# Explicit membership: every named F_* is a symbolic member of the union that
# is declared ⊆ F. Membership is set inclusion of failure channels, not a
# probability event model.
MEMBERSHIP_RULES: Dict[str, Dict[str, Any]] = {
    "R1_named_constituent_in_union": {
        "statement": "Each path-justified F_* is a member of the symbolic union U.",
        "predicate": "constituent_id ∈ U",
        "applies_to": list(CONSTITUENTS),
    },
    "R2_union_subseteq_common_F": {
        "statement": "U ⊆ F under the recovery_spec common-event definition.",
        "predicate": "U ⊆ F",
        "expression": (
            "F_input ∪ F_oracle ∪ F_cleanup ∪ F_stop ∪ "
            "F_recovery ∪ F_tail ∪ F_verify ⊆ F"
        ),
    },
    "R3_success_exit_verify_true": {
        "statement": (
            "Success exit requires Verify(x,k')=true. Report-only, unverified "
            "candidate, or exhausted residual search is a failure constituent "
            "of F, not success."
        ),
        "predicate": "exit_kind == success ⇔ verify_true_returned == true",
        "verify_crypto_required": False,
    },
    "R4_channel_fire_without_verify_true_in_F": {
        "statement": (
            "If a named F_* channel fires and no Verify=true k' is returned "
            "under the declared symbolic stopping policy, the exit is a "
            "member of common F."
        ),
        "predicate": (
            "channel ∈ CONSTITUENTS ∧ ¬verify_true_returned ⇒ classified_as_common_F"
        ),
    },
    "R5_f_sim_not_in_union_map": {
        "statement": (
            "F_sim is not a recovery_spec union constituent and has no "
            "implementation-derived implication into F (maps_to_F=false)."
        ),
        "predicate": "F_sim ∉ U ∧ maps_to_F(F_sim)=false",
        "maps_to_F": False,
    },
}


def symbolic_union() -> FrozenSet[str]:
    """Return the symbolic union set of path-justified constituents."""
    return frozenset(CONSTITUENTS)


def member_of_union(constituent_id: str, union: FrozenSet[str] | None = None) -> bool:
    u = symbolic_union() if union is None else union
    return constituent_id in u


def union_subseteq_common_f(union: FrozenSet[str] | None = None) -> bool:
    """Checklist: every union member is a declared ⊆ F constituent.

    This is a symbolic ledger check, not a probability inclusion proof and
    not crypto end-to-end justification.
    """
    u = symbolic_union() if union is None else union
    return u.issubset(set(CONSTITUENTS)) and len(u) == len(CONSTITUENTS)


def classify_exit(
    *,
    verify_true_returned: bool,
    channel: str | None,
    report_only: bool = False,
) -> Dict[str, Any]:
    """Apply membership rules to a symbolic exit (no crypto compute)."""
    if verify_true_returned and not report_only:
        return {
            "exit_kind": "success",
            "classified_as_common_F": False,
            "in_union": False,
            "channel": None,
            "rule": "R3_success_exit_verify_true",
        }
    # Failure path
    in_union = channel in CONSTITUENTS if channel else False
    return {
        "exit_kind": "failure",
        "classified_as_common_F": True,
        "in_union": in_union,
        "channel": channel,
        "rule": "R4_channel_fire_without_verify_true_in_F",
        "note": (
            "Failure relative to Verify; report_only also ∈ F by recovery_spec "
            "without being an F_sim→F map."
            if report_only
            else "Named channel failure without Verify=true ⇒ common F."
        ),
    }


def check_membership_ledger(
    path_justified: Set[str] | None = None,
) -> Dict[str, Any]:
    """Checkable membership ledger for all seven constituents."""
    justified = set(CONSTITUENTS) if path_justified is None else set(path_justified)
    u = symbolic_union()
    per_constituent: List[Dict[str, Any]] = []
    all_ok = True
    for cid in CONSTITUENTS:
        ok = member_of_union(cid, u) and cid in justified
        all_ok = all_ok and ok
        per_constituent.append(
            {
                "id": cid,
                "member_of_symbolic_union": member_of_union(cid, u),
                "path_justified_prior": cid in justified,
                "subseteq_F_by_recovery_spec": True,
                "membership_ok": ok,
                "probability_assigned": False,
            }
        )

    f_sim = {
        "id": "F_sim",
        "member_of_symbolic_union": False,
        "maps_to_F": False,
        "illicit_map_refused": True,
        "rule": "R5_f_sim_not_in_union_map",
    }

    success_control = classify_exit(
        verify_true_returned=True, channel=None, report_only=False
    )
    # Spot-check one failure channel for rule R4.
    fail_sample = classify_exit(
        verify_true_returned=False, channel="F_input", report_only=False
    )

    return {
        "union_expression": MEMBERSHIP_RULES["R2_union_subseteq_common_F"]["expression"],
        "union_members": sorted(u),
        "union_subseteq_common_F_checklist": union_subseteq_common_f(u),
        "rules": MEMBERSHIP_RULES,
        "constituents": per_constituent,
        "f_sim": f_sim,
        "success_control": success_control,
        "failure_sample": fail_sample,
        "all_membership_checks_passed": all_ok
        and success_control["exit_kind"] == "success"
        and fail_sample["classified_as_common_F"] is True
        and f_sim["maps_to_F"] is False,
        "probabilities_invented": False,
        "tau_invented": False,
        "query_memory_cleared": False,
    }
