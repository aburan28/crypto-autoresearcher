#!/usr/bin/env python3
"""
TASK-20260803-fb52f4 / GOAL-MLKEM-003 / BATCH-011
Account for the published-vs-estimator dual-attack cost gap at FIPS 203 parameters.

WHAT THIS SCRIPT IS
-------------------
EV-MLKEM-015 recorded that the published dual-attack costs of Carrier et al.
(139.5 / 195.1 / 259.7) and MATZOV-2022 (137.5 / 193.5 / 257.8) sit 4.29 / 8.69 /
14.12 and 6.29 / 10.29 / 16.02 bits BELOW what the pinned lattice-estimator's
`estimator.lwe_dual.dual_hybrid(..., fft=True)` reports under RC.MATZOV
(143.79 / 203.79 / 273.82), and that the gap GROWS with parameter size.

This script decomposes that gap into NAMED, INDIVIDUALLY SIZED modelling
differences, all evaluated inside the SAME pinned instrument
(lattice-estimator 3e48ef421ec256afddb3e7d2249a77eab6e9ba12, driven Sage-free
through tools/sage_free_estimator).

NOTHING HERE IS MEASURED. Every number is a COST-MODEL ESTIMATE produced by a
pinned estimator plus numbered modelling choices (heuristics.yaml). No ML-KEM
break is claimed and no security proof is claimed: a decomposition explains a
discrepancy between two cost estimates and by itself establishes neither.

THE INSTRUMENT MUST VALIDATE BEFORE IT IS USED. CTRL-1 runs
tools/sage_free_estimator/known_answer_control.py as a SUBPROCESS and this
script aborts non-zero if that control does not exit 0.

RUN
    git clone --depth 1 https://github.com/malb/lattice-estimator /tmp/le2
    git -C /tmp/le2 rev-parse HEAD   # 3e48ef421ec256afddb3e7d2249a77eab6e9ba12
    PYTHONPATH=<repo>/tools/sage_free_estimator/shim:/tmp/le2 \
        python3 dual_gap_decomposition.py --out results.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

import mpmath as mp

REPO = "/home/user/crypto-autoresearcher"
PINNED_COMMIT = "3e48ef421ec256afddb3e7d2249a77eab6e9ba12"
CONTROL = f"{REPO}/tools/sage_free_estimator/known_answer_control.py"
SHIM = f"{REPO}/tools/sage_free_estimator/shim"

# ---------------------------------------------------------------------------
# PUBLISHED FIGURES -- every one sourced to an archived byte, or marked unsourced
# ---------------------------------------------------------------------------
ARCHIVE = f"{REPO}/inputs/MLKEM-DUAL-SOURCES-20260802"

PUBLISHED = {
    "Carrier-CRYPTO2025": {
        "log2_cost": {"Kyber512": 139.5, "Kyber768": 195.1, "Kyber1024": 259.7},
        "sourced": True,
        "source_file": f"{ARCHIVE}/carrier_hal_front_matter.txt",
        "source_quote": (
            "the security levels for Kyber-512/768/1024 are 3.5/11.9/12.3 bits below "
            "the NIST requirements (143/207/272 bits) in the same nearest-neighbor "
            "cost model as in [SAB+20,MAT22]"
        ),
        "derivation_from_quote": "143-3.5=139.5, 207-11.9=195.1, 272-12.3=259.7",
        "units_declared_by_source": (
            "gate count in the AGPS20-style nearest-neighbour cost model of "
            "[SAB+20, MAT22]; NOT core-SVP"
        ),
    },
    "MATZOV-2022": {
        "log2_cost": {"Kyber512": 137.5, "Kyber768": 193.5, "Kyber1024": 257.8},
        "sourced": True,
        "source_file": f"{ARCHIVE}/matzov_v2_loci.txt",
        "source_quote": (
            "Table 1: ... All of the costs are log2 in the gate-count metric. "
            "Kyber512 143 ... 137.5 / Kyber768 207 ... 193.5 / Kyber1024 272 ... 257.8"
        ),
        "derivation_from_quote": "read directly from the archived Table 1 column 'This Work'",
        "units_declared_by_source": "log2 gate count",
    },
}

# NIST classical cutoffs. Sourced here to the SAME archived MATZOV Table 1 byte
# ("Required Security Level By NIST [Nat16]" column: 143 / 207 / 272) and to the
# Carrier abstract quote above. NOT verified against primary NIST/FIPS text --
# EV-MLKEM-015 and EV-MLKEM-020 (H11) both record that no NIST call text is
# readable under this program's network policy. Carried as an inherited boundary.
NIST_CUTOFF = {"Kyber512": 143, "Kyber768": 207, "Kyber1024": 272}
NIST_CUTOFF_PROVENANCE = (
    "secondary: the 'Required Security Level By NIST [Nat16]' column of MATZOV "
    "Table 1 as archived in inputs/MLKEM-DUAL-SOURCES-20260802/matzov_v2_loci.txt, "
    "and the Carrier abstract '(143/207/272 bits)'. Primary NIST text UNREAD "
    "(EV-MLKEM-020 H11: UNVERIFIABLE in this environment)."
)

# Carrier Table C.1 / C.2, transcribed from the archived extract
# inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/page37_tables_C1_C2.txt
# Column order as printed there:
#   m  beta_bkz  beta_sieve  n_enu  n_fft  k_fft  n_lat  d_lat  mu_lsc  sigma_lsc  log2N  log2T
CARRIER_C1 = {
    "C0": {
        "Kyber512": dict(m=488, beta_bkz=393, beta_sieve=393, n_enu=1, n_fft=38,
                         k_fft=8, n_lat=473, log2N=81.55),
        "Kyber768": dict(m=667, beta_bkz=588, beta_sieve=588, n_enu=6, n_fft=69,
                         k_fft=12, n_lat=693, log2N=122.02),
        "Kyber1024": dict(m=920, beta_bkz=815, beta_sieve=815, n_enu=9, n_fft=100,
                          k_fft=17, n_lat=915, log2N=169.13),
    },
    "CC": {
        "Kyber512": dict(m=475, beta_bkz=384, beta_sieve=387, n_enu=5, n_fft=52,
                         k_fft=9, n_lat=455, log2N=80.31),
        "Kyber768": dict(m=636, beta_bkz=581, beta_sieve=574, n_enu=6, n_fft=93,
                         k_fft=14, n_lat=669, log2N=119.12),
        "Kyber1024": dict(m=802, beta_bkz=811, beta_sieve=792, n_enu=10, n_fft=131,
                          k_fft=19, n_lat=883, log2N=164.35),
    },
    "CN": {
        "Kyber512": dict(m=457, beta_bkz=384, beta_sieve=388, n_enu=4, n_fft=48,
                         k_fft=9, n_lat=460, log2N=80.51),
        "Kyber768": dict(m=682, beta_bkz=583, beta_sieve=577, n_enu=8, n_fft=86,
                         k_fft=13, n_lat=674, log2N=119.74),
        "Kyber1024": dict(m=782, beta_bkz=816, beta_sieve=797, n_enu=6, n_fft=132,
                          k_fft=19, n_lat=886, log2N=165.39),
    },
}
CARRIER_C2 = {  # log2(Pwrong), log2(R), log2(Tsample), log2(N*Tdec), log2(TFFT)
    "CC": {
        "Kyber512": dict(log2_Pwrong=-119.57, log2_R=9.39, log2_Tsample=139.51,
                         log2_NTdec=117.71, log2_TFFT=124.00),
        "Kyber768": dict(log2_Pwrong=-177.79, log2_R=9.49, log2_Tsample=194.81,
                         log2_NTdec=157.74, log2_TFFT=183.15),
        "Kyber1024": dict(log2_Pwrong=-244.03, log2_R=15.15, log2_Tsample=259.35,
                          log2_NTdec=204.17, log2_TFFT=242.09),
    },
}
N_OF_SET = {"Kyber512": 512, "Kyber768": 768, "Kyber1024": 1024}

# The EV-MLKEM-015 comparison object, restated so a drift is caught, not absorbed.
EV015_DUAL_HYBRID_FFT = {
    "Kyber512": 143.79, "Kyber768": 203.79, "Kyber1024": 273.82,
}


def log2f(x):
    return math.log2(float(x))


def _cost_dict(c):
    out = {}
    for k, v in c.items():
        if k == "problem":
            continue
        try:
            out[k] = float(v)
        except (TypeError, ValueError):
            out[k] = str(v)
    return out


# ---------------------------------------------------------------------------
# CTRL-1: the known-answer control, as a subprocess, BEFORE anything else.
# ---------------------------------------------------------------------------
def ctrl1_known_answer_control(env_pythonpath):
    env = dict(os.environ)
    env["PYTHONPATH"] = env_pythonpath
    cmd = [sys.executable, CONTROL]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=900)
    return {
        "control_id": "CTRL-1",
        "command": " ".join(cmd),
        "pythonpath": env_pythonpath,
        "exit_code": proc.returncode,
        "stdout_verbatim": proc.stdout,
        "stderr_verbatim": proc.stderr,
        "wall_seconds": round(time.time() - t0, 3),
        "passes": proc.returncode == 0,
    }


# ---------------------------------------------------------------------------
# The in-process patch that makes estimator.lwe_dual.matzov executable here.
#
# WHY: estimator/lwe_dual.py:607 calls Sage's RealNumber.n(30) on the result of
# exp(). tools/sage_free_estimator's shim returns a bare mpmath mpf, which has no
# .n(), so `matzov` dies with AttributeError -- exactly the same class of harness
# gap that BATCH-010 defect D4 found for `dual`/`primal_hybrid`.
#
# SCOPE OF THE PATCH: it rebinds ONE name, estimator.lwe_dual.exp, inside THIS
# process. It writes nothing, and tools/sage_free_estimator is not modified.
# Its correctness is not assumed: CTRL-2 re-runs the controlled paths under the
# patch, CTRL-3 checks the patched matzov against the estimator's OWN
# Sage-computed doctest values committed at the pin, and CTRL-4 varies the
# patch's rounding convention to show the result does not rest on it.
# ---------------------------------------------------------------------------
_ORIG_LWE_DUAL_EXP = None


def install_n_patch(mode):
    global _ORIG_LWE_DUAL_EXP
    import estimator.lwe_dual as ld
    if _ORIG_LWE_DUAL_EXP is None:
        _ORIG_LWE_DUAL_EXP = ld.exp
    orig_exp = _ORIG_LWE_DUAL_EXP

    class _FaithfulReal(mp.mpf):
        """Sage RR(x).n(prec): round to `prec` bits, as Sage does."""
        def n(self, prec=53, digits=None, algorithm=None):
            if digits is not None:
                prec = int(digits * 3.3219280948873626) + 1
            with mp.workprec(int(prec)):
                return +mp.mpf(self)

    class _FullPrecReal(mp.mpf):
        """Null variant: .n() returns the unrounded value (200-bit shim prec)."""
        def n(self, prec=53, digits=None, algorithm=None):
            return mp.mpf(self)

    cls = _FaithfulReal if mode == "faithful" else _FullPrecReal
    ld.exp = lambda x: cls(orig_exp(x))
    return ld


# ---------------------------------------------------------------------------
# Refinement of the estimator's own MATZOV Theorem-7.6 cost function.
#
# The estimator's `matzov.__call__` searches k_enum and k_fft on a STEP-10 grid
# (estimator/lwe_dual.py:657-658, early_abort_range(..., 10)) and fixes the
# sample count m to params.n (lwe_dual.py:583-584). Both are optimiser choices,
# not cost-model content: relaxing them evaluates the SAME Theorem 7.6 formula
# on a larger feasible set, so it can only lower the reported cost. Each stage is
# reported as its own named, individually sized modelling difference.
# ---------------------------------------------------------------------------
def refine_grid(MZ, RC_model, params, base, box, budget_s, log):
    """Stage 2: local box refinement over (p, k_enum, k_fft, beta) at m = n."""
    t0 = time.time()
    best = dict(base)
    calls = 0
    p0, ke0, kf0, b0 = base["p"], base["k_enum"], base["k_fft"], base["beta"]
    for p in box["p"]:
        for ke in range(max(0, ke0 - box["ke"]), ke0 + box["ke"] + 1):
            for kf in range(max(0, kf0 - box["kf"]), kf0 + box["kf"] + 1):
                if ke + kf >= params.n:
                    continue
                for b in range(max(40, b0 - box["beta"]), b0 + box["beta"] + 1):
                    try:
                        c = MZ.cost(b, params, p=p, k_enum=ke, k_fft=kf,
                                    red_cost_model=RC_model)
                    except Exception:
                        continue
                    calls += 1
                    v = log2f(c["rop"])
                    if v < best["log2_rop"]:
                        best = dict(log2_rop=v, p=p, k_enum=ke, k_fft=kf, beta=b,
                                    m=int(params.n), beta_sieve=None,
                                    cost=_cost_dict(c))
                if time.time() - t0 > budget_s:
                    log(f"    [refine_grid] wall budget {budget_s}s hit after "
                        f"{calls} calls; returning best found so far")
                    best["budget_truncated"] = True
                    return best, calls, time.time() - t0
    return best, calls, time.time() - t0


def refine_m(MZ, RC_model, params, base, budget_s, log):
    """Stage 3: sweep the sample count m, which the estimator fixes at n."""
    t0 = time.time()
    best = dict(base)
    calls = 0
    n = int(params.n)
    for m in range(int(0.60 * n), n + 1, 2):
        for kf in range(max(1, base["k_fft"] - 6), base["k_fft"] + 7):
            for b in range(max(40, base["beta"] - 8), base["beta"] + 9):
                try:
                    c = MZ.cost(b, params, m=m, p=base["p"], k_enum=base["k_enum"],
                                k_fft=kf, red_cost_model=RC_model)
                except Exception:
                    continue
                calls += 1
                v = log2f(c["rop"])
                if v < best["log2_rop"]:
                    best = dict(log2_rop=v, p=base["p"], k_enum=base["k_enum"],
                                k_fft=kf, beta=b, m=m, beta_sieve=None,
                                cost=_cost_dict(c))
        if time.time() - t0 > budget_s:
            log(f"    [refine_m] wall budget {budget_s}s hit after {calls} calls")
            best["budget_truncated"] = True
            return best, calls, time.time() - t0
    return best, calls, time.time() - t0


def refine_beta_sieve(MZ, RC_model, params, base, budget_s, log):
    """Stage 4: sweep the explicit second block size beta_sieve.

    NOTE, recorded as an unexpected observation: passing beta_sieve explicitly is
    NOT a pure relaxation. estimator/lwe_dual.py:589-597 feeds
    `beta_sieve if beta_sieve else beta` into Nf, so the AUTOMATIC path evaluates
    the sample-count formula at beta_sieve = beta (the estimator's own comment
    reads '# We assume here that beta_sieve ~ beta') while charging the reduction
    at the balanced sieve dimension GJ21.short_vectors picks. An explicit
    beta_sieve changes BOTH. The sweep is reported for what it is.
    """
    t0 = time.time()
    best = dict(base)
    best["beta_sieve_explicit_best"] = None
    calls = 0
    auto = int(base["cost"].get("beta_", base["beta"]))
    for bs in range(max(40, auto - 60), auto + 61, 2):
        for b in range(max(40, base["beta"] - 10), base["beta"] + 11):
            try:
                c = MZ.cost(b, params, m=base["m"], p=base["p"],
                            k_enum=base["k_enum"], k_fft=base["k_fft"],
                            beta_sieve=bs, red_cost_model=RC_model)
            except Exception:
                continue
            calls += 1
            v = log2f(c["rop"])
            if v < best["log2_rop"]:
                best = dict(log2_rop=v, p=base["p"], k_enum=base["k_enum"],
                            k_fft=base["k_fft"], beta=b, m=base["m"],
                            beta_sieve=bs, cost=_cost_dict(c),
                            beta_sieve_explicit_best=bs)
        if time.time() - t0 > budget_s:
            log(f"    [refine_beta_sieve] wall budget {budget_s}s hit after {calls} calls")
            best["budget_truncated"] = True
            return best, calls, time.time() - t0
    return best, calls, time.time() - t0


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results.json")
    ap.add_argument("--wall-budget", type=float, default=2200.0)
    args = ap.parse_args()

    started = datetime.now(timezone.utc).isoformat()
    T0 = time.time()
    lines = []

    def log(s):
        print(s, flush=True)
        lines.append(s)

    R = {
        "schema": "crypto.autoresearch.dual_gap_decomposition.v1",
        "task_id": "TASK-20260803-fb52f4",
        "goal_id": "GOAL-MLKEM-003",
        "batch_id": "BATCH-011",
        "started_utc": started,
        "estimator_pin": PINNED_COMMIT,
        "what_these_numbers_are": (
            "COST-MODEL ESTIMATES from a pinned lattice-estimator plus numbered "
            "modelling choices. NOTHING WAS MEASURED. No ML-KEM break is claimed "
            "and no security proof is claimed."
        ),
        "attacks_unavailable_in_this_harness": [
            "arora_gb (PowerSeriesRing stub raises)",
            "dual (fails)",
            "primal_hybrid (fails)",
            "any 'best attack' phrasing is scoped to the attacks actually served",
        ],
        "controls": {},
        "published": PUBLISHED,
        "nist_cutoff": NIST_CUTOFF,
        "nist_cutoff_provenance": NIST_CUTOFF_PROVENANCE,
        "carrier_table_C1": CARRIER_C1,
        "carrier_table_C2": CARRIER_C2,
        "per_set": {},
        "anomalies": [],
    }

    pythonpath = f"{SHIM}:{os.environ.get('LE_DIR', '/tmp/le2')}"

    # ---------------- CTRL-1 ------------------------------------------------
    log("=" * 78)
    log("CTRL-1  known-answer control (subprocess), verbatim")
    log("=" * 78)
    c1 = ctrl1_known_answer_control(pythonpath)
    R["controls"]["CTRL-1_known_answer_control"] = c1
    log(c1["stdout_verbatim"].rstrip("\n"))
    if c1["stderr_verbatim"].strip():
        log("[stderr] " + c1["stderr_verbatim"].rstrip("\n"))
    log(f"exit_code = {c1['exit_code']}")
    if not c1["passes"]:
        log("INSTRUMENT FAILURE: the known-answer control did not exit 0. STOPPING.")
        R["terminal_state"] = "infrastructure_error"
        with open(args.out, "w") as fh:
            json.dump(R, fh, indent=2, sort_keys=True)
        return 2

    # ---------------- imports + patch --------------------------------------
    from estimator import RC, schemes
    from estimator.lwe_primal import primal_bdd
    from estimator.lwe_dual import dual_hybrid
    from estimator.reduction import MATZOV as RC_MATZOV_CLASS

    ld = install_n_patch("faithful")
    MZ = ld.MATZOV

    SETS = {"Kyber512": schemes.Kyber512, "Kyber768": schemes.Kyber768,
            "Kyber1024": schemes.Kyber1024}
    NORM = {k: v.normalize() for k, v in SETS.items()}

    # ---------------- CTRL-2: patch is inert on the controlled paths --------
    log("")
    log("=" * 78)
    log("CTRL-2  the .n() patch is inert on every path CTRL-1 covers")
    log("=" * 78)
    REF = {"Kyber512": 140.1994731076207, "Kyber768": 200.9587149140538}
    DREF = {"Kyber512": 143.78847824788485, "Kyber768": 203.78786306762115}
    ctrl2 = {"primal_bdd": {}, "dual_hybrid_fft": {}, "passes": True}
    for name, p in SETS.items():
        v = log2f(primal_bdd(p, red_cost_model=RC.MATZOV)["rop"])
        d = abs(v - REF[name]) if name in REF else None
        ctrl2["primal_bdd"][name] = {"log2_rop": v, "reference": REF.get(name), "delta": d}
        log(f"  primal_bdd  {name:10} {v:.10f}  delta={'%.3e' % d if d is not None else '(no ref)'}")
        if d is not None and d != 0.0:
            ctrl2["passes"] = False
    dual_hybrid_cost = {}
    for name, p in SETS.items():
        c = dual_hybrid(p, red_cost_model=RC.MATZOV, fft=True)
        v = log2f(c["rop"])
        dual_hybrid_cost[name] = {"log2_rop": v, "cost": _cost_dict(c)}
        d = abs(v - DREF[name]) if name in DREF else None
        ctrl2["dual_hybrid_fft"][name] = {"log2_rop": v, "reference": DREF.get(name), "delta": d}
        log(f"  dual_hybrid {name:10} {v:.10f}  delta={'%.3e' % d if d is not None else '(no ref)'}"
            f"  beta={c['beta']} d={c['d']} zeta={c['zeta']} t={c['t']} reps={c['repetitions']}")
        if d is not None and d > 1e-9:
            ctrl2["passes"] = False
        # drift check against the EV-MLKEM-015 comparison object
        if abs(v - EV015_DUAL_HYBRID_FFT[name]) > 0.01:
            R["anomalies"].append(
                f"dual_hybrid(fft=True) at {name} is {v:.6f}, which differs from the "
                f"EV-MLKEM-015 value {EV015_DUAL_HYBRID_FFT[name]} by more than 0.01 bits")
    R["controls"]["CTRL-2_patch_inert_on_controlled_paths"] = ctrl2
    log(f"  CTRL-2 passes = {ctrl2['passes']}")

    # ---------------- CTRL-3: the estimator's OWN Sage doctest for matzov ---
    # estimator/lwe.py at the pin carries Sage-computed doctest output for
    # LWE.estimate(schemes.Kyber512) and LWE.estimate.rough(schemes.Kyber512).
    # `LWE.dual_hybrid` IS `lwe_dual.matzov` (estimator/lwe.py:13), so these are
    # a Sage-computed reference for the very path the harness control does not
    # cover -- authored by the estimator maintainers, committed before this task.
    log("")
    log("=" * 78)
    log("CTRL-3  patched matzov vs the estimator's own committed Sage doctest")
    log("=" * 78)
    ctrl3 = {"cases": [], "passes": True,
             "why": ("estimator/lwe.py:13 aliases LWE.dual_hybrid to lwe_dual.matzov; "
                     "its docstrings at lines ~55 and ~124 carry Sage-computed output "
                     "for Kyber512 at the pinned commit.")}
    doctest_cases = [
        # (label, red_cost_model, expected rop/red/guess to 1 dp, beta, p, zeta, t, beta')
        ("lwe.py:124  LWE.estimate(Kyber512)      RC.MATZOV", RC.MATZOV,
         139.7, 139.5, 135.9, 387, 5, 0, 50, 391),
        ("lwe.py:55   LWE.estimate.rough(Kyber512) RC.ADPS16", RC.ADPS16,
         115.5, 115.3, 112.3, 395, 5, 0, 40, 395),
    ]
    for (label, rc, e_rop, e_red, e_guess, e_beta, e_p, e_zeta, e_t, e_bs) in doctest_cases:
        c = ld.matzov(SETS["Kyber512"], red_cost_model=rc)
        got = dict(rop=log2f(c["rop"]), red=log2f(c["red"]), guess=log2f(c["guess"]),
                   beta=int(c["beta"]), p=int(c["p"]), zeta=int(c["zeta"]),
                   t=int(c["t"]), beta_=int(c["beta_"]))
        ok = (round(got["rop"], 1) == e_rop and round(got["red"], 1) == e_red
              and round(got["guess"], 1) == e_guess and got["beta"] == e_beta
              and got["p"] == e_p and got["zeta"] == e_zeta and got["t"] == e_t
              and got["beta_"] == e_bs)
        ctrl3["cases"].append({"label": label, "got": got,
                               "expected": dict(rop=e_rop, red=e_red, guess=e_guess,
                                                beta=e_beta, p=e_p, zeta=e_zeta,
                                                t=e_t, beta_=e_bs),
                               "match": ok})
        log(f"  {label}")
        log(f"    got      rop={got['rop']:.4f} red={got['red']:.4f} guess={got['guess']:.4f} "
            f"beta={got['beta']} p={got['p']} zeta={got['zeta']} t={got['t']} beta'={got['beta_']}")
        log(f"    doctest  rop={e_rop} red={e_red} guess={e_guess} "
            f"beta={e_beta} p={e_p} zeta={e_zeta} t={e_t} beta'={e_bs}   MATCH={ok}")
        if not ok:
            ctrl3["passes"] = False
    R["controls"]["CTRL-3_estimator_own_sage_doctest_for_matzov"] = ctrl3
    log(f"  CTRL-3 passes = {ctrl3['passes']}")

    # ---------------- CTRL-4: the patch's rounding convention is not load-bearing
    log("")
    log("=" * 78)
    log("CTRL-4  null on the patch: 30-bit rounding vs full precision")
    log("=" * 78)
    matzov_base = {}
    for name, p in SETS.items():
        c = ld.matzov(p, red_cost_model=RC.MATZOV)
        matzov_base[name] = {"log2_rop": log2f(c["rop"]), "cost": _cost_dict(c)}
    install_n_patch("fullprec")
    ctrl4 = {"cases": {}, "passes": True}
    for name, p in SETS.items():
        c = ld.matzov(p, red_cost_model=RC.MATZOV)
        v = log2f(c["rop"])
        d = abs(v - matzov_base[name]["log2_rop"])
        ctrl4["cases"][name] = {"faithful": matzov_base[name]["log2_rop"],
                                "fullprec": v, "delta": d}
        log(f"  matzov {name:10} faithful={matzov_base[name]['log2_rop']:.10f} "
            f"fullprec={v:.10f} delta={d:.3e}")
        if d > 1e-6:
            ctrl4["passes"] = False
    install_n_patch("faithful")   # restore
    R["controls"]["CTRL-4_patch_rounding_null"] = ctrl4
    log(f"  CTRL-4 passes (patch convention worth < 1e-6 bits) = {ctrl4['passes']}")

    # ---------------- CTRL-5: Carrier Table C.1 internal arithmetic ---------
    log("")
    log("=" * 78)
    log("CTRL-5  archived Carrier Table C.1 arithmetic: n_enu + n_fft + n_lat == n")
    log("=" * 78)
    ctrl5 = {"rows": [], "passes": True}
    for variant, rows in CARRIER_C1.items():
        for name, r in rows.items():
            s = r["n_enu"] + r["n_fft"] + r["n_lat"]
            ok = (s == N_OF_SET[name])
            ctrl5["rows"].append({"variant": variant, "set": name, "sum": s,
                                  "n": N_OF_SET[name], "match": ok})
            if not ok:
                ctrl5["passes"] = False
    log(f"  {len(ctrl5['rows'])} rows checked; all identities hold = {ctrl5['passes']}")
    R["controls"]["CTRL-5_carrier_table_arithmetic"] = ctrl5

    # ---------------- CTRL-6: sign null -------------------------------------
    # A gap arithmetic that cannot produce a negative number is not measuring
    # anything. Score Kyber1024's estimator cost against Kyber768's published
    # figure and against its own cutoff; the sign must flip where it should.
    log("")
    log("=" * 78)
    log("CTRL-6  sign null (a discriminating control, not an identity)")
    log("=" * 78)
    ctrl6 = {
        "kyber1024_estimator_minus_kyber768_published_carrier":
            matzov_base["Kyber1024"]["log2_rop"] - PUBLISHED["Carrier-CRYPTO2025"]["log2_cost"]["Kyber768"],
        "kyber512_estimator_minus_kyber1024_published_carrier":
            matzov_base["Kyber512"]["log2_rop"] - PUBLISHED["Carrier-CRYPTO2025"]["log2_cost"]["Kyber1024"],
    }
    ctrl6["passes"] = (ctrl6["kyber1024_estimator_minus_kyber768_published_carrier"] > 0
                       and ctrl6["kyber512_estimator_minus_kyber1024_published_carrier"] < 0)
    for k, v in ctrl6.items():
        if k != "passes":
            log(f"  {k} = {v:+.4f}")
    log(f"  CTRL-6 passes (mis-paired comparisons produce both signs) = {ctrl6['passes']}")
    R["controls"]["CTRL-6_sign_null"] = ctrl6

    # =======================================================================
    # THE DECOMPOSITION
    # =======================================================================
    log("")
    log("=" * 78)
    log("DECOMPOSITION")
    log("=" * 78)

    remaining = args.wall_budget - (time.time() - T0)
    per_set_budget = max(60.0, remaining / 3.0 * 0.75)

    for name, p in SETS.items():
        pn = NORM[name]
        log("")
        log(f"--- {name} ---")
        entry = {"n": N_OF_SET[name], "q": 3329,
                 "nist_classical_cutoff": NIST_CUTOFF[name]}

        # STAGE 0 -- the EV-MLKEM-015 comparison object
        s0 = dual_hybrid_cost[name]["log2_rop"]
        entry["stage0_dual_hybrid_fft"] = {
            "log2_rop": s0,
            "estimator_function": "estimator.lwe_dual.dual_hybrid(..., fft=True)",
            "cost": dual_hybrid_cost[name]["cost"],
        }
        log(f"  S0 dual_hybrid(fft=True)             {s0:.6f}")

        # STAGE 1 -- the estimator's own MATZOV implementation
        s1 = matzov_base[name]["log2_rop"]
        entry["stage1_matzov"] = {
            "log2_rop": s1,
            "estimator_function": "estimator.lwe_dual.matzov  (== LWE.dual_hybrid)",
            "cost": matzov_base[name]["cost"],
        }
        log(f"  S1 matzov (LWE.dual_hybrid)          {s1:.6f}   D1 = {s0 - s1:+.6f}")

        base = dict(log2_rop=s1,
                    p=int(matzov_base[name]["cost"]["p"]),
                    k_enum=int(matzov_base[name]["cost"]["zeta"]),
                    k_fft=int(matzov_base[name]["cost"]["t"]),
                    beta=int(matzov_base[name]["cost"]["beta"]),
                    m=int(matzov_base[name]["cost"]["m"]),
                    beta_sieve=None,
                    cost=matzov_base[name]["cost"])

        # CTRL-7 -- refinement machinery reproduces stage 1 on the coarse grid.
        # This control CAN fail: if my box code is wrong it will not return the
        # estimator's own optimum when restricted to the estimator's own grid.
        coarse_box = {"p": [base["p"]], "ke": 0, "kf": 0, "beta": 0}
        chk, _, _ = refine_grid(MZ, RC.MATZOV, pn, base, coarse_box, 60.0, log)
        ctrl7_ok = abs(chk["log2_rop"] - s1) < 1e-9
        entry["ctrl7_refiner_reproduces_stage1_on_coarse_point"] = {
            "recomputed": chk["log2_rop"], "stage1": s1, "delta": abs(chk["log2_rop"] - s1),
            "passes": ctrl7_ok}
        log(f"  CTRL-7 refiner reproduces S1 at the coarse point: {ctrl7_ok}")

        # STAGE 2 -- optimiser grid resolution (step 10 -> step 1)
        box = {"p": list(range(2, 9)), "ke": 8, "kf": 8, "beta": 8}
        t0 = time.time()
        s2b, n2, w2 = refine_grid(MZ, RC.MATZOV, pn, base, box, per_set_budget * 0.55, log)
        s2 = s2b["log2_rop"]
        entry["stage2_fine_grid"] = {
            "log2_rop": s2, "params": {k: v for k, v in s2b.items() if k != "cost"},
            "cost": s2b.get("cost"), "calls": n2, "wall_seconds": round(w2, 1),
            "box": {"p": [2, 8], "k_enum": "+-8", "k_fft": "+-8", "beta": "+-8"},
        }
        log(f"  S2 + fine (p,k_enum,k_fft,beta) grid {s2:.6f}   D2 = {s1 - s2:+.6f}  "
            f"[{n2} evals, {w2:.0f}s]")

        # STAGE 3 -- sample count m (the estimator fixes m = n)
        s3b, n3, w3 = refine_m(MZ, RC.MATZOV, pn, s2b, per_set_budget * 0.35, log)
        s3 = s3b["log2_rop"]
        entry["stage3_optimize_m"] = {
            "log2_rop": s3, "params": {k: v for k, v in s3b.items() if k != "cost"},
            "cost": s3b.get("cost"), "calls": n3, "wall_seconds": round(w3, 1),
        }
        log(f"  S3 + optimise sample count m         {s3:.6f}   D3 = {s2 - s3:+.6f}  "
            f"[{n3} evals, {w3:.0f}s]")

        # STAGE 4 -- explicit second block size beta_sieve
        s4b, n4, w4 = refine_beta_sieve(MZ, RC.MATZOV, pn, s3b, per_set_budget * 0.20, log)
        s4 = s4b["log2_rop"]
        entry["stage4_explicit_beta_sieve"] = {
            "log2_rop": s4, "params": {k: v for k, v in s4b.items() if k != "cost"},
            "cost": s4b.get("cost"), "calls": n4, "wall_seconds": round(w4, 1),
            "note": ("explicit beta_sieve also changes Nf; see refine_beta_sieve "
                     "docstring. If no explicit value beats the automatic one, D4 = 0."),
        }
        log(f"  S4 + explicit beta_sieve             {s4:.6f}   D4 = {s3 - s4:+.6f}  "
            f"[{n4} evals, {w4:.0f}s]")

        # RESIDUALS
        entry["differences_bits"] = {
            "D1_attack_function_identity": s0 - s1,
            "D2_optimizer_grid_resolution": s1 - s2,
            "D3_sample_count_m_not_optimized": s2 - s3,
            "D4_explicit_second_block_size": s3 - s4,
        }
        entry["residual_bits"] = {}
        for pubname, pub in PUBLISHED.items():
            g = pub["log2_cost"][name]
            entry["residual_bits"][pubname] = {
                "published_log2_cost": g,
                "total_gap_from_stage0": s0 - g,
                "attributed_D1_D4": (s0 - s4),
                "unattributed_residual": s4 - g,
                "fraction_attributed": (s0 - s4) / (s0 - g) if (s0 - g) != 0 else None,
            }
            log(f"  vs {pubname:22} published {g:.2f}: total gap {s0 - g:+.4f}, "
                f"attributed {s0 - s4:+.4f}, UNATTRIBUTED RESIDUAL {s4 - g:+.4f}")

        # Parameter comparison with Carrier Table C.1
        entry["parameter_comparison_vs_carrier_C1_CC"] = {
            "estimator_stage1": {"beta_bkz": base["beta"], "beta_sieve_auto": base["cost"].get("beta_"),
                                 "k_enum": base["k_enum"], "k_fft": base["k_fft"],
                                 "p_fft_modulus": base["p"], "m": base["m"],
                                 "k_lat": N_OF_SET[name] - base["k_enum"] - base["k_fft"],
                                 "log2_N": log2f(base["cost"]["N"]),
                                 "repetitions": "none (mu=0.5 hardcoded in Nf; no outer repeat)"},
            "carrier_CC": CARRIER_C1["CC"][name],
            "carrier_CC_intermediate": CARRIER_C2["CC"][name],
            "estimator_dual_hybrid_fft": {
                "beta": dual_hybrid_cost[name]["cost"].get("beta"),
                "d": dual_hybrid_cost[name]["cost"].get("d"),
                "zeta": dual_hybrid_cost[name]["cost"].get("zeta"),
                "t": dual_hybrid_cost[name]["cost"].get("t"),
                "repetitions": dual_hybrid_cost[name]["cost"].get("repetitions"),
                "m": dual_hybrid_cost[name]["cost"].get("m"),
                "fft_modulus": 2,
            },
        }
        R["per_set"][name] = entry

    # =======================================================================
    # SENSITIVITY AXES (not part of the additive chain)
    # =======================================================================
    log("")
    log("=" * 78)
    log("AXIS A  reduction cost model (the sieve gate count) -- matzov under each RC")
    log("=" * 78)
    rc_names = ["MATZOV", "GJ21", "Kyber", "ADPS16", "BDGL16", "ChaLoy21",
                "LaaMosPol14", "CheNgu12", "ABFKSW20", "ABLR21"]
    axisA = {}
    for nm in rc_names:
        rc = getattr(RC, nm)
        axisA[nm] = {}
        for name, p in SETS.items():
            try:
                c = ld.matzov(p, red_cost_model=rc)
                axisA[nm][name] = {"log2_rop": log2f(c["rop"]),
                                   "beta": float(c["beta"]), "t": float(c["t"]),
                                   "zeta": float(c["zeta"]), "p": float(c["p"])}
            except Exception as exc:
                axisA[nm][name] = {"error": f"{type(exc).__name__}: {exc}"}
        row = "  ".join(
            f"{name}={axisA[nm][name].get('log2_rop', float('nan')):.3f}"
            if "log2_rop" in axisA[nm][name] else f"{name}=FAILED"
            for name in SETS)
        log(f"  RC.{nm:12} {row}")
    R["axis_A_reduction_cost_model_matzov"] = axisA
    # isolate the MATZOV sieve re-costing: RC.MATZOV subclasses RC.GJ21 and
    # differs ONLY in the NN_AGPS coefficient table (estimator/reduction.py:963).
    R["axis_A_matzov_vs_gj21_sieve_recosting_bits"] = {
        name: (axisA["GJ21"][name]["log2_rop"] - axisA["MATZOV"][name]["log2_rop"])
        if "log2_rop" in axisA["GJ21"][name] and "log2_rop" in axisA["MATZOV"][name] else None
        for name in SETS}
    log(f"  RC.GJ21 - RC.MATZOV (isolates the MATZOV sieve re-costing) = "
        f"{ {k: round(v, 4) for k, v in R['axis_A_matzov_vs_gj21_sieve_recosting_bits'].items() if v} }")

    axisA2 = {}
    for nm in ["MATZOV", "GJ21", "ADPS16", "BDGL16"]:
        rc = getattr(RC, nm)
        axisA2[nm] = {}
        for name, p in SETS.items():
            try:
                c = dual_hybrid(p, red_cost_model=rc, fft=True)
                axisA2[nm][name] = {"log2_rop": log2f(c["rop"]), "beta": float(c["beta"])}
            except Exception as exc:
                axisA2[nm][name] = {"error": f"{type(exc).__name__}: {exc}"}
        log(f"  [dual_hybrid fft] RC.{nm:12} " + "  ".join(
            f"{name}={axisA2[nm][name].get('log2_rop', float('nan')):.3f}"
            if "log2_rop" in axisA2[nm][name] else f"{name}=FAILED" for name in SETS))
    R["axis_A2_reduction_cost_model_dual_hybrid_fft"] = axisA2

    log("")
    log("=" * 78)
    log("AXIS B  dimensions-for-free -- both sides apply it; size what it is worth")
    log("=" * 78)

    class _NoD4F(RC_MATZOV_CLASS):
        __name__ = "MATZOV_no_d4f"

        @staticmethod
        def d4f(beta):
            return 0.0

    nod4f = _NoD4F()
    axisB = {}
    for name, p in SETS.items():
        c = ld.matzov(p, red_cost_model=nod4f)
        v = log2f(c["rop"])
        axisB[name] = {"log2_rop_no_d4f": v,
                       "log2_rop_with_d4f": matzov_base[name]["log2_rop"],
                       "d4f_worth_bits": v - matzov_base[name]["log2_rop"],
                       "d4f_at_stage1_beta": float(RC.MATZOV.d4f(
                           R["per_set"][name]["stage1_matzov"]["cost"]["beta"]))}
        log(f"  {name:10} with d4f {matzov_base[name]['log2_rop']:.4f}  "
            f"without {v:.4f}  worth {axisB[name]['d4f_worth_bits']:+.4f} bits  "
            f"(d4f(beta*) = {axisB[name]['d4f_at_stage1_beta']:.2f})")
    R["axis_B_dimensions_for_free"] = axisB

    log("")
    log("=" * 78)
    log("AXIS C  units: are the published numbers core-SVP counts rather than gates?")
    log("=" * 78)
    axisC = {}
    for name in SETS:
        core = axisA["ADPS16"][name]["log2_rop"]
        gates = matzov_base[name]["log2_rop"]
        axisC[name] = {
            "matzov_under_RC.ADPS16_coreSVP": core,
            "matzov_under_RC.MATZOV_gates": gates,
            "gate_minus_coreSVP_bits": gates - core,
            "published_carrier": PUBLISHED["Carrier-CRYPTO2025"]["log2_cost"][name],
            "published_matzov": PUBLISHED["MATZOV-2022"]["log2_cost"][name],
        }
        log(f"  {name:10} core-SVP (RC.ADPS16) {core:.3f} | gates (RC.MATZOV) {gates:.3f} "
            f"| published Carrier {axisC[name]['published_carrier']} "
            f"MATZOV {axisC[name]['published_matzov']}  -> units differ by "
            f"{gates - core:.2f} bits")
    R["axis_C_units_core_svp_vs_gates"] = axisC

    R["finished_utc"] = datetime.now(timezone.utc).isoformat()
    R["wall_seconds_total"] = round(time.time() - T0, 1)
    R["environment"] = {
        "python": sys.version,
        "platform": platform.platform(),
        "mpmath": mp.__version__,
        "cpu_count": os.cpu_count(),
    }
    R["stdout_log"] = lines
    R["terminal_state"] = "completed"

    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=2, sort_keys=True, default=str)
    h = hashlib.sha256(open(args.out, "rb").read()).hexdigest()
    log("")
    log(f"wrote {args.out}  sha256={h}  ({R['wall_seconds_total']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
