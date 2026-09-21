"""Probe BATCH-022 scaffold F_* channel wiring (no probability / no clearance)."""

from __future__ import annotations

from typing import Any, Dict, List

from .scaffold_import import import_scaffold_modules


def _prep_registry(mods):
    LifetimeRegistry = mods["lifetime_hooks"].LifetimeRegistry
    PublicInstance = mods["types"].PublicInstance
    reg = LifetimeRegistry()
    x = PublicInstance(token="x-comp", scaffold_accept_token="k*")
    reg.birth_B_input(x)
    reg.birth_B_attempt({"attempts_symbolic": True})
    return reg, x


def _path_to_recovery(reg, mods):
    """Minimal accept path to B_recovery (destroys W/R sieve)."""
    CleanupResult = mods["types"].CleanupResult
    w_s = reg.birth_W_sieve({"attempt": 0})
    r_s = reg.birth_R_sieve({"attempt": 0}, {"addr": "symbolic"})
    b_s = reg.birth_B_sieve({"attempt": 0})
    assert reg.cleanup_W_sieve(w_s, "accept") == CleanupResult.ok
    assert reg.cleanup_R_sieve(r_s, "accept") == CleanupResult.ok
    assert reg.cleanup_B_sieve(b_s, "accept") == CleanupResult.ok
    reg.destroy_W_sieve(w_s)
    reg.destroy_R_sieve(r_s)
    reg.destroy_B_sieve(b_s)
    t = reg.birth_accepted_transcript({"accepted": True})
    b_post = reg.birth_B_post(t)
    b_rec = reg.birth_B_recovery(b_post, t)
    return t, b_post, b_rec


def probe_f_star_channels() -> Dict[str, Any]:
    """Exercise each named FailureChannel stub; record wiring honesty."""
    mods = import_scaffold_modules()
    FailureChannel = mods["types"].FailureChannel
    LifetimeError = mods["lifetime_hooks"].LifetimeError
    LifetimeRegistry = mods["lifetime_hooks"].LifetimeRegistry
    PublicInstance = mods["types"].PublicInstance
    CandidateSecret = mods["types"].CandidateSecret
    CleanupResult = mods["types"].CleanupResult
    Verify = mods["verify"].Verify
    VerificationFault = mods["verify"].VerificationFault
    classify_verify_outcome = mods["verify"].classify_verify_outcome

    named_channels = [c.value for c in FailureChannel if c.value != "F"]
    results: List[Dict[str, Any]] = []

    # F_input
    reg = LifetimeRegistry()
    try:
        reg.birth_B_input(PublicInstance(token="bad", well_formed=False))
        wired = False
        detail = "expected LifetimeError"
    except LifetimeError as e:
        wired = FailureChannel.F_input in reg.failures and e.channel == FailureChannel.F_input
        detail = "malformed_x_raises_F_input"
    results.append(
        {
            "id": "F_input",
            "scaffold_channel_wired": wired,
            "exercise": detail,
            "inclusion_into_common_F": "checklist_only_not_justified",
            "verify_involved": False,
        }
    )

    # F_oracle — cleanup_W_label when handle is already cleaned maps F_oracle
    HandleState = mods["types"].HandleState
    reg, x = _prep_registry(mods)
    w = reg.birth_W_label(x, {"ctx": 1})
    w.mark(HandleState.cleaned)
    cr = reg.cleanup_W_label(w)
    wired = (
        cr == CleanupResult.cleanup_failure
        and FailureChannel.F_oracle in reg.failures
    )
    results.append(
        {
            "id": "F_oracle",
            "scaffold_channel_wired": wired,
            "exercise": "cleanup_W_label_on_non_live_maps_F_oracle",
            "inclusion_into_common_F": "checklist_only_not_justified",
            "verify_involved": False,
        }
    )

    # F_cleanup — destroy before cleanup
    reg, x = _prep_registry(mods)
    w = reg.birth_W_label(x, {})
    try:
        reg.destroy_W_label(w)
        wired = False
        detail = "expected LifetimeError"
    except LifetimeError as e:
        wired = e.channel == FailureChannel.F_cleanup
        detail = "destroy_before_cleanup_maps_F_cleanup"
    results.append(
        {
            "id": "F_cleanup",
            "scaffold_channel_wired": wired,
            "exercise": detail,
            "inclusion_into_common_F": "checklist_only_not_justified",
            "verify_involved": False,
        }
    )

    # F_stop — named stub; τ invention rejected as F_stop
    reg, x = _prep_registry(mods)
    ch = reg.note_stopping_breach()
    wired_note = ch == FailureChannel.F_stop and FailureChannel.F_stop in reg.failures
    t, b_post, b_rec = _path_to_recovery(reg, mods)
    tau_rejected = False
    try:
        reg.birth_M_tail(
            b_rec,
            width_decl={"unit": "symbolic"},
            enumeration_order_decl={},
            stopping_rule_decl={"invents_tau": True},
            shares_B_recovery_decl=False,
        )
    except LifetimeError as e:
        tau_rejected = e.channel == FailureChannel.F_stop
    results.append(
        {
            "id": "F_stop",
            "scaffold_channel_wired": wired_note and tau_rejected,
            "exercise": "note_stopping_breach_and_tau_invention_rejected",
            "inclusion_into_common_F": "checklist_only_not_justified",
            "verify_involved": False,
            "tau_invented": False,
            "qm_stopping_cleared": False,
        }
    )

    # F_recovery — B_post while W_sieve still live
    reg, x = _prep_registry(mods)
    reg.birth_W_sieve({})
    reg.birth_R_sieve({}, {})
    t = reg.birth_accepted_transcript({})
    try:
        reg.birth_B_post(t)
        wired = False
        detail = "expected LifetimeError"
    except LifetimeError as e:
        wired = (
            e.channel == FailureChannel.F_recovery
            and FailureChannel.F_recovery in reg.failures
        )
        detail = "B_post_precondition_W_sieve_not_destroyed_maps_F_recovery"
    results.append(
        {
            "id": "F_recovery",
            "scaffold_channel_wired": wired,
            "exercise": detail,
            "inclusion_into_common_F": "checklist_only_not_justified",
            "verify_involved": False,
        }
    )

    # F_tail — note_tail_exhaustion + numeric_width forbidden
    reg, x = _prep_registry(mods)
    t, b_post, b_rec = _path_to_recovery(reg, mods)
    ch = reg.note_tail_exhaustion()
    wired_note = ch == FailureChannel.F_tail
    numeric_rejected = False
    try:
        reg.birth_M_tail(
            b_rec,
            width_decl={"numeric_width": 128},
            enumeration_order_decl={},
            stopping_rule_decl={"invents_tau": False},
            shares_B_recovery_decl=False,
        )
    except LifetimeError as e:
        numeric_rejected = e.channel == FailureChannel.F_tail
    results.append(
        {
            "id": "F_tail",
            "scaffold_channel_wired": wired_note and numeric_rejected,
            "exercise": "note_tail_exhaustion_and_numeric_width_forbidden",
            "inclusion_into_common_F": "checklist_only_not_justified",
            "verify_involved": False,
            "numeric_width_invented": False,
        }
    )

    # F_verify — false and fault paths (no-crypto)
    x_ok = PublicInstance(token="x0", scaffold_accept_token="k-accept")
    false_maps = classify_verify_outcome(Verify(x_ok, CandidateSecret(token="other")))
    try:
        Verify(PublicInstance(token="x0", well_formed=False), CandidateSecret(token="k"))
        fault_maps = False
    except VerificationFault:
        fault_maps = True
    results.append(
        {
            "id": "F_verify",
            "scaffold_channel_wired": false_maps == FailureChannel.F_verify and fault_maps,
            "exercise": "no_crypto_Verify_false_and_fault_map_F_verify",
            "inclusion_into_common_F": "checklist_only_not_justified",
            "verify_involved": True,
            "crypto_body": False,
        }
    )

    enum_has_common_F = any(c.value == "F" for c in FailureChannel)
    f_sim_in_enum = any(c.value == "F_sim" for c in FailureChannel)

    return {
        "batch022_scaffold_import": mods["batch022_task_dir"],
        "named_failure_channels_in_scaffold_enum": named_channels,
        "common_F_enum_present": enum_has_common_F,
        "constituents": results,
        "required_union_checklist": {
            "expression": (
                "F_input ∪ F_oracle ∪ F_cleanup ∪ F_stop ∪ F_recovery ∪ "
                "F_tail ∪ F_verify ⊆ F"
            ),
            "status": "scaffold_channels_wired_inclusion_still_checklist_only",
            "any_constituent_inclusion_justified": False,
            "note": (
                "BATCH-022 wires FailureChannel stubs and exercisable maps; "
                "recovery_spec union ⊆ F remains unjustified without end-to-end "
                "Verify-relative stopping and probability composition."
            ),
        },
        "f_sim": {
            "present_in_scaffold_FailureChannel_enum": f_sim_in_enum,
            "maps_to_F": False,
            "map_status": "no_implementation_derived_implication",
            "note": (
                "F_sim remains BATCH-012 report-only simulator event; scaffold "
                "does not define F_sim or an F_sim→F implication. Honesty retained."
            ),
        },
        "summary": {
            "all_recovery_spec_constituents_channel_wired": all(
                r["scaffold_channel_wired"] for r in results
            ),
            "any_inclusion_into_common_F_justified": False,
            "f_sim_to_F_map_exists": False,
            "tau_invented": False,
            "qm_error_cleared": False,
            "composition_status": "fstar_composition_partial",
        },
    }
