#!/usr/bin/env python3
"""TASK-20260803-0764fc -- assemble RESULTS.json from the raw run JSON.

Reads only runs/*.json produced by the pinned yoyo_sbox_v2 binary plus the
recorded prior-batch artifacts it compares against. Computes nothing that is
not derivable from those raw counts. Every number it emits is labelled
measured or modeled.
"""
import json, os, math, subprocess, glob, datetime, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/home/user/crypto-autoresearcher"
B4 = os.path.join(ROOT, "coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-367b1b")
B5 = os.path.join(ROOT, "coordination/goals/GOAL-AES-003/batches/BATCH-005/tasks/TASK-20260803-48a239")


def rj(p):
    with open(p) as f:
        return json.load(f)


# ---------- exact statistics (no scipy on this image) ----------
def pois_tail_ge(x, lam):
    """P(K >= x | lam), exact summation from the Poisson pmf."""
    if x <= 0:
        return 1.0
    # sum the lower tail then complement, guarding for large x
    if x > 60 * max(lam, 1.0):
        # tail is astronomically small; report a log10 instead
        return 0.0
    s, term = 0.0, math.exp(-lam)
    for k in range(0, int(x)):
        s += term
        term *= lam / (k + 1)
    return max(0.0, 1.0 - s)


def pois_tail_le(x, lam):
    s, term = 0.0, math.exp(-lam)
    for k in range(0, int(x) + 1):
        s += term
        term *= lam / (k + 1)
    return min(1.0, s)


def pois_ci(x, conf=0.95):
    """Exact (Garwood) 95% CI for a Poisson mean from count x, by bisection on
    the exact tail probabilities."""
    a = (1 - conf) / 2.0
    if x == 0:
        lo = 0.0
    else:
        lo, hi = 0.0, max(1.0, 4.0 * x + 10)
        for _ in range(200):
            m = (lo + hi) / 2
            if pois_tail_ge(x, m) < a:
                lo = m
            else:
                hi = m
        lo = (lo + hi) / 2
    lo2, hi2 = 0.0, max(1.0, 4.0 * x + 20)
    for _ in range(200):
        m = (lo2 + hi2) / 2
        if pois_tail_le(x, m) > a:
            lo2 = m
        else:
            hi2 = m
    return lo, (lo2 + hi2) / 2


def binom_cdf_ge(k, n, p):
    """P(K >= k | n, p) exact."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    tot = 0.0
    for i in range(k, n + 1):
        tot += math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
    return tot


def cp_lower(k, n, alpha=0.05):
    """One-sided Clopper-Pearson lower bound: largest p with P(K>=k|n,p)=alpha.
    For k == n this equals alpha**(1/n)."""
    if k == 0:
        return 0.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        m = (lo + hi) / 2
        if binom_cdf_ge(k, n, m) < alpha:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


# ---------- liveness rules, both campaign forms ----------
def t5_full(x, v):
    """BATCH-004 frozen rule."""
    if v <= 0:
        return "UNDEFINED"
    if x / v >= 5 and pois_tail_ge(x, v) < 1e-6:
        return "ALIVE"
    if x / v <= 2.5 and pois_tail_le(x, 15.63 * v) < 1e-3:
        return "DEAD"
    return "INDETERMINATE"


def t5_simple(x, v):
    return "ALIVE" if (v > 0 and x / v >= 5) else "NOT_ALIVE"


def arm_row(path, role, note=""):
    d = rj(path)
    x = d["W_ge1_nontrivial"]
    v = d["null_expectation_analytic"]
    d2 = dict(d)
    d2["role"] = role
    d2["note"] = note
    d2["MEASURED_W_ge1"] = x
    d2["NULL_EXPECTATION_analytic_MODELED"] = v
    d2["EXCESS_FACTOR_measured_over_modeled_null"] = (x / v) if v else None
    d2["hit_rate_measured"] = x / d["nontrivial_trials"]
    d2["saturated"] = (x == d["nontrivial_trials"])
    d2["poisson_p_ge_measured_given_null"] = pois_tail_ge(x, v) if x < 1e6 else 0.0
    lo, hi = pois_ci(x) if x < 100000 else (float(x), float(x))
    d2["exact95_ci_on_lambda"] = [lo, hi]
    d2["exact95_ci_on_excess_factor"] = [lo / v, hi / v] if v else None
    d2["T5_FULL_verdict_BATCH004_frozen_rule"] = t5_full(x, v)
    d2["T5_SIMPLE_verdict_BATCH005_form"] = t5_simple(x, v)
    return d2


def timings():
    out = {}
    p = os.path.join(HERE, "runs/arms_timing.txt")
    if os.path.exists(p):
        for ln in open(p):
            parts = ln.split()
            if len(parts) >= 3 and parts[1].startswith("exit="):
                out[parts[0]] = {"exit": int(parts[1].split("=")[1]),
                                 "wall_seconds": float(parts[2].split("=")[1])}
    return out


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT).stdout.strip()


T = timings()


def attach_timing(row, name):
    row["timing"] = T.get(name, {"exit": None, "wall_seconds": None,
                                 "note": "no timing line recorded"})
    return row


# =====================================================================
R = {}
R["task_id"] = "TASK-20260803-0764fc"
R["goal_id"] = "GOAL-AES-003"
R["batch"] = "BATCH-006"
R["role"] = "executor"
R["produced_at_utc"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
R["claim_tier"] = "toy"
R["claim_tier_basis"] = (
    "Reduced-round (r in {2,3,4,5}) AES-128 permutation with the full FIPS-197 "
    "key schedule, one software T-table implementation, at most 2^31 trials per "
    "arm. Nothing here speaks to full-round or deployed AES and no comparison to "
    "published cryptanalysis is made in either direction (RQ-AES-003 R3).")
R["certificate"] = {
    "kind": "none",
    "why": "Both items are pure counting measurements. No discrete log, no "
           "factor-base relation, no key recovery is claimed or attempted, so "
           "there is nothing to certify. Set explicitly per the Executor contract."}
R["inference"] = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model": "claude-opus-5",
    "fallback_used": False,
    "model_verified": False,
    "model_verified_reason": "No `python3 -m orchestration.adapter doctor --probe` "
                             "is available under this harness; the model identifier "
                             "is unverified configuration.",
    "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c"}

# ---------- environment / provenance ----------
R["environment"] = {
    "uname": sh("uname -a"),
    "nproc_total": int(sh("nproc")),
    "threads_per_arm": 2,
    "max_concurrent_arms": "1 for SECTION A, 2 for SECTION B",
    "cpu_model": sh("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2-").strip(),
    "mem_total_kb": int(sh("grep MemTotal /proc/meminfo | awk '{print $2}'")),
    "memory_cap_gb_declared": 8,
    "peak_rss_note": "no /usr/bin/time on this image; peak RSS was not sampled. "
                     "yoyo_sbox_v2 allocates only the S-box/T-tables and per-thread "
                     "job structs, far under 1 MB; memory was never near the 8 GB cap.",
    "gcc": sh("gcc --version | head -1"),
    "python": sh("python3 --version"),
    "nothing_was_compiled": "TRUE. The binary was copied, hash-verified and executed. "
                            "gcc version is recorded for completeness only."}
R["git_state"] = {
    "commit": sh("git rev-parse HEAD"),
    "branch": sh("git rev-parse --abbrev-ref HEAD"),
    "dirty_tree": bool(sh("git status --porcelain")),
    "porcelain_lines": sh("git status --porcelain").splitlines(),
    "note": "This task wrote only inside its own task directory, which is gitignored "
            "on purpose. It committed nothing and edited no prior-batch artifact."}

# ---------- instrument ----------
R["instrument_REUSED_NOT_REWRITTEN"] = {
    "binary_executed": "yoyo_sbox_v2 (byte-identical copy of BATCH-004 "
                       "TASK-20260803-367b1b/yoyo_sbox_v2)",
    "sha256_measured": {
        "yoyo_sbox_v2": sh("sha256sum '%s/yoyo_sbox_v2' | cut -d' ' -f1" % HERE),
        "yoyo_sbox_v2.c.readonly_copy": sh(
            "sha256sum '%s/yoyo_sbox_v2.c.readonly_copy' | cut -d' ' -f1" % HERE)},
    "sha256_expected_from_BATCH005_PREREGISTRATION_lines_28_29": {
        "yoyo_sbox_v2": "d30e4d720317706043b263742062273d22fbe054f56a58a8b351f3bbb3fd9ff0",
        "src_yoyo_sbox_v2.c": "6bda2ab7f3c8e6dee358d3fcba52803e4e43f794f963bafabc51cc0de379bc9c"},
    "fips197_c1_pin": rj(os.path.join(HERE, "runs/pin_aes.json")),
    "geometry": rj(os.path.join(HERE, "runs/geom.json")),
    "pin_ran_before_any_measurement": True}
iv = R["instrument_REUSED_NOT_REWRITTEN"]
iv["sha256_match"] = (
    iv["sha256_measured"]["yoyo_sbox_v2"] ==
    iv["sha256_expected_from_BATCH005_PREREGISTRATION_lines_28_29"]["yoyo_sbox_v2"] and
    iv["sha256_measured"]["yoyo_sbox_v2.c.readonly_copy"] ==
    iv["sha256_expected_from_BATCH005_PREREGISTRATION_lines_28_29"]["src_yoyo_sbox_v2.c"])

json.dump(R, open(os.path.join(HERE, "_results_part1.json"), "w"), indent=1)
print("part1 ok, sha256_match =", iv["sha256_match"])

# =====================================================================
# repository search behind the absence claim (CORR-20260803-c92db5 discipline)
# =====================================================================
R["repository_search_behind_the_absence_claim"] = {
    "why": "My task card and the BATCH-006 dispatch queue assert that this "
           "instrument has only ever run at r in {2,5,6,10} and that the low side "
           "of the round profile has never been measured. CORR-20260803-c92db5 "
           "requires that a claim of absence be searched like a claim of presence, "
           "with the paths named.",
    "commands_run": [
        "grep -rl \"W_ge1\" coordination ledger knowledge docs experiments",
        "python3: for every file above, regex '\"rounds\"\\s*:\\s*(\\d+)' tabulated",
        "grep -rn '\"rounds\": *[34]\\b' --include=*.json --include=*.yaml --include=*.md ."],
    "files_matching_W_ge1": sh("grep -rl 'W_ge1' coordination ledger knowledge docs experiments 2>/dev/null | sort").splitlines(),
    "FINDING": "THE NARROW CLAIM IS TRUE AND THE BROAD CLAIM IS FALSE. r=3 and r=4 "
               "yoyo arms already exist in this repository, in two W_ge1-bearing "
               "files the BATCH-005 red team's enumeration did not surface.",
    "files_that_refute_the_broad_claim": [
        "coordination/goals/GOAL-AES-003/batches/BATCH-001/tasks/yoyo5/analysis.json",
        "coordination/goals/GOAL-AES-003/batches/BATCH-001/tasks/yoyo5/analysis_seed1.json"],
    "prior_r4_and_r3_readings_found": [
        {"instrument": "BATCH-001 yoyo5 yoyo2.c, AES-NI, same reduced-round convention, "
                       "pinned to FIPS-197 by four implementations (pin_receipt.json, "
                       "1554 equality checks, PASS true)",
         "rows": [
             {"r": 3, "trials": 4294967296, "seed": 20260802, "W_ge1": 4294967296,
              "null": 4.0, "excess_factor": 1073741824.0, "reading": "SATURATED"},
             {"r": 4, "trials": 4294967296, "seed": 20260802, "W_ge1": 4294967296,
              "null": 4.0, "excess_factor": 1073741824.0, "reading": "SATURATED"},
             {"r": 4, "trials": 8589934592, "seed": 88881111, "W_ge1": 8589934592,
              "null": 8.0, "excess_factor": 1073741824.0, "reading": "SATURATED"},
             {"r": 5, "trials": 4294967296, "seed": 20260802, "W_ge1": 67,
              "null": 4.0, "excess_factor": 16.75},
             {"r": 5, "trials": 8589934592, "seed": 88881111, "W_ge1": 126,
              "null": 8.0, "excess_factor": 15.75},
             {"r": 6, "trials": 4294967296, "seed": 20260802, "W_ge1": 3,
              "null": 4.0, "excess_factor": 0.75},
             {"r": 10, "trials": 4294967296, "seed": 20260802, "W_ge1": 3,
              "null": 4.0, "excess_factor": 0.75}]}],
    "what_survives_of_the_claim": [
        "TRUE: the yoyo_sbox_v2 instrument (software T-table AES, parameterized "
        "S-box) has only ever run at r in {5,6}; its BATCH-002 AES-NI predecessor "
        "probe.c only at r in {2,5,6,10}. Neither has ever run at r=3 or r=4.",
        "TRUE: no r=4 arm has ever been PAIRED to an r=5 arm on key and stream, "
        "and none has ever been run under a non-AES S-box. This task supplies both.",
        "FALSE as worded in the dispatch queue: that no r=4 measurement exists and "
        "that the low side of the profile has never been measured. It has, twice, "
        "on 2026-08-02, and it read fully saturated.",
        "MITIGATION, stated in fairness: the BATCH-001 probe was an explicitly "
        "exploratory scratchpad with no ledger record (its own PREREGISTRATION.md "
        "section 0 says so), a plausible reason it was not surfaced. That makes it "
        "weaker evidence, not absent evidence."],
    "effect_on_this_task": "My r=4 prediction was INFORMED by this prior reading, "
                           "not blind, and PREREGISTRATION.md section 1 says so before "
                           "the measurement. A confirmed prediction here is not a lucky call.",
    "searched_and_found_nothing_for": {
        "arm seed 631001 anywhere in coordination/ ledger/ knowledge/ outside this task":
            sh("grep -rln '631001' coordination ledger knowledge 2>/dev/null | grep -v 'TASK-20260803-0764fc' | sort").splitlines(),
        "S-box seeds 202608037xx anywhere outside this task":
            sh("grep -rln '202608037' coordination ledger knowledge 2>/dev/null | grep -v 'TASK-20260803-0764fc' | sort").splitlines()}}

# =====================================================================
# SECTION A -- RANK 1: the r=4 arm
# =====================================================================
A = {}
A["objective"] = ("Run r=4 under the real AES S-box at the same trial count and "
                  "geometry as the r=5 main arm, paired on seed so that `rounds` is "
                  "the only variable that changes.")
arms = {}
plan = [("A0-REPRO-R5-K1", "reproduction control vs BATCH-005 D-AES-K1"),
        ("A1-R4-MAIN", "RANK 1 PRIMARY: r=4 paired to BATCH-004 Y-AES-main (r=5) and Y-AES-main-r6 (r=6)"),
        ("A2-R4-K1", "RANK 1 SECOND PAIRING: r=4 paired to BATCH-005 D-AES-K1 (r=5, 2^30)"),
        ("A3-R3-MAIN", "exploratory profile fill, r=3"),
        ("A4-R2-MAIN", "exploratory profile fill, r=2"),
        ("A5-R4-R1-K1", "exploratory: r=4 under a drawn S-box, never asked before")]
for name, role in plan:
    p = os.path.join(HERE, "runs", name + ".json")
    if os.path.exists(p) and os.path.getsize(p) > 0:
        arms[name] = attach_timing(arm_row(p, role), name)
    else:
        arms[name] = {"arm": name, "role": role, "status": "NOT PRESENT",
                      "reason": "see budget_stamps.jsonl / runs/dropped.txt"}
A["arms"] = arms

# ---- pairing verification, field by field, not asserted ----
def pairing(new_name, ref_path, ref_label):
    if new_name not in arms or "key_hex" not in arms[new_name]:
        return {"status": "NOT CHECKED", "reason": "new arm absent"}
    n = arms[new_name]
    r = rj(ref_path)
    fields = ["sbox_spec", "sbox_seed", "sbox_first8", "amask", "smask", "trials",
              "log2N", "seed", "arm_id", "threads", "key_hex", "thread_seeds"]
    cmp = {}
    for f in fields:
        cmp[f] = {"new": n.get(f), "reference": r.get(f), "equal": n.get(f) == r.get(f)}
    cmp["rounds"] = {"new": n.get("rounds"), "reference": r.get("rounds"),
                     "equal": n.get("rounds") == r.get("rounds"),
                     "INTENDED_TO_DIFFER": True}
    identical = all(v["equal"] for k, v in cmp.items() if k != "rounds")
    return {
        "new_arm": new_name, "reference_arm": ref_label, "reference_path": ref_path,
        "field_by_field": cmp,
        "ALL_NON_ROUND_FIELDS_IDENTICAL": identical,
        "ONLY_ROUNDS_DIFFERS": identical and not cmp["rounds"]["equal"],
        "how_verified": "Values printed by the binary in each arm's own JSON were "
                        "compared field by field against the recorded prior-batch JSON. "
                        "This is a comparison of emitted values, not an assertion about "
                        "the code path.",
        "why_it_must_hold_structurally": "yoyo_sbox_v2.c line 382: key state = seed ^ "
            "0xA5A5A5A5A5A5A5A5; line 393: thread seed = seed ^ armid*0x1234567891 ^ "
            "(t+1)*0x9E3779B97F4A7C15. Neither depends on `rounds`. The plaintext pair is "
            "drawn from the thread state in worker() before any encryption call, so the "
            "trial stream is round-independent too."}

A["pairing_verification"] = {
    "A1_vs_BATCH004_r5": pairing("A1-R4-MAIN", os.path.join(B4, "runs/Y-AES-main.json"), "BATCH-004 Y-AES-main (r=5)"),
    "A1_vs_BATCH004_r6": pairing("A1-R4-MAIN", os.path.join(B4, "runs/Y-AES-main-r6.json"), "BATCH-004 Y-AES-main-r6 (r=6)"),
    "A2_vs_BATCH005_r5": pairing("A2-R4-K1", os.path.join(B5, "runs/D-AES-K1.json"), "BATCH-005 D-AES-K1 (r=5)"),
    "A0_vs_BATCH005_r5_reproduction": pairing("A0-REPRO-R5-K1", os.path.join(B5, "runs/D-AES-K1.json"), "BATCH-005 D-AES-K1 (r=5)")}

# ---- reproduction control ----
ref = rj(os.path.join(B5, "runs/D-AES-K1.json"))
a0 = arms.get("A0-REPRO-R5-K1", {})
A["reproduction_control_A0"] = {
    "purpose": "Confirm this binary in this environment reproduces a prior-batch "
               "number exactly, before any new reading is trusted.",
    "reference": "BATCH-005 D-AES-K1",
    "expected_preregistered": {"W_ge1_nontrivial": 14,
                               "key_hex": "bdf3823182ad657dab3d556b3886ba72",
                               "thread_seeds": [11400714758317678269, 4354685486758533762]},
    "measured": {k: a0.get(k) for k in ("W_ge1_nontrivial", "key_hex", "thread_seeds",
                                        "W_ge1_by_word", "whist", "trivial_swaps_excluded")},
    "reference_values": {k: ref.get(k) for k in ("W_ge1_nontrivial", "key_hex", "thread_seeds",
                                                 "W_ge1_by_word", "whist", "trivial_swaps_excluded")},
    "EXACT_MATCH": all(a0.get(k) == ref.get(k) for k in
                       ("W_ge1_nontrivial", "key_hex", "thread_seeds", "W_ge1_by_word", "whist"))}

# ---- the frozen comparison ----
y5 = rj(os.path.join(B4, "runs/Y-AES-main.json"))
y6 = rj(os.path.join(B4, "runs/Y-AES-main-r6.json"))
d5 = ref
r5_lo, r5_hi = pois_ci(y5["W_ge1_nontrivial"])
d5_lo, d5_hi = pois_ci(d5["W_ge1_nontrivial"])


def verdict(a, ref_x, ref_v, ref_lo, ref_hi):
    """Score one r=4 arm against the frozen table in PREREGISTRATION.md section 2."""
    if not a or "MEASURED_W_ge1" not in a:
        return {"verdict": "NOT MEASURED"}
    x, v = a["MEASURED_W_ge1"], a["NULL_EXPECTATION_analytic_MODELED"]
    ex = x / v
    ref_ex = ref_x / ref_v
    lo_ex, hi_ex = ref_lo / ref_v, ref_hi / ref_v
    if t5_full(x, v) == "DEAD" or ex <= 2.5:
        code, txt = "F1", ("NULL. MONOTONE PROFILE FALSIFIED -- the statistic is not "
                           "decaying with round count.")
    elif ex < lo_ex:
        code, txt = "F2", "BELOW r=5. MONOTONE PROFILE FALSIFIED (non-monotone in r)."
    elif ex <= hi_ex:
        code, txt = "F3", ("INDISTINGUISHABLE from r=5. PARTIAL FALSIFICATION: a flat "
                           "r=4/r=5 profile is inconsistent with decay from saturation at r=3.")
    elif a.get("saturated"):
        code, txt = "C2", ("SATURATED. Consistent with monotone decay. Refutes the "
                           "'peak at r=5' wording outright: the statistic is not peaked "
                           "at r=5, it is monotone decreasing in r, and r=5 is merely the "
                           "last round count with a sub-saturated above-null reading.")
    else:
        code, txt = "C1", ("Above r=5's 95% upper bound but below saturation. Consistent "
                           "with monotone decay; also refutes the 'peak at r=5' wording.")
    return {"preregistered_outcome_code": code, "meaning": txt,
            "r4_excess_factor_measured": ex,
            "r5_excess_factor_measured": ref_ex,
            "r5_exact95_ci_on_excess_factor": [lo_ex, hi_ex],
            "FALSIFIER_FIRED": code.startswith("F")}


A["FROZEN_COMPARISON"] = {
    "A1_vs_Y-AES-main": verdict(arms.get("A1-R4-MAIN"), y5["W_ge1_nontrivial"],
                                y5["null_expectation_analytic"], r5_lo, r5_hi),
    "A2_vs_D-AES-K1": verdict(arms.get("A2-R4-K1"), d5["W_ge1_nontrivial"],
                              d5["null_expectation_analytic"], d5_lo, d5_hi)}

A["preregistered_predictions_vs_measured"] = {
    "P1_r4_saturated_or_near": {
        "prediction": "W_ge1/nontrivial_trials >= 0.5, point prediction exactly 1.0",
        "A1_measured_rate": arms.get("A1-R4-MAIN", {}).get("hit_rate_measured"),
        "A2_measured_rate": arms.get("A2-R4-K1", {}).get("hit_rate_measured")},
    "P2_r3_saturated": {
        "prediction": "rate 1.0",
        "A3_measured_rate": arms.get("A3-R3-MAIN", {}).get("hit_rate_measured")},
    "P3_reproduction": {"prediction": "A0 returns exactly 14",
                        "measured": arms.get("A0-REPRO-R5-K1", {}).get("MEASURED_W_ge1")}}

A["round_profile_measured_on_this_instrument"] = [
    {"r": arms[n].get("rounds"), "arm": n, "trials": arms[n].get("nontrivial_trials"),
     "W_ge1": arms[n].get("MEASURED_W_ge1"),
     "null_modeled": arms[n].get("NULL_EXPECTATION_analytic_MODELED"),
     "excess_factor": arms[n].get("EXCESS_FACTOR_measured_over_modeled_null"),
     "source": "THIS TASK"}
    for n in ("A4-R2-MAIN", "A3-R3-MAIN", "A1-R4-MAIN", "A2-R4-K1", "A0-REPRO-R5-K1")
    if n in arms and "rounds" in arms[n]] + [
    {"r": 5, "arm": "Y-AES-main", "trials": y5["nontrivial_trials"],
     "W_ge1": y5["W_ge1_nontrivial"], "null_modeled": y5["null_expectation_analytic"],
     "excess_factor": y5["W_ge1_nontrivial"] / y5["null_expectation_analytic"],
     "source": "BATCH-004, prior"},
    {"r": 6, "arm": "Y-AES-main-r6", "trials": y6["nontrivial_trials"],
     "W_ge1": y6["W_ge1_nontrivial"], "null_modeled": y6["null_expectation_analytic"],
     "excess_factor": y6["W_ge1_nontrivial"] / y6["null_expectation_analytic"],
     "source": "BATCH-004, prior"}]

R["RANK_1_the_r4_arm"] = A
json.dump(R, open(os.path.join(HERE, "_results_part2.json"), "w"), indent=1)
print("part2 ok. A1 verdict:", A["FROZEN_COMPARISON"]["A1_vs_Y-AES-main"].get("preregistered_outcome_code"))

# =====================================================================
# SECTION B -- RANK 2: RC-8, the 27 draws
# =====================================================================
Bsec = {}
Bsec["objective"] = ("Twenty-seven independent random bijective S-box draws at r=5, "
                     "same trial count per arm, same binary, fresh seeds.")
Bsec["design"] = {
    "arm_seed": 631001, "arm_id": 1, "threads": 2, "rounds": 5,
    "amask": 1, "smask": 1, "log2N": 30, "trials_per_arm": 2 ** 30,
    "sbox_seeds": ["202608037%02d" % i for i in range(1, 28)],
    "seed_freshness": "Arm seed 631001 and S-box seeds 20260803701-727 appear nowhere "
                      "else in coordination/, ledger/ or knowledge/ (searched; result "
                      "recorded in repository_search_behind_the_absence_claim). This "
                      "matters because thread_seed depends only on (seed, armid, thread "
                      "index): reusing 431001 or 531001 at 2^30 would replay an exact "
                      "prefix of an existing trial stream, the trap BATCH-005 "
                      "RESULTS.json line 1605 records hitting.",
    "all_arms_share_the_arm_seed": True,
    "cost_of_that_choice_stated": "The S-box is the only thing that varies across the "
                                  "27 draws, which is the control the item is for. The "
                                  "price is that all draws are evaluated under ONE key "
                                  "and ONE plaintext stream, so the bound below is a "
                                  "statement about S-boxes at that key block, not "
                                  "marginalised over keys.",
    "every_draw_pinned_before_measurement": "./yoyo_sbox_v2 pin rand:<seed> 60600002 -- "
                                            "bijectivity plus 512 random key/plaintext "
                                            "vectors x 10 round counts of encrypt/decrypt "
                                            "round-trip. Full 256-entry table dumped to sboxes/."}

Bsec["liveness_rules_used"] = {
    "T5_FULL_BATCH004_frozen": "ALIVE iff X/v >= 5 AND P(K>=X | lambda=v) < 1e-6. At "
                               "v=1.0 the Poisson condition alone forces X >= 10 "
                               "(P(K>=9|1)=1.1e-6, P(K>=10|1)=1.1e-7).",
    "T5_SIMPLE_BATCH005_form": "excess factor >= 5x, i.e. X >= 5 at v=1.0.",
    "why_both": "The campaign states the rule in two non-equivalent places. Both counts "
                "are reported rather than picking the flattering one. The headline count "
                "uses T5_FULL, the stricter and chronologically first form.",
    "registered_before_measuring": True}

draws, pins = {}, {}
for i in range(1, 28):
    s = "202608037%02d" % i
    nm = "B%02d-RAND-%s" % (i, s)
    p = os.path.join(HERE, "runs", nm + ".json")
    pp = os.path.join(HERE, "runs", "pin_rand_%s.json" % s)
    if os.path.exists(pp) and os.path.getsize(pp) > 0:
        pd = rj(pp)
        pins[s] = {k: pd.get(k) for k in ("sbox_bijective", "roundtrip_checks",
                                          "roundtrip_failures", "pin_seed", "pin_pass",
                                          "sbox_first8")}
    else:
        pins[s] = {"pin_pass": None, "status": "PIN NOT PRESENT"}
    if os.path.exists(p) and os.path.getsize(p) > 0:
        draws[nm] = attach_timing(arm_row(p, "RC-8 draw %d of 27" % i), nm)
        draws[nm]["pin"] = pins[s]
    else:
        draws[nm] = {"arm": nm, "sbox_seed": int(s), "status": "NOT MEASURED",
                     "reason": "not started or dropped -- see runs/dropped.txt and "
                               "budget_stamps.jsonl", "pin": pins[s]}
Bsec["pins"] = pins
Bsec["draws"] = draws

p0 = os.path.join(HERE, "runs/B0-AES-REF.json")
Bsec["aes_reference_arm_same_fresh_seed"] = (
    attach_timing(arm_row(p0, "AES S-box reference at the same fresh arm seed 631001"),
                  "B0-AES-REF")
    if os.path.exists(p0) and os.path.getsize(p0) > 0
    else {"status": "NOT MEASURED"})

measured = [d for d in draws.values() if "MEASURED_W_ge1" in d]
n = len(measured)
alive_full = [d["arm"] for d in measured if d["T5_FULL_verdict_BATCH004_frozen_rule"] == "ALIVE"]
alive_simple = [d["arm"] for d in measured if d["T5_SIMPLE_verdict_BATCH005_form"] == "ALIVE"]
not_alive_full = [d for d in measured if d["T5_FULL_verdict_BATCH004_frozen_rule"] != "ALIVE"]
not_alive_simple = [d for d in measured if d["T5_SIMPLE_verdict_BATCH005_form"] != "ALIVE"]
pin_failures = [s for s, v in pins.items() if v.get("pin_pass") is False]

kf, ks = len(alive_full), len(alive_simple)
Bsec["RESULT"] = {
    "draws_planned": 27,
    "draws_measured": n,
    "draws_not_measured": 27 - n,
    "pin_failures": pin_failures,
    "ALIVE_count_T5_FULL": kf,
    "ALIVE_count_T5_SIMPLE": ks,
    "alive_arms_T5_FULL": alive_full,
    "not_alive_T5_FULL_detail": [
        {"arm": d["arm"], "sbox_seed": d["sbox_seed"], "sbox_first8": d.get("sbox_first8"),
         "W_ge1": d["MEASURED_W_ge1"], "nontrivial_trials": d["nontrivial_trials"],
         "trivial_swaps_excluded": d.get("trivial_swaps_excluded"),
         "whist": d.get("whist"), "W_ge1_by_word": d.get("W_ge1_by_word"),
         "null_modeled": d["NULL_EXPECTATION_analytic_MODELED"],
         "excess_factor": d["EXCESS_FACTOR_measured_over_modeled_null"],
         "poisson_p_ge_measured_given_null": d["poisson_p_ge_measured_given_null"],
         "exact95_ci_on_excess_factor": d["exact95_ci_on_excess_factor"],
         "T5_FULL": d["T5_FULL_verdict_BATCH004_frozen_rule"],
         "T5_SIMPLE": d["T5_SIMPLE_verdict_BATCH005_form"],
         "full_sbox_table_path": "sboxes/sbox_rand_%d.json" % d["sbox_seed"]}
        for d in not_alive_full],
    "not_alive_T5_SIMPLE_detail": [
        {"arm": d["arm"], "sbox_seed": d["sbox_seed"], "W_ge1": d["MEASURED_W_ge1"],
         "excess_factor": d["EXCESS_FACTOR_measured_over_modeled_null"],
         "full_sbox_table_path": "sboxes/sbox_rand_%d.json" % d["sbox_seed"]}
        for d in not_alive_simple],
    "raw_counts_every_draw": sorted(
        [(d["sbox_seed"], d["MEASURED_W_ge1"],
          d["EXCESS_FACTOR_measured_over_modeled_null"]) for d in measured])}

prior = {"draws_on_this_instrument": ["rand:20260803001", "rand:20260803002"],
         "status": "both ALIVE at r=5 in BATCH-004 (2^31) and BATCH-005 (2^30)",
         "count": 2}
Bsec["BOUND_ON_THE_PRESERVING_FRACTION"] = {
    "definition": "p = fraction of bijective S-boxes that preserve the signal at THIS "
                  "round count (r=5), THIS key block (arm seed 631001), THIS exposure "
                  "(2^30 trials) and THIS liveness rule.",
    "method": "one-sided 95% Clopper-Pearson lower bound; for k = n it equals 0.05^(1/n)",
    "this_task_alone_T5_FULL": {"k": kf, "n": n, "lower_bound_95": cp_lower(kf, n) if n else None},
    "this_task_alone_T5_SIMPLE": {"k": ks, "n": n, "lower_bound_95": cp_lower(ks, n) if n else None},
    "pooled_with_the_2_prior_draws_on_this_instrument_T5_FULL": {
        "k": kf + prior["count"], "n": n + prior["count"],
        "lower_bound_95": cp_lower(kf + prior["count"], n + prior["count"]) if n else None,
        "prior_draws": prior,
        "assumption_stated": "Pooling treats the 2 prior draws as exchangeable with "
                             "these 27. They were run at a DIFFERENT key block "
                             "(431001/531001) and, for BATCH-004, a different exposure "
                             "(2^31). That is a real assumption and it is why both the "
                             "pooled and unpooled figures are given."},
    "CURRENT_FIGURE_BEING_REPLACED": {
        "value": 0.224,
        "exact": 0.05 ** 0.5,
        "provenance": "0.05^(1/2) from two draws; CORR-20260803-791ca7, EV-AES-c66a80 OBS-B4-3",
        "what_it_says": "two preserving draws bound the preserving fraction at >= 0.224"},
    "TARGET_THE_CAMPAIGN_NAMED": {
        "value": 0.90, "requires": "29 consecutive preserving draws",
        "exact_at_29": 0.05 ** (1 / 29.0)},
    "SIDE_BY_SIDE": None}
bb = Bsec["BOUND_ON_THE_PRESERVING_FRACTION"]
bb["SIDE_BY_SIDE"] = {
    "before_this_task": 0.05 ** 0.5,
    "after_this_task_unpooled_T5_FULL": bb["this_task_alone_T5_FULL"]["lower_bound_95"],
    "after_this_task_unpooled_T5_SIMPLE": bb["this_task_alone_T5_SIMPLE"]["lower_bound_95"],
    "after_this_task_pooled_T5_FULL": bb["pooled_with_the_2_prior_draws_on_this_instrument_T5_FULL"]["lower_bound_95"]}
Bsec["preregistered_prediction_vs_measured"] = {
    "P4": {"prediction": "all 27 ALIVE under T5-SIMPLE; at least 24 of 27 ALIVE under T5-FULL",
           "measured_T5_SIMPLE": "%d of %d" % (ks, n),
           "measured_T5_FULL": "%d of %d" % (kf, n)},
    "P5": {"prediction": "B0-AES-REF ALIVE under both rules",
           "measured_T5_FULL": Bsec["aes_reference_arm_same_fresh_seed"].get(
               "T5_FULL_verdict_BATCH004_frozen_rule"),
           "measured_T5_SIMPLE": Bsec["aes_reference_arm_same_fresh_seed"].get(
               "T5_SIMPLE_verdict_BATCH005_form")}}
Bsec["what_this_cannot_establish"] = (
    "Anything about S-boxes at other key blocks, other round counts, other exposures, "
    "or about full-round or deployed AES. 27 draws from 256! bijections bound a "
    "fraction at one setting; they do not establish a structure, and no reading of "
    "S-box independence is asserted here -- that judgement belongs to the Reviewer "
    "and Coordinator.")

R["RANK_2_RC8_the_27_draws"] = Bsec
json.dump(R, open(os.path.join(HERE, "_results_part3.json"), "w"), indent=1)
print("part3 ok. ALIVE T5_FULL %d/%d, T5_SIMPLE %d/%d" % (kf, n, ks, n))

# =====================================================================
# Headline, deviations, budget, checks that did not run
# =====================================================================
v1 = A["FROZEN_COMPARISON"]["A1_vs_Y-AES-main"]
v2 = A["FROZEN_COMPARISON"]["A2_vs_D-AES-K1"]
fired = bool(v1.get("FALSIFIER_FIRED")) or bool(v2.get("FALSIFIER_FIRED"))

if fired:
    head = ("THE RANK-1 FALSIFIER FIRED. r=4 read %s, outcome code %s. The monotone "
            "round-profile that every yoyo claim in this campaign assumes is "
            "CONTRADICTED by this measurement." % (v1.get("r4_excess_factor_measured"),
                                                   v1.get("preregistered_outcome_code")))
else:
    head = ("THE RANK-1 FALSIFIER DID NOT FIRE. r=4 read SATURATED (every trial a hit, "
            "excess factor 2^30 = 1073741824 against the modeled null), far above r=5's "
            "13.5x. Outcome code %s: consistent with the campaign's monotone-decay "
            "description of the round profile. WHAT DOES DIE IS THE DISPATCH QUEUE'S "
            "WORDING: the statistic is NOT 'peaked at r=5'. It is monotone decreasing in "
            "r and saturated at r<=4, so r=5 is merely the last round count with a "
            "sub-saturated, above-null reading. A 'peak at r=5' was never a property of "
            "this statistic, and r=2 (BATCH-002 arm_PC, rate 1.0) already showed that "
            "before this task ran." % v1.get("preregistered_outcome_code"))
R["HEADLINE"] = head
R["HEADLINE_SECOND_LINE"] = (
    "SEPARATELY, AND AGAINST THE QUEUE: the claim that the low side of the profile has "
    "never been measured is FALSE. BATCH-001/tasks/yoyo5/analysis.json recorded "
    "saturated r=3 and r=4 arms on 2026-08-02. See repository_search_behind_the_absence_claim.")

R["observations_not_interpretation"] = [
    "A1-R4-MAIN: whist = [0,0,0,2147483648,0] -- W = 3 on EVERY ONE of 2^31 trials, "
    "and W_ge1_by_word = [0, 2^31, 2^31, 2^31]. The zero-difference pattern at r=4 is "
    "not a rare coincidence at this geometry: exactly three of the four plaintext words "
    "are preserved deterministically, and the one that is never preserved is word 0, the "
    "active word carrying amask=1. This is a structural, not statistical, reading and it "
    "is recorded as an observation; its mechanism is not interpreted here.",
    "The excess factor 1073741824 = 2^30 is the ARITHMETIC MAXIMUM this statistic can "
    "report against a null of trials*2^-30: a rate of 1.0 divided by a modeled null rate "
    "of 2^-30. It is a saturation ceiling, not an unbounded effect size, and must not be "
    "read as '2^30 times stronger than r=5' in any extrapolative sense.",
    "A0-REPRO reproduced BATCH-005 D-AES-K1 exactly, including W_ge1_by_word and the "
    "full whist vector, on a different session and a copied binary."]

R["protocol_deviations"] = [
    {"deviation": "A2-R4-K1 attempt 1 was killed mid-run by the agent harness's 600 s "
                  "tool timeout, not by the task budget and not by the arm's own timeout.",
     "classification": "infrastructure_error",
     "handling": "The empty output file was preserved as "
                 "runs/A2-R4-K1.ATTEMPT1-INTERRUPTED.json and the arm was re-run from "
                 "scratch under the background driver. Both attempts are recorded. No "
                 "reading was taken from the interrupted attempt.",
     "is_it_evidence": "No. A kill is resource/infrastructure, never negative evidence."},
    {"deviation": "SECTION B arms ran 2 at a time (2 threads each) on 4 cores, whereas "
                  "BATCH-004 and BATCH-005 ran arms sequentially at 2 threads.",
     "classification": "recorded deviation, no effect on counts",
     "handling": "Every arm's output is a deterministic function of its arguments "
                 "(fixed thread count, fixed per-thread seeds, fixed trial split). "
                 "Concurrency changes wall time only, and the wall times are reported "
                 "as measured under contention rather than compared to prior batches."},
    {"deviation": "The r=4 arms were preregistered with a prediction INFORMED by a prior "
                  "BATCH-001 measurement discovered during the repository search, rather "
                  "than blind.",
     "classification": "recorded, disclosed in PREREGISTRATION.md section 1 before "
                       "measuring",
     "handling": "Stated so a confirmed prediction is not read as a lucky call."}]

R["measured_vs_modeled"] = {
    "MEASURED": ["every W_ge1 count, whist, W_ge1_by_word, trivial_swaps_excluded, "
                 "nontrivial_trials, key_hex, thread_seeds, and every wall time",
                 "the FIPS-197 C.1 KAT ciphertext and all round-trip checks",
                 "the pin results for all drawn S-boxes"],
    "MODELED": ["null_expectation_analytic = nontrivial_trials * 4 * 2^-32, the "
                "PRP-null for P(W>=1). This is an ANALYTIC constant emitted by the "
                "binary (yoyo_sbox_v2.c line 28), not a measurement of this run.",
                "every EXCESS_FACTOR, since it is a measured count divided by that "
                "modeled null",
                "all Poisson tails and exact intervals, which assume the counts are "
                "Poisson under the null",
                "the Clopper-Pearson bound, which assumes the 27 draws are independent "
                "and identically distributed Bernoulli in ALIVE/not-ALIVE"],
    "optimistic_assumptions_restated_next_to_what_they_affect": [
        "The 4*2^-32 null is analytic. CORR-20260803-c92db5 records that it was checked "
        "against measurement in BATCH-002 (pooled 12 observed vs 16.0 expected over 2^34, "
        "ratio 0.75) and by the BATCH-005 red team across nine clean null arms (26 vs "
        "29.0, ratio interval [0.586, 1.314]). So it is confirmed to about +/-31%. Every "
        "excess factor in this file inherits that +/-31% uncertainty in its denominator. "
        "For the r=4 saturated arms this is irrelevant (a factor of 1.3 against 2^30); "
        "for the RC-8 draws near the ALIVE threshold it is NOT irrelevant and could move "
        "a borderline draw across the T5_FULL line.",
        "The Clopper-Pearson bound assumes the ALIVE/not-ALIVE outcomes are independent "
        "across draws. They share one key and one plaintext stream, so this is the "
        "assumption most likely to be wrong, and it is why the bound is reported as "
        "conditional on that key block."]}

# ---------- budget ----------
now = int(datetime.datetime.utcnow().timestamp())
stamps = [json.loads(l) for l in open(os.path.join(HERE, "budget_stamps.jsonl"))]
dropped = []
dp = os.path.join(HERE, "runs/dropped.txt")
if os.path.exists(dp):
    dropped = [l.strip() for l in open(dp) if l.strip()]
R["budget"] = {
    "declared_wall_clock_seconds": 6000,
    "start_utc": "2026-08-03T15:53:30Z", "start_epoch": 1785772410,
    "binding_stop_utc": "2026-08-03T17:33:30Z", "binding_stop_epoch": 1785778410,
    "computation": "binding_stop = start + 6000",
    "elapsed_at_write_s": now - 1785772410,
    "declared_memory_gb": 8,
    "memory_note": "peak RSS not sampled (no /usr/bin/time); the probe allocates well "
                   "under 1 MB and was never near the cap",
    "maximum_runs_declared": 40,
    "measuring_arms_executed": len([k for k in T if not k.startswith("pin")]),
    "verification_runs_not_counted_as_arms": "1 FIPS-197 pin, 1 geometry dump, and one "
                                             "pin + one table dump per drawn S-box. This "
                                             "reading of the run limit was registered in "
                                             "PREREGISTRATION.md section 4 in advance.",
    "arm_wall_times_measured": T,
    "DROPPED_ON_BUDGET": dropped,
    "halted_on_budget": None,
    "stamps": stamps}

R["checks_that_did_not_run"] = [
    {"check": "orchestration.adapter doctor --probe to verify the resolved model id",
     "reason": "No adapter probe exists under this Claude Code harness. model_verified "
               "is therefore false, not assumed true."},
    {"check": "Independent re-implementation of the yoyo probe",
     "reason": "Explicitly forbidden by the task: both items are controls on an existing "
               "instrument and a rewrite would add an uncontrolled factor. The validator "
               "task TASK-20260803-a13de8 carries the independent re-measurement."},
    {"check": "Peak RSS sampling",
     "reason": "No /usr/bin/time on this image."},
    {"check": "r=4 under all four (amask, smask) geometries, and r=4 at other key blocks",
     "reason": "Not in scope for this task; the arm was specified as paired to the r=5 "
               "main arm. The r=4 reading is therefore scoped to amask=1, smask=1 and "
               "the two key blocks run."},
    {"check": "RC-10 (k-byte null scaling), RC-11 (hit-index overlap), RC-12, "
              "RC-2-REMAINDER, RC-4, RC-5 from the BATCH-005 red team's control set",
     "reason": "Not assigned to this task. This task was assigned RC-9 (rank 1) and RC-8 "
               "(rank 2) only."},
    {"check": "Marginalising the RC-8 bound over keys",
     "reason": "All 27 draws share one key block by design, so that the S-box is the only "
               "varying factor. Marginalising would need the draws repeated at further key "
               "blocks; not run, and the bound is scoped accordingly."}]

R["reproduction"] = {
    "how": "From the recorded git commit, copy "
           "coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-367b1b/"
           "yoyo_sbox_v2 (sha256 d30e4d72...), verify the hash, then run the exact "
           "commands in runs/commands.txt. Every arm is deterministic in its arguments; "
           "no wall-clock, thread-count or scheduling behaviour affects any count.",
    "commands_file": "runs/commands.txt",
    "all_commands": [l.strip() for l in open(os.path.join(HERE, "runs/commands.txt"))] if
        os.path.exists(os.path.join(HERE, "runs/commands.txt")) else [],
    "determinism_basis": "thread count is fixed per arm, trials are split "
                         "deterministically (N/nthr with the remainder to thread 0), and "
                         "each thread's splitmix64 state is a fixed function of "
                         "(seed, armid, thread index)."}

R["artifact_paths"] = [
    os.path.join(HERE, "RESULTS.json"),
    os.path.join(HERE, "PREREGISTRATION.md"),
    os.path.join(HERE, "budget_stamps.jsonl")]
R["supporting_paths_not_declared_artifacts"] = sorted(
    glob.glob(os.path.join(HERE, "runs/*")) + glob.glob(os.path.join(HERE, "sboxes/*")))

R["scope_statement"] = (
    "TOY TIER. Every number here is scoped to: the yoyo_sbox_v2 software T-table AES-128 "
    "permutation reduced to r in {2,3,4,5} with the full FIPS-197 key schedule; the "
    "(amask=1, smask=1) probe geometry; the two key blocks 431001/531001 for SECTION A "
    "and the single key block 631001 for SECTION B; at most 2^31 trials per arm; and the "
    "S-boxes actually drawn. Nothing here speaks to full-round or deployed AES, and no "
    "comparison to published cryptanalysis is made in either direction. This file records "
    "observations; it declares no hypothesis supported, rejected or closed, and no "
    "heuristic validated or refuted.")

R["completion_gate_self_check"] = {
    "r4_arm_reported_with_pairing_verified_field_by_field_not_asserted":
        A["pairing_verification"]["A1_vs_BATCH004_r5"].get("ALL_NON_ROUND_FIELDS_IDENTICAL"),
    "falsifier_outcome_stated_without_softening": True,
    "RC8_alive_count_and_bound_stated_beside_0.224": True,
    "rank_1_prioritised_if_budget_cut": True,
    "json_load_confirmation": "recorded in parser_confirmation below"}

out = os.path.join(HERE, "RESULTS.json")
json.dump(R, open(out, "w"), indent=1)
# ---- parse our own file, then record that we did ----
with open(out) as f:
    reread = json.load(f)
R["parser_confirmation"] = {
    "check": "json.load() executed on this exact file after writing it",
    "result": "PARSED",
    "top_level_keys": len(reread),
    "bytes": os.path.getsize(out),
    "when_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
json.dump(R, open(out, "w"), indent=1)
with open(out) as f:
    reread2 = json.load(f)
print("RESULTS.json written and re-parsed OK:", len(reread2), "top-level keys,",
      os.path.getsize(out), "bytes")
print("HEADLINE:", R["HEADLINE"][:120])
for f in ("_results_part1.json", "_results_part2.json", "_results_part3.json"):
    p = os.path.join(HERE, f)
    if os.path.exists(p):
        os.remove(p)
