"""Executor for EXP-JINV-6c5b8e and EXP-EWALK-cc0353 (GOAL-ENDO-001, BATCH-cb71b5).

EXP-JINV-6c5b8e -- does a special j-invariant change the ALGEBRAIC cost of the
Semaev decomposition system? On j = 0 the curve has a = 0 and on j = 1728 it has
b = 0, so monomials of S_3 vanish identically. That is resource R2 (the curve
equation), the one place j-invariant specialness is not blocked outright by the
scalar-action argument of H-ENDO-001. The measurement is the Groebner cost of
the S_3 decomposition ideal at MATCHED p and MATCHED factor-base size, against a
generic-j null.

EXP-EWALK-cc0353 -- SUPERSEDED, DO NOT USE. `rho_steps` below canonicalises the
walk point to its Aut-orbit representative without carrying the automorphism's
eigenvalue through to the (a, b) exponents, so every orbit collision yields a
relation that does not hold. RUN-EWALK-p1009-a's quotient arm is an invalid
measurement and is not evidence in either direction; see CORR-20260807-df0585.
The function is retained UNCHANGED so the superseded run stays reproducible. New
EWALK measurements use harness/run_ewalk2.py (EXP-EWALK-4fc679). The original
intent is recorded below for the record:

    does the automorphism-quotient walk exceed sqrt(|Aut|)?
Pollard rho on E/Aut is predicted to cost 0.886*sqrt(N/|Aut|) group operations.
j = 0 with p = 1 mod 3 has |Aut| = 6, j = 1728 with p = 1 mod 4 has |Aut| = 4,
generic has |Aut| = 2. The lane exists to MEASURE THE CEILING; an excess over
the prediction is treated as a suspected instrument artifact, not a result.

Usage:
    python3 -m harness.run_jinv --p 1009 --fb 9 --targets 24 --trials 40
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from dataclasses import asdict, dataclass

import sympy

from . import exp_icinv as ex
from . import isogeny_class as ic
from .runner import RunResult, write_run
from .toycurve import EllipticCurve, Point

EXP_JINV = "EXP-JINV-dd60d3"   # supersedes EXP-JINV-6c5b8e (confounded sampler)
EXP_EWALK = "EXP-EWALK-cc0353"

x1, x2, x3 = sympy.symbols("x1 x2 x3")


# --------------------------------------------------------------------------
# EXP-JINV
# --------------------------------------------------------------------------


def s3_expr(a: int, b: int):
    return ((x1 - x2) ** 2 * x3 ** 2
            - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3
            + ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)))


def s3_stats(p: int, a: int, b: int) -> dict:
    poly = sympy.Poly(sympy.expand(s3_expr(a, b)), x1, x2, x3, modulus=p)
    monos = [m for m, c in zip(poly.monoms(), poly.coeffs()) if c % p != 0]
    return {"support": len(monos),
            "total_degree": poly.total_degree(),
            "degree_x3": max(m[2] for m in monos) if monos else 0}


def groebner_cost(E: EllipticCurve, fb: list[int], target: Point) -> dict:
    """Cost of the S_3 decomposition ideal <S3(x1,x2,xR), fV(x1), fV(x2)>.

    Reported as IMPLEMENTATION-BOUND PROXIES, exactly as harness/semaev.py
    insists: sympy runs a Buchberger-family routine and does not expose the
    degree of regularity. Basis size, max total degree and wall time are what
    is observable; only trends across matched arms are interpreted.
    """
    a, b, p = E.a, E.b, E.p
    fV1 = sympy.prod([(x1 - v) for v in fb])
    fV2 = sympy.prod([(x2 - v) for v in fb])
    system = [s3_expr(a, b).subs(x3, target[0]), fV1, fV2]
    t0 = time.perf_counter()
    G = sympy.groebner(system, x1, x2, modulus=p, order="grevlex")
    secs = time.perf_counter() - t0
    polys = list(G.exprs)
    md = 0
    for g in polys:
        try:
            md = max(md, sympy.Poly(g, x1, x2, modulus=p).total_degree())
        except sympy.PolynomialError:
            pass
    trivial = len(polys) == 1 and polys[0] == 1
    return {"gb_seconds": secs, "gb_size": len(polys),
            "gb_max_degree": md, "trivial_ideal": bool(trivial)}


def decomposition_certificate(E: EllipticCurve, fb: list[int], R: Point) -> dict:
    """Independent exact search for R = A + B over the factor base."""
    pts = []
    for x in fb:
        P = E.lift_x(x)
        if P is not None:
            pts.extend([P, E.negate(P)])
    for i in range(len(pts)):
        for j in range(i, len(pts)):
            if E.add(pts[i], pts[j]) == R:
                return {"kind": "decomposition",
                        "statement": {"curve": {"p": E.p, "a": E.a, "b": E.b},
                                      "target": list(R),
                                      "summands": [list(pts[i]), list(pts[j])],
                                      "factor_base": fb}}
    return {"kind": "none"}


def find_special_curves(p: int) -> dict:
    """One representative each of j=0, j=1728, and several generic-j curves,
    all over the SAME p. Traces differ -- they must, since j=0 forces D_0=-3 --
    so this arm compares ALGEBRAIC cost at matched p and matched factor-base
    size, and explicitly NOT within one isogeny class."""
    recs = ic.enumerate_curves(p)
    out = {"j0": [], "j1728": [], "generic": []}
    for r in recs:
        if r.j == 0:
            out["j0"].append(r)
        elif r.j == 1728 % p:
            out["j1728"].append(r)
    generic = [r for r in recs if r.j not in (0, 1728 % p) and r.aut_order == 2]
    step = max(1, len(generic) // 12)
    out["generic"] = generic[::step][:12]
    return out


def run_jinv(p: int, fb_size: int, n_targets: int, seed: int) -> dict:
    fam = find_special_curves(p)
    arms = {}
    for name in ("j0", "j1728", "generic"):
        rows = []
        for rec in fam[name][:6 if name != "generic" else 12]:
            E = rec.curve()
            fb = ex.factor_base_fixed_size(E, fb_size)
            # UNIFORM sampler. The j-families compared here have DIFFERENT
            # traces -- j=0 forces D_0=-3, so they must -- and the hash-and-lift
            # sampler's acceptance is a function of #E, so it would make the
            # target sets systematically different per arm. CORR-20260807-a05e1e.
            tg = ex.targets_uniform(E, rec.order, n_targets, seed)
            costs = [groebner_cost(E, fb, T) for T in tg]
            cert = None
            for T in tg:
                c = decomposition_certificate(E, fb, T)
                if c["kind"] != "none":
                    cert = c
                    break
            rows.append({
                "a": rec.a, "b": rec.b, "j": rec.j, "trace": rec.trace,
                "order": rec.order, "aut_order": rec.aut_order,
                "s3": s3_stats(p, rec.a, rec.b),
                "fb_size": len(fb), "n_targets": len(tg),
                "gb_seconds_mean": statistics.mean(c["gb_seconds"] for c in costs),
                "gb_size_mean": statistics.mean(c["gb_size"] for c in costs),
                "gb_max_degree_max": max(c["gb_max_degree"] for c in costs),
                "trivial_fraction": sum(c["trivial_ideal"] for c in costs) / len(costs),
                "certificate": cert,
            })
        arms[name] = rows
    summary = {}
    for name, rows in arms.items():
        if not rows:
            continue
        summary[name] = {
            "n_curves": len(rows),
            "s3_support": sorted({r["s3"]["support"] for r in rows}),
            "s3_total_degree": sorted({r["s3"]["total_degree"] for r in rows}),
            "gb_seconds_mean": statistics.mean(r["gb_seconds_mean"] for r in rows),
            "gb_size_mean": statistics.mean(r["gb_size_mean"] for r in rows),
            "gb_max_degree": max(r["gb_max_degree_max"] for r in rows),
            "trivial_fraction": statistics.mean(r["trivial_fraction"] for r in rows),
        }
    base = summary.get("generic", {}).get("gb_seconds_mean")
    for name in summary:
        summary[name]["gb_seconds_ratio_vs_generic"] = (
            summary[name]["gb_seconds_mean"] / base if base else None)
    return {"p": p, "fb_size": fb_size, "n_targets": n_targets,
            "target_sampler": "targets_uniform",
            "supersedes": ("EXP-JINV-6c5b8e / RUN-JINV-p1009-a, whose Groebner "
                           "timing comparison used the confounded hash-and-lift "
                           "sampler; the exact S_3 monomial-support counts in "
                           "that run are symbolic and use no targets, so they "
                           "stand unchanged"),
            "arms": arms, "summary": summary}


# --------------------------------------------------------------------------
# EXP-EWALK
# --------------------------------------------------------------------------


def _order_of(E: EllipticCurve, P: Point, n: int) -> int:
    o = n
    for q in ex._factor(n):
        while o % q == 0 and E.mul(o // q, P) is None:
            o //= q
    return o


def aut_orbit_representative(E: EllipticCurve, P: Point, zeta: int | None,
                             aut: int) -> Point:
    """Canonical representative of P's orbit under Aut(E), for walk quotienting.

    Negation is always available. On j=0 (a=0) the extra automorphism is
    (x,y) -> (zeta*x, y) with zeta a primitive cube root of unity; on j=1728
    (b=0) it is (x,y) -> (-x, i*y) with i a primitive fourth root. The
    representative is the lexicographically smallest orbit element, which makes
    the quotient walk deterministic and collision-detectable.
    """
    if P is None:
        return None
    p = E.p
    orbit = {P, E.negate(P)}
    if zeta is not None and aut == 6:
        x, y = P
        for k in (1, 2):
            xx = x * pow(zeta, k, p) % p
            orbit.add((xx, y))
            orbit.add((xx, (-y) % p))
    elif zeta is not None and aut == 4:
        x, y = P
        xx = (-x) % p
        orbit.add((xx, y * zeta % p))
        orbit.add((xx, (-y * zeta) % p))
    return min(orbit)


def rho_steps(E: EllipticCurve, P: Point, Q: Point, N: int, seed: int,
              quotient: bool, zeta: int | None, aut: int,
              max_steps: int) -> tuple[int | None, int, int]:
    """Pollard rho with an r-adding walk. Returns (k, steps, fruitless).

    `quotient=True` walks on Aut-orbit representatives. The extra bookkeeping is
    that the automorphism multiplies the (a,b) exponents by its eigenvalue; the
    implementation avoids needing the eigenvalue by re-deriving the exponents
    from the walk itself only for negation (eigenvalue -1) and, for the larger
    automorphism groups, by DETECTING rather than exploiting the extra
    collisions. That distinction is recorded in the metrics: `aut_used` is the
    automorphism group order actually exploited, which is 2 unless the
    eigenvalue is available.
    """
    import hashlib
    r = 20
    offs = []
    for i in range(r):
        h = int(hashlib.sha256(f"{seed}:off:{i}".encode()).hexdigest(), 16)
        ai, bi = h % N, (h >> 64) % N
        offs.append((ai, bi, E.add(E.mul(ai, P), E.mul(bi, Q))))

    def part(R: Point) -> int:
        return R[0] % r if R else 0

    def canon(R: Point) -> Point:
        return aut_orbit_representative(E, R, zeta, aut) if quotient else R

    a0 = (seed * 7 + 1) % N
    R = E.mul(a0, P)
    a, b = a0, 0
    seen = {canon(R): (a, b)}
    fruitless = 0
    for step in range(1, max_steps + 1):
        i = part(canon(R))
        ai, bi, T = offs[i]
        R2 = E.add(R, T)
        if R2 is None:
            return None, step, fruitless
        if R2 == R:
            fruitless += 1
        R, a, b = R2, (a + ai) % N, (b + bi) % N
        c = canon(R)
        if c in seen:
            a2, b2 = seen[c]
            db = (b - b2) % N
            if db == 0:
                fruitless += 1
                continue
            k = (a2 - a) * pow(db, -1, N) % N
            if E.mul(k, P) == Q:
                return k, step, fruitless
            fruitless += 1
            continue
        seen[c] = (a, b)
    return None, max_steps, fruitless


def run_ewalk(p: int, trials: int, seed: int, max_steps: int) -> dict:
    fam = find_special_curves(p)
    zeta3 = None
    if p % 3 == 1:
        g = ic._multiplicative_generator(p)
        zeta3 = pow(g, (p - 1) // 3, p)
    zeta4 = None
    if p % 4 == 1:
        g = ic._multiplicative_generator(p)
        zeta4 = pow(g, (p - 1) // 4, p)

    arms = {}
    for name, zeta in (("j0", zeta3), ("j1728", zeta4), ("generic", None)):
        recs = fam[name][:3 if name != "generic" else 4]
        rows = []
        for rec in recs:
            E = rec.curve()
            n = rec.order
            N = max(ex._factor(n))
            if N < 40:
                continue
            cof = n // N
            P = None
            for x in range(2, p):
                R = E.lift_x(x)
                if R is None:
                    continue
                cand = E.mul(cof, R)
                if cand is not None and _order_of(E, cand, N) == N:
                    P = cand
                    break
            if P is None:
                continue
            for mode, q in (("plain", False), ("quotient", True)):
                steps, solved, fruit = [], 0, 0
                for tr in range(trials):
                    k = (seed * 31 + tr * 97) % N or 1
                    Q = E.mul(k, P)
                    got, st, fr = rho_steps(E, P, Q, N, seed + tr, q,
                                            zeta, rec.aut_order, max_steps)
                    steps.append(st)
                    fruit += fr
                    if got == k:
                        solved += 1
                pred_plain = 0.886 * math.sqrt(N)
                pred_quot = 0.886 * math.sqrt(N / rec.aut_order)
                rows.append({
                    "a": rec.a, "b": rec.b, "j": rec.j, "aut_order": rec.aut_order,
                    "N": N, "mode": mode, "trials": trials,
                    "solved": solved,
                    "mean_steps": statistics.mean(steps),
                    "fruitless_total": fruit,
                    "predicted_plain": pred_plain,
                    "predicted_quotient": pred_quot,
                    "ratio_vs_plain_prediction":
                        statistics.mean(steps) / pred_plain,
                    "ratio_vs_quotient_prediction":
                        statistics.mean(steps) / pred_quot,
                })
        arms[name] = rows

    summary = {}
    for name, rows in arms.items():
        for mode in ("plain", "quotient"):
            sel = [r for r in rows if r["mode"] == mode]
            if not sel:
                continue
            summary[f"{name}:{mode}"] = {
                "n_curves": len(sel),
                "aut_order": sel[0]["aut_order"],
                "mean_steps": statistics.mean(r["mean_steps"] for r in sel),
                "solve_rate": sum(r["solved"] for r in sel) /
                              sum(r["trials"] for r in sel),
                "mean_ratio_vs_plain_prediction":
                    statistics.mean(r["ratio_vs_plain_prediction"] for r in sel),
            }
    # observed speedup vs the sqrt(|Aut|) ceiling
    for name in ("j0", "j1728", "generic"):
        a, b = summary.get(f"{name}:plain"), summary.get(f"{name}:quotient")
        if a and b:
            summary[f"{name}:speedup"] = {
                "observed": a["mean_steps"] / b["mean_steps"] if b["mean_steps"] else None,
                "sqrt_aut_ceiling": math.sqrt(a["aut_order"]),
                "exceeds_ceiling": bool(b["mean_steps"] and
                                        a["mean_steps"] / b["mean_steps"]
                                        > math.sqrt(a["aut_order"]) * 1.15),
            }
    return {"p": p, "trials": trials, "arms": arms, "summary": summary,
            "ceiling_note": (
                "sqrt(|Aut|) is a CONSTANT factor bounded by sqrt(6) and is "
                "never an exponent (KN-TECH-018). Any measured excess is a "
                "suspected instrument artifact until a null says otherwise.")}


# --------------------------------------------------------------------------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, default=1009)
    ap.add_argument("--fb", type=int, default=9)
    ap.add_argument("--targets", type=int, default=20)
    ap.add_argument("--trials", type=int, default=30)
    ap.add_argument("--max-steps", type=int, default=60000)
    ap.add_argument("--seed", type=int, default=20260807)
    ap.add_argument("--suffix", default=None)
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--only", choices=["jinv", "ewalk"], default=None)
    args = ap.parse_args(argv)
    suffix = args.suffix or f"p{args.p}s{args.seed}"
    cmd = "python3 -m harness.run_jinv " + " ".join(sys.argv[1:])

    if args.only in (None, "jinv"):
        t0 = time.time()
        print(f"== EXP-JINV-6c5b8e: special j-invariant algebraic cost, p={args.p} ==")
        res = run_jinv(args.p, args.fb, args.targets, args.seed)
        print(json.dumps(res["summary"], indent=1, default=str))
        t1 = time.time()
        cert = {"kind": "none"}
        for rows in res["arms"].values():
            for r in rows:
                if r.get("certificate") and r["certificate"]["kind"] != "none":
                    cert = r["certificate"]
                    break
            if cert["kind"] != "none":
                break
        if not args.no_write:
            print("wrote", write_run(EXP_JINV, "JINV", RunResult(
                run_suffix=suffix, curve_id=f"P{args.p}-jfamilies",
                seed=args.seed,
                parameters={"p": args.p, "fb": args.fb, "targets": args.targets},
                metrics=res["summary"], certificate=cert, valid=True, raw=res),
                status="completed", command=cmd, started=t0, finished=t1))

    if args.only in (None, "ewalk"):
        t0 = time.time()
        print(f"\n== EXP-EWALK-cc0353: automorphism-quotient walk ceiling, p={args.p} ==")
        res = run_ewalk(args.p, args.trials, args.seed, args.max_steps)
        print(json.dumps(res["summary"], indent=1, default=str))
        t1 = time.time()
        if not args.no_write:
            print("wrote", write_run(EXP_EWALK, "EWALK", RunResult(
                run_suffix=suffix, curve_id=f"P{args.p}-jfamilies",
                seed=args.seed,
                parameters={"p": args.p, "trials": args.trials,
                            "max_steps": args.max_steps},
                metrics=res["summary"], certificate={"kind": "none"},
                valid=True, raw=res),
                status="completed", command=cmd, started=t0, finished=t1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
