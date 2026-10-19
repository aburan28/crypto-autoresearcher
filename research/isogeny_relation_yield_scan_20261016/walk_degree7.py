"""Enumerate a bounded certified degree-7 floor walk, without yield sampling.

The JSONL output is opened exclusively and fsynced after every record.  A
failure leaves its prefix intact for diagnosis.  This is a preparatory curve
search, not the scientific relation-yield runner.
"""

import argparse
import json
import os
import time

from sage.all import EllipticCurve, GF, is_prime
from sage.version import version as sage_version


PANELS = {
    "P29": (320092037, 320091991, 101186781, 57596093, 0, 112219098, 8209, 2048),
    "P37": (81640512137, 81640511861, 6064550680, 68678790390, 2, 25752399999, 131101, 256),
}
SMOKE_SCALAR = 123456789


def model(curve):
    return {"a": int(curve.a4()), "b": int(curve.a6()),
            "j": int(curve.j_invariant())}


def point(point_value):
    return [int(point_value[0]), int(point_value[1])]


def canonical_curve(field, j, r, nonsquare):
    if int(j) in (0, 1728):
        raise ValueError("exceptional j requires a versioned model rule")
    a = 3 * j / (field(1728) - j)
    b = 2 * j / (field(1728) - j)
    first = EllipticCurve(field, [a, b])
    if int(first.cardinality()) == r:
        return first, "untwisted"
    second = EllipticCurve(field, [nonsquare**2 * a, nonsquare**3 * b])
    if int(second.cardinality()) != r:
        raise ValueError("neither canonical twist has the expected group order")
    return second, "quadratic_twist"


def emit(handle, obj):
    handle.write(json.dumps(obj, sort_keys=True) + "\n")
    handle.flush()
    os.fsync(handle.fileno())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stratum", choices=sorted(PANELS), required=True)
    parser.add_argument("--edges", type=int, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    p, r, a, b, gx, gy, conductor, full_count = PANELS[args.stratum]
    if not 1 <= args.edges <= full_count:
        parser.error(f"--edges must be in 1..{full_count}")
    if os.path.exists(args.out):
        parser.error("output already exists; records are write-once")
    field = GF(p)
    if not is_prime(p) or not is_prime(r):
        raise ValueError("field or group order is not prime")
    nonsquare = next(field(n) for n in range(2, p) if not field(n).is_square())
    original = EllipticCurve(field, [a, b])
    if int(original.cardinality()) != r:
        raise ValueError("source group order changed")
    original_g = original(field(gx), field(gy))
    original_q = SMOKE_SCALAR * original_g
    current, source_twist = canonical_curve(field, original.j_invariant(), r, nonsquare)
    source_iso = original.isomorphism_to(current)
    current_g, current_q = source_iso(original_g), source_iso(original_q)
    previous_j = None
    seen = {int(current.j_invariant())}
    start = time.monotonic()
    with open(args.out, "x", encoding="utf-8") as handle:
        emit(handle, {"kind": "header", "schema": "ectd.degree7.walk.v1",
                      "stratum": args.stratum, "requested_edges": args.edges,
                      "sage_version": sage_version, "p": p, "r": r,
                      "D_K": -19, "f_pi": conductor, "f_E": conductor,
                      "degree": 7, "smoke_scalar": SMOKE_SCALAR,
                      "original_source": model(original), "source_generator": [gx, gy],
                      "canonical_source": model(current), "source_twist": source_twist,
                      "source_isomorphism": str(source_iso.rational_maps()),
                      "least_nonsquare": int(nonsquare)})
        for index in range(1, args.edges + 1):
            neighbors = sorted(current.isogenies_prime_degree(7),
                               key=lambda phi: int(phi.codomain().j_invariant()))
            if len(neighbors) != 2:
                raise ValueError(f"step {index}: expected two degree-7 neighbors, got {len(neighbors)}")
            phi = next((x for x in neighbors
                        if int(x.codomain().j_invariant()) != previous_j), None)
            if phi is None:
                raise ValueError(f"step {index}: no nonbacktracking neighbor")
            raw = phi.codomain()
            next_j = int(raw.j_invariant())
            if next_j in seen:
                raise ValueError(f"step {index}: repeated j={next_j}")
            dual = phi.dual()
            raw_g, raw_q = phi(current_g), phi(current_q)
            checks = {
                "degree_7": int(phi.degree()) == 7,
                "raw_order_r": int(raw.cardinality()) == r,
                "dual_g": dual(raw_g) == 7 * current_g,
                "dual_q": dual(raw_q) == 7 * current_q,
                "smoke_scalar_raw": raw_q == SMOKE_SCALAR * raw_g,
            }
            next_curve, twist = canonical_curve(field, raw.j_invariant(), r, nonsquare)
            iso = raw.isomorphism_to(next_curve)
            next_g, next_q = iso(raw_g), iso(raw_q)
            checks.update({
                "canonical_j": int(next_curve.j_invariant()) == next_j,
                "canonical_order_r": int(next_curve.cardinality()) == r,
                "canonical_generator_order_r": next_g != next_curve(0) and r * next_g == next_curve(0),
                "smoke_scalar_canonical": next_q == SMOKE_SCALAR * next_g,
            })
            if not all(checks.values()):
                raise ValueError(f"step {index}: failed checks {checks}")
            emit(handle, {"kind": "edge", "index": index, "source": model(current),
                          "raw_codomain": model(raw), "canonical_codomain": model(next_curve),
                          "kernel_polynomial": str(phi.kernel_polynomial()),
                          "codomain_isomorphism": str(iso.rational_maps()),
                          "canonical_twist": twist, "image_generator": point(next_g),
                          "image_smoke_target": point(next_q), "checks": checks})
            previous_j = int(current.j_invariant())
            current, current_g, current_q = next_curve, next_g, next_q
            seen.add(next_j)
        emit(handle, {"kind": "complete", "edges": args.edges,
                      "distinct_vertices": len(seen), "last_j": int(current.j_invariant()),
                      "wall_seconds": time.monotonic() - start,
                      "all_edge_checks_passed": True})


if __name__ == "__main__":
    main()
