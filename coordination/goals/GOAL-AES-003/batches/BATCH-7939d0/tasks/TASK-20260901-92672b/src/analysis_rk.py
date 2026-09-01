#!/usr/bin/env python3
# analysis_rk.py -- TASK-20260901-92672b (BATCH-7939d0, GOAL-AES-003).
#
# Exact conditional-binomial (Poisson-ratio) machinery + Garwood Poisson CIs,
# written for this task, structurally mirroring BATCH-015's analysis.py (which
# is itself a structural mirror of EV-AES-e4c091's Rank-1 rule and BATCH-014's
# OUTCOME-A'/B'/C' rule). BEFORE computing any new statistic it reproduces the
# figures published in this comparison family as a self-check gate:
#   14 vs 1            -> p = 9.765625e-4, ratio CI [2.1300416502432444, 591.9684937326185]
#   14 vs 0 (BATCH-014)-> p = 0.0001220703125, ratio CI lower 3.3171226765018393
#   Garwood x=1,m=1    -> [0.025, 5.572];  Garwood x=6,m=8 -> [0.275, 1.632]
# No scipy dependency: exact binomial tails via fractions, chi-square
# quantiles via an implemented regularized incomplete gamma inverse.
#
# Pure arithmetic on already-written run JSONs plus file-level integrity
# checks (parity hashes, AES-arm field comparison, mtime gate). No status
# assignment, no evidence strength, no promotion recommendation.
import hashlib, json, math, os, sys
from fractions import Fraction

TASKDIR = "coordination/goals/GOAL-AES-003/batches/BATCH-7939d0/tasks/TASK-20260901-92672b"
L1_PATH = "coordination/goals/GOAL-AES-003/batches/BATCH-015/tasks/TASK-20260805-d408ac/runs/L1-AES-R5-P30.json"
M1_PATH = "coordination/goals/GOAL-AES-003/batches/BATCH-014/tasks/TASK-20260805-b95720/runs/M1-FEISTEL-P30.json"

def _gammap_series(a, x):
    if x == 0.0: return 0.0
    ap = a; s = 1.0 / a; d = s
    for _ in range(1000):
        ap += 1.0; d *= x / ap; s += d
        if abs(d) < abs(s) * 1e-15: break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))

def _gammaq_cf(a, x):
    b = x + 1.0 - a; c = 1e300; d = 1.0 / b; h = d
    for i in range(1, 1000):
        an = -i * (i - a); b += 2.0
        d = an * d + b; d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c; c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d; de = d * c; h *= de
        if abs(de - 1.0) < 1e-15: break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))

def gammainc_reg(a, x):
    if x <= 0: return 0.0
    return _gammap_series(a, x) if x < a + 1.0 else 1.0 - _gammaq_cf(a, x)

def qchisq(p, df):
    lo, hi = 0.0, df + 50.0 * math.sqrt(2.0 * df) + 200.0
    while gammainc_reg(df / 2.0, hi / 2.0) < p: hi *= 2
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if gammainc_reg(df / 2.0, mid / 2.0) < p: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)

def garwood_ci(x, m):
    lo = 0.0 if x == 0 else 0.5 * qchisq(0.025, 2 * x) / m
    hi = 0.5 * qchisq(0.975, 2 * x + 2) / m
    return [lo, hi]

def binom_tail_exact_ge(k, n, p_frac):
    q = Fraction(1) - p_frac
    s = Fraction(0)
    for i in range(k, n + 1):
        s += Fraction(math.comb(n, i)) * p_frac ** i * q ** (n - i)
    return s

def binom_cdf_float(k, n, p):
    s = 0.0
    for i in range(0, k + 1):
        s += math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                      + i * math.log(p) + (n - i) * math.log1p(-p)) if 0 < p < 1 else (1.0 if (i == n if p == 1 else i == 0) else 0.0)
    return s

def _solve(f):
    lo, hi = 0.0, 1.0
    flo, fhi = f(lo + 1e-16), f(hi - 1e-16)
    for _ in range(300):
        mid = 0.5 * (lo + hi); fm = f(mid)
        if (flo <= 0 and fm <= 0) or (flo > 0 and fm > 0): lo, flo = mid, fm
        else: hi, fhi = mid, fm
    return 0.5 * (lo + hi)

def clopper_pearson(x, n):
    if n == 0: return [0.0, 1.0]
    lo = 0.0 if x == 0 else _solve(lambda p: 1.0 - binom_cdf_float(x - 1, n, p) - 0.025)
    hi = 1.0 if x == n else _solve(lambda p: binom_cdf_float(x, n, p) - 0.025)
    return [lo, hi]

def comparison(x_aes, nontriv_aes, x_sub, nontriv_sub):
    m_aes = Fraction(nontriv_aes * 4, 2 ** 32)
    m_sub = Fraction(nontriv_sub * 4, 2 ** 32)
    n = x_aes + x_sub
    p0 = m_aes / (m_aes + m_sub)
    if n == 0:
        p_val = 1.0
    else:
        tail_ge = binom_tail_exact_ge(x_aes, n, p0)
        tail_le = binom_tail_exact_ge(n - x_aes, n, Fraction(1) - p0)
        p_val = float(min(Fraction(1), 2 * min(tail_ge, tail_le)))
    cp = clopper_pearson(x_aes, n) if n > 0 else [0.0, 1.0]
    scale = float(m_sub / m_aes)
    ratio_point = (float('inf') if x_sub == 0 else (x_aes / float(m_aes)) / (x_sub / float(m_sub)))
    ratio_lo = (cp[0] / (1 - cp[0])) * scale if cp[0] < 1 else float('inf')
    ratio_hi = (cp[1] / (1 - cp[1])) * scale if cp[1] < 1 else float('inf')
    R = x_sub / float(m_sub)
    Rci = garwood_ci(x_sub, float(m_sub))
    return {
        "x_aes": x_aes, "x_sub": x_sub,
        "m_aes": float(m_aes), "m_sub": float(m_sub),
        "nontriv_aes": nontriv_aes, "nontriv_sub": nontriv_sub,
        "n": n, "p0_exact": str(p0), "p0_float": float(p0),
        "p_value": p_val,
        "cp_p_ci": cp,
        "ratio_point": ratio_point,
        "ratio_ci": [ratio_lo, ratio_hi],
        "R_sub_point": R,
        "R_sub_garwood_95ci": Rci,
        "R_ci_contains_1": Rci[0] <= 1.0 <= Rci[1],
        "R_ci_lower_gt_1": Rci[0] > 1.0,
    }

def outcome(cmp):
    if cmp["R_ci_contains_1"] and cmp["p_value"] < 0.01: return "OUTCOME-A'"
    if cmp["R_ci_lower_gt_1"] and cmp["p_value"] >= 0.01: return "OUTCOME-B'"
    return "OUTCOME-C'"

def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def main():
    runs = os.path.join(TASKDIR, "runs")
    out = {"task_id": "TASK-20260901-92672b", "self_checks": {}, "gates": {},
           "comparisons": {}, "task_level": {}, "integrity": {}}

    sc = out["self_checks"]
    c1 = comparison(14, 2 ** 30, 1, 2 ** 30)
    sc["ev_e4c091_and_batch015_14_vs_1"] = {
        "p_value": c1["p_value"], "expected_p": 0.0009765625,
        "ratio_ci": c1["ratio_ci"],
        "published_ratio_ci": [2.1300416502432444, 591.9684937326185],
        "match_p": abs(c1["p_value"] - 0.0009765625) < 1e-12,
        "match_ratio_ci": abs(c1["ratio_ci"][0] - 2.1300416502432444) < 1e-6
                          and abs(c1["ratio_ci"][1] - 591.9684937326185) < 1e-6,
    }
    c2 = comparison(14, 1073741824, 0, 1073741823)
    sc["batch014_M1_14_vs_0"] = {
        "p_value": c2["p_value"], "expected_p": 0.0001220703125,
        "p0_float": c2["p0_float"],
        "ratio_ci": c2["ratio_ci"],
        "published_ratio_ci_lower": 3.3171226765018393,
        "match_p": abs(c2["p_value"] - 0.0001220703125) < 1e-9,
        "match_ratio_ci_lower": abs(c2["ratio_ci"][0] - 3.3171226765018393) < 1e-6,
    }
    g1 = garwood_ci(1, 1.0); g6 = garwood_ci(6, 8.0)
    sc["garwood_ev_e4c091_N1"] = {"ci": g1, "published": [0.025, 5.572],
        "match": round(g1[0], 3) == 0.025 and round(g1[1], 3) == 5.572}
    sc["garwood_ev_e4c091_N2_R"] = {"ci": g6, "published": [0.275, 1.632],
        "match": round(g6[0], 3) == 0.275 and round(g6[1], 3) == 1.632}
    sc["all_pass"] = all([
        sc["ev_e4c091_and_batch015_14_vs_1"]["match_p"],
        sc["ev_e4c091_and_batch015_14_vs_1"]["match_ratio_ci"],
        sc["batch014_M1_14_vs_0"]["match_p"],
        sc["batch014_M1_14_vs_0"]["match_ratio_ci_lower"],
        sc["garwood_ev_e4c091_N1"]["match"],
        sc["garwood_ev_e4c091_N2_R"]["match"]])
    if not sc["all_pass"]:
        with open(os.path.join(runs, "decision_analysis.json"), "w") as f:
            json.dump(out, f, indent=2)
        print("SELF-CHECK FAILED -- analysis machinery does not reproduce published figures; stopping before touching run JSONs")
        sys.exit(1)

    # ---- determinism gates ----
    det = {}
    for r in (4, 8, 16, 32):
        d = json.load(open(os.path.join(runs, f"DET-R{r}.json")))
        det[f"DET-R{r}"] = {"deterministic": d["deterministic"],
                            "same_key_same_input_same_output": d["same_key_same_input_same_output"],
                            "decrypt_inverts_encrypt": d["decrypt_inverts_encrypt"],
                            "round_key_schedule_reproducible": d["round_key_schedule_reproducible"],
                            "fixed_points_in_4096_trials": d["fixed_points_in_4096_trials"]}
    out["gates"]["determinism"] = det
    out["gates"]["determinism_all_pass"] = all(v["deterministic"] for v in det.values())

    # ---- r=16 byte-parity gate ----
    pairs = [("DET-R16.json", "DET-R16-VERBATIM.json"),
             ("SMOKE22-R16.json", "SMOKE22-R16-VERBATIM.json")]
    parity = {}
    for a, b in pairs:
        ha, hb = sha256(os.path.join(runs, a)), sha256(os.path.join(runs, b))
        parity[a + "_vs_" + b] = {"sha256_variant": ha, "sha256_verbatim": hb, "identical": ha == hb}
    out["gates"]["r16_byte_parity"] = parity
    out["gates"]["r16_byte_parity_pass"] = all(v["identical"] for v in parity.values())

    # ---- AES arm verification vs archived L1 and frozen comparator ----
    aes = json.load(open(os.path.join(runs, "AES-P30.json")))
    l1 = json.load(open(L1_PATH))
    allowed_diff = {"arm", "elapsed_seconds_measured", "measured_rate_trials_per_sec"}
    diffs = {}
    for k in set(aes) | set(l1):
        va, vl = aes.get(k, "<missing>"), l1.get(k, "<missing>")
        if k in allowed_diff:
            continue
        if va != vl:
            diffs[k] = {"AES-P30": va, "L1-AES-R5-P30": vl}
    frozen_fields = {
        "W_ge1_nontrivial": 14,
        "whist": [1073741810, 14, 0, 0, 0],
        "W_ge1_by_word": [4, 4, 2, 4],
        "thread_seeds": [11400714758317678269, 4354685486758533762],
        "plaintext_stream_digest": ["de8dee29c9310a13", "01089d650f48ca1b"],
        "seed": 531001, "arm_id": 1, "amask": 1, "smask": 1, "log2N": 30,
        "key_stream_seeds": [4284374398386231716, 9614918541733233340],
    }
    frozen_diffs = {k: {"AES-P30": aes.get(k, "<missing>"), "frozen_P1-R5-PAIR_via_BATCH-015": v}
                    for k, v in frozen_fields.items() if aes.get(k, "<missing>") != v}
    aes_hit_match = aes.get("hit_trials") == l1.get("hit_trials")
    out["gates"]["aes_arm_reproduction"] = {
        "compared_to": ["BATCH-015 L1-AES-R5-P30.json (field-by-field)",
                        "frozen P1-R5-PAIR values as recorded in BATCH-015's verified frozen_comparator block"],
        "allowed_field_differences": sorted(allowed_diff),
        "field_differences_vs_L1_beyond_allowed": diffs,
        "field_differences_vs_frozen": frozen_diffs,
        "hit_trials_identical_to_L1": aes_hit_match,
        "pass": len(diffs) == 0 and len(frozen_diffs) == 0 and aes_hit_match,
    }

    # ---- secondary parity: F-R16-P30 vs RC-D's archived M1-FEISTEL-P30 ----
    m1 = json.load(open(M1_PATH))
    f16 = json.load(open(os.path.join(runs, "F-R16-P30.json")))
    m1_norm = {k: v for k, v in m1.items() if k != "arm"}
    f16_norm = {k: v for k, v in f16.items() if k != "arm"}
    f16_diffs = {k: {"F-R16-P30": f16_norm.get(k, "<missing>"), "M1-FEISTEL-P30": m1_norm.get(k, "<missing>")}
                 for k in set(m1_norm) | set(f16_norm) if m1_norm.get(k, "<missing>") != f16_norm.get(k, "<missing>")}
    out["gates"]["f_r16_vs_rcd_M1_field_parity"] = {
        "note": "preregistered secondary parity: identical parameters except arm label, so all fields except 'arm' are expected identical",
        "field_differences_beyond_arm": f16_diffs,
        "pass": len(f16_diffs) == 0,
    }

    # ---- per-arm comparisons vs frozen comparator and vs live AES arm ----
    frozen = {"x": 14, "nontriv": 1073741824}
    arms = {}
    for r in (4, 8, 16, 32):
        j = json.load(open(os.path.join(runs, f"F-R{r}-P30.json")))
        cf = comparison(frozen["x"], frozen["nontriv"], j["W_ge1_nontrivial"], j["nontrivial_trials"])
        cf["outcome"] = outcome(cf)
        cl = comparison(aes["W_ge1_nontrivial"], aes["nontrivial_trials"], j["W_ge1_nontrivial"], j["nontrivial_trials"])
        cl["outcome"] = outcome(cl)
        arms[f"F-R{r}-P30"] = {
            "feistel_rounds_actual": j["feistel_rounds_actual"],
            "trials": j["trials"], "nontrivial_trials": j["nontrivial_trials"],
            "W_ge1_nontrivial": j["W_ge1_nontrivial"],
            "whist": j["whist"], "W_ge1_by_word": j["W_ge1_by_word"],
            "null_expectation_analytic": j["null_expectation_analytic"],
            "seed": j["seed"], "arm_id": j["arm_id"], "threads": j["threads"],
            "amask": j["amask"], "smask": j["smask"],
            "key_hex": j["key_hex"],
            "plaintext_stream_digest_per_thread": j["plaintext_stream_digest_per_thread"],
            "hit_trials": j["hit_trials"],
            "vs_frozen_r5": cf,
            "vs_live_AES-P30": cl,
        }
    out["comparisons"] = arms

    # ---- task-level taxonomy (PREREGISTRATION.md section 6) ----
    xs = [arms[f"F-R{r}-P30"]["W_ge1_nontrivial"] for r in (4, 8, 16, 32)]
    outcomes = [arms[f"F-R{r}-P30"]["vs_frozen_r5"]["outcome"] for r in (4, 8, 16, 32)]
    Rs = [arms[f"F-R{r}-P30"]["vs_frozen_r5"]["R_sub_point"] for r in (4, 8, 16, 32)]
    all_A = all(o == "OUTCOME-A'" for o in outcomes)
    nondec = all(xs[i] <= xs[i + 1] for i in range(3))
    noninc = all(xs[i] >= xs[i + 1] for i in range(3))
    strict = any(xs[i] != xs[i + 1] for i in range(3))
    complete = all(os.path.exists(os.path.join(runs, f"F-R{r}-P30.json")) for r in (4, 8, 16, 32))
    if not complete or not out["gates"]["r16_byte_parity_pass"] or not out["gates"]["determinism_all_pass"] or not out["gates"]["aes_arm_reproduction"]["pass"]:
        verdict, direction = "(d) INFRA/BUDGET-FAILURE", None
    elif all_A:
        verdict, direction = "(a) ABSENCE-PERSISTS", None
    elif nondec and strict:
        verdict, direction = "(b) MONOTONIC-DECAY", "toward_high_r"
    elif noninc and strict:
        verdict, direction = "(b) MONOTONIC-DECAY", "toward_low_r"
    elif not strict:
        verdict, direction = "(b) FLAT-FAILURE (extension disclosed: absence fails at all four r with no movement; not literally covered by the preregistered (a)-(c) wording)", None
    else:
        verdict, direction = "(c) NON-MONOTONIC", None
    trend_note = ("no movement: x(r) constant" if not strict else
                  "movement present: direction and magnitude in x_sequence and per-arm R_sub_point")
    out["task_level"] = {
        "rule_source": "PREREGISTRATION.md section 6 (written before any run output)",
        "x_sequence_r4_r8_r16_r32": xs,
        "R_sequence_r4_r8_r16_r32": Rs,
        "per_arm_outcomes_vs_frozen": outcomes,
        "all_arms_OUTCOME_A": all_A,
        "verdict": verdict,
        "direction": direction,
        "trend_note": trend_note,
        "null_control_statement": "round count is the parameter meant to move structure; if the statistic does not move with r that is the measured result (absence is round-count-robust); if it moves, direction and magnitude are reported above -- neither is silenced",
    }

    # ---- mtime gate: PREREGISTRATION.md predates every runs/ output ----
    pre_mtime = os.path.getmtime(os.path.join(TASKDIR, "PREREGISTRATION.md"))
    viol = []
    run_files = {}
    for fn in sorted(os.listdir(runs)):
        p = os.path.join(runs, fn)
        if os.path.isfile(p):
            run_files[fn] = os.path.getmtime(p)
            if run_files[fn] < pre_mtime:
                pass
            elif run_files[fn] == pre_mtime:
                viol.append(fn)
            # a run file newer than the preregistration is the EXPECTED direction
    newer_than_pre = [fn for fn, mt in run_files.items() if mt > pre_mtime]
    out["integrity"]["preregistration_mtime_gate"] = {
        "PREREGISTRATION_md_mtime_epoch": pre_mtime,
        "n_runs_files": len(run_files),
        "n_run_files_newer_than_preregistration": len(newer_than_pre),
        "pass": len(newer_than_pre) == len(run_files) and len(run_files) > 0,
        "note": "every file in runs/ must be NEWER than PREREGISTRATION.md (preregistration predates all run outputs)",
    }

    with open(os.path.join(runs, "decision_analysis.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out["self_checks"], indent=1))
    print("GATES:", json.dumps({k: v for k, v in out["gates"].items() if k.endswith("pass") or k.endswith("reproduction")}, indent=1))
    print("TASK LEVEL:", json.dumps(out["task_level"], indent=1))

if __name__ == "__main__":
    main()
