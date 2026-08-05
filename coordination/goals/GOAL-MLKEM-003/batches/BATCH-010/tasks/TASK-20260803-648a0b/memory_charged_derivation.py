#!/usr/bin/env python3
"""Memory-charged re-derivation of the FIPS 203 NIST margin under RC.MATZOV.

TASK-20260803-648a0b / BATCH-010 / GOAL-MLKEM-003.

WHAT THIS DOES
--------------
EV-MLKEM-015 recorded that `primal_bdd` under `RC.MATZOV` costs
140.1994731076 / 200.9587149141 / 270.7236234535 bits for Kyber-512/768/1024,
which is BELOW the NIST classical category cutoffs 143 / 207 / 272 by
2.80 / 6.04 / 1.28 bits.  That cost model is a pure gate count: it charges
nothing at all for the sieve database or for reaching it.

This script asks one question and answers it exactly:

    c*  =  the smallest memory-charge exponent c such that charging M^c to the
           attack raises its estimated cost to the NIST cutoff, i.e. the
           smallest c that ERASES the undercut.

Nothing here is a measurement.  Every number below is a COST-MODEL ESTIMATE
produced by a pinned estimator plus explicitly numbered modelling choices
(see `heuristics.yaml`, H1..H12).  No ML-KEM break is claimed, and a c that
RAISES the estimated cost is not a proof of security either -- it is a
statement about one cost model at one parameter set under stated heuristics.

INSTRUMENT DISCIPLINE
---------------------
Step 0 shells out to `tools/sage_free_estimator/known_answer_control.py` and
refuses to continue unless it exits 0 with delta 0.00e+00 against the
Sage-computed reference archived in RUN-MLKEM-015-001.  Arora-Groebner is
unavailable in this harness (`PowerSeriesRing` is a raising stub), so no
statement here is scoped as "best attack overall" -- only `primal_bdd` under
`RC.MATZOV`, which is the combination the control covers.

USAGE
-----
    git clone --depth 1 https://github.com/malb/lattice-estimator /tmp/le
    git -C /tmp/le rev-parse HEAD   # 3e48ef421ec256afddb3e7d2249a77eab6e9ba12
    PYTHONPATH=<repo>/tools/sage_free_estimator/shim:/tmp/le \
        python3 memory_charged_derivation.py --out results.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import subprocess
import sys
import time

# --------------------------------------------------------------------------
# Fixed inputs.  These are NOT recomputed here; they are the frozen references
# the run is scored against.
# --------------------------------------------------------------------------

PINNED_ESTIMATOR_COMMIT = "3e48ef421ec256afddb3e7d2249a77eab6e9ba12"

# NIST classical category cutoffs, in bits of classical gate count.
# Provenance: recorded in RUN-MLKEM-015-001/raw-result.json ("nist_cutoffs")
# and quoted as "the NIST classical requirements (143 / 207 / 272 bits)" by
# KN-LIT-7617 (Carrier et al.) and KN-LIT-110 (MATZOV 2022).  Not re-derived
# from the NIST call for proposals in this batch -- see heuristic H11.
NIST_CLASSICAL_CUTOFF = {"Kyber512": 143.0, "Kyber768": 207.0, "Kyber1024": 272.0}

# Free-memory (c = 0) reference costs from RUN-MLKEM-015-001, computed under
# real Sage.  Used only as an equality check on this run's own recomputation.
EV_MLKEM_015_REFERENCE_LOG2_ROP = {
    "Kyber512": 140.1994731076207,
    "Kyber768": 200.9587149140538,
    "Kyber1024": 270.7236234535225,  # no Sage reference in the control file;
                                     # value as recorded in RUN-MLKEM-015-001.
}

# Sieve database size exponent.  N_vectors(n) = 2^(SIEVE_DB_EXPONENT * n).
# SOURCED, three ways -- see heuristic H4:
#   (a) in-instrument: the pinned lattice-estimator writes
#       `floor(2 ** (0.2075 * beta_))` for the number of vectors a sieve in
#       dimension beta_ outputs, at reduction.py:415, :854, :936 (commit
#       3e48ef4);
#   (b) closed form: log2(sqrt(4/3)) = 0.2075187496... , the Gaussian-heuristic
#       count of lattice points within sqrt(4/3) * gh(n), checked below (CTRL-3);
#   (c) literature in this repo's corpus: KN-LIT-104 (Micciancio-Voulgaris 2010,
#       Gauss Sieve space proportional to the kissing constant, tau_n >
#       2^((0.2075+o(1))n)), KN-LIT-6625 (angular-LSH sieve, 2^(0.2075n+o(n))
#       space), KN-LIT-6765 (triple sieve, 2^(0.2075n+o(n)) memory),
#       KN-LIT-081 (0.2075187n list exponent), KN-TECH-044, KN-OPEN-017.
SIEVE_DB_EXPONENT = 0.2075
SIEVE_DB_EXPONENT_CLOSED_FORM = math.log2(math.sqrt(4.0 / 3.0))

# Memory-charge exponents to report.  Provenance per entry in heuristics.yaml
# (H6/H7/H8) and in results.json under "charge_conventions".
NAMED_CHARGES = [
    ("c=0 free memory", 0.0),
    ("c=1/6", 1.0 / 6.0),
    ("c=1/3 (3D wiring)", 1.0 / 3.0),
    ("c=1/2 (2D layout)", 0.5),
    ("c=1 (hardware x time)", 1.0),
]

# Fine sweep, used to locate c* by bisection independently of the closed form.
SWEEP = [i / 1000.0 for i in range(0, 1001)]

# Fraction-of-gates-that-are-memory-accesses sensitivity (heuristic H9).
ACCESS_FRACTIONS_LOG2 = [0.0, -10.0, -20.0, -30.0]


def run_known_answer_control(repo_root: str, estimator_dir: str) -> dict:
    """Step 0.  Refuse to produce any number from an unvalidated instrument."""
    script = os.path.join(repo_root, "tools", "sage_free_estimator",
                          "known_answer_control.py")
    shim = os.path.join(repo_root, "tools", "sage_free_estimator", "shim")
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{shim}:{estimator_dir}"
    cmd = [sys.executable, script]
    started = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    elapsed = time.time() - started
    return {
        "command": f"PYTHONPATH={shim}:{estimator_dir} {sys.executable} {script}",
        "argv": cmd,
        "pythonpath": env["PYTHONPATH"],
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "wall_seconds": elapsed,
    }


def sieve_memory(sieve_dim: float, log2_q: float, bits_per_coeff: int) -> dict:
    """Sieve database size in three explicitly-converted units.

    UNIT CHAIN (heuristic H5).  A sieve in dimension `n` holds

        N  =  2^(0.2075 * n)                         VECTORS,

    each represented -- following the pinned estimator's own memory
    convention for sieving (`cost["mem"] += sieve_dim * N`, "memory
    requirement in integers mod q", estimator/lwe_dual.py:172 and :204) -- by

        n  coefficients in Z_q,                      so
        M_zq   = n * 2^(0.2075 * n)                  ELEMENTS OF Z_q,  and
        M_bits = ceil(log2 q) * n * 2^(0.2075 * n)   BITS.

    For Kyber, q = 3329, log2 q = 11.700...,  ceil(log2 q) = 12 bits.
    """
    log2_vectors = SIEVE_DB_EXPONENT * sieve_dim
    log2_zq = log2_vectors + math.log2(sieve_dim)
    log2_bits = log2_zq + math.log2(bits_per_coeff)
    log2_bits_info = log2_vectors + math.log2(sieve_dim) + log2_q
    return {
        "sieve_dimension": sieve_dim,
        "log2_memory_vectors": log2_vectors,
        "log2_memory_zq_elements": log2_zq,
        "log2_memory_bits_packed": log2_bits,
        "log2_memory_bits_information_theoretic": log2_bits_info,
        "conversion": (
            f"vectors -> Z_q elements: x {sieve_dim:.6f} coefficients "
            f"(+{math.log2(sieve_dim):.6f} bits); "
            f"Z_q elements -> bits: x {bits_per_coeff} "
            f"(+{math.log2(bits_per_coeff):.6f} bits)"
        ),
    }


def charged_log2_peak(log2_rop: float, log2_mem: float, c: float,
                      log2_access_fraction: float = 0.0) -> float:
    """Model A: charge the whole gate count by the PEAK sieve memory."""
    return log2_rop + log2_access_fraction + c * log2_mem


def charged_log2_perterm(log2_red: float, log2_mem_bkz: float,
                         log2_svp: float, log2_mem_svp: float, c: float,
                         log2_access_fraction: float = 0.0) -> float:
    """Model B: charge each cost term by the memory of the sieve it runs."""
    a = log2_red + log2_access_fraction + c * log2_mem_bkz
    b = log2_svp + log2_access_fraction + c * log2_mem_svp
    hi = max(a, b)
    return hi + math.log2(2.0 ** (a - hi) + 2.0 ** (b - hi))


def bisect_cstar(f, target: float, lo: float = 0.0, hi: float = 4.0,
                 iters: int = 200) -> float:
    """Smallest c in [lo, hi] with f(c) >= target.  f must be increasing."""
    if f(lo) >= target:
        return lo
    if f(hi) < target:
        return float("nan")
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if f(mid) >= target:
            hi = mid
        else:
            lo = mid
    return hi


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=os.environ.get(
        "REPO_ROOT", "/home/user/crypto-autoresearcher"))
    ap.add_argument("--estimator-dir", default=os.environ.get(
        "ESTIMATOR_DIR", "/tmp/le"))
    ap.add_argument("--out", default="results.json")
    ap.add_argument("--control-log", default=None)
    args = ap.parse_args()

    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # ---------------------------------------------------------------- step 0
    print("=" * 78)
    print("STEP 0 -- KNOWN-ANSWER CONTROL (CTRL-0). "
          "No number is produced from an unvalidated instrument.")
    print("=" * 78)
    control = run_known_answer_control(args.repo_root, args.estimator_dir)
    print(f"$ {control['command']}")
    sys.stdout.write(control["stdout"])
    if control["stderr"]:
        sys.stderr.write(control["stderr"])
    print(f"[control exit code: {control['exit_code']}]")
    if control["exit_code"] != 0:
        print("FAIL: known-answer control did not exit 0. "
              "INSTRUMENT FAILURE -- stopping, no numbers produced.",
              file=sys.stderr)
        return 2
    if "delta 0.0" not in control["stdout"]:
        print("FAIL: control stdout does not assert delta 0.0. "
              "INSTRUMENT FAILURE -- stopping.", file=sys.stderr)
        return 2
    if args.control_log:
        with open(args.control_log, "w") as fh:
            fh.write(control["stdout"])
            fh.write(control["stderr"])

    # ------------------------------------------------------------- estimator
    from estimator import RC, schemes                      # noqa: E402
    from estimator.lwe_primal import primal_bdd, PrimalHybrid  # noqa: E402

    est_commit = subprocess.run(
        ["git", "-C", args.estimator_dir, "rev-parse", "HEAD"],
        capture_output=True, text=True).stdout.strip()
    print(f"\nlattice-estimator HEAD: {est_commit}")
    if est_commit != PINNED_ESTIMATOR_COMMIT:
        print(f"FAIL: estimator is not at the pin {PINNED_ESTIMATOR_COMMIT}.",
              file=sys.stderr)
        return 2

    # ---------------------------------------------------- CTRL-3: constant
    print("\n" + "=" * 78)
    print("CTRL-3 -- sieve database exponent: instrument constant vs closed form")
    print("=" * 78)
    print(f"  estimator literal            : {SIEVE_DB_EXPONENT}")
    print(f"  log2(sqrt(4/3))              : {SIEVE_DB_EXPONENT_CLOSED_FORM!r}")
    print(f"  |difference|                 : "
          f"{abs(SIEVE_DB_EXPONENT - SIEVE_DB_EXPONENT_CLOSED_FORM):.3e}")
    ctrl3_pass = abs(SIEVE_DB_EXPONENT - SIEVE_DB_EXPONENT_CLOSED_FORM) < 2e-5
    print(f"  CTRL-3: {'PASS' if ctrl3_pass else 'FAIL'} "
          f"(agree to < 2e-5; the estimator's literal is the rounded closed form)")

    params = {
        "Kyber512": schemes.Kyber512,
        "Kyber768": schemes.Kyber768,
        "Kyber1024": schemes.Kyber1024,
    }

    per_set = {}
    controls = {
        "CTRL-0_known_answer_control": {
            "description": "tools/sage_free_estimator/known_answer_control.py "
                           "reproduces the Sage-computed RUN-MLKEM-015-001 "
                           "primal_bdd/MATZOV costs to delta 0.0",
            "passed": control["exit_code"] == 0,
        },
        "CTRL-3_sieve_exponent_closed_form": {
            "description": "estimator literal 0.2075 vs log2(sqrt(4/3))",
            "estimator_literal": SIEVE_DB_EXPONENT,
            "closed_form": SIEVE_DB_EXPONENT_CLOSED_FORM,
            "abs_difference": abs(SIEVE_DB_EXPONENT
                                  - SIEVE_DB_EXPONENT_CLOSED_FORM),
            "passed": ctrl3_pass,
        },
        "CTRL-1_cost_decomposition": {
            "description": "rop == red + svp exactly, and red/svp are "
                           "independently recomputed as MATZOV(beta,d) and "
                           "MATZOV(eta+1,eta+1) + babai_cost(d-eta)",
            "per_set": {},
        },
        "CTRL-2_baseline_matches_EV_MLKEM_015": {
            "description": "this run's log2(rop) equals the value recorded in "
                           "RUN-MLKEM-015-001 / EV-MLKEM-015",
            "per_set": {},
        },
        "CTRL-4_unit_consistency": {
            "description": "c* scales exactly inversely with log2(M); the ratio "
                           "of c* across units must equal the inverse ratio of "
                           "log2(M) across units (Model A only, where c* is a "
                           "closed form)",
            "per_set": {},
        },
        "CTRL-5_null_object_zero_memory": {
            "description": "NULL-OBJECT CONTROL. Re-run the identical charging "
                           "pipeline on an attack with no memory (log2 M = 0). "
                           "The margin must not move for any c, and c* must be "
                           "undefined (no finite c erases the undercut). This is "
                           "the control that distinguishes 'memory charging bites' "
                           "from 'the pipeline manufactures a penalty'.",
            "per_set": {},
        },
        "CTRL-6_closed_form_vs_bisection": {
            "description": "Model A c* from the closed form m0/log2(M) agrees "
                           "with c* located by bisection on the sweep",
            "per_set": {},
        },
        "CTRL-7_monotonicity": {
            "description": "charged margin is non-increasing in c over the sweep",
            "per_set": {},
        },
    }

    for name, p in params.items():
        print("\n" + "=" * 78)
        print(f"{name}")
        print("=" * 78)

        r = primal_bdd(p, red_cost_model=RC.MATZOV)
        beta, eta, d = int(r["beta"]), int(r["eta"]), int(r["d"])
        rop, red, svp = float(r["rop"]), float(r["red"]), float(r["svp"])
        log2_rop, log2_red, log2_svp = (math.log2(rop), math.log2(red),
                                        math.log2(svp))
        cutoff = NIST_CLASSICAL_CUTOFF[name]
        m0 = cutoff - log2_rop                       # free-memory UNDERCUT, bits

        # --- CTRL-1: independent recomputation of the two cost terms.
        # WHICH DIMENSION DOES THE MODEL SIEVE IN?  Answer, from the pinned
        # source rather than assumption (heuristic H2/H3):
        #   estimator/lwe_primal.py:465  bkz_cost = costf(red_cost_model, beta, d)
        #   estimator/lwe_primal.py:488  svp_cost = costf(red_cost_model,
        #                                                svp_dim, svp_dim)
        #   estimator/lwe_primal.py:482  eta = svp_dim - 1  (non-homogeneous LWE)
        #   estimator/lwe_primal.py:490  svp_cost["rop"] += babai_cost(d - eta)
        # and estimator/reduction.py:800 (class Kyber, inherited by GJ21 ->
        # MATZOV) sieves not in the raw block size but in
        #   beta_ = beta - d4f(beta),
        # the dimensions-for-free-reduced dimension.  So the model performs
        # sieves in TWO dimensions: beta - d4f(beta) inside progressive BKZ,
        # and (eta+1) - d4f(eta+1) for the single final SVP/BDD call.
        bkz_only = float(RC.MATZOV(beta, d))
        svp_only = (float(RC.MATZOV(eta + 1, eta + 1))
                    + float(PrimalHybrid.babai_cost(d - eta)["rop"]))
        decomposition_exact = (red + svp == rop) and \
                              (abs(math.log2(bkz_only) - log2_red) < 1e-9) and \
                              (abs(math.log2(svp_only) - log2_svp) < 1e-9)
        controls["CTRL-1_cost_decomposition"]["per_set"][name] = {
            "red_plus_svp_minus_rop": red + svp - rop,
            "log2_red": log2_red,
            "log2_red_recomputed_MATZOV_beta_d": math.log2(bkz_only),
            "log2_svp": log2_svp,
            "log2_svp_recomputed_MATZOV_etaplus1_plus_babai":
                math.log2(svp_only),
            "passed": bool(decomposition_exact),
        }

        ref = EV_MLKEM_015_REFERENCE_LOG2_ROP[name]
        controls["CTRL-2_baseline_matches_EV_MLKEM_015"]["per_set"][name] = {
            "this_run_log2_rop": log2_rop,
            "RUN_MLKEM_015_001_log2_rop": ref,
            "delta": abs(log2_rop - ref),
            "passed": bool(abs(log2_rop - ref) == 0.0),
        }

        d4f_beta = float(RC.MATZOV.d4f(beta))
        d4f_svp = float(RC.MATZOV.d4f(eta + 1))
        sieve_dim_bkz = beta - d4f_beta
        sieve_dim_svp = (eta + 1) - d4f_svp

        log2_q = math.log2(float(p.q))
        bits_per_coeff = math.ceil(log2_q)

        mem_bkz = sieve_memory(sieve_dim_bkz, log2_q, bits_per_coeff)
        mem_svp = sieve_memory(sieve_dim_svp, log2_q, bits_per_coeff)
        peak_is = "svp" if (mem_svp["log2_memory_zq_elements"]
                            >= mem_bkz["log2_memory_zq_elements"]) else "bkz"
        mem_peak = mem_svp if peak_is == "svp" else mem_bkz

        print(f"  beta = {beta}   eta = {eta}   d = {d}")
        print(f"  log2(rop) = {log2_rop:.10f}  "
              f"(red {log2_red:.6f} + svp {log2_svp:.6f})")
        print(f"  NIST classical cutoff = {cutoff:.0f}   "
              f"free-memory margin (cutoff - log2 rop) = {m0:+.6f} bits "
              f"({'UNDERCUT' if m0 > 0 else 'no undercut'})")
        print(f"  BKZ sieve dim  = beta   - d4f(beta)   = {beta} - "
              f"{d4f_beta:.6f} = {sieve_dim_bkz:.6f}")
        print(f"  SVP sieve dim  = (eta+1)- d4f(eta+1)  = {eta + 1} - "
              f"{d4f_svp:.6f} = {sieve_dim_svp:.6f}")
        print(f"  peak sieve is the {peak_is.upper()} call "
              f"(eta+1 > beta, so the final BDD/SVP call dominates memory)")
        print(f"  log2 M  [vectors]     bkz {mem_bkz['log2_memory_vectors']:10.6f}"
              f"   svp {mem_svp['log2_memory_vectors']:10.6f}")
        print(f"  log2 M  [Z_q elements] bkz "
              f"{mem_bkz['log2_memory_zq_elements']:10.6f}"
              f"   svp {mem_svp['log2_memory_zq_elements']:10.6f}")
        print(f"  log2 M  [bits, {bits_per_coeff}/coeff] bkz "
              f"{mem_bkz['log2_memory_bits_packed']:10.6f}"
              f"   svp {mem_svp['log2_memory_bits_packed']:10.6f}")
        print(f"  unit conversion: {mem_svp['conversion']}")

        # ------------------------------------------------- charged cost family
        units = {
            "vectors": mem_peak["log2_memory_vectors"],
            "zq_elements": mem_peak["log2_memory_zq_elements"],
            "bits_packed": mem_peak["log2_memory_bits_packed"],
            "bits_information_theoretic":
                mem_peak["log2_memory_bits_information_theoretic"],
        }
        units_bkz = {
            "vectors": mem_bkz["log2_memory_vectors"],
            "zq_elements": mem_bkz["log2_memory_zq_elements"],
            "bits_packed": mem_bkz["log2_memory_bits_packed"],
            "bits_information_theoretic":
                mem_bkz["log2_memory_bits_information_theoretic"],
        }

        charged = {}
        for unit, log2M in units.items():
            rows = []
            for label, c in NAMED_CHARGES:
                lg = charged_log2_peak(log2_rop, log2M, c)
                rows.append({
                    "label": label,
                    "c": c,
                    "log2_charged_cost_modelA_peak": lg,
                    "margin_bits_modelA": cutoff - lg,
                    "log2_charged_cost_modelB_perterm":
                        charged_log2_perterm(log2_red, units_bkz[unit],
                                             log2_svp, log2M, c),
                    "margin_bits_modelB":
                        cutoff - charged_log2_perterm(log2_red, units_bkz[unit],
                                                      log2_svp, log2M, c),
                    "log2_implied_per_access_charge": c * log2M,
                })
            # closed form (Model A) and bisection (Model B)
            cstar_A = m0 / log2M
            cstar_A_bisect = bisect_cstar(
                lambda c: charged_log2_peak(log2_rop, log2M, c), cutoff)
            cstar_B = bisect_cstar(
                lambda c: charged_log2_perterm(log2_red, units_bkz[unit],
                                               log2_svp, log2M, c), cutoff)
            charged[unit] = {
                "log2_memory_peak": log2M,
                "log2_memory_bkz_sieve": units_bkz[unit],
                "named_charges": rows,
                "c_star_modelA_peak_closed_form": cstar_A,
                "c_star_modelA_peak_bisection": cstar_A_bisect,
                "c_star_modelB_per_term_bisection": cstar_B,
                "c_star_sensitivity_to_access_fraction": {
                    f"log2_f={lf:.0f}": (m0 - lf) / log2M
                    for lf in ACCESS_FRACTIONS_LOG2
                },
            }

        headline_unit = "zq_elements"
        log2M = units[headline_unit]
        cstar = m0 / log2M

        print(f"\n  --- charged cost family (unit: Z_q elements, "
              f"log2 M_peak = {log2M:.6f}) ---")
        print(f"  {'convention':26} {'c':>8} {'log2 cost A':>13} "
              f"{'margin A':>10} {'log2 cost B':>13} {'margin B':>10}")
        for row in charged[headline_unit]["named_charges"]:
            print(f"  {row['label']:26} {row['c']:8.4f} "
                  f"{row['log2_charged_cost_modelA_peak']:13.4f} "
                  f"{row['margin_bits_modelA']:+10.4f} "
                  f"{row['log2_charged_cost_modelB_perterm']:13.4f} "
                  f"{row['margin_bits_modelB']:+10.4f}")

        print(f"\n  c* (Model A, closed form m0/log2 M) = {cstar:.8f}")
        print(f"  c* across units: " + ", ".join(
            f"{u}={charged[u]['c_star_modelA_peak_closed_form']:.6f}"
            for u in ("vectors", "zq_elements", "bits_packed")))
        print(f"  c* (Model B, per-term, Z_q) = "
              f"{charged[headline_unit]['c_star_modelB_per_term_bisection']:.8f}")
        print(f"  PHYSICAL MEANING: charging M^c* multiplies the estimated cost "
              f"by exactly 2^{m0:.4f} = {2 ** m0:.3f}x.")
        print(f"    Equivalently: a per-memory-access surcharge of "
              f"{2 ** m0:.3f} gate-equivalents, applied to every gate in the "
              f"MATZOV count, erases the undercut.")
        print(f"    For comparison, a single access to {log2M:.1f} bits of "
              f"memory costs 2^{log2M / 3:.1f} under a 3D wiring bound and "
              f"2^{log2M / 2:.1f} under a 2D one.")

        # --------------------------------------------------- CTRL-4/5/6/7
        r_units = (charged["vectors"]["c_star_modelA_peak_closed_form"]
                   / charged["bits_packed"]["c_star_modelA_peak_closed_form"])
        r_mem = (units["bits_packed"] / units["vectors"])
        controls["CTRL-4_unit_consistency"]["per_set"][name] = {
            "cstar_vectors_over_cstar_bits": r_units,
            "log2M_bits_over_log2M_vectors": r_mem,
            "abs_difference": abs(r_units - r_mem),
            "passed": bool(abs(r_units - r_mem) < 1e-12),
        }

        null_rows = [{"c": c, "log2_charged_cost":
                      charged_log2_peak(log2_rop, 0.0, c),
                      "margin_bits": cutoff - charged_log2_peak(log2_rop, 0.0, c)}
                     for _, c in NAMED_CHARGES]
        null_moves = max(abs(row["margin_bits"] - m0) for row in null_rows)
        controls["CTRL-5_null_object_zero_memory"]["per_set"][name] = {
            "rows": null_rows,
            "max_margin_movement_bits": null_moves,
            "c_star": None,
            "passed": bool(null_moves == 0.0),
        }

        controls["CTRL-6_closed_form_vs_bisection"]["per_set"][name] = {
            "closed_form": cstar,
            "bisection": charged[headline_unit]["c_star_modelA_peak_bisection"],
            "abs_difference": abs(
                cstar - charged[headline_unit]["c_star_modelA_peak_bisection"]),
            "passed": bool(abs(
                cstar
                - charged[headline_unit]["c_star_modelA_peak_bisection"]) < 1e-9),
        }

        margins = [cutoff - charged_log2_peak(log2_rop, log2M, c) for c in SWEEP]
        mono = all(margins[i + 1] <= margins[i] + 1e-12
                   for i in range(len(margins) - 1))
        controls["CTRL-7_monotonicity"]["per_set"][name] = {
            "sweep_points": len(SWEEP),
            "margin_at_c0": margins[0],
            "margin_at_c1": margins[-1],
            "passed": bool(mono),
        }

        sweep_rows = [
            {"c": c,
             "log2_charged_cost_modelA": charged_log2_peak(log2_rop, log2M, c),
             "margin_bits_modelA": cutoff - charged_log2_peak(log2_rop, log2M, c)}
            for c in [0.0, 0.005, 0.0071, 0.01, 0.02, 0.0304, 0.0316, 0.035,
                      0.04, 0.0459, 0.05, 0.06, 0.08, 0.1, 1 / 6, 0.25,
                      1 / 3, 0.5, 1.0]
        ]

        per_set[name] = {
            "estimate_not_measurement": True,
            "attack": "primal_bdd",
            "cost_model": "RC.MATZOV (list_decoding-classical)",
            "beta": beta,
            "eta": eta,
            "d": d,
            "log2_rop_free_memory": log2_rop,
            "log2_rop_red_term": log2_red,
            "log2_rop_svp_term": log2_svp,
            "nist_classical_cutoff_bits": cutoff,
            "free_memory_margin_bits": m0,
            "free_memory_margin_direction":
                "attack BELOW cutoff (undercut)" if m0 > 0
                else "attack AT OR ABOVE cutoff",
            "d4f_beta": d4f_beta,
            "d4f_eta_plus_1": d4f_svp,
            "sieve_dimension_bkz": sieve_dim_bkz,
            "sieve_dimension_svp": sieve_dim_svp,
            "peak_sieve_call": peak_is,
            "q": int(p.q),
            "log2_q": log2_q,
            "bits_per_coefficient_packed": bits_per_coeff,
            "memory_bkz_sieve": mem_bkz,
            "memory_svp_sieve": mem_svp,
            "memory_peak": mem_peak,
            "charged": charged,
            "headline_unit": headline_unit,
            "c_star_headline_modelA_zq_elements": cstar,
            "c_star_headline_modelB_zq_elements":
                charged[headline_unit]["c_star_modelB_per_term_bisection"],
            "c_star_physical_meaning": {
                "multiplier_at_c_star": 2.0 ** m0,
                "log2_multiplier_at_c_star": m0,
                "statement": (
                    f"Charging M^c* multiplies the estimated attack cost by "
                    f"2^{m0:.4f} = {2 ** m0:.3f}x. Equivalently, if every gate "
                    f"in the MATZOV count is treated as one access to the "
                    f"2^{log2M:.1f}-element sieve database, a per-access cost of "
                    f"{2 ** m0:.3f} gate-equivalents suffices to erase the "
                    f"undercut. A 3D wiring bound charges 2^{log2M / 3:.1f} per "
                    f"access and a 2D one 2^{log2M / 2:.1f}."),
            },
            "sweep": sweep_rows,
        }

    out = {
        "schema": "crypto.autoresearch.memory_charged_derivation.v1",
        "task_id": "TASK-20260803-648a0b",
        "batch": "BATCH-010",
        "goal_id": "GOAL-MLKEM-003",
        "generated_utc": started_utc,
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status_note": (
            "ALL NUMBERS HERE ARE COST-MODEL ESTIMATES, NOT MEASUREMENTS. "
            "No ML-KEM break is claimed. A charge that raises the estimated "
            "cost above a NIST cutoff is not a proof of security: it is a "
            "statement about one cost model, at one parameter set, under the "
            "numbered heuristics in heuristics.yaml. Scope is primal_bdd under "
            "RC.MATZOV only -- Arora-Groebner is unavailable in this harness, "
            "so no 'best attack overall' phrasing applies."),
        "instrument": {
            "lattice_estimator_commit": est_commit,
            "pinned_commit_expected": PINNED_ESTIMATOR_COMMIT,
            "harness": "tools/sage_free_estimator (Sage-free shim)",
            "arora_gb_available": False,
        },
        "known_answer_control": control,
        "definitions": {
            "free_memory_margin_bits":
                "NIST classical cutoff (bits) minus log2(rop). POSITIVE means "
                "the estimated attack is CHEAPER than the cutoff (an undercut).",
            "charge_model_A_peak":
                "log2 cost = log2(rop) + c * log2(M_peak); M_peak is the larger "
                "of the two sieve databases the cost model runs.",
            "charge_model_B_per_term":
                "cost = red * M_bkz^c + svp * M_svp^c; each cost term is charged "
                "by the memory of the sieve that produces it.",
            "c_star":
                "the smallest c for which the charged cost reaches the NIST "
                "cutoff, i.e. the smallest memory charge that ERASES the "
                "undercut. Model A closed form: c* = margin / log2(M_peak).",
        },
        "charge_conventions": {
            "c=0": {
                "name": "free memory",
                "source": "The convention of the NIST category cutoffs and of "
                          "the published MATZOV / Kyber / lattice-estimator gate "
                          "counts: a pure gate count with no memory term. This "
                          "is the convention EV-MLKEM-015 reports in.",
                "sourced": True,
            },
            "c=1/6": {
                "name": "intermediate probe point",
                "source": "THIS BATCH'S OWN CONSTRUCTION. No source; included "
                          "only to make the family's shape visible between c* "
                          "and the 3D convention.",
                "sourced": False,
            },
            "c=1/3": {
                "name": "three-dimensional wiring / Wiener full cost",
                "source": "KN-LIT-094 (Wiener, 'The Full Cost of Cryptanalytic "
                          "Attacks', J. Cryptology 17(2):105-124, 2004; corpus "
                          "entry citation_verified: read) and its technique "
                          "abstract KN-TECH-035. Wiener resolves the cost of "
                          "wiring many processors to a large memory in three "
                          "dimensions and obtains BSGS full cost n^(2/3+o(1)) "
                          "from n^(1/2+o(1)) processor steps -- which is exactly "
                          "T * M^(1/3) at M = T = n^(1/2). KN-OPEN-016's sibling "
                          "KN-OPEN-017 poses this same charge for sieving.",
                "sourced": True,
            },
            "c=1/2": {
                "name": "two-dimensional layout / sqrt memory access",
                "source": "THIS BATCH'S OWN CONSTRUCTION, by specialising the "
                          "KN-LIT-094 wiring argument to a planar layout: M cells "
                          "in a plane have diameter ~M^(1/2), so one access costs "
                          "~M^(1/2). No primary source for the 2D case was "
                          "located in this repository's corpus or retrieved "
                          "during this batch. Recorded as unsourced (H7).",
                "sourced": False,
            },
            "c=1": {
                "name": "hardware quantity x time occupied",
                "source": "The literal definition of full cost in KN-LIT-094 / "
                          "KN-TECH-035 ('the quantity of hardware multiplied by "
                          "the time it is occupied'), instantiated with hardware "
                          "quantity ~ memory. Included as the family's upper end. "
                          "Wiener does not claim this is the right charge for "
                          "every algorithm; the n^(2/3) BSGS result comes from "
                          "the optimised M^(1/3) access charge, not from T*M.",
                "sourced": "partial",
            },
        },
        "per_parameter_set": per_set,
        "controls": controls,
        "heuristics_file": "heuristics.yaml",
    }

    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=False)
        fh.write("\n")

    print("\n" + "=" * 78)
    print("CONTROL SUMMARY")
    print("=" * 78)
    all_pass = True
    for key, blk in controls.items():
        if "passed" in blk:
            ok = blk["passed"]
            print(f"  {key:44} {'PASS' if ok else 'FAIL'}")
            all_pass &= bool(ok)
        else:
            ok = all(v["passed"] for v in blk["per_set"].values())
            print(f"  {key:44} {'PASS' if ok else 'FAIL'}")
            all_pass &= bool(ok)
    print(f"\n  ALL CONTROLS: {'PASS' if all_pass else 'FAIL'}")

    print("\n" + "=" * 78)
    print("HEADLINE (cost-model ESTIMATES, unit: Z_q elements, Model A)")
    print("=" * 78)
    print(f"  {'set':11} {'log2 rop':>11} {'cutoff':>7} {'margin':>9} "
          f"{'log2 M':>9} {'c*':>10} {'x at c*':>9}")
    for name, blk in per_set.items():
        print(f"  {name:11} {blk['log2_rop_free_memory']:11.4f} "
              f"{blk['nist_classical_cutoff_bits']:7.0f} "
              f"{blk['free_memory_margin_bits']:+9.4f} "
              f"{blk['memory_peak']['log2_memory_zq_elements']:9.4f} "
              f"{blk['c_star_headline_modelA_zq_elements']:10.6f} "
              f"{blk['c_star_physical_meaning']['multiplier_at_c_star']:9.3f}")

    print(f"\n  Wrote {args.out}")
    print("  Reminder: estimates, not measurements. No break claimed; a raised "
          "estimate is not a security proof.")
    return 0 if all_pass else 3


if __name__ == "__main__":
    raise SystemExit(main())
