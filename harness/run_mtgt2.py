"""Executor for EXP-MTGT-952db3 (GOAL-ENDO-001, BATCH-523510).

SUPERSEDES the cost claims of EXP-MTGT-321a54, per CORR-20260807-3ee25d
defects D1 and D2 (independent Red Team review of BATCH-cb71b5):

  D1. RUN-MTGT-p4001e2 (ell=2) measured the IDENTITY MAP: `velu_odd`'s +-pair
      loop is empty at ell=2, so it silently returned (a, b) unchanged.
      `harness/isogeny_class.py:velu_odd` now RAISES on even ell instead.

  D2. The rebuild baseline called `build_table`, a full double-and-add per
      entry, against a table of CONSECUTIVE multiples where [s]P = [s-1]P + P
      costs one addition. That inflated the "rebuild" cost by ~log2(N) and
      made transport look ~6x cheaper than it is. Independently re-derived
      by the Coordinator (min-over-7 timing, byte-identical tables): ratio
      12.23 at S=400, 15.18 at S=2000, matching the Red Team's report.

This module fixes both: it refuses ell=2 (enforced by velu_odd itself), adds
`build_table_incremental` as the correct rebuild baseline, and SWEEPS ell to
find the true crossover where transport stops winning -- the Red Team's
least-squares fit of the ORIGINAL (still-wrong) numbers put it near ell=17.1;
this measures it directly against the corrected baseline.

Usage:
    python3 -m harness.run_mtgt2 --p 50021 --table-size 400 --ells 3,5,7,11,13,17,19,23
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time

from . import exp_icinv as ex
from . import isogeny_class as ic
from .runner import RunResult, write_run
from .toycurve import EllipticCurve, Point

EXP_ID = "EXP-MTGT-952db3"
SUPERSEDES = "EXP-MTGT-321a54 (cost claims only; transport correctness stands)"
REPS = 7   # min-over-REPS timing, per the Red Team's noise-avoidance method


def build_table_batch(E: EllipticCurve, P: Point, size: int) -> list[tuple]:
    """The ORIGINAL (inflated) builder: one double-and-add per entry.

    Kept only as a labelled comparison point -- this is NOT the rebuild
    baseline any cost claim may be measured against.
    """
    return [(E.mul(s, P), s) for s in range(1, size + 1)]


def build_table_incremental(E: EllipticCurve, P: Point, size: int) -> list[tuple]:
    """The CORRECT rebuild baseline for a table of consecutive multiples.

    [s]P = [s-1]P + P, so each entry costs exactly one point addition. This is
    what "rebuilding" actually costs and is what transport must be compared
    against.
    """
    out, R = [], None
    for s in range(1, size + 1):
        R = E.add(R, P)
        out.append((R, s))
    return out


def transport_table(E: EllipticCurve, kernel_pts: list[Point],
                    table: list[tuple]) -> tuple[list[tuple], int]:
    out, evals = [], 0
    for (pt, s) in table:
        img = ic.velu_image(E, kernel_pts, pt)
        evals += 1
        if img is not None:
            out.append((img, s))
    return out, evals


def timed_min(fn, reps: int = REPS) -> tuple[float, object]:
    """min() over `reps` repetitions -- avoids the noise that made a first,
    single-shot D2 measurement APPEAR to refute the Red Team (ratio 0.72
    instead of the real ~12)."""
    best_t, best_r = None, None
    for _ in range(reps):
        t0 = time.perf_counter()
        r = fn()
        t = time.perf_counter() - t0
        if best_t is None or t < best_t:
            best_t, best_r = t, r
    return best_t, best_r


def find_curve_for_ell(p: int, ell: int, min_N: int = 100, tries: int = 400):
    """A curve at p whose order is divisible by ell, with a large prime cofactor.

    Searches CANDIDATE (a, b) pairs directly and computes each one's trace,
    exactly as `run_ewalk2.find_curves` does -- NOT a full class enumeration.
    `ic.isogeny_classes(p)` is a complete O(p^2) census (every j-invariant times
    an O(p) character sum) and is the right tool when completeness must be
    CERTIFIED (as in EXP-ICINV), but it is the wrong tool here: this sweep only
    ever needs ONE curve per ell, and calling the full census once per ell value
    made the first version of this sweep try to do ~10 * O(p^2) work at
    p = 50021 -- billions of operations in pure Python -- and it never
    finished. Returns (N, trace, rec) or None.
    """
    for i in range(tries):
        a, b = (i * 7 + 3) % p, (i * 11 + 5) % p
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            continue
        n = ic.curve_order(p, a, b)
        if n % ell:
            continue
        N = max(ex._factor(n))
        if N < min_N:
            continue
        j = ic.j_invariant(p, a, b)
        aut = 6 if (j == 0 and p % 3 == 1) else (4 if (j == 1728 % p and p % 4 == 1) else 2)
        rec = ic.CurveRecord(p, a, b, j, p + 1 - n, n, aut)
        return N, p + 1 - n, [rec]
    return None


def measure_one(p: int, ell: int, table_size: int) -> dict:
    found = find_curve_for_ell(p, ell)
    if found is None:
        return {"ell": ell, "invalid": True,
                "reason": f"no ordinary class at p={p} has order divisible by ell={ell}"}
    N, t, recs = found
    n = p + 1 - t
    rec = recs[0]
    E = rec.curve()

    gen = ic.find_kernel_generator(E, n, ell)
    if gen is None:
        return {"ell": ell, "invalid": True, "reason": f"no order-{ell} point found"}
    kernel_pts, R = [], gen
    for _ in range((ell - 1) // 2):
        kernel_pts.append(R)
        R = E.add(R, gen)

    a2, b2, _ = ic.velu_odd(E, gen, ell)
    E2 = EllipticCurve(p, a2, b2)
    t2 = ic.trace_of_frobenius(p, a2, b2)

    P = None
    cof = n // N
    for x in range(2, p):
        Rr = E.lift_x(x)
        if Rr is None:
            continue
        cand = E.mul(cof, Rr)
        if cand is not None and E.mul(N, cand) is None:
            P = cand
            break
    if P is None:
        return {"ell": ell, "invalid": True, "reason": "no point of order N found"}

    transport_secs, (tt, evals) = timed_min(
        lambda: transport_table(E, kernel_pts, build_table_incremental(E, P, table_size)))
    # transport_table itself needs a table; time transport ALONE by pre-building once
    table = build_table_incremental(E, P, table_size)
    transport_secs, (tt, evals) = timed_min(lambda: transport_table(E, kernel_pts, table))

    rebuild_batch_secs, _ = timed_min(lambda: build_table_batch(E, P, table_size))
    fP = ic.velu_image(E, kernel_pts, P)
    rebuild_incr_secs, _ = timed_min(lambda: build_table_incremental(E2, fP, table_size))

    bad = [s for (pt, s) in tt if E2.mul(s, fP) != pt]
    on_curve = all(E2.is_on_curve(pt) for (pt, _) in tt)
    identical_tables = build_table_batch(E, P, table_size) == build_table_incremental(E, P, table_size)

    return {
        "ell": ell, "invalid": False,
        "p": p, "trace_source": t, "trace_target": t2, "same_isogeny_class": t == t2,
        "N": N, "table_size": table_size,
        "entries_surviving": len(tt), "entries_lost_to_kernel": table_size - len(tt),
        "all_entries_on_target_curve": bool(on_curve),
        "entries_failing_certificate": len(bad),
        "transport_certificate_verified": bool(on_curve and not bad and tt),
        "builders_agree_on_table_content": bool(identical_tables),
        "transport_seconds_min_of_%d" % REPS: transport_secs,
        "rebuild_incremental_seconds_min_of_%d" % REPS: rebuild_incr_secs,
        "rebuild_batch_seconds_min_of_%d" % REPS: rebuild_batch_secs,
        "transport_over_correct_rebuild": (transport_secs / rebuild_incr_secs
                                           if rebuild_incr_secs else None),
        "transport_over_batch_rebuild_INFLATED_DO_NOT_CITE":
            (transport_secs / rebuild_batch_secs if rebuild_batch_secs else None),
        "batch_over_incremental_inflation_factor":
            (rebuild_batch_secs / rebuild_incr_secs if rebuild_incr_secs else None),
        "log2_N": N.bit_length(),
    }


def sweep(p: int, ells: list[int], table_size: int) -> dict:
    rows = [measure_one(p, ell, table_size) for ell in ells]
    valid = [r for r in rows if not r["invalid"]]
    # Crossover: smallest ell (interpolated) where transport_over_correct_rebuild >= 1.0
    crossover = None
    ratios = [(r["ell"], r["transport_over_correct_rebuild"]) for r in valid]
    for (e1, r1), (e2, r2) in zip(ratios, ratios[1:]):
        if r1 is not None and r2 is not None and r1 < 1.0 <= r2:
            # linear interpolation in ell
            crossover = e1 + (1.0 - r1) * (e2 - e1) / (r2 - r1)
            break
    all_certified = all(r["transport_certificate_verified"] for r in valid)
    all_same_class = all(r["same_isogeny_class"] for r in valid)
    return {
        "p": p, "table_size": table_size, "ells_requested": ells,
        "rows": rows,
        "n_valid": len(valid),
        "all_certified": bool(all_certified),
        "all_same_class": bool(all_same_class),
        "crossover_ell_estimate": crossover,
        "ratios": ratios,
        "mean_inflation_factor_of_original_baseline":
            (statistics.mean(r["batch_over_incremental_inflation_factor"]
                             for r in valid) if valid else None),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, default=50021)
    ap.add_argument("--table-size", type=int, default=400)
    ap.add_argument("--ells", default="3,5,7,11,13,17,19,23,29,31")
    ap.add_argument("--seed", type=int, default=20260807)
    ap.add_argument("--suffix", default=None)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    ells = [int(x) for x in args.ells.split(",")]
    cmd = "python3 -m harness.run_mtgt2 " + " ".join(sys.argv[1:])

    t0 = time.time()
    print(f"== EXP-MTGT-952db3: corrected transport-vs-rebuild sweep, p={args.p} ==")
    res = sweep(args.p, ells, args.table_size)
    for r in res["rows"]:
        if r["invalid"]:
            print(f"  ell={r['ell']:3d}  INVALID: {r['reason']}")
            continue
        print(f"  ell={r['ell']:3d}  N={r['N']:8d} (log2={r['log2_N']:2d})  "
              f"transport={r['transport_seconds_min_of_7']*1000:8.4f}ms  "
              f"rebuild_correct={r['rebuild_incremental_seconds_min_of_7']*1000:8.4f}ms  "
              f"ratio={r['transport_over_correct_rebuild']:.3f}  "
              f"certified={r['transport_certificate_verified']}  "
              f"same_class={r['same_isogeny_class']}")
    print(f"\n  crossover ell (transport stops winning): "
          f"{res['crossover_ell_estimate']}")
    print(f"  mean inflation factor of the ORIGINAL (wrong) baseline: "
          f"{res['mean_inflation_factor_of_original_baseline']:.2f}"
          if res['mean_inflation_factor_of_original_baseline'] else "  n/a")
    print(f"  all entries certified: {res['all_certified']}   "
          f"all targets same isogeny class: {res['all_same_class']}")
    t1 = time.time()

    if not args.no_write:
        metrics = {"crossover_ell_estimate": res["crossover_ell_estimate"],
                  "all_certified": res["all_certified"],
                  "all_same_class": res["all_same_class"],
                  "mean_inflation_factor_of_original_baseline":
                      res["mean_inflation_factor_of_original_baseline"],
                  "ratios": {str(e): r for e, r in res["ratios"]}}
        rid = write_run(EXP_ID, "MTGT", RunResult(
            run_suffix=args.suffix or f"p{args.p}sweep",
            curve_id=f"P{args.p}-multi-ell-sweep", seed=args.seed,
            parameters={"p": args.p, "table_size": args.table_size, "ells": ells},
            metrics=metrics, certificate={"kind": "none"},
            valid=bool(res["all_certified"] and res["all_same_class"]),
            invalid_reason=(None if (res["all_certified"] and res["all_same_class"])
                            else "certificate or class-membership failure in the sweep"),
            raw={**res, "supersedes": SUPERSEDES}),
            status="completed", command=cmd, started=t0, finished=t1)
        print("\nwrote", rid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
