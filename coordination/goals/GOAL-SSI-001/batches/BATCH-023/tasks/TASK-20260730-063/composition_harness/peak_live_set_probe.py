"""Probe stage live-set membership and peak-as-max (no numeric widths)."""

from __future__ import annotations

from typing import Any, Dict, List, Set

from .scaffold_import import import_scaffold_modules


RECOVERY_SPEC_STAGES = (
    "preparation",
    "sieve_attempt",
    "recovery",
    "tail_verification",
)


def probe_peak_live_sets() -> Dict[str, Any]:
    """Walk stages with BATCH-022 StageLiveSetTracker; peak = max, not sum."""
    mods = import_scaffold_modules()
    STAGE_LIVE_SETS = mods["state_machine"].STAGE_LIVE_SETS
    StageLiveSetTracker = mods["state_machine"].StageLiveSetTracker
    LifetimeRegistry = mods["lifetime_hooks"].LifetimeRegistry
    PublicInstance = mods["types"].PublicInstance
    CleanupResult = mods["types"].CleanupResult
    CandidateSecret = mods["types"].CandidateSecret
    Verify = mods["verify"].Verify

    # Checklist agreement with recovery_spec / BATCH-017 / BATCH-021
    expected = {
        "preparation": {"B_input", "B_attempt", "W_label", "R_label"},
        "sieve_attempt": {"B_input", "B_attempt", "W_sieve", "R_sieve", "B_sieve"},
        "recovery": {
            "B_input",
            "B_attempt",
            "B_post",
            "B_recovery",
            "accepted_transcript",
        },
        "tail_verification": {
            "B_input",
            "B_attempt",
            "B_recovery",
            "M_tail",
            "B_candidate",
        },
    }
    checklist_match = all(STAGE_LIVE_SETS[s] == expected[s] for s in RECOVERY_SPEC_STAGES)

    stage_records: List[Dict[str, Any]] = []
    symbolic_cardinalities: Dict[str, int] = {}

    # --- preparation stage membership ---
    reg = LifetimeRegistry()
    tracker: StageLiveSetTracker = reg.tracker
    x = PublicInstance(token="x-peak", scaffold_accept_token="k*")
    reg.birth_B_input(x)
    reg.birth_B_attempt({"attempts_symbolic": True})
    w_l = reg.birth_W_label(x, {"ctx": 1})
    r_l = reg.birth_R_label(x, {"ctx": 1}, {"addr": "symbolic"})
    prep_ok = tracker.live_subset_of_stage("preparation") and tracker.required_members_present(
        "preparation", expected["preparation"]
    )
    symbolic_cardinalities["preparation"] = len(tracker.live)
    stage_records.append(
        {
            "stage": "preparation",
            "checklist_members": sorted(expected["preparation"]),
            "observed_live": sorted(tracker.live),
            "symbolic_membership_check_supported": True,
            "live_subset_of_stage": tracker.live_subset_of_stage("preparation"),
            "required_members_present": tracker.required_members_present(
                "preparation", expected["preparation"]
            ),
            "stage_check_passed": prep_ok,
            "numeric_widths": "not_invented",
        }
    )

    # cleanup preparation W/R before sieve
    reg.last_use_W_label(w_l)
    assert reg.cleanup_W_label(w_l) == CleanupResult.ok
    reg.destroy_W_label(w_l)
    reg.last_use_R_label(r_l)
    assert reg.cleanup_R_label(r_l) == CleanupResult.ok
    reg.destroy_R_label(r_l)

    # --- sieve_attempt ---
    w_s = reg.birth_W_sieve({"attempt": 0})
    r_s = reg.birth_R_sieve({"attempt": 0}, {"addr": "symbolic"})
    b_s = reg.birth_B_sieve({"attempt": 0})
    sieve_ok = tracker.live_subset_of_stage("sieve_attempt") and tracker.required_members_present(
        "sieve_attempt", expected["sieve_attempt"]
    )
    symbolic_cardinalities["sieve_attempt"] = len(tracker.live)
    stage_records.append(
        {
            "stage": "sieve_attempt",
            "checklist_members": sorted(expected["sieve_attempt"]),
            "observed_live": sorted(tracker.live),
            "symbolic_membership_check_supported": True,
            "live_subset_of_stage": tracker.live_subset_of_stage("sieve_attempt"),
            "required_members_present": tracker.required_members_present(
                "sieve_attempt", expected["sieve_attempt"]
            ),
            "stage_check_passed": sieve_ok,
            "numeric_widths": "not_invented",
        }
    )

    for h, cfn, dfn in (
        (w_s, lambda h: reg.cleanup_W_sieve(h, "accept"), reg.destroy_W_sieve),
        (r_s, lambda h: reg.cleanup_R_sieve(h, "accept"), reg.destroy_R_sieve),
        (b_s, lambda h: reg.cleanup_B_sieve(h, "accept"), reg.destroy_B_sieve),
    ):
        assert cfn(h) == CleanupResult.ok
        dfn(h)

    # --- recovery ---
    t = reg.birth_accepted_transcript({"accepted": True})
    b_post = reg.birth_B_post(t)
    b_rec = reg.birth_B_recovery(b_post, t)
    rec_ok = tracker.live_subset_of_stage("recovery") and tracker.required_members_present(
        "recovery", expected["recovery"]
    )
    symbolic_cardinalities["recovery"] = len(tracker.live)
    stage_records.append(
        {
            "stage": "recovery",
            "checklist_members": sorted(expected["recovery"]),
            "observed_live": sorted(tracker.live),
            "symbolic_membership_check_supported": True,
            "live_subset_of_stage": tracker.live_subset_of_stage("recovery"),
            "required_members_present": tracker.required_members_present(
                "recovery", expected["recovery"]
            ),
            "stage_check_passed": rec_ok,
            "numeric_widths": "not_invented",
        }
    )

    # Destroy B_post and accepted_transcript before tail (not in tail live set)
    assert reg.cleanup_B_post(b_post) == CleanupResult.ok
    reg.destroy_B_post(b_post)
    assert reg.cleanup_accepted_transcript(t) == CleanupResult.ok
    reg.destroy_accepted_transcript(t)

    # --- tail_verification ---
    m = reg.birth_M_tail(
        b_rec,
        width_decl={"unit": "symbolic_deferred"},
        enumeration_order_decl={"order": "symbolic"},
        stopping_rule_decl={"invents_tau": False, "rule": "symbolic_open"},
        shares_B_recovery_decl=True,
    )
    cand = reg.birth_B_candidate(m)
    tail_ok = tracker.live_subset_of_stage(
        "tail_verification"
    ) and tracker.required_members_present("tail_verification", expected["tail_verification"])
    symbolic_cardinalities["tail_verification"] = len(tracker.live)
    stage_records.append(
        {
            "stage": "tail_verification",
            "checklist_members": sorted(expected["tail_verification"]),
            "observed_live": sorted(tracker.live),
            "symbolic_membership_check_supported": True,
            "live_subset_of_stage": tracker.live_subset_of_stage("tail_verification"),
            "required_members_present": tracker.required_members_present(
                "tail_verification", expected["tail_verification"]
            ),
            "stage_check_passed": tail_ok,
            "numeric_widths": "not_invented",
        }
    )

    # Synthetic verify only (no crypto); retain record for cleanup discipline
    assert Verify(x, CandidateSecret(token="k*")) is True
    reg.retain_final_verification_record()

    # Peak = max over stage symbolic cardinalities, NOT sum
    peak_value = max(symbolic_cardinalities.values())
    peak_stages = [s for s, c in symbolic_cardinalities.items() if c == peak_value]
    sum_if_mistaken = sum(symbolic_cardinalities.values())

    api_support = {
        "StageLiveSetTracker_class": True,
        "STAGE_LIVE_SETS_checklist": checklist_match,
        "live_subset_of_stage": hasattr(StageLiveSetTracker, "live_subset_of_stage"),
        "required_members_present": hasattr(StageLiveSetTracker, "required_members_present"),
        "peak_accounting_note_method": hasattr(StageLiveSetTracker, "peak_accounting_note"),
        "numeric_widths_supported": False,
        "peak_byte_bound_supported": False,
    }

    return {
        "batch022_scaffold_import": mods["batch022_task_dir"],
        "recovery_spec_peak_rule": "max_over_named_stage_live_sets_not_sum",
        "stage_live_sets_checklist_matches_recovery_spec": checklist_match,
        "stages": stage_records,
        "symbolic_stage_cardinalities_object_count_not_bytes": symbolic_cardinalities,
        "peak": {
            "definition": "max(symbolic_stage_cardinalities), not sum",
            "peak_symbolic_object_count": peak_value,
            "peak_stages": peak_stages,
            "mistaken_sum_of_stage_counts": sum_if_mistaken,
            "mistaken_sum_rejected_as_peak": True,
            "numeric_widths": "not_invented",
            "peak_byte_bound": "unresolved",
            "note": (
                "Object-count max is a checklist accounting device only; it is "
                "not a memory-width or QUERY_MEMORY bound."
            ),
        },
        "scaffold_api_support": api_support,
        "summary": {
            "all_stage_membership_checks_passed": all(s["stage_check_passed"] for s in stage_records),
            "symbolic_membership_checks_supported": True,
            "numeric_widths_invented": False,
            "qm_memory_map_cleared": False,
            "peak_liveset_status": "peak_liveset_partial",
        },
    }
