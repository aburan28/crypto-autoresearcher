"""Operational-error composition structure (symbolic / set-theoretic only).

Channels combine into operational failure by set union under the recovery_spec
common-event definition. No invented probabilities, numeric bounds, or
security bits.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .membership_rules import CONSTITUENTS, MEMBERSHIP_RULES, check_membership_ledger

# How named channels compose into operational failure — checklist / set theory.
COMPOSITION_STRUCTURE: Dict[str, Any] = {
    "kind": "symbolic_set_union_under_common_event_F",
    "not_kind": [
        "probability_sum",
        "probability_union_bound_with_numeric_epsilons",
        "security_bit_reduction",
        "independent_Bernoulli_product",
    ],
    "common_event_F": (
        "F = { the procedure fails to return a k' with Verify(x,k')=true "
        "within its declared stopping policy }"
    ),
    "operational_failure_rule": (
        "An exit is an operational failure exactly when it is not a success "
        "exit. Success requires Verify=true. Any fired F_* channel without "
        "Verify=true is a constituent of F."
    ),
    "combination_rule": (
        "Operational failure set is the symbolic union of the seven "
        "path-justified constituents; membership in any constituent without "
        "Verify=true places the exit in F. Overlaps are permitted; no "
        "disjointness or independence assumption is asserted."
    ),
    "expression": MEMBERSHIP_RULES["R2_union_subseteq_common_F"]["expression"],
    "checklist_items": [
        {
            "id": "C1_all_constituents_named",
            "required": True,
            "description": "All seven recovery_spec F_* names present in ledger.",
        },
        {
            "id": "C2_prior_path_justification",
            "required": True,
            "description": (
                "BATCH-024 path_justified_on_scaffold retained as prior "
                "justification scope (scaffold-only)."
            ),
        },
        {
            "id": "C3_union_membership_explicit",
            "required": True,
            "description": "Each F_* has an explicit member_of_symbolic_union=true rule.",
        },
        {
            "id": "C4_success_exit_verify_true",
            "required": True,
            "description": "Success exit is Verify=true only.",
        },
        {
            "id": "C5_no_probability_weights",
            "required": True,
            "description": "No Pr[F_*], no union-bound epsilons, no security bits.",
        },
        {
            "id": "C6_f_sim_honesty",
            "required": True,
            "description": "F_sim maps_to_F=false retained; not a union constituent.",
        },
        {
            "id": "C7_no_tau",
            "required": True,
            "description": "No Verify-relative τ or joint Q/S/P/C finiteness invented.",
        },
    ],
    "dependency_assumptions_identified": [
        "scaffold_no_crypto_Verify_token_semantics",
        "symbolic_stopping_policy_halt_without_verify_true",
        "batch024_path_justified_on_scaffold_prior",
        "overlaps_among_F_star_permitted_without_independence_claim",
    ],
    "forbidden_fields_in_ledger": [
        "probability",
        "Pr",
        "epsilon",
        "security_bits",
        "union_bound_numeric",
        "tau",
        "joint_expectation",
    ],
}


def _ledger_has_forbidden_numeric_claims(blob: Dict[str, Any]) -> List[str]:
    """Shallow scan for forbidden probability/security keys in a dict tree."""
    forbidden_hits: List[str] = []
    stack = [("", blob)]
    while stack:
        path, node = stack.pop()
        if isinstance(node, dict):
            for k, v in node.items():
                key_l = str(k).lower()
                for bad in (
                    "probability",
                    "security_bit",
                    "epsilon_bound",
                    "pr_f_",
                    "union_bound_numeric",
                ):
                    if bad in key_l:
                        forbidden_hits.append(f"{path}.{k}" if path else str(k))
                if isinstance(v, (dict, list)):
                    stack.append((f"{path}.{k}" if path else str(k), v))
        elif isinstance(node, list):
            for i, item in enumerate(node):
                if isinstance(item, (dict, list)):
                    stack.append((f"{path}[{i}]", item))
    return forbidden_hits


def check_composition_structure() -> Dict[str, Any]:
    """Validate composition checklist against membership ledger (zero compute)."""
    membership = check_membership_ledger()
    checklist_results = []
    for item in COMPOSITION_STRUCTURE["checklist_items"]:
        iid = item["id"]
        if iid == "C1_all_constituents_named":
            passed = membership["union_members"] == sorted(CONSTITUENTS)
        elif iid == "C2_prior_path_justification":
            passed = all(c["path_justified_prior"] for c in membership["constituents"])
        elif iid == "C3_union_membership_explicit":
            passed = all(
                c["member_of_symbolic_union"] for c in membership["constituents"]
            )
        elif iid == "C4_success_exit_verify_true":
            passed = membership["success_control"]["exit_kind"] == "success"
        elif iid == "C5_no_probability_weights":
            passed = (
                membership["probabilities_invented"] is False
                and all(c["probability_assigned"] is False for c in membership["constituents"])
            )
        elif iid == "C6_f_sim_honesty":
            passed = membership["f_sim"]["maps_to_F"] is False
        elif iid == "C7_no_tau":
            passed = membership["tau_invented"] is False
        else:
            passed = False
        checklist_results.append(
            {"id": iid, "required": item["required"], "passed": passed}
        )

    forbidden_hits = _ledger_has_forbidden_numeric_claims(
        {
            "composition": COMPOSITION_STRUCTURE,
            "membership_summary": {
                "probabilities_invented": membership["probabilities_invented"],
                "tau_invented": membership["tau_invented"],
            },
        }
    )
    # Note: forbidden_fields_in_ledger lists names as documentation; the scan
    # above targets claim-like keys, not the documentation list itself.
    all_checklist = all(r["passed"] for r in checklist_results)

    return {
        "composition_kind": COMPOSITION_STRUCTURE["kind"],
        "expression": COMPOSITION_STRUCTURE["expression"],
        "operational_failure_rule": COMPOSITION_STRUCTURE["operational_failure_rule"],
        "combination_rule": COMPOSITION_STRUCTURE["combination_rule"],
        "checklist_results": checklist_results,
        "dependency_assumptions_identified": COMPOSITION_STRUCTURE[
            "dependency_assumptions_identified"
        ],
        "forbidden_claim_key_hits": forbidden_hits,
        "membership_all_passed": membership["all_membership_checks_passed"],
        "composition_structure_ok": all_checklist
        and membership["all_membership_checks_passed"]
        and len(forbidden_hits) == 0,
        "status": "f_union_ledger_partial",
        "probabilities_invented": False,
        "numeric_error_bounds_invented": False,
        "security_bits_invented": False,
        "query_memory_cleared": False,
        "qm_stopping_cleared": False,
        "interpretation_limit": (
            "Symbolic/set-theoretic composition ledger only. Not probability "
            "composition, not crypto Verify, not QUERY_MEMORY clearance."
        ),
    }
