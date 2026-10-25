"""R2: what the coverage criterion can and cannot fail on (red team, TASK-20261023-7b5dc6).

Reads raw-result.json of both runs by key (raw.curves[].coverage rows only).  For every cell
(p, H, curve) with n = n_points, N = N_p, the recorded statistic is
    ratio = distinct / model,  model = N (1 - (1 - 1/N)^n).
Since distinct <= min(n, N), ratio <= cap = min(n, N) / model, whatever the points are.

The script
  1. splits the cell populations (frozen rule: n >= 30 and model <= 0.9 N, upper median s[n//2];
     hypothesis rule: n >= 30) by curve and reports where the cells come from;
  2. reports, per cell, the cap and whether the cell is injective (distinct == n);
  3. scores the SAME frozen statistic on the same (n, N) cells for alternatives whose conclusion is
     known: (A) an arithmetic progression {kG : |k| <= m} in a cyclic E(F_p) (every residue's discrete
     log is known -- maximal structure), (B) the uniform model's own sampling distribution (n independent
     uniform draws), (C) a +-symmetric uniform set {O} u {+-Q_i} (the shape of a point set that counts P
     and -P), (D) points confined to a subgroup of index k = 2, 3, 4 (uniform inside it);
  4. evaluates the frozen clauses (median in [0.8, 1.2], frac above 1.5 < 0.05, every n >= 30 cell in
     [0.5, 1.5]) on each alternative, Monte Carlo with a fixed seed.
Output rt_coverage_output.json.
"""
import json, math, os, random, statistics, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
RUNS = {"RUN-CZLIFT-ca7450": 100000, "RUN-CZLIFT-b1dce4": 300000}
REPS = 400


def model(N, n):
    return N * (1 - (1 - 1 / N) ** n)


def frozen_stats(cells, ratios):
    sel = [r for c, r in zip(cells, ratios) if c["n_points"] >= 30 and model(c["N_p"], c["n_points"]) <= 0.9 * c["N_p"]]
    hyp = [r for c, r in zip(cells, ratios) if c["n_points"] >= 30]
    s = sorted(sel)
    med = s[len(s) // 2] if s else None
    return {"median_frozen": med,
            "frac_above_1p5_frozen": (sum(r > 1.5 for r in sel) / len(sel)) if sel else None,
            "all_hyp_cells_in_0p5_1p5": all(0.5 <= r <= 1.5 for r in hyp),
            "pass_frozen": (med is not None and 0.8 <= med <= 1.2 and sum(r > 1.5 for r in sel) / len(sel) < 0.05)}


def distinct_uniform(rng, N, n):
    return len(set(rng.randrange(N) for _ in range(n)))


def distinct_symmetric(rng, N, n):
    m = (n - 1) // 2  # n = 1 (O) + 2m affine points
    S = {0}
    for _ in range(m):
        q = rng.randrange(N)
        S.add(q); S.add((-q) % N)
    return len(S)


def distinct_subgroup(rng, N, n, k):
    M = N // k
    return len(set(rng.randrange(M) for _ in range(n)))


def main():
    out = {"runs": {}}
    rng = random.Random(20261023)
    for run, hmax in RUNS.items():
        raw = json.load(open(os.path.join(REPO, "experiments/EXP-CZLIFT-14f6d5/runs", run, "raw-result.json")))["raw"]["curves"]
        cells = []
        for cv in raw:
            for c in cv["coverage"]:
                cc = dict(c); cc["label"] = cv["label"]
                cells.append(cc)
        obs = [c["ratio_to_model"] for c in cells]
        R = {"observed": frozen_stats(cells, obs)}
        # 1. where the cells come from
        by = {}
        for c in cells:
            m = model(c["N_p"], c["n_points"])
            fz = c["n_points"] >= 30 and m <= 0.9 * c["N_p"]
            hy = c["n_points"] >= 30
            b = by.setdefault(c["label"], {"frozen_cells": 0, "hyp_cells": 0, "frozen_ratios": [], "injective_frozen": 0,
                                            "cap_gt_1p2_frozen": 0, "cap_gt_1p5_frozen": 0, "x_frozen": []})
            if hy:
                b["hyp_cells"] += 1
            if fz:
                b["frozen_cells"] += 1
                b["frozen_ratios"].append(c["ratio_to_model"])
                b["x_frozen"].append(c["n_points"] / c["N_p"])
                cap = min(c["n_points"], c["N_p"]) / m
                b["injective_frozen"] += int(c["distinct"] == c["n_points"])
                b["cap_gt_1p2_frozen"] += int(cap > 1.2)
                b["cap_gt_1p5_frozen"] += int(cap > 1.5)
        for lab, b in by.items():
            rs = sorted(b.pop("frozen_ratios")); xs = b.pop("x_frozen")
            b["median_frozen_rule"] = rs[len(rs) // 2] if rs else None
            b["min_ratio"] = rs[0] if rs else None
            b["max_ratio"] = rs[-1] if rs else None
            b["x_median"] = statistics.median(xs) if xs else None
            b["x_max"] = max(xs) if xs else None
        R["by_curve"] = by
        # observed: injective cells and the ratio-equals-cap fraction overall (frozen set)
        fz_cells = [c for c in cells if c["n_points"] >= 30 and model(c["N_p"], c["n_points"]) <= 0.9 * c["N_p"]]
        R["frozen_cells_total"] = len(fz_cells)
        R["frozen_injective_fraction"] = sum(c["distinct"] == c["n_points"] for c in fz_cells) / len(fz_cells)
        R["frozen_cells_with_cap_gt_1p5"] = sum(min(c["n_points"], c["N_p"]) / model(c["N_p"], c["n_points"]) > 1.5 for c in fz_cells)
        R["frozen_cells_with_cap_gt_1p2"] = sum(min(c["n_points"], c["N_p"]) / model(c["N_p"], c["n_points"]) > 1.2 for c in fz_cells)
        # collisions on the frozen set
        R["collisions_observed_sum"] = sum(c["n_points"] - c["distinct"] for c in fz_cells)
        R["collisions_uniform_expected_sum"] = sum(c["n_points"] - model(c["N_p"], c["n_points"]) for c in fz_cells)
        # BK-only frozen stats (the only record curve with cells)
        bk = [c for c in cells if c["label"].startswith("brumer")]
        R["record_curves_only"] = frozen_stats(bk, [c["ratio_to_model"] for c in bk])
        R["record_curves_only"]["cells_frozen"] = sum(1 for c in bk if c["n_points"] >= 30 and model(c["N_p"], c["n_points"]) <= 0.9 * c["N_p"])
        # 3./4. alternatives on identical (n, N) cells
        alt = {}
        prog = [min(c["n_points"], c["N_p"]) / model(c["N_p"], c["n_points"]) for c in cells]
        alt["A_progression_kG"] = frozen_stats(cells, prog)
        for name, fn in (("B_uniform_draws", lambda N, n: distinct_uniform(rng, N, n)),
                         ("C_symmetric_uniform", lambda N, n: distinct_symmetric(rng, N, n)),
                         ("D_subgroup_index2", lambda N, n: distinct_subgroup(rng, N, n, 2)),
                         ("D_subgroup_index3", lambda N, n: distinct_subgroup(rng, N, n, 3)),
                         ("D_subgroup_index4", lambda N, n: distinct_subgroup(rng, N, n, 4))):
            meds, fracs, passes, allin = [], [], 0, 0
            for _ in range(REPS):
                rr = [fn(c["N_p"], c["n_points"]) / model(c["N_p"], c["n_points"]) for c in cells]
                st = frozen_stats(cells, rr)
                meds.append(st["median_frozen"]); fracs.append(st["frac_above_1p5_frozen"])
                passes += int(st["pass_frozen"]); allin += int(st["all_hyp_cells_in_0p5_1p5"])
            alt[name] = {"reps": REPS, "median_frozen_mean": float(np.mean(meds)),
                         "median_frozen_p2.5_p97.5": [float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5))],
                         "frac_above_1p5_mean": float(np.mean(fracs)), "pass_frozen_rate": passes / REPS,
                         "all_hyp_cells_in_band_rate": allin / REPS}
        R["alternatives_same_cells"] = alt
        out["runs"][run] = R
        print(run, json.dumps({k: v for k, v in R.items() if k != "by_curve"}, indent=1, default=str))
        print(json.dumps(by, indent=1))
    json.dump(out, open(os.path.join(HERE, "rt_coverage_output.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
