#!/usr/bin/env sage
"""Bounded, reproducible prime-degree isogeny discovery (ordinary prime fields)."""
from sage.all import *
import argparse, json, time

def search(p, a, b, primes, out):
    F = GF(p)
    E = EllipticCurve(F, [a, b])
    n = ZZ(E.cardinality())
    t = ZZ(p + 1 - n)
    delta = t*t - 4*p
    if delta >= 0:
        raise ValueError("Expected ordinary elliptic curve with negative Frobenius discriminant")
    D = ZZ(delta).squarefree_part()
    # The squarefree part is not necessarily a fundamental discriminant.
    DK = fundamental_discriminant(D)
    quotient = ZZ(delta // DK)
    if quotient < 0 or not quotient.is_square():
        raise ValueError("Invalid Frobenius conductor decomposition")
    fpi = quotient.sqrt()
    if p.divides(t):
        raise ValueError("Supersingular curve: ordinary volcano classification inapplicable")
    with open(out, "w") as fp:
        for ell in primes:
            ell = ZZ(ell)
            start = time.monotonic()
            row = dict(p=int(p), a=int(a), b=int(b), j=str(E.j_invariant()),
                       trace=int(t), frobenius_discriminant=str(delta),
                       fundamental_discriminant=str(DK), frobenius_conductor=str(fpi),
                       ell=int(ell), ell_divides_fpi=bool(fpi % ell == 0),
                       status="unattempted")
            try:
                maps = E.isogenies_prime_degree(ell)
                edges = []
                for phi in maps:
                    C = phi.codomain()
                    assert phi.degree() == ell
                    assert phi.is_separable()
                    assert C.cardinality() == n
                    # Sage's isogeny construction certifies a map; endomorphism
                    # conductor classification requires a separate certified routine.
                    edges.append(dict(codomain_ainvs=[str(x) for x in C.ainvs()],
                                      codomain_j=str(C.j_invariant()),
                                      degree=int(phi.degree()), separable=True,
                                      same_point_count=True,
                                      conductor_direction="unclassified"))
                row.update(status="constructed" if edges else "no_rational_maps_returned", edges=edges)
            except (ValueError, NotImplementedError, RuntimeError) as exc:
                row.update(status="construction_error", error=repr(exc))
            row["elapsed_seconds"] = time.monotonic() - start
            fp.write(json.dumps(row, sort_keys=True) + "\n")
            fp.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, default=101)
    parser.add_argument("--a", type=int, default=1)
    parser.add_argument("--b", type=int, default=0)
    parser.add_argument("--primes", type=int, nargs="+", default=[2,3,5,7])
    parser.add_argument("--out", default="prime_isogeny_results.jsonl")
    args = parser.parse_args()
    search(args.p, args.a, args.b, args.primes, args.out)
