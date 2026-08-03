"""Probe path-justified F_* ⊆ F inclusions on FC0-EXT scaffolding.

Beyond BATCH-023 scaffold_channel_wired: each constituent must show an
executable procedure failure path that (1) records the named channel,
(2) returns no k' with Verify=true, and (3) is therefore classified as
common F under the recovery_spec definition.

Scaffolding stubs alone are insufficient. Probability bounds, crypto
Verify, τ, and QUERY_MEMORY clearance remain out of scope.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .procedure_driver import FAILURE_RUNNERS, ScaffoldProcedure
from .scaffold_import import import_scaffold_modules


def _path_justification_checks(channel_id: str, outcome) -> Dict[str, Any]:
    """Checkable criteria for path_justified_on_scaffold."""
    channel_matches = outcome.channel == channel_id
    no_verify_true = outcome.verify_true_returned is False
    classified_F = outcome.classified_as_common_F is True
    failure_exit = outcome.exit_kind == "failure"
    channel_in_failures = channel_id in outcome.failures_recorded
    # F_verify false path records channel via procedure; fault path too.
    justified = (
        channel_matches
        and no_verify_true
        and classified_F
        and failure_exit
        and channel_in_failures
    )
    return {
        "channel_matches": channel_matches,
        "verify_true_returned": outcome.verify_true_returned,
        "classified_as_common_F": classified_F,
        "exit_kind": outcome.exit_kind,
        "channel_in_failures_recorded": channel_in_failures,
        "path_justified": justified,
    }


def probe_path_justified_inclusions() -> Dict[str, Any]:
    """Run success control + per-F_* failure paths; record inclusion status."""
    mods = import_scaffold_modules()
    proc = ScaffoldProcedure()

    success = proc.run_success_control()
    success_control = {
        "exit_kind": success.exit_kind,
        "verify_true_returned": success.verify_true_returned,
        "classified_as_common_F": success.classified_as_common_F,
        "k_prime_token": success.k_prime_token,
        "passed": (
            success.exit_kind == "success"
            and success.verify_true_returned is True
            and success.classified_as_common_F is False
        ),
        "note": (
            "Contrasting success path on no-crypto scaffold Verify; not a "
            "cryptographic body and not CollimationSieve."
        ),
    }

    # Extra F_verify fault path (second exercise for same constituent).
    fault_outcome = proc.run_fail_F_verify_fault()
    fault_checks = _path_justification_checks("F_verify", fault_outcome)

    constituents: List[Dict[str, Any]] = []
    for channel_id, method_name in FAILURE_RUNNERS.items():
        outcome = getattr(proc, method_name)()
        checks = _path_justification_checks(channel_id, outcome)
        if channel_id == "F_verify":
            # Require both false and fault paths for F_verify.
            checks["fault_path_justified"] = fault_checks["path_justified"]
            checks["path_justified"] = (
                checks["path_justified"] and fault_checks["path_justified"]
            )

        if checks["path_justified"]:
            status = "path_justified_on_scaffold"
            rationale = (
                f"Executable scaffold procedure path triggers {channel_id}, "
                "halts under symbolic stopping policy without Verify=true, "
                "and is classified as common F per recovery_spec. Still "
                "zero-compute / no crypto Verify body; not probability-"
                "composed union justification; not QUERY_MEMORY clearance."
            )
        else:
            status = "still_checklist_only"
            rationale = (
                f"Path justification checks failed for {channel_id}: {checks}"
            )

        entry: Dict[str, Any] = {
            "id": channel_id,
            "status": status,
            "rationale": rationale,
            "checks": checks,
            "outcome": {
                "exit_kind": outcome.exit_kind,
                "channel": outcome.channel,
                "classified_as_common_F": outcome.classified_as_common_F,
                "verify_true_returned": outcome.verify_true_returned,
                "failures_recorded": outcome.failures_recorded,
                "injection": outcome.notes.get("injection"),
                "recovery_spec_role": outcome.notes.get("recovery_spec_role"),
            },
            "scaffold_failure_path": {
                "procedure": f"ScaffoldProcedure.{method_name}",
                "events": outcome.events,
                "stopping_policy": outcome.stopping_policy,
            },
            "justified_by_implemented_end_to_end_crypto_path": False,
            "probability_bounds": False,
            "crypto_verify_body": False,
        }
        if channel_id == "F_stop":
            entry["tau_invented"] = bool(outcome.notes.get("tau_invented", False))
            entry["qm_stopping_cleared"] = bool(
                outcome.notes.get("qm_stopping_cleared", False)
            )
            entry["tau_invention_rejected"] = bool(
                outcome.notes.get("tau_invention_rejected", False)
            )
        if channel_id == "F_tail":
            entry["numeric_width_invented"] = bool(
                outcome.notes.get("numeric_width_invented", False)
            )
        if channel_id == "F_verify":
            entry["fault_path"] = {
                "checks": fault_checks,
                "events": fault_outcome.events,
                "injection": fault_outcome.notes.get("injection"),
            }
            entry["crypto_body"] = False
        constituents.append(entry)

    justified_ids = [
        c["id"] for c in constituents if c["status"] == "path_justified_on_scaffold"
    ]
    checklist_ids = [
        c["id"] for c in constituents if c["status"] == "still_checklist_only"
    ]
    blocked_ids = [
        c["id"] for c in constituents if c["status"] == "blocked_with_certificate"
    ]

    if justified_ids and not checklist_ids and not blocked_ids:
        union_status = "path_justified_on_scaffold_all_constituents"
        composition_status = "path_justified_partial"
    elif justified_ids:
        union_status = "path_justified_partial_union_incomplete"
        composition_status = "path_justified_partial"
    else:
        union_status = "still_checklist_only"
        composition_status = "fstar_composition_partial"

    return {
        "batch022_scaffold_import": mods["batch022_task_dir"],
        "common_event_F_definition": (
            "F = { the procedure fails to return a k' with Verify(x,k')=true "
            "within its declared stopping policy }"
        ),
        "path_justification_criterion": (
            "Named F_* channel recorded on an executable scaffold procedure "
            "path that returns no Verify=true k' under the symbolic stopping "
            "policy, hence classified_as_common_F. Stubs alone insufficient. "
            "Not crypto end-to-end; not probability bounds; not τ."
        ),
        "success_control": success_control,
        "constituents": constituents,
        "required_union": {
            "expression": (
                "F_input ∪ F_oracle ∪ F_cleanup ∪ F_stop ∪ F_recovery ∪ "
                "F_tail ∪ F_verify ⊆ F"
            ),
            "status": union_status,
            "path_justified_constituents": justified_ids,
            "still_checklist_only_constituents": checklist_ids,
            "blocked_constituents": blocked_ids,
            "probability_composition": False,
            "dependency_assumptions_identified": [
                "scaffold_no_crypto_Verify_token_semantics",
                "symbolic_stopping_policy_halt_without_verify_true",
            ],
            "note": (
                "Per-constituent scaffold path justification advances beyond "
                "BATCH-023 checklist_only_not_justified. Union probability "
                "composition, crypto Verify, and CollimationSieve end-to-end "
                "paths remain absent. Not QUERY_MEMORY / QM-ERROR clearance."
            ),
        },
        "summary": {
            "composition_status": composition_status,
            "success_control_passed": success_control["passed"],
            "all_constituents_path_justified_on_scaffold": (
                len(justified_ids) == 7 and not checklist_ids and not blocked_ids
            ),
            "any_still_checklist_only": bool(checklist_ids),
            "tau_invented": False,
            "qm_stopping_cleared": False,
            "qm_error_cleared": False,
            "query_memory_cleared": False,
            "crypto_verify_implemented": False,
            "curve_isogeny_quantum_circuit_compute": False,
        },
    }
