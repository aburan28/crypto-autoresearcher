"""PHASE A driver: blind re-derivation of (d_ff, d_lf) and the d_lf slope.

Reads nothing but the parameters transcribed in params.py (from the handoff's
review_plan.blind_rederivation.parameters).  Writes tables/rederivation_results.json.
"""
import json
import sys
import time

sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/"
                   "pfdr-battery-20260904/reviews/TASK-20260904-42b33a/scripts")

from hky import (SquarefreeRing, semaev_S3_digit, deg_poly, closure_B, dim_leq,
                 zero_set, ideal_cap_dim, eval_rank)
from params import INSTANCES, S_VALUES, D_MAX
from stats_ols import ols, outcome_rule

OUT = ("/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/"
       "reviews/TASK-20260904-42b33a/tables/rederivation_results.json")


def run_one(p, a, b, xR, s):
    n = 2 * s
    t0 = time.time()
    gen = semaev_S3_digit(p, a, b, xR, s)
    ring = SquarefreeRing(n, p, D_MAX)
    Z = zero_set(gen, n, p)
    rec = {
        "s": s, "n": n, "p": p, "a": a, "b": b, "x_R": xR,
        "deg_S_tilde": deg_poly(gen), "n_terms_S_tilde": len(gen),
        "solutions_Z": [{"ell1": z & ((1 << s) - 1), "ell2": z >> s} for z in sorted(Z)],
        "num_solutions": len(Z),
        "per_degree": {}, "fall_history": [], "cols_at_Dmax": ring.ncols(min(D_MAX, n)),
    }
    prev_dim = 0
    for D in range(0, D_MAX + 1):
        cap = ideal_cap_dim(Z, ring, D, p)
        W, rounds, prod = closure_B(ring, gen, D, ideal_dim=cap)
        lhs = dim_leq(W, ring, D, D - 1) if D > 0 else 0
        fall = bool(D > 0 and lhs > prev_dim)
        rec["per_degree"][str(D)] = {
            "N_cols": ring.ncols(min(D, n)),
            "dim_V_FD": W.dim,
            "dim_ideal_cap": cap,
            "dim_V_FD_cap_B_leq_Dm1": lhs,
            "dim_V_FDm1": prev_dim,
            "fall": fall,
            "rounds_executed": rounds,
            "productive_rounds": prod,
            "iteration_count": 1 + prod,
            "saturates_ideal_cap": bool(W.dim == cap),
        }
        if fall:
            rec["fall_history"].append(D)
        prev_dim = W.dim
    # censoring certificate (own derivation; see report joint V1)
    capmax = rec["per_degree"][str(D_MAX)]["dim_ideal_cap"]
    vmax = rec["per_degree"][str(D_MAX)]["dim_V_FD"]
    rk6 = eval_rank(Z, ring, D_MAX - 1, p)
    rec["certificate"] = {
        "V_at_Dmax_equals_ideal_cap": bool(vmax == capmax),
        "eval_rank_at_Dmax_minus_1": rk6,
        "num_solutions": len(Z),
        "eval_surjective_from_B_leq_6": bool(rk6 == len(Z)),
        "structural_Dmax_ge_n_plus_1": bool(D_MAX >= n + 1),
    }
    certified = rec["certificate"]["V_at_Dmax_equals_ideal_cap"] and \
        rec["certificate"]["eval_surjective_from_B_leq_6"]
    rec["certificate"]["no_fall_above_Dmax_certified"] = bool(certified)
    rec["right_censored"] = not certified
    fh = rec["fall_history"]
    rec["d_ff"] = fh[0] if fh else None
    rec["d_lf"] = fh[-1] if fh else None
    rec["single_fall"] = bool(len(fh) == 1)
    rec["seconds"] = round(time.time() - t0, 2)
    return rec


def main():
    results = []
    for (p, cs, a, b, ts, xR) in INSTANCES:
        for s in S_VALUES:
            rec = run_one(p, a, b, xR, s)
            rec["curve_seed"] = cs
            rec["target_seed"] = ts
            results.append(rec)
            print(f"p={p} curve={cs} target={ts} s={s}: falls={rec['fall_history']} "
                  f"(d_ff,d_lf)=({rec['d_ff']},{rec['d_lf']}) censored={rec['right_censored']} "
                  f"|Z|={rec['num_solutions']} t={rec['seconds']}s", flush=True)

    # ---------------- OLS fits on d_lf (and d_ff) over s = 2..5
    used = [r for r in results if not r["right_censored"] and r["d_lf"] is not None]
    fits = {}
    for key in ("d_lf", "d_ff"):
        xs = [r["s"] for r in used]
        ys = [r[key] for r in used]
        fits[key + "_per_draw"] = ols(xs, ys)
        # per (s, p) cell means
        cells = {}
        for r in used:
            cells.setdefault((r["s"], r["p"]), []).append(r[key])
        cx = sorted(cells)
        fits[key + "_per_cell"] = ols([c[0] for c in cx],
                                      [sum(cells[c]) / len(cells[c]) for c in cx])
        fits[key + "_per_cell_detail"] = {f"s{c[0]}_p{c[1]}":
                                          {"n": len(cells[c]),
                                           "mean": sum(cells[c]) / len(cells[c]),
                                           "values": sorted(set(cells[c]))}
                                          for c in cx}
        # per s means
        per_s = {}
        for r in used:
            per_s.setdefault(r["s"], []).append(r[key])
        sx = sorted(per_s)
        fits[key + "_per_s"] = ols(sx, [sum(per_s[k]) / len(per_s[k]) for k in sx])
        fits[key + "_per_s_detail"] = {str(k): {"n": len(per_s[k]),
                                                "mean": sum(per_s[k]) / len(per_s[k]),
                                                "values": sorted(set(per_s[k]))}
                                       for k in sx}
    for k in list(fits):
        if k.endswith("_per_draw") or k.endswith("_per_cell") or k.endswith("_per_s"):
            fits[k]["outcome_rule"] = outcome_rule(fits[k]["ci95"])

    # flat-run check for the Outcome III second clause
    per_s_vals = {}
    for r in used:
        per_s_vals.setdefault(r["s"], set()).add(r["d_lf"])
    flat_runs = []
    ss = sorted(per_s_vals)
    cur = [ss[0]]
    for i in range(1, len(ss)):
        same = (per_s_vals[ss[i]] == per_s_vals[ss[i - 1]] and len(per_s_vals[ss[i]]) == 1)
        if same and ss[i] == ss[i - 1] + 1:
            cur.append(ss[i])
        else:
            flat_runs.append(cur)
            cur = [ss[i]]
    flat_runs.append(cur)
    longest_flat = max(len(x) for x in flat_runs)

    out = {
        "results": results,
        "fits": fits,
        "n_used_in_fits": len(used),
        "n_censored_excluded": sum(1 for r in results if r["right_censored"]),
        "longest_flat_run_in_s": longest_flat,
        "flat_runs": flat_runs,
        "outcome_III_flat_clause_met": bool(longest_flat >= 4),
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("\nwrote", OUT)
    for k in ("d_lf_per_draw", "d_lf_per_cell", "d_lf_per_s",
              "d_ff_per_draw", "d_ff_per_cell", "d_ff_per_s"):
        f = fits[k]
        print(f"{k:16s} n={f['n']:3d} slope={f['slope']:.6f} "
              f"ci95=[{f['ci95'][0]:.4f}, {f['ci95'][1]:.4f}] "
              f"s2={f['residual_variance']:.6f} rule={f['outcome_rule']}")
    print("longest flat run in s:", longest_flat)


if __name__ == "__main__":
    main()
