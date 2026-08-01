#!/usr/bin/env python3
"""EXP-XEDN-002 arm B: exhaustive enumeration with the FROZEN predicate.

What is exhausted (stated exactly, because part of the space is out of budget):

  p = 5, 7   FULL slot space: every b of degree exactly 6 x every monic
             quadratic x, i.e. all (p-1)*p^8 slots.
  p = 11, 13 COMPLETE b-marginals for an explicitly listed set of x values:
             for each listed x, every one of the (p-1)*p^6 surfaces b of degree
             exactly 6 is enumerated.  The remaining x values are NOT covered by
             the frozen predicate at these sizes: the full space is 2,143,588,810
             slots at p=11 and 9,788,768,652 at p=13, which at the measured
             ~5.2 us per dual-classified slot needs ~11,000 and ~51,000 CPU
             seconds, far beyond this experiment's 2 CPU-hour budget.  Arm C
             covers the full space at these sizes with an INDEPENDENT vectorized
             enumeration over sections.

Every enumerated slot is classified three ways: by the frozen predicate, by an
independent square-root-extraction + discriminant reference implementing the
same semantics, and by the square-root extraction alone (the MATHEMATICAL
"is a nonzero square" condition).  This makes control 1 exhaustive over exactly
the slots that were enumerated.

Usage (see implementation/run_arm.sh):
  python3 experiments/EXP-XEDN-002/implementation/arm_b_exhaustive.py --run-id RUN-XEDN-002-B
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import os
import random
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xedn2_lib as L                                            # noqa: E402

FULL_SIZES = [5, 7]
MARGINAL_PLAN = {11: 12, 13: 6}         # p -> number of complete b-marginals
FIXED_X = [(0, 0), (0, 1), (3, 5)]      # x=t^2, x=t^2+t, x=t^2+5t+3 (planted x*)

_FROZEN = None
_SQRTS = {}


def _init():
    global _FROZEN
    if _FROZEN is None:
        _FROZEN, _ = L.load_frozen()
    return _FROZEN


def x_slice(p: int, k: int) -> list:
    """Deterministic list of k monic quadratics (x0, x1) for the b-marginals."""
    chosen = [(x0 % p, x1 % p) for (x0, x1) in FIXED_X]
    rng = random.Random(L.SEEDS[0])
    rest = sorted({(a, b) for a in range(p) for b in range(p)} - set(chosen))
    chosen += rng.sample(rest, max(0, k - len(chosen)))
    return chosen[:k]


def enumerate_marginal(job) -> dict:
    """Enumerate every b of degree exactly 6 for one fixed monic quadratic x."""
    p, x0, x1 = job
    t_start = time.time()
    frozen = _init()
    if p not in _SQRTS:
        _SQRTS[p] = L.sqrt_table(p)
    sqrts = _SQRTS[p]
    padd = frozen.padd
    isq = frozen.is_square_poly
    x3 = L.poly_cube_monic_quadratic(x0, x1, p, frozen)
    ref_sqrt = L.ref_poly_sqrt
    ref_sf = L.ref_is_squarefree_disc

    slots = 0
    hits_frozen = 0
    hits_ref_pred = 0
    hits_true_square = 0
    disagree_pred = []
    missed_examples = []
    rng = range(p)
    for tail in itertools.product(rng, rng, rng, rng, rng, rng):
        base = list(tail)
        for b6 in range(1, p):
            b = base + [b6]
            f = padd(x3, b, p)
            slots += 1
            fz = isq(f, p) is not None
            y = ref_sqrt(f, p, sqrts)
            true_sq = y is not None
            rp = true_sq and ref_sf(y, p)
            if fz:
                hits_frozen += 1
            if rp:
                hits_ref_pred += 1
            if true_sq:
                hits_true_square += 1
            if fz != rp and len(disagree_pred) < 20:
                disagree_pred.append({"b": b, "x": [x0, x1, 1], "f": list(f),
                                      "frozen": fz, "reference": rp})
            if true_sq and not fz and len(missed_examples) < 5:
                missed_examples.append({"b": b, "x": [x0, x1, 1], "f": list(f),
                                        "sqrt": y})
    return {
        "p": p, "x": [x0, x1, 1], "slots": slots,
        "hits_frozen": hits_frozen,
        "hits_ref_predicate_semantics": hits_ref_pred,
        "hits_true_square": hits_true_square,
        "frozen_vs_reference_disagreements": len(disagree_pred),
        "disagreement_examples": disagree_pred,
        "true_squares_missed_by_frozen": hits_true_square - hits_frozen,
        "missed_examples": missed_examples,
        "unit_seconds": round(time.time() - t_start, 2),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="RUN-XEDN-002-B")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--wall-cap", type=float, default=1700.0,
                    help="hard wall-clock cap (s); remaining units are censored "
                         "and recorded as such")
    args = ap.parse_args()

    started = dt.datetime.now(dt.timezone.utc).isoformat()
    t0 = time.time()
    frozen, digest = L.load_frozen()
    print(f"EXP-XEDN-002 arm B exhaustive enumeration, run {args.run_id}")
    print(f"frozen predicate: experiments/EXP-XEDN-001/xedni_sections.py "
          f"sha256={digest}")
    print(f"workers={args.workers} wall_cap={args.wall_cap}s (hit counts are "
          f"order-independent; only scheduling is nondeterministic)")
    print()

    # ---- plan (smallest sizes first, so the full-space claims cannot be the
    # ---- ones truncated if the wall cap is ever reached)
    jobs = []
    planned = {}
    for p in FULL_SIZES:
        xs = [(x0, x1) for x0 in range(p) for x1 in range(p)]
        jobs += [(p, x0, x1) for (x0, x1) in xs]
        planned[p] = {"mode": "full_slot_space", "x_planned": len(xs),
                      "x_in_family": p * p}
    for p in sorted(MARGINAL_PLAN):
        xs = x_slice(p, MARGINAL_PLAN[p])
        jobs += [(p, x0, x1) for (x0, x1) in xs]
        planned[p] = {"mode": "complete_b_marginals_for_listed_x",
                      "x_planned": len(xs), "x_in_family": p * p,
                      "x_list": [[x0, x1, 1] for (x0, x1) in xs]}
    for p in sorted(planned):
        pl = planned[p]
        print(f"  planned p={p:>3}: {pl['mode']}, {pl['x_planned']}/"
              f"{pl['x_in_family']} x values, "
              f"{pl['x_planned'] * (p - 1) * p**6:,} slots")
    print(f"  total planned work units: {len(jobs)}")
    print()

    results = []
    censored = []
    with Pool(processes=args.workers, initializer=_init) as pool:
        it = pool.imap(enumerate_marginal, jobs)
        for i, job in enumerate(jobs, 1):
            if time.time() - t0 > args.wall_cap:
                censored = jobs[i - 1:]
                print(f"    WALL CAP {args.wall_cap}s reached: censoring "
                      f"{len(censored)} remaining work units", flush=True)
                pool.terminate()
                break
            res = next(it)
            results.append(res)
            if res["p"] >= 11 or i % 25 == 0 or i == len(jobs):
                print(f"    [{i}/{len(jobs)}] p={res['p']} x={res['x']} "
                      f"slots={res['slots']:,} hits_frozen={res['hits_frozen']} "
                      f"unit={res['unit_seconds']}s elapsed={time.time()-t0:.0f}s",
                      flush=True)
    results.sort(key=lambda r: (r["p"], r["x"]))

    # ---- aggregate over the units that actually completed
    per_p = {}
    for r in results:
        agg = per_p.setdefault(r["p"], {
            "slots": 0, "hits_frozen": 0, "hits_ref_predicate_semantics": 0,
            "hits_true_square": 0, "disagreements": 0,
            "true_squares_missed_by_frozen": 0,
            "per_x_hits_frozen": {}, "disagreement_examples": [],
            "missed_examples": []})
        agg["slots"] += r["slots"]
        agg["hits_frozen"] += r["hits_frozen"]
        agg["hits_ref_predicate_semantics"] += r["hits_ref_predicate_semantics"]
        agg["hits_true_square"] += r["hits_true_square"]
        agg["disagreements"] += r["frozen_vs_reference_disagreements"]
        agg["true_squares_missed_by_frozen"] += r["true_squares_missed_by_frozen"]
        agg["per_x_hits_frozen"][str(r["x"])] = r["hits_frozen"]
        agg["disagreement_examples"] += r["disagreement_examples"][:3]
        agg["missed_examples"] += r["missed_examples"][:1]

    coverage = {}
    for p in sorted(per_p):
        nx = len(per_p[p]["per_x_hits_frozen"])
        full = (p in FULL_SIZES) and nx == p * p
        coverage[p] = {
            "mode": "full_slot_space" if full
                    else "complete_b_marginals_for_listed_x",
            "x_values_enumerated": nx,
            "x_values_in_family": p * p,
            "x_list_enumerated": sorted(per_p[p]["per_x_hits_frozen"].keys()),
            "slots_enumerated": per_p[p]["slots"],
            "slots_in_family": (p - 1) * p**8,
            "fraction_of_slot_space": per_p[p]["slots"] / ((p - 1) * p**8),
            "full_slot_space_exhausted_with_frozen_predicate": full,
            "planned_x_values": planned[p]["x_planned"],
            "censored_x_values": planned[p]["x_planned"] - nx,
        }
        print(f"  covered p={p:>3}: {coverage[p]['mode']}, x values {nx}"
              f"/{p*p}, slots {per_p[p]['slots']:,} of {(p-1)*p**8:,} "
              f"({coverage[p]['fraction_of_slot_space']:.4%})")
    print()

    print("== arm B vs arm A ==")
    comparison = {}
    all_agree = bool(per_p)
    for p in sorted(per_p):
        agg = per_p[p]
        q = L.q_pred(p)
        nx = len(agg["per_x_hits_frozen"])
        distinct = sorted(set(agg["per_x_hits_frozen"].values()))
        predicted_slice = nx * q
        ok = agg["hits_frozen"] == predicted_slice
        x_inv = distinct == [q]
        ref_ok = (agg["disagreements"] == 0
                  and agg["hits_ref_predicate_semantics"] == agg["hits_frozen"])
        missed_ok = (agg["true_squares_missed_by_frozen"]
                     == nx * L.q_missed_by_frozen(p))
        all_agree = all_agree and ok and x_inv and ref_ok and missed_ok
        full = coverage[p]["full_slot_space_exhausted_with_frozen_predicate"]
        comparison[p] = {
            "mode": coverage[p]["mode"],
            "slots_enumerated": agg["slots"],
            "hits_frozen_observed": agg["hits_frozen"],
            "closed_form_per_x": q,
            "closed_form_for_enumerated_slice": predicted_slice,
            "agrees_with_closed_form": ok,
            "distinct_per_x_hit_counts": distinct,
            "x_invariance_holds": x_inv,
            "full_space_N_hit_closed_form": L.n_hit(p),
            "full_space_N_hit_observed": (agg["hits_frozen"] if full else None),
            "full_space_verified_with_frozen_predicate": bool(full and ok),
            "hits_ref_predicate_semantics": agg["hits_ref_predicate_semantics"],
            "frozen_vs_reference_disagreements": agg["disagreements"],
            "reference_agrees_everywhere": ref_ok,
            "hits_true_square": agg["hits_true_square"],
            "closed_form_true_square_for_slice": nx * L.q_true_square(p),
            "true_squares_missed_by_frozen": agg["true_squares_missed_by_frozen"],
            "closed_form_missed_per_x": L.q_missed_by_frozen(p),
            "closed_form_missed_for_slice": nx * L.q_missed_by_frozen(p),
            "missed_agrees_with_closed_form": missed_ok,
            "disagreement_examples": agg["disagreement_examples"],
            "missed_examples": agg["missed_examples"][:3],
        }
        print(f"  p={p:>3} [{coverage[p]['mode']}]")
        print(f"        slots={agg['slots']:,}  hits_frozen={agg['hits_frozen']:,}  "
              f"closed_form={predicted_slice:,}  agree={ok}")
        print(f"        per-x hit counts distinct values={distinct} "
              f"(closed form per x = {q})  x_invariance={x_inv}")
        print(f"        independent reference (same semantics): "
              f"{agg['hits_ref_predicate_semantics']:,}  "
              f"disagreements={agg['disagreements']}  agree={ref_ok}")
        print(f"        mathematical squares: {agg['hits_true_square']:,} "
              f"(closed form {nx * L.q_true_square(p):,})  "
              f"missed by frozen={agg['true_squares_missed_by_frozen']:,} "
              f"(closed form {nx * L.q_missed_by_frozen(p):,})  agree={missed_ok}")
        if full:
            print(f"        FULL SLOT SPACE: N_hit observed {agg['hits_frozen']:,} "
                  f"== closed form {L.n_hit(p):,}: "
                  f"{agg['hits_frozen'] == L.n_hit(p)}")
    print()
    print(f"  ARM A/B AGREEMENT AT EVERY ENUMERATED SIZE: {all_agree}")
    fully = [p for p in sorted(coverage)
             if coverage[p]["full_slot_space_exhausted_with_frozen_predicate"]]
    partly = [p for p in sorted(coverage) if p not in fully]
    print(f"  full slot space exhausted with the frozen predicate at p in {fully}")
    print(f"  p in {partly}: complete b-marginals only (NOT the full slot space)")
    print()

    finished = dt.datetime.now(dt.timezone.utc).isoformat()
    wall = time.time() - t0
    total_slots = sum(v["slots"] for v in per_p.values())
    raw = {
        "arm": "B",
        "frozen_predicate_sha256": digest,
        "planned_coverage": {str(k): v for k, v in planned.items()},
        "actual_coverage": {str(k): v for k, v in coverage.items()},
        "censored_work_units": [{"p": j[0], "x": [j[1], j[2], 1]} for j in censored],
        "comparison_with_arm_a": {str(k): v for k, v in comparison.items()},
        "per_unit_results": [{k: v for k, v in r.items()
                              if k != "disagreement_examples"} for r in results],
        "arm_a_b_agree_at_every_enumerated_size": all_agree,
        "full_slot_space_exhausted_at": fully,
        "b_marginals_only_at": partly,
        "total_slots_enumerated": total_slots,
        "total_frozen_predicate_calls": total_slots,
        "total_independent_reference_calls": total_slots,
        "not_enumerated": {
            "reason": ("the full slot space at p=11 (2,143,588,810 slots) and p=13 "
                       "(9,788,768,652 slots) needs ~11,000 and ~51,000 CPU seconds at "
                       "the measured ~5.2 us per dual-classified slot, beyond the "
                       "1800 s per-run and 2 CPU-hour budget"),
            "fraction_enumerated": {str(p): coverage[p]["fraction_of_slot_space"]
                                    for p in partly},
            "covered_instead_by": ("arm C independent vectorized full-space section "
                                   "fibering at p in {5,7,11,13}"),
        },
    }
    L.write_run_record(
        run_id=args.run_id,
        purpose=("Arm B exhaustive frozen-predicate slot enumeration: full slot space "
                 "at p in {5,7} and complete b-marginals for listed x at p in {11,13}, "
                 "compared against the arm A closed form"),
        entrypoint="experiments/EXP-XEDN-002/implementation/arm_b_exhaustive.py",
        parameters={
            "field_bits": max(list(FULL_SIZES) + list(MARGINAL_PLAN)).bit_length(),
            "primes": sorted(list(FULL_SIZES) + list(MARGINAL_PLAN)),
            "surface_family": "y^2 = x^3 + b(t), deg b = 6",
            "section_shape": "x monic deg 2, y deg <= 3",
            "predicate": "EXP-XEDN-001 is_square_poly",
            "arms": ["B"],
            "full_space_sizes": FULL_SIZES,
            "marginal_sizes": {str(k): v for k, v in MARGINAL_PLAN.items()},
            "workers": args.workers,
            "wall_cap_seconds": args.wall_cap,
        },
        started_at=started, finished_at=finished, wall=wall,
        validity="valid" if all_agree else "invalid",
        validity_reason=(
            "frozen-predicate enumeration reproduced the arm A closed form exactly on "
            "every enumerated slice, and the independent reference agreed on every "
            "enumerated slot" if all_agree else
            "enumeration disagreed with the arm A closed form or with the independent "
            "reference; see comparison_with_arm_a"),
        summary=(f"{total_slots:,} slots enumerated with the frozen predicate; hits "
                 f"match the closed form on every enumerated slice: {all_agree}; full "
                 f"slot space exhausted at p in {fully}, complete b-marginals only at "
                 f"p in {partly}"),
        raw=raw,
        status="completed" if all_agree else "invalid",
    )
    print(f"arm B complete in {wall:.1f}s; peak_memory_mb={L.peak_memory_mb()}")
    return 0 if all_agree else 1


if __name__ == "__main__":
    raise SystemExit(main())
