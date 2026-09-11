#!/usr/bin/env python3
"""J2 main recomputation: Stage B'' 200-cell grid.

For every (n_bits, seed, a) cell:
  - accounting identity  sum_d b(d) + cycle_mass + capped_mass == N  (exact int;
    sum_d b(d) recomputed from raw basin_sizes, masses from summary)
  - residual_fraction == (cycle_mass + capped_mass)/N
  - cap == ceil(8*W), W = sqrt(a*N/T)
  - shares top-T_sel / T / T/4 / T/8 recomputed from raw basin_sizes
  - cov_static recomputed from raw static_T_r2_dps + basin sizes
  - margin identity  margin == share_top_Tsel - cov_static
  - STATIC(T) selection recomputed from pool (S,h,W): top-T weights, set-equality
    with static_T_r2_dps; pool_weights == S + 4*W*h; tie count at T-th weight
  - margin_geq_0, rho_oracle, min_basin_size, n_dps, self-checks o1/o2/o3,
    exceedance, margin_T4/T8 identities
  - null-arm margins recomputed from raw null dps arrays (uniform, size-biased,
    randsel); shuf checked at identity level only (permutation RNG not recorded)
  - cov_static_shuf presence

Then per-(N,a): mean margin, margin>=0 count (production), and bootstrap CI
reproduction (B=10000, rng default_rng(20260907 + 1000*log2(N) + round(10000*a)))
on BOTH Stage B'' margins and Stage A'' cells.jsonl margins; the Stage A''
reproduction is compared against Stage A'' summary.json's recorded CIs.
"""
import json
import math
import numpy as np
from fractions import Fraction
from collections import defaultdict

T_OF = {20: 64, 24: 256}
N_OF = {20: 1 << 20, 24: 1 << 24}
A_GRID = [Fraction(1, 16), Fraction(1, 8), Fraction(3, 16), Fraction(1, 4)]

fail = defaultdict(list)      # check name -> list of failing cell ids
notes = []
cells_out = {}

def rec_cell(cid, check, ok, detail=None):
    if not ok:
        fail[check].append(cid if detail is None else (cid, detail))

for nbits in (20, 24):
    for seed in range(1, 26):
        rid = f"RUN-ECDLP-6ac801-v3-n{nbits}-s{seed:02d}"
        base = f"experiments/EXP-ECDLP-6ac801/runs/{rid}"
        raw = json.load(open(f"{base}/raw-result.json"))
        summ = json.load(open(f"{base}/summary.json"))
        N = N_OF[nbits]; T = T_OF[nbits]
        T_sel, T4, T8 = T // 2, T // 4, T // 8
        for a in A_GRID:
            key = f"a={float(a):.6f}"
            cid = f"n{nbits}/s{seed:02d}/{key}"
            rc = raw["cells"][key]
            sc = summ["cells"][key]
            sizes = rc["basin_sizes"]
            dps = rc["basin_dps"]
            size_of = dict(zip(dps, sizes))
            sum_b = int(sum(sizes))
            cm, capm = sc["cycle_mass"], sc["capped_mass"]
            rec_cell(cid, "accounting_identity", sum_b + cm + capm == N,
                     f"sum_b={sum_b} cm={cm} capm={capm} N={N}")
            rec_cell(cid, "basin_mass_accounting_sum_field",
                     sc["basin_mass_accounting_sum"] == N)
            rf = Fraction(cm + capm, N)
            rec_cell(cid, "residual_fraction",
                     abs(float(rf) - sc["residual_fraction"]) <= 2e-18,
                     f"rec={float(rf)} recd={sc['residual_fraction']}")
            W = math.sqrt(float(a) * N / T)
            rec_cell(cid, "cap_formula", sc["cap"] == math.ceil(8 * W),
                     f"W={W} cap={sc['cap']}")
            ss = np.sort(np.asarray(sizes, dtype=np.int64))[::-1]
            for name, k, recd in [("share_Tsel", T_sel, sc["exact_top_T_sel_share"]),
                                  ("share_T", T, sc["exact_top_T_share"]),
                                  ("share_T4", T4, sc["exact_top_T4_share"]),
                                  ("share_T8", T8, sc["exact_top_T8_share"])]:
                v = Fraction(int(ss[:k].sum()), N)
                rec_cell(cid, f"recomputed_{name}",
                         abs(float(v) - recd) <= 2e-16, f"rec={float(v)} recd={recd}")
                rec_cell(cid, f"recorded_{name}_is_nearest_double",
                         abs(float(v) - recd) <= abs(np.nextafter(float(v), 0) - float(v)))
            share_Tsel = Fraction(int(ss[:T_sel].sum()), N)
            share_T = Fraction(int(ss[:T].sum()), N)
            share_T4 = Fraction(int(ss[:T4].sum()), N)
            share_T8 = Fraction(int(ss[:T8].sum()), N)
            # cov_static from the selected T pool entries
            sel = rc["static_T_r2_dps"]
            rec_cell(cid, "static_sel_size_T", len(sel) == T, f"len={len(sel)}")
            cov_num = sum(size_of[d] for d in sel)
            cov = Fraction(cov_num, N)
            rec_cell(cid, "recomputed_cov_static",
                     abs(float(cov) - sc["static_T_r2_exact_coverage"]) <= 2e-16,
                     f"rec={float(cov)} recd={sc['static_T_r2_exact_coverage']}")
            # margin identity (exact rational)
            margin = share_Tsel - cov
            rec_cell(cid, "margin_identity_exact",
                     abs(float(margin) - sc["margin"]) <= 2e-16,
                     f"rec={float(margin)} recd={sc['margin']}")
            rec_cell(cid, "margin_identity_from_recorded_fields",
                     (sc["exact_top_T_sel_share"] - sc["static_T_r2_exact_coverage"])
                     == sc["margin"])
            rec_cell(cid, "margin_geq_0_flag", sc["margin_geq_0"] == (sc["margin"] >= 0))
            # margin_T4 / margin_T8 identities
            rec_cell(cid, "margin_T4_identity",
                     abs(float(share_T4 - cov) - sc["margin_T4"]) <= 4e-16)
            rec_cell(cid, "margin_T8_identity",
                     abs(float(share_T8 - cov) - sc["margin_T8"]) <= 4e-16)
            # independent selection recompute from pool
            pS = np.asarray(rc["pool_S"], dtype=np.float64)
            ph = np.asarray(rc["pool_h"], dtype=np.float64)
            pw = np.asarray(rc["pool_weights"], dtype=np.float64)
            rec_cell(cid, "pool_size_rT", len(pS) == 2 * T, f"len={len(pS)}")
            w_calc = pS + 4.0 * W * ph
            rec_cell(cid, "pool_weights_formula",
                     np.allclose(w_calc, pw, rtol=0, atol=1e-9),
                     f"maxdiff={float(np.max(np.abs(w_calc - pw)))}")
            order = np.argsort(-pw, kind="stable")
            Tth = pw[order[T - 1]]
            n_tied = int((pw == Tth).sum())
            rec_cell(cid, "tie_count_at_T_th_weight",
                     n_tied == sc["tie_count_at_T_th_weight"],
                     f"rec={n_tied} recd={sc['tie_count_at_T_th_weight']}")
            if n_tied == 1:
                sel_recomputed = set(rc["pool_dps"][i] for i in order[:T])
                rec_cell(cid, "static_selection_set_equality",
                         sel_recomputed == set(sel))
            else:
                notes.append(f"{cid}: tie at T-th weight (n_tied={n_tied}); "
                             "selection set-equality checked as subset-boundary only")
                # boundary check: every selected entry has weight >= Tth and
                # every non-selected pool entry outside sel has weight <= Tth
                sel_set = set(sel)
                w_of = dict(zip(rc["pool_dps"], pw))
                ok_bound = all(w_of[d] >= Tth for d in sel_set) and \
                    all(w_of[d] <= Tth for d in w_of if d not in sel_set)
                rec_cell(cid, "static_selection_boundary_consistency", ok_bound)
            # rho_oracle: smallest k with top-k share >= cov
            csum = np.cumsum(ss[:T])
            ks = [k for k in range(1, T + 1)
                  if Fraction(int(csum[k - 1]), N) >= cov]
            kstar = ks[0] if ks else None
            rho = Fraction(kstar, T) if kstar else None
            rec_cell(cid, "rho_oracle",
                     rho is not None and abs(float(rho) - sc["rho_oracle"]) <= 1e-12,
                     f"rec={rho} recd={sc['rho_oracle']}")
            rec_cell(cid, "min_basin_size", int(ss[-1]) == sc["min_basin_size"]
                     and sc["min_basin_size"] >= 1)
            rec_cell(cid, "n_dps_raw", len(sizes) == len(dps))
            # self-checks recomputed
            rec_cell(cid, "o2_coverage_nesting",
                     share_T >= share_Tsel >= share_T4 >= share_T8)
            rec_cell(cid, "o3_margin_nesting",
                     (share_Tsel - cov) >= (share_T4 - cov) >= (share_T8 - cov))
            rec_cell(cid, "exceedance_flag",
                     sc["exceedance"] == (sc["exact_top_T_sel_share"] > 1.0
                                          or sc["exact_top_T_sel_share"]
                                          > sc["exact_top_T_share"]))
            rec_cell(cid, "self_check_fields_satisfied",
                     sc["self_check_o1_basin_mass_accounting"] == "SATISFIED"
                     and sc["self_check_o2_exact_coverage_nesting"] == "SATISFIED"
                     and sc["self_check_o3_margin_nesting"] == "SATISFIED")
            rec_cell(cid, "capped_walks_present", "capped_walks" in sc)
            rec_cell(cid, "cov_static_shuf_present",
                     "control_n_null_shuf_cov_static_shuf_diagnostic" in sc)
            # null arms recomputed from raw arrays
            for arr, fld, lbl in [
                    ("null_uniform_dps", "control_i_null_oracle_rand_uniform_margin",
                     "null_uniform"),
                    ("null_sizebiased_dps", "control_j_null_oracle_rand_sizebiased_margin_diagnostic",
                     "null_sizebiased"),
                    ("null_randsel_pool_dps", "control_k_null_randsel_pool_margin",
                     "null_randsel")]:
                arrd = rc[arr]
                rec_cell(cid, f"{lbl}_subset_size", len(arrd) == T_sel, f"len={len(arrd)}")
                covn = Fraction(sum(size_of[d] for d in arrd), N)
                m = covn - cov
                rec_cell(cid, f"recomputed_{lbl}_margin",
                         abs(float(m) - sc[fld]) <= 2e-16,
                         f"rec={float(m)} recd={sc[fld]}")
            # shuf: identity level only
            shuf_cov = sc["control_n_null_shuf_cov_static_shuf_diagnostic"]
            rec_cell(cid, "null_shuf_margin_identity",
                     abs((sc["exact_top_T_sel_share"] - shuf_cov)
                         - sc["control_n_null_shuf_margin_diagnostic"]) <= 2e-16)
            cells_out[cid] = {
                "margin": sc["margin"], "margin_geq_0": sc["margin_geq_0"],
                "cov_static": float(cov), "share_Tsel": float(share_Tsel)}

# ---------------- per-(N,a) aggregates (production) -------------------
agg = {}
for nbits in (20, 24):
    for a in A_GRID:
        key = f"a={float(a):.6f}"
        ms = [cells_out[f"n{nbits}/s{s:02d}/{key}"]["margin"] for s in range(1, 26)]
        agg[f"N=2^{nbits} a={a}"] = {
            "mean_margin": float(np.mean(ms)),
            "n_margin_geq_0": sum(1 for m in ms if m >= 0),
            "n_seeds": len(ms)}

# ---------------- bootstrap CI reproduction ---------------------------
def boot(margins, seed):
    rng = np.random.default_rng(seed)
    n = len(margins)
    x = np.asarray(margins, dtype=np.float64)
    idx = rng.integers(0, n, size=(10000, n))
    means = x[idx].mean(axis=1)
    return (float(np.percentile(means, 2.5, method="linear")),
            float(np.percentile(means, 97.5, method="linear")))

# Stage A'' cells.jsonl
A_cells = defaultdict(list)
with open("coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-4433c1/reviews/"
          "TASK-20260907-7afa98/cells.jsonl") as f:
    for line in f:
        d = json.loads(line)
        A_cells[(d["N"], d["a_num"], d["a_den"])].append(d["margin"])
A_summ = json.load(open("coordination/goals/GOAL-ECDLP-bbc21f/batches/"
                        "BATCH-4433c1/reviews/TASK-20260907-7afa98/summary.json"))
A_summ_by = {(s["N"], s["a_num"], s["a_den"]): s for s in A_summ["summaries"]}

# Stage B'' margins
B_cells = defaultdict(list)
for nbits in (20, 24):
    for a in A_GRID:
        key = f"a={float(a):.6f}"
        for s in range(1, 26):
            B_cells[(N_OF[nbits], a.numerator, a.denominator)].append(
                cells_out[f"n{nbits}/s{s:02d}/{key}"]["margin"])

ci_report = {}
for (N, an, ad) in sorted(A_cells):
    a = Fraction(an, ad)
    seed = 20260907 + 1000 * int(math.log2(N)) + round(10000 * float(a))
    sA = A_summ_by[(N, an, ad)]
    loA, hiA = boot(A_cells[(N, an, ad)], seed)
    loB, hiB = boot(B_cells[(N, an, ad)], seed)
    ci_report[f"N={N} a={an}/{ad}"] = {
        "derived_seed": seed,
        "recorded_bootstrap_seed": sA["bootstrap_seed_used"],
        "seed_matches_formula": seed == sA["bootstrap_seed_used"],
        "bootstrap_B_recorded": sA["bootstrap_B"],
        "stageA_ci_recorded": [sA["ci_lo"], sA["ci_hi"]],
        "stageA_ci_reproduced": [loA, hiA],
        "stageA_ci_reproduces": (abs(loA - sA["ci_lo"]) <= 1e-12
                                 and abs(hiA - sA["ci_hi"]) <= 1e-12),
        "stageA_straddle_recorded": sA["ci_straddles_zero"],
        "stageA_straddle_reproduced": (loA < 0 < hiA),
        "stageB_ci_computed_observation_only": [loB, hiB],
        "stageB_straddles_zero": (loB < 0 < hiB),
        "stageA_k25": sA["k_25"], "stageA_verdict25": sA["verdict_25"],
        "stageA_mean_margin": sA["mean_margin"],
    }

out = {
    "n_cells": len(cells_out),
    "failed_checks": {k: (v if len(v) <= 12 else v[:12] + [f"...({len(v)} total)"])
                      for k, v in fail.items()},
    "n_failed_checks_total": sum(len(v) for v in fail.values()),
    "notes": notes,
    "per_Na_aggregates_production": agg,
    "bootstrap_ci": ci_report,
}
print(json.dumps(out, indent=1))
with open("coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-12ee85/reviews/"
          "TASK-20260910-c8cb36/recompute_results.json", "w") as f:
    json.dump(out, f, indent=1)
