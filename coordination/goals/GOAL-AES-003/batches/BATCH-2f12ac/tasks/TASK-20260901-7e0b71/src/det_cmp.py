#!/usr/bin/env python3
# det_cmp.py -- TASK-20260901-7e0b71 (BATCH-2f12ac, GOAL-AES-003)
#
# Determinism double comparison (IDEA-20260901-363851 integrity_gates.determinism):
# two invocations of an IDENTICAL command line (including the arm name label,
# per the record's "identical command line") at log2N=20, threads=4,
# seed=531001 must produce byte-identical receipts including every e
# histogram and per-hit record, TIMING FIELDS EXCEPTED (preregistered strip
# set exactly {elapsed_seconds_measured, measured_rate_trials_per_sec}).
#
# usage: python3 src/det_cmp.py <receipt_a.json> <receipt_b.json> <out.json>
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
STRIP_SEMANTIC = {"elapsed_seconds_measured", "measured_rate_trials_per_sec"}

def strip_lines(text, keys):
    return "\n".join(l for l in text.splitlines()
                     if not any(f"\"{k}\":" in l for k in keys))

def main():
    a_path, b_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(a_path) as f:
        a_raw = f.read()
    with open(b_path) as f:
        b_raw = f.read()
    with open(a_path) as f:
        a = json.load(f)
    with open(b_path) as f:
        b = json.load(f)
    timing_only_byte_identity = (
        strip_lines(a_raw, ["elapsed_seconds_measured", "measured_rate_trials_per_sec"])
        == strip_lines(b_raw, ["elapsed_seconds_measured", "measured_rate_trials_per_sec"]))
    differing_semantic = [k for k in set(a) | set(b)
                          if k not in STRIP_SEMANTIC and a.get(k) != b.get(k)]
    det_pass = timing_only_byte_identity and not differing_semantic
    out = {
        "schema": "crypto.autoresearch.det_cmp.v1",
        "task_id": "TASK-20260901-7e0b71",
        "idea_record": "IDEA-20260901-363851",
        "receipt_a": a_path,
        "receipt_b": b_path,
        "arm_label_a": a.get("arm"),
        "arm_label_b": b.get("arm"),
        "preregistered_strip_set_timing": ["elapsed_seconds_measured", "measured_rate_trials_per_sec"],
        "preregistered_strip_set_semantic": sorted(STRIP_SEMANTIC),
        "byte_identical_modulo_timing_lines": timing_only_byte_identity,
        "differing_semantic_fields": differing_semantic,
        "determinism_pass": det_pass,
        "on_failure": "instrument void; HALT invalid_measurement (rule 5)",
        "compared_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": ("this file is machine-generated JSON; parsed whole with python3 "
                              "json.load (both inputs and this output) before task completion"),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"determinism_pass": det_pass,
                      "byte_identical_modulo_timing": timing_only_byte_identity,
                      "differing_semantic_fields": differing_semantic}, indent=1))
    sys.exit(0 if det_pass else 8)

if __name__ == "__main__":
    main()
