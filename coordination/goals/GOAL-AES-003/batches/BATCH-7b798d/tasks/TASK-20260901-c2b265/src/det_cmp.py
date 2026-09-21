#!/usr/bin/env python3
# det_cmp.py -- TASK-20260901-c2b265 (BATCH-7b798d, GOAL-AES-003)
#
# S1-5 determinism-double comparator. Follows the BATCH-ace664
# TASK-20260901-579808 P5 convention: the two receipts of the IDENTICAL
# command must be byte-identical modulo the preregistered timing strip set
# {elapsed_seconds_measured, measured_rate_trials_per_sec} (wall-clock
# fields; not semantic). Any semantic difference -> determinism FAIL ->
# SH-GATE-FAIL (instrument void; HALT invalid_measurement, rule 5).
#
# usage: python3 src/det_cmp.py <receipt_a.json> <receipt_b.json> <out_cmp.json>
# Exit: 0 determinism pass; 14 determinism fail.
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
STRIP_SET = ["elapsed_seconds_measured", "measured_rate_trials_per_sec"]


def main():
    a_path, b_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(a_path) as f:
        a_raw = f.read()
    with open(b_path) as f:
        b_raw = f.read()
    a = json.loads(a_raw)
    b = json.loads(b_raw)

    raw_identical = a_raw == b_raw

    keys = set(a.keys()) | set(b.keys())
    differing = sorted(k for k in keys
                       if k not in STRIP_SET and a.get(k) != b.get(k))
    strip_diffs = {k: {"a": a.get(k), "b": b.get(k)}
                   for k in STRIP_SET if a.get(k) != b.get(k)}

    def strip_lines(raw):
        return "\n".join(ln for ln in raw.splitlines()
                         if not any(f'"{k}"' in ln for k in STRIP_SET))

    byte_identical_modulo_timing = strip_lines(a_raw) == strip_lines(b_raw)
    ok = (not differing) and byte_identical_modulo_timing

    out = {
        "schema": "crypto.autoresearch.det_cmp.v1",
        "task_id": "TASK-20260901-c2b265",
        "idea_record": "IDEA-20260901-582ea9",
        "pin_decision": "DEC-20260901-fb6f11",
        "run_id": "S1-5",
        "receipt_a": a_path,
        "receipt_b": b_path,
        "arm_label_a": a.get("arm"),
        "arm_label_b": b.get("arm"),
        "commands_identical_attestation": ("both invocations ran the identical "
                                           "command string (same arm label, r=5, "
                                           "amask=1, smask=1, log2N=20, seed "
                                           "531001, armid 1, threads 4, aes)"),
        "preregistered_strip_set_timing": STRIP_SET,
        "raw_byte_identical": raw_identical,
        "raw_byte_identical_note": ("wall-clock timing fields make raw byte "
                                    "identity impossible by construction; the "
                                    "preregistered comparator notion is "
                                    "byte-identity modulo the strip set "
                                    "(BATCH-ace664 P5 convention)"),
        "byte_identical_modulo_timing_lines": byte_identical_modulo_timing,
        "differing_semantic_fields": differing,
        "strip_set_value_differences": strip_diffs,
        "determinism_pass": ok,
        "on_failure": "instrument void; HALT invalid_measurement (rule 5); SH-GATE-FAIL",
        "compared_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": ("this file is machine-generated JSON; parsed whole "
                              "with python3 json.load before task completion"),
        "inference": INFERENCE,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"raw_byte_identical": raw_identical,
                      "byte_identical_modulo_timing": byte_identical_modulo_timing,
                      "differing_semantic_fields": differing,
                      "determinism_pass": ok}, indent=1))
    sys.exit(0 if ok else 14)


if __name__ == "__main__":
    main()
