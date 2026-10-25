"""R2 null-object controls with the run's own nesting (red team, TASK-20261023-7b5dc6).

Uses the red-team enumeration (rt_count_output.json, which reproduces every recorded count) to
recompute each cell's distinct-residue count independently, then compares the frozen statistic
(upper median of distinct/model over cells with n >= 30 and model <= 0.9 N_p) with two nulls
that keep the run's nesting in H and its per-prime correlation:

  U  uniform points: every affine point gets an independent uniform residue of Z/N_p (O -> 0);
  F  same-height random rationals ("Farey null"): every x = a/d^2 is replaced by a'/d^2 with a'
     uniform on [-H(x), H(x)], gcd(a', d) = 1 (same denominator, same height bound, no curve);
     each x contributes the pair {Q, -Q}, so distinct = 1 + 2 * #{distinct finite x mod p}.

Collisions of reductions of curve points depend only on x mod p (P, -P share x), so F isolates
how much of the collision deficit is the arithmetic of small-height rationals rather than the
Mordell-Weil group.  400 replicates, seed fixed.  Output rt_coverage_null_output.json.
"""
import json, math, os, random, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
RUN = "RUN-CZLIFT-b1dce4"
REPS = 400


def model(N, n):
    return N * (1 - (1 - 1 / N) ** n)


def upper_median(v):
    s = sorted(v)
    return s[len(s) // 2] if s else None


def distinct_from_x(xs, p):
    """xs: list of (a, d, c); returns 1 + sum over distinct finite x mod p (2 each, 1 if 2y+a1x+a3 = 0 mod p)."""
    seen = {}
    for a, d, c in xs:
        if d % p == 0:
            continue  # reduces to O
        r = (a * pow(d * d, -1, p)) % p
        two = (c % p) != 0 and c != 0
        seen[r] = seen.get(r, False) or two
    return 1 + sum(2 if t else 1 for t in seen.values())


def main():
    pts_all = json.load(open(os.path.join(HERE, "rt_count_output.json")))["curves"]
    raw = json.load(open(os.path.join(REPO, "experiments/EXP-CZLIFT-14f6d5/runs", RUN, "raw-result.json")))["raw"]["curves"]
    rng = random.Random(20261023)
    cells = []  # (label, p, H, N_p, n, distinct_recorded)
    for cv in raw:
        for c in cv["coverage"]:
            cells.append((cv["label"], c["p"], c["H"], c["N_p"], c["n_points"], c["distinct"]))
    # 1. independent recomputation of distinct from the red-team point lists
    mism = 0
    obs = {}
    for lab, p, H, N, n, dist in cells:
        xs = [t for t in pts_all[lab]["points_adc"] if max(abs(t[0]), t[1] ** 2) <= H]
        n_mine = 1 + sum(1 if t[2] == 0 else 2 for t in xs)
        dm = distinct_from_x(xs, p)
        if n_mine != n or dm != dist:
            mism += 1
        obs[(lab, p, H)] = dm
    keep = [(lab, p, H, N, n) for lab, p, H, N, n, _ in cells if n >= 30 and model(N, n) <= 0.9 * N]
    def stat(dist_of):
        return upper_median([dist_of[(lab, p, H)] / model(N, n) for lab, p, H, N, n in keep])
    def stat_label(dist_of, prefix):
        return upper_median([dist_of[(lab, p, H)] / model(N, n) for lab, p, H, N, n in keep if lab.startswith(prefix)])
    out = {"run": RUN, "distinct_recompute_mismatches": mism, "cells_frozen": len(keep),
           "observed_median": stat(obs), "observed_median_rank7": stat_label(obs, "3826"),
           "observed_median_bk": stat_label(obs, "brumer")}
    # collisions on hmax cells only (one cell per curve and prime: approximately independent)
    top = {}
    for lab, p, H, N, n in keep:
        if (lab, p) not in top or H > top[(lab, p)][0]:
            top[(lab, p)] = (H, N, n)
    obs_col = sum(n - obs[(lab, p, H)] for (lab, p), (H, N, n) in top.items())
    exp_col = sum(n - model(N, n) for (lab, p), (H, N, n) in top.items())
    out["top_cells"] = len(top)
    out["top_cells_collisions_observed"] = obs_col
    out["top_cells_collisions_uniform_expected"] = exp_col
    # 2. nulls with nesting
    grids = {}
    for lab, p, H, N, n in keep:
        grids.setdefault((lab, p), []).append((H, N, n))
    nulls = {"U_uniform_points": [], "F_same_height_rationals": []}
    nulls_bk = {"U_uniform_points": [], "F_same_height_rationals": []}
    col_null = {"U_uniform_points": [], "F_same_height_rationals": []}
    for rep in range(REPS):
        dU, dF = {}, {}
        for (lab, p), lst in grids.items():
            N = lst[0][1]
            Hmax = max(H for H, _, _ in lst)
            xs = [t for t in pts_all[lab]["points_adc"] if max(abs(t[0]), t[1] ** 2) <= Hmax]
            # U: independent residue per affine point; F: same denominator, random numerator, same height bound
            items = []
            for a, d, c in xs:
                h = max(abs(a), d * d)
                us = [rng.randrange(N) for _ in range(1 if c == 0 else 2)]
                while True:
                    a2 = rng.randint(-h, h)
                    if math.gcd(a2, d) == 1:
                        break
                rF = None if d % p == 0 else (a2 * pow(d * d, -1, p)) % p
                items.append((h, us, rF))
            items.sort(key=lambda t: t[0])
            setU, setF = {0}, set()
            i = 0
            for H, _, n in sorted(lst):
                while i < len(items) and items[i][0] <= H:
                    setU.update(items[i][1])
                    if items[i][2] is not None:
                        setF.add(items[i][2])
                    i += 1
                dU[(lab, p, H)] = len(setU)
                dF[(lab, p, H)] = 1 + 2 * len(setF)
        nulls["U_uniform_points"].append(stat(dU)); nulls["F_same_height_rationals"].append(stat(dF))
        nulls_bk["U_uniform_points"].append(stat_label(dU, "brumer")); nulls_bk["F_same_height_rationals"].append(stat_label(dF, "brumer"))
        col_null["U_uniform_points"].append(sum(n - dU[(lab, p, H)] for (lab, p), (H, N, n) in top.items()))
        col_null["F_same_height_rationals"].append(sum(n - dF[(lab, p, H)] for (lab, p), (H, N, n) in top.items()))
    for k in nulls:
        v = np.array(nulls[k]); vb = np.array(nulls_bk[k]); cc = np.array(col_null[k])
        out[k] = {"median_stat_mean": float(v.mean()), "median_stat_sd": float(v.std()),
                  "median_stat_p0.5_p99.5": [float(np.percentile(v, 0.5)), float(np.percentile(v, 99.5))],
                  "frac_reps_ge_observed": float((v >= out["observed_median"]).mean()),
                  "bk_median_mean": float(vb.mean()), "bk_median_p0.5_p99.5": [float(np.percentile(vb, 0.5)), float(np.percentile(vb, 99.5))],
                  "bk_frac_reps_ge_observed": float((vb >= out["observed_median_bk"]).mean()),
                  "top_collisions_mean": float(cc.mean()), "top_collisions_sd": float(cc.std()),
                  "top_collisions_frac_reps_le_observed": float((cc <= obs_col).mean())}
    print(json.dumps(out, indent=1))
    json.dump(out, open(os.path.join(HERE, "rt_coverage_null_output.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
