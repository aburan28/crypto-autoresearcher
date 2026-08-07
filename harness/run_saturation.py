"""Executor for EXP-ICINV-55c2d8 (GOAL-ENDO-001, BATCH-523510).

Resolves CORR-20260807-3ee25d defect D8 (independent Red Team review of
BATCH-cb71b5): DECOMPOSITION.md section 5 prediction 1 predicted ZERO
within-class variance in relation yield, and under the corrected uniform
sampler the m=3 decomposition rate is over-dispersed at both primes tested.
The Red Team's own saturation-decay sweep (working notes, not a run record)
showed the over-dispersion FALLING with factor-base density -- variance ratio
0.93 at |3V|/#E = 0.023, rising to 2.04 at 0.53 -- but the batch had run only
the single saturated point (density 0.53), so whether the over-dispersion
survives at the density a real m=3 decomposition search would actually use
(near 1/3! ~ 0.167) was UNESTABLISHED.

This module runs that sweep properly, as a harness experiment with an
immutable run record instead of ad hoc scratch: for a certified-complete
isogeny class, at increasing factor-base sizes (hence increasing |3V|/#E), it
measures the m=3 decomposition-rate over-dispersion against its own binomial
null (NULL-B) and reports the trend across the density range that brackets
1/3!.

Usage:
    python3 -m harness.run_saturation --p 4001 --targets 400
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from dataclasses import asdict

from . import exp_icinv as ex
from . import isogeny_class as ic
from .runner import RunResult, write_run
from .toycurve import EllipticCurve, Point

EXP_ID = "EXP-ICINV-55c2d8"


def decomposition_rate_m3_with_size(E: EllipticCurve, fb: list[int],
                                    targets: list[Point]) -> tuple[int, int, int]:
    """(hits, trials, |3V|) -- as exp_icinv.decomposition_rate_m3, but also
    returns the sum-set size, which the density sweep needs and the original
    function does not expose."""
    pts: list[Point] = []
    for x in fb:
        P = E.lift_x(x)
        if P is not None:
            pts.append(P)
            pts.append(E.negate(P))
    two = set()
    for i in range(len(pts)):
        for jx in range(i, len(pts)):
            S = E.add(pts[i], pts[jx])
            if S is not None:
                two.add(S)
    three = set()
    for S in two:
        for R in pts:
            T = E.add(S, R)
            if T is not None:
                three.add(T)
    hits = sum(1 for T in targets if T in three)
    return hits, len(targets), len(three)


def measure_at_density(recs, fb_size: int, n_targets: int, seed: int) -> dict:
    """One factor-base size, every curve in the class, uniform targets."""
    hits_per_curve, sizes_per_curve, densities_per_curve = [], [], []
    for rec in recs:
        E = rec.curve()
        fb = ex.factor_base_fixed_size(E, fb_size)
        tg = ex.targets_uniform(E, rec.order, n_targets, seed)
        h, t, size3v = decomposition_rate_m3_with_size(E, fb, tg)
        hits_per_curve.append(h)
        sizes_per_curve.append(size3v)
        densities_per_curve.append(size3v / rec.order)

    verdict = ex.binomial_null_verdict("decomp_rate_m3", hits_per_curve, n_targets)
    rates = [h / n_targets for h in hits_per_curve]
    # Residual after removing the |3V|/#E prediction -- the m=2 finding earlier
    # in this campaign showed the analogous residual falls to ~0.73x binomial
    # noise once |3V| is controlled for. Reported here at every density so the
    # trend, not one point, is on record.
    predicted = densities_per_curve
    residual = [o - p for o, p in zip(rates, predicted)]
    resid_var = statistics.variance(residual) if len(residual) > 1 else 0.0
    mean_rate = statistics.mean(rates)
    binom_var = mean_rate * (1 - mean_rate) / n_targets if 0 < mean_rate < 1 else 0.0

    return {
        "fb_size": fb_size,
        "mean_density_3V_over_order": statistics.mean(densities_per_curve),
        "mean_rate": mean_rate,
        "observed_variance": verdict.variance,
        "binomial_null_variance": verdict.null_variance,
        "variance_ratio": verdict.ratio,
        "verdict": verdict.verdict,
        "residual_after_removing_3V_prediction_variance": resid_var,
        "residual_over_binomial_ratio": (resid_var / binom_var if binom_var else None),
        "n_curves": len(recs),
    }


def run(p: int, fb_sizes: list[int], n_targets: int, seed: int, controls: int) -> dict:
    classes = ic.isogeny_classes(p)
    cens = ic.class_census(p, classes)
    if any(not c.agrees for c in cens):
        return {"invalid": True, "reason": "census failed: enumeration incomplete"}
    ordinary = sorted(((len(v), t) for t, v in classes.items() if t % p != 0),
                      reverse=True)
    target_trace = ordinary[0][1]
    recs = classes[target_trace]
    n = recs[0].order

    rows = [measure_at_density(recs, fb, n_targets, seed) for fb in fb_sizes]

    # 1/m! for m=3 is the density a real length-3 decomposition search would
    # naturally operate near (a factor base whose 3-fold sumset is expected to
    # cover about 1/3! of the group, by the usual smoothness-probability
    # heuristic). Bracket it explicitly rather than reporting only the extremes.
    target_density = 1.0 / 6.0
    closest = min(rows, key=lambda r: abs(r["mean_density_3V_over_order"] - target_density))

    monotonic_decay = all(
        rows[i]["variance_ratio"] >= rows[i + 1]["variance_ratio"] - 1e-9
        for i in range(len(rows) - 1)
        if rows[i]["variance_ratio"] not in (float("inf"),) and
           rows[i + 1]["variance_ratio"] not in (float("inf"),))

    return {
        "p": p, "target_trace": target_trace, "order": n, "n_curves": len(recs),
        "fb_sizes": fb_sizes, "n_targets": n_targets, "rows": rows,
        "target_density_1_over_3fact": target_density,
        "row_closest_to_operating_density": closest,
        "variance_ratio_decays_monotonically_with_density": bool(monotonic_decay),
        "interpretation": (
            f"At the density closest to 1/3! ({closest['mean_density_3V_over_order']:.4f} "
            f"vs target {target_density:.4f}), the variance ratio is "
            f"{closest['variance_ratio']:.3f} ({closest['verdict']}). "
            + ("This is CONSISTENT WITH the saturation-artifact reading: the "
               "over-dispersion decays toward the operating density and does "
               "not persist there." if closest["variance_ratio"] < 1.3 else
               "This is NOT explained by saturation alone: material "
               "over-dispersion persists at the density a real decomposition "
               "search would use, and DECOMPOSITION.md section 5 prediction 1 "
               "remains refuted at the density that matters.")),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, default=4001)
    ap.add_argument("--fb-sizes", default="4,5,6,7,8,9,10,11,12,13,15,18,22")
    ap.add_argument("--targets", type=int, default=400)
    ap.add_argument("--seed", type=int, default=20260807)
    ap.add_argument("--controls", type=int, default=0)
    ap.add_argument("--suffix", default=None)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    fb_sizes = [int(x) for x in args.fb_sizes.split(",")]
    cmd = "python3 -m harness.run_saturation " + " ".join(sys.argv[1:])

    t0 = time.time()
    print(f"== EXP-ICINV-55c2d8: m=3 saturation-decay sweep, p={args.p} ==")
    res = run(args.p, fb_sizes, args.targets, args.seed, args.controls)
    if res.get("invalid"):
        print("INVALID:", res["reason"])
        return 3
    for r in res["rows"]:
        print(f"  fb={r['fb_size']:3d}  density={r['mean_density_3V_over_order']:.4f}  "
              f"mean_rate={r['mean_rate']:.4f}  var_ratio={r['variance_ratio']:6.3f}  "
              f"resid/binom={r['residual_over_binomial_ratio']}  -> {r['verdict']}")
    print(f"\n  closest to 1/3!={res['target_density_1_over_3fact']:.4f}: "
          f"fb={res['row_closest_to_operating_density']['fb_size']} "
          f"density={res['row_closest_to_operating_density']['mean_density_3V_over_order']:.4f} "
          f"ratio={res['row_closest_to_operating_density']['variance_ratio']:.3f}")
    print(f"  monotonic decay across the sweep: "
          f"{res['variance_ratio_decays_monotonically_with_density']}")
    print(f"\n  {res['interpretation']}")
    t1 = time.time()

    if not args.no_write:
        metrics = {"target_density_1_over_3fact": res["target_density_1_over_3fact"],
                  "row_closest_to_operating_density": res["row_closest_to_operating_density"],
                  "variance_ratio_decays_monotonically_with_density":
                      res["variance_ratio_decays_monotonically_with_density"],
                  "interpretation": res["interpretation"],
                  "density_to_ratio": {f"{r['mean_density_3V_over_order']:.4f}":
                                       r["variance_ratio"] for r in res["rows"]}}
        rid = write_run(EXP_ID, "ICINV", RunResult(
            run_suffix=args.suffix or f"p{args.p}-satsweep",
            curve_id=f"CLASS-p{args.p}-t{res['target_trace']}", seed=args.seed,
            parameters={"p": args.p, "fb_sizes": fb_sizes, "targets": args.targets},
            metrics=metrics, certificate={"kind": "none"}, valid=True, raw=res),
            status="completed", command=cmd, started=t0, finished=t1)
        print("\nwrote", rid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
