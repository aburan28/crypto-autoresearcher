"""Red-team summary statistics (TASK-20261023-62eb31): exact Clopper-Pearson
intervals, the literal-sampler Poisson reading of finding F1, the naive-height
ratio law, and aggregation of rt_modp_null.json / rt_regulator_control.json."""
from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def binom_cdf(k, n, p):
    if p <= 0:
        return 1.0
    if p >= 1:
        return 0.0 if k < n else 1.0
    s = 0.0
    lp, lq = math.log(p), math.log1p(-p)
    for i in range(0, k + 1):
        s += math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lp + (n - i) * lq)
    return s


def bisect(f, lo, hi):
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid):
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def cp(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else bisect(lambda p: binom_cdf(k - 1, n, p) <= 1 - alpha / 2, 0.0, 1.0)
    hi = 1.0 if k == n else bisect(lambda p: binom_cdf(k, n, p) <= alpha / 2, 0.0, 1.0)
    return [lo, hi]


def cp_upper_one_sided(k, n, alpha=0.05):
    return bisect(lambda p: binom_cdf(k, n, p) <= alpha, 0.0, 1.0)


def pois_cdf(k, lam):
    return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))


def main():
    out = {}
    out["dependence_rate_within_6"] = {
        "pooled": {"k": 1, "n": 3200, "rate": 1 / 3200, "cp95_two_sided": cp(1, 3200), "cp95_one_sided_upper": cp_upper_one_sided(1, 3200)},
        "seed_20261009": {"k": 1, "n": 1600, "rate": 1 / 1600, "cp95_two_sided": cp(1, 1600), "cp95_one_sided_upper": cp_upper_one_sided(1, 1600)},
        "seed_20261010": {"k": 0, "n": 1600, "rate": 0.0, "cp95_two_sided": cp(0, 1600), "cp95_one_sided_upper": cp_upper_one_sided(0, 1600)},
        "r2_pooled": {"k": 1, "n": 1600, "cp95_two_sided": cp(1, 1600)},
        "r3_pooled": {"k": 0, "n": 1600, "cp95_two_sided": cp(0, 1600)},
    }
    # literal reading of 'random points' (y = 0 admitted): expected 2-torsion hits per seed
    primes = [101, 211, 401, 809, 1601, 3203, 6421, 12809]
    lam = sum(100 * (2 + 3) / p for p in primes)
    thr_succ = math.floor(0.002 * 1600)   # rate <= 0.002  <=> count <= 3
    thr_fals = math.floor(0.01 * 1600)    # rate > 0.01    <=> count >= 17
    p_succ = pois_cdf(thr_succ, lam)
    p_fals = 1 - pois_cdf(thr_fals, lam)
    out["literal_sampler_reading"] = {
        "expected_2torsion_dependent_per_seed": round(lam, 3), "expected_rate": round(lam / 1600, 5),
        "P_success_criterion_met_one_seed": p_succ, "P_success_both_seeds": p_succ ** 2,
        "P_falsification_met_one_seed": p_fals, "P_inconclusive_one_seed": 1 - p_succ - p_fals,
        "note": "Poisson approximation, 2-torsion hits only (y = 0 lift is 2-torsion over Q); any other relation adds to the count.",
    }
    # naive height ratio law: E log|X~| = log(p/2) - 1 for X~ uniform on the symmetric range
    out["naive_height_ratio_law"] = {str(p): round((math.log(p / 2) - 1) / math.log(p), 4) for p in primes}
    # mod-p null and lift survival
    mp = json.load(open(os.path.join(HERE, "rt_modp_null.json")))
    tot = {2: 0, 3: 0}
    for c in mp["cells"]:
        tot[c["r"]] += c["modp_bounded_relation_count"]
    k_q = {2: 1, 3: 0}
    out["lift_survival_fraction"] = {
        "modp_bounded_relations_r2": tot[2], "modp_bounded_relations_r3": tot[3],
        "Q_relations_r2": 1, "Q_relations_r3": 0,
        "pooled": {"k": 1, "n": tot[2] + tot[3], "rate": 1 / (tot[2] + tot[3]), "cp95_two_sided": cp(1, tot[2] + tot[3])},
        "r2": {"k": 1, "n": tot[2], "cp95_two_sided": cp(1, tot[2])},
        "r3": {"k": 0, "n": tot[3], "cp95_two_sided": cp(0, tot[3])},
        "large_p_r2_cells_p_ge_3203_modp_bounded_relations": sum(c["modp_bounded_relation_count"] for c in mp["cells"] if c["r"] == 2 and c["p"] >= 3203),
        "large_p_r2_cells_p_ge_3203_trials": sum(c["trials"] for c in mp["cells"] if c["r"] == 2 and c["p"] >= 3203),
    }
    print(json.dumps(out, indent=1))
    json.dump(out, open(os.path.join(HERE, "rt_stats.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
