"""RED-TEAM DIAGNOSTIC (TASK-20260907-ee1ca7, joint J5).  NOT A RUN RECORD.

THE MISSING NULL.  Write the measured quantity as a difference of two losses:

    margin = TopShare(T_sel) - StaticCov(T, r)
           = [ TopShare(T) - StaticCov(T, r) ]      <- ESTIMATOR LOSS
             - [ TopShare(T) - TopShare(T_sel) ]    <- HALVING LOSS

Both declared controls of amendment Section 5 act on the FIRST term only.
NULL_A_G3 destroys the evidence/size correspondence, which drives the
estimator loss to its uninformative maximum.  DECAY_G3 grows r, which shrinks
the estimator loss.  NEITHER touches the halving loss -- and the halving loss
is the term that carries essentially all of the a-dependence, hence the
crossing the claim is about.

This diagnostic supplies a null object of the same shape for the SECOND term.
NULL_T (tail null): keep N, the map, the DP set, the pool draw, w(d), the
tie-break, the selected table, the total reachable basin mass M and the DP
count D all EXACTLY as measured; replace only the SHAPE of the basin-size
multiset by a uniform balls-in-bins allocation of the same M over the same D
bins, assigned to DPs IN THE SAME RANK ORDER as the true sizes so that the
evidence/size rank correspondence -- the thing NULL_A already controls -- is
preserved rather than destroyed a second time.

If G3 still PASSES under NULL_T, the PASS is not attributable to basin-size
tail concentration and the mechanism the amendment names is not what produces
it.  If G3 FAILS under NULL_T at every a, the tail concentration is
load-bearing and the claimed mechanism survives a control it was never given.

Writes only under the red-team task directory.  Changes no verdict.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, *([".."] * 8)))
sys.path.insert(0, os.path.join(_REPO, "experiments", "EXP-ECDLP-612fb1"))

from source_v3 import g3_predicate as G  # noqa: E402

N_BITS, R = 24, 2
A_GRID = (0.0625, 0.125, 0.1875, 0.25)
SEEDS = (1, 2, 3, 4, 5)
NULL_T_STREAM = 900          # declared here, before the run, and not changed after


def one(a: float, seed: int) -> dict:
    P = G.make_params(n_bits=N_BITS, a=a, seed=seed)
    T, T_sel = P.T, G.t_sel_of(P.T)
    basins = G.exact_basins(P)

    # --- the producer's own path, unchanged: pool -> weight -> selection ----
    ev = G.build_pool(P, R)
    keys = G.tiebreak_keys(P, ev.size())
    sel = G.select_static_indices(G.selection_weight(ev, P.W), keys, T)
    table = G.selected_dps(ev, sel["indices"])

    sizes = np.asarray(basins.size, dtype=np.int64)
    D = int(sizes.size)
    M = int(sizes.sum())
    N = int(P.N)
    idx_table = basins.index_of(np.asarray(table, dtype=np.int64))

    srt = np.sort(sizes)[::-1]
    top_T = float(srt[:T].sum()) / N
    top_T_sel = float(srt[:T_sel].sum()) / N
    cov = float(sizes[idx_table].sum()) / N

    # --- NULL_T: same M, same D, flat allocation, SAME RANK ASSIGNMENT ------
    rng = np.random.default_rng(NULL_T_STREAM + seed)
    null_sizes = rng.multinomial(M, np.full(D, 1.0 / D))
    null_sorted = np.sort(null_sizes)[::-1]
    rank_of_dp = np.argsort(np.lexsort((basins.dps, -sizes)))  # 0 = largest true basin
    null_size_of_dp = null_sorted[rank_of_dp]

    ntop_T = float(null_sorted[:T].sum()) / N
    ntop_T_sel = float(null_sorted[:T_sel].sum()) / N
    ncov = float(null_size_of_dp[idx_table].sum()) / N

    del basins, sizes
    return {
        "a": a, "seed": seed, "N": N, "T": T, "T_sel": T_sel, "r": R,
        "dp_count_D": D, "reachable_basin_mass_M": M, "M_over_N": M / N,
        "observed": {
            "top_share_T": top_T, "top_share_T_sel": top_T_sel,
            "static_cov": cov,
            "margin": top_T_sel - cov,
            "estimator_loss": top_T - cov,
            "halving_loss": top_T - top_T_sel,
            "g3": bool(top_T_sel - cov >= 0.0),
        },
        "null_T": {
            "top_share_T": ntop_T, "top_share_T_sel": ntop_T_sel,
            "static_cov": ncov,
            "margin": ntop_T_sel - ncov,
            "estimator_loss": ntop_T - ncov,
            "halving_loss": ntop_T - ntop_T_sel,
            "g3": bool(ntop_T_sel - ncov >= 0.0),
        },
    }


def main():
    t0 = time.time()
    rows, cells = [], []
    for a in A_GRID:
        for s in SEEDS:
            row = one(a, s)
            rows.append(row)
            print("a=%-7s s=%d  obs margin=%+.9f (halv %.6f, est %.6f)  "
                  "NULL_T margin=%+.9f (halv %.6f, est %.6f)"
                  % (a, s, row["observed"]["margin"], row["observed"]["halving_loss"],
                     row["observed"]["estimator_loss"], row["null_T"]["margin"],
                     row["null_T"]["halving_loss"], row["null_T"]["estimator_loss"]),
                  flush=True)
    for a in A_GRID:
        sub = [r for r in rows if r["a"] == a]
        cells.append({
            "a": a, "N": 2 ** N_BITS, "r": R,
            "observed_pass_count_of_5": sum(r["observed"]["g3"] for r in sub),
            "null_T_pass_count_of_5": sum(r["null_T"]["g3"] for r in sub),
            "observed_margin_mean": sum(r["observed"]["margin"] for r in sub) / len(sub),
            "null_T_margin_mean": sum(r["null_T"]["margin"] for r in sub) / len(sub),
            "observed_halving_loss_mean": sum(r["observed"]["halving_loss"] for r in sub) / len(sub),
            "null_T_halving_loss_mean": sum(r["null_T"]["halving_loss"] for r in sub) / len(sub),
            "observed_estimator_loss_mean": sum(r["observed"]["estimator_loss"] for r in sub) / len(sub),
            "null_T_estimator_loss_mean": sum(r["null_T"]["estimator_loss"] for r in sub) / len(sub),
        })
    out = os.path.join(_HERE, "tail_null.json")
    json.dump({
        "diagnostic": "red-team NULL_T tail null, TASK-20260907-ee1ca7 joint J5",
        "is_a_run_record": False, "changes_any_verdict": False,
        "declared_before_the_run": {
            "null_stream_seed": NULL_T_STREAM,
            "prediction": "if the amendment's stated mechanism is what produces the "
                          "PASS, NULL_T must FAIL at every a including a = 1/16",
        },
        "wall_seconds_total": round(time.time() - t0, 3),
        "per_cell": cells, "per_seed_rows": rows,
    }, open(out, "w"), indent=1)
    print("\n".join("a=%-7s observed %d/5   NULL_T %d/5" %
                    (c["a"], c["observed_pass_count_of_5"], c["null_T_pass_count_of_5"])
                    for c in cells))
    print("wrote", out, "%.1fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
