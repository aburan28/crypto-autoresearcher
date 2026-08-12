"""Executor for EXP-EWALK-4fc679 (GOAL-ENDO-001, BATCH-cb71b5).

SUPERSEDES the EXP-EWALK-cc0353 measurement, whose quotient walk was wrong.

What was wrong, stated plainly, because it is the whole reason this file exists:
`harness/run_jinv.py:rho_steps` canonicalised the walk point to its Aut-orbit
representative but did NOT carry the automorphism's action through to the
(a, b) exponents. An automorphism phi acts on the prime-order subgroup as
multiplication by a scalar lambda, so replacing R = [a]P + [b]Q by phi^i(R)
replaces the exponents by (lambda^i a, lambda^i b). Omitting that makes every
orbit collision produce an exponent relation that does not hold, which the code
then discarded as "fruitless". On j = 1728 that turned a 9-step solve into a
1676-step one -- a 260x SLOWDOWN misreported as a measurement. It is an
implementation defect and is never evidence about the sqrt(|Aut|) ceiling
(AGENTS.md rule 5). RUN-EWALK-p1009-a is superseded by CORR-20260807-*.

This version:
  * computes lambda from the CM equation (L^2+L+1=0 for j=0, L^2+1=0 for j=1728)
    and VERIFIES it against phi(P) = [lambda]P before walking -- publicly
    computable without solving any discrete logarithm, as H-ENDO-001 requires;
  * carries lambda^i through the exponents on every canonicalisation;
  * refuses to run an arm whose lambda does not exist in Z/N (which happens
    whenever 3 (resp. 4) does not divide N-1) and records the refusal instead of
    silently falling back to |Aut| = 2;
  * runs at N large enough for the step count to mean something.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
import time

from . import exp_icinv as ex
from . import isogeny_class as ic
from .runner import RunResult, write_run
from .toycurve import EllipticCurve, Point

EXP_ID = "EXP-EWALK-4fc679"
SUPERSEDES = "EXP-EWALK-cc0353 / RUN-EWALK-p1009-a"


def _order_of(E: EllipticCurve, P: Point, n: int) -> int:
    o = n
    for q in ex._factor(n):
        while o % q == 0 and E.mul(o // q, P) is None:
            o //= q
    return o


def _point_of_order(E: EllipticCurve, n: int, N: int) -> Point:
    cof = n // N
    for x in range(2, min(E.p, 20000)):
        R = E.lift_x(x)
        if R is None:
            continue
        P = E.mul(cof, R)
        if P is not None and _order_of(E, P, N) == N:
            return P
    return None


def find_curves(p: int, want: int, kind: str, min_N_bits: int) -> list:
    """Curves of the requested kind with a large prime subgroup.

    Does NOT enumerate the whole field -- EWALK needs a handful of curves at
    p far too large for the O(p^2) full census, so traces are computed only for
    the candidates actually tried.
    """
    out = []
    g = ic._multiplicative_generator(p)
    if kind == "j0":
        cands = [(0, pow(g, i, p)) for i in range(1, 400)]
    elif kind == "j1728":
        cands = [(pow(g, i, p), 0) for i in range(1, 400)]
    else:
        cands = [(i, 3 * i + 7) for i in range(1, 400)]
    for (a, b) in cands:
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            continue
        n = ic.curve_order(p, a, b)
        N = max(ex._factor(n))
        if N.bit_length() < min_N_bits:
            continue
        j = ic.j_invariant(p, a, b)
        aut = 6 if (j == 0 and p % 3 == 1) else (4 if (j == 1728 % p and p % 4 == 1) else 2)
        out.append({"a": a, "b": b, "j": j, "order": n, "N": N, "aut": aut,
                    "trace": p + 1 - n})
        if len(out) >= want:
            break
    return out


def automorphism(p: int, kind: str, zeta: int):
    """The non-trivial automorphism as a map on points, plus its order."""
    if kind == "j0":
        return (lambda P: None if P is None else (P[0] * zeta % p, P[1])), 3
    if kind == "j1728":
        return (lambda P: None if P is None else ((-P[0]) % p, P[1] * zeta % p)), 4
    return (lambda P: P), 1


def eigenvalue(E: EllipticCurve, P: Point, phi, N: int, kind: str) -> int | None:
    """lambda in Z/N with phi(P) = [lambda]P, from the CM equation.

    PUBLICLY COMPUTABLE: the candidates are the roots of L^2+L+1 (j=0) or
    L^2+1 (j=1728) mod N, obtained by Tonelli-Shanks, and the right one is
    selected by a single scalar multiplication. No discrete logarithm is solved,
    which is exactly the exclusion H-ENDO-001 states.
    """
    D0 = -3 if kind == "j0" else (-4 if kind == "j1728" else None)
    if D0 is None:
        return None
    cands = ic.cm_eigenvalues(E.p, N, D0)
    target = phi(P)
    for lam in cands:
        if E.mul(lam, P) == target:
            return lam
    return None


def rho(E: EllipticCurve, P: Point, Q: Point, N: int, seed: int, *,
        phi=None, lam: int | None = None, aut_order: int = 1,
        max_steps: int = 4_000_000) -> tuple[int | None, int, int]:
    """r-adding Pollard rho; walks on Aut-orbit representatives when phi is given.

    Returns (recovered k or None, steps, fruitless_events). The exponent
    bookkeeping is the part the superseded version omitted: canonicalising R to
    phi^i(R) multiplies (a, b) by lam^i.
    """
    r = 32
    offs = []
    for i in range(r):
        h = int(hashlib.sha256(f"{seed}:o:{i}".encode()).hexdigest(), 16)
        ai, bi = h % N, (h >> 128) % N
        offs.append((ai, bi, E.add(E.mul(ai, P), E.mul(bi, Q))))

    def canon(R: Point) -> tuple[Point, int]:
        """(representative, exponent multiplier) for R's orbit under Aut."""
        if R is None:
            return None, 1
        best, mult = R, 1
        # negation is always an automorphism: eigenvalue -1
        cands = [(R, 1), (E.negate(R), N - 1)]
        if phi is not None and lam is not None:
            S, m = R, 1
            for _ in range(aut_order // 2 - 1 if aut_order > 2 else 0):
                S = phi(S)
                m = m * lam % N
                cands.append((S, m))
                cands.append((E.negate(S), (N - m) % N))
        for (S, m) in cands:
            if S is not None and (best is None or S < best):
                best, mult = S, m
        return best, mult

    a = (seed * 7 + 1) % N or 1
    b = 0
    R = E.mul(a, P)
    c, m = canon(R)
    seen = {c: (a * m % N, b * m % N)}
    fruitless = 0
    for step in range(1, max_steps + 1):
        cR, _ = canon(R)
        if cR is None:
            return None, step, fruitless
        ai, bi, T = offs[cR[0] % r]
        R2 = E.add(R, T)
        if R2 is None:
            return None, step, fruitless
        if R2 == R:
            fruitless += 1
        R = R2
        a, b = (a + ai) % N, (b + bi) % N
        c, m = canon(R)
        ca, cb = a * m % N, b * m % N
        if c in seen:
            a2, b2 = seen[c]
            db = (cb - b2) % N
            if db == 0:
                fruitless += 1
                continue
            k = (a2 - ca) * pow(db, -1, N) % N
            if E.mul(k, P) == Q:
                return k, step, fruitless
            fruitless += 1
            continue
        seen[c] = (ca, cb)
    return None, max_steps, fruitless


def run(p: int, trials: int, seed: int, min_N_bits: int, max_steps: int) -> dict:
    g = ic._multiplicative_generator(p)
    zeta3 = pow(g, (p - 1) // 3, p) if p % 3 == 1 else None
    zeta4 = pow(g, (p - 1) // 4, p) if p % 4 == 1 else None

    arms, refusals = {}, []
    for kind, zeta in (("j0", zeta3), ("j1728", zeta4), ("generic", None)):
        if kind in ("j0", "j1728") and zeta is None:
            refusals.append({"arm": kind, "reason":
                             f"p={p} does not admit the required root of unity"})
            continue
        recs = find_curves(p, 2, kind, min_N_bits)
        rows = []
        for rec in recs:
            E = EllipticCurve(p, rec["a"], rec["b"])
            N = rec["N"]
            P = _point_of_order(E, rec["order"], N)
            if P is None:
                continue
            phi, ao = automorphism(p, kind, zeta) if zeta else (None, 1)
            lam = eigenvalue(E, P, phi, N, kind) if phi else None
            if kind in ("j0", "j1728") and lam is None:
                refusals.append({"arm": kind, "a": rec["a"], "b": rec["b"], "N": N,
                                 "reason": ("no CM eigenvalue in Z/N: the "
                                            "automorphism does not act with a "
                                            "scalar of the required order on "
                                            "this subgroup")})
                continue
            aut_used = rec["aut"] if lam is not None else 2
            for mode in ("plain", "quotient"):
                steps, solved, fruit = [], 0, 0
                for tr in range(trials):
                    k = (seed * 31 + tr * 97) % N or 1
                    Q = E.mul(k, P)
                    got, st, fr = rho(
                        E, P, Q, N, seed + tr,
                        phi=(phi if mode == "quotient" else None),
                        lam=(lam if mode == "quotient" else None),
                        aut_order=(aut_used if mode == "quotient" else 2),
                        max_steps=max_steps)
                    steps.append(st)
                    fruit += fr
                    solved += int(got == k)
                pred = 0.886 * math.sqrt(N / (aut_used if mode == "quotient" else 2))
                rows.append({
                    "a": rec["a"], "b": rec["b"], "j": rec["j"], "N": N,
                    "aut_available": rec["aut"], "aut_used": aut_used,
                    "eigenvalue_found": lam is not None, "mode": mode,
                    "trials": trials, "solved": solved,
                    "mean_steps": statistics.mean(steps),
                    "fruitless_total": fruit,
                    "prediction": pred,
                    "ratio_observed_over_predicted":
                        statistics.mean(steps) / pred,
                })
        arms[kind] = rows

    summary = {"refusals": refusals}
    for kind, rows in arms.items():
        for mode in ("plain", "quotient"):
            sel = [r for r in rows if r["mode"] == mode and r["solved"] == r["trials"]]
            allsel = [r for r in rows if r["mode"] == mode]
            if not allsel:
                continue
            summary[f"{kind}:{mode}"] = {
                "n_curves": len(allsel),
                "all_trials_solved": len(sel) == len(allsel),
                "solve_rate": sum(r["solved"] for r in allsel) /
                              sum(r["trials"] for r in allsel),
                "aut_used": allsel[0]["aut_used"],
                "mean_steps": statistics.mean(r["mean_steps"] for r in allsel),
                "mean_ratio_observed_over_predicted":
                    statistics.mean(r["ratio_observed_over_predicted"] for r in allsel),
            }
        pl, qt = summary.get(f"{kind}:plain"), summary.get(f"{kind}:quotient")
        if pl and qt and qt["mean_steps"]:
            obs = pl["mean_steps"] / qt["mean_steps"]
            # BOTH modes quotient by negation -- `canon` always includes it --
            # so the INCREMENTAL ceiling for the quotient arm is
            # sqrt(|Aut| / 2), not sqrt(|Aut|). Comparing against sqrt(|Aut|)
            # would understate the measured speedup by sqrt(2) and is the
            # mistake this line exists to avoid. The program's rho baseline
            # convention already folds the negation sqrt(2) in (KN-TECH-006).
            incremental = math.sqrt(qt["aut_used"] / 2)
            summary[f"{kind}:speedup"] = {
                "observed_speedup_quotient_over_plain": obs,
                "incremental_ceiling_sqrt_aut_over_2": incremental,
                "absolute_ceiling_sqrt_aut": math.sqrt(qt["aut_used"]),
                "observed_over_incremental_ceiling": obs / incremental,
                "exceeds_incremental_ceiling_by_15pct":
                    bool(obs > incremental * 1.15),
                "note": ("both arms already quotient by negation, so the "
                         "comparable prediction is sqrt(|Aut|/2); for a generic "
                         "curve |Aut| = 2 makes the two arms identical BY "
                         "CONSTRUCTION and a speedup of exactly 1.0 there is a "
                         "self-check, not a measurement"),
            }
    summary["ceiling_note"] = (
        "sqrt(|Aut|) is a CONSTANT factor bounded by sqrt(6) and never an "
        "exponent (KN-TECH-018). A measured excess is a suspected instrument "
        "artifact until a null control says otherwise. A measured SHORTFALL is "
        "a legitimate result: fruitless-cycle handling has real cost.")
    return {"p": p, "trials": trials, "min_N_bits": min_N_bits,
            "supersedes": SUPERSEDES, "arms": arms, "summary": summary}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, default=100003)
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20260807)
    ap.add_argument("--min-n-bits", type=int, default=14)
    ap.add_argument("--max-steps", type=int, default=400000)
    ap.add_argument("--suffix", default=None)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    t0 = time.time()
    res = run(args.p, args.trials, args.seed, args.min_n_bits, args.max_steps)
    print(json.dumps(res["summary"], indent=1, default=str))
    t1 = time.time()
    if not args.no_write:
        print("wrote", write_run(EXP_ID, "EWALK", RunResult(
            run_suffix=args.suffix or f"p{args.p}s{args.seed}",
            curve_id=f"P{args.p}-jfamilies", seed=args.seed,
            parameters={"p": args.p, "trials": args.trials,
                        "min_N_bits": args.min_n_bits,
                        "max_steps": args.max_steps},
            metrics=res["summary"], certificate={"kind": "none"},
            valid=True, raw=res),
            status="completed",
            command="python3 -m harness.run_ewalk2 " + " ".join(sys.argv[1:]),
            started=t0, finished=t1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
