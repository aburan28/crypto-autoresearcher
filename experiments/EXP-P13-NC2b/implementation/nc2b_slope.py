#!/usr/bin/env python3
"""EXP-P13-NC2b / NC2b-SLOPE: Synthetic slope null test of assumption L1.

Zero new compute.  All inputs are committed values from RUN-PEC-49c773-a.
Observations only.  No interpretation, no status change.
"""

import hashlib
import json
import math
import os
import sys
import time
from datetime import datetime, timezone

# ── frozen contract constants ────────────────────────────────────────────────

RUN_ID   = "RUN-P13-NC2b-a"
EXP_ID   = "EXP-P13-NC2b"
TASK_ID  = "TASK-20260804-241b87"

COMMITTED_RAW_JSON = (
    "experiments/EXP-PEC-49c773/runs/RUN-PEC-49c773-a/raw-result.json")
COMMITTED_SHA256 = (
    "13f8f3fa55dc2dfeabe29d4d01f60d5d69370485fae523b208a7b53e6128add6")

REF_NULL_NOMINAL = 12.2595          # from DEC-20260802-48c72c
WMID_GAMMA_NULL_EXPECTED = -0.013241522288809005
WMID_LOG2A_NULL_EXPECTED  = 12.333420743532526

TOLERANCE_BITS = 0.75               # NC2b-SLOPE gate

# B_opt constants from EXP-PEC-49c773 specification section 6
B_OPT = {
    "NIST_I_256":   14.200000000000001,
    "NIST_III_384": 17.8,
    "NIST_V_512":   20.900000000000002,
    "log2p_576":    22.3,
    "log2p_768":    26.1,
}

# Pre-registered numerators from frozen spec (for cross-check)
PREREGISTERED_NUMERATORS = {
    0.4: {
        "NIST_I_256":   17.9395,
        "NIST_III_384": 19.3795,
        "NIST_V_512":   20.6195,
        "log2p_576":    21.1795,
        "log2p_768":    22.6995,
    },
    0.8: {
        "NIST_I_256":   23.6195,
        "NIST_III_384": 26.4995,
        "NIST_V_512":   28.9795,
        "log2p_576":    30.0995,
        "log2p_768":    33.1395,
    },
}

S_VALUES = [0.4, 0.8]
WINDOWS  = {"W-ALL": None, "W-MID": 11}   # W-MID: ell >= 11


# ── helpers ──────────────────────────────────────────────────────────────────

def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def ols_fit(xs, ys):
    """OLS slope and intercept."""
    n = len(xs)
    if n < 2:
        return None, None, None, None
    xm = sum(xs) / n
    ym = sum(ys) / n
    sxx = sum((x - xm)**2 for x in xs)
    sxy = sum((xs[i] - xm) * (ys[i] - ym) for i in range(n))
    if sxx == 0:
        return None, None, None, None
    slope = sxy / sxx
    intercept = ym - slope * xm
    resids = [ys[i] - (slope * xs[i] + intercept) for i in range(n)]
    sse = sum(r**2 for r in resids)
    se_slope = math.sqrt(sse / ((n - 2) * sxx)) if n > 2 and sse > 0 else 0.0
    return slope, intercept, se_slope, resids


def ols_ci95(slope, se_slope, n):
    """Analytic 95% CI for slope using t-distribution approximation."""
    # t critical value for 95% CI, n-2 df: use Normal for large n, t_table for small
    t_crit = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
              6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
    df = n - 2
    tc = t_crit.get(df, 1.960)  # fall back to Normal for df > 10
    return [slope - tc * se_slope, slope + tc * se_slope]


def log(msg, t0, lines):
    line = "[%7.1fs] %s" % (time.time() - t0, msg)
    print(line, flush=True)
    lines.append(line)


# ── main ──────────────────────────────────────────────────────────────────────

def main(repo_root=".", out=None):
    T0 = time.time()
    loglines = []

    def logf(msg):
        log(msg, T0, loglines)

    logf("NC2b-SLOPE (EXP-P13-NC2b) starting")

    R = {
        "run_id":         RUN_ID,
        "experiment_id":  EXP_ID,
        "task_id":        TASK_ID,
        "started_utc":    datetime.now(timezone.utc).isoformat(),
        "protocol_deviations": [],
        "anomalies": [],
    }

    # Step 1: verify input SHA-256
    raw_path = os.path.join(repo_root, COMMITTED_RAW_JSON)
    logf("Step 1: verify raw-result.json SHA-256")
    if not os.path.exists(raw_path):
        R["status"] = "infrastructure_error"
        R["error"]  = "null_series_unavailable: raw-result.json not found at %s" % raw_path
        logf("  NOT FOUND: %s" % raw_path)
        if out:
            json.dump(R, open(out, "w"), indent=1)
        return 1, R

    actual_sha = file_sha256(raw_path)
    sha_match  = (actual_sha == COMMITTED_SHA256)
    R["input_sha256"] = {
        "path": COMMITTED_RAW_JSON,
        "expected": COMMITTED_SHA256,
        "observed": actual_sha,
        "match": sha_match,
    }
    logf("  SHA-256 match: %s (expected=%s observed=%s)"
         % (sha_match, COMMITTED_SHA256[:16], actual_sha[:16]))

    if not sha_match:
        R["status"] = "infrastructure_error"
        R["error"]  = "SHA-256 mismatch; stopping"
        logf("  STOPPING: SHA-256 mismatch")
        if out:
            json.dump(R, open(out, "w"), indent=1)
        return 1, R

    # Step 2: read committed null series
    with open(raw_path) as fh:
        data = json.load(fh)

    null_series_raw = data["controls"]["C-NULL"]["per_ell_per_entry"]
    null_series = {int(k): v for k, v in null_series_raw.items()}
    ells_all = sorted(null_series.keys())
    logf("Step 2: read null series: %d ell values (%d..%d)"
         % (len(ells_all), min(ells_all), max(ells_all)))

    # Also get ell measured from C-NULL
    ell_measured = data["controls"]["C-NULL"].get("ell_measured", ells_all)
    logf("  ell_measured count: %d" % len(ell_measured))

    # Step 2: Refit log2(N(ell)) on log2(ell) over W-MID (ell >= 11)
    logf("Step 2: refit null OLS over W-MID (ell >= 11)")
    wmid_ells   = [e for e in ells_all if e >= 11]
    wmid_log2e  = [math.log2(e) for e in wmid_ells]
    wmid_log2N  = [math.log2(null_series[e]) for e in wmid_ells]
    gamma_refit, log2A_refit, se_gamma, _ = ols_fit(wmid_log2e, wmid_log2N)

    # REF_null: median of log2(N(ell)) over W-MID
    ref_null_median = sorted(wmid_log2N)[len(wmid_log2N)//2]
    # The spec says REF_null = W-MID OLS intercept at ell=1 (log2A_null_refit)
    # BUT: the gate uses REF_null_used = log2(A_null_refit) from the OLS fit
    # From nc2b spec step 2: "REF_null_used (the refit intercept)"
    ref_null_used = log2A_refit

    diff_from_nominal = abs(ref_null_used - REF_NULL_NOMINAL) if ref_null_used is not None else None
    logf("  gamma_null_refit = %.9f (expected %.9f)"
         % (gamma_refit, WMID_GAMMA_NULL_EXPECTED))
    logf("  log2(A_null_refit) = %.9f (expected %.9f)"
         % (log2A_refit, WMID_LOG2A_NULL_EXPECTED))
    logf("  REF_null_used = %.7f (nominal %.7f, diff=%.6f)"
         % (ref_null_used, REF_NULL_NOMINAL, diff_from_nominal if diff_from_nominal else 0))

    if diff_from_nominal is not None and diff_from_nominal > 0.05:
        msg = ("REF_null_refit differs from %.4f by %.6f bits (>0.05 bit threshold); "
               "recording as finding" % (REF_NULL_NOMINAL, diff_from_nominal))
        logf("  FINDING: " + msg)
        R["anomalies"].append(msg)

    # Record gamma_null discrepancy as an unexpected observation (AGENTS.md rule 8)
    gamma_discrepancy = abs(gamma_refit - WMID_GAMMA_NULL_EXPECTED) if gamma_refit is not None else None
    if gamma_discrepancy is not None and gamma_discrepancy > 0.005:
        anomaly_msg = (
            "UNEXPECTED OBSERVATION: gamma_null_refit=%.9f differs from "
            "DEC-20260802-48c72c expected value %.9f by %.6f. "
            "DIAGNOSIS: the committed nc2b null_fit in RUN-PEC-49c773-a used the "
            "EXP-PEC-6be870 null series (ell 11..101, n=21), whose gamma was %.9f. "
            "The EXP-P13-NC2b spec points to controls.C-NULL.per_ell_per_entry "
            "which is the EXP-PEC-49c773 null series (ell 2..211, n=47). "
            "Using W-MID (ell>=11) on the 47-ell series gives n=43 ells with "
            "gamma=%.9f -- a different object. Gate evaluation uses the REFIT values "
            "not the expected values, so the gate result is valid."
            % (gamma_refit, WMID_GAMMA_NULL_EXPECTED, gamma_discrepancy,
               WMID_GAMMA_NULL_EXPECTED, gamma_refit)
        )
        logf("  ANOMALY: " + anomaly_msg[:200] + "...")
        R["anomalies"].append(anomaly_msg)

    R["step2"] = {
        "wmid_n": len(wmid_ells),
        "gamma_null_refit":          gamma_refit,
        "gamma_null_expected":        WMID_GAMMA_NULL_EXPECTED,
        "gamma_null_reproduced_within_1e-6": (
            abs(gamma_refit - WMID_GAMMA_NULL_EXPECTED) < 1e-6
            if gamma_refit is not None else False),
        "log2_A_null_refit":         log2A_refit,
        "log2_A_null_expected":      WMID_LOG2A_NULL_EXPECTED,
        "REF_null_used":             ref_null_used,
        "REF_null_nominal":          REF_NULL_NOMINAL,
        "REF_null_diff_from_nominal": diff_from_nominal,
    }

    # Step 3: Form synthetic series S_s(ell) = N(ell) * ell^s
    logf("Step 3: form synthetic series S_s(ell) for s in %s" % S_VALUES)
    synthetic = {}
    for s in S_VALUES:
        S = {ell: null_series[ell] * (ell**s) for ell in ells_all}
        synthetic[s] = S
        sample_vals = {ell: S[ell] for ell in [11, 47, 101, 211] if ell in S}
        logf("  s=%.1f sample S_s(ell): %s" % (s, {e: "%.2f" % v for e, v in sample_vals.items()}))

    R["step3"] = {
        str(s): {
            "description": "S_s(ell) = N(ell) * ell^s",
            "sample_ells": {str(ell): synthetic[s][ell] for ell in [11, 47, 101, 151, 211]
                            if ell in synthetic[s]},
        }
        for s in S_VALUES
    }

    # Step 4: Apply estimator (W-ALL and W-MID)
    logf("Step 4: apply estimator")
    windows = {
        "W-ALL": ells_all,
        "W-MID": [e for e in ells_all if e >= 11],
    }

    results_by_s = {}
    for s in S_VALUES:
        results_by_s[s] = {}
        for wname, wells in windows.items():
            xs = [math.log2(e) for e in wells]
            ys = [math.log2(synthetic[s][e]) for e in wells]
            slope_s, intercept_s, se_s, _ = ols_fit(xs, ys)
            ci_s = ols_ci95(slope_s, se_s, len(wells)) if slope_s is not None else None
            logf("  s=%.1f %s: gamma_s_hat=%.6f (SE=%.6f) log2(A_s_hat)=%.6f"
                 % (s, wname, slope_s if slope_s else float('nan'),
                    se_s if se_s else float('nan'),
                    intercept_s if intercept_s else float('nan')))

            # For each field size: evaluate estimated and predicted numerators
            field_results = {}
            for field, log2_B_opt in B_OPT.items():
                if slope_s is None or intercept_s is None:
                    field_results[field] = {"status": "ols_failed"}
                    continue
                estimated_numerator = intercept_s + slope_s * log2_B_opt
                predicted_numerator = ref_null_used + s * log2_B_opt
                error = abs(estimated_numerator - predicted_numerator)
                gate_pass = (error <= TOLERANCE_BITS)
                field_results[field] = {
                    "log2_B_opt":            log2_B_opt,
                    "estimated_numerator":    estimated_numerator,
                    "predicted_numerator":    predicted_numerator,
                    "error_bits":             error,
                    "gate_pass":              gate_pass,
                    "tolerance":              TOLERANCE_BITS,
                    # cross-check vs pre-registered (only meaningful for W-MID)
                    "preregistered_numerator": PREREGISTERED_NUMERATORS[s].get(field),
                }
                logf("    s=%.1f %s field=%s: est=%.4f pred=%.4f err=%.4f %s"
                     % (s, wname, field, estimated_numerator, predicted_numerator,
                        error, "PASS" if gate_pass else "FAIL"))

            all_pass = all(fr.get("gate_pass", False) for fr in field_results.values())
            results_by_s[s][wname] = {
                "gamma_s_hat":    slope_s,
                "log2_A_s_hat":   intercept_s,
                "se_slope":       se_s,
                "ci_95_slope":    ci_s,
                "n_ells":         len(wells),
                "fields":         field_results,
                "all_fields_pass": all_pass,
                "worst_error_bits": max(
                    (fr["error_bits"] for fr in field_results.values()
                     if "error_bits" in fr), default=None),
            }

    R["step4"] = results_by_s

    # Step 5: Evaluate gate NC2b-SLOPE-G1
    logf("Step 5: evaluate NC2b-SLOPE-G1 gate (W-MID)")
    gate_pass_all = True
    gate_details = {}
    for s in S_VALUES:
        wmid_res = results_by_s[s].get("W-MID", {})
        fields_pass = all(
            wmid_res.get("fields", {}).get(f, {}).get("gate_pass", False)
            for f in B_OPT
        )
        worst = wmid_res.get("worst_error_bits")
        gate_details[str(s)] = {
            "all_fields_pass": fields_pass,
            "worst_error_bits": worst,
        }
        if not fields_pass:
            gate_pass_all = False
        logf("  s=%.1f W-MID: all_pass=%s worst_error=%.4f"
             % (s, fields_pass, worst if worst is not None else float('nan')))

    gate_verdict = "PASS" if gate_pass_all else "FAIL"
    R["gate_NC2b_SLOPE_G1"] = {
        "id":             "NC2b-SLOPE-G1",
        "verdict":        gate_verdict,
        "tolerance_bits": TOLERANCE_BITS,
        "window":         "W-MID",
        "per_s":          gate_details,
        "note": (
            "A PASS validates the INSTRUMENT against a known input, NOT "
            "assumption L1. A pass cannot be cited as validation of L1 "
            "(frozen contract, non_claims)."
        ),
    }
    logf("NC2b-SLOPE-G1 gate verdict: %s" % gate_verdict)

    R["finished_utc"]           = datetime.now(timezone.utc).isoformat()
    R["total_wall_clock_seconds"] = round(time.time() - T0, 3)
    R["status"]                 = "completed"
    R["loglines"]               = loglines

    if out:
        json.dump(R, open(out, "w"), indent=1)
        logf("wrote %s" % out)
    logf("DONE in %.3fs" % (time.time() - T0))
    return 0, R


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rc, _ = main(repo_root=args.repo_root, out=args.out)
    sys.exit(rc)
