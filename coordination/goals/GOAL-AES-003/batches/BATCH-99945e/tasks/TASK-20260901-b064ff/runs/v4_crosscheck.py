#!/usr/bin/env python3
# VALIDATOR RUN 4 (TASK-20260901-b064ff): final cross-consistency, battery outcome
# derived by the validator from the preregistered consequence map + recounted values.
import json

BASE = "coordination/goals/GOAL-AES-003/batches/BATCH-99945e/tasks/TASK-20260901-74271d/"
RUNS = BASE + "runs/"
MINE = "coordination/goals/GOAL-AES-003/batches/BATCH-99945e/tasks/TASK-20260901-b064ff/runs/"
out = {"checks": []}
fails = []

def check(name, cond, detail=""):
    out["checks"].append({"name": name, "ok": bool(cond), "detail": detail})
    if not cond:
        fails.append(name)

def load(p):
    with open(p) as f:
        return json.load(f)

res = load(BASE + "RESULTS.json")
N30 = 2**30

# --- 1. battery outcome derived INDEPENDENTLY from preregistered consequence map ---
j4 = load(RUNS + "J4_rbij_arm.json")
j3 = load(RUNS + "J3_affine_rerun.json")
j2 = load(RUNS + "J2_keyed_bridge.json")
j1 = load(RUNS + "J1_census_ext.json")
k16 = load(RUNS + "J1_keyed_r16.json")
g = load(RUNS + "GUARD_feistel_bridge.json")

hits4 = sum(j4["whist"][1:])
# PREREGISTRATION section 1 bands: DEAD <=8, gray 9..99, ALIVE >=100
j4_band = "DEAD" if hits4 <= 8 else ("GRAY" if hits4 <= 99 else "ALIVE")
# section 2: hits >= 2^30-8 and W=3 on 100% nontrivial
j3_ok = sum(j3["whist"][1:]) >= N30 - 8 and j3["whist"] == [0, 0, 0, N30, 0]
# section 3: 500/500 both laws both cells
j2_ok = all(c["qdiff_equals_pdiff"] == 500 and c["W_equals_4_minus_absA"] == 500 for c in j2["cells"]) and len(j2["cells"]) == 2
# section 4: guards + flat law r=11..16 + keyed r16 500/500
j1_ok = (all(v["DrMr_is_I"] and v["MrDr_is_I"] for v in j1["per_r_port_guards_DrMr_and_MrDr_both_I128"].values())
         and j1["all_instances_match"] and j1["flat_law_ok_extension_r11_r16"]
         and k16["cells"][0]["qdiff_equals_pdiff"] == 500 and k16["cells"][0]["W_equals_4_minus_absA"] == 500)
# section 5: holds < 50% => GUARD PASS
guard_pass = g["identity_law_read_first_500"]["identity_law_holds_count"] < 250

battery = "ALL-SEALED" if (j4_band == "DEAD" and j3_ok and j2_ok and j1_ok and guard_pass) else (
    "KILLED-AT-J4" if j4_band == "ALIVE" else ("NARROWED/INCONCLUSIVE-AT-J4" if j4_band == "GRAY" else "DEFECT-AT-OTHER-ARM"))
check("X.battery_outcome_independent", battery == "ALL-SEALED" == res["battery_level_outcome"],
      f"validator-derived={battery} J4_band={j4_band} j3_ok={j3_ok} j2_ok={j2_ok} j1_ok={j1_ok} guard_pass={guard_pass}")

# --- 2. deviations: all producer-disclosed, all independently corroborated ---
devs = res["deviations_and_unexpected_observations"]
fatal = load(RUNS + "build_pins_attempt1_fatal.json")
check("X.dev1_run1_fatal_preserved_disclosed", fatal["overall_pass"] is False
      and fatal["checks"]["frozen_table_C_vs_python_byte_match"] is False
      and any("attempt 1" in d and "orchestrator bug" in d for d in devs))
check("X.dev2_J4_subclass_disclosed", any("16 symbols" in d and "256" in d for d in devs)
      and "sbox_interpretation_disclosure" in res["arms"]["J4"]["configuration"])
check("X.dev3_rcon_disclosed", any("rcon" in d and "6c,d8,ab,4d,9a,2f" in d for d in devs))
check("X.dev4_trivial_swap_r3_recorded", any("one trivial swap" in d for d in devs)
      and j2["cells"][0]["trivial_swaps"] == 1)
check("X.dev5_zhist_shape_recorded", any("zhist" in d for d in devs))
check("X.no_undeclared_reruns", len(devs) == 6 and any("No other deviations" in d for d in devs))

# --- 3. J4 zhist observation consistency ---
zh = j4["zhist"]
check("X.J4_zhist_sum_and_concentration", sum(zh) == N30 and zh[0] / N30 > 0.93,
      f"zhist[0]/2^30={zh[0]/N30:.4f}; W=1 events: whist[1]={j4['whist'][1]}, wword={j4['W_ge1_by_word']}")
check("X.J4_two_hits_both_W1_word0_word3", j4["whist"][1] == 2 and j4["W_ge1_by_word"] == [1, 0, 0, 1])

# --- 4. GUARD semantics fields ---
check("X.GUARD_round_semantics", g["parameters"]["rounds_field_ignored"] == 5
      and g["parameters"]["feistel_rounds_actual"] == 16 and g["parameters"]["read_trials_first"] == 500
      and g["parameters"]["stream_trials"] == 512 and g["parameters"]["threads"] == 1 and g["parameters"]["arm_id"] == 999)

# --- 5. RESULTS vs decision_analysis consistency ---
da = load(RUNS + "decision_analysis.json")
check("X.decision_analysis_matches_RESULTS", da["battery_level_outcome"] == res["battery_level_outcome"]
      and all(da["arms"][a]["meets_expectation"] for a in ("J4", "J3", "J2", "J1", "GUARD")))

# --- 6. budget compliance ---
st = res["budget"]
check("X.budget_within_declared", st["elapsed_seconds"] == 744 <= 2700 and st["runs_used"] == 7 <= 8 and not st["halted_at_stop"])

# --- 7. validator artifacts parse ---
for f in ("v1_recount_controls.json", "v2_fresh_derivation.json", "v3_j4_table.json"):
    try:
        load(MINE + f)
        ok = True
    except Exception as e:
        ok = False
    check(f"X.validator_artifact_parses:{f}", ok)

out["battery_outcome_validator_derived"] = battery
out["fails"] = fails
out["n_checks"] = len(out["checks"])
with open(MINE + "v4_crosscheck.json", "w") as f2:
    json.dump(out, f2, indent=1)
print(json.dumps({"n_checks": out["n_checks"], "fails": fails, "battery": battery}, indent=1))
