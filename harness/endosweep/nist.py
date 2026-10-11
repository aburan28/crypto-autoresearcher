"""Every NIST curve through the endomorphism sweep.

FIPS 186-4's fifteen curves -- P-192 to P-521 over prime fields, the Koblitz
curves K-163 to K-571 and the pseudorandom B-163 to B-571 over F_{2^m} --
and the Montgomery and Edwards curves that SP 800-186 adds, as the
std-curves database has them (Curve25519 with Ed25519, Curve448 with Ed448
and Ed448-Goldilocks).  For every curve:

* the group order verified from the constants alone (``targets.verify`` on a
  prime field, on the short Weierstrass model of an Edwards or Montgomery
  curve; ``binary.verify`` on F_{2^m});
* the discriminant scan of ``quadorder`` on t^2 - 4q (|D_K| <= 2 000 000);
* the **exact** CM discriminant D_K and conductor f, from a complete
  factorisation of 4q - t^2 into proven primes.  A factorisation is a
  certificate anyone can re-check in a second (multiply, test primality);
  ``--factorizations`` keeps them, and ``--factor-budget`` lets PARI
  (cypari2, optional) look for missing ones within a time limit per number;
* the cheapest non-scalar endomorphism: on a Koblitz curve the Frobenius tau
  (verified on points, with its eigenvalue on the order-n subgroup), on every
  other curve none of degree below |D_K| / 4;
* on the binary curves, counted scalar multiplications: width-w NAF on every
  curve and, on the Koblitz curves, Solinas' width-w tau-adic NAF.

    python -m harness.endosweep.nist --std-curves STD_CURVES_CHECKOUT \\
        --factorizations research/endosweep_nist_20261006/factorizations.jsonl \\
        --out-dir research/endosweep_nist_20261006
"""
from __future__ import annotations

import argparse
import json
import os
import time

from . import binary as BI
from . import quadorder as QO
from .chainsweep import class_number
from .corpus import _int, load_std_curves
from .targets import verify, weierstrass_target

FIPS_186_4 = ["P-192", "P-224", "P-256", "P-384", "P-521",
              "K-163", "K-233", "K-283", "K-409", "K-571",
              "B-163", "B-233", "B-283", "B-409", "B-571"]
SP_800_186 = ["Curve25519", "Ed25519", "Curve448", "Ed448", "Ed448-Goldilocks"]
SCAN_BOUND = 2_000_000


# ---------------------------------------------------------------------------
# factorisation certificates
# ---------------------------------------------------------------------------

def check_factorization(N: int, factors: list) -> list[tuple[int, int]]:
    """[(p, e)] if prod p^e = N with every p prime; raises otherwise."""
    from sympy import isprime
    fac = [(int(p), int(e)) for p, e in factors]
    prod = 1
    for p, e in fac:
        prod *= p ** e
        if not isprime(p):
            raise ValueError(f"{p} is not prime")
    if prod != N:
        raise ValueError("the factors do not multiply to N")
    return sorted(fac)


def load_factorizations(path: str | None) -> dict[int, list]:
    out: dict[int, list] = {}
    if not path or not os.path.exists(path):
        return out
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if "factors" in r:
                N = int(r["N"])
                out[N] = check_factorization(N, r["factors"])
    return out


def load_partial_certificates(path: str | None) -> dict[int, list]:
    """Partial factorisations {N: [(p, e), ...]}: proven primes found for a number not yet split completely.

    A record carries ``partial_factors`` and the composite ``cofactor`` they leave; it is accepted only
    if the factors are prime, they and the cofactor multiply to N, and the cofactor is composite.
    """
    from sympy import isprime
    out: dict[int, list] = {}
    if not path or not os.path.exists(path):
        return out
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if "partial_factors" not in r:
                continue
            N, C = int(r["N"]), int(r["cofactor"])
            fac = [(int(p), int(e)) for p, e in r["partial_factors"]]
            prod = C
            for p, e in fac:
                if not isprime(p):
                    raise ValueError(f"{p} is not prime")
                prod *= p ** e
            if prod != N or C < 4 or isprime(C):
                raise ValueError("the partial factorisation does not leave a composite cofactor of N")
            out[N] = sorted(fac)
    return out


def _pari_factor(N: int, conn) -> None:
    import cypari2
    pari = cypari2.Pari()
    pari.allocatemem(10 ** 9)
    F = pari.factor(N)
    conn.send([[str(int(F[0][i])), int(F[1][i])] for i in range(len(F[0]))])


def pari_factor(N: int, budget: float) -> list | None:
    """PARI's factorisation of N within ``budget`` seconds, or None (no cypari2, or out of time)."""
    import multiprocessing as mp
    try:
        import cypari2  # noqa: F401
    except ImportError:
        return None
    a, b = mp.Pipe(False)
    p = mp.Process(target=_pari_factor, args=(N, b))
    p.start()
    p.join(budget)
    if p.is_alive():
        p.kill()
        p.join()
        return None
    return a.recv() if a.poll() else None


def partial_factorization(N: int, bound: int = 10 ** 7, known: list | None = None) -> dict:
    """Trial division of N by every prime below ``bound``, and what it proves about |D_K|.

    N = S * C with S the part found and C free of primes below ``bound``.  If C
    is 1, a prime or the square of a prime, the factorisation is complete.
    Otherwise, when C is not a perfect square its squarefree part is a product
    of primes >= bound, so the squarefree part of N -- and |D_K|, which is that
    or four times it -- is at least (the primes of odd exponent in S) * bound.
    ``known`` adds proven primes found otherwise (ECM, say) to S before the trial division.
    """
    from math import isqrt
    from sympy import isprime, primerange
    small, C = [], N
    for p, _e in known or []:
        e = 0
        while C % p == 0:
            C //= p
            e += 1
        if e:
            small.append((p, e))
    for p in primerange(2, bound):
        if p * p > C:
            break
        if any(p == k for k, _ in small):
            continue
        if C % p == 0:
            e = 0
            while C % p == 0:
                C //= p
                e += 1
            small.append((p, e))
    core = 1
    for p, e in small:
        if e % 2:
            core *= p
    r = isqrt(C)
    if C == 1 or isprime(C):
        return {"complete": True, "factors": small + ([(C, 1)] if C > 1 else [])}
    if r * r == C and isprime(r):
        return {"complete": True, "factors": small + [(r, 2)]}
    square = r * r == C
    small.sort()
    return {"complete": False, "trial_division_bound": bound, "factors": small,
            "cofactor_digits": len(str(C)), "cofactor_composite": True, "cofactor_square": square,
            "abs_D_K_at_least": core if square else core * bound}


def exact_discriminant(D_frob: int, fac: list[tuple[int, int]]) -> tuple[int, int]:
    """(D_K, f) with t^2 - 4q = D_K f^2, from the factorisation of 4q - t^2."""
    core, f = 1, 1
    for p, e in fac:
        f *= p ** (e // 2)
        if e % 2:
            core *= p
    if (-core) % 4 == 1:
        DK = -core
    else:
        DK = -4 * core
        if f % 2:
            raise ArithmeticError("t^2 - 4q is not a discriminant")
        f //= 2
    if DK * f * f != D_frob:
        raise ArithmeticError("D_K f^2 does not reproduce t^2 - 4q")
    return DK, f


# ---------------------------------------------------------------------------
# one curve
# ---------------------------------------------------------------------------

def _discriminants(q: int, t: int, factors: dict, budget: float, new: dict) -> dict:
    D_frob = QO.frobenius_discriminant(q, t)
    scan = QO.small_discriminant_scan(D_frob, SCAN_BOUND)
    out = {"q": q, "t": t, "t2_minus_4q_bits": (-D_frob).bit_length(), "scan": {"D_K": scan.found, "f": scan.conductor,
                                                                         "certificate": scan.certificate}}
    N = -D_frob
    fac = factors.get(N)
    if fac is None and scan.found is None and budget > 0:
        t0 = time.time()
        raw = pari_factor(N, budget)
        if raw is not None:
            fac = check_factorization(N, raw)
            factors[N] = fac
            new[N] = {"N": str(N), "factors": [[str(p), e] for p, e in fac],
                      "found_by": "PARI factor", "seconds": round(time.time() - t0, 1)}
    if scan.found is not None:
        DK, f = scan.found, scan.conductor
        out["exact"] = {"D_K": DK, "f": f, "how": "the scan: t^2 - 4q = D_K f^2 with D_K fundamental"}
    elif fac is not None:
        DK, f = exact_discriminant(D_frob, fac)
        out["exact"] = {"D_K": DK, "f": f, "how": "complete factorisation of 4q - t^2 into primes",
                        "factorization": [[str(p), e] for p, e in fac]}
    else:
        part = partial_factorization(N, known=factors.get(("partial", N)))
        if part["complete"]:
            fac = check_factorization(N, part["factors"])
            DK, f = exact_discriminant(D_frob, fac)
            out["exact"] = {"D_K": DK, "f": f, "how": "the known primes and trial division below 10^7 left a prime cofactor",
                            "factorization": [[str(p), e] for p, e in fac]}
        else:
            out["exact"] = None
            lo = part["abs_D_K_at_least"]
            out["bound"] = {"abs_D_K_at_least": lo, "log2": _log2(lo), "min_nonscalar_degree_at_least": lo // 4,
                            "how": (f"4q - t^2 = {' * '.join(str(p) + ('^' + str(e) if e > 1 else '') for p, e in part['factors'])}"
                                    f" * C with C a {part['cofactor_digits']}-digit composite, not a perfect square, "
                                    f"with no prime factor below {part['trial_division_bound']}")}
            return out
    out["exact"]["log2_abs_D_K"] = _log2(abs(DK))
    out["exact"]["min_nonscalar_degree"] = QO.min_nonscalar_degree(DK)
    out["exact"]["class_number"] = class_number(DK) if abs(DK) <= 10 ** 6 else None
    return out


def _log2(x: int) -> float:
    import math
    return round(math.log2(x), 2)


def _no_endo_below(res: dict) -> str:
    if res.get("bound"):
        return f"none below degree {res['bound']['min_nonscalar_degree_at_least']} (partial factorisation)"
    return f"none below degree {SCAN_BOUND // 4} (scan)"


def prime_curve(T, factors: dict, budget: float, new: dict) -> dict:
    W = weierstrass_target(T)
    if W.verified is None:
        verify(W)
    res = {"field": f"F_p, p of {T.p.bit_length()} bits", "model": T.model, "verified": bool(W.verified),
           "verification": W.verification}
    if not W.verified:
        return res
    res.update(_discriminants(W.q, W.trace, factors, budget, new))
    ex = res.get("exact")
    res["cheapest"] = ("none (every non-scalar endomorphism has at least the degree shown)" if ex and abs(ex["D_K"]) > 4
                       else "a unit" if ex else _no_endo_below(res))
    return res


def binary_curve(c: dict, factors: dict, budget: float, new: dict, scalars: int, widths) -> dict:
    F = BI.field_from_entry(c["field"])
    E = BI.BinaryCurve(F, _int(c["params"]["a"]), _int(c["params"]["b"]))
    n, h = _int(c["order"]), _int(c["cofactor"])
    G = (_int(c["generator"]["x"]), _int(c["generator"]["y"]))
    v = BI.verify(E, n, h, G)
    res = {"field": f"F_2^{F.m}, x^{F.m} + " + " + ".join(f"x^{k}" if k else "1" for k in F.low),
           "a": E.a, "b_bits": E.b.bit_length(), "koblitz": BI.is_koblitz(E), "verified": v.ok,
           "verification": v.note}
    if not v.ok:
        return res
    res.update(_discriminants(F.q, v.trace, factors, budget, new))
    kob = None
    if BI.is_koblitz(E):
        kob, checks = BI.koblitz(E, n, h, G)
        res["tau"] = {"mu": kob.mu, "checks": checks, "all_checks_pass": all(checks.values()),
                      "eigenvalue": hex(kob.lam), "delta": [str(kob.delta[0]), str(kob.delta[1])]}
        res["cheapest"] = "Frobenius tau, degree 2 (inseparable): 2 squarings affine, 3 in Lopez-Dahab"
    else:
        ex = res.get("exact")
        res["cheapest"] = ("none (every non-scalar endomorphism has at least the degree shown)" if ex else
                           _no_endo_below(res))
    t0 = time.time()
    res["scalar_multiplication"] = BI.scalar_counts(E, G, n, kob=kob, widths=widths, scalars=scalars)
    res["scalar_multiplication"]["seconds"] = round(time.time() - t0, 1)
    sm = res["scalar_multiplication"]["configs"]
    res["summary"] = {}
    for label, s in (("S_free", 0.0), ("S_equals_M", 1.0)):
        bw = BI.best(sm, "wnaf", s)
        row = {"best_wnaf": bw[0], "wnaf_M_eq": bw[1]}
        if kob:
            bt = BI.best(sm, "tnaf", s)
            row.update({"best_tnaf": bt[0], "tnaf_M_eq": bt[1], "ratio": round(bw[1] / bt[1], 3)})
        res["summary"][label] = row
    return res


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------

def markdown(doc: dict) -> str:
    L = ["# NIST curves through the endomorphism sweep", ""]
    L.append("FIPS 186-4's fifteen curves and the Montgomery and Edwards curves of SP 800-186 as std-curves has "
             "them.  `D_K` is exact where 4q - t^2 is completely factored into primes (the factorisation is in "
             "`nist.json`); the degree column is the smallest norm of an element of the maximal order outside Z, a lower bound on "
             "the degree of every endomorphism outside Z.")
    L.append("")
    L.append("| curve | field | verified | D_K | log2 abs(D_K) | f | smallest non-scalar degree | cheapest endomorphism |")
    L.append("|:--|:--|:--|--:|--:|--:|--:|:--|")
    for name, r in doc["curves"].items():
        ex = r.get("exact")
        dup = f" (same curve as {r['duplicate_of']})" if r.get("duplicate_of") else ""
        if ex:
            dk = str(ex["D_K"]) if abs(ex["D_K"]) < 10 ** 12 else f"−({len(str(abs(ex['D_K'])))} digits)"
            deg = ex["min_nonscalar_degree"]
            degs = str(deg) if deg < 10 ** 12 else f"2^{_log2(deg)}"
            L.append(f"| {name}{dup} | {r['field']} | {r['verified']} | {dk} | {ex['log2_abs_D_K']} | "
                     f"{ex['f'] if ex['f'] < 10 ** 12 else '(' + str(len(str(ex['f']))) + ' digits)'} | {degs} | "
                     f"{r.get('cheapest', '')} |")
        elif r.get("bound"):
            bd = r["bound"]
            L.append(f"| {name}{dup} | {r['field']} | {r['verified']} | abs(D_K) ≥ {bd['abs_D_K_at_least']} | "
                     f"≥ {bd['log2']} | | ≥ {bd['min_nonscalar_degree_at_least']} | {r.get('cheapest', '')} |")
        else:
            L.append(f"| {name}{dup} | {r['field']} | {r['verified']} | abs(D_K) > {SCAN_BOUND} | | | ≥ {SCAN_BOUND // 4} | "
                     f"{r.get('cheapest', '')} |")
    L.append("")
    L.append("## Binary curves: counted scalar multiplication")
    L.append("")
    L.append("Mean field multiplications (M) and squarings (S) per `k·G` over random scalars, counted on the "
             "arithmetic executed (Lopez-Dahab coordinates, affine tables from one batched Itoh-Tsujii inversion). "
             "M_eq is given with squarings free and with squarings as dear as multiplications, the two ends of "
             "what a polynomial-basis implementation pays.")
    L.append("")
    L.append("| curve | best wNAF (S free) | M_eq | best TNAF (S free) | M_eq | ratio | best wNAF (S = M) | M_eq | "
             "best TNAF (S = M) | M_eq | ratio | results agree |")
    L.append("|:--|:--|--:|:--|--:|--:|:--|--:|:--|--:|--:|:--|")
    for name, r in doc["curves"].items():
        if "summary" not in r:
            continue
        a, b = r["summary"]["S_free"], r["summary"]["S_equals_M"]
        sm = r["scalar_multiplication"]
        L.append(f"| {name} | {a['best_wnaf']} | {a['wnaf_M_eq']} | {a.get('best_tnaf', '—')} | {a.get('tnaf_M_eq', '—')} | "
                 f"{a.get('ratio', '—')} | {b['best_wnaf']} | {b['wnaf_M_eq']} | {b.get('best_tnaf', '—')} | "
                 f"{b.get('tnaf_M_eq', '—')} | {b.get('ratio', '—')} | "
                 f"{sm['all_algorithms_agree'] and sm['reference_agrees']} ({sm['scalars']} scalars) |")
    L.append("")
    L.append("## Every configuration counted")
    for name, r in doc["curves"].items():
        if "scalar_multiplication" not in r:
            continue
        L.append("")
        L.append(f"### {name}")
        L.append("")
        L.append("| configuration | M | S | inversions | M sd | precompute M | precompute S |")
        L.append("|:--|--:|--:|--:|--:|--:|--:|")
        for k, v in r["scalar_multiplication"]["configs"].items():
            L.append(f"| {k} | {v['M']} | {v['S']} | {v['I']} | {v['M_sd']} | {v['precompute_M']} | {v['precompute_S']} |")
    L.append("")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="every NIST curve through the endomorphism sweep")
    ap.add_argument("--std-curves", required=True, help="a J08nY/std-curves checkout")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--factorizations", default=None, help="JSON-lines factorisation certificates (read, and extended)")
    ap.add_argument("--factor-budget", type=float, default=0.0, help="seconds of PARI factoring per missing number")
    ap.add_argument("--scalars", type=int, default=32)
    ap.add_argument("--widths", default="2,3,4,5,6,7")
    args = ap.parse_args(argv)
    widths = tuple(int(w) for w in args.widths.split(","))
    factors = load_factorizations(args.factorizations)
    factors.update({("partial", N): fac for N, fac in load_partial_certificates(args.factorizations).items()})
    new: dict = {}
    raw = {}
    for cat in ("nist", "other"):
        for c in json.load(open(os.path.join(args.std_curves, cat, "curves.json")))["curves"]:
            raw[f"{cat}/{c['name']}"] = c
    targets = {e.name: T for T, e, _ in load_std_curves(args.std_curves) if T is not None}
    names = [f"nist/{n}" for n in FIPS_186_4] + [f"other/{n}" for n in SP_800_186]
    doc: dict = {"std_curves_commit": _git_head(args.std_curves), "scan_bound": SCAN_BOUND, "curves": {}}
    seen: dict = {}
    for name in names:
        c = raw[name]
        t0 = time.time()
        if c["field"]["type"] == "Prime":
            r = prime_curve(targets[name], factors, args.factor_budget, new)
            key = None
            if r.get("verified"):
                W = weierstrass_target(targets[name])
                p, a, b = W.p, W.coeffs["a"] % W.p, W.coeffs["b"] % W.p
                den = (4 * pow(a, 3, p) + 27 * b * b) % p
                key = (p, 1728 * 4 * pow(a, 3, p) * pow(den, -1, p) % p, W.n, W.h)
            if key in seen:
                r["duplicate_of"] = seen[key]
            elif key:
                seen[key] = name
        else:
            r = binary_curve(c, factors, args.factor_budget, new, args.scalars, widths)
        r["elapsed_s"] = round(time.time() - t0, 1)
        doc["curves"][name] = r
        ex = r.get("exact")
        print(f"[{r['elapsed_s']:7.1f}s] {name:24s} verified={r.get('verified')} "
              f"D_K={'exact, log2 ' + str(ex['log2_abs_D_K']) if ex else 'scan only'} "
              f"{r.get('summary', {}).get('S_equals_M', '')}", flush=True)
    if new and args.factorizations:
        with open(args.factorizations, "a") as f:
            for rec in new.values():
                f.write(json.dumps(rec) + "\n")
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "nist.json"), "w") as f:
        json.dump(doc, f, indent=1, default=str)
        f.write("\n")
    with open(os.path.join(args.out_dir, "nist.md"), "w") as f:
        f.write(markdown(doc))
    bad = [n for n, r in doc["curves"].items() if not r.get("verified")
           or ("tau" in r and not r["tau"]["all_checks_pass"])
           or ("scalar_multiplication" in r and not (r["scalar_multiplication"]["all_algorithms_agree"]
                                                    and r["scalar_multiplication"]["reference_agrees"]))]
    print("failed:", bad)
    return 1 if bad else 0


def _git_head(path: str) -> str | None:
    import subprocess
    try:
        return subprocess.run(["git", "-C", path, "rev-parse", "HEAD"], check=True, capture_output=True,
                              text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


if __name__ == "__main__":
    raise SystemExit(main())
