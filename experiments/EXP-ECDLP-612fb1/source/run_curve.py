"""Stage 3 certified curve cell of EXP-ECDLP-612fb1: one seed s in {1, 2, 3}.

Same arm engine as the generic cells (instrument.run_arm), same seed
offsets, a = 1/4, U = 8T, arms STATIC(T), STATIC(T/2), RESEL-L(T),
RESEL-L(T/2), NULL-A(T/2), RHO.  Every solved target emits a discrete_log
certificate re-verified by verify_certificate (independent code) and
checked against the seeded logarithm, which only the checker reads.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import instrument as I  # noqa: E402
import curve as C  # noqa: E402
import verify_certificate as V  # noqa: E402

U_MULT_CURVE = 8


def log(msg: str) -> None:
    print(msg, flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--curve-record", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--no-basins", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    rec = json.load(open(args.curve_record))
    E = C.Curve(p=rec["p"], a=rec["a"], b=rec["b"], N=rec["N"], G=tuple(rec["P"]))
    ver = V.verify_curve_record(rec)
    log(f"[curve] {rec['curve_id']} p={E.p} a={E.a} b={E.b} N={E.N} P={E.G} independent verification={ver['verified']}")
    if not ver["verified"]:
        raise SystemExit("curve record failed independent verification")
    P = I.Params(n_bits=24, a=0.25, seed=args.seed, N_override=E.N)
    P.U_max = U_MULT_CURVE * P.T
    walk = C.CurveWalk(E, P)
    params = P.describe()
    params.update({"curve_id": rec["curve_id"], "p": E.p, "curve_a": E.a, "curve_b": E.b, "field_bits": rec["field_bits"],
                   "walk": "r-adding, r = 32, M_j = [m_j]P", "multipliers_m_j": walk.m,
                   "seeds": {**params["seeds"], "multiplier_stream": [P.seed, 7], "curve_search_seed": 1000}})
    log(f"[params] {json.dumps(params)}")
    summary = {"params": params, "curve": {**rec, "verification": ver}}
    raw = {"params": params, "curve": rec}

    # ---------------------------------------------------------------- exact basins (optional)
    basins = None
    oracle_share = None
    if not args.no_basins:
        tb = time.time()
        basins = C.exact_basins_curve(E, walk)
        sizes = basins.size
        W2 = P.W ** 2
        ref = I.borel_survival(1 - P.theta, int(min(400 * W2, E.N)))
        slope, npts = I.survival_slope(sizes, 10, int(W2 / 4))
        slope_ref, _ = I.survival_slope(None, 10, int(W2 / 4), ref_survival=ref)
        cut = I.fit_cutoff(sizes, P.theta, int(W2 / 4))
        xstar, cmax = I.c_max(P.a)
        top = {t: basins.top_share(t) for t in (P.T // 4, P.T // 2, 3 * P.T // 4, P.T, 2 * P.T)}
        oracle_share = top
        band = I.borel_max_band(1 - P.theta, int(round(E.N / P.W)), int(min(400 * W2, E.N)))
        hist_vals, hist_counts = np.unique(sizes, return_counts=True)
        summary["basins"] = {"n_dps": int(len(sizes)), "cycle_mass": basins.cycle_mass,
                             "cycle_mass_frac": basins.cycle_mass / E.N, "capped_mass": basins.capped_mass,
                             "capped_mass_frac": basins.capped_mass / E.N,
                             "survival_slope": slope, "MODELED_borel_survival_slope_same_estimator": slope_ref,
                             "cutoff": cut, "top_T_share": top[P.T], "top_share_by_t": {str(k): v for k, v in top.items()},
                             "C_max_model": cmax, "top_T_share_over_C_max": top[P.T] / cmax,
                             "largest_basin": int(sizes.max()), "largest_basin_borel_99_band": list(band),
                             "largest_basin_in_band": bool(band[0] <= int(sizes.max()) <= band[1]),
                             "basins_seconds": time.time() - tb}
        log(f"[basins] {json.dumps(summary['basins'])}")
        with gzip.open(os.path.join(args.outdir, "basin_histogram.json.gz"), "wt") as fh:
            json.dump({"curve_id": rec["curve_id"], "N": E.N, "a": P.a, "seed": P.seed, "W": P.W, "cap": P.cap,
                       "cycle_mass": basins.cycle_mass, "capped_mass": basins.capped_mass, "n_dps": int(len(sizes)),
                       "histogram": {"size": hist_vals.tolist(), "count": hist_counts.tolist()}}, fh)

    # ---------------------------------------------------------------- precomputation pool (r = 2), logs known
    tp = time.time()
    rng_pre = np.random.default_rng(P.seed)
    dps, S, h, logs = [], [], [], []
    index = {}
    walks = P_cost = capped = inf_hits = 0
    batch = 512
    target_distinct = 2 * P.T
    while len(dps) < target_distinct:
        rs = rng_pre.integers(1, E.N, size=batch, dtype=np.int64)
        pts = [E.mul(int(r), E.G) for r in rs]
        x0 = np.asarray([q[0] for q in pts], dtype=np.int64)
        y0 = np.asarray([q[1] for q in pts], dtype=np.int64)
        term, length, sc, ih = walk.walk(x0, y0, rs)
        inf_hits += ih
        for i in range(batch):
            walks += 1
            t = int(term[i]); L = int(length[i]); P_cost += L
            if t < 0:
                capped += 1
            else:
                j = index.get(t)
                if j is None:
                    index[t] = len(dps); dps.append(t); S.append(float(L)); h.append(1); logs.append(int(sc[i]))
                else:
                    S[j] += L; h[j] += 1
                    # consistency: the known log of an existing entry must agree
                    if logs[j] != int(sc[i]):
                        raise SystemExit(f"precomputation log inconsistency at DP {t}")
            if len(dps) == target_distinct:
                break
    pools = {2 * P.T: I.PoolSnapshot(r=2, dps=dps, S=S, h=h, walks=walks, P_cost=P_cost, capped_walks=capped, logs=logs)}
    summary["pools"] = {"2": {"distinct_dps": len(dps), "walks": walks, "P_group_ops": P_cost, "capped_walks": capped,
                              "walks_reaching_infinity": inf_hits, "P_over_sqrt_NT": P_cost / math.sqrt(E.N * P.T),
                              "restart_scalar_mults": walks, "restart_group_ops": walks * P.restart_cost,
                              "seconds": time.time() - tp}}
    log(f"[pools] {json.dumps(summary['pools'])}")

    # ---------------------------------------------------------------- targets (seeded logs sealed for the checker)
    tt = time.time()
    rng_t = np.random.default_rng(P.seed_targets)
    U = P.U_max
    secret_x = rng_t.integers(1, E.N, size=U, dtype=np.int64)          # read ONLY by the checker below
    c = rng_t.integers(0, E.N, size=(U, P.k), dtype=np.int64)
    Q = [E.mul(int(x), E.G) for x in secret_x]                          # instance generation
    starts_x = np.empty((U, P.k), dtype=np.int64)
    starts_y = np.empty((U, P.k), dtype=np.int64)
    inf_starts = 0
    for u in range(U):
        for j in range(P.k):
            S0 = E.add(Q[u], E.mul(int(c[u, j]), E.G))
            if S0 is None:
                inf_starts += 1
                S0 = (-1, -1)
            starts_x[u, j], starts_y[u, j] = S0
    term, length, sc, ih = walk.walk(starts_x.reshape(-1), starts_y.reshape(-1), c.reshape(-1))
    term = term.reshape(U, P.k); length = length.reshape(U, P.k); walk_scalar = sc.reshape(U, P.k)
    summary["online_walks"] = {"count": int(term.size), "capped_fraction_all_walks": float((term < 0).mean()),
                               "walks_reaching_infinity": int(ih), "starts_at_infinity": inf_starts,
                               "mean_length_all_walks": float(length.mean()), "mean_length_over_W": float(length.mean() / P.W),
                               "restart_scalar_mults_generated": int(U * P.k), "seconds": time.time() - tt}
    if basins is not None:
        # cross-check the walker against the exact tables on every start
        keys0 = walk.key(starts_x.reshape(-1), starts_y.reshape(-1))
        idx0 = np.searchsorted(basins.keys, keys0)
        ok = (idx0 < len(basins.keys)) & (basins.keys[np.minimum(idx0, len(basins.keys) - 1)] == keys0)
        d = basins.dist[idx0[ok]].astype(np.int64)
        reach = d <= P.cap
        t_exp = np.where(reach, basins.keys[basins.first_dp[idx0[ok]]], -1)
        l_exp = np.where(reach, d, P.cap)
        agree = bool(np.array_equal(t_exp, term.reshape(-1)[ok]) and np.array_equal(l_exp, length.reshape(-1)[ok]))
        summary["walker_vs_exact_basins_agree"] = agree
    log(f"[walks] {json.dumps(summary['online_walks'])} walker_vs_basins={summary.get('walker_vs_exact_basins_agree')}")

    # ---------------------------------------------------------------- arms
    T = P.T
    arms = [I.ArmConfig(name="STATIC(T)", mode="static", t_sel=T),
            I.ArmConfig(name="STATIC(T/2)", mode="static", t_sel=T // 2),
            I.ArmConfig(name="RESEL-L(T)", mode="resel_lower", t_sel=T, twin="STATIC(T)"),
            I.ArmConfig(name="RESEL-L(T/2)", mode="resel_lower", t_sel=T // 2, twin="STATIC(T/2)"),
            I.ArmConfig(name="NULL-A(T/2)", mode="null_a", t_sel=T // 2, twin="STATIC(T/2)"),
            I.ArmConfig(name="RHO", mode="rho", t_sel=0)]
    results = {}
    summary["arms"] = {}
    raw["arms"] = {}
    certs_all = []
    cert_stats = {"solved_total": 0, "passed": 0, "failed": 0, "seeded_log_passed": 0, "seeded_log_failed": 0,
                  "per_arm": {}, "rho_collisions_no_certificate": 0}
    G_list = [E.G[0], E.G[1]]
    for cfg in arms:
        ta = time.time()
        res = I.run_arm(P, cfg, pools, term, length, basins, oracle_share, None,
                        walk_scalar=walk_scalar, group_order=E.N)
        results[cfg.name] = res
        per_round = []
        for r_ in res.rounds:
            p_, lo, hi = I.wilson(r_["hits"], r_["walks"])
            r_ = dict(r_); r_["hit_rate_wilson95"] = [lo, hi]; per_round.append(r_)
        eps_ss = {"4T": float(res.solved[2 * T:4 * T].mean()), "8T": float(res.solved[6 * T:8 * T].mean())}
        eps_cum = {"4T": float(res.solved[:4 * T].mean()), "8T": float(res.solved[:8 * T].mean())}
        # certificates
        certs = []
        n_pass = n_fail = n_seed_ok = n_seed_bad = 0
        if cfg.mode == "rho":
            cert_stats["rho_collisions_no_certificate"] += int(res.solved.sum())
        else:
            for u in np.flatnonzero(res.solved):
                k = int(res.k_found[u])
                cert = {"kind": "discrete_log", "curve_id": rec["curve_id"], "P": G_list, "Q": [Q[u][0], Q[u][1]], "k": k,
                        "target": int(u), "arm": cfg.name}
                v = V.verify_discrete_log(cert, {"p": E.p, "a": E.a, "b": E.b, "N": E.N, "curve_id": rec["curve_id"]})
                cert["verified"] = v["verified"]
                cert["verifier"] = "verify_certificate.verify_discrete_log (independent Montgomery ladder)"
                cert["reason"] = v["reason"]
                seed_ok = (k == int(secret_x[u]))                   # checker-only read of the seeded logarithm
                cert["seeded_log_match"] = bool(seed_ok)
                n_pass += int(v["verified"]); n_fail += int(not v["verified"])
                n_seed_ok += int(seed_ok); n_seed_bad += int(not seed_ok)
                certs.append(cert)
            cert_stats["solved_total"] += int(res.solved.sum())
            cert_stats["passed"] += n_pass; cert_stats["failed"] += n_fail
            cert_stats["seeded_log_passed"] += n_seed_ok; cert_stats["seeded_log_failed"] += n_seed_bad
        cert_stats["per_arm"][cfg.name] = {"solved": int(res.solved.sum()), "certificates": len(certs),
                                           "passed": n_pass, "failed": n_fail, "seeded_log_matches": n_seed_ok}
        certs_all.extend(certs)
        summary["arms"][cfg.name] = {
            "config": {"mode": cfg.mode, "t_sel": cfg.t_sel, "r": cfg.r, "R": T, "twin": cfg.twin},
            "rounds": per_round, "eps_ss": eps_ss, "eps_cum": eps_cum,
            "solved_total": int(res.solved.sum()), "group_ops_total": int(res.steps.sum()),
            "L_mean_per_target": float(res.steps.mean()),
            "L_mean_per_solved_target": float(res.steps[res.solved].mean()) if res.solved.any() else None,
            "restarts_total": int(res.used.sum()), "restart_group_ops_total": float(res.used.sum() * P.restart_cost),
            "lookups_total": int(sum(r_["lookups"] for r_ in res.rounds)),
            "capped_walks_used": int(sum(r_["capped_walks_used"] for r_ in res.rounds)),
            "capped_walk_fraction_used": float(sum(r_["capped_walks_used"] for r_ in res.rounds) / max(1, res.used.sum())),
            "reselection_int_ops_total": int(res.reselection_ops_total),
            "S_bits": res.S_bits, "S_peak_bits": res.S_peak_bits, "max_pool_entries": res.max_pool,
            "selector_verified_against_numpy": res.selector_verified,
            "certificates": cert_stats["per_arm"][cfg.name],
            "certificate_scalar_mults": len(certs),
            "seconds": time.time() - ta}
        raw["arms"][cfg.name] = {"config": summary["arms"][cfg.name]["config"],
                                 "walks_used": res.used.tolist(), "solved": res.solved.astype(int).tolist(),
                                 "hit_entry": res.hit_dp.tolist(), "k_found": res.k_found.tolist(),
                                 "steps_per_walk": [[int(length[u, j]) if j < res.used[u] else None for j in range(P.k)] for u in range(U)],
                                 "group_ops": res.steps.tolist(), "rounds": per_round, "certificates": certs}
        log(f"[arm] {cfg.name}: solved={int(res.solved.sum())}/{U} eps_ss(8T)={eps_ss['8T']:.4f} p_last={per_round[-1]['hit_rate']:.4f} "
            f"certs pass/fail={n_pass}/{n_fail} seeded-log ok={n_seed_ok} ({time.time() - ta:.1f}s)")
    cert_stats["pass_count_equals_solved_count"] = (cert_stats["passed"] == cert_stats["solved_total"] and cert_stats["failed"] == 0)
    cert_stats["seeded_log_all_match"] = (cert_stats["seeded_log_passed"] == cert_stats["solved_total"])
    cert_stats["verifier"] = "experiments/EXP-ECDLP-612fb1/source/verify_certificate.py (no code shared with the walk)"
    cert_stats["note_rho"] = ("RHO hits are collisions among a target's own walks Q_u + [c]P; such a collision yields "
                              "(c + s - c' - s') P = O and no logarithm, so RHO emits no certificate on the curve")
    summary["certificates"] = cert_stats
    with open(os.path.join(args.outdir, "certificates.json"), "w") as fh:
        json.dump({"curve": rec, "stats": cert_stats, "certificates": certs_all}, fh)

    checks = {"round0_identity": {}, "exceedance": {}}
    for cfg in arms:
        if cfg.twin is None:
            continue
        me, tw_ = results[cfg.name], results[cfg.twin]
        checks["round0_identity"][cfg.name] = bool(np.array_equal(me.used[:T], tw_.used[:T]) and np.array_equal(me.solved[:T], tw_.solved[:T])
                                                   and np.array_equal(me.hit_dp[:T], tw_.hit_dp[:T]) and np.array_equal(me.steps[:T], tw_.steps[:T]))
        if basins is not None and cfg.mode in ("resel_lower", "null_a"):
            ex = [r_.get("exact_exceeds_oracle", False) for r_ in results[cfg.name].rounds]
            checks["exceedance"][cfg.name] = {"any_exact_exceedance": bool(any(ex)),
                                              "max_exact_minus_oracle": max(r_["exact_coverage"] - r_["oracle_share"] for r_ in results[cfg.name].rounds)}
    summary["checks"] = checks
    summary["headline_metrics"] = {"eps_ss_8T_STATIC_T": summary["arms"]["STATIC(T)"]["eps_ss"]["8T"],
                                   "eps_ss_8T_RESEL_L_T2": summary["arms"]["RESEL-L(T/2)"]["eps_ss"]["8T"],
                                   "certificates_passed": cert_stats["passed"], "solved_total": cert_stats["solved_total"]}
    summary["cost_table"] = {"MEASURED": {n: {"walk_group_ops": summary["arms"][n]["group_ops_total"],
                                              "restarts": summary["arms"][n]["restarts_total"],
                                              "restart_group_ops": summary["arms"][n]["restart_group_ops_total"],
                                              "lookups": summary["arms"][n]["lookups_total"],
                                              "reselection_int_ops": summary["arms"][n]["reselection_int_ops_total"],
                                              "certificate_scalar_mults": summary["arms"][n]["certificate_scalar_mults"],
                                              "S_bits": summary["arms"][n]["S_bits"], "S_peak_bits": summary["arms"][n]["S_peak_bits"],
                                              "P_group_ops": P_cost} for n in summary["arms"]},
                             "MODELED": {"C_max(1/4)": I.c_max(0.25)[1], "restart_cost_formula": "1.5 ceil(log2 N) per online walk",
                                         "unit_note": "one group operation = one affine point addition (about 1 inversion + 3 mults); not converted"}}
    summary["elapsed_seconds"] = time.time() - t0
    with open(os.path.join(args.outdir, "cost_table.json"), "w") as fh:
        json.dump(summary["cost_table"], fh, indent=1)
    with open(os.path.join(args.outdir, "curve_record.json"), "w") as fh:
        json.dump({**rec, "verification_in_this_run": ver}, fh, indent=1)
    with open(os.path.join(args.outdir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    with open(os.path.join(args.outdir, "raw-result.json"), "w") as fh:
        json.dump(raw, fh)
    log(f"[checks] {json.dumps(checks)}")
    log(f"[certificates] {json.dumps({k: v for k, v in cert_stats.items() if k != 'per_arm'})}")
    log(f"[done] {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
