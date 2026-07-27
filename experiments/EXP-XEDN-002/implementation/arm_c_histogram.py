#!/usr/bin/env python3
"""EXP-XEDN-002 arm C: exact per-surface section-count histogram.

Method: fiber over sections instead of surfaces.  Enumerate every pair
(x, y) with x a monic quadratic and deg y <= 3, set b := y^2 - x^3, keep the
pairs whose b has degree exactly 6, and bin by b.  This visits the FULL slot
space at every size (it is a bijective reindexing of the incidence set), with no
call to the frozen predicate: the square/squarefree logic here is the
independent discriminant-based reference, so arm C is also a full-space
cross-check of arm A at p in {5, 7, 11, 13}.

Counting conventions (both reported, because they differ by a factor of two):
  * "slot"  = an x value for which a section exists.  y and -y are the same slot.
  * "point" = a section as a point of the Mordell-Weil group; y and -y are two
              distinct points (P and -P), so points = 2 * slots exactly.
Neither is a count of INDEPENDENT sections: distinct sections may be dependent
(P and -P always are), so both numbers are upper bounds on the number of
independent sections of this degree shape.

Usage (see implementation/run_arm.sh):
  python3 experiments/EXP-XEDN-002/implementation/arm_c_histogram.py --run-id RUN-XEDN-002-C
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xedn2_lib as L                                            # noqa: E402

SIZES = [5, 7, 11, 13]
FREE_X_SIZES = [5, 7, 11, 13]
S_MAX = 9


def poly_mul_vec(A: np.ndarray, B: np.ndarray, p: int) -> np.ndarray:
    """Rowwise polynomial product of coefficient arrays (low-to-high)."""
    na, nb = A.shape[1], B.shape[1]
    out = np.zeros((A.shape[0], na + nb - 1), dtype=np.int64)
    for i in range(na):
        col = A[:, i:i + 1]
        out[:, i:i + nb] += col * B
    return out % p


def all_y(p: int):
    """All y of degree <= 3 with masks for 'nonzero' and 'nonzero squarefree'."""
    g = np.indices((p, p, p, p)).reshape(4, -1).T.astype(np.int64)  # y0,y1,y2,y3
    ysq = poly_mul_vec(g, g, p)                                    # 7 coefficients
    nonzero = np.any(g != 0, axis=1)
    sf = np.zeros(g.shape[0], dtype=bool)
    for i in range(g.shape[0]):
        y = [int(c) for c in g[i]]
        while len(y) > 1 and y[-1] == 0:
            y.pop()
        sf[i] = L.ref_is_squarefree_disc(y, p)
    return g, ysq, nonzero, sf


def all_x(p: int, monic: bool):
    if monic:
        g = np.indices((p, p)).reshape(2, -1).T.astype(np.int64)
        X = np.concatenate([g, np.ones((g.shape[0], 1), dtype=np.int64)], axis=1)
    else:
        X = np.indices((p, p, p)).reshape(3, -1).T.astype(np.int64)
    X3 = poly_mul_vec(poly_mul_vec(X, X, p), X, p)
    return X, X3


def census(p: int, monic: bool, y_mask: np.ndarray, ysq: np.ndarray,
           X3: np.ndarray) -> dict:
    """Bin (x, y) pairs by the induced b; return the per-surface point counts."""
    powers = (p ** np.arange(7)).astype(np.int64)
    counts = np.zeros(p ** 7, dtype=np.int32)
    ysq_m = ysq[y_mask]
    pairs = 0
    for i in range(X3.shape[0]):
        b = (ysq_m - X3[i]) % p
        keep = b[:, 6] != 0
        if not keep.any():
            continue
        codes = b[keep] @ powers
        np.add.at(counts, codes, 1)
        pairs += int(keep.sum())
    return {"counts": counts, "pairs": pairs}


def summarize(p: int, counts: np.ndarray, pairs: int, monic: bool,
              label: str) -> dict:
    n_surfaces = (p - 1) * p**6
    nz = counts[counts > 0]
    all_even = bool(np.all(nz % 2 == 0))
    slots = nz // 2
    surfaces_with_any = int(nz.size)
    max_slots = int(slots.max()) if slots.size else 0
    hist_slots = np.bincount(slots, minlength=max_slots + 1).tolist()
    hist_slots[0] = n_surfaces - surfaces_with_any
    at_least = {}
    for s in range(1, S_MAX + 1):
        cnt = int((slots >= s).sum())
        at_least[s] = {"surfaces": cnt, "fraction": cnt / n_surfaces}
    at_least_points = {}
    for s in range(1, S_MAX + 1):
        cnt = int((nz >= s).sum())
        at_least_points[s] = {"surfaces": cnt, "fraction": cnt / n_surfaces}
    # examples of the most-populated surfaces
    examples = []
    if slots.size:
        idx_nz = np.nonzero(counts)[0]
        top = idx_nz[np.argsort(-counts[idx_nz])[:5]]
        for code in top:
            code = int(code)
            b = [(code // p**i) % p for i in range(7)]
            examples.append({"b": b, "points": int(counts[code]),
                             "slots": int(counts[code]) // 2})
    return {
        "label": label, "p": p, "x_convention": "monic_deg2" if monic else "free_deg_le2",
        "n_surfaces": n_surfaces,
        "n_slots_per_surface": p**2 if monic else p**3,
        "section_points_total": pairs,
        "hit_slots_total": pairs // 2,
        "all_point_counts_even": all_even,
        "surfaces_with_at_least_one_slot": surfaces_with_any,
        "fraction_with_at_least_one_slot": surfaces_with_any / n_surfaces,
        "max_slots_on_a_surface": max_slots,
        "mean_slots_per_surface": (pairs / 2) / n_surfaces,
        "histogram_slots_per_surface": hist_slots,
        "at_least_s_slots": at_least,
        "at_least_s_points": at_least_points,
        "top_surfaces": examples,
    }


def induced_exponents(rows: list, key: str) -> dict:
    out = {}
    for s in range(1, S_MAX + 1):
        seq = []
        for r1, r2 in zip(rows, rows[1:]):
            f1 = r1[key][s]["fraction"]
            f2 = r2[key][s]["fraction"]
            if f1 > 0 and f2 > 0:
                seq.append({"p1": r1["p"], "p2": r2["p"],
                            "alpha_eff": -math.log(f2 / f1) / math.log(r2["p"] / r1["p"])})
            else:
                seq.append({"p1": r1["p"], "p2": r2["p"], "alpha_eff": None,
                            "note": "zero at one or both sizes; exponent undefined"})
        out[s] = seq
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="RUN-XEDN-002-C")
    args = ap.parse_args()

    started = dt.datetime.now(dt.timezone.utc).isoformat()
    t0 = time.time()
    print(f"EXP-XEDN-002 arm C exact section histogram, run {args.run_id}")
    print("no frozen-predicate call in this arm: squarefreeness comes from the "
          "independent discriminant reference")
    print()

    monic_pred, monic_true, free_pred = [], [], []
    for p in SIZES:
        tp = time.time()
        g, ysq, nonzero, sf = all_y(p)
        _, X3m = all_x(p, monic=True)
        c = census(p, True, sf, ysq, X3m)
        r = summarize(p, c["counts"], c["pairs"], True, "frozen_predicate_semantics")
        r["closed_form_N_hit"] = L.n_hit(p)
        r["matches_closed_form"] = (r["hit_slots_total"] == L.n_hit(p))
        r["closed_form_mean_slots_per_surface"] = float(L.mean_sections_per_surface(p))
        monic_pred.append(r)
        del c
        c = census(p, True, nonzero, ysq, X3m)
        rt = summarize(p, c["counts"], c["pairs"], True, "mathematical_square")
        rt["closed_form_N_hit_true_square"] = L.n_hit_true_square(p)
        rt["matches_closed_form"] = (rt["hit_slots_total"]
                                     == L.n_hit_true_square(p))
        monic_true.append(rt)
        del c
        print(f"  p={p:>3} monic-x census done in {time.time()-tp:.1f}s: "
              f"hit_slots={r['hit_slots_total']:,} "
              f"closed_form={L.n_hit(p):,} match={r['matches_closed_form']}; "
              f"surfaces_with_>=1={r['surfaces_with_at_least_one_slot']:,} "
              f"({r['fraction_with_at_least_one_slot']:.6f}) "
              f"max_slots={r['max_slots_on_a_surface']} "
              f"peak_mb={L.peak_memory_mb()}", flush=True)
        if p in FREE_X_SIZES:
            tp = time.time()
            _, X3f = all_x(p, monic=False)
            c = census(p, False, sf, ysq, X3f)
            rf = summarize(p, c["counts"], c["pairs"], False,
                           "frozen_predicate_semantics_free_x")
            rf["closed_form_N_hit_free_x"] = L.n_hit_free_x(p)
            rf["matches_closed_form"] = (rf["hit_slots_total"]
                                         == L.n_hit_free_x(p))
            free_pred.append(rf)
            del c
            print(f"        free-x variant in {time.time()-tp:.1f}s: "
                  f"hit_slots={rf['hit_slots_total']:,} "
                  f"closed_form={L.n_hit_free_x(p):,} "
                  f"match={rf['matches_closed_form']}; "
                  f"surfaces_with_>=1={rf['fraction_with_at_least_one_slot']:.6f} "
                  f"max_slots={rf['max_slots_on_a_surface']} "
                  f"peak_mb={L.peak_memory_mb()}", flush=True)
        del g, ysq, nonzero, sf, X3m

    print()
    print("== arm C: exact P[at least s hit slots per surface] (frozen semantics, "
          "monic x, deg b = 6 exactly) ==")
    hdr = "  s  " + "".join(f"{'p=' + str(r['p']):>26}" for r in monic_pred)
    print(hdr)
    for s in range(1, S_MAX + 1):
        cells = ""
        for r in monic_pred:
            e = r["at_least_s_slots"][s]
            cells += f"{e['surfaces']:>12,}/{r['n_surfaces']:<13,}"
        print(f"  {s}  {cells}")
    print("  fraction:")
    for s in range(1, S_MAX + 1):
        cells = "".join(f"{r['at_least_s_slots'][s]['fraction']:>26.9g}"
                        for r in monic_pred)
        print(f"  {s}  {cells}")
    print()
    print("== arm C: same, counting SECTION POINTS (P and -P separately) ==")
    for s in range(1, S_MAX + 1):
        cells = "".join(f"{r['at_least_s_points'][s]['fraction']:>26.9g}"
                        for r in monic_pred)
        print(f"  {s}  {cells}")
    print()

    exp_slots = induced_exponents(monic_pred, "at_least_s_slots")
    exp_points = induced_exponents(monic_pred, "at_least_s_points")
    print("== arm C: induced exponents for P[>= s slots] ==")
    for s in range(1, S_MAX + 1):
        parts = []
        for e in exp_slots[s]:
            parts.append(f"{e['p1']}->{e['p2']}: "
                         + (f"{e['alpha_eff']:.4f}" if e["alpha_eff"] is not None
                            else "undef"))
        print(f"  s={s}: " + "   ".join(parts))
    print()
    print("== arm C: free-(non-monic)-x variant, OUTSIDE the frozen slot definition ==")
    for r in free_pred:
        print(f"  p={r['p']:>3} P[>=1 slot]={r['at_least_s_slots'][1]['fraction']:.6f} "
              f"P[>=9 slots]={r['at_least_s_slots'][9]['fraction']:.3e} "
              f"mean_slots={r['mean_slots_per_surface']:.6f} "
              f"max_slots={r['max_slots_on_a_surface']}")
    print()
    print("== arm C: predicate-vs-mathematics (monic x) ==")
    for r, rt in zip(monic_pred, monic_true):
        print(f"  p={r['p']:>3} frozen hit slots={r['hit_slots_total']:,} "
              f"mathematical squares={rt['hit_slots_total']:,} "
              f"P[>=1] frozen={r['fraction_with_at_least_one_slot']:.6f} "
              f"mathematical={rt['fraction_with_at_least_one_slot']:.6f}")
    print()

    all_match = (all(r["matches_closed_form"] for r in monic_pred)
                 and all(r["matches_closed_form"] for r in monic_true)
                 and all(r["matches_closed_form"] for r in free_pred))
    all_even = all(r["all_point_counts_even"] for r in monic_pred)
    print(f"  arm C totals match the arm A closed forms at every size: {all_match}")
    print(f"  every per-surface point count is even (P/-P pairing): {all_even}")
    largest = max(r["p"] for r in monic_pred)
    print(f"  largest completed histogram size: p={largest}; "
          f"sizes attempted: {SIZES}")
    print()

    finished = dt.datetime.now(dt.timezone.utc).isoformat()
    wall = time.time() - t0
    raw = {
        "arm": "C",
        "method": ("full-space section fibering over (x, y) pairs, binned by the "
                   "induced b; independent of the frozen predicate"),
        "counting_conventions": {
            "slot": "an x value admitting a section; y and -y give the same slot",
            "point": "a section as a Mordell-Weil point; points = 2 * slots exactly",
            "independence_caveat": (
                "these are counts of DISTINCT sections of one degree shape, an upper "
                "bound on the number of INDEPENDENT sections: P and -P are always "
                "dependent, and distinct slots may also be dependent (e.g. P and 2P). "
                "No Mordell-Weil rank or height pairing was computed in this run."),
        },
        "shioda_tate_requirement": {
            "rank_bound_r": 8,
            "sections_needed_for_a_relation": "s >= r + 1, i.e. s >= 9",
            "source": "Shioda-Tate bound for a rational elliptic surface (literature; "
                      "not recomputed here)",
        },
        "monic_x_frozen_semantics": monic_pred,
        "monic_x_mathematical_square": monic_true,
        "free_x_frozen_semantics": free_pred,
        "induced_exponents_slots": exp_slots,
        "induced_exponents_points": exp_points,
        "all_totals_match_closed_form": all_match,
        "all_point_counts_even": all_even,
        "largest_completed_size": largest,
        "sizes_attempted": SIZES,
        "sizes_skipped": [],
    }
    L.write_run_record(
        run_id=args.run_id,
        purpose=("Arm C exact per-surface section-count histogram over the whole frozen "
                 "family by independent section fibering, with the s >= 9 "
                 "multi-section comparison"),
        entrypoint="experiments/EXP-XEDN-002/implementation/arm_c_histogram.py",
        parameters={
            "field_bits": max(SIZES).bit_length(),
            "primes": SIZES,
            "surface_family": "y^2 = x^3 + b(t), deg b = 6",
            "section_shape": "x monic deg 2, y deg <= 3",
            "predicate": "EXP-XEDN-001 is_square_poly",
            "arms": ["C"],
            "s_range": [1, S_MAX],
            "free_x_variant_sizes": FREE_X_SIZES,
        },
        started_at=started, finished_at=finished, wall=wall,
        validity="valid" if (all_match and all_even) else "invalid",
        validity_reason=(
            "exact full-space section fibering; totals reproduce the arm A closed forms "
            "at every size and every per-surface point count is even as the P/-P "
            "pairing requires" if (all_match and all_even) else
            "totals disagree with the arm A closed forms or the P/-P pairing failed"),
        summary=(f"largest completed size p={largest}; "
                 f"P[>=1 hit slot] = "
                 f"{[round(r['fraction_with_at_least_one_slot'], 6) for r in monic_pred]} "
                 f"at p={SIZES}; maximum hit slots on any surface = "
                 f"{[r['max_slots_on_a_surface'] for r in monic_pred]}; "
                 f"P[>=9 slots] = "
                 f"{[r['at_least_s_slots'][9]['fraction'] for r in monic_pred]}"),
        raw=raw,
        status="completed" if (all_match and all_even) else "invalid",
    )
    print(f"arm C complete in {wall:.1f}s; peak_memory_mb={L.peak_memory_mb()}")
    return 0 if (all_match and all_even) else 1


if __name__ == "__main__":
    raise SystemExit(main())
