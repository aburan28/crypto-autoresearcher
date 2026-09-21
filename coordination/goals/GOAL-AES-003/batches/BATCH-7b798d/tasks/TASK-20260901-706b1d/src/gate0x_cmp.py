#!/usr/bin/env python3
# gate0x_cmp.py -- TASK-20260901-706b1d (BATCH-7b798d, GOAL-AES-003)
#
# GATE-0X REBUILD (S0-4, BLOCKING; IDEA-20260901-582ea9 PR-S6):
# field-by-field comparison of the PIN-T0 widened cap-256 receipt against
#   (a) the CERTIFIED Gate-0x rebuild receipt P2_gate0x.json of BATCH-ace664
#       TASK-20260901-579808 (itself the field-exact cap-256 rebuild of the
#       committed immutable L1-AES-R5-P30 receipt, gate0_pass true there) --
#       PRIMARY reference; and
#   (b) the committed immutable L1-AES-R5-P30 receipt of BATCH-015
#       TASK-20260805-d408ac -- continuity reference (the committed 14-hit
#       reading).
#
# EXTENDED ALLOWED-DIFF LIST EXACTLY (PREREGISTRATION.md section 6):
#   value-difference allowed list (inherited from the BATCH-ace664 Gate-0x
#   convention):
#     {arm, probe, oracle, elapsed_seconds_measured,
#      measured_rate_trials_per_sec, hit_log_cap}
#     (hit_log_cap is 256 on both sides; carried for convention continuity)
#   additive allowed list (fields this build ADDS vs the references --
#   pin label + interior-surface declaration ONLY, pinned values):
#     {schedule_pin == "PIN-T0", schedule_pin_position == 0,
#      schedule_pin_decision == "DEC-20260901-fb6f11"}
# Every other field MUST be identical. Any committed field missing, any
# non-allowed field differing, any unexpected added field, or any
# identity-check failure -> FAIL (exit 5) -> HALT as SH-GATE-FAIL
# (invalid_measurement, rule 5).
#
# usage: python3 src/gate0x_cmp.py <new_receipt.json> <ace664_P2_receipt.json> <committed_L1.json> <out.json>
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (session-reported; no
# adapter probe run in this session); fallback_used true; model_verified
# false; degraded_requirements []; amendment DEC-20260831-0d1eeb.
import json, sys, datetime

INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "resolved_model_id_note": "session-reported; no adapter probe run in this session",
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
}
ALLOWED_DIFF = {"arm", "probe", "oracle", "elapsed_seconds_measured",
                "measured_rate_trials_per_sec",
                # carried from the BATCH-ace664 Gate-0x convention; 256 on
                # both sides in this task (value-equal, kept for continuity):
                "hit_log_cap"}
PIN_LABEL_ADDED = {"schedule_pin", "schedule_pin_position",
                   "schedule_pin_decision"}
PIN_LABEL_EXPECTED = {"schedule_pin": "PIN-T0", "schedule_pin_position": 0,
                      "schedule_pin_decision": "DEC-20260901-fb6f11"}
# fields the cap-256 lineage build ADDED vs L1 (preregistered in the lineage;
# carried unchanged through the BATCH-ace664 P2 receipt):
KNOWN_ADDED = {"zhist", "sbox_table_hex", "key_hex", "sbox", "sbox_k",
               "sbox_positions", "sbox_bijective", "arm_table_concat_sha256",
               "ewhist_all", "ewhist_miss",
               "ewhist_hit", "ewbithist_all", "ewbithist_miss", "ewbithist_hit",
               "hit_e_detail",
               "ezdiag_all", "ezdiag_miss", "ezdiag_hit",
               "ezoff_all", "ezoff_miss", "ezoff_hit"}
EXPECTED_HITS = 14   # committed L1-AES-R5-P30 reading, continuity check


def compare(ref, new, allowed):
    missing, mismatched, allowed_diffs, matched = [], [], [], []
    for field, rval in ref.items():
        if field not in new:
            missing.append(field)
            continue
        nval = new[field]
        if field in allowed:
            allowed_diffs.append({"field": field, "ref": rval, "new": nval})
        elif nval == rval:
            matched.append(field)
        else:
            mismatched.append({"field": field, "ref": rval, "new": nval})
    return missing, mismatched, allowed_diffs, matched


def main():
    new_path, p2_path, l1_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    with open(new_path) as f:
        new = json.load(f)
    with open(p2_path) as f:
        p2 = json.load(f)
    with open(l1_path) as f:
        l1 = json.load(f)

    # ---- primary: identity vs the certified cap-256 P2 receipt ----
    p2_missing, p2_mismatched, p2_allowed, p2_matched = compare(p2, new, ALLOWED_DIFF)
    p2_added = sorted(set(new.keys()) - set(p2.keys()))
    p2_unexpected_added = sorted(set(p2_added) - PIN_LABEL_ADDED)
    pin_label_ok = all(new.get(k) == v for k, v in PIN_LABEL_EXPECTED.items())

    # ---- continuity: identity vs the committed L1 receipt ----
    l1_missing, l1_mismatched, l1_allowed, l1_matched = compare(l1, new, ALLOWED_DIFF)
    l1_added = sorted(set(new.keys()) - set(l1.keys()))
    l1_unexpected_added = sorted(set(l1_added) - (KNOWN_ADDED | PIN_LABEL_ADDED))

    identity_checks = {
        "hit_trials_identical_vs_P2": new.get("hit_trials") == p2.get("hit_trials"),
        "hit_e_detail_identical_vs_P2_14_records": (
            new.get("hit_e_detail") == p2.get("hit_e_detail")
            and len(p2.get("hit_e_detail", [])) == EXPECTED_HITS),
        "ez_counters_identical_vs_P2": all(
            new.get(k) == p2.get(k) for k in
            ("ezdiag_all", "ezdiag_miss", "ezdiag_hit",
             "ezoff_all", "ezoff_miss", "ezoff_hit")),
        "hit_log_overflow_zero_both": new.get("hit_log_overflow") == 0
                                      and p2.get("hit_log_overflow") == 0,
        "hit_log_cap_new_is_256": new.get("hit_log_cap") == 256,
        "w_ge1_continuity_14": new.get("W_ge1_nontrivial") == EXPECTED_HITS
                               and p2.get("W_ge1_nontrivial") == EXPECTED_HITS
                               and l1.get("W_ge1_nontrivial") == EXPECTED_HITS,
        "pin_label_fields_pinned_values": pin_label_ok,
    }
    gate_pass = (
        not p2_missing and not p2_mismatched and not p2_unexpected_added
        and not l1_missing and not l1_mismatched and not l1_unexpected_added
        and all(identity_checks.values()))
    out = {
        "schema": "crypto.autoresearch.gate0x_cmp.v3",
        "task_id": "TASK-20260901-706b1d",
        "idea_record": "IDEA-20260901-582ea9",
        "pin_decision": "DEC-20260901-fb6f11",
        "gate": "GATE-0X REBUILD (PIN-T0 widening non-perturbation, BLOCKING)",
        "new_receipt": new_path,
        "certified_P2_receipt_ace664": p2_path,
        "committed_L1_receipt": l1_path,
        "allowed_diff_list_value": sorted(ALLOWED_DIFF),
        "allowed_diff_list_additive_pin_label": sorted(PIN_LABEL_ADDED),
        "pin_label_expected_values": PIN_LABEL_EXPECTED,
        "added_fields_preregistered_set_vs_L1": sorted(KNOWN_ADDED | PIN_LABEL_ADDED),
        "vs_P2_matched_fields_identical": p2_matched,
        "vs_P2_allowed_diffs_observed": p2_allowed,
        "vs_P2_missing_fields": p2_missing,
        "vs_P2_mismatched_fields": p2_mismatched,
        "vs_P2_added_fields_observed": p2_added,
        "vs_P2_added_fields_unexpected": p2_unexpected_added,
        "vs_L1_matched_fields_identical": l1_matched,
        "vs_L1_allowed_diffs_observed": l1_allowed,
        "vs_L1_missing_fields": l1_missing,
        "vs_L1_mismatched_fields": l1_mismatched,
        "vs_L1_added_fields_observed": l1_added,
        "vs_L1_added_fields_unexpected": l1_unexpected_added,
        "identity_checks": identity_checks,
        "gate0x_pass": gate_pass,
        "on_failure": "HALT as SH-GATE-FAIL/invalid_measurement (rule 5); no further arms; honest report",
        "compared_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": ("this file is machine-generated JSON; parsed whole with python3 "
                              "json.load (all three inputs and this output) before task completion"),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"gate0x_pass": gate_pass,
                      "vs_P2_missing": p2_missing,
                      "vs_P2_mismatched": [m["field"] for m in p2_mismatched],
                      "vs_P2_unexpected_added": p2_unexpected_added,
                      "vs_L1_missing": l1_missing,
                      "vs_L1_mismatched": [m["field"] for m in l1_mismatched],
                      "vs_L1_unexpected_added": l1_unexpected_added,
                      "identity_checks": identity_checks}, indent=1))
    sys.exit(0 if gate_pass else 5)


if __name__ == "__main__":
    main()
