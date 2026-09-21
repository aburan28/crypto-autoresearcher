#!/usr/bin/env python3
"""EXP-P13-NC2d / NC2d-PROPER: C-PSCALE re-run at ell in {47,101,151,211}.

Observations only.  No interpretation, no status change, no hypothesis promotion.

Permanent constraint (DEC-20260802-48c72c): the frozen specification governs.
Regressor is log2(log2 p) NOT log2(p) — the handoff's simplified description
is overridden by the frozen spec.

The instrument is experiments/EXP-PEC-6be870/implementation/per_entry_cost.py,
imported by path; not copied or re-implemented.
"""

import argparse
import hashlib
import importlib.util
import json
import math
import os
import random
import subprocess
import sys
import time
from datetime import datetime, timezone

# ── frozen contract constants ────────────────────────────────────────────────

RUN_ID         = "RUN-P13-NC2d-a"
EXP_ID         = "EXP-P13-NC2d"
TASK_ID        = "TASK-20260804-241b87"

MEASUREMENT_ELL = [47, 101, 151, 211]
J_POOL_SIZE     = 4
WALK_SEEDS      = [20260802001, 20260802002, 20260802003, 20260802004]

# p3 = largest prime < 2^40 with p ≡ 3 (mod 4), from committed run
P3              = 1099511627563
LOG2_P3         = math.log2(P3)

# Committed per_entry medians at p3 (IMPL-A) from RUN-PEC-49c773-a
# (medians over j-indices 0..7, primary IMPL-A samples)
COMMITTED_P3_PRIMARY = {
    47:  22712.416666666668,   # median of 8 values
    101: 46482.652450980392,   # median of 8 values
    151: 67928.865131578947,   # median of 8 values
    211: 94026.771226415094,   # median of 8 values
}

# Committed null per_entry at p3 (IMPL-A) from RUN-PEC-49c773-a C-NULL
# (per_ell_per_entry, median over 8 j-values)
COMMITTED_P3_NULL = {
    47:  4874.489583333334,
    101: 4903.127450980392,
    151: 4923.529605263158,
    211: 4914.452830188679,
}

# Pre-registered band and gap bound (frozen from spec)
PREREGISTERED_BAND  = [0.85, 1.15]
PREDICTED_ALPHA     = 1.0
NULL_GAP_BOUND      = 0.15  # FC-4 threshold

# SHA-256 of committed Phi_ell files from RUN-PEC-49c773-a
COMMITTED_SHA256 = {
    47:  "0f59ebd98b232a0a41515a72e480ed911fa403a7520231709f3643c668b57755",
    101: "47293c73985468b2888c312533a2b52def7231d3e358aaccd30bc126af59535a",
    151: "37257bb3ab89608b82723f2cd2836b7e77aff7eef2a233814deb3cde418efe26",
    211: "277c461643f606cf10698953409952b96746f0d3e240ca8286726fc9bdd269ee",
}

MODPOLY_URL_FMT = "https://math.mit.edu/~drew/modpolys/jfiles/phi_j_%d.txt"
INSTRUMENT_PATH = "experiments/EXP-PEC-6be870/implementation/per_entry_cost.py"
INSTRUMENT_SHA256_COMMITTED = (
    "aea73ef79c3bdf6091b1fd61950bd8449618b295effd9d39a096f65197020ef1")


# ── helpers ──────────────────────────────────────────────────────────────────

def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def median(vals):
    s = sorted(vals)
    n = len(s)
    if n == 0:
        return None
    mid = n // 2
    if n % 2 == 0:
        return (s[mid - 1] + s[mid]) / 2.0
    return float(s[mid])


def ols_3pt(xs, ys):
    """OLS slope and intercept for three (x, y) pairs."""
    n = len(xs)
    assert n == 3
    xm = sum(xs) / n
    ym = sum(ys) / n
    cov = sum((xs[i] - xm) * (ys[i] - ym) for i in range(n)) / n
    var = sum((x - xm)**2 for x in xs) / n
    if var == 0:
        return None, None
    slope = cov / var
    intercept = ym - slope * xm
    return slope, intercept


def ols_slope_se(xs, ys, slope, intercept):
    """Analytic OLS SE for slope (3 points)."""
    n = len(xs)
    resids = [ys[i] - (slope * xs[i] + intercept) for i in range(n)]
    sse = sum(r**2 for r in resids)
    if n <= 2 or sse == 0:
        return 0.0
    s2 = sse / (n - 2)
    xm = sum(xs) / n
    sxx = sum((x - xm)**2 for x in xs)
    if sxx == 0:
        return float('inf')
    return math.sqrt(s2 / sxx)


def ols_pooled_fixed_effects(data_by_ell):
    """Pooled OLS with ell fixed effects.

    data_by_ell: {ell: [(log2_log2_p, log2_per_entry), ...]}
    Returns pooled alpha (slope coefficient on log2(log2 p)).
    """
    # Within-ell demeaning
    xs_demeaned, ys_demeaned = [], []
    for ell in sorted(data_by_ell):
        pts = data_by_ell[ell]
        xm = sum(p[0] for p in pts) / len(pts)
        ym = sum(p[1] for p in pts) / len(pts)
        for (x, y) in pts:
            xs_demeaned.append(x - xm)
            ys_demeaned.append(y - ym)
    # OLS on demeaned data
    cov = sum(xs_demeaned[i] * ys_demeaned[i]
              for i in range(len(xs_demeaned))) / len(xs_demeaned)
    var = sum(x**2 for x in xs_demeaned) / len(xs_demeaned)
    if var == 0:
        return None
    return cov / var


def jackknife_leave_one_ell(per_ell_alpha):
    """Leave-one-ell-out jackknife over the 4 ell values.

    per_ell_alpha: {ell: alpha_hat}
    Returns [min, max] of the four leave-one-out pooled estimates.
    """
    ells = sorted(per_ell_alpha.keys())
    estimates = []
    for leave_out in ells:
        remaining = [e for e in ells if e != leave_out]
        alphas = [per_ell_alpha[e] for e in remaining]
        estimates.append(sum(alphas) / len(alphas))
    return [min(estimates), max(estimates)]


def log(msg, t0=None, loglines=None):
    t = time.time()
    if t0 is not None:
        line = "[%7.1fs] %s" % (t - t0, msg)
    else:
        line = msg
    print(line, flush=True)
    if loglines is not None:
        loglines.append(line)
    return line


# ── modular polynomial acquisition ──────────────────────────────────────────

def fetch_and_verify_modpoly(ell, outdir, log_fn):
    """Fetch phi_j_{ell}.txt, verify SHA-256 against committed value.

    Returns (local_path, sha256, status_record).
    """
    url = MODPOLY_URL_FMT % ell
    dest = os.path.join(outdir, "phi_j_%d.txt" % ell)
    committed = COMMITTED_SHA256[ell]

    # Check if file already exists with correct hash
    if os.path.exists(dest):
        actual = file_sha256(dest)
        if actual == committed:
            log_fn("  ell=%d: local file present, SHA-256 matches committed" % ell)
            return dest, actual, {"ell": ell, "status": "local_verified",
                                  "sha256": actual, "committed_sha256": committed,
                                  "match": True}
        else:
            log_fn("  ell=%d: local file present but SHA-256 MISMATCH, re-fetching" % ell)
            os.remove(dest)

    # Fetch
    ts = datetime.now(timezone.utc).isoformat()
    t1 = time.time()
    cmd = ["curl", "-sS", "--max-time", "120", "-w", "%{http_code}", "-o", dest, url]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=135)
        code = proc.stdout.strip()
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        code, rc = "", -1

    dt = time.time() - t1

    if rc != 0 or code != "200" or not os.path.exists(dest):
        rec = {"ell": ell, "status": "fetch_failed", "url": url,
               "fetch_utc": ts, "http_status": code, "returncode": rc,
               "fetch_seconds": round(dt, 3)}
        log_fn("  ell=%d: FETCH FAILED http_status=%s rc=%d" % (ell, code, rc))
        return None, None, rec

    actual = file_sha256(dest)
    byte_len = os.path.getsize(dest)
    match = (actual == committed)
    rec = {"ell": ell, "status": "fetched", "url": url, "fetch_utc": ts,
           "http_status": int(code), "byte_length": byte_len,
           "sha256": actual, "committed_sha256": committed,
           "match": match, "fetch_seconds": round(dt, 3)}
    if match:
        log_fn("  ell=%d: fetched %.1f kB, SHA-256 MATCH" % (ell, byte_len / 1024))
    else:
        log_fn("  ell=%d: fetched %.1f kB, SHA-256 MISMATCH actual=%s committed=%s"
               % (ell, byte_len / 1024, actual[:16], committed[:16]))
    return (dest if match else None), actual, rec


# ── prime finder (from per_entry_cost.py mirror) ─────────────────────────────

def miller_rabin(n, bases):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in bases:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


FIRST_20_PRIME_BASES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
                        31, 37, 41, 43, 47, 53, 59, 61, 67, 71]


def largest_prime_below(bound, cong, mod):
    """Largest prime p < bound with p ≡ cong (mod mod)."""
    n = bound - 1
    if n % mod != cong:
        n -= (n % mod - cong) % mod
    while n >= 2:
        if miller_rabin(n, FIRST_20_PRIME_BASES):
            return n
        n -= mod
    raise ValueError("no prime found below %d with p ≡ %d (mod %d)" % (bound, cong, mod))


# ── single prime arm ──────────────────────────────────────────────────────────

def run_arm(label, log2_bound, modpoly_paths, walk_seeds, ell_list, PE, log_fn):
    """Measure per_entry for ell_list at the largest prime < 2^log2_bound, p≡3 mod 4."""
    result = {"label": label, "log2_bound": log2_bound}
    try:
        p = largest_prime_below(2**log2_bound, cong=3, mod=4)
        PE.set_prime(p)
        result["p"] = p
        result["log2_p"] = math.log2(p)
        log_fn("  arm %s: p=%d (log2_p=%.6f)" % (label, p, result["log2_p"]))

        # C-BASE.1
        rng_cbase = random.Random("EXP-P13-NC2d|cbase1|%d" % log2_bound)
        cb1 = PE.control_c_base_1(p, rng_cbase)
        result["C-BASE-1"] = cb1
        log_fn("    C-BASE-1: %s" % cb1["verdict"])
        if cb1["verdict"] != "pass":
            result["status"] = "cbase1_fail"
            return result

        # Parse and reduce modpolys
        mod = {}
        cbase2 = {}
        for ell in [2] + list(ell_list):
            path = modpoly_paths.get(ell)
            if path is None:
                log_fn("    ell=%d: modpoly path missing, skip" % ell)
                continue
            terms, saw, dup = PE.parse_modpoly(path)
            v = PE.verify_modpoly(ell, terms, saw, dup)
            cbase2[ell] = v["verdict"]
            if v["verdict"] != "pass":
                log_fn("    ell=%d: C-BASE.2 FAIL" % ell)
                continue
            mod[ell] = PE.reduce_modpoly(ell, terms, p)
            del terms
        result["C-BASE-2"] = cbase2
        log_fn("    C-BASE-2 verdicts: %s" % cbase2)

        # Walk pool
        n_walk = 3 * math.ceil(math.log2(p))
        result["n_walk"] = n_walk
        result["walk_seeds"] = list(walk_seeds)
        pool, _chains = PE.walk_pool(mod[2], n_walk, walk_seeds, lambda m: None)
        result["pool"] = [[j[0], j[1]] for j in pool]
        log_fn("    walk: n_walk=%d, pool_size=%d" % (n_walk, len(pool)))

        # Set globals for the instrument's measure_ functions
        PE._G["mod"] = mod
        PE._G["pool"] = pool
        PE.CNT[0] = 0
        PE.CNT[1] = 0
        PE.GTOT[0] = 0
        PE.GTOT[1] = 0

        # Primary measurements (IMPL-A only, j 0..3)
        prim = []
        nul  = []
        t_start = time.time()
        for ell in ell_list:
            if ell not in mod:
                log_fn("    ell=%d: skipped (no modpoly)" % ell)
                continue
            for ji in range(len(pool)):
                r = PE.measure_primary((ell, ji, "IMPL-A"))
                prim.append(r)
                n = PE.measure_null((ell, ji, "IMPL-A"))
                nul.append(n)
                # Reset counters between samples to keep C-INSTR isolation
                PE.CNT[0] = 0
                PE.CNT[1] = 0
        t_end = time.time()

        result["samples_primary"] = prim
        result["samples_null"] = nul
        result["measurement_seconds"] = round(t_end - t_start, 3)
        log_fn("    measured %d primary + %d null samples in %.1fs"
               % (len(prim), len(nul), t_end - t_start))
        result["status"] = "ok"
    except Exception as exc:
        result["status"] = "error"
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
        log_fn("  arm %s ERROR: %s" % (label, result["error"]))
    return result


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    T0 = time.time()
    root = os.path.abspath(args.repo_root)
    loglines = []

    def logf(msg):
        log(msg, T0, loglines)

    logf("NC2d-PROPER (EXP-P13-NC2d) starting")
    logf("Permanent constraint: frozen spec governs. Regressor is log2(log2 p).")

    # Detect handoff conflict
    handoff_conflict = (
        "CONFLICT DETECTED: handoff description says 'Fit OLS: log2(cost) = "
        "alpha * log2(p) + const' but the frozen specification says regressor "
        "is log2(log2 p). Frozen spec governs (DEC-20260802-48c72c). Using "
        "log2(log2 p) as regressor."
    )
    logf("CONFLICT: " + handoff_conflict)

    R = {
        "run_id": RUN_ID,
        "experiment_id": EXP_ID,
        "task_id": TASK_ID,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "handoff_conflict": handoff_conflict,
        "protocol_deviations": [],
        "anomalies": [],
    }

    # 1. Verify instrument
    inst_path = os.path.join(root, INSTRUMENT_PATH)
    logf("verifying instrument: %s" % inst_path)
    if not os.path.exists(inst_path):
        R["status"] = "infrastructure_error"
        R["error"] = "instrument not found: %s" % inst_path
        json.dump(R, open(args.out, "w"), indent=1)
        return 1
    inst_sha = file_sha256(inst_path)
    inst_match = (inst_sha == INSTRUMENT_SHA256_COMMITTED)
    R["instrument"] = {
        "path": INSTRUMENT_PATH,
        "sha256_observed": inst_sha,
        "sha256_committed": INSTRUMENT_SHA256_COMMITTED,
        "match": inst_match,
    }
    logf("  instrument SHA-256 match: %s" % inst_match)
    if not inst_match:
        R["anomalies"].append(
            "instrument SHA-256 changed: observed=%s committed=%s"
            % (inst_sha[:16], INSTRUMENT_SHA256_COMMITTED[:16]))

    # 2. Import instrument
    spec = importlib.util.spec_from_file_location("per_entry_cost", inst_path)
    PE = importlib.util.module_from_spec(spec)
    # Suppress instrument's main() on import
    _orig_argv = sys.argv
    sys.argv = ["per_entry_cost.py"]
    spec.loader.exec_module(PE)
    sys.argv = _orig_argv
    logf("  instrument imported OK")

    # 3. Fetch and verify Phi_ell files
    scratch_modpolys = os.path.join(args.scratch, "modpolys_nc2d")
    os.makedirs(scratch_modpolys, exist_ok=True)
    phi_verify = {}
    modpoly_paths = {}
    logf("C-PHI-VERIFY: checking Phi_ell files for ell in %s" % MEASUREMENT_ELL)
    for ell in MEASUREMENT_ELL:
        path, sha256, rec = fetch_and_verify_modpoly(ell, scratch_modpolys, logf)
        phi_verify[ell] = rec
        if path is not None:
            modpoly_paths[ell] = path
        else:
            logf("  ell=%d: MISSING or SHA-256 mismatch — cannot proceed with this ell" % ell)

    # Also need phi_j_2.txt for the walk
    url2 = MODPOLY_URL_FMT % 2
    dest2 = os.path.join(scratch_modpolys, "phi_j_2.txt")
    if not os.path.exists(dest2):
        logf("fetching phi_j_2.txt for walk...")
        proc = subprocess.run(
            ["curl", "-sS", "--max-time", "30", "-o", dest2, url2],
            capture_output=True, text=True, timeout=45)
        if proc.returncode != 0 or not os.path.exists(dest2):
            R["status"] = "infrastructure_error"
            R["error"] = "could not fetch phi_j_2.txt for walk"
            json.dump(R, open(args.out, "w"), indent=1)
            return 1
    modpoly_paths[2] = dest2

    R["C-PHI-VERIFY"] = {str(ell): phi_verify[ell] for ell in MEASUREMENT_ELL}
    all_verified = all(phi_verify[ell].get("match", False) for ell in MEASUREMENT_ELL)
    logf("  C-PHI-VERIFY all matched: %s" % all_verified)
    if not all_verified:
        missing = [ell for ell in MEASUREMENT_ELL if not phi_verify[ell].get("match")]
        R["status"] = "infrastructure_error"
        R["error"] = "C-PHI-VERIFY failed for ell=%s" % missing
        logf("STOPPING: C-PHI-VERIFY failed")
        R["loglines"] = loglines
        json.dump(R, open(args.out, "w"), indent=1)
        return 1

    # 4. Run measurement arms at p1 and p2
    logf("running measurement arms at p1 (2^20) and p2 (2^30)")
    arms = {}
    for (label, log2_bound) in [("p1", 20), ("p2", 30)]:
        logf("arm %s (2^%d)..." % (label, log2_bound))
        arm = run_arm(label, log2_bound, modpoly_paths, WALK_SEEDS,
                      MEASUREMENT_ELL, PE, logf)
        arms[label] = arm
        logf("  arm %s done: status=%s" % (label, arm.get("status")))
    R["arms"] = arms

    # 5. Check arm status
    if any(arms[k].get("status") != "ok" for k in arms):
        failed = [k for k in arms if arms[k].get("status") != "ok"]
        R["status"] = "infrastructure_error"
        R["error"] = "arms failed: %s" % failed
        R["loglines"] = loglines
        json.dump(R, open(args.out, "w"), indent=1)
        return 1

    # 6. Compute per_entry medians at p1 and p2
    def arm_medians(arm, series="primary"):
        key = "samples_primary" if series == "primary" else "samples_null"
        samples = arm.get(key, [])
        by_ell = {}
        for s in samples:
            ell = s["ell"]
            pe = s.get("per_entry")
            if pe is not None:
                by_ell.setdefault(ell, []).append(pe)
        return {ell: median(vals) for ell, vals in by_ell.items()}

    p1_primary = arm_medians(arms["p1"], "primary")
    p2_primary = arm_medians(arms["p2"], "primary")
    p1_null    = arm_medians(arms["p1"], "null")
    p2_null    = arm_medians(arms["p2"], "null")

    logf("per_entry medians at p1: primary=%s null=%s" % (p1_primary, p1_null))
    logf("per_entry medians at p2: primary=%s null=%s" % (p2_primary, p2_null))
    logf("per_entry medians at p3 (committed): primary=%s null=%s"
         % (COMMITTED_P3_PRIMARY, COMMITTED_P3_NULL))

    # 7. Build data series: points = [(log2_log2_p, log2_per_entry), ...]
    log2_p_p1 = arms["p1"]["log2_p"]
    log2_p_p2 = arms["p2"]["log2_p"]
    log2_p_p3 = LOG2_P3

    def x(log2_p):
        return math.log2(log2_p)

    primes_info = {
        "p1": {"p": arms["p1"]["p"], "log2_p": log2_p_p1, "log2_log2_p": x(log2_p_p1)},
        "p2": {"p": arms["p2"]["p"], "log2_p": log2_p_p2, "log2_log2_p": x(log2_p_p2)},
        "p3": {"p": P3, "log2_p": log2_p_p3, "log2_log2_p": x(log2_p_p3)},
    }
    R["primes"] = primes_info
    logf("primes: %s" % {k: "p=%d log2_p=%.3f x=%.4f" % (v["p"], v["log2_p"], v["log2_log2_p"])
                          for k, v in primes_info.items()})

    # 8. Per-ell OLS alpha_hat and alpha_null
    per_ell_results = {}
    alpha_primary_by_ell = {}
    alpha_null_by_ell    = {}

    for ell in MEASUREMENT_ELL:
        # Primary
        xs_p = [x(log2_p_p1), x(log2_p_p2), x(log2_p_p3)]
        vals_primary = [
            p1_primary.get(ell),
            p2_primary.get(ell),
            COMMITTED_P3_PRIMARY.get(ell),
        ]
        vals_null = [
            p1_null.get(ell),
            p2_null.get(ell),
            COMMITTED_P3_NULL.get(ell),
        ]

        if any(v is None for v in vals_primary):
            per_ell_results[ell] = {"status": "missing_data", "vals_primary": vals_primary}
            logf("  ell=%d: missing primary data, skip" % ell)
            continue

        ys_p = [math.log2(v) for v in vals_primary]
        ys_n = [math.log2(v) for v in vals_null]

        slope_p, intercept_p = ols_3pt(xs_p, ys_p)
        se_p = ols_slope_se(xs_p, ys_p, slope_p, intercept_p)
        slope_n, intercept_n = ols_3pt(xs_p, ys_n)
        se_n = ols_slope_se(xs_p, ys_n, slope_n, intercept_n)

        alpha_primary_by_ell[ell] = slope_p
        alpha_null_by_ell[ell]    = slope_n

        per_ell_results[ell] = {
            "ell": ell,
            "log2_log2_p": xs_p,
            "log2_per_entry_primary": ys_p,
            "log2_per_entry_null": ys_n,
            "per_entry_primary": vals_primary,
            "per_entry_null": vals_null,
            "alpha_hat_primary": slope_p,
            "alpha_hat_primary_se": se_p,
            "alpha_hat_null": slope_n,
            "alpha_hat_null_se": se_n,
            "gap_abs": abs(slope_p - slope_n),
            "status": "ok",
        }
        logf("  ell=%d: alpha_primary=%.4f (SE=%.4f) alpha_null=%.4f (SE=%.4f) gap=%.4f"
             % (ell, slope_p, se_p, slope_n, se_n, abs(slope_p - slope_n)))

    R["per_ell"] = per_ell_results

    # 9. Pooled OLS with ell fixed effects
    if len(alpha_primary_by_ell) < 2:
        R["status"] = "insufficient_data"
        R["error"] = "fewer than 2 ell with valid alpha estimates"
        R["loglines"] = loglines
        json.dump(R, open(args.out, "w"), indent=1)
        return 1

    # Build data dict for pooled OLS
    data_primary = {}
    data_null = {}
    for ell in MEASUREMENT_ELL:
        if ell not in alpha_primary_by_ell:
            continue
        xs_p = [x(log2_p_p1), x(log2_p_p2), x(log2_p_p3)]
        vals_p = [
            p1_primary.get(ell),
            p2_primary.get(ell),
            COMMITTED_P3_PRIMARY.get(ell),
        ]
        vals_n = [
            p1_null.get(ell),
            p2_null.get(ell),
            COMMITTED_P3_NULL.get(ell),
        ]
        data_primary[ell] = list(zip(xs_p, [math.log2(v) for v in vals_p]))
        data_null[ell]    = list(zip(xs_p, [math.log2(v) for v in vals_n]))

    alpha_primary = ols_pooled_fixed_effects(data_primary)
    alpha_null    = ols_pooled_fixed_effects(data_null)
    gap_pooled    = abs(alpha_primary - alpha_null) if (alpha_primary is not None
                                                         and alpha_null is not None) else None

    logf("pooled: alpha_primary=%.4f alpha_null=%.4f gap=%.4f"
         % (alpha_primary, alpha_null, gap_pooled))

    # 10. Jackknife leave-one-ell-out
    jk = jackknife_leave_one_ell(alpha_primary_by_ell)
    logf("jackknife [min, max] = [%.4f, %.4f]" % (jk[0], jk[1]))

    # 11. No-trend check: fit alpha_hat(ell) ~ b * log2(ell) + const over 4 ells
    ells_for_trend = sorted(alpha_primary_by_ell.keys())
    if len(ells_for_trend) >= 2:
        xs_trend = [math.log2(e) for e in ells_for_trend]
        ys_trend = [alpha_primary_by_ell[e] for e in ells_for_trend]
        # OLS
        xm = sum(xs_trend) / len(xs_trend)
        ym = sum(ys_trend) / len(ys_trend)
        cov = sum((xs_trend[i] - xm) * (ys_trend[i] - ym)
                  for i in range(len(xs_trend))) / len(xs_trend)
        var_x = sum((x - xm)**2 for x in xs_trend) / len(xs_trend)
        b_trend = cov / var_x if var_x > 0 else None
        if b_trend is not None and len(ells_for_trend) > 2:
            b_intercept = ym - b_trend * xm
            resids = [ys_trend[i] - (b_trend * xs_trend[i] + b_intercept)
                      for i in range(len(xs_trend))]
            sse = sum(r**2 for r in resids)
            n = len(xs_trend)
            s2 = sse / (n - 2) if n > 2 else 0
            sxx = sum((x - xm)**2 for x in xs_trend)
            b_se = math.sqrt(s2 / sxx) if sxx > 0 else float('inf')
        else:
            b_se = None
        no_trend_pass = (b_trend is not None and abs(b_trend) <= 0.10)
        logf("no-trend: b=%.4f SE=%s pass=%s"
             % (b_trend, ("%.4f" % b_se if b_se is not None else "n/a"), no_trend_pass))
    else:
        b_trend = None
        b_se = None
        no_trend_pass = None
        logf("no-trend check: insufficient ell count")

    R["no_trend"] = {
        "b": b_trend,
        "se": b_se,
        "pass_criterion": "|b| <= 0.10",
        "verdict": ("PASS" if no_trend_pass else ("FAIL" if b_trend is not None else "INSUFFICIENT_DATA")),
    }

    # 12. FC-2 and FC-4 evaluation
    # FC-2: jackknife interval disjoint from [0.85, 1.15]
    if jk[0] is not None and jk[1] is not None:
        fc2_fired = (jk[1] < PREREGISTERED_BAND[0] or jk[0] > PREREGISTERED_BAND[1])
        jk_overlap = not fc2_fired
        jk_contained = (jk[0] >= PREREGISTERED_BAND[0] and jk[1] <= PREREGISTERED_BAND[1])
    else:
        fc2_fired = None
        jk_overlap = None
        jk_contained = None

    # FC-4: |alpha_primary - alpha_null| > 0.15
    if gap_pooled is not None:
        fc4_fired = gap_pooled > NULL_GAP_BOUND
    else:
        fc4_fired = None

    # Rerank trigger: FC-4 fires
    rerank_trigger = fc4_fired

    logf("FC-2 fired: %s (JK=[%.4f, %.4f], band=%s)"
         % (fc2_fired, jk[0], jk[1], PREREGISTERED_BAND))
    logf("FC-4 fired: %s (|alpha_primary - alpha_null| = %.4f, threshold=%.2f)"
         % (fc4_fired, gap_pooled if gap_pooled is not None else float('nan'), NULL_GAP_BOUND))
    logf("RERANK TRIGGER: %s" % ("FIRES" if rerank_trigger else "DOES NOT FIRE"))

    # 13. Comparison to prior
    prior = {
        "experiment_id": "EXP-PEC-49c773",
        "run_id": "RUN-PEC-49c773-a",
        "control": "C-PSCALE",
        "ell_set_prior": [3, 5, 7, 11, 13],
        "alpha_primary_prior": 1.1596976732,
        "alpha_null_prior":    0.9935080487,
        "gap_prior":           0.1661896244,
        "FC4_prior":           True,
        "note": ("Prior FC-4 fired at ell in {3,5,7,11,13} (some below Karatsuba "
                 "threshold). This run is a NEW measurement at ell in {47,101,151,211} "
                 "(all above Karatsuba threshold). Prior firing stands as a matter of record."),
    }

    # 14. Final result assembly
    R["pooled"] = {
        "alpha_primary": alpha_primary,
        "alpha_null":    alpha_null,
        "gap":           gap_pooled,
    }
    R["jackknife"] = {
        "interval": jk,
        "overlap_with_band": jk_overlap,
        "contained_in_band": jk_contained,
        "band": PREREGISTERED_BAND,
    }
    R["FC_2"] = {
        "condition": "jackknife interval disjoint from [0.85, 1.15]",
        "fired": fc2_fired,
        "verdict": ("FC-2 FIRED" if fc2_fired else "FC-2 DID NOT FIRE"),
    }
    R["FC_4"] = {
        "condition": "|alpha_primary - alpha_null| > 0.15",
        "value": gap_pooled,
        "threshold": NULL_GAP_BOUND,
        "fired": fc4_fired,
        "verdict": ("FC-4 FIRED" if fc4_fired else "FC-4 DID NOT FIRE"),
    }
    R["RERANK_TRIGGER"] = {
        "fired": rerank_trigger,
        "verdict": ("RERANK TRIGGER FIRES" if rerank_trigger else
                    "RERANK TRIGGER DOES NOT FIRE"),
        "consequence": (
            "If FIRES: batch remaining capacity redirects to characterising "
            "discrepancy; NC-3/NC-6 NOT executed. "
            "If DOES NOT FIRE: MECHANISM-INCONSISTENT label on L5 RETIRED "
            "BY MEASUREMENT; NC-3/NC-6 unblocked."
        ),
    }
    R["comparison_to_prior"] = prior
    R["finished_utc"] = datetime.now(timezone.utc).isoformat()
    R["total_wall_clock_seconds"] = round(time.time() - T0, 3)
    R["status"] = "completed"
    R["loglines"] = loglines

    json.dump(R, open(args.out, "w"), indent=1)
    logf("wrote %s (%.0f kB)" % (args.out, os.path.getsize(args.out) / 1024))
    logf("DONE in %.1fs" % (time.time() - T0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
