"""Executor for EXP-EWALK-5ca18c (GOAL-ENDO-001, BATCH-523510).

SUPERSEDES the point-estimate reading of EXP-EWALK-4fc679, per
CORR-20260807-3ee25d defect D9 (independent Red Team review of BATCH-cb71b5):

  D9. The reported speedup of 1.641 (94.7% of the sqrt(3) ceiling, "never
      above") was a SINGLE DRAW. Over 8 seeds the Red Team found mean 1.7344
      (sd 0.2046, min 1.3705, max 2.0333) -- statistically ON the ceiling,
      with 3/8 seeds ABOVE it, and one seed tripping the campaign's own P3
      pause threshold (exceeds_incremental_ceiling_by_15pct). The batch's
      attribution of the 5.3% shortfall to fruitless-cycle cost was also
      contradicted by the run's own counter, which read fruitless_total = 0
      in every arm of that one draw.

This module runs `harness.run_ewalk2.run` across MANY seeds and reports the
actual distribution instead of one number, for both j=0 and (at a suitable
prime) j=1728. It also aggregates `fruitless_total` across seeds to test the
fruitless-cost attribution honestly instead of asserting it from one draw.

p = 100003 (used for the single-draw EXP-EWALK-4fc679 run) refuses the j=1728
arm because 100003 = 3 mod 4. This module defaults to p = 100057, which the
Red Team verified is prime and 1 mod 12 (so both zeta_3 and zeta_4 exist),
enabling j=0 AND j=1728 in the same run.

Usage:
    python3 -m harness.run_ewalk3 --p 100057 --seeds 20 --trials 24
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time

from . import run_ewalk2 as ew2
from .runner import RunResult, write_run

EXP_ID = "EXP-EWALK-5ca18c"
SUPERSEDES = "EXP-EWALK-4fc679 (point-estimate reading only; the corrected walk logic stands)"


def _dist(vals: list[float]) -> dict:
    return {"n": len(vals), "mean": statistics.mean(vals),
            "sd": statistics.stdev(vals) if len(vals) > 1 else 0.0,
            "min": min(vals), "max": max(vals), "values": vals}


def run_distribution(p: int, seeds: list[int], trials: int, min_N_bits: int,
                     max_steps: int) -> dict:
    per_seed = {}
    for s in seeds:
        per_seed[s] = ew2.run(p, trials, s, min_N_bits, max_steps)

    kinds_present = set()
    for res in per_seed.values():
        for k in res["arms"]:
            if res["arms"][k]:
                kinds_present.add(k)

    dist = {}
    fruitless_by_kind_mode = {}
    for kind in kinds_present:
        speedups, ratios_to_ceiling, exceeds_flags = [], [], []
        for s, res in per_seed.items():
            sp = res["summary"].get(f"{kind}:speedup")
            if sp is None:
                continue
            speedups.append(sp["observed_speedup_quotient_over_plain"])
            ratios_to_ceiling.append(sp["observed_over_incremental_ceiling"])
            exceeds_flags.append(sp["exceeds_incremental_ceiling_by_15pct"])
        if not speedups:
            continue
        dist[f"{kind}:speedup_distribution"] = _dist(speedups)
        dist[f"{kind}:ratio_to_ceiling_distribution"] = _dist(ratios_to_ceiling)
        dist[f"{kind}:n_seeds_exceeding_ceiling_by_15pct"] = sum(exceeds_flags)
        dist[f"{kind}:fraction_seeds_exceeding_ceiling_by_15pct"] = (
            sum(exceeds_flags) / len(exceeds_flags))

        for mode in ("plain", "quotient"):
            fr = []
            for res in per_seed.values():
                for row in res["arms"].get(kind, []):
                    if row["mode"] == mode:
                        fr.append(row["fruitless_total"])
            if fr:
                # `fr` has one entry per (curve, seed) pair, not per seed -- the
                # rows list contains multiple curves per kind. Labelled
                # `n_samples` rather than `n_seeds` for exactly that reason.
                fruitless_by_kind_mode[f"{kind}:{mode}"] = {
                    "n_samples": len(fr),
                    "total_across_all_samples": sum(fr),
                    "n_zero_samples": sum(1 for x in fr if x == 0),
                    "n_nonzero_samples": sum(1 for x in fr if x != 0),
                    "mean": statistics.mean(fr),
                    "max": max(fr),
                }

    # The generic arm is DETERMINISTIC by construction (D9's caveat): for
    # kind == "generic", run_ewalk2.run passes phi=None, lam=None, aut_order=2
    # in BOTH modes, so plain and quotient receive identical arguments and
    # rho() is a pure function of them. Confirm that here explicitly rather
    # than asserting it from the single committed run, so the "self-check, not
    # a measurement" reading is verified across every seed, not assumed.
    generic_identical_every_seed = True
    for res in per_seed.values():
        sp = res["summary"].get("generic:speedup")
        if sp and abs(sp["observed_speedup_quotient_over_plain"] - 1.0) > 1e-12:
            generic_identical_every_seed = False

    return {
        "p": p, "seeds": seeds, "trials": trials,
        "n_seeds": len(seeds),
        "distributions": dist,
        "fruitless_by_kind_mode": fruitless_by_kind_mode,
        "generic_arm_exactly_1_every_seed": generic_identical_every_seed,
        "generic_arm_note": (
            "Confirmed deterministic: for kind='generic', rho() receives "
            "phi=None, lam=None, aut_order=2 in BOTH modes, so plain and "
            "quotient are the same computation. A generic-arm speedup of "
            "exactly 1.0 on every seed is therefore a CODE-PATH IDENTITY, not "
            "independent evidence that the walk logic is correct on curves "
            "where the automorphism actually acts (CORR-20260807-3ee25d)."),
        "per_seed_raw": {str(s): res["summary"] for s, res in per_seed.items()},
        "refusals": next(iter(per_seed.values()))["summary"].get("refusals", []),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, default=100057)
    ap.add_argument("--seeds", type=int, default=20,
                    help="number of seeds, drawn as 20260807, 20260807+1, ...")
    ap.add_argument("--trials", type=int, default=24)
    ap.add_argument("--min-n-bits", type=int, default=14)
    ap.add_argument("--max-steps", type=int, default=400000)
    ap.add_argument("--base-seed", type=int, default=20260807)
    ap.add_argument("--suffix", default=None)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    seeds = list(range(args.base_seed, args.base_seed + args.seeds))
    cmd = "python3 -m harness.run_ewalk3 " + " ".join(sys.argv[1:])

    t0 = time.time()
    print(f"== EXP-EWALK-5ca18c: seed-distribution walk speedup, p={args.p}, "
          f"{args.seeds} seeds ==")
    res = run_distribution(args.p, seeds, args.trials, args.min_n_bits, args.max_steps)
    for k, d in res["distributions"].items():
        if isinstance(d, dict) and "mean" in d:
            print(f"  {k:45s} n={d['n']:3d} mean={d['mean']:.4f} sd={d['sd']:.4f} "
                  f"min={d['min']:.4f} max={d['max']:.4f}")
        else:
            print(f"  {k:45s} {d}")
    print("\n  fruitless-cycle counts by kind:mode across all seeds:")
    for k, v in res["fruitless_by_kind_mode"].items():
        print(f"    {k:20s} total={v['total_across_all_samples']:4d}  "
              f"zero_samples={v['n_zero_samples']}/{v['n_samples']}  "
              f"mean={v['mean']:.2f}  max={v['max']}")
    print(f"\n  generic arm exactly 1.0 on every seed: "
          f"{res['generic_arm_exactly_1_every_seed']}")
    if res["refusals"]:
        print("  refusals:", res["refusals"])
    t1 = time.time()

    if not args.no_write:
        metrics = {k: v for k, v in res["distributions"].items()}
        metrics["fruitless_by_kind_mode"] = res["fruitless_by_kind_mode"]
        metrics["generic_arm_exactly_1_every_seed"] = res["generic_arm_exactly_1_every_seed"]
        rid = write_run(EXP_ID, "EWALK", RunResult(
            run_suffix=args.suffix or f"p{args.p}-{args.seeds}seeds",
            curve_id=f"P{args.p}-jfamilies", seed=args.base_seed,
            parameters={"p": args.p, "seeds": seeds, "trials": args.trials,
                        "min_N_bits": args.min_n_bits, "max_steps": args.max_steps},
            metrics=metrics, certificate={"kind": "none"}, valid=True,
            raw={**res, "supersedes": SUPERSEDES}),
            status="completed", command=cmd, started=t0, finished=t1)
        print("\nwrote", rid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
