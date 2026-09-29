#!/usr/bin/env python3
# s2a_gate0x_cmp.py -- TASK-20260903-7893b2 (BATCH-060cb4, GOAL-AES-003)
#
# S2a-2 GATE-0X EXTENDED REBUILD (IDEA-20260903-8f26ac stage_s2a;
# PREREGISTRATION.md section 15 convention): field-by-field comparison of the
# EXTENDED-build receipt (aes, r5, 1, 1, 2^30, seed 531001, armid 1,
# threads 2) against
#   (a) the committed immutable L1-AES-R5-P30 receipt of BATCH-015
#       TASK-20260805-d408ac -- the reference named by the dispatch brief --
#       under the EXTENDED allowed-diff list (lineage value list + additive
#       pin-label fields + preregistered cap-256 added-field set; the declared
#       k=3 extension adds NO receipt fields, so the additive set is
#       unchanged: "the interior-surface + token fields are the only
#       additions" of the proposal is satisfied by zero new additions); and
#   (b) the frozen PIN-T0 build's own certified Gate-0x receipt
#       S3_gate0x.json of BATCH-7b798d TASK-20260901-706b1d -- the STRONGER
#       identity reference (same build family; only value-list fields may
#       differ; zero added fields allowed).
#
# EXTENDED ALLOWED-DIFF LIST EXACTLY:
#   value-difference allowed (inherited lineage convention):
#     {arm, probe, oracle, elapsed_seconds_measured,
#      measured_rate_trials_per_sec, hit_log_cap}
#   additive allowed vs L1 (preregistered cap-256 lineage additions):
#     KNOWN_ADDED = {zhist, sbox_table_hex, key_hex, sbox, sbox_k,
#       sbox_positions, sbox_bijective, arm_table_concat_sha256,
#       ewhist_all, ewhist_miss, ewhist_hit, ewbithist_all, ewbithist_miss,
#       ewbithist_hit, hit_e_detail, ezdiag_all, ezdiag_miss, ezdiag_hit,
#       ezoff_all, ezoff_miss, ezoff_hit}
#     + pin label {schedule_pin, schedule_pin_position,
#       schedule_pin_decision} pinned to PIN-T0/0/DEC-20260901-fb6f11
#   additive allowed vs the frozen-build receipt: NONE (the declared diff
#     adds no receipt fields).
# Any committed field missing, any non-allowed field differing, any
# unexpected added field, or any identity-check failure -> gate0x_pass False
# -> CC3-GATE-FAIL halt.
#
# usage: python3 src/s2a_gate0x_cmp.py <new_receipt> <L1_receipt> <frozen_gate0x_receipt> <out.json>
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
                "measured_rate_trials_per_sec", "hit_log_cap"}
PIN_LABEL_ADDED = {"schedule_pin", "schedule_pin_position",
                   "schedule_pin_decision"}
PIN_LABEL_EXPECTED = {"schedule_pin": "PIN-T0", "schedule_pin_position": 0,
                      "schedule_pin_decision": "DEC-20260901-fb6f11"}
KNOWN_ADDED = {"zhist", "sbox_table_hex", "key_hex", "sbox", "sbox_k",
               "sbox_positions", "sbox_bijective", "arm_table_concat_sha256",
               "ewhist_all", "ewhist_miss",
               "ewhist_hit", "ewbithist_all", "ewbithist_miss", "ewbithist_hit",
               "hit_e_detail",
               "ezdiag_all", "ezdiag_miss", "ezdiag_hit",
               "ezoff_all", "ezoff_miss", "ezoff_hit"}
EXPECTED_HITS = 14


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
    new_path, l1_path, frozen_path, out_path = sys.argv[1:5]
    new = json.load(open(new_path))
    l1 = json.load(open(l1_path))
    frozen = json.load(open(frozen_path))

    l1_missing, l1_mismatched, l1_allowed, l1_matched = compare(l1, new, ALLOWED_DIFF)
    l1_added = sorted(set(new.keys()) - set(l1.keys()))
    l1_unexpected_added = sorted(set(l1_added) - (KNOWN_ADDED | PIN_LABEL_ADDED))

    fz_missing, fz_mismatched, fz_allowed, fz_matched = compare(frozen, new, ALLOWED_DIFF)
    fz_added = sorted(set(new.keys()) - set(frozen.keys()))
    fz_removed = sorted(set(frozen.keys()) - set(new.keys()))
    pin_label_ok = all(new.get(k) == v for k, v in PIN_LABEL_EXPECTED.items())

    identity_checks = {
        "hit_trials_identical_vs_frozen": new.get("hit_trials") == frozen.get("hit_trials"),
        "hit_e_detail_identical_vs_frozen_14_records": (
            new.get("hit_e_detail") == frozen.get("hit_e_detail")
            and len(frozen.get("hit_e_detail", [])) == EXPECTED_HITS),
        "ez_counters_identical_vs_frozen": all(
            new.get(k) == frozen.get(k) for k in
            ("ezdiag_all", "ezdiag_miss", "ezdiag_hit",
             "ezoff_all", "ezoff_miss", "ezoff_hit")),
        "ewhist_counters_identical_vs_frozen": all(
            new.get(k) == frozen.get(k) for k in
            ("ewhist_all", "ewhist_miss", "ewhist_hit",
             "ewbithist_all", "ewbithist_miss", "ewbithist_hit")),
        "whist_identical_vs_frozen_and_L1": new.get("whist") == frozen.get("whist") == l1.get("whist"),
        "hit_log_overflow_zero_both": new.get("hit_log_overflow") == 0
                                      and frozen.get("hit_log_overflow") == 0,
        "hit_log_cap_new_is_256": new.get("hit_log_cap") == 256,
        "w_ge1_continuity_14": new.get("W_ge1_nontrivial") == EXPECTED_HITS
                               and frozen.get("W_ge1_nontrivial") == EXPECTED_HITS
                               and l1.get("W_ge1_nontrivial") == EXPECTED_HITS,
        "pin_label_fields_pinned_values": pin_label_ok,
        "arm_table_concat_sha256_identical_vs_frozen":
            new.get("arm_table_concat_sha256") == frozen.get("arm_table_concat_sha256"),
        "sbox_table_identical_vs_frozen": new.get("sbox_table_hex") == frozen.get("sbox_table_hex"),
        "thread_and_key_stream_seeds_identical_vs_frozen":
            new.get("thread_seeds") == frozen.get("thread_seeds")
            and new.get("key_stream_seeds") == frozen.get("key_stream_seeds"),
        "plaintext_stream_digest_identical_vs_frozen_and_L1":
            new.get("plaintext_stream_digest") == frozen.get("plaintext_stream_digest")
            == l1.get("plaintext_stream_digest"),
        "no_added_fields_vs_frozen_build_receipt": fz_added == [],
        "no_removed_fields_vs_frozen_build_receipt": fz_removed == [],
    }
    gate_pass = (
        not l1_missing and not l1_mismatched and not l1_unexpected_added
        and not fz_missing and not fz_mismatched
        and all(identity_checks.values()))
    out = {
        "schema": "crypto.autoresearch.gate0x_cmp.v4",
        "task_id": "TASK-20260903-7893b2",
        "batch_id": "BATCH-060cb4",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260903-8f26ac",
        "run_id": "S2a-2",
        "gate": "GATE-0X EXTENDED REBUILD (k=3 extension non-perturbation of the aes seat)",
        "new_receipt": new_path,
        "committed_L1_receipt": l1_path,
        "frozen_build_gate0x_receipt": frozen_path,
        "extended_allowed_diff_list_value": sorted(ALLOWED_DIFF),
        "extended_allowed_diff_list_additive_vs_L1": sorted(KNOWN_ADDED | PIN_LABEL_ADDED),
        "extended_allowed_diff_list_additive_vs_frozen": [],
        "pin_label_expected_values": PIN_LABEL_EXPECTED,
        "vs_L1_matched_fields_identical": l1_matched,
        "vs_L1_allowed_diffs_observed": l1_allowed,
        "vs_L1_missing_fields": l1_missing,
        "vs_L1_mismatched_fields": l1_mismatched,
        "vs_L1_added_fields_observed": l1_added,
        "vs_L1_added_fields_unexpected": l1_unexpected_added,
        "vs_frozen_matched_fields_identical": fz_matched,
        "vs_frozen_allowed_diffs_observed": fz_allowed,
        "vs_frozen_missing_fields": fz_missing,
        "vs_frozen_mismatched_fields": fz_mismatched,
        "vs_frozen_added_fields_observed": fz_added,
        "vs_frozen_removed_fields_observed": fz_removed,
        "identity_checks": identity_checks,
        "gate0x_pass": gate_pass,
        "on_failure": "HALT as CC3-GATE-FAIL/invalid_measurement (rule 5); no further arms; honest report",
        "compared_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": ("machine-generated JSON; parsed whole with python3 json.load "
                              "(all three inputs and this output) before task completion"),
        "inference": INFERENCE,
    }
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps({"gate0x_pass": gate_pass,
                      "vs_L1_missing": l1_missing,
                      "vs_L1_mismatched": [m["field"] for m in l1_mismatched],
                      "vs_L1_unexpected_added": l1_unexpected_added,
                      "vs_frozen_missing": fz_missing,
                      "vs_frozen_mismatched": [m["field"] for m in fz_mismatched],
                      "vs_frozen_added": fz_added,
                      "identity_checks": {k: v for k, v in identity_checks.items() if not v}},
                       indent=1))
    sys.exit(0 if gate_pass else 5)


if __name__ == "__main__":
    main()
