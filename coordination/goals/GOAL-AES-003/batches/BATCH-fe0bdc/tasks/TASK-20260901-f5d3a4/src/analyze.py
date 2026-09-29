#!/usr/bin/env python3
# analyze.py -- TASK-20260901-f5d3a4 RUN 6. Applies the pre-registered
# decision rule of IDEA-20260901-04606c (PREREGISTRATION.md section 5) to
# the run receipts; re-verifies the census digest after the fixture arm;
# checks the preregistration mtime ordering; parses every JSON artifact
# whole and attests. Writes runs/decision_analysis.json and
# runs/parse_check.txt. NO status/strength/promotion interpretation.
import json, sys, os, hashlib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
RUNS = os.path.join(TASK, "runs")
N = 1 << 30
EXCESS_E = 1 << 30          # frozen excess_E = 2^30 (record PR-4)
BAND_FLOOR = N - 8          # acceptance band hits >= 2^30 - 8 (record PR-4)

def load(name):
    p = os.path.join(RUNS, name)
    with open(p) as f:
        return json.load(f), p

gate, _ = load("gate0.json")
census_raw = open(os.path.join(RUNS, "census.json")).read()
census = json.loads(census_raw)
bridge, _ = load("keyed_bridge.json")
arm, _ = load("fixture_arm.json")

census_digest_now = hashlib.sha256(census_raw.encode()).hexdigest()

# ---- preregistration mtime ordering ----
pre_mtime = os.path.getmtime(os.path.join(TASK, "PREREGISTRATION.md"))
run_files = ["gate0.json", "census.json", "keyed_bridge.json", "fixture_arm.json",
             "gate0.stdout", "census.stdout", "keyed_bridge.stdout",
             "fixture_arm.timing.txt"]
mtime_check = []
for rf in run_files:
    p = os.path.join(RUNS, rf)
    if os.path.exists(p):
        mtime_check.append({"file": f"runs/{rf}", "mtime": os.path.getmtime(p),
                            "after_preregistration": os.path.getmtime(p) >= pre_mtime})
mtime_ok = all(e["after_preregistration"] for e in mtime_check)

# ---- decision rule inputs ----
gate_pass = gate["gate0_pass"]
census_match = census["all_100_instances_match_preregistration"]
bridge_pass = bridge["bridge_pass"]

T = arm["trivial_swaps_excluded"]
NT = arm["nontrivial_trials"]
hits = arm["W_ge1_nontrivial"]
whist = arm["whist"]
wword = arm["W_ge1_by_word"]
trials = arm["trials"]

law_exact = (whist[3] == NT and whist[0] == 0 and whist[1] == 0
             and whist[2] == 0 and whist[4] == 0)
hits_identity = (hits == NT)
band_ok = hits >= BAND_FLOOR
excess = hits * EXCESS_E / (NT if NT else 1)      # hits / (NT * 2^-30)
ratio_rel = excess / EXCESS_E
ratio_ok = abs(ratio_rel - 1.0) <= 2.0 ** -20
E_T = N * 2.0 ** -32
wword_expected = (wword == [0, NT, NT, NT])
arm_ok = bool(law_exact and hits_identity and band_ok and ratio_ok and wword_expected
              and trials == N and NT == N - T)

with open(os.path.join(RUNS, "census.json.digest.txt")) as f:
    census_digest_run2 = f.read().split()[0]
digest_unchanged = (census_digest_now == census_digest_run2)

if not gate_pass:
    verdict = "GATE-FAIL (F1): invalid_measurement; halt; all prospective census readings VOID; no mechanism conclusion"
    arm_fired = "gate halt"
elif not census_match:
    verdict = "CENSUS-FAIL (F3): table void; convention/port defect; halt; no mechanism conclusion"
    arm_fired = "census-mismatch"
elif not (bridge_pass and arm_ok):
    verdict = "PIPELINE-FAIL (F2): instrument indicted; escalate to 02f7c4 battery + independent review; no mechanism conclusion"
    arm_fired = "defect"
else:
    verdict = ("CONFIRMED-MISMATCH-ALIVE: the pinned instrument's affine-limit trial map is the identity "
               "(flat census); the skeleton is alive at every r <= 10 including r=6 where AES is measured "
               "dead; the death round is not carried by the linear skeleton and is nonlinearity-driven "
               "(toy-tier conclusion under the record's decision rule, citing this record's artifacts plus "
               "EV-AES-048545, EV-AES-64750e, EV-AES-d33b1c)")
    arm_fired = "MISMATCH-ALIVE"

out = {
    "schema": "crypto.autoresearch.decision046.v1",
    "task_id": "TASK-20260901-f5d3a4",
    "idea_record": "IDEA-20260901-04606c",
    "decision_rule_source": "PREREGISTRATION.md section 5 (verbatim from record preregistered_decision_rule)",
    "inputs": {
        "gate0_pass": gate_pass,
        "census_all_100_match": census_match,
        "bridge_pass": bridge_pass,
        "fixture_arm": {
            "trials": trials, "trivial_T": T, "nontrivial": NT,
            "hits_W_ge1_nontrivial": hits,
            "E_T_preregistered": E_T,
            "whist": whist, "whist_all_W3_on_nontrivial": law_exact,
            "W_ge1_by_word": wword, "wword_matches_identity_prediction": wword_expected,
            "hits_equal_2^30_minus_T": hits_identity,
            "acceptance_band_floor_2^30-8": BAND_FLOOR,
            "in_band": band_ok,
            "excess_ratio_vs_frozen_excess_E": ratio_rel,
            "excess_ratio_within_1pm2^-20": ratio_ok,
            "arm_ok": arm_ok,
        },
        "census_digest_sha256_after_arm": census_digest_now,
        "census_digest_sha256_at_RUN2": census_digest_run2,
        "census_digest_unchanged_since_RUN2": digest_unchanged,
        "preregistration_mtime": pre_mtime,
        "run_file_mtimes_after_preregistration": mtime_check,
        "mtime_order_ok": mtime_ok,
    },
    "verdict_arm": arm_fired,
    "verdict": verdict,
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "parse_attestation": "this file is machine-generated JSON; parsed whole with python3 json.load before task completion (stated in RESULTS.json)",
    "inference": {
        "policy": "executor-implementation",
        "requested_policy": "executor-implementation",
        "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
        "model_verified": False,
        "fallback_used": True,
        "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
        "degraded_requirements": [],
        "amendment": "DEC-20260831-0d1eeb",
        "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
    },
}
txt = json.dumps(out, indent=1)
with open(os.path.join(RUNS, "decision_analysis.json"), "w") as f:
    f.write(txt)

# ---- parse attestation of every JSON artifact ----
targets = ["gate0.json", "census.json", "keyed_bridge.json", "fixture_arm.json",
           "build_pin_cal.json", "decision_analysis.json"]
lines = []
all_parse = True
for t in targets:
    p = os.path.join(RUNS, t)
    try:
        with open(p) as f:
            json.load(f)
        lines.append(f"OK   {t}: parsed whole with python3 json.load")
    except Exception as e:
        all_parse = False
        lines.append(f"FAIL {t}: {e}")
lines.append(f"parse_all_ok: {all_parse}")
with open(os.path.join(RUNS, "parse_check.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")

print(json.dumps({"verdict_arm": arm_fired, "gate": gate_pass, "census": census_match,
                  "bridge": bridge_pass, "arm_ok": arm_ok, "T": T, "hits": hits,
                  "ratio_rel": ratio_rel, "digest_unchanged": digest_unchanged,
                  "mtime_ok": mtime_ok, "parse_all_ok": all_parse}, indent=1))
