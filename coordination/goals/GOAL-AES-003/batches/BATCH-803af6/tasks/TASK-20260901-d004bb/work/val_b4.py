#!/usr/bin/env python3
"""Validator fresh re-derivation (RUN 3): B4 signed deltas trial-by-trial from raw
receipts, ENABLED-build equivalence gate vs committed BATCH-015 immutable receipts,
and control checks. Pure arithmetic on committed JSON files; no producer code."""
import hashlib, json, sys

B = "coordination/goals/GOAL-AES-003/batches/"

def load(p):
    with open(p) as f:
        return json.load(f)

arms = {
    "AES_ON":  load(B + "BATCH-803af6/tasks/TASK-20260901-e2e66e/runs/B4-AES-ON-P30.json"),
    "AES_OFF": load(B + "BATCH-803af6/tasks/TASK-20260901-e2e66e/runs/B4-AES-OFF-P30.json"),
    "FF_ON":   load(B + "BATCH-803af6/tasks/TASK-20260901-e2e66e/runs/B4-FF-ON-P30.json"),
    "FF_OFF":  load(B + "BATCH-803af6/tasks/TASK-20260901-e2e66e/runs/B4-FF-OFF-P30.json"),
    "SMOKE_ON":  load(B + "BATCH-803af6/tasks/TASK-20260901-e2e66e/runs/SMOKE-B4-ON-2p20.json"),
    "SMOKE_OFF": load(B + "BATCH-803af6/tasks/TASK-20260901-e2e66e/runs/SMOKE-B4-OFF-2p20.json"),
}
ref = {
    "L1": load(B + "BATCH-015/tasks/TASK-20260805-d408ac/runs/L1-AES-R5-P30.json"),
    "M1": load(B + "BATCH-015/tasks/TASK-20260805-d408ac/runs/M1-FF-P30.json"),
}

# 14 hit pairs exactly as pre-registered in TASK-20260901-e2e66e PREREGISTRATION.md section 5
PREREG_AES_HITS = {(0,52735906),(0,178745786),(0,266298850),(0,273520598),(0,339544647),
                   (0,523527834),(1,67724771),(1,90384281),(1,147208629),(1,286947500),
                   (1,336820358),(1,440575768),(1,451495737),(1,490333025)}
PREREG_FF_HITS = {(1,270788492)}

def hitset(r):
    return {(h[0], h[1]) for h in r["hit_trials"]}

def trivialset(r):
    return {(h[0], h[1]) for h in r["trivial_trials"]}

out = {"schema": "validator.b4_rederivation.v1", "task_id": "TASK-20260901-d004bb", "arms": {}}

for name, on_key, off_key, has_keys in (("AES_R5", "AES_ON", "AES_OFF", False),
                                        ("FF_NULL", "FF_ON", "FF_OFF", True)):
    ON, OFF = arms[on_key], arms[off_key]
    T_ON_counter = ON["trivial_swaps_excluded"]
    T_OFF_counter = OFF["trivial_swaps_excluded"]
    triv_ON = trivialset(ON); triv_OFF = trivialset(OFF)
    T_list_ON = len(triv_ON) + ON["trivial_log_overflow"]
    T_list_OFF = len(triv_OFF) + OFF["trivial_log_overflow"]
    hits_ON, hits_OFF = hitset(ON), hitset(OFF)
    wge1_ON, wge1_OFF = ON["W_ge1_nontrivial"], OFF["W_ge1_nontrivial"]
    delta = wge1_OFF - wge1_ON
    T = T_OFF_counter
    a = {
        "spec_identical": {
            "seed": ON["seed"] == OFF["seed"] == 531001,
            "arm_id": ON["arm_id"] == OFF["arm_id"] == 1,
            "threads": ON["threads"] == OFF["threads"] == 2,
            "log2N": ON["log2N"] == OFF["log2N"] == 30,
            "trials": ON["trials"] == OFF["trials"] == 2**30,
            "amask_smask": ON["amask"] == OFF["amask"] == 1 and ON["smask"] == OFF["smask"] == 1,
            "build_flags_differ_as_declared": ON["exclude_trivial_build"] == 1 and OFF["exclude_trivial_build"] == 0,
        },
        "P1_stream_identity": {
            "plaintext_digest_equal": ON["plaintext_stream_digest"] == OFF["plaintext_stream_digest"],
            "thread_seeds_equal": ON["thread_seeds"] == OFF["thread_seeds"],
            "key_digest_equal": (ON.get("key_stream_digest") == OFF.get("key_stream_digest")) if has_keys else None,
        },
        "P2_trivial_count": {"T_counter_ON": T_ON_counter, "T_counter_OFF": T_OFF_counter,
                             "T_list_ON": T_list_ON, "T_list_OFF": T_list_OFF,
                             "counters_equal": T_ON_counter == T_OFF_counter},
        "P3_signed_delta": {"W_ge1_ON": wge1_ON, "W_ge1_OFF": wge1_OFF,
                            "signed_delta_OFF_minus_ON": delta, "T": T,
                            "delta_equals_T": delta == T},
        "P4_trial_by_trial": {
            "hits_ON_count": len(hits_ON), "hits_OFF_count": len(hits_OFF),
            "hits_ON_subset_hits_OFF": hits_ON.issubset(hits_OFF),
            "hits_OFF_minus_hits_ON": sorted(hits_OFF - hits_ON),
            "trivial_set_OFF": sorted(triv_OFF),
            "hits_OFF_minus_hits_ON_equals_trivial_set": (hits_OFF - hits_ON) == triv_OFF,
            "all_logged_trivial_W_eq_3": all(h[2] == 3 for h in OFF["trivial_trials"] + ON["trivial_trials"]) if (OFF["trivial_trials"] or ON["trivial_trials"]) else True,
        },
        "P5_whist": {
            "whist_ON": ON["whist"], "whist_OFF": OFF["whist"],
            "whist3_delta_eq_T": OFF["whist"][3] - ON["whist"][3] == T,
            "other_bins_equal": [ON["whist"][k] for k in (0,1,2,4)] == [OFF["whist"][k] for k in (0,1,2,4)],
            "sum_whist_ON": sum(ON["whist"]), "sum_whist_OFF": sum(OFF["whist"]),
            "sum_OFF_eq_trials": sum(OFF["whist"]) == OFF["trials"],
            "sum_ON_eq_trials_minus_T": sum(ON["whist"]) == ON["trials"] - T,
        },
        "P6_wword": {
            "ON": ON["W_ge1_by_word"], "OFF": OFF["W_ge1_by_word"],
            "delta": [OFF["W_ge1_by_word"][j] - ON["W_ge1_by_word"][j] for j in range(4)],
            "expected_delta_amask1": [0, T, T, T],
        },
    }
    a["P6_wword"]["delta_matches_expected"] = a["P6_wword"]["delta"] == a["P6_wword"]["expected_delta_amask1"]
    out["arms"][name] = a

# equivalence gate vs committed immutable receipts
def gate(run, r, with_key_digest):
    g = {
        "thread_seeds": run["thread_seeds"] == r["thread_seeds"],
        "plaintext_digest": run["plaintext_stream_digest"] == r["plaintext_stream_digest"],
        "trivial_swaps_excluded": run["trivial_swaps_excluded"] == r["trivial_swaps_excluded"],
        "nontrivial_trials": run["nontrivial_trials"] == r["nontrivial_trials"],
        "W_ge1": run["W_ge1_nontrivial"] == r["W_ge1_nontrivial"],
        "whist": run["whist"] == r["whist"],
        "W_ge1_by_word": run["W_ge1_by_word"] == r["W_ge1_by_word"],
        "hit_pairs_identical": hitset(run) == hitset(r),
        "seed_armid_threads_log2N": (run["seed"], run["arm_id"], run["threads"], run["log2N"]) == (r["seed"], r["arm_id"], r["threads"], r["log2N"]),
    }
    if with_key_digest:
        g["key_digest"] = run["key_stream_digest"] == r["key_stream_digest"]
        g["first_trial_keys_hex"] = run["first_trial_keys_hex"] == r["first_trial_keys_hex"]
    g["all_pass"] = all(v for v in g.values() if isinstance(v, bool))
    return g

out["equivalence_gate_vs_committed_Batch015_receipts"] = {
    "B4_AES_ON_vs_L1_AES_R5_P30": gate(arms["AES_ON"], ref["L1"], False),
    "B4_FF_ON_vs_M1_FF_P30": gate(arms["FF_ON"], ref["M1"], True),
    "committed_L1_hits_eq_preregistered_14": hitset(ref["L1"]) == PREREG_AES_HITS,
    "committed_M1_hits_eq_preregistered_1": hitset(ref["M1"]) == PREREG_FF_HITS,
    "note_committed_receipts_hit_trials_logged_field": {
        "L1_hit_trials_logged": ref["L1"]["hit_trials_logged"], "L1_hit_list_len": len(ref["L1"]["hit_trials"]),
        "M1_hit_trials_logged": ref["M1"]["hit_trials_logged"], "M1_hit_list_len": len(ref["M1"]["hit_trials"]),
        "B4_AES_ON_hit_trials_logged": arms["AES_ON"]["hit_trials_logged"],
        "B4_FF_ON_hit_trials_logged": arms["FF_ON"]["hit_trials_logged"],
        "reading": "base instrument printed thread-0-only count in hit_trials_logged while hit_trials covered all threads; B4 builds corrected the counter to the full sum (disclosed deviation). Substantive comparison uses the (thread,t) pair sets.",
    },
}

out["smoke_2p20"] = {
    "plaintext_digest_equal": arms["SMOKE_ON"]["plaintext_stream_digest"] == arms["SMOKE_OFF"]["plaintext_stream_digest"],
    "T": arms["SMOKE_OFF"]["trivial_swaps_excluded"],
    "delta": arms["SMOKE_OFF"]["W_ge1_nontrivial"] - arms["SMOKE_ON"]["W_ge1_nontrivial"],
    "hitsets_equal": hitset(arms["SMOKE_ON"]) == hitset(arms["SMOKE_OFF"]),
}

out["power"] = {
    "expected_trivial_per_arm_at_2p30": 2**30 / 2**32,
    "realized_T": {k: out["arms"][k]["P2_trivial_count"]["T_counter_OFF"] for k in ("AES_R5", "FF_NULL")},
    "nonzero_delta_path_exercised": any(out["arms"][k]["P2_trivial_count"]["T_counter_OFF"] > 0 for k in ("AES_R5", "FF_NULL")),
}

# file digests of the six run JSONs (recomputed now)
dg = {}
for k, fname in (("SMOKE_ON","SMOKE-B4-ON-2p20.json"),("SMOKE_OFF","SMOKE-B4-OFF-2p20.json"),
                 ("AES_ON","B4-AES-ON-P30.json"),("AES_OFF","B4-AES-OFF-P30.json"),
                 ("FF_ON","B4-FF-ON-P30.json"),("FF_OFF","B4-FF-OFF-P30.json")):
    p = B + "BATCH-803af6/tasks/TASK-20260901-e2e66e/runs/" + fname
    dg[fname] = hashlib.sha256(open(p, "rb").read()).hexdigest()
out["run_json_sha256_recomputed"] = dg

with open(sys.argv[1], "w") as f:
    json.dump(out, f, indent=1)

for name in ("AES_R5", "FF_NULL"):
    a = out["arms"][name]
    print(name, "delta:", a["P3_signed_delta"]["signed_delta_OFF_minus_ON"], "T:", a["P3_signed_delta"]["T"],
          "delta==T:", a["P3_signed_delta"]["delta_equals_T"],
          "| hits OFF\\ON:", a["P4_trial_by_trial"]["hits_OFF_minus_hits_ON"],
          "| P4 set id:", a["P4_trial_by_trial"]["hits_OFF_minus_hits_ON_equals_trivial_set"],
          "| spec:", all(a["spec_identical"].values()),
          "| P1:", all(v for v in a["P1_stream_identity"].values() if v is not None),
          "| P5:", a["P5_whist"]["whist3_delta_eq_T"] and a["P5_whist"]["other_bins_equal"] and a["P5_whist"]["sum_OFF_eq_trials"] and a["P5_whist"]["sum_ON_eq_trials_minus_T"],
          "| P6:", a["P6_wword"]["delta_matches_expected"])
eg = out["equivalence_gate_vs_committed_Batch015_receipts"]
print("gate AES:", eg["B4_AES_ON_vs_L1_AES_R5_P30"]["all_pass"], "gate FF:", eg["B4_FF_ON_vs_M1_FF_P30"]["all_pass"],
      "L1 hits == prereg 14:", eg["committed_L1_hits_eq_preregistered_14"], "M1 hit == prereg:", eg["committed_M1_hits_eq_preregistered_1"])
print("smoke:", out["smoke_2p20"])
print("power:", out["power"])
print("OK")
