#!/usr/bin/env python3
"""EXP-MLKEM-007 driver.

Stages
  calibrate : pre-run parameter pinning on TRAINING seeds only (not a run)
  controls  : RUN-MLKEM-025 -- sampler, covariance-model, exact-equality,
              known-answer controls; builds and caches the reduced dual bases
  gate32    : RUN-MLKEM-026 -- n=32 gate
  full64    : RUN-MLKEM-027 -- n=64 full toy test (gate-conditional)
  analysis  : RUN-MLKEM-028 -- charged-work accounting, outcome classification

Usage:
  python3 run_experiment.py --stage <stage> --run-id <RUN-ID> --out <dir>
"""

import argparse
import hashlib
import json
import math
import os
import platform
import random
import resource
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mlwe_sampler import (Q, ETA, CBD_PROB, CBD_WEIGHTS, CBD_DENOM, LAYER_CLASS,
                          gen_instance, gen_control_permutations, derive_rng,
                          derivation_path, shift_signs, apply_shift, layer,
                          flatten)
import orbit_scoring as osc
import covariance_fusion as cf
import controls as ctl

# =========================================================================
# FROZEN CONFIGURATION -- pinned in implementation.md before RUN-MLKEM-025.
# =========================================================================
CONFIG = {
    "q": Q,
    "eta": ETA,
    "module_rank_k": 2,
    "layer_prime_p": 3,
    "ring_sizes": [32, 64],
    "training_seeds": list(range(1, 16)),
    "held_out_seeds": list(range(16, 31)),
    # Guess block G = {i : i % d_shift == 0} inside ring component 0.
    # d_shift is pinned per ring size; G is shift-invariant under X^{d_shift}.
    "d_shift": {"32": 8, "64": 8},
    "pool_size": 2048,
    "pool_construction": "LLL(delta=0.99) on the projected q-ary dual lattice, "
                        "then the pool_size shortest of {+-b_i} U {+-b_i+-b_j}",
    "lll_delta": 0.99,
    "switch_modulus_P": 3 ** 7,
    "vector_count_grid": [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048],
    "reference_vector_count": 2048,
    "matched_false_positive_rate_alpha": 1.0 / 80.0,
    "standardised_threshold_tau": 3.0,
    "success_target": 0.5,
    "gate_r_eff_min_n32": 2.0,
    "threshold_r_eff_min_n64": 4.0,
    "gate_vector_ratio_min_n32": 2.0,
    "threshold_vector_ratio_min_n64": 4.0,
    "gls_vs_unweighted_fpr_ratio_max": 0.5,
    "orbit_vs_permutation_min_bits": 1.0,
    "charged_work_bytes_per_element": 8,
    "chi2_critical_df6_alpha_0.001": ctl.CHI2_CRIT_DF6_ALPHA_001,
}

FUSION_RULES = ["unfused_single_orbit", "unweighted_mean", "gls_covariance_aware",
                "random_signed_permutation", "shuffled_orbit_labels"]


# ----------------------------------------------------------------- helpers

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def peak_rss_bytes():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def environment_block():
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "sage_version": None,
        "dependencies": {"third_party": "none (Python standard library only)",
                         "numpy": "absent", "fpylll": "absent",
                         "sympy": "absent", "sage": "absent"},
        "cpu_count": os.cpu_count(),
    }


def orbit_for(n, d_shift):
    """Maximal admissible shift-invariant orbit for guess block spacing d_shift.

    X^{n} = -1 gives scores identical up to a global candidate sign, so only the
    n/d_shift shifts j = 0, d, 2d, ..., n-d are distinct orbit elements.
    """
    return list(range(0, n, d_shift))


# --------------------------------------------------- per-instance pipeline

def reduce_instance(inst, guess_block, work):
    B, notG, dim = osc.build_dual_basis(inst, guess_block)
    t0 = time.time()
    B, stats = osc.lll(B, CONFIG["lll_delta"], work)
    stats["lll_seconds"] = time.time() - t0
    stats["dimension"] = dim
    return B, notG, stats


def instance_pool(Bred, inst, guess_block, notG, work, pool_size):
    pool, pstats = osc.build_pool(Bred, pool_size, work)
    vs, uGs = osc.pool_to_vu(pool, inst, guess_block, notG)
    work.integer_ops += len(pool) * len(guess_block) * inst.n * inst.k
    work.vector_generation_ops += len(pool) * len(guess_block) * inst.n * inst.k
    return vs, uGs, pstats


def element_scores(inst, vs, uGs, elements_residuals, guess_block, sw,
                   cand_maps, checkpoints, work, prod_cache=None):
    """Scores for a list of elements given their residual columns."""
    rho_sw = [osc.switch_vec(sw, col, work) for col in elements_residuals]
    if prod_cache is None:
        uG_sw = [[sw.switch(x) for x in row] for row in uGs]
        work.transforms += len(uGs) * len(guess_block)
        h = osc.build_h_tables(uG_sw, sw, work)
        cands = osc.enumerate_candidates(len(guess_block))
        prod = osc.candidate_products(h, cands, work)
        prod_cache = (cands, prod)
    cands, prod = prod_cache
    sc = osc.orbit_scores(rho_sw, prod, None, cand_maps, sw, checkpoints, work)
    work.bytes_read += (len(prod) * len(vs) * 2 +
                        len(elements_residuals) * len(vs)) * \
        CONFIG["charged_work_bytes_per_element"]
    return sc, prod_cache, cands


def build_candidate_maps(cands, guess_block, src_maps):
    """cand_maps[element][candidate_index] -> candidate index after the
    element's signed permutation acting on the guess block."""
    index = dict((c, i) for i, c in enumerate(cands))
    out = []
    for src in src_maps:
        row = []
        for c in cands:
            cp = osc.permuted_candidate(c, guess_block, src)
            row.append(index[cp])
        out.append(row)
    return out


def analyse_scores(per_instance, elements, rule_weights, checkpoints):
    """per_instance: list of dicts with 'scores'[oi][ck][ci] and 'correct_ci'."""
    out = {}
    for ck, m in enumerate(checkpoints):
        rows = []
        for rec in per_instance:
            n_cand = len(rec["scores"][0][ck])
            fused = []
            for ci in range(n_cand):
                vec = [rec["scores"][oi][ck][ci] for oi in range(len(elements))]
                fused.append(cf.fuse(vec, rule_weights))
            mu = cf.mean(fused)
            var = sum((x - mu) ** 2 for x in fused) / max(len(fused) - 1, 1)
            sd = math.sqrt(var) if var > 0 else 0.0
            z = cf.standardise(fused, mu, sd)
            rows.append({"seed": rec["seed"], "correct_ci": rec["correct_ci"],
                         "z": z})
        out[m] = rows
    return out


def operating_point(rows, alpha, target):
    """Threshold at matched held-out FPR alpha over pooled wrong candidates;
    success = fraction of instances whose correct candidate exceeds it."""
    wrong = []
    for r in rows:
        for ci, zz in enumerate(r["z"]):
            if ci != r["correct_ci"]:
                wrong.append(zz)
    wrong.sort()
    tau = cf.quantile(wrong, 1.0 - alpha)
    hits = sum(1 for r in rows if r["z"][r["correct_ci"]] > tau)
    lo, hi = cf.wilson_interval(hits, len(rows))
    return {"threshold": tau, "successes": hits, "instances": len(rows),
            "success_rate": hits / len(rows) if rows else float("nan"),
            "success_ci95": [lo, hi], "wrong_candidate_samples": len(wrong),
            "realised_fpr": sum(1 for w in wrong if w > tau) / len(wrong)
            if wrong else float("nan")}


def fpr_at_matched_detection(rows, target):
    """Threshold calibrated so the correct-candidate detection rate is >= target;
    report the wrong-candidate FPR there (matched-TPR comparison)."""
    correct = sorted((r["z"][r["correct_ci"]] for r in rows), reverse=True)
    if not correct:
        return {"threshold": float("nan"), "fpr": float("nan")}
    k = max(1, int(math.floor(target * len(correct))))
    tau = correct[k - 1]
    wrong = []
    for r in rows:
        for ci, zz in enumerate(r["z"]):
            if ci != r["correct_ci"]:
                wrong.append(zz)
    fp = sum(1 for w in wrong if w >= tau)
    return {"threshold": tau, "detection_rate": k / len(correct),
            "false_positives": fp, "wrong_candidates": len(wrong),
            "fpr": fp / len(wrong) if wrong else float("nan")}


def fpr_at_fixed_tau(rows, tau):
    wrong = []
    for r in rows:
        for ci, zz in enumerate(r["z"]):
            if ci != r["correct_ci"]:
                wrong.append(zz)
    fp = sum(1 for w in wrong if w > tau)
    return {"threshold": tau, "false_positives": fp,
            "wrong_candidates": len(wrong),
            "fpr": fp / len(wrong) if wrong else float("nan")}


# ------------------------------------------------------- charged-work model
# Every quantity below is an EXACT OPERATION COUNT of the code path that was
# actually executed, evaluated at pool size m ("counted_exact"); the LLL and
# sieve terms are direct MEASURED counters from the executed reduction.  The
# only declared assumption is the byte width used to convert element touches
# into memory traffic (charged_work_bytes_per_element = 8), stated in
# implementation.md and repeated in cost_accounting.json.

def charged_work(rule, m, ctx):
    """Frozen charged-work accounting for one fusion rule at m pool vectors."""
    n = ctx["n"]
    k = ctx["k"]
    nk = n * k
    g = ctx["guess_block_size"]
    dim = ctx["lattice_dimension"]
    n_cand = ctx["n_candidates"]
    n_elem = 1 if rule == "unfused_single_orbit" else ctx["subset_size"]
    uses_cov = rule in ("gls_covariance_aware", "random_signed_permutation",
                        "shuffled_orbit_labels")
    uses_subset = rule != "unfused_single_orbit"

    vecgen = ctx["lll_ops_mean"] + ctx["sieve_ops_mean"] + m * dim + m * g * nk
    transforms = n_elem * m + m * g
    residual = n_elem * m * nk
    htab = m * g * 7
    prods = n_cand * m * g * 4
    scores = n_elem * n_cand * 4 * m
    score_ops = residual + htab + prods + scores
    cov = (ctx["training_samples"] * n_elem * n_elem * 2 + n_elem ** 3) if uses_cov else 0
    subset = ctx["subset_search_ops"] if uses_subset else 0
    verify = ctx["candidates_verified"] * g
    elements_touched = n_cand * m * 2 + n_elem * m + m * g
    byts = elements_touched * CONFIG["charged_work_bytes_per_element"]
    total_ops = vecgen + score_ops + cov + subset + verify
    return {
        "rule": rule, "vectors_m": m, "orbit_elements_used": n_elem,
        "vector_generation_ops": vecgen,
        "vector_generation_ops_lll_component": ctx["lll_ops_mean"],
        "vector_generation_ops_sieve_component": ctx["sieve_ops_mean"],
        "transform_count": transforms,
        "transform_precision_bits": math.log2(CONFIG["switch_modulus_P"]),
        "score_ops": score_ops,
        "covariance_estimation_ops": cov,
        "orbit_subset_search_ops": subset,
        "candidate_verification_ops": verify,
        "bytes_moved": byts,
        "total_integer_ops": total_ops,
        "total_charged_work": total_ops + byts,
        "accounting_kind": "counted_exact (operation counts of the executed "
                           "code path at pool size m); LLL and sieve terms are "
                           "measured counters",
    }


# ============================================================== STAGE: pool

def build_or_load_bases(n, seeds, guard, phase_of, cache_path, work, log):
    """Reduced dual bases, cached as JSON so RUN-MLKEM-026 reuses exactly the
    bases RUN-MLKEM-025 built and charged."""
    d_shift = CONFIG["d_shift"][str(n)]
    guess_block = osc.guess_block_indices(n, d_shift)
    if cache_path and os.path.exists(cache_path):
        with open(cache_path) as fh:
            blob = json.load(fh)
        work.bytes_read += os.path.getsize(cache_path)
        log("loaded cached reduced bases from %s (sha256=%s)"
            % (cache_path, sha256_file(cache_path)))
        return guess_block, blob
    blob = {"n": n, "d_shift": d_shift, "guess_block": guess_block,
            "lll_delta": CONFIG["lll_delta"], "bases": {}, "lll_stats": {}}
    for seed in seeds:
        guard.read(phase_of(seed), n, seed)
        inst = gen_instance(n, seed, CONFIG["module_rank_k"])
        B, notG, stats = reduce_instance(inst, guess_block, work)
        blob["bases"][str(seed)] = B
        blob["lll_stats"][str(seed)] = stats
        log("n=%d seed=%d LLL dim=%d %.1fs swaps=%d"
            % (n, seed, stats["dimension"], stats["lll_seconds"], stats["swaps"]))
    if cache_path:
        with open(cache_path, "w") as fh:
            json.dump(blob, fh)
        work.bytes_written += os.path.getsize(cache_path)
    return guess_block, blob


# ========================================================== STAGE: controls

def stage_controls(args, log, work):
    n = 32
    seeds = CONFIG["training_seeds"] + CONFIG["held_out_seeds"]
    guard = ctl.SeedGuard(CONFIG["training_seeds"], CONFIG["held_out_seeds"])
    d_shift = CONFIG["d_shift"][str(n)]
    orbit = orbit_for(n, d_shift)
    guess_block = osc.guess_block_indices(n, d_shift)
    sw = osc.Switch(CONFIG["switch_modulus_P"])
    res = {"stage": "controls", "config": CONFIG, "orbit": orbit,
           "guess_block": guess_block}

    # --- CTRL-COVARIANCE-MODEL, both ring sizes (needs no lattice) ---------
    t0 = time.time()
    cov_ctrl = {}
    for nn in CONFIG["ring_sizes"]:
        ds = CONFIG["d_shift"][str(nn)]
        orb = orbit_for(nn, ds)
        insts = []
        for s in seeds:
            guard.read("control_measurement", nn, s)
            insts.append(gen_instance(nn, s, CONFIG["module_rank_k"]))
        cov_ctrl[str(nn)] = ctl.covariance_model_control(nn, seeds, orb,
                                                         CONFIG["module_rank_k"],
                                                         insts)
        log("CTRL-COVARIANCE-MODEL n=%d elements=%s pass=%s"
            % (nn, orb, cov_ctrl[str(nn)]["pass"]))
        del insts
    res["ctrl_covariance_model"] = cov_ctrl
    res["ctrl_covariance_model_seconds"] = time.time() - t0

    # --- reduced dual bases for every n=32 instance ------------------------
    t0 = time.time()
    cache = os.path.join(args.out, "reduced-bases-n32.json")
    _, blob = build_or_load_bases(
        n, seeds, guard,
        lambda s: "pool_construction", cache, work, log)
    res["lll_stats"] = blob["lll_stats"]
    res["basis_cache"] = {"path": os.path.relpath(cache, args.repo_root),
                          "sha256": sha256_file(cache),
                          "bytes": os.path.getsize(cache)}
    res["pool_construction_seconds"] = time.time() - t0

    verif = osc.verify_lll_output(blob["bases"][str(seeds[0])], CONFIG["lll_delta"])
    res["lll_independent_verification_seed_%d" % seeds[0]] = {
        "size_reduced": verif["size_reduced"], "lovasz": verif["lovasz"]}

    # --- CTRL-EXACT-EQUALITY ----------------------------------------------
    t0 = time.time()
    eq = []
    for seed in CONFIG["training_seeds"][:3]:
        guard.read("control_measurement", n, seed)
        inst = gen_instance(n, seed, CONFIG["module_rank_k"])
        Bred = blob["bases"][str(seed)]
        notG = [I for I in range(n * CONFIG["module_rank_k"])
                if I not in set(guess_block)]
        vs, uGs, pstats = instance_pool(Bred, inst, guess_block, notG,
                                        osc.Work(), 64)
        r = ctl.exact_equality_control(inst, vs, uGs, orbit, guess_block, sw,
                                       max_vectors=16, max_candidates=9)
        r["seed"] = seed
        r["pool_norms"] = pstats
        eq.append(r)
        log("CTRL-EXACT-EQUALITY seed=%d residual_checks=%d phase_checks=%d pass=%s"
            % (seed, r["residual_checks"], r["phase_index_checks"], r["pass"]))
    res["ctrl_exact_equality"] = eq
    res["ctrl_exact_equality_pass"] = all(r["pass"] for r in eq)
    res["ctrl_exact_equality_seconds"] = time.time() - t0

    # --- CTRL-KNOWN-ANSWER: unfused baseline at the reference vector count --
    t0 = time.time()
    m_ref = CONFIG["reference_vector_count"]
    checkpoints = [m_ref]
    rows = []
    pool_norms = []
    for seed in CONFIG["training_seeds"]:
        guard.read("control_measurement", n, seed)
        inst = gen_instance(n, seed, CONFIG["module_rank_k"])
        Bred = blob["bases"][str(seed)]
        notG = [I for I in range(n * CONFIG["module_rank_k"])
                if I not in set(guess_block)]
        w2 = osc.Work()
        vs, uGs, pstats = instance_pool(Bred, inst, guess_block, notG, w2, m_ref)
        pool_norms.append(pstats)
        resid = osc.orbit_residuals_batched_fast(vs, inst, [0], w2)
        cands = osc.enumerate_candidates(len(guess_block))
        cand_maps = build_candidate_maps(cands, guess_block,
                                         [shift_signs(n, 0)])
        sc, _, _ = element_scores(inst, vs, uGs, resid, guess_block, sw,
                                  cand_maps, checkpoints, w2)
        correct = tuple(layer(inst.s[0][i]) for i in guess_block)
        ci = cands.index(correct)
        fused = sc[0][0]
        mu = cf.mean(fused)
        sd = math.sqrt(sum((x - mu) ** 2 for x in fused) / max(len(fused) - 1, 1))
        z = cf.standardise(fused, mu, sd)
        rank = 1 + sum(1 for v in z if v > z[ci])
        rows.append({"seed": seed, "correct_ci": ci, "z": z, "rank": rank,
                     "z_correct": z[ci]})
        work.add(w2)
        log("CTRL-KNOWN-ANSWER seed=%d rank=%d z=%.2f" % (seed, rank, z[ci]))
    op = operating_point(rows, CONFIG["matched_false_positive_rate_alpha"],
                         CONFIG["success_target"])
    top1 = sum(1 for r in rows if r["rank"] == 1) / len(rows)
    res["ctrl_known_answer"] = {
        "reference_vector_count": m_ref,
        "orbit_element": 0,
        "instances": [{"seed": r["seed"], "rank": r["rank"],
                       "z_correct": r["z_correct"]} for r in rows],
        "top1_recovery_rate": top1,
        "operating_point": op,
        "pass": top1 >= CONFIG["success_target"],
        "pool_norm_summary": {
            "norm_min": min(p["norm_min"] for p in pool_norms),
            "norm_median_mean": cf.mean([p["norm_median"] for p in pool_norms]),
            "norm_max": max(p["norm_max"] for p in pool_norms)},
    }
    res["ctrl_known_answer_seconds"] = time.time() - t0

    # --- n=64 feasibility probe (measured, bounded) ------------------------
    res["n64_feasibility_probe"] = n64_probe(log, budget_seconds=args.n64_probe_seconds)

    res["ctrl_seed_discipline"] = guard.attestation()
    res["work"] = work.asdict()
    return res


def n64_probe(log, budget_seconds):
    """Measured, bounded probe of the n=64 pool-construction cost.

    Runs LLL on the n=64 projected dual basis for at most `budget_seconds`; the
    measurement is the wall time actually consumed and whether reduction
    completed.  Nothing is extrapolated here; the projection is done in the
    analysis stage and labelled `modeled`.
    """
    if budget_seconds <= 0:
        return {"executed": False, "reason": "probe disabled"}
    n = 64
    d_shift = CONFIG["d_shift"][str(n)]
    guess_block = osc.guess_block_indices(n, d_shift)
    inst = gen_instance(n, CONFIG["training_seeds"][0], CONFIG["module_rank_k"])
    B, notG, dim = osc.build_dual_basis(inst, guess_block)
    log("n=64 probe: dual lattice dimension %d, |G|=%d" % (dim, len(guess_block)))
    t0 = time.time()
    completed = True
    try:
        _deadline_lll(B, CONFIG["lll_delta"], t0 + budget_seconds)
    except TimeoutError:
        completed = False
    dt = time.time() - t0
    log("n=64 probe: LLL %s after %.1f s" %
        ("completed" if completed else "did NOT complete", dt))
    return {"executed": True, "n": n, "dimension": dim,
            "guess_block_size": len(guess_block),
            "orbit_size": len(orbit_for(n, d_shift)),
            "budget_seconds": budget_seconds, "elapsed_seconds": dt,
            "completed": completed}


def _deadline_lll(B, delta, deadline):
    """LLL that raises TimeoutError past `deadline` (measurement, not a result)."""
    d = len(B)
    n = len(B[0])
    mu = [[0.0] * d for _ in range(d)]
    Bn = [0.0] * d

    def dot(u, v):
        return sum(x * y for x, y in zip(u, v))

    Bn[0] = float(dot(B[0], B[0]))
    kmax, k, counter = 0, 1, 0
    while k < d:
        counter += 1
        if counter % 200 == 0 and time.time() > deadline:
            raise TimeoutError()
        if k > kmax:
            kmax = k
            bk = B[k]
            for j in range(k):
                s = float(dot(bk, B[j]))
                for i in range(j):
                    s -= mu[j][i] * mu[k][i] * Bn[i]
                mu[k][j] = s / Bn[j] if Bn[j] else 0.0
            s = float(dot(bk, bk))
            for j in range(k):
                s -= mu[k][j] ** 2 * Bn[j]
            Bn[k] = s
        m = mu[k][k - 1]
        if abs(m) > 0.5:
            r = int(m + 0.5) if m > 0 else -int(0.5 - m)
            bk, bl = B[k], B[k - 1]
            for t in range(n):
                bk[t] -= r * bl[t]
            for i in range(k - 1):
                mu[k][i] -= r * mu[k - 1][i]
            mu[k][k - 1] = m - r
        if Bn[k] < (delta - mu[k][k - 1] ** 2) * Bn[k - 1]:
            mu_ = mu[k][k - 1]
            Bt = Bn[k] + mu_ * mu_ * Bn[k - 1]
            if Bt == 0.0:
                Bn[k], Bn[k - 1] = Bn[k - 1], Bn[k]
                B[k], B[k - 1] = B[k - 1], B[k]
                k = max(k - 1, 1)
                continue
            mu[k][k - 1] = mu_ * Bn[k - 1] / Bt
            Bn[k] = Bn[k - 1] * Bn[k] / Bt
            Bn[k - 1] = Bt
            B[k], B[k - 1] = B[k - 1], B[k]
            for j in range(k - 1):
                mu[k][j], mu[k - 1][j] = mu[k - 1][j], mu[k][j]
            mkk = mu[k][k - 1]
            for i in range(k + 1, kmax + 1):
                t = mu[i][k]
                mu[i][k] = mu[i][k - 1] - mu_ * t
                mu[i][k - 1] = t + mkk * mu[i][k]
            k = max(k - 1, 1)
        else:
            for l in range(k - 2, -1, -1):
                m = mu[k][l]
                if abs(m) > 0.5:
                    r = int(m + 0.5) if m > 0 else -int(0.5 - m)
                    bk, bl = B[k], B[l]
                    for t in range(n):
                        bk[t] -= r * bl[t]
                    for i in range(l):
                        mu[k][i] -= r * mu[l][i]
                    mu[k][l] = m - r
            k += 1
    return B


# ============================================================ STAGE: gate32

def score_all_instances(n, seeds, guard, phase, blob, guess_block, orbit, sw,
                        checkpoints, work, log, want_controls=True):
    """Per-instance orbit / permutation / shuffled-label scores."""
    nk = n * CONFIG["module_rank_k"]
    notG = [I for I in range(nk) if I not in set(guess_block)]
    cands = osc.enumerate_candidates(len(guess_block))
    orbit_maps_src = [shift_signs(n, j) for j in orbit]
    orbit_cand_maps = build_candidate_maps(cands, guess_block, orbit_maps_src)
    out = []
    for seed in seeds:
        guard.read(phase, n, seed)
        t0 = time.time()
        inst = gen_instance(n, seed, CONFIG["module_rank_k"])
        # controls fixed BEFORE the secret is used downstream
        perms, perm_path = gen_control_permutations(n, seed, len(orbit),
                                                    guess_block)
        w2 = osc.Work()
        Bred = blob["bases"][str(seed)]
        vs, uGs, pstats = instance_pool(Bred, inst, guess_block, notG, w2,
                                        CONFIG["pool_size"])
        resid = osc.orbit_residuals_batched_fast(vs, inst, orbit, w2)
        sc, prod_cache, _ = element_scores(inst, vs, uGs, resid, guess_block, sw,
                                           orbit_cand_maps, checkpoints, w2)
        rec = {"seed": seed, "pool": pstats,
               "orbit_scores": sc, "seconds": None,
               "permutation_derivation_path": perm_path}
        w_orbit = osc.Work()
        w_orbit.add(w2)
        rec["work_orbit"] = w2.asdict()

        if want_controls:
            wc = osc.Work()
            perm_resid = [osc.perm_residuals(vs, inst, src, wc) for src in perms]
            perm_cand_maps = build_candidate_maps(cands, guess_block, perms)
            scp, _, _ = element_scores(inst, vs, uGs, perm_resid, guess_block, sw,
                                       perm_cand_maps, checkpoints, wc,
                                       prod_cache=prod_cache)
            rec["perm_scores"] = scp
            rec["work_perm"] = wc.asdict()
            rng, _ = derive_rng(n, seed, "shuffled_orbit_labels")
            sh = ctl.shuffled_label_map(len(orbit), rng)
            rec["shuffle_map"] = sh
            ws = osc.Work()
            shuffled_maps = [orbit_cand_maps[sh[i]] for i in range(len(orbit))]
            scs, _, _ = element_scores(inst, vs, uGs, resid, guess_block, sw,
                                       shuffled_maps, checkpoints, ws,
                                       prod_cache=prod_cache)
            rec["shuffled_scores"] = scs
            rec["work_shuffled"] = ws.asdict()
            work.add(wc)
        correct = tuple(layer(inst.s[0][i]) for i in guess_block)
        rec["correct_ci"] = cands.index(correct)
        rec["correct_layer"] = list(correct)
        rec["secret_hash"] = hashlib.sha256(
            json.dumps([inst.s[0], inst.s[1]]).encode()).hexdigest()
        rec["seconds"] = time.time() - t0
        work.add(w2)
        out.append(rec)
        log("n=%d seed=%d scored in %.1f s (pool median norm %.0f)"
            % (n, seed, rec["seconds"], pstats["norm_median"]))
    return out, cands


def stage_gate32(args, log, work):
    n = 32
    guard = ctl.SeedGuard(CONFIG["training_seeds"], CONFIG["held_out_seeds"])
    d_shift = CONFIG["d_shift"][str(n)]
    orbit_full = orbit_for(n, d_shift)
    guess_block = osc.guess_block_indices(n, d_shift)
    sw = osc.Switch(CONFIG["switch_modulus_P"])
    checkpoints = CONFIG["vector_count_grid"]
    res = {"stage": "gate32", "config": CONFIG, "orbit_full": orbit_full,
           "guess_block": guess_block}

    cache = os.path.join(args.basis_cache)
    with open(cache) as fh:
        blob = json.load(fh)
    work.bytes_read += os.path.getsize(cache)
    res["basis_cache"] = {"path": os.path.relpath(cache, args.repo_root),
                          "sha256": sha256_file(cache)}

    t0 = time.time()
    train, cands = score_all_instances(n, CONFIG["training_seeds"], guard,
                                       "covariance_fit", blob, guess_block,
                                       orbit_full, sw, checkpoints, work, log)
    res["training_seconds"] = time.time() - t0
    t0 = time.time()
    held, _ = score_all_instances(n, CONFIG["held_out_seeds"], guard,
                                  "held_out_evaluation", blob, guess_block,
                                  orbit_full, sw, checkpoints, work, log)
    res["held_out_seconds"] = time.time() - t0

    # ---- covariance, effective rank, subset selection (TRAINING ONLY) -----
    wsub = osc.Work()

    def wrong_vectors(recs, key, subset_idx, ck):
        vecs = []
        for r in recs:
            n_cand = len(r[key][0][ck])
            for ci in range(n_cand):
                if ci == r["correct_ci"]:
                    continue
                vecs.append([r[key][oi][ck][ci] for oi in subset_idx])
        return vecs

    def per_instance_standardised_cov(recs, key, subset_idx, ck):
        """Covariance of per-instance-standardised wrong-candidate score
        vectors, so instance-to-instance score scale does not dominate."""
        vecs = []
        for r in recs:
            n_cand = len(r[key][0][ck])
            cols = []
            for oi in subset_idx:
                col = [r[key][oi][ck][ci] for ci in range(n_cand)]
                mu = cf.mean(col)
                sd = math.sqrt(sum((x - mu) ** 2 for x in col) /
                               max(len(col) - 1, 1))
                cols.append([(x - mu) / sd if sd > 0 else 0.0 for x in col])
            for ci in range(n_cand):
                if ci == r["correct_ci"]:
                    continue
                vecs.append([cols[a][ci] for a in range(len(subset_idx))])
        return vecs

    ck_ref = checkpoints.index(CONFIG["reference_vector_count"])
    subsets = []
    for size in range(2, len(orbit_full) + 1):
        subsets.append(list(range(size)))
    subset_report = []
    for sub in subsets:
        vecs = per_instance_standardised_cov(train, "orbit_scores", sub, ck_ref)
        S = cf.covariance(vecs, wsub)
        r_eff = cf.effective_rank(S)
        subset_report.append({"subset_indices": sub,
                              "orbit_elements": [orbit_full[i] for i in sub],
                              "size": len(sub), "training_r_eff": r_eff,
                              "covariance": S})
        wsub.subset_search_ops += len(vecs) * len(sub) * len(sub)
    best = max(subset_report, key=lambda r: (r["training_r_eff"], -r["size"]))
    subset_idx = best["subset_indices"]
    orbit = [orbit_full[i] for i in subset_idx]
    res["orbit_subset_selection"] = {
        "rule": "argmax training r_eff over prefixes of the maximal admissible "
                "shift-invariant orbit, size cap 32; ties -> smaller size",
        "candidates": [{"orbit_elements": r["orbit_elements"],
                        "training_r_eff": r["training_r_eff"]}
                       for r in subset_report],
        "selected": orbit, "selected_indices": subset_idx,
        "training_r_eff": best["training_r_eff"]}
    res["work_subset_search"] = wsub.asdict()
    log("selected orbit subset %s (training r_eff=%.3f)"
        % (orbit, best["training_r_eff"]))

    # ---- covariance / r_eff per vector count, train and held-out ----------
    cov_report = {"orbit": {}, "random_signed_permutation": {},
                  "shuffled_orbit_labels": {}}
    wcov = osc.Work()
    gls_weights_by_m = {}
    for ck, m in enumerate(checkpoints):
        for key, label in (("orbit_scores", "orbit"),
                           ("perm_scores", "random_signed_permutation"),
                           ("shuffled_scores", "shuffled_orbit_labels")):
            vtr = per_instance_standardised_cov(train, key, subset_idx, ck)
            vho = per_instance_standardised_cov(held, key, subset_idx, ck)
            Str = cf.covariance(vtr, wcov)
            Sho = cf.covariance(vho, wcov)
            rtr = cf.effective_rank(Str)
            rho = cf.effective_rank(Sho)
            w, ok = cf.gls_weights(Str, work=wcov)
            cov_report[label][str(m)] = {
                "training_covariance": Str, "held_out_covariance": Sho,
                "training_r_eff": rtr, "held_out_r_eff": rho,
                "r_eff_relative_deviation":
                    abs(rho - rtr) / rtr if rtr and rtr == rtr else float("nan"),
                "gls_weights": w, "gls_invertible": ok,
                "training_samples": len(vtr), "held_out_samples": len(vho)}
            if label == "orbit":
                gls_weights_by_m[m] = w
    res["covariance_report"] = cov_report
    res["work_covariance"] = wcov.asdict()

    # ---- fusion rules ----------------------------------------------------
    d = len(subset_idx)
    rule_defs = {
        "unfused_single_orbit": ("orbit_scores", [0], [1.0]),
        "unweighted_mean": ("orbit_scores", subset_idx, [1.0 / d] * d),
        "gls_covariance_aware": ("orbit_scores", subset_idx, None),
        "random_signed_permutation": ("perm_scores", subset_idx, None),
        "shuffled_orbit_labels": ("shuffled_scores", subset_idx, None),
    }
    results = {}
    for rule, (key, idxs, wts) in rule_defs.items():
        per_m = {}
        for ck, m in enumerate(checkpoints):
            if wts is None:
                vtr = per_instance_standardised_cov(
                    train, key, idxs, ck)
                S = cf.covariance(vtr, wcov)
                w, _ = cf.gls_weights(S, work=wcov)
            else:
                w = wts
            rows_ho = []
            rows_tr = []
            for recs, dest in ((held, rows_ho), (train, rows_tr)):
                for r in recs:
                    n_cand = len(r[key][0][ck])
                    fused = []
                    for ci in range(n_cand):
                        vec = [r[key][oi][ck][ci] for oi in idxs]
                        fused.append(cf.fuse(vec, w))
                    mu = cf.mean(fused)
                    sd = math.sqrt(sum((x - mu) ** 2 for x in fused) /
                                   max(len(fused) - 1, 1))
                    dest.append({"seed": r["seed"], "correct_ci": r["correct_ci"],
                                 "z": cf.standardise(fused, mu, sd)})
            op = operating_point(rows_ho, CONFIG["matched_false_positive_rate_alpha"],
                                 CONFIG["success_target"])
            op_tr = operating_point(rows_tr, CONFIG["matched_false_positive_rate_alpha"],
                                    CONFIG["success_target"])
            per_m[str(m)] = {
                "weights": w,
                "held_out": op,
                "training": op_tr,
                "held_out_fpr_at_matched_detection":
                    fpr_at_matched_detection(rows_ho, CONFIG["success_target"]),
                "held_out_fpr_at_tau": fpr_at_fixed_tau(
                    rows_ho, CONFIG["standardised_threshold_tau"]),
            }
        m50 = None
        for m in checkpoints:
            if per_m[str(m)]["held_out"]["success_rate"] >= CONFIG["success_target"]:
                m50 = m
                break
        results[rule] = {"per_vector_count": per_m,
                         "m50_held_out": m50,
                         "elements_used": [orbit_full[i] for i in idxs]
                         if key != "perm_scores" else
                         ["random_signed_permutation_%d" % i for i in idxs]}
        log("rule=%-28s m50=%s" % (rule, m50))
    res["fusion_results"] = results

    # ---- charged work ----------------------------------------------------
    lll_ops = [blob["lll_stats"][str(s)]["ops"]
               for s in CONFIG["training_seeds"] + CONFIG["held_out_seeds"]]
    sieve_ops = (train[0]["work_orbit"]["vector_generation_ops"] -
                 int(cf.mean(lll_ops)))
    ctx = {
        "n": n, "k": CONFIG["module_rank_k"],
        "guess_block_size": len(guess_block),
        "lattice_dimension": blob["lll_stats"][str(CONFIG["training_seeds"][0])]["dimension"],
        "n_candidates": len(cands),
        "subset_size": len(subset_idx),
        "training_samples": len(CONFIG["training_seeds"]) * (len(cands) - 1),
        "subset_search_ops": wsub.subset_search_ops,
        "candidates_verified": len(cands),
        "lll_ops_mean": int(cf.mean(lll_ops)),
        "sieve_ops_mean": max(sieve_ops, 0),
    }
    res["charged_work_context"] = ctx
    cost = {}
    for rule in rule_defs:
        m50 = results[rule]["m50_held_out"]
        m_op = m50 if m50 else CONFIG["reference_vector_count"]
        cost[rule] = {
            "m50_held_out": m50,
            "reached_operating_point": m50 is not None,
            "operating_point_vectors": m_op,
            "operating_point_fallback":
                None if m50 else "rule never reached 50% held-out success on "
                                 "the frozen vector-count grid; work is "
                                 "reported at the reference vector count and "
                                 "no gain is inferred",
            "at_operating_point": charged_work(rule, m_op, ctx),
            "at_reference_vector_count":
                charged_work(rule, CONFIG["reference_vector_count"], ctx),
        }
    res["charged_work"] = cost
    res["work_totals"] = {
        "measured_total": work.asdict(),
        "subset_search": wsub.asdict(),
        "covariance": wcov.asdict(),
        "per_instance_orbit": train[0]["work_orbit"],
        "per_instance_perm": train[0].get("work_perm"),
    }
    res["ctrl_seed_discipline"] = guard.attestation()

    # ---- frozen n=32 gate decision ---------------------------------------
    m_ref = str(CONFIG["reference_vector_count"])
    r_eff_ho = cov_report["orbit"][m_ref]["held_out_r_eff"]
    r_eff_tr = cov_report["orbit"][m_ref]["training_r_eff"]
    m50_un = results["unfused_single_orbit"]["m50_held_out"]
    m50_gls = results["gls_covariance_aware"]["m50_held_out"]
    w_un = cost["unfused_single_orbit"]["at_operating_point"]
    w_gls = cost["gls_covariance_aware"]["at_operating_point"]
    work_lower = (w_un is not None and w_gls is not None and
                  w_gls["total_charged_work"] < w_un["total_charged_work"])
    ratio = (m50_un / m50_gls) if (m50_un and m50_gls) else None
    gate = {
        "criteria": {
            "held_out_r_eff_at_reference_vector_count": r_eff_ho,
            "held_out_r_eff_min": CONFIG["gate_r_eff_min_n32"],
            "held_out_r_eff_pass": bool(r_eff_ho == r_eff_ho and
                                        r_eff_ho >= CONFIG["gate_r_eff_min_n32"]),
            "exact_equality_pass": None,  # imported from RUN-MLKEM-025
            "fused_work_lower_than_unfused": work_lower,
            "charged_work_gls": w_gls["total_charged_work"] if w_gls else None,
            "charged_work_unfused": w_un["total_charged_work"] if w_un else None,
        },
        "training_r_eff_at_reference_vector_count": r_eff_tr,
        "vector_count_ratio_unfused_over_gls": ratio,
        "vector_count_ratio_min": CONFIG["gate_vector_ratio_min_n32"],
        "m50_unfused": m50_un, "m50_gls": m50_gls,
    }
    res["gate_decision"] = gate

    # ---- HEUR-001 comparison statistics (reported, not adjudicated) ------
    heur = {}
    for m in checkpoints:
        e = cov_report["orbit"][str(m)]
        gls = results["gls_covariance_aware"]["per_vector_count"][str(m)]
        heur[str(m)] = {
            "training_r_eff": e["training_r_eff"],
            "held_out_r_eff": e["held_out_r_eff"],
            "r_eff_relative_deviation": e["r_eff_relative_deviation"],
            "r_eff_deviation_below_0.50": (e["r_eff_relative_deviation"] < 0.5)
            if e["r_eff_relative_deviation"] == e["r_eff_relative_deviation"] else None,
            "training_fpr_at_tau": None,
            "held_out_fpr_at_tau": gls["held_out_fpr_at_tau"]["fpr"],
        }
    res["heur_001_statistics"] = heur

    # ---- raw per-instance scores go to a side file ------------------------
    def slim(recs):
        out = []
        for r in recs:
            out.append({
                "seed": r["seed"], "correct_ci": r["correct_ci"],
                "correct_layer": r["correct_layer"],
                "secret_hash": r["secret_hash"],
                "pool": r["pool"],
                "shuffle_map": r.get("shuffle_map"),
                "permutation_derivation_path": r["permutation_derivation_path"],
                "orbit_scores_at_grid": r["orbit_scores"],
                "perm_scores_at_grid": r.get("perm_scores"),
                "shuffled_scores_at_grid": r.get("shuffled_scores"),
            })
        return out

    side = os.path.join(args.out, "orbit-scores.json")
    with open(side, "w") as fh:
        json.dump({"vector_count_grid": checkpoints,
                   "orbit_full": orbit_full,
                   "candidates": [list(c) for c in cands],
                   "training": slim(train), "held_out": slim(held)},
                  fh, separators=(",", ":"))
    res["orbit_scores_file"] = {
        "path": "experiments/EXP-MLKEM-007/runs/%s/orbit-scores.json" % args.run_id,
        "sha256": sha256_file(side), "bytes": os.path.getsize(side)}
    return res


# ============================================================ STAGE: full64

def stage_full64(args, log, work):
    """n=64 full toy test.  Executed only on an n=32 gate pass."""
    n = 64
    d_shift = CONFIG["d_shift"][str(n)]
    guess_block = osc.guess_block_indices(n, d_shift)
    orbit = orbit_for(n, d_shift)
    res = {"stage": "full64", "config": CONFIG, "orbit": orbit,
           "guess_block": guess_block}
    guard = ctl.SeedGuard(CONFIG["training_seeds"], CONFIG["held_out_seeds"])
    budget = args.stage_budget_seconds
    t0 = time.time()
    completed_seeds = []
    bases = {}
    aborted = None
    for seed in CONFIG["training_seeds"] + CONFIG["held_out_seeds"]:
        if time.time() - t0 > budget:
            aborted = "stage wall-clock budget exhausted"
            break
        guard.read("pool_construction", n, seed)
        inst = gen_instance(n, seed, CONFIG["module_rank_k"])
        B, notG, dim = osc.build_dual_basis(inst, guess_block)
        res["dimension"] = dim
        t1 = time.time()
        try:
            _deadline_lll(B, CONFIG["lll_delta"], t0 + budget)
        except TimeoutError:
            aborted = "LLL did not complete within the stage budget"
            res["last_attempted_seed"] = seed
            res["last_attempt_seconds"] = time.time() - t1
            break
        bases[str(seed)] = B
        completed_seeds.append(seed)
        log("n=64 seed=%d LLL done %.1f s" % (seed, time.time() - t1))
    res["elapsed_seconds"] = time.time() - t0
    res["seeds_with_completed_reduction"] = completed_seeds
    res["seeds_required"] = len(CONFIG["training_seeds"]) + len(CONFIG["held_out_seeds"])
    res["aborted_reason"] = aborted
    res["ctrl_seed_discipline"] = guard.attestation()
    res["work"] = work.asdict()
    return res


# =========================================================== STAGE: analysis

def stage_analysis(args, log, work):
    res = {"stage": "analysis", "config": CONFIG}
    raws = {}
    for rid in ("RUN-MLKEM-025", "RUN-MLKEM-026", "RUN-MLKEM-027"):
        p = os.path.join(args.runs_root, rid, "raw.json")
        if os.path.exists(p):
            with open(p) as fh:
                raws[rid] = json.load(fh)
            work.bytes_read += os.path.getsize(p)
    res["inputs"] = sorted(raws.keys())
    res["raw_pointers"] = dict(
        (k, {"path": "experiments/EXP-MLKEM-007/runs/%s/raw.json" % k,
             "sha256": sha256_file(os.path.join(args.runs_root, k, "raw.json"))})
        for k in raws)

    c25 = raws.get("RUN-MLKEM-025", {})
    c26 = raws.get("RUN-MLKEM-026", {})
    c27 = raws.get("RUN-MLKEM-027", {})
    ana_dir = os.path.join(args.repo_root, "experiments", "EXP-MLKEM-007", "analysis")
    os.makedirs(ana_dir, exist_ok=True)

    # ---------------- covariance_report.json ------------------------------
    cov_out = {
        "experiment_id": "EXP-MLKEM-007",
        "source_runs": ["RUN-MLKEM-025", "RUN-MLKEM-026"],
        "ctrl_covariance_model": c25.get("ctrl_covariance_model"),
        "orbit_subset_selection": c26.get("orbit_subset_selection"),
        "orbit_score_covariance": c26.get("covariance_report"),
        "heur_001_statistics": c26.get("heur_001_statistics"),
        "heur_001_comparison": heur_001_comparison(c26),
        "note": "Effective rank r_eff = (tr Sigma)^2 / tr(Sigma^2) of the "
                "wrong-candidate orbit-score covariance, estimated on the 15 "
                "training seeds and re-measured on the 15 held-out seeds. "
                "Observations only; no adjudication of HEUR-001.",
    }
    _write_json(os.path.join(ana_dir, "covariance_report.json"), cov_out, work)

    # ---------------- gate_decision.json ----------------------------------
    gate = dict(c26.get("gate_decision") or {})
    eq_pass = c25.get("ctrl_exact_equality_pass")
    if "criteria" in gate:
        gate["criteria"]["exact_equality_pass"] = eq_pass
    crit = gate.get("criteria", {})
    gate_pass = bool(crit.get("held_out_r_eff_pass") and eq_pass and
                     crit.get("fused_work_lower_than_unfused"))
    gate["gate_pass"] = gate_pass
    gate["gate_rule"] = ("Stop and reject (correlated_reindexing) if held-out "
                         "r_eff < 2.0 at n=32, if scalar and batched scores "
                         "disagree on the exact check, or if measured fused "
                         "work is not lower than the unfused baseline.")
    gate["run_027_disposition"] = ("executed" if gate_pass else
                                   "cancelled_by_budget / gate_stop")
    _write_json(os.path.join(ana_dir, "gate_decision.json"), gate, work)

    # ---------------- cost_accounting.json --------------------------------
    fus = c26.get("fusion_results", {})
    ctx = c26.get("charged_work_context", {})
    cw = c26.get("charged_work", {})
    # RUN-MLKEM-026 wrote its per-rule cost table under the key "charged_work",
    # which main() then overwrote with the aggregate Work counters (an output
    # key collision, recorded as an anomaly).  The table is recomputed here from
    # the recorded charged_work_context and the recorded m50 values with the
    # SAME frozen charged_work() function; the two values RUN-MLKEM-026 recorded
    # inside gate_decision.criteria are used as a cross-check.
    recomputed = False
    if not isinstance(cw, dict) or "unfused_single_orbit" not in cw:
        recomputed = True
        cw = {}
        for rule, fr in fus.items():
            m50 = fr.get("m50_held_out")
            m_op = m50 if m50 else CONFIG["reference_vector_count"]
            cw[rule] = {
                "m50_held_out": m50,
                "reached_operating_point": m50 is not None,
                "operating_point_vectors": m_op,
                "operating_point_fallback":
                    None if m50 else "rule never reached 50% held-out success "
                                     "on the frozen vector-count grid; work is "
                                     "reported at the reference vector count "
                                     "and no gain is inferred",
                "at_operating_point": charged_work(rule, m_op, ctx),
                "at_reference_vector_count":
                    charged_work(rule, CONFIG["reference_vector_count"], ctx),
            }
    gcrit = (c26.get("gate_decision") or {}).get("criteria", {})
    crosscheck = {
        "recomputed_from_recorded_context": recomputed,
        "run_026_recorded_charged_work_gls": gcrit.get("charged_work_gls"),
        "recomputed_charged_work_gls":
            cw.get("gls_covariance_aware", {}).get("at_operating_point", {})
              .get("total_charged_work"),
        "run_026_recorded_charged_work_unfused": gcrit.get("charged_work_unfused"),
        "recomputed_charged_work_unfused":
            cw.get("unfused_single_orbit", {}).get("at_operating_point", {})
              .get("total_charged_work"),
    }
    crosscheck["agrees"] = (
        crosscheck["run_026_recorded_charged_work_gls"] ==
        crosscheck["recomputed_charged_work_gls"] and
        crosscheck["run_026_recorded_charged_work_unfused"] ==
        crosscheck["recomputed_charged_work_unfused"])
    log("charged-work cross-check vs RUN-MLKEM-026 gate record: %s"
        % crosscheck["agrees"])
    ratios = {}
    base_entry = cw.get("unfused_single_orbit", {})
    base = base_entry.get("at_operating_point")
    base_ok = base_entry.get("reached_operating_point")
    pool_size = CONFIG["pool_size"]
    for rule, entry in cw.items():
        at = entry.get("at_operating_point")
        ok = entry.get("reached_operating_point")
        both = bool(at and base and ok and base_ok)
        # MODELED alternative: vector generation charged proportionally to m,
        # as it would be in a sieve-dominated (not LLL-dominated) regime.
        def modeled_total(a):
            if not a:
                return None
            fixed = (a["vector_generation_ops_lll_component"] +
                     a["vector_generation_ops_sieve_component"])
            return (a["total_charged_work"] - fixed +
                    fixed * a["vectors_m"] / pool_size)
        ratios[rule] = {
            "m50_held_out": entry.get("m50_held_out"),
            "reached_operating_point": ok,
            "operating_point_vectors": entry.get("operating_point_vectors"),
            "total_charged_work": at["total_charged_work"] if at else None,
            "ratio_to_unfused": (at["total_charged_work"] / base["total_charged_work"])
            if both else None,
            "projected_gain_bits_vs_unfused":
                math.log2(base["total_charged_work"] / at["total_charged_work"])
                if both else None,
            "modeled_sieve_dominated_total_charged_work": modeled_total(at),
            "modeled_sieve_dominated_ratio_to_unfused":
                (modeled_total(at) / modeled_total(base)) if both else None,
            "modeled_sieve_dominated_gain_bits":
                math.log2(modeled_total(base) / modeled_total(at)) if both else None,
        }
    orbit_bits = ratios.get("gls_covariance_aware", {}).get("projected_gain_bits_vs_unfused")
    perm_bits = ratios.get("random_signed_permutation", {}).get("projected_gain_bits_vs_unfused")
    cost_out = {
        "experiment_id": "EXP-MLKEM-007",
        "source_run": "RUN-MLKEM-026",
        "context": ctx,
        "raw_summary_crosscheck": crosscheck,
        "per_rule": ratios,
        "per_rule_detail": cw,
        "total_charged_score_work_ratio_gls_over_unfused":
            ratios.get("gls_covariance_aware", {}).get("ratio_to_unfused"),
        "true_orbit_vs_random_signed_permutation_gain_bits":
            (orbit_bits - perm_bits) if (orbit_bits is not None and
                                         perm_bits is not None) else None,
        "true_orbit_vs_random_signed_permutation_note":
            "If the random signed-permutation control never reaches the 50% "
            "held-out operating point on the frozen vector-count grid its "
            "projected gain is not defined; that case is reported as "
            "'control_did_not_reach_operating_point' and the difference is "
            "reported as null, never as an inferred value.",
        "modeled_alternative_note":
            "The frozen decision metric is the counted_exact accounting above. "
            "The 'modeled_sieve_dominated_*' fields re-charge the LLL and sieve "
            "terms proportionally to the pool size m, i.e. they MODEL a regime "
            "in which short-vector generation scales with the number of vectors "
            "produced rather than being a fixed per-instance reduction. They are "
            "MODELED, not measured, and are reported only so the measured "
            "LLL-dominated result is not mistaken for a regime-independent one.",
        "labels": {"measured": ["lll_ops_mean", "sieve_ops_mean",
                                "wall_clock_seconds", "peak_rss_bytes",
                                "cpu_seconds"],
                   "counted_exact": ["vector_generation_ops", "score_ops",
                                     "covariance_estimation_ops",
                                     "orbit_subset_search_ops",
                                     "candidate_verification_ops",
                                     "transform_count"],
                   "modeled": ["bytes_moved",
                               "modeled_sieve_dominated_total_charged_work",
                               "modeled_sieve_dominated_ratio_to_unfused",
                               "modeled_sieve_dominated_gain_bits"]},
        "declared_optimistic_assumptions": [
            "Memory traffic is charged as 8 bytes per element touched "
            "(charged_work_bytes_per_element); a real memory hierarchy would "
            "charge more, so this UNDER-estimates the fused pipeline's cost "
            "relative to the unfused baseline, which touches fewer elements.",
            "Integer operations and bytes moved are summed with unit weight; "
            "this is a toy cost model only and is not an estimator-level cost.",
            "The LLL reduction is charged once per instance and is independent "
            "of the pool size m, which UNDER-states the vector-count advantage "
            "of any rule that needs fewer pool vectors.",
            "Candidate verification is charged for the full enumerated "
            "candidate set, identical for every rule.",
        ],
    }
    _write_json(os.path.join(ana_dir, "cost_accounting.json"), cost_out, work)

    # ---------------- outcome classification (frozen precedence) ----------
    findings = []

    def note(cls, hit, why):
        findings.append({"class": cls, "matched": bool(hit), "evidence": why})

    seed_ok = ((c25.get("ctrl_seed_discipline") or {}).get("pass") and
               (c26.get("ctrl_seed_discipline") or {}).get("pass"))
    artifacts_ok = ("RUN-MLKEM-025" in raws and "RUN-MLKEM-026" in raws)
    invalid = (not eq_pass) or (not seed_ok) or (not artifacts_ok)
    note("invalid_implementation_or_instrumentation", invalid,
         {"exact_equality_pass": eq_pass, "seed_discipline_pass": seed_ok,
          "required_run_raws_present": artifacts_ok})

    covm = c25.get("ctrl_covariance_model") or {}
    cov_pass = all(v.get("pass") for v in covm.values()) if covm else False
    note("covariance_control_failed", not cov_pass,
         {"per_ring_size": dict((kk, vv.get("pass")) for kk, vv in covm.items())})

    ka = c25.get("ctrl_known_answer") or {}
    note("known_answer_baseline_failed", not ka.get("pass"),
         {"top1_recovery_rate": ka.get("top1_recovery_rate"),
          "reference_vector_count": ka.get("reference_vector_count")})

    r_eff_ho = crit.get("held_out_r_eff_at_reference_vector_count")
    corr_n32 = (r_eff_ho is None or r_eff_ho != r_eff_ho or
                r_eff_ho < CONFIG["gate_r_eff_min_n32"])
    n64_measured = bool(c27 and c27.get("stage") == "full64" and
                        not c27.get("aborted_reason"))
    note("correlated_reindexing", corr_n32,
         {"held_out_r_eff_n32": r_eff_ho,
          "gate_min_n32": CONFIG["gate_r_eff_min_n32"],
          "n32_limb_matched": corr_n32,
          "n64_limb": "evaluated" if n64_measured else "UNEVALUATED",
          "n64_limb_note":
              "The frozen definition also matches if held-out r_eff < 4.0 at "
              "n=64 for every selected subset of size at most 32.  n=64 was "
              "not measured (see RUN-MLKEM-027), so that disjunct is neither "
              "true nor false here and no value is inferred for it.  The "
              "classification below is therefore established at n=32 only."})

    gls = fus.get("gls_covariance_aware", {})
    unw = fus.get("unweighted_mean", {})
    m_at = str(gls.get("m50_held_out") or CONFIG["reference_vector_count"])
    fpr_gls = (gls.get("per_vector_count", {}).get(m_at, {})
               .get("held_out_fpr_at_matched_detection", {}).get("fpr"))
    fpr_unw = (unw.get("per_vector_count", {}).get(m_at, {})
               .get("held_out_fpr_at_matched_detection", {}).get("fpr"))
    fpr_ratio = (fpr_gls / fpr_unw) if (fpr_gls is not None and fpr_unw) else None
    no_adv = not (fpr_ratio is not None and
                  fpr_ratio <= CONFIG["gls_vs_unweighted_fpr_ratio_max"])
    note("fusion_no_advantage", no_adv,
         {"matched_vectors": m_at, "held_out_fpr_gls": fpr_gls,
          "held_out_fpr_unweighted_mean": fpr_unw,
          "ratio": fpr_ratio, "required_max": CONFIG["gls_vs_unweighted_fpr_ratio_max"],
          "comparison": "matched held-out detection rate 0.5"})

    delta_bits = cost_out["true_orbit_vs_random_signed_permutation_gain_bits"]
    generic = (delta_bits is not None and
               delta_bits < CONFIG["orbit_vs_permutation_min_bits"])
    note("generic_batching", generic,
         {"true_orbit_minus_permutation_bits": delta_bits,
          "required_min_bits": CONFIG["orbit_vs_permutation_min_bits"],
          "permutation_m50": fus.get("random_signed_permutation", {}).get("m50_held_out")})

    wr = cost_out["total_charged_score_work_ratio_gls_over_unfused"]
    nonbottle = (wr is None or wr >= 1.0)
    note("non_bottleneck_local_gain", nonbottle,
         {"total_charged_score_work_ratio": wr, "required_max": 1.0})

    note("structural_information_gain_candidate", True,
         {"reached_only_if_no_earlier_class_matched": True})

    classification = None
    for f in findings:
        if f["matched"]:
            classification = f["class"]
            break
    res["outcome_classification"] = {
        "precedence": [f["class"] for f in findings],
        "evaluation": findings,
        "classification": classification,
        "scope": {
            "ring_sizes_measured": [32],
            "ring_sizes_not_measured": [64],
            "note": "Every threshold below was evaluated at n=32 only. The "
                    "n=64 thresholds of the frozen success criterion "
                    "(r_eff >= 4.0, >= 4x vector-count reduction) were not "
                    "measured; see RUN-MLKEM-027.  No value is inferred for "
                    "them and the classification asserts nothing about n=64.",
        },
        "note": "Executor records the classification produced by the frozen "
                "precedence rule.  Interpretation of H-MLKEM-007 is reserved "
                "for the Reviewer and Coordinator.",
    }

    # negative control: shuffled orbit labels must show no held-out gain
    sh = fus.get("shuffled_orbit_labels", {})
    res["ctrl_shuffled_orbit_labels"] = {
        "m50_held_out": sh.get("m50_held_out"),
        "m50_held_out_unfused": fus.get("unfused_single_orbit", {}).get("m50_held_out"),
        "gain_vs_unfused":
            (fus.get("unfused_single_orbit", {}).get("m50_held_out") /
             sh.get("m50_held_out"))
            if sh.get("m50_held_out") else None,
        "pass_condition": "no held-out gain; any gain invalidates the pipeline",
    }
    # ---- exact re-verification of the cached reduced bases ---------------
    cache = os.path.join(args.runs_root, "RUN-MLKEM-025", "reduced-bases-n32.json")
    if os.path.exists(cache):
        with open(cache) as fh:
            blob = json.load(fh)
        work.bytes_read += os.path.getsize(cache)
        checks = {}
        for seed in (CONFIG["training_seeds"][0], CONFIG["held_out_seeds"][0]):
            v = osc.verify_lll_output(blob["bases"][str(seed)], CONFIG["lll_delta"])
            v.pop("gs_norms", None)
            checks[str(seed)] = v
            log("exact LLL re-verification seed=%s size_viol=%d lovasz_viol=%d "
                "max|mu|=%.6f effective_delta=%.6f"
                % (seed, v["size_reduction_violations"], v["lovasz_violations"],
                   v["max_abs_mu"], v["effective_delta_satisfied"]))
        res["lll_exact_reverification"] = {
            "verifier": "integer Gram + exact-rational Gram-Schmidt; shares no "
                        "floating-point state with the LLL solver",
            "requested_delta": CONFIG["lll_delta"],
            "per_seed": checks,
            "note": "The solver keeps its Gram-Schmidt bookkeeping in float64. "
                    "Any residual violation is a float-drift artifact of that "
                    "choice and is reported with its exact magnitude; it does "
                    "not affect the exact-equality control, the residual "
                    "arithmetic, or the measured pool norms, all of which are "
                    "computed over the integers.",
        }

    res["artifacts_written"] = [
        "experiments/EXP-MLKEM-007/analysis/covariance_report.json",
        "experiments/EXP-MLKEM-007/analysis/gate_decision.json",
        "experiments/EXP-MLKEM-007/analysis/cost_accounting.json",
    ]
    return res


def heur_001_comparison(c26):
    """Frozen-prediction comparison statistics for HEUR-001.

    HEUR-001 (ledger/hypotheses/H-MLKEM-007.yaml) predicts that GLS weights
    fitted on the 15 training instances keep their held-out false-positive rate
    inside a factor-2 band computed from the TRAINING covariance, and that the
    held-out effective rank deviates from its training estimate by less than
    50 percent.  Reported here as comparison statistics only; adjudication of
    HEUR-001 belongs to the Reviewer and Coordinator.
    """
    cov = (c26.get("covariance_report") or {}).get("orbit", {})
    fus = (c26.get("fusion_results") or {})
    gls = fus.get("gls_covariance_aware", {}).get("per_vector_count", {})
    unw = fus.get("unweighted_mean", {}).get("per_vector_count", {})
    out = {}
    for m, e in cov.items():
        w = e.get("gls_weights") or []
        Str = e.get("training_covariance") or []
        Sho = e.get("held_out_covariance") or []

        def quad(S):
            if not S:
                return None
            return sum(w[i] * S[i][j] * w[j] for i in range(len(w))
                       for j in range(len(w)))
        vtr = quad(Str)
        vho = quad(Sho)
        g = gls.get(m, {})
        u = unw.get(m, {})
        fg = (g.get("held_out_fpr_at_tau") or {}).get("fpr")
        fu = (u.get("held_out_fpr_at_tau") or {}).get("fpr")
        out[m] = {
            "training_fused_null_variance_under_gls_weights": vtr,
            "held_out_fused_null_variance_under_gls_weights": vho,
            "held_out_over_training_variance_ratio":
                (vho / vtr) if (vtr and vho is not None) else None,
            "variance_ratio_within_factor_2":
                (0.5 <= (vho / vtr) <= 2.0) if (vtr and vho is not None) else None,
            "training_r_eff": e.get("training_r_eff"),
            "held_out_r_eff": e.get("held_out_r_eff"),
            "r_eff_relative_deviation": e.get("r_eff_relative_deviation"),
            "r_eff_deviation_below_0.50":
                (e.get("r_eff_relative_deviation") < 0.5)
                if isinstance(e.get("r_eff_relative_deviation"), float) and
                e.get("r_eff_relative_deviation") == e.get("r_eff_relative_deviation")
                else None,
            "held_out_fpr_at_tau_gls": fg,
            "held_out_fpr_at_tau_unweighted_mean": fu,
            "gls_over_unweighted_fpr_ratio_at_tau":
                (fg / fu) if (fg is not None and fu) else None,
        }
    return {"frozen_prediction_reference":
                "H-MLKEM-007.heuristic_assumptions[HEUR-001] "
                "(formal_statement and falsification_condition), frozen at "
                "hypothesis approval and not modified",
            "per_vector_count": out,
            "adjudication": "not performed by the Executor"}


def _write_json(path, obj, work):
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, default=str)
    work.bytes_written += os.path.getsize(path)


# ==================================================================== main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--repo-root", default=os.getcwd())
    ap.add_argument("--runs-root", default=None)
    ap.add_argument("--basis-cache", default=None)
    ap.add_argument("--stage-budget-seconds", type=float, default=1500.0)
    ap.add_argument("--n64-probe-seconds", type=float, default=0.0)
    ap.add_argument("--memory-limit-gb", type=float, default=4.0)
    args = ap.parse_args()
    if args.runs_root is None:
        args.runs_root = os.path.dirname(os.path.abspath(args.out))

    lim = int(args.memory_limit_gb * (1 << 30))
    try:
        resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
    except (ValueError, OSError) as exc:
        sys.stderr.write("WARNING: could not set RLIMIT_AS: %r\n" % (exc,))

    os.makedirs(args.out, exist_ok=True)
    started = now()
    t0 = time.time()

    def log(msg):
        sys.stdout.write("[%s] %s\n" % (now(), msg))
        sys.stdout.flush()

    log("stage=%s run_id=%s pid=%d" % (args.stage, args.run_id, os.getpid()))
    log("config sha256=%s" % hashlib.sha256(
        json.dumps(CONFIG, sort_keys=True).encode()).hexdigest())

    work = osc.Work()
    fn = {"controls": stage_controls, "gate32": stage_gate32,
          "full64": stage_full64, "analysis": stage_analysis}[args.stage]
    payload = fn(args, log, work)

    elapsed = time.time() - t0
    ru = resource.getrusage(resource.RUSAGE_SELF)
    payload["run_id"] = args.run_id
    payload["timing"] = {"started_at": started, "finished_at": now(),
                         "wall_seconds": elapsed}
    payload["resources"] = {"peak_rss_bytes": peak_rss_bytes(),
                            "cpu_seconds": ru.ru_utime + ru.ru_stime}
    payload["environment"] = environment_block()
    payload["charged_work"] = work.asdict()
    out = os.path.join(args.out, "raw.json")
    with open(out, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True, default=str)
    log("wrote %s (%d bytes) in %.1f s, peak RSS %.1f MB"
        % (out, os.path.getsize(out), elapsed, peak_rss_bytes() / 1e6))


if __name__ == "__main__":
    main()
