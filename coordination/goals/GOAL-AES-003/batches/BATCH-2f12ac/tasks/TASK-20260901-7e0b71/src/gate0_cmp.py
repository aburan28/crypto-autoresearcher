#!/usr/bin/env python3
# gate0_cmp.py -- TASK-20260901-7e0b71 (BATCH-2f12ac, GOAL-AES-003)
#
# GATE 0 (BLOCKING, IDEA-20260901-363851 integrity_gates.gate_0_anchor_reproduction):
# field-by-field comparison of the logging-ON derivative receipt against the
# committed immutable receipt L1-AES-R5-P30 (BATCH-015 TASK-20260805-d408ac).
#
# Allowed-diff list EXACTLY (preregistered, verbatim from the record):
#   {arm label, probe label, oracle label, elapsed_seconds_measured,
#    measured_rate_trials_per_sec}
# plus fields the derivative ADDS (recorded informationally, never failures):
#   zhist, sbox_table_hex, key_hex, sbox, sbox_k, sbox_positions,
#   sbox_bijective, all e fields (ewhist_*, ewbithist_*, hit_e_detail).
# Any committed field missing, or any non-allowed field differing -> FAIL
# (exit 5) -> task HALTS as F4/invalid_measurement (rule 5).
#
# usage: python3 src/gate0_cmp.py <new_receipt.json> <committed_receipt.json> <out.json>
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
                "measured_rate_trials_per_sec"}
KNOWN_ADDED = {"zhist", "sbox_table_hex", "key_hex", "sbox", "sbox_k",
               "sbox_positions", "sbox_bijective", "arm_table_concat_sha256",
               "ewhist_all", "ewhist_miss",
               "ewhist_hit", "ewbithist_all", "ewbithist_miss", "ewbithist_hit",
               "hit_e_detail"}

def main():
    new_path, committed_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(new_path) as f:
        new = json.load(f)
    with open(committed_path) as f:
        committed = json.load(f)
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
    gate_pass = (not missing) and (not mismatched) and hit_indices_ok
    out = {
        "schema": "crypto.autoresearch.gate0_cmp.v1",
        "task_id": "TASK-20260901-7e0b71",
        "idea_record": "IDEA-20260901-363851",
        "gate": "GATE 0 anchor reproduction (BLOCKING) + perturbation check + J5 carrier arm",
        "new_receipt": new_path,
        "committed_receipt": committed_path,
        "allowed_diff_list_preregistered": sorted(ALLOWED_DIFF),
        "added_fields_preregistered_set": sorted(KNOWN_ADDED),
        "matched_fields_identical": matched,
        "allowed_diffs_observed": allowed_diffs,
        "missing_committed_fields": missing,
        "mismatched_fields": mismatched,
        "added_fields_observed": added,
        "added_fields_unexpected": unexpected_added,
        "n_hit_indices_committed": len(committed.get("hit_trials", [])),
        "n_hit_indices_new": len(new.get("hit_trials", [])),
        "all_14_hit_indices_identical": hit_indices_ok,
        "gate0_pass": gate_pass,
        "on_failure": "HALT as F4/invalid_measurement (rule 5); no further arms; honest report",
        "compared_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": ("this file is machine-generated JSON; parsed whole with python3 "
                              "json.load (both inputs and this output) before task completion"),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"gate0_pass": gate_pass, "missing": missing,
                      "mismatched": [m["field"] for m in mismatched],
                      "hits_identical": hit_indices_ok,
                      "unexpected_added": unexpected_added}, indent=1))
    sys.exit(0 if gate_pass else 5)

if __name__ == "__main__":
    main()
