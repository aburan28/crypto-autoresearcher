#!/usr/bin/env python3
# gate0x_cmp.py -- TASK-20260901-579808 (BATCH-ace664, GOAL-AES-003)
#
# GATE-0 EXTENDED REBUILD (P2, BLOCKING; IDEA-20260901-f8294e PR-P3):
# field-by-field comparison of the cap-256 derivative receipt against the
# committed immutable receipt L1-AES-R5-P30 (BATCH-015 TASK-20260805-d408ac),
# PLUS identity of the derivative-added deterministic fields against the
# committed G3 receipt of BATCH-5ed9a3 (same seat, cap-64 build).
#
# Extended allowed-diff list EXACTLY (PREREGISTRATION.md section 7):
#   {arm, probe, oracle, elapsed_seconds_measured,
#    measured_rate_trials_per_sec, hit_log_cap}
# where hit_log_cap (64 -> 256) is the single NEW allowed diff of this record.
# Fields the derivative ADDS vs L1 (recorded informationally, never failures):
#   the Stage-0 set + the BATCH-5ed9a3 extension (see KNOWN_ADDED).
# G3 identity requirements (gate-failing): hit_e_detail identical (14 records),
#   ezdiag_*/ezoff_* identical, hit_trials identical, hit_log_overflow == 0 on
#   both sides, and ALL other shared fields identical except {arm,
#   elapsed_seconds_measured, measured_rate_trials_per_sec, hit_log_cap}.
# Any committed field missing, any non-allowed field differing, any unexpected
# added field, or any G3-identity failure -> FAIL (exit 5) -> HALT as
# FX5-P/invalid_measurement (rule 5).
#
# usage: python3 src/gate0x_cmp.py <new_receipt.json> <committed_L1.json> <committed_G3.json> <out.json>
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL session model
# under inference amendment DEC-20260831-0d1eeb); fallback_used true;
# model_verified false; degraded_requirements [];
# amendment DEC-20260831-0d1eeb;
# standing_basis 0137a051eb5828789eb267fa83c8278086578d4c.
import json, sys, datetime

INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
    "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
}
ALLOWED_DIFF = {"arm", "probe", "oracle", "elapsed_seconds_measured",
                "measured_rate_trials_per_sec",
                # single NEW allowed diff of IDEA-20260901-f8294e (cap delta):
                "hit_log_cap"}
KNOWN_ADDED = {"zhist", "sbox_table_hex", "key_hex", "sbox", "sbox_k",
               "sbox_positions", "sbox_bijective", "arm_table_concat_sha256",
               "ewhist_all", "ewhist_miss",
               "ewhist_hit", "ewbithist_all", "ewbithist_miss", "ewbithist_hit",
               "hit_e_detail",
               "ezdiag_all", "ezdiag_miss", "ezdiag_hit",
               "ezoff_all", "ezoff_miss", "ezoff_hit"}
G3_ALLOW_DIFF = {"arm", "elapsed_seconds_measured", "measured_rate_trials_per_sec",
                 "hit_log_cap"}


def main():
    new_path, l1_path, g3_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    with open(new_path) as f:
        new = json.load(f)
    with open(l1_path) as f:
        committed = json.load(f)
    with open(g3_path) as f:
        g3 = json.load(f)

    missing, mismatched, allowed_diffs, matched = [], [], [], []
    for field, cval in committed.items():
        if field not in new:
            missing.append(field)
            continue
        nval = new[field]
        if field in ALLOWED_DIFF:
            allowed_diffs.append({"field": field, "committed": cval, "new": nval})
        elif nval == cval:
            matched.append(field)
        else:
            mismatched.append({"field": field, "committed": cval, "new": nval})
    added = sorted(set(new.keys()) - set(committed.keys()))
    unexpected_added = sorted(set(added) - KNOWN_ADDED)
    hit_indices_ok = new.get("hit_trials") == committed.get("hit_trials")
    cap_is_256 = new.get("hit_log_cap") == 256

    g3_mismatched, g3_matched, g3_allowed = [], [], []
    for field, gval in g3.items():
        if field not in new:
            g3_mismatched.append({"field": field, "g3": gval, "new": "<missing>"})
            continue
        nval = new[field]
        if field in G3_ALLOW_DIFF:
            g3_allowed.append({"field": field, "g3": gval, "new": nval})
        elif nval == gval:
            g3_matched.append(field)
        else:
            g3_mismatched.append({"field": field, "g3": gval, "new": nval})
    g3_identity_checks = {
        "hit_e_detail_identical_14_records": (
            new.get("hit_e_detail") == g3.get("hit_e_detail")
            and len(g3.get("hit_e_detail", [])) == 14),
        "ez_counters_identical": all(
            new.get(k) == g3.get(k) for k in
            ("ezdiag_all", "ezdiag_miss", "ezdiag_hit",
             "ezoff_all", "ezoff_miss", "ezoff_hit")),
        "hit_trials_identical": new.get("hit_trials") == g3.get("hit_trials"),
        "hit_log_overflow_zero_both": new.get("hit_log_overflow") == 0
                                     and g3.get("hit_log_overflow") == 0,
        "all_other_shared_fields_identical": not g3_mismatched,
    }
    g3_ok = all(g3_identity_checks.values())

    gate_pass = (not missing) and (not mismatched) and (not unexpected_added) \
        and hit_indices_ok and cap_is_256 and g3_ok
    out = {
        "schema": "crypto.autoresearch.gate0x_cmp.v2",
        "task_id": "TASK-20260901-579808",
        "idea_record": "IDEA-20260901-f8294e",
        "gate": "GATE-0 EXTENDED REBUILD (cap-256 non-perturbation, BLOCKING)",
        "new_receipt": new_path,
        "committed_L1_receipt": l1_path,
        "committed_G3_receipt": g3_path,
        "allowed_diff_list_extended": sorted(ALLOWED_DIFF),
        "new_allowed_diff_this_record": ["hit_log_cap"],
        "added_fields_preregistered_set": sorted(KNOWN_ADDED),
        "matched_fields_identical_vs_L1": matched,
        "allowed_diffs_observed_vs_L1": allowed_diffs,
        "missing_committed_fields": missing,
        "mismatched_fields_vs_L1": mismatched,
        "added_fields_observed": added,
        "added_fields_unexpected": unexpected_added,
        "n_hit_indices_committed": len(committed.get("hit_trials", [])),
        "n_hit_indices_new": len(new.get("hit_trials", [])),
        "all_hit_indices_identical_vs_L1": hit_indices_ok,
        "hit_log_cap_new_is_256": cap_is_256,
        "g3_identity_checks": g3_identity_checks,
        "g3_matched_fields": g3_matched,
        "g3_allowed_diffs_observed": g3_allowed,
        "g3_mismatched_fields": g3_mismatched,
        "gate0_pass": gate_pass,
        "on_failure": "HALT as FX5-P/invalid_measurement (rule 5); no further arms; honest report",
        "compared_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": ("this file is machine-generated JSON; parsed whole with python3 "
                              "json.load (all three inputs and this output) before task completion"),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"gate0_pass": gate_pass, "missing": missing,
                      "mismatched_vs_L1": [m["field"] for m in mismatched],
                      "unexpected_added": unexpected_added,
                      "hits_identical_vs_L1": hit_indices_ok,
                      "cap_is_256": cap_is_256,
                      "g3_ok": g3_ok,
                      "g3_mismatched": [m["field"] for m in g3_mismatched]}, indent=1))
    sys.exit(0 if gate_pass else 5)


if __name__ == "__main__":
    main()
