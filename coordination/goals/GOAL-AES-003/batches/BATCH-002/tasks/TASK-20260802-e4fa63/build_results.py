import json, math, os, sys, subprocess, time, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze
D = os.path.dirname(os.path.abspath(__file__))
os.chdir(D)

ARMS = json.load(open("arms_meta.json"))
env = json.load(open("environment.json"))
pin = json.load(open("pin_receipt.json"))
geom = json.load(open("geom.json"))
pc = json.load(open("arm_PC.json"))

def arm_block(meta):
    f = "arm_%s.json" % meta["name"]
    if not os.path.exists(f) or os.path.getsize(f) == 0:
        return {"arm": meta["name"], "role": meta["role"], "status": "NOT RUN",
                "reason": meta.get("not_run_reason", "not reached before the binding stop"),
                "command": meta["command"]}
    a = json.load(open(f))
    s = analyze.summarize(a)
    s["role"] = meta["role"]
    s["object_description"] = meta["object"]
    s["command"] = meta["command"]
    s["exit_status"] = meta["exit_status"]
    s["wall_seconds"] = meta["wall_seconds"]
    s["status"] = "completed"
    s["Z_goodness_of_fit_vs_binomial_16_2e-8"] = analyze.zchi2(a)
    return s

blocks = {m["name"]: arm_block(m) for m in ARMS}

# ---- pooled measured PRP null ----
null_arms = [b for k, b in blocks.items() if b.get("role") == "measured_prp_null"
             and b.get("status") == "completed"]
null_N = sum(b["nontrivial_trials"] for b in null_arms)
null_k = sum(b["W_ge1_observed"] for b in null_arms)
null_lam_analytic = sum(b["W_ge1_expected_analytic_PRP_null"] for b in null_arms)
measured_rate = null_k / null_N if null_N else None
analytic_rate = float(analyze.P_EXACT)

null_cmp = {
    "measured_null_arms": [b["arm"] for b in null_arms],
    "measured_null_total_nontrivial_trials": null_N,
    "measured_null_W_ge1_count": null_k,
    "measured_null_per_trial_rate": measured_rate,
    "analytic_null_per_trial_rate": analytic_rate,
    "analytic_null_per_trial_rate_expression": "1-(1-2^-32)^4, i.e. 2^-30 to first order",
    "measured_over_analytic_ratio": (measured_rate/analytic_rate) if measured_rate else None,
    "expected_count_under_analytic_null": null_lam_analytic,
    "poisson_99pct_interval_under_analytic_null": list(analyze.pois_interval(null_lam_analytic, 0.99)),
    "measured_count_inside_99pct_interval": None,
    "agreement_verdict": None,
}
lo, hi = null_cmp["poisson_99pct_interval_under_analytic_null"]
inside = (lo <= null_k <= hi)
null_cmp["measured_count_inside_99pct_interval"] = inside
null_cmp["agreement_verdict"] = (
    "AGREE: the empirically measured PRP null is inside the 99% Poisson interval of the "
    "analytic null, so on this data the analytic table used by BATCH-001 is not contradicted."
    if inside else
    "DISAGREE: the measured null falls outside the 99% Poisson interval of the analytic null. "
    "V5 fires and every other arm in this session is VOID.")

# ---- AES arms scored against the measured null ----
scored = {}
for k, b in blocks.items():
    if b.get("status") != "completed" or b.get("role") not in ("main", "replicate", "r6", "structure_destroyed"):
        continue
    N = b["nontrivial_trials"]; obs = b["W_ge1_observed"]
    lam_meas = measured_rate * N if measured_rate else None
    ts = analyze.two_sample_conditional(obs, N, null_k, null_N)
    scored[k] = {
        "observed": obs,
        "expected_under_analytic_null": b["W_ge1_expected_analytic_PRP_null"],
        "excess_factor_vs_analytic_null": b["excess_factor_vs_analytic"],
        "expected_under_measured_null": lam_meas,
        "excess_factor_vs_measured_null": (obs/lam_meas) if lam_meas else None,
        "two_sample_exact_conditional_test_vs_measured_null": ts,
        "poisson_log10_tail_p_vs_analytic_null": b["poisson_log10_tail_p_ge_obs_under_analytic_null"],
    }

# ---- preregistered non-replication criteria, applied to the main arm ----
main = blocks["A1"]
N1 = main["nontrivial_trials"]; k1 = main["W_ge1_observed"]
lam1 = main["W_ge1_expected_analytic_PRP_null"]
lo1, hi1 = analyze.pois_interval(lam1, 0.99)
N1_fired = (lo1 <= k1 <= hi1)
p_two = scored["A1"]["two_sample_exact_conditional_test_vs_measured_null"]["p_exact_float"]
N2_fired = (p_two > 1e-3)

# ---- false-positive rate framing (wording defect fix) ----
thr = 40
fpr_ntrial = analyze.pois_tail_ge(thr, lam1)                 # analytic null
def pois_log10_lower_tail_lt(k, lam):
    """log10 P(X < k) for Poisson(lam), summed downward in log space so that a tail
    far below double precision is reported as a number rather than as a negative zero."""
    if k <= 0: return float("-inf")
    logt = -lam + (k-1)*math.log(lam) - math.lgamma(k)   # term at i = k-1
    tot = 1.0; t = 1.0; i = k-1
    while i > 0 and t > 1e-18:
        t *= i/lam; i -= 1; tot += t
    return (logt + math.log(tot))/math.log(10)

log10_fnr = pois_log10_lower_tail_lt(thr, float(k1))     # alt rate = the measured r=5 count
fnr_ntrial = 10.0**log10_fnr if log10_fnr > -300 else 0.0
fpr_measnull = analyze.pois_tail_ge(thr, measured_rate * N1) if measured_rate else None
fp = {
  "TERMINOLOGY_NOTE": (
    "The BATCH-001 validator identified that a quantity called a 'distinguishing advantage' "
    "of 2^-46 is in fact a FALSE-POSITIVE RATE against the control. The number was right and "
    "the word was wrong in a way that flattered the result. This artifact uses 'false-positive "
    "rate' for that quantity and reserves 'advantage' for its correct meaning. A test with no "
    "false negatives and false-positive rate p has distinguishing advantage ~1-p, which is "
    "close to 1, not to p."),
  "single_trial_test": {
    "rule": "flag a trial when W >= 1",
    "false_positive_rate_per_trial_MEASURED": measured_rate,
    "false_positive_rate_per_trial_ANALYTIC": analytic_rate,
    "true_positive_rate_per_trial_MEASURED_at_r5": k1/N1,
    "advantage_correctly_stated": (k1/N1) - measured_rate,
    "advantage_exact_form": "TPR - FPR",
    "advantage_note": ("TPR - FPR. This single-trial test has an enormous FALSE-NEGATIVE rate, "
                       "so the 1-p form does NOT apply to it and is not used."),
  },
  "counting_test_over_N_trials": {
    "rule": "run N = %d trials and flag the cipher when the W>=1 count is >= %d" % (N1, thr),
    "threshold": thr,
    "false_positive_rate_under_analytic_null": fpr_ntrial,
    "false_positive_rate_under_measured_null": fpr_measnull,
    "false_negative_rate_at_the_measured_r5_rate": fnr_ntrial,
    "false_negative_rate_log10": log10_fnr,
    "false_negative_rate_note": ("computed in log space; it is far below double precision, which is "
                                 "why it is also reported as a log10 value. An earlier draft of this "
                                 "script obtained it as 1 - upper_tail and got a NEGATIVE rate of "
                                 "-4.26e-14, a pure floating-point artifact; that draft was corrected "
                                 "before the number was reported and the defect is recorded here "
                                 "rather than silently dropped."),
    "advantage_correctly_stated": 1.0 - fpr_ntrial - fnr_ntrial,
    "advantage_exact_form": "1 - FPR - FNR = 1 - %.3e - 10^%.1f" % (fpr_ntrial, log10_fnr),
    "advantage_note": ("1 - FPR - FNR. Here the false-negative rate is negligible, so the "
                       "1-p form is legitimate and the advantage is close to 1, NOT close to "
                       "the false-positive rate."),
  },
}

# ---- death round MEASURED BY THIS CAMPAIGN ----
alive = []
for nm in ("A1", "A1b", "A2", "A2b"):
    b = blocks.get(nm)
    if not b or b.get("status") != "completed": continue
    sc = scored.get(nm)
    if sc and sc["two_sample_exact_conditional_test_vs_measured_null"]["p_exact_float"] < 1e-3:
        alive.append((b["rounds"], nm))
death = {
  "arms_significant_vs_measured_null_p_lt_1e-3": sorted(set(r for r, _ in alive)),
  "largest_r_alive_MEASURED_BY_THIS_SESSION": (max(r for r, _ in alive) if alive else None),
  "death_round_MEASURED_BY_THIS_SESSION": (max(r for r, _ in alive) + 1 if alive else None),
  "scope": ("MEASURED BY THIS CAMPAIGN, on this object, this statistic, these round counts, "
            "these trial counts and this instrument. NO comparison is made to any published "
            "death round in either direction; this repository cannot adjudicate that."),
  "power_caveat": None,
}
def pois_upper(k, alpha=0.05):
    """one-sided upper confidence bound on the Poisson mean given an observed count k:
    the largest lam with P(X <= k | lam) >= alpha, by bisection."""
    def cdf(lam):
        tot=0.0; t=math.exp(-lam)
        for i in range(k+1):
            tot+=t; t*=lam/(i+1)
        return tot
    lo_, hi_ = 0.0, max(10.0, 4.0*(k+1))
    while cdf(hi_) > alpha: hi_ *= 2
    for _ in range(200):
        mid=(lo_+hi_)/2
        if cdf(mid) > alpha: lo_=mid
        else: hi_=mid
    return (lo_+hi_)/2

for nm, b in blocks.items():
    if b.get("status")=="completed":
        b["excess_factor_95pct_upper_bound"] = pois_upper(b["W_ge1_observed"]) / b["W_ge1_expected_analytic_PRP_null"]

r6 = [b for nm,b in blocks.items() if b.get("role")=="r6" and b.get("status")=="completed"]
if r6:
    ub = min(b["excess_factor_95pct_upper_bound"] for b in r6)
    death["power_caveat"] = (
        "The r=6 arms read no usable signal, and that is a bound, not a proof of absence. "
        "Their tightest one-sided 95%% upper bound on the r=6 excess factor is %.2fx "
        "(observed counts %s against analytic expectations %s), so an r=6 excess smaller than "
        "that is NOT excluded by this session. 'Death at r=6' here means 'no excess detectable "
        "at these trial counts with this statistic', never 'no excess exists'." % (
            ub, [b["W_ge1_observed"] for b in r6],
            [round(b["W_ge1_expected_analytic_PRP_null"],2) for b in r6]))

PRED = {
 "PR-0 pin": {"predicted": "FIPS-197 C.1 KAT exact both directions; 0 round-trip failures over >=512 vectors x r=1..10"},
 "PR-1 positive control r=2": {"predicted": "W = 3 in 100% of non-trivial trials"},
 "PR-2 A1 r=5 excess factor": {"predicted_point": 16.0, "predicted_band": [8.0, 25.0]},
 "PR-3 A2 r=6 excess factor": {"predicted_point": 1.0, "predicted_band": [0.0, 3.0]},
 "PR-4 measured PRP null excess factor": {"predicted_point": 1.0,
   "predicted": "measured null agrees with analytic 2^-30 within Poisson error"},
 "PR-5 A4 structure-destroyed excess factor": {"predicted_point": 1.0, "predicted_band": [0.0, 3.0]},
 "PR-6 death round": {"predicted": 6, "predicted_note": "largest r alive predicted to be 5"},
}
PRED["PR-0 pin"]["measured"] = {
  "kat_encrypt_match": pin["fips197_c1_kat_encrypt_match"],
  "kat_decrypt_match": pin["fips197_c1_kat_decrypt_match"],
  "kat_ciphertext_computed": pin["fips197_c1_kat_ciphertext_computed"],
  "roundtrip_checks": pin["roundtrip_checks"], "roundtrip_failures": pin["roundtrip_failures"]}
PRED["PR-0 pin"]["outcome"] = "MET" if pin["pin_pass"] else "FAILED -> V2, every arm VOID"
pc_all = (pc["whist"][3] == pc["nontrivial_trials"])
PRED["PR-1 positive control r=2"]["measured"] = {
  "nontrivial_trials": pc["nontrivial_trials"], "whist": pc["whist"],
  "fraction_with_W_eq_3": pc["whist"][3]/pc["nontrivial_trials"]}
PRED["PR-1 positive control r=2"]["outcome"] = "MET" if pc_all else "FAILED -> V1"
def band(nm, key, lo_, hi_):
    b = blocks.get(nm)
    if not b or b.get("status")!="completed":
        PRED[key]["measured"] = "NOT RUN"; PRED[key]["outcome"] = "NOT RUN"; return
    x = b["excess_factor_vs_analytic"]
    PRED[key]["measured_excess_factor"] = x
    PRED[key]["measured_counts"] = {"observed": b["W_ge1_observed"],
                                    "expected_analytic": b["W_ge1_expected_analytic_PRP_null"],
                                    "nontrivial_trials": b["nontrivial_trials"]}
    PRED[key]["outcome"] = "INSIDE predicted band" if lo_ <= x <= hi_ else "OUTSIDE predicted band"
band("A1", "PR-2 A1 r=5 excess factor", 8.0, 25.0)
band("A2", "PR-3 A2 r=6 excess factor", 0.0, 3.0)
band("A4", "PR-5 A4 structure-destroyed excess factor", 0.0, 3.0)
PRED["PR-4 measured PRP null excess factor"]["measured_excess_factor"] = (
    null_cmp["measured_over_analytic_ratio"])
PRED["PR-4 measured PRP null excess factor"]["measured_counts"] = {
    "observed": null_k, "expected_analytic": null_lam_analytic,
    "nontrivial_trials": null_N}
PRED["PR-4 measured PRP null excess factor"]["outcome"] = (
    "MET (measured null inside the 99% Poisson interval of the analytic null)" if inside
    else "FAILED -> V5")
PRED["PR-6 death round"]["measured"] = death["death_round_MEASURED_BY_THIS_SESSION"]
PRED["PR-6 death round"]["outcome"] = ("MET" if death["death_round_MEASURED_BY_THIS_SESSION"] == 6
                                       else "DIFFERS FROM PREDICTION")

TABLE = []
for m in ARMS:
    b = blocks[m["name"]]
    if b.get("status") != "completed":
        TABLE.append({"arm": m["name"], "role": m["role"], "status": "NOT RUN",
                      "reason": b.get("reason")}); continue
    TABLE.append({
      "arm": m["name"], "role": m["role"], "object": m["object"],
      "rounds": b["rounds"], "amask": b["amask"], "smask": b["smask"],
      "trials": b["trials"], "nontrivial_trials": b["nontrivial_trials"],
      "trivial_swaps_excluded": b["trivial_swaps_excluded"],
      "seed": b["seed"], "arm_id": b["arm_id"], "key_hex": b["key_hex"],
      "thread_seeds": b["thread_seeds"],
      "HIT_COUNT_W_ge1": b["W_ge1_observed"],
      "NULL_EXPECTATION_analytic": b["W_ge1_expected_analytic_PRP_null"],
      "excess_factor": b["excess_factor_vs_analytic"],
      "excess_factor_95pct_upper_bound": b["excess_factor_95pct_upper_bound"],
      "resolution_bits": b["resolution_bits"],
      "whist": b["whist"],
    })

out = {
  "schema": "crypto.autoresearch.task_results.v1",
  "task_id": "TASK-20260802-e4fa63",
  "title": "RANK 3: independent re-execution of the yoyo objects at r=5 and r=6",
  "goal_id": "GOAL-AES-003", "batch": "BATCH-002", "role": "executor",
  "claim_tier": "toy",
  "certificate": {"kind": "none",
                  "basis": "pure measurement run; no solve, no relation, no key recovery is claimed or required"},
  "inference": {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model": "claude-opus-5",
    "resolved_model_basis": ("self-reported by the running session's own system context; no adapter "
                             "probe was executed, so this resolution is not independently verified"),
    "fallback_used": True,
    "fallback_basis": ("orchestration/model-policies.yaml names GPT-5.6-family policy aliases that "
                       "Claude Code cannot resolve; every subagent in this harness runs model: inherit"),
    "model_verified": False,
    "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
    "independence_note": ("This session supplies SESSION and IMPLEMENTATION independence from both "
                          "prior implementations and supplies NO MODEL independence. Nothing here "
                          "may count toward a closure quorum."),
  },
  "headline_table_hit_count_beside_null_expectation": TABLE,
  "headline_statements": [
    "PIN: the probe reproduces FIPS-197 C.1 exactly in both directions and passes 5120/5120 "
    "enc/dec round-trip checks over r=1..10 on 512 random (key,plaintext) vectors, 0 failures.",
    "GEOMETRY: plaintext-side words are forward diagonals (PW[0]={0,5,10,15}); ciphertext-side "
    "words are INVERSE-ShiftRows diagonals (CW[0]={0,13,10,7}). The probe emits both tables and "
    "they match the preregistration, so the object built here is the object BATCH-001 measured.",
    "r=5 REPLICATES in a third, independent implementation: 125 hits against an analytic null "
    "expectation of 8.0 over 2^33 trials, an excess factor of 15.6x; and on an independent key at "
    "2^32, 60 hits against 4.0, an excess factor of 15.0x.",
    "MEASURED PRP NULL: 12 hits over 2^34 trials against an analytic expectation of 16.0, a "
    "measured/analytic ratio of 0.75, inside the 99% Poisson interval [6,27]. The empirical null "
    "AGREES with the analytic table; this is the specific gap the task named and it is now closed "
    "on this data.",
    "r=6: 6 hits against 4.0 at 2^32 and 7 against 8.0 at 2^33. No usable signal, confirming "
    "BATCH-001's reading, with a one-sided 95% upper bound of 1.64x on any r=6 excess.",
    "STRUCTURE-DESTROYED CONTROL: 4 hits against 4.0, an excess factor of 1.0. The r=5 excess "
    "does not survive destroying the diagonal-coset structure, so it is not a pipeline artifact.",
  ],
  "environment": env,
  "geometry_used": geom,
  "cipher_pin": pin,
  "positive_control": pc,
  "arms": blocks,
  "measured_vs_analytic_null": null_cmp,
  "arms_scored_against_measured_null": scored,
  "preregistered_non_replication_criteria": {
    "N1_count_inside_99pct_poisson_interval_of_analytic_null": {
      "interval": [lo1, hi1], "observed": k1, "fired": bool(N1_fired)},
    "N2_not_significant_vs_measured_null_p_gt_1e-3": {
      "p": p_two, "fired": bool(N2_fired)},
    "verdict": ("NEITHER non-replication criterion fired: the r=5 reading REPLICATES in this "
                "independent third implementation."
                if not (N1_fired or N2_fired) else
                "A non-replication criterion FIRED; see the fields above."),
  },
  "false_positive_rate_and_advantage": fp,
  "death_round": death,
  "predictions_vs_measured": PRED,
  "exact_commands": [
    {"step": "build", "command": "gcc -O2 -maes -msse4.1 -pthread -o probe probe.c",
     "exit_status": 0, "cwd": "coordination/goals/GOAL-AES-003/batches/BATCH-002/tasks/TASK-20260802-e4fa63"},
    {"step": "geometry emit", "command": "./probe geom > geom.json", "exit_status": 0},
    {"step": "cipher pin", "command": "./probe pin 424242001 > pin_receipt.json", "exit_status": 0},
    {"step": "positive control", "command": "./probe arm PC 2 1 1 20 424242001 1 4 > arm_PC.json", "exit_status": 0},
  ] + [{"step": "arm " + m["name"], "command": m.get("command"),
        "exit_status": m.get("exit_status"), "wall_seconds": m.get("wall_seconds")} for m in ARMS] + [
    {"step": "analysis", "command": "python3 build_results.py  (imports analyze.py)", "exit_status": 0},
  ],
  "argument_order": "./probe arm <name> <rounds> <amask> <smask> <log2N> <seed> <arm_id> <threads>",
  "void_conditions": {
    "V1 positive control r=2 not 100% W=3": {"fired": not pc_all,
      "reading": "W=3 in %d of %d non-trivial trials" % (pc["whist"][3], pc["nontrivial_trials"])},
    "V2 pin failure": {"fired": not pin["pin_pass"],
      "reading": "KAT exact both directions; %d/%d round-trip checks passed" % (
        pin["roundtrip_checks"]-pin["roundtrip_failures"], pin["roundtrip_checks"])},
    "V3 emitted geometry differs from PREREGISTRATION sec.2": {
      "fired": not (geom["PW"] == [[0,5,10,15],[4,9,14,3],[8,13,2,7],[12,1,6,11]] and
                    geom["CW"] == [[0,13,10,7],[4,1,14,11],[8,5,2,15],[12,9,6,3]]),
      "reading": {"PW": geom["PW"], "CW": geom["CW"]}},
    "V4 excess flat across r and still present at r=10": {
      "fired": any(scored.get(nm, {}).get("two_sample_exact_conditional_test_vs_measured_null", {}).get("p_exact_float", 1) < 1e-3
                   for nm in ("A3", "A3b")),
      "reading": "the r=10 arms ARE the measured null arms and read 5 and 7 against an analytic 8.0 each; the excess is not flat across r"},
    "V5 measured null departs from the analytic null": {"fired": not inside,
      "reading": null_cmp["agreement_verdict"]},
    "V6 unexcluded degenerate trials": {"fired": False,
      "reading": ("p0=p1 and zero-difference active words are excluded by rejection sampling inside "
                  "the trial loop; trivial swaps (c0=c1 on the swapped word) are detected, excluded "
                  "from every histogram and COUNTED per arm; smask 0 and 15 are rejected by the "
                  "binary with exit 3. Trivial-swap counts per arm: " +
                  str({m["name"]: blocks[m["name"]].get("trivial_swaps_excluded") for m in ARMS
                       if blocks[m["name"]].get("status") == "completed"}))},
    "V7 wall-clock halt": {"fired": False,
      "reading": "all seven arms completed before the binding stop at 2026-08-02T18:07:28Z"},
  },
  "checks_that_did_not_run": [
    {"check": "swap-mask sweep over S other than {0}", "reason":
     "budget priority went to the four mandated arms plus a replicate and two extra null arms. "
     "NOT RUN, therefore this session says nothing about the S-dependence of the excess."},
    {"check": "active-mask sweep at intermediate A ({0,1} and {0,1,2})", "reason":
     "not reached; only the two extremes A={0} (main) and A={0,1,2,3} (structure-destroyed) were run."},
    {"check": "iterated / multi-generation yoyo", "reason": "not reached before the binding stop."},
    {"check": "arms at r=3, r=4 and r=7", "reason":
     "not mandated by this task card and not reached; the death-round statement is therefore "
     "bracketed only by the r=5 and r=6 arms actually run, plus the r=10 null arms."},
    {"check": "second structure-destroyed control at 2^33", "reason":
     "not reached; the single A4 arm at 2^32 has an expectation of only 4.0 and is correspondingly thin."},
    {"check": "adapter probe to verify the resolved model identifier", "reason":
     "no adapter probe exists in this harness; model_verified is recorded false and the resolved "
     "model is self-reported, not verified."},
    {"check": "independent re-verification of a solution certificate", "reason":
     "not applicable: this is a pure measurement run with certificate.kind none. No solve or "
     "relation is claimed."},
  ],
  "protocol_deviations": [
    {"deviation": "Two arms were added that the preregistration did not list: A3b (a second "
                  "measured PRP null at 2^33) and A2b (a second r=6 arm at 2^33).",
     "direction": "ADDS null and control data, does not add AES signal arms",
     "when": "launched at 2026-08-02T17:33Z, AFTER the five preregistered arms had completed and "
             "after A1 had already been read",
     "handling": "recorded here rather than absorbed. Both are reported with their own seeds and "
                 "keys; the pooled measured null and the r=6 statement both use them, and both "
                 "readings are individually reported so a reviewer can recompute with A3/A2 alone. "
                 "Neither addition changes the r=5 verdict: A1 against the A3-only null gives "
                 "p = 2.19e-31, against the pooled null p = 1.03e-45."},
    {"deviation": "The preregistration set N >= 2^32 per arm without fixing a per-arm N; A1 and "
                  "A3 were run at 2^33 and A2, A4, A1b at 2^32.",
     "handling": "each arm reports its own N, its own expectation and its own resolution in bits; "
                 "no arm is compared to another at a different N except through rate-based tests."},
  ],
  "reproduction": {
    "reproduction_check_performed": {
      "command": "./probe arm A1b 5 1 1 32 777000333 15 4 > repro_A1b.json",
      "exit_status": 0,
      "result": "BYTE-IDENTICAL to arm_A1b.json (diff empty), so the declared arm reproduces "
                "exactly from the recorded command at git commit 41414e805b68374bcf40f8cfc0eb796e88ebfc56",
      "utc_start": "2026-08-02T17:52:43Z", "utc_end": "2026-08-02T17:54:36Z"},
    "steps": ["gcc -O2 -maes -msse4.1 -pthread -o probe probe.c",
              "./probe pin 424242001", "./probe geom",
              "then each arm command in exact_commands", "python3 build_results.py"],
    "determinism": ("every arm is fully determined by its (rounds, amask, smask, log2N, seed, arm_id, "
                    "threads) tuple: keys derive from seed ^ 0xA5A5..., per-thread splitmix64 streams "
                    "derive from seed ^ arm_id*0x1234567891 ^ (thread+1)*0x9E3779B97F4A7C15. Thread "
                    "count changes the trial-to-stream assignment, so reproduction requires threads=4."),
    "note": "no wall-clock timing enters any reported statistic; timings are recorded for budget only.",
  },
  "scope_and_prohibitions": [
    "claim_tier toy. NOTHING here is a statement about full-round or deployed AES.",
    "NO comparison is made to published cryptanalysis in either direction, and no novelty "
    "assessment is made in either direction (RQ-AES-003 R3; DEC-20260731-019 ruling 3).",
    "The measured death round is reported AS MEASURED BY THIS CAMPAIGN only, with no comparison "
    "to any published death round in either direction.",
    "This session records observations. It does not declare any hypothesis supported, rejected or "
    "closed, and does not declare any heuristic validated or refuted. That judgment belongs to the "
    "Reviewer and the Coordinator.",
    "Per DEC-20260802-9bda5c ruling 3, the r=4 and r=5 properties of this campaign are NOT "
    "AES-S-box-specific; this session measured the yoyo object on real AES-128 only and ran no "
    "random-S-box arm, so it contributes no new evidence on that relabelling in either direction.",
  ],
  "ledger_reading_note": ("This session read ledger/decisions/DEC-20260802-007.yaml as named in its "
                          "task card. During the session the dispatch queue was updated to name "
                          "DEC-20260802-9bda5c instead. Both files exist; a diff shows the content "
                          "is identical apart from the identifier and an added id_remap_note, so no "
                          "reading in this artifact depends on which identifier is canonical."),
  "budget": {
    "declared_wall_clock_seconds": 3600, "declared_memory_gb": 16,
    "start_utc": "2026-08-02T17:07:28Z", "binding_stop_utc": "2026-08-02T18:07:28Z",
    "halted_on_budget": False,
    "dropped_work": ["swap-mask sweep", "intermediate active-mask sweep", "iterated yoyo",
                     "r=3, r=4 and r=7 arms", "second structure-destroyed control at 2^33"],
    "peak_memory": "not separately instrumented; the probe allocates only per-thread histograms "
                   "(a few hundred bytes each) and holds no table, so resident set stays far below "
                   "the 16 GB cap. Recorded as not measured rather than estimated.",
    "runs_used": 10, "maximum_runs": 24,
  },
}
json.dump(out, open("RESULTS.json", "w"), indent=1)
print("wrote RESULTS.json")
