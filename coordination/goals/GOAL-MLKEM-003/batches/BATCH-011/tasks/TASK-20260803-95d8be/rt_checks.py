#!/usr/bin/env python3
"""
TASK-20260803-95d8be / GOAL-MLKEM-003 / BATCH-011 -- RED TEAM, independent session.

This is the ONE results-bearing run this task's budget allows. It does not
repair, reproduce-for-confirmation, or extend the TASK-20260803-fb52f4 package.
It runs the checks that could FALSIFY that package's interpretation.

NOTHING HERE IS MEASURED. Every number is a cost-model estimate out of pinned
lattice-estimator 3e48ef421ec256afddb3e7d2249a77eab6e9ba12 driven Sage-free
through tools/sage_free_estimator. No ML-KEM break is claimed and no security
proof is claimed.

Blocks:
  C0  known-answer control, as a subprocess, before anything else (task card).
  C1  instrument identity: file hashes, pin, and whether LWE.dual_hybrid is
      lwe_dual.matzov.
  R1  independent recomputation of S0 (dual_hybrid fft=True), S1 (matzov) and
      primal_bdd on all three sets, plus whether each cost dict carries `mem`.
  R2  SYMMETRIC-OPTIMISER control. The package relaxed optimiser slack for
      `matzov` (stages 2-4) and compared the result against the STOCK
      primal_bdd. This block gives primal_bdd a comparable local relaxation
      and asks how much of ANOM-3 survives equal treatment.
  R3  MEMORY. `matzov` reports no `mem`; `dual_hybrid` does (lwe_dual.py:172,
      :249) and `primal_bdd` reports none at all. This block reconstructs the
      dual's memory in the estimator's OWN documented unit ("integers mod q",
      lwe_dual.py:204) and computes the memory-charge exponents at which
      ANOM-3 and the NIST undercut flip.
  N1  sign null on R3's crossover quantity.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

import mpmath as mp

REPO = "/home/user/crypto-autoresearcher"
LE = os.environ.get("LE_DIR", "/tmp/le2")
PIN = "3e48ef421ec256afddb3e7d2249a77eab6e9ba12"
CONTROL = f"{REPO}/tools/sage_free_estimator/known_answer_control.py"
SHIM = f"{REPO}/tools/sage_free_estimator/shim"

OUT = {}
T0 = time.time()


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def lg2(x):
    return float(mp.log(mp.mpf(str(x)), 2))


# --------------------------------------------------------------------------
# C0 -- known-answer control, subprocess, FIRST.
# --------------------------------------------------------------------------
env = dict(os.environ)
env["PYTHONPATH"] = f"{SHIM}:{LE}"
p = subprocess.run([sys.executable, CONTROL], capture_output=True, text=True, env=env)
OUT["C0_known_answer_control"] = {
    "cmd": f"PYTHONPATH={SHIM}:{LE} python3 {CONTROL}",
    "exit_code": p.returncode,
    "stdout_verbatim": p.stdout,
    "stderr_verbatim": p.stderr,
    "control_sha256": sha(CONTROL),
    "shim_sha256": sha(f"{SHIM}/sage/all.py"),
}
if p.returncode != 0:
    OUT["ABORTED"] = "known-answer control did not exit 0; no research figure may be reported"
    json.dump(OUT, open(sys.argv[1], "w"), indent=1, sort_keys=True)
    sys.exit(2)

sys.path.insert(0, SHIM)
sys.path.insert(0, LE)

from estimator import LWE, schemes  # noqa: E402
from estimator.reduction import RC  # noqa: E402
import estimator.lwe_dual as ld  # noqa: E402
import estimator.lwe_primal as lp  # noqa: E402

# --------------------------------------------------------------------------
# C1 -- instrument identity.
# --------------------------------------------------------------------------
rev = subprocess.run(["git", "-C", LE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
dirty = subprocess.run(["git", "-C", LE, "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
OUT["C1_instrument_identity"] = {
    "le_dir": LE,
    "git_head": rev,
    "pin_expected": PIN,
    "pin_matches": rev == PIN,
    "dirty": dirty,
    "file_sha256": {f: sha(f"{LE}/estimator/{f}") for f in
                    ("lwe.py", "lwe_dual.py", "lwe_primal.py", "reduction.py")},
    "LWE_dual_hybrid_is_lwe_dual_matzov": LWE.dual_hybrid is ld.matzov,
    "LWE_dual_hybrid_repr": repr(LWE.dual_hybrid),
    "lwe_dual_dual_hybrid_repr": repr(ld.dual_hybrid),
    "network_used": False,
}

# the in-process .n(prec) patch, identical in intent to the producer's H4 patch.
_orig_exp = ld.exp


class _FaithfulReal(mp.mpf):
    def n(self, prec=53, digits=None, algorithm=None):
        if digits is not None:
            prec = int(digits * 3.3219280948873626) + 1
        with mp.workprec(int(prec)):
            return +mp.mpf(self)


ld.exp = lambda x: _FaithfulReal(_orig_exp(x))
OUT["C1_instrument_identity"]["in_process_patch"] = (
    "estimator.lwe_dual.exp rebound in THIS process so RealNumber.n(30) at "
    "lwe_dual.py:607 resolves; nothing written; same intent as producer H4"
)

SETS = {"Kyber512": schemes.Kyber512, "Kyber768": schemes.Kyber768, "Kyber1024": schemes.Kyber1024}
CUTOFF = {"Kyber512": 143, "Kyber768": 207, "Kyber1024": 272}
CUTOFF_PROVENANCE = (
    "SECONDARY ONLY, inherited unchanged from EV-MLKEM-015/EV-MLKEM-020 H11 and "
    "producer H8. No primary NIST/FIPS-203 text was read by this task. Every "
    "margin below inherits that."
)


def costdict(c):
    d = {}
    for k in c.keys():
        try:
            d[str(k)] = float(c[k])
        except Exception:
            d[str(k)] = str(c[k])
    return d


# --------------------------------------------------------------------------
# R1 -- independent recomputation.
# --------------------------------------------------------------------------
R1 = {}
for name, par in SETS.items():
    row = {}
    t = time.time()
    c0 = ld.dual_hybrid(par, red_cost_model=RC.MATZOV, fft=True)
    row["S0_lwe_dual_dual_hybrid_fft"] = {"log2_rop": lg2(c0["rop"]), "cost": costdict(c0),
                                          "has_mem_field": "mem" in c0.keys(),
                                          "seconds": round(time.time() - t, 2)}
    t = time.time()
    c1 = ld.matzov(par, red_cost_model=RC.MATZOV)
    row["S1_lwe_dual_matzov"] = {"log2_rop": lg2(c1["rop"]), "cost": costdict(c1),
                                 "has_mem_field": "mem" in c1.keys(),
                                 "seconds": round(time.time() - t, 2)}
    t = time.time()
    cp = LWE.primal_bdd(par, red_cost_model=RC.MATZOV)
    row["primal_bdd_stock"] = {"log2_rop": lg2(cp["rop"]), "cost": costdict(cp),
                               "has_mem_field": "mem" in cp.keys(),
                               "seconds": round(time.time() - t, 2)}
    row["ANOM3_primal_minus_matzov_bits"] = row["primal_bdd_stock"]["log2_rop"] - row["S1_lwe_dual_matzov"]["log2_rop"]
    row["matzov_margin_vs_cutoff_bits"] = CUTOFF[name] - row["S1_lwe_dual_matzov"]["log2_rop"]
    row["primal_margin_vs_cutoff_bits"] = CUTOFF[name] - row["primal_bdd_stock"]["log2_rop"]
    R1[name] = row
OUT["R1_recomputation"] = R1
OUT["R1_note"] = ("Reproduces or fails to reproduce the package's S0/S1/primal_bdd. "
                  "`has_mem_field` is the load-bearing column: see R3.")

# --------------------------------------------------------------------------
# R2 -- SYMMETRIC-OPTIMISER control on the primal side.
# --------------------------------------------------------------------------
R2 = {}
for name, par in SETS.items():
    stock = R1[name]["primal_bdd_stock"]["cost"]
    b0, d0 = int(stock["beta"]), int(stock["d"])
    best = (R1[name]["primal_bdd_stock"]["log2_rop"], b0, d0)
    calls = 0
    t = time.time()
    for beta in range(max(40, b0 - 8), b0 + 9):
        for dd in range(d0 - 40, d0 + 41, 4):
            if time.time() - t > 420:
                break
            try:
                c = lp.PrimalHybrid.cost(beta=beta, params=par.normalize(), zeta=0, babai=False,
                                         mitm=False, d=dd, red_cost_model=RC.MATZOV)
                calls += 1
                v = lg2(c["rop"])
                if v < best[0]:
                    best = (v, beta, dd)
            except Exception:
                pass
    R2[name] = {
        "stock_log2_rop": R1[name]["primal_bdd_stock"]["log2_rop"],
        "refined_log2_rop": best[0],
        "refined_beta": best[1],
        "refined_d": best[2],
        "primal_optimiser_slack_bits": R1[name]["primal_bdd_stock"]["log2_rop"] - best[0],
        "calls": calls,
        "seconds": round(time.time() - t, 2),
        "box": "beta +-8 step 1, d +-40 step 4, zeta=0, babai=False, mitm=False, RC.MATZOV",
    }
    R2[name]["ANOM3_after_symmetric_treatment_bits"] = best[0] - R1[name]["S1_lwe_dual_matzov"]["log2_rop"]
OUT["R2_symmetric_optimiser_control"] = R2
OUT["R2_note"] = (
    "The package relaxed optimiser slack on the DUAL side only (stages 2-4: fine "
    "(p,k_enum,k_fft,beta) grid, sample count m, explicit beta_sieve) and then "
    "tabulated 'primal - S4' against the STOCK primal_bdd. This block asks what "
    "the primal side recovers under a comparable local relaxation. It is a "
    "LOWER bound on primal-side slack (local box, d step 4, eta not varied)."
)

# --------------------------------------------------------------------------
# R3 -- MEMORY, in the estimator's own documented unit.
# --------------------------------------------------------------------------
# lwe_dual.py:204 "``mem``: memory requirement in integers mod q"
# lwe_dual.py:169-172 charges sieve_dim * N for the stored dual vectors
# lwe_dual.py:249    memory_cost = size_fft  (the distinguisher table)
# MATZOV.cost (lwe_dual.py:613-626) sets NO mem key at all; T_fftf(k,p) =
# C_mul*k*p**(k+1) (lwe_dual.py:507) is an FFT over Z_p^k, so its accumulator
# table has p**k entries.
R3 = {}
for name, par in SETS.items():
    c1 = R1[name]["S1_lwe_dual_matzov"]["cost"]
    p_fft, k_fft, k_enum = c1["p"], c1["t"], c1["zeta"]
    beta_sieve = c1["beta_"]
    m = c1["m"]
    n = float(par.n)
    k_lat = n - k_fft - k_enum
    d_dual = k_lat + m
    log2_fft_table_entries = k_fft * math.log2(p_fft)
    log2_sieve_db_vectors = 0.2075 * beta_sieve
    log2_sieve_db_zq = log2_sieve_db_vectors + math.log2(beta_sieve)
    log2_M_dual = math.log2(2.0 ** (log2_fft_table_entries - 200) + 2.0 ** (log2_sieve_db_zq - 200)) + 200

    cp = R1[name]["primal_bdd_stock"]["cost"]
    eta = cp.get("eta", cp.get("η"))
    beta_p = cp["beta"]
    # d4f as the instrument applies it (reduction.py:800 path, RC.MATZOV inherits Kyber.d4f)
    d4f_eta = float(RC.MATZOV.d4f(eta))
    d4f_beta = float(RC.MATZOV.d4f(beta_p))
    svp_dim_eff = eta - d4f_eta
    bkz_dim_eff = beta_p - d4f_beta
    peak = max(svp_dim_eff, bkz_dim_eff)
    log2_M_primal = 0.2075 * peak + math.log2(peak)

    tm = R1[name]["S1_lwe_dual_matzov"]["log2_rop"]
    tp = R1[name]["primal_bdd_stock"]["log2_rop"]
    dmem = log2_M_dual - log2_M_primal
    R3[name] = {
        "matzov_p_fft": p_fft, "matzov_k_fft": k_fft, "matzov_k_enum": k_enum,
        "matzov_beta_sieve": beta_sieve, "matzov_d": d_dual,
        "log2_matzov_fft_table_entries": log2_fft_table_entries,
        "log2_matzov_sieve_db_zq_elements": log2_sieve_db_zq,
        "log2_M_matzov_total": log2_M_dual,
        "log2_M_dual_hybrid_fft_reported_by_instrument":
            lg2(R1[name]["S0_lwe_dual_dual_hybrid_fft"]["cost"]["mem"])
            if "mem" in R1[name]["S0_lwe_dual_dual_hybrid_fft"]["cost"] else None,
        "primal_eta": eta, "primal_beta": beta_p,
        "primal_svp_dim_effective": svp_dim_eff, "primal_bkz_dim_effective": bkz_dim_eff,
        "log2_M_primal_bdd": log2_M_primal,
        "log2_M_primal_bdd_EV_MLKEM_020_recorded":
            {"Kyber512": 88.494071, "Kyber768": 131.657286, "Kyber1024": 180.924993}[name],
        "memory_excess_of_dual_over_primal_bits": dmem,
        "ANOM3_time_advantage_bits": tp - tm,
        "c_flip_ANOM3": ((tp - tm) / dmem) if abs(dmem) > 1e-9 else None,
        "c_star_dual_vs_cutoff": (CUTOFF[name] - tm) / log2_M_dual,
        "c_star_primal_vs_cutoff": (CUTOFF[name] - tp) / log2_M_primal,
    }
OUT["R3_memory"] = R3
OUT["R3_note"] = (
    "c_flip_ANOM3 is the memory-charge exponent c in T*M^c at which matzov stops "
    "being cheaper than primal_bdd, holding both attacks fixed (no memory-aware "
    "re-optimisation, the same H10 posture EV-MLKEM-020 used). c_star_* is the "
    "exponent at which the undercut of the (SECONDARY-SOURCED) NIST cutoff dies. "
    "Units: entries. The FFT accumulator is not a Z_q element and is generally "
    "WIDER, so log2_M_matzov_total is an UNDERSTATEMENT in bits, i.e. conservative "
    "AGAINST this red team's own objection."
)

# --------------------------------------------------------------------------
# N1 -- sign null on the R3 crossover.
# --------------------------------------------------------------------------
signs = sorted({(1 if R3[s]["memory_excess_of_dual_over_primal_bits"] > 0 else -1) for s in R3})
OUT["N1_sign_null"] = {
    "what": "the memory-excess quantity must be able to take both signs, else it is rigged",
    "per_set_memory_excess_bits": {s: R3[s]["memory_excess_of_dual_over_primal_bits"] for s in R3},
    "both_signs_observed": len(signs) == 2,
    "verdict": ("DISCRIMINATING: the quantity takes both signs across the three sets, so it is not "
                "an artifact of an arithmetic that can only produce one sign"
                if len(signs) == 2 else
                "ONE SIGN ONLY across the three sets; treat with the caution the inventor protocol "
                "requires of a quantity that cannot decay"),
}

OUT["meta"] = {
    "task_id": "TASK-20260803-95d8be",
    "role": "red-team",
    "finished_utc": datetime.now(timezone.utc).isoformat(),
    "wall_seconds": round(time.time() - T0, 2),
    "python": sys.version,
    "mpmath": mp.__version__,
    "nist_cutoff_provenance": CUTOFF_PROVENANCE,
    "what_these_numbers_are": "COST-MODEL ESTIMATES. Nothing was measured. No break, no proof.",
}
json.dump(OUT, open(sys.argv[1], "w"), indent=1, sort_keys=True, default=str)
print(json.dumps({k: OUT[k] for k in ("R1_recomputation", "R2_symmetric_optimiser_control",
                                      "R3_memory", "N1_sign_null")}, indent=1, default=str))
