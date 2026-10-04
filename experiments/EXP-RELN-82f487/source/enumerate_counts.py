"""Stage 1: base construction per arm and exhaustive enumeration of the
m=3 negation-closed decomposition-count vector c_D(r), with the closed-form
total check sum_r c_D(r) = C(B+2,3) (deviation exactly 0 or the run halts).

This is the FALLBACK enumerator authorized by specification.yaml's
EXHAUSTIVE-LABEL-SOURCE-FALLBACK clause: EXP-RELN-f202be's committed count
vectors were built under a DIFFERENT curve-seed convention and geometry
panel (x_interval_low/mid, qr_class; not this contract's E_x_interval/
E_random_matched/ZN_interval/ZN_random/E_log_interval_canary panel with
curve_seeds [101,102,103]), so no identical (p,a,b,N,base_seed,arm,
convention) cell exists to reuse; this module is used for every cell run
under this contract (recorded plainly in every manifest and in the
execution report).
"""
from __future__ import annotations

import hashlib
import itertools
import math
import os
import sys
from math import comb

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from harness.toycurve import EllipticCurve  # noqa: E402


def seed_int(seed: int, tag: str) -> int:
    h = hashlib.sha256(f"{seed}:{tag}".encode()).hexdigest()
    return int(h, 16)


def b_eff_for_N(N: int) -> int:
    cube = (6 * N) ** (1.0 / 3.0)
    inner = math.ceil(cube - 1e-9)
    if inner ** 3 < 6 * N:
        inner += 1
    return math.ceil(inner / 2.0)


def all_curve_points(curve: EllipticCurve):
    """All affine points of E(F_p) (identity O excluded), by naive scan.
    Toy scale only (p up to ~10^6)."""
    pts = []
    p = curve.p
    for x in range(p):
        rhs = (x * x * x + curve.a * x + curve.b) % p
        if rhs == 0:
            pts.append((x, 0))
        elif pow(rhs, (p - 1) // 2, p) == 1:
            y = curve.lift_x(x)[1]
            pts.append((x, y))
            pts.append((x, (-y) % p))
    return pts


def build_base_E_x_interval(curve: EllipticCurve, points_by_x: dict, base_seed: int, B_eff: int):
    x_values = sorted(points_by_x.keys())
    n = len(x_values)
    x0_idx = seed_int(base_seed, "x0") % n
    # smallest window (consecutive by x rank, wrapping) giving exactly B_eff
    # distinct x-values
    idxs = [(x0_idx + i) % n for i in range(B_eff)]
    chosen_x = [x_values[i] for i in idxs]
    D = []
    for x in chosen_x:
        D.extend(points_by_x[x])  # both +-P for this x
    return D, {"x0_index": x0_idx, "x_values": chosen_x}


def build_base_E_random_matched(curve: EllipticCurve, points_by_x: dict, base_seed: int, B_eff: int):
    import numpy as np
    x_values = sorted(points_by_x.keys())
    rng = np.random.default_rng(seed_int(base_seed, "random_matched") % (2 ** 32))
    chosen_idx = rng.choice(len(x_values), size=B_eff, replace=False)
    chosen_x = [x_values[i] for i in sorted(chosen_idx.tolist())]
    D = []
    for x in chosen_x:
        D.extend(points_by_x[x])
    return D, {"x_values": chosen_x}


def build_base_ZN_interval(N: int, B_eff: int):
    D = []
    for d in range(1, B_eff + 1):
        D.append(d % N)
        D.append((-d) % N)
    return D, {"interval": [1, B_eff]}


def build_base_ZN_random(N: int, base_seed: int, B_eff: int):
    import numpy as np
    rng = np.random.default_rng(seed_int(base_seed, "zn_random") % (2 ** 32))
    hi = (N - 1) // 2
    chosen = rng.choice(hi, size=B_eff, replace=False) + 1
    D = []
    for d in chosen.tolist():
        D.append(d % N)
        D.append((-d) % N)
    return D, {"residues": chosen.tolist()}


def build_base_E_log_canary(curve: EllipticCurve, P, B_eff: int):
    D = []
    cur = P
    small_multiples = []
    for j in range(1, B_eff + 1):
        Rj = curve.mul(j, P)
        small_multiples.append(j)
        D.append(Rj)
        D.append(curve.negate(Rj))
    return D, {"multiples": small_multiples}


def enumerate_count_vector_E(curve: EllipticCurve, D):
    """Full c_D(r) for r ranging over all group elements, arity m=3,
    unreduced multisets with repetition. Returns dict point-> count and the
    total (must equal C(B+2,3))."""
    B = len(D)
    counts = {}
    add = curve.add
    for i, j, k in itertools.combinations_with_replacement(range(B), 3):
        s = add(add(D[i], D[j]), D[k])
        key = s if s is not None else "O"
        counts[key] = counts.get(key, 0) + 1
    total = sum(counts.values())
    expected = comb(B + 2, 3)
    return counts, total, expected


def enumerate_count_vector_ZN(N: int, D):
    B = len(D)
    counts = {}
    for i, j, k in itertools.combinations_with_replacement(range(B), 3):
        s = (D[i] + D[j] + D[k]) % N
        counts[s] = counts.get(s, 0) + 1
    total = sum(counts.values())
    expected = comb(B + 2, 3)
    return counts, total, expected


def enumerate_with_triples_E(curve: EllipticCurve, D):
    """Like enumerate_count_vector_E but also records, per target key, the
    list of (i,j,k) base-index triples certifying that decomposition (used
    to build the training graph in graph_build.py; NEVER consumed by
    features.py, which is statically audited to forbid this import)."""
    B = len(D)
    counts = {}
    triples = {}
    add = curve.add
    for i, j, k in itertools.combinations_with_replacement(range(B), 3):
        s = add(add(D[i], D[j]), D[k])
        key = s if s is not None else "O"
        counts[key] = counts.get(key, 0) + 1
        triples.setdefault(key, []).append((i, j, k))
    total = sum(counts.values())
    expected = comb(B + 2, 3)
    return counts, triples, total, expected


def enumerate_with_triples_ZN(N: int, D):
    B = len(D)
    counts = {}
    triples = {}
    for i, j, k in itertools.combinations_with_replacement(range(B), 3):
        s = (D[i] + D[j] + D[k]) % N
        counts[s] = counts.get(s, 0) + 1
        triples.setdefault(s, []).append((i, j, k))
    total = sum(counts.values())
    expected = comb(B + 2, 3)
    return counts, triples, total, expected


if __name__ == "__main__":
    from curve_gen import generate_curve
    rec = generate_curve(14, 1, 101)
    curve = EllipticCurve(rec["p"], rec["a"], rec["b"])
    N = rec["N"]
    B_eff = b_eff_for_N(N)
    print("B_eff", B_eff, "B", 2 * B_eff)
    pts = all_curve_points(curve)
    points_by_x = {}
    for (x, y) in pts:
        points_by_x.setdefault(x, []).append((x, y))
    D, meta = build_base_E_x_interval(curve, points_by_x, 201, B_eff)
    print("base size", len(D))
    counts, total, expected = enumerate_count_vector_E(curve, D)
    print("total", total, "expected", expected, "deviation", total - expected)
