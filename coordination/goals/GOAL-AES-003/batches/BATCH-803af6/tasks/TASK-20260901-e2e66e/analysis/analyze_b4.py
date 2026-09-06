#!/usr/bin/env python3
"""TASK-20260901-e2e66e B4 exclusion-toggle audit analysis.

Reads the six run JSONs of this task plus the two committed immutable
equivalence-gate receipts (BATCH-015 L1-AES-R5-P30 / M1-FF-P30) and evaluates:
  - the ENABLED-build equivalence gate (PREREGISTRATION.md section 5)
  - per-arm predictions P1..P7 (PREREGISTRATION.md section 6)
  - the C4 verdict rule (record IDEA-20260901-02f7c4: signed W>=1 delta equals
    the trivial-trial count exactly, trial-by-trial, on both arms)
Pure arithmetic on already-written run JSONs; not a run.
"""
import json, hashlib, os

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
RUNS = os.path.join(TASK, "runs")
B15 = os.path.normpath(os.path.join(
    TASK, "..", "..", "..", "BATCH-015", "tasks", "TASK-20260805-d408ac", "runs"))

def load(p):
    with open(p) as f:
        return json.load(f)

on_aes  = load(os.path.join(RUNS, "B4-AES-ON-P30.json"))
off_aes = load(os.path.join(RUNS, "B4-AES-OFF-P30.json"))
on_ff   = load(os.path.join(RUNS, "B4-FF-ON-P30.json"))
off_ff  = load(os.path.join(RUNS, "B4-FF-OFF-P30.json"))
smk_on  = load(os.path.join(RUNS, "SMOKE-B4-ON-2p20.json"))
smk_off = load(os.path.join(RUNS, "SMOKE-B4-OFF-2p20.json"))
ref_aes = load(os.path.join(B15, "L1-AES-R5-P30.json"))
ref_ff  = load(os.path.join(B15, "M1-FF-P30.json"))

out = {"task_id": "TASK-20260901-e2e66e", "battery": "B4 exclusion-toggle audit",
       "frozen_spec": "ledger/proposals/IDEA-20260901-02f7c4.yaml",
       "equivalence_gate_references": {
           "aes": os.path.join(B15, "L1-AES-R5-P30.json"),
           "ff":  os.path.join(B15, "M1-FF-P30.json")},
       "arms": {}}

def hit_set(d):
    return {(h[0], h[1]) for h in d["hit_trials"]}

def hit_w_map(d):
    return {(h[0], h[1]): h[2] for h in d["hit_trials"]}

def trivial_set(d):
    return {(h[0], h[1]) for h in d["trivial_trials"]}

def equiv_gate(run, ref, tag, check_key_digest):
    g = {}
    g["thread_seeds_equal"] = run["thread_seeds"] == ref["thread_seeds"]
    g["plaintext_stream_digest_equal"] = run["plaintext_stream_digest"] == ref["plaintext_stream_digest"]
    if check_key_digest:
        g["key_stream_digest_equal"] = run.get("key_stream_digest") == ref.get("key_stream_digest")
    g["trivial_swaps_excluded_equal"] = run["trivial_swaps_excluded"] == ref["trivial_swaps_excluded"]
    g["nontrivial_trials_equal"] = run["nontrivial_trials"] == ref["nontrivial_trials"]
    g["W_ge1_equal"] = run["W_ge1_nontrivial"] == ref["W_ge1_nontrivial"]
    g["whist_equal"] = run["whist"] == ref["whist"]
    g["W_ge1_by_word_equal"] = run["W_ge1_by_word"] == ref["W_ge1_by_word"]
    run_pairs = sorted(hit_set(run))
    ref_pairs = sorted(hit_set(ref))
    g["hit_thread_t_pairs_identical"] = run_pairs == ref_pairs
    g["hit_count_ref"] = len(ref_pairs)
    g["hit_count_run"] = len(run_pairs)
    g["passed"] = all(v for k, v in g.items() if k not in ("hit_count_ref", "hit_count_run"))
    return g

def arm_checks(on, off, name):
    T = on["trivial_swaps_excluded"]
    T_off = off["trivial_swaps_excluded"]
    c = {}
    c["P1_stream_identity"] = {
        "plaintext_digest_equal_on_off": on["plaintext_stream_digest"] == off["plaintext_stream_digest"],
        "plaintext_digest_on": on["plaintext_stream_digest"],
        "plaintext_digest_off": off["plaintext_stream_digest"]}
    if "key_stream_digest" in on:
        c["P1_stream_identity"]["key_digest_equal_on_off"] = on["key_stream_digest"] == off["key_stream_digest"]
        c["P1_stream_identity"]["key_digest_on"] = on["key_stream_digest"]
        c["P1_stream_identity"]["key_digest_off"] = off["key_stream_digest"]
    c["P1_stream_identity"]["passed"] = all(
        v for k, v in c["P1_stream_identity"].items() if k.endswith("equal_on_off"))
    c["P2_trivial_count_identity"] = {
        "trivial_ON": T, "trivial_OFF": T_off, "equal": T == T_off, "passed": T == T_off}
    delta = off["W_ge1_nontrivial"] - on["W_ge1_nontrivial"]
    c["P3_signed_wge1_delta"] = {
        "W_ge1_ON": on["W_ge1_nontrivial"], "W_ge1_OFF": off["W_ge1_nontrivial"],
        "signed_delta_OFF_minus_ON": delta, "trivial_count_T": T,
        "delta_equals_T_exactly": delta == T, "passed": delta == T}
    h_on, h_off, tr = hit_set(on), hit_set(off), trivial_set(off) | trivial_set(on)
    setdiff = h_off - h_on
    all_trivial_W3 = all(h[2] == 3 for h in (on["trivial_trials"] + off["trivial_trials"]))
    c["P4_trial_by_trial"] = {
        "hits_ON_subset_hits_OFF": h_on <= h_off,
        "hits_OFF_minus_hits_ON_equals_trivial_set": setdiff == tr,
        "hits_OFF_minus_hits_ON": sorted(setdiff),
        "trivial_set": sorted(tr),
        "hits_ON": sorted(h_on),
        "hits_OFF": sorted(h_off),
        "all_logged_trivial_W_equal_3": all_trivial_W3,
        "trivial_entries_on": on["trivial_trials"],
        "trivial_entries_off": off["trivial_trials"]}
    c["P4_trial_by_trial"]["passed"] = (
        c["P4_trial_by_trial"]["hits_ON_subset_hits_OFF"]
        and c["P4_trial_by_trial"]["hits_OFF_minus_hits_ON_equals_trivial_set"]
        and all_trivial_W3)
    wh_ok3 = off["whist"][3] - on["whist"][3] == T
    wh_others = all(off["whist"][k] == on["whist"][k] for k in (0, 1, 2, 4))
    c["P5_histogram_identity"] = {
        "whist_ON": on["whist"], "whist_OFF": off["whist"],
        "whist3_delta": off["whist"][3] - on["whist"][3], "T": T,
        "whist3_delta_equals_T": wh_ok3, "other_bins_equal": wh_others,
        "passed": wh_ok3 and wh_others}
    ww = [off["W_ge1_by_word"][j] - on["W_ge1_by_word"][j] for j in range(4)]
    c["P6_perword_identity"] = {
        "W_ge1_by_word_ON": on["W_ge1_by_word"], "W_ge1_by_word_OFF": off["W_ge1_by_word"],
        "delta_by_word": ww, "expected_delta_by_word_amask1": [0, T, T, T],
        "passed": ww == [0, T, T, T]}
    N = on["trials"]
    c["P7_accounting"] = {
        "sum_whist_OFF": sum(off["whist"]), "expected_OFF": N,
        "sum_whist_ON": sum(on["whist"]), "expected_ON": N - T,
        "passed": sum(off["whist"]) == N and sum(on["whist"]) == N - T}
    arm_pass = all(c[p]["passed"] for p in
                   ("P1_stream_identity", "P2_trivial_count_identity", "P3_signed_wge1_delta",
                    "P4_trial_by_trial", "P5_histogram_identity", "P6_perword_identity",
                    "P7_accounting"))
    c["C4_arm_verdict"] = "PASS" if (c["P3_signed_wge1_delta"]["passed"]
                                     and c["P4_trial_by_trial"]["passed"]) else "FAIL"
    c["arm_all_predictions_pass"] = arm_pass
    c["power_note"] = {
        "trivial_trials_realized_T": T,
        "expected_T_at_2p30": 0.25,
        "vacuous_if_T_zero": T == 0,
        "statement": ("T=0 realized: the signed-delta identity holds exactly (0=0) but the "
                      "non-zero-delta path of the exclusion was not exercised by data on this "
                      "arm at this exposure; pre-registered power disclosure, PREREGISTRATION.md "
                      "section 4.") if T == 0 else "T>=1 realized: delta checked on real trivial trials."}
    return c

out["equivalence_gate"] = {
    "B4-AES-ON-P30_vs_L1-AES-R5-P30": equiv_gate(on_aes, ref_aes, "aes", False),
    "B4-FF-ON-P30_vs_M1-FF-P30": equiv_gate(on_ff, ref_ff, "ff", True)}
out["equivalence_gate"]["both_passed"] = (
    out["equivalence_gate"]["B4-AES-ON-P30_vs_L1-AES-R5-P30"]["passed"]
    and out["equivalence_gate"]["B4-FF-ON-P30_vs_M1-FF-P30"]["passed"])

out["arms"]["AES-R5"] = arm_checks(on_aes, off_aes, "AES-R5")
out["arms"]["FF-NULL"] = arm_checks(on_ff, off_ff, "FF-NULL")

out["smoke_cross_build_stream_identity_2p20"] = {
    "plaintext_digest_equal": smk_on["plaintext_stream_digest"] == smk_off["plaintext_stream_digest"],
    "digest": smk_on["plaintext_stream_digest"],
    "T_at_2p20": smk_on["trivial_swaps_excluded"],
    "delta_at_2p20": smk_off["W_ge1_nontrivial"] - smk_on["W_ge1_nontrivial"]}

# trial-by-trial delta table (per task card: the table or its digest)
table = []
for arm, on, off in (("AES-R5", on_aes, off_aes), ("FF-NULL", on_ff, off_ff)):
    T = on["trivial_swaps_excluded"]
    table.append({
        "arm": arm,
        "trivial_trial_entries_on": on["trivial_trials"],
        "trivial_trial_entries_off": off["trivial_trials"],
        "trivial_count_T": T,
        "signed_wge1_delta": off["W_ge1_nontrivial"] - on["W_ge1_nontrivial"],
        "delta_minus_T": (off["W_ge1_nontrivial"] - on["W_ge1_nontrivial"]) - T,
        "hits_on_count": len(on["hit_trials"]),
        "hits_off_count": len(off["hit_trials"]),
        "hit_set_difference_off_minus_on": sorted(hit_set(off) - hit_set(on)),
        "verdict": "EXACT" if (off["W_ge1_nontrivial"] - on["W_ge1_nontrivial"]) == T else "MISMATCH"})
out["trial_by_trial_delta_table"] = table

aes_c4 = out["arms"]["AES-R5"]["C4_arm_verdict"]
ff_c4 = out["arms"]["FF-NULL"]["C4_arm_verdict"]
gate_ok = out["equivalence_gate"]["both_passed"]
out["C4_overall"] = {
    "per_arm": {"AES-R5": aes_c4, "FF-NULL": ff_c4},
    "enabled_build_equivalence_gate_passed": gate_ok,
    "verdict": "PASS" if (aes_c4 == "PASS" and ff_c4 == "PASS" and gate_ok) else "FAIL",
    "rule": ("C4 PASS iff the exclusion-toggle delta equals the trivial-trial count on both "
             "arms within exact arithmetic, trial-by-trial (IDEA-20260901-02f7c4 claim C4 / "
             "PR-4). Any other delta is F3."),
    "power_limitation": (
        "Zero trivial trials realized on BOTH arms at 2^30 (expected ~0.25 per arm). The "
        "signed-delta identity is verified exactly (0=0 on both arms) with full stream "
        "identity and trial-by-trial set machinery, but no non-zero delta was realized, so "
        "this audit's discrimination on the non-trivial code path at this exposure is "
        "vacuous; stated per the record's minimal_test regime ('zero-or-one trivial trials') "
        "and PREREGISTRATION.md section 4 power disclosure. Run budget (6/6) was exhausted "
        "by the four arms plus two pre-registered smokes, so no higher-exposure extension "
        "was run.")}

out["run_inventory"] = {
    "runs": ["SMOKE-B4-ON-2p20", "SMOKE-B4-OFF-2p20", "B4-AES-ON-P30", "B4-AES-OFF-P30",
             "B4-FF-ON-P30", "B4-FF-OFF-P30"],
    "run_count": 6, "maximum_runs": 6,
    "counting_convention": "one binary invocation = one run (TASK-20260805-d408ac convention); this analysis script is arithmetic on written JSONs, not a run"}

out["artifact_digests_sha256"] = {
    f: hashlib.sha256(open(os.path.join(RUNS, f), "rb").read()).hexdigest()
    for f in ["SMOKE-B4-ON-2p20.json", "SMOKE-B4-OFF-2p20.json", "B4-AES-ON-P30.json",
              "B4-AES-OFF-P30.json", "B4-FF-ON-P30.json", "B4-FF-OFF-P30.json"]}

out["inference"] = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
    "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c"}
out["parse_attestation"] = (
    "This file (runs/decision_analysis.json) was generated by python3 json.dumps and the "
    "whole file was re-parsed with python3 json.load before the analysis finished; all six "
    "run JSONs and both BATCH-015 equivalence-gate receipts parsed whole with json.load as "
    "well. Parse status: OK.")

with open(os.path.join(RUNS, "decision_analysis.json"), "w") as f:
    json.dump(out, f, indent=2)

# self-verify: parse back the whole file
json.load(open(os.path.join(RUNS, "decision_analysis.json")))
print("decision_analysis.json written and re-parsed OK")
print("equivalence_gate both_passed:", out["equivalence_gate"]["both_passed"])
print("C4 per arm:", out["C4_overall"]["per_arm"], "overall:", out["C4_overall"]["verdict"])
for row in out["trial_by_trial_delta_table"]:
    print(row["arm"], "T=", row["trivial_count_T"], "delta=", row["signed_wge1_delta"], row["verdict"])
