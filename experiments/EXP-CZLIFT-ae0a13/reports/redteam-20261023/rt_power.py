"""R2 power analysis for the frozen success / arm-difference tests (red team, TASK-20261023-1d45b5).

Reads only (arm, p, number of rows) per curve from each run's raw-result.json.
For each arm and seed it computes, exactly (Poisson-binomial DP over rows), the
distribution of the success count X under per-row success probability r_i,
then the frozen statistic z = (X/n - ref)/sqrt(ref(1-ref)/n), ref = mean(1/p_i)
(run.py summarize), and P(z > 4). Alternatives: r_i = c/p_i and r_i = p_i^-alpha.
Arm difference: pooled two-proportion z exactly as summarize(); P(|z| > 3).
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "..", "..", "runs")
RUN_IDS = ["RUN-CZLIFT-dab752", "RUN-CZLIFT-5b2581"]


def rows_by_arm(run_id):
    raw = json.load(open(os.path.join(RUNS, run_id, "raw-result.json")))
    out = {"cm_canonical": [], "random_naive": []}
    for c in raw["raw"]["curves"]:
        out[c["arm"]].extend([c["p"]] * len(c["rows"]))
    return out


def pb_dist(rs):
    d = [1.0]
    for r in rs:
        nd = [0.0] * (len(d) + 1)
        for k, v in enumerate(d):
            if v < 1e-300:
                continue
            nd[k] += v * (1 - r)
            nd[k + 1] += v * r
        d = nd
    return d


def z_of(x, n, ref):
    return (x / n - ref) / math.sqrt(ref * (1 - ref) / n)


def p_z_gt(ps, rs, thr=4.0):
    n = len(ps)
    ref = sum(1 / p for p in ps) / n
    d = pb_dist(rs)
    return sum(v for x, v in enumerate(d) if z_of(x, n, ref) > thr), ref, n


def min_count_for(ps, thr=4.0):
    n = len(ps)
    ref = sum(1 / p for p in ps) / n
    x = 0
    while z_of(x, n, ref) <= thr:
        x += 1
    return x


def armdiff_power(psa, rsa, psb, rsb, thr=3.0):
    da, db = pb_dist(rsa), pb_dist(rsb)
    na, nb = len(psa), len(psb)
    tot = 0.0
    for xa, va in enumerate(da):
        if va < 1e-15:
            continue
        for xb, vb in enumerate(db):
            if vb < 1e-15:
                continue
            ra, rb = xa / na, xb / nb
            pooled = (xa + xb) / (na + nb)
            se = math.sqrt(pooled * (1 - pooled) * (1 / na + 1 / nb))
            if se and abs((ra - rb) / se) > thr:
                tot += va * vb
    return tot


def main():
    out = {"per_run": {}, "alternatives": {}, "armdiff": {}}
    data = {r: rows_by_arm(r) for r in RUN_IDS}
    lines = []
    for r in RUN_IDS:
        for arm in ("cm_canonical", "random_naive"):
            ps = data[r][arm]
            n = len(ps)
            ref = sum(1 / p for p in ps) / n
            xmin = min_count_for(ps)
            null_fp, _, _ = p_z_gt(ps, [1 / p for p in ps])
            out["per_run"][f"{r}/{arm}"] = {
                "n": n, "ref_inv_p": ref, "min_successes_for_z_gt_4": xmin,
                "rate_threshold": xmin / n, "threshold_over_ref": xmin / n / ref,
                "null_false_positive_P(z>4)": null_fp}
            lines.append(f"{r} {arm}: n={n} ref={ref:.5f} need X>={xmin} "
                         f"(rate {xmin/n:.4f} = {xmin/n/ref:.2f}x ref); null P(z>4)={null_fp:.2e}")
    # alternatives
    alts = [("c/p", c) for c in (2, 3, 4, 5, 6, 8, 10, 12)] + \
           [("p^-alpha", a) for a in (0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85)]
    for kind, par in alts:
        rec = {}
        for r in RUN_IDS:
            for arm in ("cm_canonical", "random_naive"):
                ps = data[r][arm]
                rs = [min(1.0, par / p) if kind == "c/p" else p ** (-par) for p in ps]
                pw, _, _ = p_z_gt(ps, rs)
                rec[f"{r}/{arm}"] = pw
        same_arm_both = {arm: rec[f"{RUN_IDS[0]}/{arm}"] * rec[f"{RUN_IDS[1]}/{arm}"]
                         for arm in ("cm_canonical", "random_naive")}
        # leak present on both arms: falsification fires if some arm z>4 on both seeds
        any_arm = 1.0
        for r in RUN_IDS:
            q = (1 - rec[f"{r}/cm_canonical"]) * (1 - rec[f"{r}/random_naive"])
            any_arm *= (1 - q)
        rec["P(same arm z>4 on both seeds): cm"] = same_arm_both["cm_canonical"]
        rec["P(same arm z>4 on both seeds): random"] = same_arm_both["random_naive"]
        rec["P(some arm z>4 on each seed)"] = any_arm
        out["alternatives"][f"{kind}={par}"] = rec
        lines.append(f"alt {kind}={par}: " + ", ".join(f"{k.split('/')[-1] if '/' in k else k}:{v:.3f}"
                                                        for k, v in rec.items()))
    # arm difference: cm arm leaks at c/p, random arm at 1/p
    for c in (1, 2, 3, 4, 6, 8, 10):
        rec = {}
        for r in RUN_IDS:
            psa, psb = data[r]["cm_canonical"], data[r]["random_naive"]
            rec[r] = armdiff_power(psa, [min(1, c / p) for p in psa], psb, [1 / p for p in psb])
        rec["both_seeds"] = rec[RUN_IDS[0]] * rec[RUN_IDS[1]]
        out["armdiff"][f"cm_rate={c}/p,random_rate=1/p"] = rec
        lines.append(f"armdiff cm={c}/p vs random=1/p: P(|z|>3) " +
                     ", ".join(f"{k}:{v:.3f}" for k, v in rec.items()))
    # detectable absolute difference at the frozen 3-sigma pooled threshold
    for r in RUN_IDS:
        na, nb = len(data[r]["cm_canonical"]), len(data[r]["random_naive"])
        pooled = (sum(1 / p for p in data[r]["cm_canonical"]) + sum(1 / p for p in data[r]["random_naive"])) / (na + nb)
        se = math.sqrt(pooled * (1 - pooled) * (1 / na + 1 / nb))
        out["armdiff"][f"{r}/abs_difference_at_3sigma_under_null_pooled"] = 3 * se
        lines.append(f"{r}: arm-difference 3-sigma absolute threshold at the null pooled rate {pooled:.5f}: {3*se:.4f} ({3*se/pooled:.1f}x pooled 1/p)")
    json.dump(out, open(os.path.join(HERE, "rt_power_output.json"), "w"), indent=1)
    print("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
