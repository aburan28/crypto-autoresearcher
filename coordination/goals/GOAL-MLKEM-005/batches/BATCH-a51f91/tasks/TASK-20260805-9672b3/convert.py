#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TASK-20260805-9672b3 (T3 of BATCH-a51f91, GOAL-MLKEM-005).

Replace the LINEARISED norm-ratio -> block-size conversion

        dbeta_lin = ln(c) / (2 ln delta)                      [linearisation]

with a FINITE DIFFERENCE OF THE OPTIMISER'S OWN OUTPUT, with the number of
samples m (equivalently the lattice rank d = m + n) RE-OPTIMISED:

        dbeta_fd(c) = beta*(c) - beta*(1)                     [this instrument]

where beta*(x) is the block size the lattice-estimator's own primal_bdd
optimiser selects when the target-vector norm is scaled by x, under RC.MATZOV.

WHAT THE KNOB IS.  In the primal BDD embedding the target vector is (e | s)
(times the Bai-Galbraith factor xi, which is 1 here because Xs == Xe for every
FIPS 203 parameter set).  Scaling BOTH Xs.stddev and Xe.stddev by c scales the
target-vector norm by exactly c and leaves the lattice completely alone: q, n,
the number of available samples, the basis profile and the volume q^(d-n) are
all unchanged, and xi stays exactly 1 (estimator's PrimalUSVP._xi_factor
returns RR(1) unless Xs < Xe).  So c is a pure norm ratio, which is the
quantity the linearisation is applied to in this lane.

WHY IT DIFFERS FROM THE LINEARISATION.  dbeta_lin = ln c / (2 ln delta) is
obtained by differentiating the success condition at FIXED d AND FIXED m and
keeping only the 2 ln delta term of the derivative.  The estimator does neither:
primal_hybrid.cost_zeta optimises beta first (step 1) and then RE-OPTIMISES d,
hence m = d - n, at that beta (step 2, `local_minimum(params.n - zeta,
cost["d"] + 1)`), and its success condition carries further beta-dependence.
This script reports what the optimiser actually does.

OBLIGATION-4 LABEL, BINDING AND RESTATED IN THE OUTPUT
------------------------------------------------------
The ratio of the omitted to the retained denominator term in that
linearisation is  1/(4 beta ln delta) -- a function of beta ALONE, with sign
and magnitude fixed A PRIORI, derivable before anything is run.  The
linearisation-vs-finite-difference comparison in `design_audit_NOT_A_FINDING`
is therefore a DESIGN AUDIT, NOT A FINDING.  No number from that block may
enter an evidence record or a knowledge entry.  What MAY be recorded is the
finite-difference table, which is an instrument output.

SCOPE AND PROHIBITIONS (from the task card, restated next to the numbers)
------------------------------------------------------------------------
* Every rop / beta / eta / d in this file is a MODELLED cost-model estimate
  produced by the lattice-estimator.  Nothing here is a measurement of a real
  lattice, a real sieve, or a real attack.  The finite difference is an exact,
  deterministic readout of a piece of software; "measured" below always means
  "read off this instrument", never "observed in a lattice experiment".
* The mechanism this feeds is SESSION recovery, not key recovery.  No number
  here may be subtracted from the in-repo primal_bdd margins of
  2.80 / 6.04 / 1.28 bits.
* No ML-KEM break claim, and no security claim in either direction.
  AGENTS.md rule 12 is UNMET and UNWAIVED.  No EV-MLKEM-* or KN-* status change.
* The toy-shape arm is instrument characterisation of the CONVERSION only.  It
  is not crypto-scale evidence and must not be transported to beta = 606,
  d = 1420.

USAGE (single run; the known-answer control runs first, from inside this run)
    PYTHONPATH=tools/sage_free_estimator/shim:<estimator> python3 convert.py
with <estimator> a clone of github.com/malb/lattice-estimator at
3e48ef421ec256afddb3e7d2249a77eab6e9ba12.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Frozen constants of this task
# ---------------------------------------------------------------------------
TASK_ID = "TASK-20260805-9672b3"
BATCH_ID = "BATCH-a51f91"
GOAL_ID = "GOAL-MLKEM-005"
PINNED_ESTIMATOR = "3e48ef421ec256afddb3e7d2249a77eab6e9ba12"

# The four norm ratios named in the handoff.  Written as k/400 so that the
# scan grid below hits them as the identical IEEE-754 doubles.
C_VALUES = [0.99, 0.98, 0.95, 0.90]
# Card-supplied conversion constant.  NOTE (labelling): 0.292 is the classical
# core-sieve exponent (BDGL16 list decoding, asymptotic).  The beta values it
# is applied to come from RC.MATZOV, whose own per-block slope is
# a = 0.29613500308205365 ("list_decoding-classical") BEFORE dimensions-for-
# free, progressive overhead C and the (d - beta) SVP-call factor.  So
# 0.292 * dbeta and the estimator's own d log2(rop) are two DIFFERENT cost
# models; both are reported, separately, and neither is a measurement.
BITS_PER_BLOCK_CARD = 0.292

SCAN_K_MIN, SCAN_K_MAX, SCAN_DEN = 360, 400, 400  # c = k/400 over [0.90, 1.00]
SIGN_CONTROL_C = [1.01, 1.02, 1.05]               # norm made WORSE: beta must not fall
WALL_CLOCK_BUDGET_S = 2400.0
SOFT_ABORT_S = 1900.0                             # leave room to write results.json

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_repo(start):
    """Walk up to the repository root. Located by content, not by counting '..'
    levels: attempt 001 of this task crashed at t = 0.07 s because a hard-coded
    six-level walk landed one directory short (see receipt.json, attempt 001,
    implementation_error). No research number was produced by that attempt."""
    d = start
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, "tools", "sage_free_estimator")):
            return d
        d = os.path.dirname(d)
    raise SystemExit("FATAL: repository root (containing tools/sage_free_estimator) not found")


REPO = _find_repo(HERE)
OUT = os.path.join(HERE, "results.json")

T0 = time.time()
CALLS = {"arm_a": 0, "arm_b": 0}


def elapsed() -> float:
    return time.time() - T0


def peak_rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024.0 ** 2)


def sh(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 16), b""):
            h.update(blk)
    return h.hexdigest()


def sha256_tree(root):
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in sorted(filenames):
            p = os.path.join(dirpath, fn)
            out[os.path.relpath(p, REPO)] = sha256_file(p)
    return dict(sorted(out.items()))


# ---------------------------------------------------------------------------
# STEP 0 -- the known-answer control, on the COMMITTED shim, before any other
# number.  Recorded VERBATIM.  A failure aborts: that is an infrastructure
# outcome under AGENTS.md rule 5, never evidence.
# ---------------------------------------------------------------------------
def step0_known_answer_control(estimator_path):
    script = os.path.join(REPO, "tools", "sage_free_estimator", "known_answer_control.py")
    env_pp = os.path.join(REPO, "tools", "sage_free_estimator", "shim") + ":" + estimator_path
    cmd = [sys.executable, script]
    t = time.time()
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": env_pp})
    dt = time.time() - t
    rec = {
        "why_first": ("AGENTS.md rule 5 and the task card: the shim asserts nothing on its "
                      "own authority. It is trusted only insofar as it reproduces values "
                      "computed under REAL Sage (RUN-MLKEM-015-001, EXP-MLKEM-015) and "
                      "committed before the shim existed."),
        "command": f"PYTHONPATH={env_pp} {sys.executable} {os.path.relpath(script, REPO)}",
        "cwd": REPO,
        "script_sha256": sha256_file(script),
        "exit_code": p.returncode,
        "wall_clock_seconds": round(dt, 3),
        "stdout_verbatim": p.stdout,
        "stderr_verbatim": p.stderr,
    }
    ok_primal = "0.00e+00" in p.stdout and p.returncode == 0 and "PASS:" in p.stdout
    rec["passed"] = bool(ok_primal)
    rec["primal_bdd_delta_required"] = "0.00e+00 (exact equality, not a tolerance)"
    rec["primal_bdd_delta_observed"] = (
        "0.00e+00 on Kyber512 and Kyber768" if ok_primal else "NOT 0.00e+00 -- see stdout_verbatim")
    return rec


# ---------------------------------------------------------------------------
# The instrument
# ---------------------------------------------------------------------------
def build():
    """Import the estimator and return the callables used below."""
    from estimator import RC, ND, schemes                      # noqa: F401
    from estimator.lwe_primal import primal_bdd, PrimalHybrid  # noqa: F401
    from estimator.lwe_parameters import LWEParameters         # noqa: F401
    from estimator.reduction import delta as deltaf            # noqa: F401
    return RC, ND, schemes, primal_bdd, PrimalHybrid, LWEParameters, deltaf


def scaled_params(ND, p, c):
    """Scale the TARGET-VECTOR norm by exactly c, leaving the lattice alone.

    Both Xs and Xe are replaced by DiscreteGaussian at c * (their stddev).  The
    substitution of the distribution FAMILY is inert on this code path and that
    is verified, not assumed: control C1 checks that at c = 1 the substituted
    parameters reproduce the CenteredBinomial baseline EXACTLY (rop, beta, eta
    and d), against the Sage-computed known-answer values.
    """
    return p.updated(Xs=ND.DiscreteGaussian(c * float(p.Xs.stddev)),
                     Xe=ND.DiscreteGaussian(c * float(p.Xe.stddev)))


def read(cost, n):
    """Read the optimiser's answer.  d = m_used + n for zeta = 0, because the
    simulated basis is [q I_m | A_n ; 0 | xi I_n] (estimator lwe_primal.py:
    log_vol = (d - n) log q + n log xi), so m_used = d - n."""
    d = int(cost["d"])
    return {
        "log2_rop": math.log2(float(cost["rop"])),
        "beta": int(cost["beta"]),
        "eta": int(cost["eta"]),
        "d": d,
        "m_used": d - n,
    }


def arm_a(primal_bdd, RC, params, n):
    """ARM A -- the deliverable.  Full optimiser: beta optimised, then d (hence
    m) RE-OPTIMISED at that beta.  This is exactly `primal_bdd(p, RC.MATZOV)`."""
    CALLS["arm_a"] += 1
    return read(primal_bdd(params, red_cost_model=RC.MATZOV), n)


def arm_b(PrimalHybrid, LWEParameters, RC, params, n):
    """ARM B -- control.  Same code path with step 2 (the d re-optimisation)
    switched OFF, so d stays at the estimator's closed-form heuristic
    d(beta) = max(beta, min(ceil(sqrt(n log(q/xi) / log delta(beta))), m)).

    This cannot be obtained through the public entry point: `primal_bdd(p,
    optimize_d=False)` SILENTLY DISCARDS the kwarg (primal_hybrid.__call__
    builds `f = partial(self.cost_zeta, ...)` WITHOUT **kwds, and the explicit-
    zeta branch calls `f(zeta=zeta)`), returning the fully-optimised answer.
    That is recorded as instrument anomaly A1.  We therefore call cost_zeta
    directly, reproducing __call__'s own preprocessing, and control C2 verifies
    that the same call with optimize_d=True reproduces primal_bdd bit-for-bit.
    """
    CALLS["arm_b"] += 2
    pn = LWEParameters.normalize(params)
    assert pn == params, "normalize() is not the identity on these parameters"
    m_allowed = params.m + params.n if params.Xs <= params.Xe else params.m
    kw = dict(zeta=0, params=pn, red_cost_model=RC.MATZOV, m=m_allowed,
              babai=False, mitm=False)
    return (read(PrimalHybrid.cost_zeta(optimize_d=True, **kw), n),
            read(PrimalHybrid.cost_zeta(optimize_d=False, **kw), n),
            int(m_allowed))


def diff(base, scal, c):
    """The finite difference, plus the two bit figures kept in SEPARATE fields."""
    dbeta = scal["beta"] - base["beta"]
    return {
        "c": c,
        "ln_c": math.log(c),
        "baseline": base,
        "scaled": scal,
        # --- the deliverable: the optimiser's own output, m re-optimised ---
        "delta_beta_fd": dbeta,
        "bits_0292_x_delta_beta_fd": BITS_PER_BLOCK_CARD * dbeta,
        # --- what the estimator itself says the cost change is (RC.MATZOV) ---
        "delta_log2_rop_matzov": scal["log2_rop"] - base["log2_rop"],
        # --- what m re-optimisation did ---
        "delta_d": scal["d"] - base["d"],
        "delta_m_used": scal["m_used"] - base["m_used"],
        "delta_eta": scal["eta"] - base["eta"],
    }


def main():
    estimator_path = None
    for entry in os.environ.get("PYTHONPATH", "").split(":"):
        if entry and os.path.isdir(os.path.join(entry, "estimator")):
            estimator_path = os.path.abspath(entry)
            break
    if estimator_path is None:
        print("FATAL: no lattice-estimator on PYTHONPATH", file=sys.stderr)
        return 2

    res = {
        "schema": "crypto.autoresearch.task_results.v1",
        "task_id": TASK_ID, "batch_id": BATCH_ID, "goal_id": GOAL_ID,
        "role": "executor",
        "title": ("T3: norm ratio -> block size by finite difference of the estimator's own "
                  "optimiser output, with m re-optimised"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "role_note": ("Executor output: observations only. No hypothesis is declared supported, "
                      "rejected or closed; no heuristic is declared validated or refuted."),
    }

    # ---- 0. the control, first, verbatim ---------------------------------
    res["step0_known_answer_control"] = step0_known_answer_control(estimator_path)
    if not res["step0_known_answer_control"]["passed"]:
        res["aborted"] = {
            "reason": "known-answer control did not PASS at delta 0.00e+00",
            "failure_class": "infrastructure_error",
            "note": ("AGENTS.md rule 5: this is an infrastructure outcome, NOT evidence. "
                     "No finite-difference number was computed."),
        }
        with open(OUT, "w") as fh:
            json.dump(res, fh, indent=2)
        print("ABORT: known-answer control failed. See results.json.", file=sys.stderr)
        return 1
    print(res["step0_known_answer_control"]["stdout_verbatim"])

    RC, ND, schemes, primal_bdd, PrimalHybrid, LWEParameters, deltaf = build()

    # ---- provenance ------------------------------------------------------
    rc_repo, sha_repo, _ = sh(["git", "rev-parse", "HEAD"], cwd=REPO)
    _, dirty_repo, _ = sh(["git", "status", "--porcelain"], cwd=REPO)
    _, branch, _ = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO)
    rc_est, sha_est, _ = sh(["git", "rev-parse", "HEAD"], cwd=estimator_path)
    _, dirty_est, _ = sh(["git", "status", "--porcelain"], cwd=estimator_path)
    import mpmath
    import scipy
    res["instrument"] = {
        "repo_commit": sha_repo.strip(),
        "repo_branch": branch.strip(),
        "repo_dirty_tree": dirty_repo.strip().splitlines(),
        "estimator_path": estimator_path,
        "estimator_commit": sha_est.strip(),
        "estimator_commit_pinned": PINNED_ESTIMATOR,
        "estimator_commit_matches_pin": sha_est.strip() == PINNED_ESTIMATOR,
        "estimator_dirty_tree": dirty_est.strip().splitlines(),
        "shim_file_sha256": sha256_tree(os.path.join(REPO, "tools", "sage_free_estimator")),
        "shim_edited_by_this_task": False,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "mpmath": mpmath.__version__,
        "scipy": scipy.__version__,
        "attack": "primal_bdd (PrimalHybrid with zeta=0, mitm=False, babai=False)",
        "red_cost_model": "RC.MATZOV",
        "red_cost_model_note": (
            "MATZOV == GJ21 with nn='list_decoding-classical': a = 0.29613500308205365, "
            "b = 20.387885985467914, then dimensions-for-free d4f(beta), progressive-BKZ "
            "overhead C = 1/(1 - 2^-a) and svp_calls = C * max(d - beta, 1). Its effective "
            "bits-per-block slope is therefore NOT the 0.292 of the card's conversion "
            "constant; both are reported, in separate fields."),
        "randomness": ("None. The estimator is deterministic on this path: no RNG is used, "
                       "no sampling is performed, scipy.optimize.minimize_scalar is only "
                       "reached on the zeta=None branch which primal_bdd does not take "
                       "(it passes zeta=0). No seed exists to record. Determinism is "
                       "corroborated by the known-answer control reproducing archived "
                       "Sage values to delta 0.0."),
    }
    res["method"] = {
        "knob": ("norm ratio c applied to the BDD target vector (e | s) by scaling BOTH "
                 "Xs.stddev and Xe.stddev by c. The lattice is untouched: q, n, the sample "
                 "budget m + n, the basis profile and vol = q^(d-n) xi^n are unchanged, and "
                 "xi = 1 exactly (PrimalUSVP._xi_factor returns RR(1) unless Xs < Xe, and "
                 "Xs == Xe for all three FIPS 203 sets, before and after scaling)."),
        "arm_a": ("primal_bdd(p, RC.MATZOV): beta optimised (cost_zeta step 1), then d -- "
                  "hence m = d - n -- RE-OPTIMISED at that beta (step 2). THE DELIVERABLE."),
        "arm_b": ("cost_zeta(..., optimize_d=False): identical except step 2 is skipped, so d "
                  "is slaved to the closed-form heuristic d(beta). Isolates what re-optimising "
                  "m contributes. Not a claim about the world; an instrument control."),
        "delta_beta_fd": "beta*(c) - beta*(1), both from the optimiser, integer-valued by construction",
        "quantisation_disclosure": (
            "beta*(.) is an INTEGER selected by a discrete search, so delta_beta_fd is "
            "quantised to integers and carries the optimiser's own selection noise. The "
            "linearisation returns a real number. A cell-by-cell difference between them is "
            "therefore partly quantisation and must not be read as a smooth correction: see "
            "the `scan` block, which exposes the staircase directly."),
        "why_normalize_forbids_scaling_Xe_alone": (
            "LWEParameters.normalize() SWAPS secret and noise when Xe < Xs and m == n, which "
            "holds for all three Kyber sets. Scaling Xe alone would therefore silently change "
            "which distribution plays which role and would not be a norm-ratio experiment. "
            "Both are scaled together, which is also the quantity ln c/(2 ln delta) is applied "
            "to in this lane."),
    }

    SETS = [("Kyber512", schemes.Kyber512), ("Kyber768", schemes.Kyber768),
            ("Kyber1024", schemes.Kyber1024)]

    # ---- controls --------------------------------------------------------
    controls = {}

    # C1 / NULL OBJECT: at c = 1 the substituted parameters must reproduce the
    # CenteredBinomial baseline EXACTLY, including the two Sage-archived values.
    kac_ref = {"Kyber512": 140.1994731076207, "Kyber768": 200.9587149140538}
    c1 = []
    for name, p in SETS:
        native = arm_a(primal_bdd, RC, p, p.n)
        null = arm_a(primal_bdd, RC, scaled_params(ND, p, 1.0), p.n)
        row = {
            "set": name,
            "native_centered_binomial": native,
            "substituted_gaussian_c_equals_1": null,
            "identical": native == null,
            "log2_rop_delta": null["log2_rop"] - native["log2_rop"],
            "sage_archived_reference": kac_ref.get(name),
            "delta_vs_sage_archived_reference": (
                None if name not in kac_ref else abs(native["log2_rop"] - kac_ref[name])),
        }
        c1.append(row)
    controls["C1_null_object_and_baseline_fidelity"] = {
        "what": ("The null object: the identical measurement with the parameter that is meant "
                 "to produce the signal set to NO CHANGE (c = 1), through the identical "
                 "code path including the DiscreteGaussian substitution. Every delta must be "
                 "exactly 0, and the baseline must still equal the Sage-archived value."),
        "pass": all(r["identical"] and (r["delta_vs_sage_archived_reference"] in (None, 0.0))
                    for r in c1),
        "rows": c1,
    }

    # C2: cost_zeta(optimize_d=True) must reproduce primal_bdd bit-for-bit,
    # which is what licenses Arm B to be called the same path minus step 2.
    c2 = []
    for name, p in SETS:
        a = arm_a(primal_bdd, RC, p, p.n)
        via_cost_zeta, _b, m_allowed = arm_b(PrimalHybrid, LWEParameters, RC, p, p.n)
        c2.append({"set": name, "primal_bdd": a, "cost_zeta_optimize_d_True": via_cost_zeta,
                   "identical": a == via_cost_zeta, "m_allowed_bai_galbraith": m_allowed})
    controls["C2_arm_b_path_equivalence"] = {
        "what": "Arm B's entry point reproduces the public entry point when step 2 is left on.",
        "pass": all(r["identical"] for r in c2), "rows": c2,
    }

    # C3 SIGN CONTROL: make the norm WORSE (c > 1); beta must not fall.
    c3 = []
    for name, p in SETS:
        base = arm_a(primal_bdd, RC, scaled_params(ND, p, 1.0), p.n)
        for c in SIGN_CONTROL_C:
            s = arm_a(primal_bdd, RC, scaled_params(ND, p, c), p.n)
            c3.append({"set": name, "c": c, "delta_beta": s["beta"] - base["beta"],
                       "delta_log2_rop_matzov": s["log2_rop"] - base["log2_rop"],
                       "beta_did_not_fall": s["beta"] >= base["beta"],
                       "cost_did_not_fall": s["log2_rop"] >= base["log2_rop"]})
    controls["C3_sign_control"] = {
        "what": ("The artifact tell: a quantity that does not respond correctly when the "
                 "parameter meant to drive it is reversed. Enlarging the target norm must not "
                 "reduce beta or cost."),
        "pass": all(r["beta_did_not_fall"] and r["cost_did_not_fall"] for r in c3),
        "rows": c3,
    }
    res["controls"] = controls
    print(f"[{elapsed():7.1f}s] controls done: "
          f"{ {k: v['pass'] for k, v in controls.items()} }")

    # ---- the finite-difference table (ARM A) -----------------------------
    baselines, table, tableB = {}, [], []
    for name, p in SETS:
        base = arm_a(primal_bdd, RC, scaled_params(ND, p, 1.0), p.n)
        baseA, baseB, _m = arm_b(PrimalHybrid, LWEParameters, RC, scaled_params(ND, p, 1.0), p.n)
        delta_b = float(deltaf(base["beta"]))
        baselines[name] = {
            "n": int(p.n), "q": int(p.q),
            "stddev_Xs": float(p.Xs.stddev), "stddev_Xe": float(p.Xe.stddev),
            "arm_a": base, "arm_b_d_not_reoptimised": baseB,
            "d_reoptimisation_worth_bits_at_baseline": baseB["log2_rop"] - base["log2_rop"],
            "delta_root_hermite_at_baseline_beta": delta_b,
            "ln_delta": math.log(delta_b),
        }
        for c in C_VALUES:
            sp = scaled_params(ND, p, c)
            row = diff(base, arm_a(primal_bdd, RC, sp, p.n), c)
            row["set"] = name
            table.append(row)
            _a, b_, _m = arm_b(PrimalHybrid, LWEParameters, RC, sp, p.n)
            rowB = diff(baseB, b_, c)
            rowB["set"] = name
            tableB.append(rowB)
        print(f"[{elapsed():7.1f}s] {name} table done")

    res["baselines"] = baselines
    res["finite_difference_table"] = {
        "label": "INSTRUMENT OUTPUT -- recordable.",
        "definition": "delta_beta_fd = beta*(c) - beta*(1) from primal_bdd/RC.MATZOV, m re-optimised",
        "units": {"delta_beta_fd": "BKZ blocks (integer)",
                  "bits_0292_x_delta_beta_fd": "bits, using the card's 0.292 constant",
                  "delta_log2_rop_matzov": "bits, the estimator's OWN cost delta under RC.MATZOV"},
        "all_numbers_are": "MODELLED cost-model estimates, not measurements",
        "rows": table,
    }
    res["arm_b_d_not_reoptimised"] = {
        "label": "CONTROL ARM -- isolates the contribution of re-optimising m.",
        "rows": tableB,
    }

    # ---- the staircase ---------------------------------------------------
    scan = {}
    for name, p in SETS:
        base = arm_a(primal_bdd, RC, scaled_params(ND, p, 1.0), p.n)
        pts = []
        for k in range(SCAN_K_MIN, SCAN_K_MAX + 1):
            if elapsed() > SOFT_ABORT_S:
                scan.setdefault("truncated", []).append(
                    {"set": name, "stopped_at_k": k,
                     "reason": "soft wall-clock guard; partial scan recorded, not discarded"})
                break
            c = k / SCAN_DEN
            s = arm_a(primal_bdd, RC, scaled_params(ND, p, c), p.n)
            pts.append({"c": c, "beta": s["beta"], "delta_beta_fd": s["beta"] - base["beta"],
                        "d": s["d"], "m_used": s["m_used"], "eta": s["eta"],
                        "log2_rop": s["log2_rop"],
                        "delta_log2_rop_matzov": s["log2_rop"] - base["log2_rop"]})
        # monotone-decay check: |delta_beta| must go to 0 as c -> 1
        near = [q for q in pts if q["c"] >= 0.995]
        far = [q for q in pts if q["c"] <= 0.91]
        scan[name] = {
            "points": pts,
            # a larger norm ratio is a HARDER instance, so beta*(c) should be
            # non-decreasing in c. Whether it is, is an observation.
            "beta_nondecreasing_in_c": all(pts[i]["beta"] <= pts[i + 1]["beta"]
                                           for i in range(len(pts) - 1)),
            "decay_check_max_abs_delta_beta_c_ge_0p995": max((abs(q["delta_beta_fd"]) for q in near),
                                                            default=None),
            "decay_check_max_abs_delta_beta_c_le_0p91": max((abs(q["delta_beta_fd"]) for q in far),
                                                            default=None),
        }
        print(f"[{elapsed():7.1f}s] {name} scan done ({len(pts)} points)")

    # non-monotonicity of beta*(c), reported as observed
    for name in list(scan.keys()):
        if name in ("truncated",):
            continue
        pts = scan[name]["points"]
        if len(pts) < 2:
            scan[name]["summary_skipped"] = "fewer than two scan points recorded"
            continue
        inv = [{"c_lo": pts[i]["c"], "c_hi": pts[i + 1]["c"],
                "beta_lo": pts[i]["beta"], "beta_hi": pts[i + 1]["beta"]}
               for i in range(len(pts) - 1) if pts[i + 1]["beta"] > pts[i]["beta"]]
        scan[name]["beta_increases_as_c_increases_count"] = len(inv)
        scan[name]["beta_non_monotone_in_c_count"] = sum(
            1 for i in range(len(pts) - 1) if pts[i + 1]["beta"] < pts[i]["beta"])
        scan[name]["non_monotone_pairs_beta_rises_when_norm_grows"] = inv
        b = [q["beta"] for q in pts]
        scan[name]["beta_range_over_scan"] = [min(b), max(b)]
        d_ = [q["d"] for q in pts]
        scan[name]["d_range_over_scan"] = [min(d_), max(d_)]
        # secant slope over the whole window: quantisation-free readout of the
        # optimiser's sensitivity, still a finite difference (no linearisation).
        lo, hi = pts[0], pts[-1]
        dlnc = math.log(hi["c"]) - math.log(lo["c"])
        scan[name]["secant_dbeta_per_dlnc_over_scan_window"] = (hi["beta"] - lo["beta"]) / dlnc
        scan[name]["secant_dlog2rop_per_dbeta_over_scan_window"] = (
            None if hi["beta"] == lo["beta"]
            else (hi["log2_rop"] - lo["log2_rop"]) / (hi["beta"] - lo["beta"]))
    res["scan_staircase"] = {
        "label": "INSTRUMENT OUTPUT -- recordable.",
        "what": ("beta*(c) on the grid c = k/400, k = 360..400. Exposes the integer staircase "
                 "and any non-monotonicity of the optimiser's selection, both of which the "
                 "linearisation cannot represent."),
        "by_set": scan,
    }

    # ---- DESIGN AUDIT ----------------------------------------------------
    audit_rows = []
    for r in table:
        name = r["set"]
        lnd = baselines[name]["ln_delta"]
        lin = r["ln_c"] / (2.0 * lnd)
        audit_rows.append({
            "set": name, "c": r["c"],
            "delta_beta_linearised": lin,
            "bits_0292_x_delta_beta_linearised": BITS_PER_BLOCK_CARD * lin,
            "delta_beta_fd_arm_a": r["delta_beta_fd"],
            "difference_fd_minus_lin": r["delta_beta_fd"] - lin,
            "bits_difference_0292": BITS_PER_BLOCK_CARD * (r["delta_beta_fd"] - lin),
        })
    a_priori = []
    for b in (30, 40, 60, 100, 200, 389, 606, 855):
        dl = math.log(float(deltaf(b)))
        a_priori.append({"beta": b, "delta": float(deltaf(b)), "ln_delta": dl,
                         "omitted_over_retained_1_over_4beta_lndelta": 1.0 / (4.0 * b * dl)})
    res["design_audit_NOT_A_FINDING"] = {
        "LABEL": "DESIGN AUDIT, NOT A FINDING.",
        "binding_statement": (
            "The ratio of the omitted to the retained denominator term in "
            "dbeta = ln c / (2 ln delta) is 1/(4 beta ln delta): a function of beta ALONE, "
            "with sign and magnitude FIXED A PRIORI. It is derivable before running anything. "
            "NO NUMBER IN THIS BLOCK MAY ENTER AN EVIDENCE RECORD OR A KNOWLEDGE ENTRY. "
            "Presenting a forced quantity as a result is the failure that cost the two "
            "predecessor campaigns eighteen batches."),
        "derivation_of_the_forced_ratio": (
            "Writing the 2016-estimate success condition as f(beta) = (2 beta - d - 1) ln delta "
            "+ (m/d) ln q - ln||v|| - (1/2) ln(beta/d) = 0 and perturbing ||v|| -> c||v||, the "
            "compensating shift is dbeta = ln c / f'(beta) with f'(beta) = 2 ln delta "
            "- 1/(2 beta) + (2 beta - d - 1) (d/dbeta) ln delta. The linearisation keeps only "
            "2 ln delta; the -1/(2 beta) term it drops stands to it in ratio "
            "(1/(2 beta))/(2 ln delta) = 1/(4 beta ln delta). Nothing is measured by writing "
            "this down."),
        "a_priori_ratio_by_beta": a_priori,
        "cellwise_comparison": audit_rows,
        "why_the_cellwise_comparison_is_also_not_a_finding": (
            "delta_beta_fd is integer-valued and carries the optimiser's selection noise "
            "(see scan_staircase), while delta_beta_linearised is real-valued. Their "
            "difference at |delta_beta| of order 1-3 is dominated by quantisation, not by the "
            "dropped terms. It is reported because it was computed, not because it supports "
            "anything."),
    }

    # ---- toy-shape arm ---------------------------------------------------
    from estimator.lwe_parameters import LWEParameters as LP
    toys = [("toy_n100_q3329_sigma1", LP(n=100, q=3329, Xs=ND.DiscreteGaussian(1.0),
                                         Xe=ND.DiscreteGaussian(1.0), m=100, tag="toy100")),
            ("toy_n200_q3329_sigma1", LP(n=200, q=3329, Xs=ND.DiscreteGaussian(1.0),
                                         Xe=ND.DiscreteGaussian(1.0), m=200, tag="toy200"))]
    toy_out = []
    for name, p in toys:
        base = arm_a(primal_bdd, RC, scaled_params(ND, p, 1.0), p.n)
        lnd = math.log(float(deltaf(base["beta"])))
        rows = []
        for c in C_VALUES:
            r = diff(base, arm_a(primal_bdd, RC, scaled_params(ND, p, c), p.n), c)
            r["delta_beta_linearised"] = r["ln_c"] / (2.0 * lnd)
            r["difference_fd_minus_lin"] = r["delta_beta_fd"] - r["delta_beta_linearised"]
            rows.append(r)
        toy_out.append({"set": name, "n": int(p.n), "baseline": base,
                        "ln_delta": lnd,
                        "a_priori_ratio_1_over_4beta_lndelta": 1.0 / (4.0 * base["beta"] * lnd),
                        "rows": rows})
    res["toy_shape_arm_NOT_CRYPTO_SCALE"] = {
        "LABEL": ("Instrument characterisation of the CONVERSION at small beta. NOT crypto-scale "
                  "evidence. Must not be transported to beta = 606 / d = 1420; the task card "
                  "forbids it explicitly."),
        "what": "The identical finite difference at optimiser-selected beta of order 40 and 90.",
        "sets": toy_out,
    }

    # ---- anomalies, budget ----------------------------------------------
    res["anomalies"] = [
        {"id": "A1",
         "class": "instrument behaviour (upstream lattice-estimator, not the shim)",
         "what": ("primal_bdd(params, optimize_d=False) SILENTLY IGNORES the kwarg and returns "
                  "the fully d-optimised answer. primal_hybrid.__call__ builds "
                  "f = partial(self.cost_zeta, ...) without **kwds, and the explicit-zeta branch "
                  "(the one primal_bdd takes, zeta=0) calls f(zeta=zeta), so every extra kwarg is "
                  "dropped without warning."),
         "evidence": ("Kyber512: primal_bdd(..., optimize_d=False) returned log2rop "
                      "140.1994731076207, beta 389, d 1005 -- identical to the default call -- "
                      "while cost_zeta(..., optimize_d=False) returns 140.2082434547, d 1013."),
         "consequence": ("Anyone controlling the estimator through primal_bdd kwargs may believe "
                         "they disabled something they did not. Arm B here calls cost_zeta "
                         "directly and control C2 verifies the equivalence."),
         "shim_change_needed": False,
         "action_taken": "recorded; tools/sage_free_estimator was NOT edited (task card)"},
    ]
    res["budget"] = {
        "wall_clock_seconds_budget": WALL_CLOCK_BUDGET_S,
        "wall_clock_seconds_used": round(elapsed(), 3),
        "within_wall_clock_budget": elapsed() <= WALL_CLOCK_BUDGET_S,
        "memory_gb_budget": 4,
        "peak_rss_gb_measured": round(peak_rss_gb(), 4),
        "maximum_runs_budget": 1,
        "estimator_optimiser_calls_this_run": dict(CALLS),
        "note": ("The estimator memoises cost/beta_params per parameter object "
                 "(@cached_function), so repeated calls at an identical c are served from "
                 "cache; the counts are calls made, not distinct optimisations."),
    }

    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=2)
    print(f"[{elapsed():7.1f}s] wrote {OUT}  peak RSS {peak_rss_gb():.3f} GB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
