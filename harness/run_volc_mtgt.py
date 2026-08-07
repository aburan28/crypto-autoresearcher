"""Executor for EXP-VOLC-9fec05 and EXP-MTGT-321a54 (GOAL-ENDO-001, BATCH-cb71b5).

EXP-VOLC-9fec05 -- does position in the ell-isogeny volcano change any measured
attack-cost functional? Levels are assigned STRUCTURALLY, by counting the
order-ell subgroups of E(F_p)[ell] that are Galois-stable: ell+1 at the crater
when ell splits in the order, 1 on the sides, 0 at the floor. Every EXP-ICINV
functional is then re-analysed stratified by level. The prediction fixed before
running is NO effect, because on the prime-order subgroup every endomorphism is
a scalar (H-ENDO-001) and depth is invisible there.

EXP-MTGT-321a54 -- does preprocessing transport? A preprocessing table is a set
of (point, scalar) pairs. Transport theorem T1 says an isogeny phi maps points
to points and leaves scalars untouched, so the table maps to a valid table on
the target curve at the cost of |table| Velu evaluations. This measures whether
that is true (it must be, and the certificate proves it per entry), what it
costs, and -- the part that actually matters -- whether it beats rebuilding.

Usage:
    python3 -m harness.run_volc_mtgt --p 2003 --ell 3
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time

from . import exp_icinv as ex
from . import isogeny_class as ic
from .runner import RunResult, write_run
from .toycurve import EllipticCurve, Point

EXP_VOLC = "EXP-VOLC-9fec05"
EXP_MTGT = "EXP-MTGT-321a54"


# --------------------------------------------------------------------------
# EXP-VOLC
# --------------------------------------------------------------------------


def ell_subgroup_count(E: EllipticCurve, order: int, ell: int) -> int | None:
    """Vertex degree in the ell-volcano: the number of F_p-RATIONAL ell-isogenies.

    A rational ell-isogeny corresponds to a GALOIS-STABLE order-ell subgroup of
    E[ell]. Galois-stable is strictly weaker than pointwise rational: a subgroup
    can be stable while none of its non-zero points lies in E(F_p). Counting
    rational points of order ell therefore UNDERCOUNTS the vertex degree and, at
    p = 4001 / ell = 7 where 7 does not divide #E at all, returned 0 for every
    curve in a class whose 7-volcano provably has depth (conductor 28). That was
    a defect in the first version of this function; it is recorded rather than
    quietly fixed because it produced the `levels_observed: [0]` in
    RUN-VOLC-p4001e7.

    ell = 2 is computed EXACTLY and cheaply: the order-2 subgroups are generated
    by the 2-torsion points, whose x-coordinates are the roots of x^3 + ax + b in
    F_p, so the vertex degree is exactly that root count, in {0, 1, 3}. This is
    genuinely level-bearing: the root count varies WITHIN an isogeny class.

    Odd ell needs the modular polynomial Phi_ell(j(E), Y) and its root count in
    F_p. That is not implemented here, and this function returns None rather than
    a wrong number -- a missing measurement stays missing (AGENTS.md rule 9).
    """
    if ell == 2:
        return sum(1 for x in range(E.p)
                   if (x * x % E.p * x + E.a * x + E.b) % E.p == 0)
    return None


def run_volc(p: int, ell: int, fb_m3: int, targets: int, seed: int,
             trace: int | None = None) -> dict:
    classes = ic.isogeny_classes(p)
    cens = ic.class_census(p, classes)
    if any(not c.agrees for c in cens):
        return {"invalid": True,
                "reason": "census failed: enumeration incomplete"}
    if trace is not None:
        if trace not in classes:
            return {"invalid": True, "reason": f"no class with trace {trace}"}
        t = trace
    else:
        # Prefer a class whose Frobenius conductor is divisible by ell -- that is
        # exactly the condition for the ell-volcano to have DEPTH. Without it
        # every curve sits at the same level and the stratification test has
        # nothing to stratify, which is a power failure and not a negative.
        deep = []
        for tt, v in classes.items():
            if tt % p == 0:
                continue
            _, f = ic.fundamental_discriminant(tt * tt - 4 * p)
            if f % ell == 0:
                deep.append((len(v), tt))
        pool = deep or [(len(v), tt) for tt, v in classes.items()
                        if tt % p != 0 and (p + 1 - tt) % ell == 0]
        if not pool:
            return {"invalid": True,
                    "reason": f"no ordinary class at p={p} has order divisible by ell={ell}"}
        t = sorted(pool, reverse=True)[0][1]
    recs = classes[t]
    n = recs[0].order

    if ell != 2:
        return {"invalid": True,
                "reason": (f"volcano level determination for ell={ell} needs the "
                           f"modular polynomial Phi_{ell}, which is not "
                           f"implemented; refusing to report a level rather than "
                           f"reporting a wrong one"),
                "p": p, "ell": ell}
    rows = []
    for rec in recs:
        E = rec.curve()
        deg = ell_subgroup_count(E, n, ell)
        fb = ex.factor_base_fixed_size(E, fb_m3)
        tg = ex._targets(E, targets, seed)
        h3, t3 = ex.decomposition_rate_m3(E, fb, tg)
        rows.append({
            "a": rec.a, "b": rec.b, "j": rec.j, "aut": rec.aut_order,
            "ell_degree": deg, "hits_m3": h3,
            "rate_m3": h3 / t3 if t3 else float("nan"),
            "two_torsion_x": ex.two_torsion_x_count(p, rec.a, rec.b),
            "s3_support": ex.s3_monomial_support(p, rec.a, rec.b),
        })

    levels = sorted({r["ell_degree"] for r in rows})
    strata = {}
    for L in levels:
        sel = [r for r in rows if r["ell_degree"] == L]
        strata[str(L)] = {
            "n_curves": len(sel),
            "mean_rate_m3": statistics.mean(r["rate_m3"] for r in sel),
            "var_rate_m3": (statistics.variance(r["rate_m3"] for r in sel)
                            if len(sel) > 1 else 0.0),
            "s3_support": sorted({r["s3_support"] for r in sel}),
            "two_torsion_x": sorted({r["two_torsion_x"] for r in sel}),
        }

    # Does the level partition explain any variance the class does not?
    groups = {L: [r["rate_m3"] for r in rows if r["ell_degree"] == L]
              for L in levels}
    usable = {k: v for k, v in groups.items() if len(v) > 1}
    if len(usable) > 1:
        obs, nullmean, pval = ex.permutation_null(usable, iterations=2000,
                                                  seed=seed)
        strat = {"observed_mean_within_level_variance": obs,
                 "null_mean": nullmean, "p_value": pval,
                 "interpretation": ("volcano level predicts decomposition rate"
                                    if pval < 0.05 else
                                    "volcano level carries no detectable "
                                    "information about decomposition rate")}
    else:
        strat = {"p_value": None,
                 "interpretation": "insufficient level diversity to test"}

    D0, f = ic.fundamental_discriminant(t * t - 4 * p)
    return {"p": p, "ell": ell, "trace": t, "order": n, "n_curves": len(rows),
            "fundamental_discriminant": D0, "frobenius_conductor": f,
            "volcano_has_depth_at_ell": f % ell == 0,
            "levels_observed": levels, "strata": strata,
            "stratification_test": strat, "rows": rows}


# --------------------------------------------------------------------------
# EXP-MTGT
# --------------------------------------------------------------------------


def build_table(E: EllipticCurve, P: Point, N: int, size: int) -> list[tuple]:
    """A preprocessing table: `size` pairs ([s]P, s) with s deterministic."""
    return [((E.mul(s, P)), s) for s in range(1, size + 1)]


def transport_table(E: EllipticCurve, kernel_pts: list[Point],
                    table: list[tuple]) -> tuple[list[tuple], int]:
    """Apply the isogeny to every table entry. Returns (table', evaluations)."""
    out, evals = [], 0
    for (pt, s) in table:
        img = ic.velu_image(E, kernel_pts, pt)
        evals += 1
        if img is not None:
            out.append((img, s))
    return out, evals


def run_mtgt(p: int, ell: int, table_size: int, seed: int) -> dict:
    """Build a table on E, transport it, and certify every surviving entry."""
    classes = ic.isogeny_classes(p)
    best = None
    for t, recs in classes.items():
        if t % p == 0:
            continue
        n = p + 1 - t
        if n % ell:
            continue
        N = max(ex._factor(n))
        if N < 100:
            continue
        if best is None or N > best[0]:
            best = (N, t, recs)
    if best is None:
        return {"invalid": True, "reason": "no suitable class"}
    N, t, recs = best
    n = p + 1 - t
    rec = recs[0]
    E = rec.curve()

    gen = ic.find_kernel_generator(E, n, ell)
    if gen is None:
        return {"invalid": True, "reason": f"no order-{ell} point"}
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
        return {"invalid": True, "reason": "no point of order N"}

    t0 = time.perf_counter()
    table = build_table(E, P, N, table_size)
    build_secs = time.perf_counter() - t0

    t0 = time.perf_counter()
    tt, evals = transport_table(E, kernel_pts, table)
    transport_secs = time.perf_counter() - t0

    fP = ic.velu_image(E, kernel_pts, P)
    # CERTIFY EVERY SURVIVING ENTRY, independently of the transport code:
    # recompute [s]phi(P) with plain double-and-add on the target curve.
    bad = [s for (pt, s) in tt if E2.mul(s, fP) != pt]
    on_curve = all(E2.is_on_curve(pt) for (pt, _) in tt)

    t0 = time.perf_counter()
    _ = build_table(E2, fP, N, table_size)
    rebuild_secs = time.perf_counter() - t0

    return {
        "p": p, "ell": ell, "trace_source": t, "trace_target": t2,
        "same_isogeny_class": t == t2,
        "N": N, "table_size": table_size,
        "entries_surviving": len(tt),
        "entries_lost_to_kernel": table_size - len(tt),
        "all_entries_on_target_curve": bool(on_curve),
        "entries_failing_certificate": len(bad),
        "transport_certificate_verified": bool(on_curve and not bad and tt),
        "build_seconds": build_secs,
        "transport_seconds": transport_secs,
        "rebuild_seconds": rebuild_secs,
        "transport_over_rebuild": (transport_secs / rebuild_secs
                                   if rebuild_secs else None),
        "velu_evaluations": evals,
        "verdict_note": (
            "Transport preserves the scalar exactly (T1), so the table is valid "
            "on the target. Whether that is USEFUL is a separate question and the "
            "cost ratio above is the answer: transport costs one Velu evaluation "
            "per entry, rebuilding costs one scalar multiplication per entry. "
            "Neither changes the ST^2 = N preprocessing frontier, because the "
            "table's SIZE and the online cost it buys are identical on both "
            "curves -- transport moves a point on the frontier, it does not move "
            "the frontier."),
    }


# --------------------------------------------------------------------------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, default=2003)
    ap.add_argument("--ell", type=int, default=3)
    ap.add_argument("--fb-m3", type=int, default=11)
    ap.add_argument("--targets", type=int, default=300)
    ap.add_argument("--table-size", type=int, default=400)
    ap.add_argument("--seed", type=int, default=20260807)
    ap.add_argument("--trace", type=int, default=None)
    ap.add_argument("--suffix", default=None)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    suffix = args.suffix or f"p{args.p}e{args.ell}"
    cmd = "python3 -m harness.run_volc_mtgt " + " ".join(sys.argv[1:])

    t0 = time.time()
    print(f"== EXP-VOLC-9fec05: volcano-level stratification, p={args.p} ell={args.ell} ==")
    v = run_volc(args.p, args.ell, args.fb_m3, args.targets, args.seed, args.trace)
    print(json.dumps({k: val for k, val in v.items() if k != "rows"},
                     indent=1, default=str))
    t1 = time.time()
    if not args.no_write and not v.get("invalid"):
        print("wrote", write_run(EXP_VOLC, "VOLC", RunResult(
            run_suffix=suffix, curve_id=f"CLASS-p{args.p}-t{v['trace']}",
            seed=args.seed,
            parameters={"p": args.p, "ell": args.ell, "fb_m3": args.fb_m3,
                        "targets": args.targets},
            metrics={k: val for k, val in v.items() if k != "rows"},
            certificate={"kind": "none"}, valid=True, raw=v),
            status="completed", command=cmd, started=t0, finished=t1))

    t0 = time.time()
    print(f"\n== EXP-MTGT-321a54: preprocessing transport, p={args.p} ell={args.ell} ==")
    m = run_mtgt(args.p, args.ell, args.table_size, args.seed)
    print(json.dumps(m, indent=1, default=str))
    t1 = time.time()
    if not args.no_write and not m.get("invalid"):
        print("wrote", write_run(EXP_MTGT, "MTGT", RunResult(
            run_suffix=suffix, curve_id=f"P{args.p}-t{m['trace_source']}",
            seed=args.seed,
            parameters={"p": args.p, "ell": args.ell,
                        "table_size": args.table_size},
            metrics=m, certificate={"kind": "none"},
            valid=bool(m["transport_certificate_verified"]),
            invalid_reason=(None if m["transport_certificate_verified"]
                            else "transport certificate failed"),
            raw=m),
            status="completed", command=cmd, started=t0, finished=t1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
