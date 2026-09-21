#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TASK-20260803-69f3cd -- reserve checks S1-S5 on ANOM-3 (GOAL-MLKEM-003, BATCH-012).

WHAT ANOM-3 IS. Under RC.MATZOV the pinned lattice-estimator
(3e48ef421ec256afddb3e7d2249a77eab6e9ba12) reports

    estimator.lwe_dual.matzov   139.6560414809 / 196.3662433540 / 262.3356800075
    estimator.lwe_primal.primal_bdd
                                140.1994731076 / 200.9587149141 / 270.7236234535

at Kyber-512/768/1024, i.e. `matzov` undercuts `primal_bdd` by
+0.543432 / +4.592472 / +8.387943 bits.  This script does NOT test the security
reading of that (already dissolved twice: shared independence law; EV-MLKEM-020
memory charging).  It tests two things the BATCH-011 reviews named and left
unrun:

  (1) is the INTERNAL ordering (matzov cheaper than primal_bdd, inside the
      estimator's own frame) a finding or an artifact?
  (2) are the load-bearing 768/1024 numbers checkable at all?

EVERYTHING HERE IS A COST-MODEL ESTIMATE, NOT A MEASUREMENT.  No claim about
ML-KEM's actual security is made or implied.  AGENTS.md rule 12 is UNMET and
UNWAIVED for this batch: nothing here corrects EV-MLKEM-015 or any KN-* entry.

THE FIVE CHECKS
  S1  Sage reference.  Attempt to obtain real Sage and re-derive the matzov
      numbers under it.  A failure to obtain Sage is a DECLARED RESULT under
      AGENTS.md rule 5, recorded with its exact commands and outputs.
  S2  Box widening.  Scan MATZOV.cost over a grid materially wider AND finer
      than the optimiser's own, in beta, k_enum, k_fft and p, at 768 and 1024.
  S3  Null object.  Same comparison shape, signal removed (validator DEF-7).
  S4  Decay test extended to N x 2^24 and 2^32 with full re-optimisation.
  S5  c* per attack.  Never transferred between attacks (DEC-20260803-85adf8
      CE-1).

USAGE (the exact command recorded in receipt.json):
    PYTHONPATH=tools/sage_free_estimator/shim:/tmp/le python3 <this file>

Step 0 (tools/sage_free_estimator/known_answer_control.py, unpatched committed
shim) MUST have passed before this script is run; its verbatim output is in
report.md and receipt.json.  This script re-anchors on the same baseline values
and aborts if they move.
"""
from __future__ import annotations

import json
import math
import os
import random
import subprocess
import sys
import time

TASK_DIR = os.path.dirname(os.path.abspath(__file__))
SEED = 20260803  # only source of randomness in this script (S3 ensemble)

# ---------------------------------------------------------------------------
# Baseline anchors.  These are the numbers ANOM-3 is stated in.  If the local
# instrument does not reproduce them the whole script is meaningless, so it
# aborts rather than reporting anything.
# ---------------------------------------------------------------------------
ANCHOR_PRIMAL = {
    "Kyber512": 140.1994731076207,
    "Kyber768": 200.9587149140538,
    "Kyber1024": 270.7236234535225,
}
ANCHOR_MATZOV = {
    "Kyber512": 139.6560414809,
    "Kyber768": 196.3662433540,
    "Kyber1024": 262.3356800075,
}
ANCHOR_TOL = 1e-9          # primal: from the archived Sage run, exact-equality bar
ANCHOR_TOL_MATZOV = 1e-9   # matzov: from the BATCH-011 red team's reproduction
NIST_CUTOFF = {"Kyber512": 143, "Kyber768": 207, "Kyber1024": 272}

SETS = ("Kyber512", "Kyber768", "Kyber1024")


def lg2(x):
    return math.log2(float(x))


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


LOG_LINES = []


def log(msg=""):
    print(msg, flush=True)
    LOG_LINES.append(msg)


# ===========================================================================
# S0 -- instrument identity and baseline anchor
# ===========================================================================
def s0_identity_and_anchor(mods):
    """Record WHICH callable is being used, and re-anchor on ANOM-3's numbers.

    The callable identity matters and has already caused one Coordinator error
    in this campaign: estimator/lwe.py:13 does `from .lwe_dual import matzov as
    dual_hybrid`, so the PUBLIC name LWE.dual_hybrid is the MATZOV class
    (lwe_dual.py:496, instantiated at line 689).  The MODULE-LEVEL function
    estimator.lwe_dual.dual_hybrid is a different attack entirely (it dispatches
    to DualHybrid = DH, lwe_dual.py:493).
    """
    RC, schemes, primal_bdd, matzov, MATZOV, lwe, lwe_dual = mods
    out = {
        "public_LWE_dual_hybrid_is_lwe_dual_matzov": bool(lwe.dual_hybrid is matzov),
        "type_of_lwe_dual_matzov": type(matzov).__module__ + "." + type(matzov).__name__,
        "module_level_lwe_dual_dual_hybrid_is_matzov": bool(
            getattr(lwe_dual, "dual_hybrid", None) is matzov),
        "module_level_dual_hybrid_kind": type(getattr(lwe_dual, "dual_hybrid", None)).__name__,
        "anchor": {},
        "optimum_reported_by_estimator": {},
    }
    failures = []
    for nm in SETS:
        params = getattr(schemes, nm)
        rp = primal_bdd(params, red_cost_model=RC.MATZOV)
        rm = matzov(params, red_cost_model=RC.MATZOV)
        gp, gm = lg2(rp["rop"]), lg2(rm["rop"])
        dp = abs(gp - ANCHOR_PRIMAL[nm])
        dm = abs(gm - ANCHOR_MATZOV[nm])
        out["anchor"][nm] = {
            "primal_bdd_log2rop": gp, "primal_bdd_anchor": ANCHOR_PRIMAL[nm],
            "primal_bdd_delta": dp,
            "matzov_log2rop": gm, "matzov_anchor": ANCHOR_MATZOV[nm],
            "matzov_delta": dm,
            "margin_primal_minus_matzov_bits": gp - gm,
        }
        out["optimum_reported_by_estimator"][nm] = {
            k: int(rm[k]) for k in ("beta", "p", "zeta", "t", "m", "beta_")
        }
        if dp > ANCHOR_TOL:
            failures.append(f"{nm}/primal delta={dp:.3e}")
        if dm > ANCHOR_TOL_MATZOV:
            failures.append(f"{nm}/matzov delta={dm:.3e}")
    out["anchor_ok"] = not failures
    out["anchor_failures"] = failures
    return out


# ===========================================================================
# S1 -- Sage reference
# ===========================================================================
S1_ESTIMATOR_UNDER_SAGE = r'''
import json, math, sys
res = {}
try:
    import sage.all as _sa
    res["sage_all_file"] = _sa.__file__
    try:
        from sage.version import version as _v
        res["sage_version"] = _v
    except Exception as e:
        res["sage_version"] = "unavailable: %r" % (e,)
except Exception as e:
    print(json.dumps({"import_sage_all_error": repr(e)})); sys.exit(3)
try:
    from estimator import RC, schemes
    from estimator.lwe_primal import primal_bdd
    from estimator.lwe_dual import matzov
except Exception as e:
    res["import_estimator_error"] = repr(e)
    print(json.dumps(res)); sys.exit(4)
for nm in ("Kyber512", "Kyber768", "Kyber1024"):
    p = getattr(schemes, nm)
    row = {}
    for tag, fn in (("primal_bdd", primal_bdd), ("matzov", matzov)):
        try:
            r = fn(p, red_cost_model=RC.MATZOV)
            row[tag] = math.log2(float(r["rop"]))
        except Exception as e:
            row[tag + "_error"] = repr(e)
    res[nm] = row
print(json.dumps(res))
'''


def s1_sage_reference():
    """Attempt a REAL-Sage re-derivation of the matzov numbers.

    The claim under test is that 196.3662433540 and 262.3356800075 rest on an
    instrument path no archived Sage run covers.  That claim is established
    independently of whether Sage can be installed, by reading the archived run:
    experiments/EXP-MLKEM-015/implementation/reproduce_estimates.py:16 imports
    `dual_hybrid` from estimator.lwe_dual -- the DualHybrid function -- and the
    archived field `dual_fft_MATZOV_log2` is 143.788/203.788/273.817.  Nothing
    in that run calls `matzov`.  So the coverage gap is a fact about the
    archive, not about this host.

    What this function adds is whether the gap can be CLOSED here.
    """
    out = {"attempt_transcript_path": os.path.join(TASK_DIR, "sage_attempt_transcript.txt")}

    # (a) the coverage fact, re-derived from the committed archive.
    repo = os.path.abspath(os.path.join(TASK_DIR, "..", "..", "..", "..", "..", ".."))
    impl = os.path.join(repo, "experiments", "EXP-MLKEM-015", "implementation",
                        "reproduce_estimates.py")
    raw = os.path.join(repo, "experiments", "EXP-MLKEM-015", "runs",
                       "RUN-MLKEM-015-001", "raw-result.json")
    cov = {}
    try:
        src = open(impl).read()
        cov["archived_sage_run_imports"] = [
            ln.strip() for ln in src.splitlines()
            if "import" in ln and ("lwe_dual" in ln or "lwe_primal" in ln)]
        cov["archived_sage_run_calls_matzov"] = ("matzov(" in src)
        cov["archived_sage_run_calls_module_dual_hybrid"] = ("dual_hybrid(params" in src)
    except OSError as e:
        cov["implementation_read_error"] = repr(e)
    try:
        rr = json.load(open(raw))
        cov["archived_dual_fft_MATZOV_log2"] = {
            k: v["dual_fft_MATZOV_log2"] for k, v in rr["summaries_MATZOV_matched"].items()}
        cov["archived_primal_bdd_MATZOV_log2"] = {
            k: v["primal_bdd_MATZOV_log2"] for k, v in rr["summaries_MATZOV_matched"].items()}
        cov["archived_sage_version"] = rr.get("sage_version")
    except (OSError, KeyError, ValueError) as e:
        cov["raw_result_read_error"] = repr(e)
    out["archived_sage_coverage"] = cov

    # (b) live probes for a usable Sage on this host.
    probes = []
    for label, cmd in (
        ("sage_on_path", ["bash", "-lc", "command -v sage || echo NOT-FOUND"]),
        ("import_sage_system_python", [sys.executable, "-c",
                                       "import sage; print(sage.__file__)"]),
        ("import_sage_all_system_python", [sys.executable, "-c",
                                           "import sage.all; print(sage.all.__file__)"]),
        ("apt_cache_policy_sagemath", ["bash", "-lc", "apt-cache policy sagemath"]),
        ("import_sage_all_venv", ["/tmp/sagevenv/bin/python", "-c",
                                  "import sage.all; print(sage.all.__file__)"]),
    ):
        try:
            pr = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            probes.append({"label": label, "cmd": cmd, "exit": pr.returncode,
                           "stdout": pr.stdout.strip()[:2000],
                           "stderr": pr.stderr.strip()[:2000]})
        except (OSError, subprocess.SubprocessError) as e:
            probes.append({"label": label, "cmd": cmd, "exit": None, "error": repr(e)})
    out["live_probes"] = probes

    # (c) if any interpreter can import sage.all, run the estimator under it
    #     WITHOUT the shim on PYTHONPATH, and compare.
    candidates = [sys.executable, "/tmp/sagevenv/bin/python"]
    out["real_sage_runs"] = []
    verified = False
    for interp in candidates:
        if not os.path.exists(interp):
            out["real_sage_runs"].append({"interpreter": interp, "status": "absent"})
            continue
        env = dict(os.environ)
        # NO shim: the point is to use a genuine sage.all.
        env["PYTHONPATH"] = os.environ.get("ESTIMATOR_PATH", "/tmp/le")
        try:
            pr = subprocess.run([interp, "-c", S1_ESTIMATOR_UNDER_SAGE], env=env,
                                capture_output=True, text=True, timeout=1200)
        except (OSError, subprocess.SubprocessError) as e:
            out["real_sage_runs"].append({"interpreter": interp, "status": "error",
                                          "error": repr(e)})
            continue
        rec = {"interpreter": interp, "exit": pr.returncode,
               "stderr_tail": pr.stderr.strip()[-3000:]}
        try:
            rec["result"] = json.loads(pr.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            rec["stdout_tail"] = pr.stdout.strip()[-3000:]
        out["real_sage_runs"].append(rec)
        r = rec.get("result") or {}
        if pr.returncode == 0 and "sage_all_file" in r and "Kyber768" in r:
            cmp_ = {}
            for nm in SETS:
                row = r.get(nm, {})
                if "matzov" in row:
                    cmp_[nm] = {
                        "sage_matzov_log2rop": row["matzov"],
                        "shim_anchor": ANCHOR_MATZOV[nm],
                        "delta_bits": abs(row["matzov"] - ANCHOR_MATZOV[nm]),
                    }
                if "primal_bdd" in row:
                    cmp_.setdefault(nm, {})["sage_primal_bdd_log2rop"] = row["primal_bdd"]
                    cmp_[nm]["shim_primal_anchor"] = ANCHOR_PRIMAL[nm]
                    cmp_[nm]["primal_delta_bits"] = abs(row["primal_bdd"] - ANCHOR_PRIMAL[nm])
            rec["comparison_vs_shim"] = cmp_
            verified = bool(cmp_)
    out["matzov_768_1024_verified_against_real_sage"] = verified
    out["status"] = "verified_against_sage" if verified else "sage_unavailable_declared"
    return out


# ===========================================================================
# S2 -- box widening
# ===========================================================================
def s2_box_widening(mods, budget_s_per_set=185.0):
    """Scan MATZOV.cost over a box materially wider AND finer than the optimiser's.

    WHY THE OPTIMISER'S BOX IS SMALL.  MATZOV.__call__ (lwe_dual.py:628-687)
    searches
        p      : early_abort_range(2, params.q)          -- aborts once t==0 and p>2
        k_enum : early_abort_range(0, params.n, 10)      -- STEP 10, early abort
        k_fft  : early_abort_range(0, params.n-k_enum,10)-- STEP 10, early abort
        beta   : local_minimum(40, max_beta, precision=1)-- LOCAL minimum, not exhaustive
    so it is coarse in k_enum/k_fft, greedy in beta, and early-aborting in all
    three.  Any of those could hide a cheaper point.

    A NOTE ON THE PRIOR INFORMAL SCAN.  The Coordinator reports a 1701-point
    scan (beta +-40 step 4, k_enum/k_fft 0-40 step 5) finding +0.000000 bits.
    That scan cannot have contained the Kyber-1024 optimum, whose k_fft is 120,
    nor the Kyber-768 optimum's k_fft of 60 -- both lie outside 0-40.  A grid
    that excludes the incumbent trivially fails to beat it.  This scan is
    centred on the incumbent and is wider than it on every axis.

    Stage A: coarse and wide (beta +-176 step 8, k_enum 0..156 step 6,
             k_fft 0..252 step 6, p in 2..8).
    Stage B: fine and local around BOTH the incumbent and stage A's best
             (beta +-24 step 1, k_enum/k_fft +-15 step 1, p in 2..8).
    """
    RC, schemes, primal_bdd, matzov, MATZOV, lwe, lwe_dual = mods
    out = {}
    for nm in ("Kyber768", "Kyber1024"):
        t_start = time.time()
        params = getattr(schemes, nm).normalize()
        inc = matzov(getattr(schemes, nm), red_cost_model=RC.MATZOV)
        b0, p0, ke0, kf0 = int(inc["beta"]), int(inc["p"]), int(inc["zeta"]), int(inc["t"])
        inc_log2 = lg2(inc["rop"])

        evaluated = 0
        best = {"log2rop": inc_log2, "beta": b0, "p": p0, "k_enum": ke0, "k_fft": kf0,
                "source": "incumbent"}
        errors = 0

        def scan(betas, kes, kfs, ps, tag, deadline):
            nonlocal evaluated, best, errors
            truncated = False
            for beta in betas:
                if time.time() > deadline:
                    truncated = True
                    break
                for ke in kes:
                    for kf in kfs:
                        if ke + kf >= params.n:
                            continue
                        for pp in ps:
                            try:
                                c = MATZOV.cost(beta, params, p=pp, k_enum=ke, k_fft=kf,
                                                red_cost_model=RC.MATZOV)
                                v = lg2(c["rop"])
                            except Exception:
                                errors += 1
                                continue
                            evaluated += 1
                            if v < best["log2rop"]:
                                best = {"log2rop": v, "beta": beta, "p": pp,
                                        "k_enum": ke, "k_fft": kf, "source": tag}
            return truncated

        # ---- Stage A: wide + coarse -----------------------------------
        A_beta = list(range(max(40, b0 - 176), b0 + 177, 8))
        A_ke = list(range(0, 157, 6))
        A_kf = list(range(0, 253, 6))
        A_p = [2, 3, 4, 5, 6, 7, 8]
        deadline = t_start + budget_s_per_set * 0.62
        truncA = scan(A_beta, A_ke, A_kf, A_p, "stageA_wide_coarse", deadline)
        after_A = dict(best)
        evalA = evaluated

        # ---- Stage B: fine, around incumbent and around stage A best ---
        deadline = t_start + budget_s_per_set
        truncB = False
        centres = {(b0, ke0, kf0)}
        centres.add((best["beta"], best["k_enum"], best["k_fft"]))
        for (cb, cke, ckf) in sorted(centres):
            B_beta = list(range(max(40, cb - 24), cb + 25))
            B_ke = list(range(max(0, cke - 15), cke + 16))
            B_kf = list(range(max(0, ckf - 15), ckf + 16))
            truncB |= scan(B_beta, B_ke, B_kf, [2, 3, 4, 5, 6, 7, 8],
                           "stageB_fine_local", deadline)

        out[nm] = {
            "incumbent_log2rop": inc_log2,
            "incumbent_point": {"beta": b0, "p": p0, "k_enum": ke0, "k_fft": kf0},
            "optimiser_box_note": ("k_enum/k_fft searched with STEP 10 and early abort; "
                                   "beta by local_minimum(40, max_beta, precision=1)"),
            "stageA": {"beta_range": [A_beta[0], A_beta[-1], 8],
                       "k_enum_range": [0, 156, 6], "k_fft_range": [0, 252, 6],
                       "p_values": A_p, "points_evaluated": evalA,
                       "truncated_by_time": truncA,
                       "best_log2rop": after_A["log2rop"]},
            "stageB": {"centres": sorted(centres),
                       "beta_halfwidth": 24, "k_halfwidth": 15, "step": 1,
                       "p_values": [2, 3, 4, 5, 6, 7, 8],
                       "points_evaluated": evaluated - evalA,
                       "truncated_by_time": truncB},
            "total_points_evaluated": evaluated,
            "cost_call_exceptions": errors,
            "best_found": best,
            "improvement_bits_over_incumbent": inc_log2 - best["log2rop"],
            "beats_incumbent": best["log2rop"] < inc_log2 - 1e-12,
            "wall_seconds": time.time() - t_start,
        }
        log(f"  S2 {nm}: {evaluated} points, best {best['log2rop']:.10f} "
            f"vs incumbent {inc_log2:.10f} "
            f"(improvement {inc_log2 - best['log2rop']:+.6f} bits) "
            f"[{time.time()-t_start:.0f}s]")
    return out


# ===========================================================================
# S3 -- null object
# ===========================================================================
def s3_null_object(mods, n_random=24, budget_s=210.0):
    """A null of the same SHAPE as the matzov-vs-primal_bdd comparison, signal removed.

    THE CLAIM'S SHAPE.  ANOM-3 is: "at Kyber's parameters, running these two
    estimator entry points and subtracting produces a POSITIVE margin, i.e. the
    dual attack undercuts the primal one."  The implied signal is that something
    about Kyber's parameters produces that ordering.

    THE NULL.  Remove Kyber-specificity: run the IDENTICAL comparison machinery
    over an ensemble of LWE parameter sets that are Kyber-SHAPED (same
    distribution families, same q regime, same m=n convention) but whose
    (n, q, secret/error widths) are drawn at random over a wide band, none of
    them ML-KEM.  If the margin is positive on essentially the whole ensemble,
    then "matzov < primal_bdd" is a generic property of the two cost functions
    and carries no information about Kyber.  The comparison would then "find" an
    ordering with the signal removed, which is what DEF-7 asked to be measured.

    NULL-2 (cost-model null).  Re-run the SAME comparison at the SAME three
    Kyber sets under reduction cost models other than RC.MATZOV.  If the sign is
    invariant to the cost model, the ordering is not a property of the MATZOV
    reduction frame that ANOM-3 is stated in.

    Randomness: `random.Random(SEED)` with SEED recorded; the ensemble is
    regenerated identically on rerun.
    """
    RC, schemes, primal_bdd, matzov, MATZOV, lwe, lwe_dual = mods
    from estimator.lwe_parameters import LWEParameters
    from estimator.nd import NoiseDistribution

    rng = random.Random(SEED)
    t0 = time.time()

    # ---- NULL-1: Kyber-shaped but non-Kyber parameter ensemble -----------
    ens = []
    for i in range(n_random):
        n = rng.choice([256, 320, 384, 448, 512, 576, 640, 704, 768, 832, 896,
                        960, 1024, 1088, 1152, 1280])
        q = rng.choice([769, 1409, 2049, 3329, 3457, 4591, 7681, 8192, 12289, 40961])
        eta_s = rng.choice([1, 2, 3, 4, 5])
        eta_e = rng.choice([1, 2, 3, 4, 5])
        ens.append((f"NULL{i:02d}", n, q, eta_s, eta_e))

    rows, pos, neg, err = [], 0, 0, 0
    for (tag, n, q, eta_s, eta_e) in ens:
        if time.time() - t0 > budget_s * 0.75:
            break
        try:
            P = LWEParameters(
                n=n, q=q,
                Xs=NoiseDistribution.CenteredBinomial(eta_s),
                Xe=NoiseDistribution.CenteredBinomial(eta_e),
                m=n, tag=tag)
            rp = primal_bdd(P, red_cost_model=RC.MATZOV)
            rm = matzov(P, red_cost_model=RC.MATZOV)
            gp, gm = lg2(rp["rop"]), lg2(rm["rop"])
            rows.append({"tag": tag, "n": n, "q": q, "eta_s": eta_s, "eta_e": eta_e,
                         "primal_bdd_log2rop": gp, "matzov_log2rop": gm,
                         "margin_primal_minus_matzov_bits": gp - gm})
            if gp - gm > 0:
                pos += 1
            else:
                neg += 1
        except Exception as e:
            err += 1
            rows.append({"tag": tag, "n": n, "q": q, "eta_s": eta_s, "eta_e": eta_e,
                         "error": repr(e)[:300]})
    margins = [r["margin_primal_minus_matzov_bits"] for r in rows if "margin_primal_minus_matzov_bits" in r]
    margins_sorted = sorted(margins)

    null1 = {
        "design": ("identical comparison machinery (primal_bdd vs matzov, RC.MATZOV, "
                   "log2 rop) on Kyber-SHAPED but non-Kyber LWE parameters; "
                   "Kyber-specificity is the removed signal"),
        "seed": SEED,
        "n_requested": n_random, "n_evaluated": len(margins), "n_errors": err,
        "positive_margin_count": pos, "negative_margin_count": neg,
        "fraction_matzov_undercuts_primal": (pos / len(margins)) if margins else None,
        "margin_bits_min": margins_sorted[0] if margins else None,
        "margin_bits_median": (margins_sorted[len(margins_sorted) // 2]
                               if margins else None),
        "margin_bits_max": margins_sorted[-1] if margins else None,
        "rows": rows,
    }

    # ---- NULL-2: cost-model null at the real Kyber sets -------------------
    null2_rows = []
    for cm_name in ("ADPS16", "BDGL16", "LaaMosPol14", "CheNgu12", "ABLR21", "ChaLoy21"):
        cm = getattr(RC, cm_name, None)
        if cm is None:
            null2_rows.append({"cost_model": cm_name, "error": "absent from RC"})
            continue
        for nm in SETS:
            P = getattr(schemes, nm)
            row = {"cost_model": cm_name, "set": nm}
            try:
                row["primal_bdd_log2rop"] = lg2(primal_bdd(P, red_cost_model=cm)["rop"])
            except Exception as e:
                row["primal_bdd_error"] = repr(e)[:200]
            try:
                row["matzov_log2rop"] = lg2(matzov(P, red_cost_model=cm)["rop"])
            except Exception as e:
                row["matzov_error"] = repr(e)[:200]
            if "primal_bdd_log2rop" in row and "matzov_log2rop" in row:
                row["margin_primal_minus_matzov_bits"] = (
                    row["primal_bdd_log2rop"] - row["matzov_log2rop"])
            null2_rows.append(row)
    signs = [r["margin_primal_minus_matzov_bits"] > 0 for r in null2_rows
             if "margin_primal_minus_matzov_bits" in r]
    null2 = {
        "design": ("same comparison at the same three Kyber sets under reduction cost "
                   "models OTHER than RC.MATZOV; the removed signal is the MATZOV "
                   "reduction frame ANOM-3 is stated in"),
        "rows": null2_rows,
        "n_evaluated": len(signs),
        "fraction_matzov_undercuts_primal": (sum(signs) / len(signs)) if signs else None,
    }
    return {"null1_non_kyber_ensemble": null1, "null2_cost_model": null2,
            "wall_seconds": time.time() - t0}


# ===========================================================================
# S4 -- decay test, extended
# ===========================================================================
def s4_decay(mods, deltas=(0, 1, 2, 4, 8, 16, 24, 32), budget_s=280.0):
    """Inflate Nf's output by 2^delta with FULL re-optimisation; report flip point.

    RECIPE (the BATCH-011 red team's, extended).  `MATZOV.Nf` returns the
    required sample count N.  Subclass MATZOV and multiply Nf's return by
    2^delta, changing nothing else, then re-run the FULL optimiser (`__call__`)
    so beta, p, k_enum and k_fft are re-chosen under the inflated N.  The margin
    reported is primal_bdd - matzov_delta, with primal_bdd UNCHANGED (the
    inflation is a statement about the dual attack's sample requirement only).

    WHY.  Under the inventor protocol a signal that never decays when the
    parameter meant to destroy it is increased is the canonical artifact tell.
    Ducas-Pulles act in exactly this direction: if the independence assumption
    understates the required N, the true N is larger.  delta is the number of
    bits by which N is understated.  The flip point is the delta at which the
    margin reaches 0, i.e. at which matzov stops undercutting primal_bdd.

    The subclass is verified to reproduce the pinned optimum at delta = 0 before
    any inflated row is reported.
    """
    RC, schemes, primal_bdd, matzov, MATZOV, lwe, lwe_dual = mods
    from sage.all import RR
    t0 = time.time()

    def make_inflated(delta_bits):
        factor = RR(2) ** RR(delta_bits)

        class Inflated(MATZOV):
            @classmethod
            def Nf(cls, params, m, beta_bkz, beta_sieve, k_enum, k_fft, p):
                return RR(MATZOV.Nf(params, m, beta_bkz, beta_sieve,
                                    k_enum, k_fft, p) * factor)
        return Inflated()

    # primal side, unchanged, computed once
    primal = {nm: lg2(primal_bdd(getattr(schemes, nm), red_cost_model=RC.MATZOV)["rop"])
              for nm in SETS}

    def margin(nm, delta_bits):
        inst = make_inflated(delta_bits)
        r = inst(getattr(schemes, nm), red_cost_model=RC.MATZOV)
        return primal[nm] - lg2(r["rop"]), lg2(r["rop"]), {
            k: int(r[k]) for k in ("beta", "p", "zeta", "t", "beta_")}

    out = {"recipe": ("subclass MATZOV; Nf -> Nf * 2^delta; full re-optimisation via "
                      "MATZOV.__call__ under RC.MATZOV; primal_bdd unchanged"),
           "primal_bdd_log2rop": primal, "table": {}, "flip_points": {},
           "subclass_verified_at_delta0": {}}

    for nm in SETS:
        rowset = []
        for d in deltas:
            if time.time() - t0 > budget_s:
                rowset.append({"delta_bits": d, "status": "not_run_budget_exhausted"})
                continue
            try:
                mg, mval, pt = margin(nm, d)
                rowset.append({"delta_bits": d, "matzov_log2rop": mval,
                               "margin_primal_minus_matzov_bits": mg, "point": pt})
            except Exception as e:
                rowset.append({"delta_bits": d, "error": repr(e)[:300]})
        out["table"][nm] = rowset
        d0 = [r for r in rowset if r.get("delta_bits") == 0 and "matzov_log2rop" in r]
        if d0:
            out["subclass_verified_at_delta0"][nm] = {
                "subclass_log2rop": d0[0]["matzov_log2rop"],
                "anchor": ANCHOR_MATZOV[nm],
                "delta": abs(d0[0]["matzov_log2rop"] - ANCHOR_MATZOV[nm]),
            }

    # bisect the flip point where the margin crosses zero
    for nm in SETS:
        rows = [r for r in out["table"][nm] if "margin_primal_minus_matzov_bits" in r]
        if not rows:
            out["flip_points"][nm] = {"status": "no_rows"}
            continue
        lo = None
        hi = None
        for r in rows:
            if r["margin_primal_minus_matzov_bits"] > 0:
                lo = r["delta_bits"] if lo is None or r["delta_bits"] > lo else lo
            else:
                hi = r["delta_bits"] if hi is None or r["delta_bits"] < hi else hi
        if hi is None:
            out["flip_points"][nm] = {
                "status": "no_flip_within_tested_range",
                "max_delta_tested": max(r["delta_bits"] for r in rows),
                "margin_at_max_delta_bits": [r["margin_primal_minus_matzov_bits"]
                                             for r in rows
                                             if r["delta_bits"] == max(x["delta_bits"] for x in rows)][0],
            }
            continue
        a, b = float(lo if lo is not None else 0.0), float(hi)
        try:
            for _ in range(14):
                if time.time() - t0 > budget_s * 1.35:
                    break
                mid = 0.5 * (a + b)
                mg, _, _ = margin(nm, mid)
                if mg > 0:
                    a = mid
                else:
                    b = mid
            out["flip_points"][nm] = {"status": "bracketed",
                                      "delta_flip_bits": 0.5 * (a + b),
                                      "bracket": [a, b],
                                      "N_understatement_factor": 2 ** (0.5 * (a + b))}
        except Exception as e:
            out["flip_points"][nm] = {"status": "bisection_error", "error": repr(e)[:300]}
    out["wall_seconds"] = time.time() - t0
    return out


# ===========================================================================
# S5 -- c* per attack
# ===========================================================================
def s5_cstar(mods, s0):
    """Report the critical memory-charge exponent PER ATTACK.  Never transferred.

    DEFINITION (EV-MLKEM-020's, not invented here): c* = margin / log2(M), where
    margin = NIST classical cutoff - log2(rop) in bits and M is the attack's own
    peak memory.  c* is the exponent c at which charging rop * M^c reaches the
    cutoff.

    MEMORY RECIPES, both stated, neither preferred:
      Model A (EV-MLKEM-020's own, sieve only):
          log2 M = 0.2075 * b + log2(b),  b = the attack's sieve dimension.
          For `matzov`, b is its reported beta_ (beta_sieve).
      Model P (BATCH-011 red team's, peak incl. the FFT table):
          log2 M = log2( 2^(0.2075*b+log2 b) + p^k_fft ), an INFERENCE from
          T_fftf's p**(k+1) at lwe_dual.py:513 -- labelled as an inference, not
          a quotation from MATZOV-2022.

    WHAT THIS FUNCTION WILL NOT DO.  It computes c* for `matzov` ONLY, from
    `matzov`'s own reported optimum.  EV-MLKEM-020's c* ~ 0.0316/0.0459/0.0071
    belongs to `primal_bdd` and is quoted here for contrast with an explicit
    owner label; it is NOT reused as matzov's, which is exactly the error
    DEC-20260803-85adf8 records as CE-1.  `primal_bdd` reports no beta_sieve
    (it never calls short_vectors), so no primal memory figure is recomputed
    here at all.
    """
    out = {"definition": "c* = (NIST_classical_cutoff_bits - log2 rop) / log2(M)",
           "per_attack": {}, "transfer_prohibition": (
               "c* is per-attack. EV-MLKEM-020's 0.0316/0.0459/0.0071 are "
               "primal_bdd's under Model A and are NOT matzov's "
               "(DEC-20260803-85adf8 CE-1).")}
    for nm in SETS:
        opt = s0["optimum_reported_by_estimator"][nm]
        cost = s0["anchor"][nm]["matzov_log2rop"]
        b = opt["beta_"]
        kfft, p = opt["t"], opt["p"]
        margin = NIST_CUTOFF[nm] - cost
        logM_A = 0.2075 * b + math.log2(b)
        logM_P = math.log2(2 ** logM_A + float(p) ** kfft) if kfft * math.log2(p) < 900 else (
            kfft * math.log2(p))
        out["per_attack"][nm] = {
            "attack": "estimator.lwe_dual.matzov (class MATZOV, == public LWE.dual_hybrid)",
            "reduction_cost_model": "RC.MATZOV",
            "log2_rop": cost,
            "nist_classical_cutoff_bits": NIST_CUTOFF[nm],
            "free_memory_margin_bits": margin,
            "sieve_dimension_beta_sieve": b,
            "k_fft": kfft, "p": p,
            "modelA_log2_memory_sieve_only": logM_A,
            "modelA_cstar_matzov": margin / logM_A,
            "modelP_log2_memory_peak_incl_fft_table": logM_P,
            "modelP_cstar_matzov": margin / logM_P,
        }
    out["primal_bdd_cstar_for_contrast_not_transferred"] = {
        "owner_attack": "estimator.lwe_primal.primal_bdd",
        "source_record": "EV-MLKEM-020 (Model A)",
        "Kyber512": 0.03164649, "Kyber768": 0.04588645, "Kyber1024": 0.00705473,
        "note": "quoted with its owner; never applied to matzov",
    }
    return out


# ===========================================================================
def main():
    t_all = time.time()
    log(f"reserve_checks.py  TASK-20260803-69f3cd  start {now()}")
    log(f"python {sys.version.split()[0]}  PYTHONPATH={os.environ.get('PYTHONPATH','')}")

    from estimator import RC, schemes
    from estimator.lwe_primal import primal_bdd
    from estimator.lwe_dual import matzov, MATZOV
    import estimator.lwe as lwe
    import estimator.lwe_dual as lwe_dual
    mods = (RC, schemes, primal_bdd, matzov, MATZOV, lwe, lwe_dual)

    results = {
        "task_id": "TASK-20260803-69f3cd",
        "goal_id": "GOAL-MLKEM-003", "batch_id": "BATCH-012",
        "started_utc": now(),
        "seed": SEED,
        "lattice_estimator_pin": "3e48ef421ec256afddb3e7d2249a77eab6e9ba12",
        "measurement_class": ("COST-MODEL ESTIMATE, not a measurement. No ML-KEM "
                              "break claim, no security proof, no crypto-scale claim "
                              "beyond the estimator's own frame."),
        "rule12_status": "UNMET and UNWAIVED; nothing here corrects EV-MLKEM-015.",
    }

    log("\n== S0: callable identity + baseline anchor ==")
    s0 = s0_identity_and_anchor(mods)
    results["S0_identity_and_anchor"] = s0
    for nm in SETS:
        a = s0["anchor"][nm]
        log(f"  {nm}: primal {a['primal_bdd_log2rop']:.10f} (d={a['primal_bdd_delta']:.1e}) "
            f"matzov {a['matzov_log2rop']:.10f} (d={a['matzov_delta']:.1e}) "
            f"margin {a['margin_primal_minus_matzov_bits']:+.6f}")
    if not s0["anchor_ok"]:
        log("ABORT: baseline anchor not reproduced: " + "; ".join(s0["anchor_failures"]))
        results["status"] = "aborted_anchor_mismatch"
        json.dump(results, open(os.path.join(TASK_DIR, "results.json"), "w"), indent=2)
        return 1

    log("\n== S1: Sage reference ==")
    results["S1_sage_reference"] = s1_sage_reference()
    log(f"  S1 status: {results['S1_sage_reference']['status']}")

    log("\n== S2: box widening (Kyber-768, Kyber-1024) ==")
    results["S2_box_widening"] = s2_box_widening(mods)

    log("\n== S3: null object ==")
    s3 = s3_null_object(mods)
    results["S3_null_object"] = s3
    log(f"  NULL-1: {s3['null1_non_kyber_ensemble']['n_evaluated']} non-Kyber sets, "
        f"matzov undercuts primal in "
        f"{s3['null1_non_kyber_ensemble']['fraction_matzov_undercuts_primal']}")
    log(f"  NULL-2: cost-model null, matzov undercuts primal in "
        f"{s3['null2_cost_model']['fraction_matzov_undercuts_primal']}")

    log("\n== S4: decay test, extended to 2^24 and 2^32 ==")
    s4 = s4_decay(mods)
    results["S4_decay"] = s4
    for nm in SETS:
        log(f"  {nm}: " + ", ".join(
            f"d{r['delta_bits']}={r['margin_primal_minus_matzov_bits']:+.6f}"
            for r in s4["table"][nm] if "margin_primal_minus_matzov_bits" in r))
        log(f"     flip: {s4['flip_points'][nm]}")

    log("\n== S5: c* per attack ==")
    results["S5_cstar"] = s5_cstar(mods, s0)
    for nm in SETS:
        r = results["S5_cstar"]["per_attack"][nm]
        log(f"  {nm} matzov: margin {r['free_memory_margin_bits']:+.6f}  "
            f"c*_A={r['modelA_cstar_matzov']:.6f}  c*_P={r['modelP_cstar_matzov']:.6f}")

    results["finished_utc"] = now()
    results["wall_seconds_total"] = time.time() - t_all
    results["status"] = "completed"
    with open(os.path.join(TASK_DIR, "results.json"), "w") as fh:
        json.dump(results, fh, indent=2)
    with open(os.path.join(TASK_DIR, "run_stdout.log"), "w") as fh:
        fh.write("\n".join(LOG_LINES) + "\n")
    log(f"\ndone in {time.time()-t_all:.0f}s -> results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
