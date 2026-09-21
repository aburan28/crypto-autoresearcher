#!/usr/bin/env python3
"""Assemble highrank_pool.json for TASK-20260822-a7a9e8 from the run outputs.

Selection is declared, not cherry-picked: ALL curves of certified rank >= 11,
plus the first N (in search order) at each of ranks 10 and 9 from the M10 run,
plus the first N at rank 7 from the M8 control run.  Nothing is filtered by
outcome beyond the stated rank thresholds.

usage: assemble_pool.py <m8.json> <m10.json> <augment.json> <out.json> [N]
"""
import json
import sys


def record(c, run, construction, extra_u=None):
    return dict(
        curve_id="%s#%s" % (construction, "_".join(str(a) for a in c["A"])),
        construction=construction,
        construction_note=NOTE[construction],
        source_run=run,
        parameters_A=c["A"],
        base_index=c.get("base_index"),
        extra_quartic_u=extra_u or [],
        s_polynomial_coeffs_low_to_high=c["s_poly"],
        g_polynomial_coeffs_low_to_high=c["g_poly"],
        min_ainv=c["min_ainv"],
        A=c["A"],
        kind=c["kind"],
        certified_rank=c["certified_rank"],
        n_points_exhibited=len(c["points"]),
        independent_points=c["independent_points"],
        all_points=c["points"],
        independent_indices=c["independent_indices"],
        regulator_det=c["regulator_det"],
        regulator_det_highprec=c["regulator_det_highprec"],
        regulator_det_agree_60_vs_120_digits=c["regulator_det_agree"],
        hadamard_ratio=c["hadamard_ratio"],
        height_diagonal=c["height_diagonal"],
        exact_check_all_points=c["exact_check_all_points"],
        s_poly=c["s_poly"], g_poly=c["g_poly"],
    )


NOTE = {
    "m8": "Mestre deg-8: p=prod(x-a_i) over 8 a_i, g=monic deg-4 part of "
          "sqrt(p), s=g^2-p is a CUBIC, points (a_i,g(a_i)); >=1 relation "
          "(their sum is O), so at most 7 independent.",
    "m10": "Mestre deg-10: p=prod(x-a_i) over 10 a_i, g=monic deg-5 part of "
           "sqrt(p), s=g^2-p is a QUARTIC with s(a_i)=g(a_i)^2; reduced to a "
           "cubic by the osculating-parabola map (see construct_highrank.py). "
           "9 of the 10 points survive (the base point maps to infinity), so "
           "at most 9 independent from the construction alone.",
    "m10+extra": "m10 as above, PLUS extra rational points found by scanning "
                 "u=n/d, |n|<=400, d<=12 for s(u) a rational square, mapped "
                 "through the same reduction. These can exceed the "
                 "construction ceiling of 9.",
}


def main():
    m8f, m10f, augf, out = sys.argv[1:5]
    N = int(sys.argv[5]) if len(sys.argv) > 5 else 150
    m8 = json.load(open(m8f))
    m10 = json.load(open(m10f))
    aug = json.load(open(augf))
    curves = []

    # augmented curves (may exceed rank 9) -- all with rank >= 11, then N each
    byrank = {}
    for r in aug["results"]:
        c = r.get("augmented_curve")
        if not c:
            continue
        byrank.setdefault(c["certified_rank"], []).append((c, r["extra_u"]))
    for rk in sorted(byrank, reverse=True):
        lst = byrank[rk]
        take = lst if rk >= 11 else lst[:N]
        for c, eu in take:
            curves.append(record(c, "RUN-a7a9e8-004-augment-full",
                                 "m10+extra", eu))

    base9 = [c for c in m10["curves"] if c["certified_rank"] == 9][:N]
    for c in base9:
        curves.append(record(c, "RUN-a7a9e8-002-m10-main", "m10"))
    base7 = [c for c in m8["curves"] if c["certified_rank"] == 7][:N]
    for c in base7:
        curves.append(record(c, "RUN-a7a9e8-001-m8-control", "m8"))

    hist = {}
    for c in curves:
        hist[str(c["certified_rank"])] = hist.get(str(c["certified_rank"]), 0) + 1
    obj = dict(
        schema="crypto.autoresearch.highrank_pool.v1",
        task_id="TASK-20260822-a7a9e8",
        goal_id="GOAL-ECRANK-002",
        batch_id="BATCH-e0caa5",
        claim_kind="certified Mordell-Weil rank LOWER BOUND from exhibited "
                   "rational points, independence by Neron-Tate height "
                   "pairing matrix. No analytic rank, no ellrank r_high, no "
                   "point-free bound is included anywhere.",
        selection_rule="ALL curves of certified rank >= 11 from "
                       "RUN-a7a9e8-004-augment-full, plus the first %d in "
                       "search order at rank 10 and 9 (m10) and rank 7 (m8 "
                       "control). No outcome-dependent filtering beyond "
                       "these declared thresholds." % N,
        max_certified_rank=max(c["certified_rank"] for c in curves),
        rank_histogram_in_pool=hist,
        n_curves=len(curves),
        curves=curves,
    )
    json.dump(obj, open(out, "w"), indent=1)
    print("wrote %s curves=%d hist=%s" % (out, len(curves), hist))


if __name__ == "__main__":
    main()
