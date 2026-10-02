"""Supplementary MC-5 calibration for F7 (declared before running): two
heteroscedastic noise laws the main calibration does not cover --
(i) residuals resampled WITHIN each rung from that rung's own fit residuals, and
(ii) Gaussian noise with the rung's own residual s.d. -- for the m = 4 small_x
on-mode series S3, ratio_rank, ratio_rank1 and ratio_frozen, at beta0 = 0 and at the observed
slope; 1000 series each; frozen bootstrap_slope (reps 2000, seed 0) per series.
Seeds: random.Random('F7-supp|<quantity>|<law>|<beta0>').

usage: python3 f7_supp.py <outdir>
"""
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f7  # noqa: E402  (own module: series(), the stats.py loader)

S = f7.S


def main():
    outdir = sys.argv[1]
    recs = [json.loads(l) for l in open(os.path.join(HERE, "..", "rederivation", "out", "instances.jsonl"))]
    out = []
    for q in ("S3", "ratio_rank", "ratio_rank1", "ratio_frozen"):
        xs, ys, gs = f7.series(recs, 4, "small_x", "on", q)
        b, res, sd = f7.residual_sd(xs, ys)
        by_rung = {}
        for g, e in zip(gs, res):
            by_rung.setdefault(g, []).append(e)
        rung_sd = {g: statistics.pstdev(v) * math.sqrt(len(v) / max(1, len(v) - 1)) for g, v in by_rung.items()}
        for law in ("within_rung_empirical", "rung_sd_gauss"):
            for beta0 in (0.0, b):
                rng = random.Random(f"F7-supp|{q}|{law}|{beta0:.6f}")
                cover, zs, false_excl = 0, [], 0
                for _ in range(1000):
                    if law == "within_rung_empirical":
                        eps = [rng.choice(by_rung[g]) for g in gs]
                    else:
                        eps = [rng.gauss(0, rung_sd[g]) for g in gs]
                    yy = [beta0 * x + e for x, e in zip(xs, eps)]
                    f = S.bootstrap_slope(xs, yy, gs, reps=2000, level=0.95, seed=0)
                    bh, lo, hi = f["slope"], f["lo"], f["hi"]
                    cover += lo <= beta0 <= hi
                    hw = (bh - lo) if beta0 < bh else (hi - bh)
                    zs.append(abs(bh - beta0) / hw if hw > 0 else float("inf"))
                    if beta0 == 0 and (hi < 0 or lo > 0):
                        false_excl += 1
                zs.sort()
                p = cover / 1000
                out.append({"quantity": q, "law": law, "beta0": beta0, "n_series": 1000, "coverage": p,
                            "coverage_se": math.sqrt(p * (1 - p) / 1000), "kappa_95": zs[949],
                            "false_exclusion_rate_of_0": false_excl / 1000 if beta0 == 0 else None,
                            "rung_residual_sd": rung_sd})
    json.dump(out, open(os.path.join(outdir, "f7-supp.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps([{k: v for k, v in o.items() if k != "rung_residual_sd"} for o in out], indent=1))


if __name__ == "__main__":
    main()
