#!/usr/bin/env sage
"""SageMath experiment: odd-degree separable edges and inseparable Frobenius in char 2.

Run: sage tools/isogeny_separability_experiment.sage --degree 5 --samples 4 --output results.jsonl
Requires SageMath; deliberately small defaults. Missing edges are reported, not fabricated.
"""
import argparse
import json
import random
import time

def emit(out, row):
    out.write(json.dumps(row, sort_keys=True) + "\n")
    out.flush()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--degree", type=int, default=5)
    parser.add_argument("--samples", type=int, default=4)
    parser.add_argument("--seed", type=int, default=20261009)
    parser.add_argument("--ell", type=int, nargs="+", default=[3, 5, 7])
    parser.add_argument("--output", default="isogeny_separability.jsonl")
    args = parser.parse_args()
    if args.degree < 2 or args.samples < 1:
        parser.error("degree >= 2 and samples >= 1 required")
    F = GF(2**args.degree, 'z')
    rng = random.Random(args.seed)
    with open(args.output, "w") as out:
        for i in range(args.samples):
            a2 = F.fetch_int(rng.randrange(2**args.degree))
            a6 = F.fetch_int(rng.randrange(1, 2**args.degree))
            E = EllipticCurve(F, [F(1), a2, F(0), F(0), a6])
            N = int(E.cardinality())
            P = E.random_point()
            # Relative Frobenius E -> E^(2), not necessarily an endomorphism of E.
            E2 = EllipticCurve(F, [F(1), a2**2, F(0), F(0), a6**2])
            def frob(P):
                if P.is_zero():
                    return E2(0)
                return E2(P[0]**2, P[1]**2)
            Q = E.random_point()
            valid = frob(P+Q) == frob(P)+frob(Q)
            emit(out, dict(kind="frobenius", curve=i, field_degree=args.degree,
                           characteristic=2, map_degree=2, separable=False,
                           kernel_geometric_size=1, group_order=N,
                           homomorphism_verified=bool(valid), seed=args.seed,
                           a2=str(a2), a6=str(a6)))
            if not valid:
                raise AssertionError("Frobenius homomorphism verification failed")
            for ell in args.ell:
                if ell % 2 == 0 or ell < 3 or not Integer(ell).is_prime():
                    raise ValueError("ell must be an odd prime")
                start = time.monotonic()
                try:
                    edges = E.isogenies_prime_degree(ell)
                except (NotImplementedError, ValueError, RuntimeError) as exc:
                    emit(out, dict(kind="edge_search_error", curve=i, ell=ell,
                                   error=type(exc).__name__, detail=str(exc),
                                   elapsed_s=time.monotonic()-start))
                    continue
                emit(out, dict(kind="edge_search", curve=i, ell=ell,
                               edge_count=len(edges), elapsed_s=time.monotonic()-start))
                for j, phi in enumerate(edges):
                    target = phi.codomain()
                    valid = phi(P+Q) == phi(P)+phi(Q)
                    # Degree prime to characteristic => separable.
                    emit(out, dict(kind="odd_isogeny", curve=i, edge=j, ell=ell,
                                   map_degree=int(phi.degree()), separable=True,
                                   group_order=N, target_group_order=int(target.cardinality()),
                                   target_j=str(target.j_invariant()),
                                   homomorphism_verified=bool(valid),
                                   elapsed_s=time.monotonic()-start))
                    if not valid or target.cardinality() != N or phi.degree() != ell:
                        raise AssertionError("isogeny verification failed")

if __name__ == "__main__":
    main()
