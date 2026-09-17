#!/usr/bin/env python3
"""eq4sys.py -- the SINGLE summation-polynomial system of Semaev ePrint 2015/310
eq. (4), Weil-descended over F_2.  This is the `nearby_object` control of
EXP-SEMBIN-7e1371: the system the chained system (5) replaces.

    S_{m+1}(x_1, ..., x_m, R_X) = 0,   x_i in V, dim_F2 V = k,

descended to n Boolean equations in N = m k variables.  The paper states the
maximal total degree of those Boolean equations is at most m(m-1) (Section 4.5,
"According to [10, 3] the equation (4) ... is reducible ... to a system of n
Boolean equations in mk variables ... The maximal total degree of the Boolean
equations is at most m(m-1)"), against degree 3 for eq. (5).  The measured
degree profile is recorded per instance rather than assumed.

Summation polynomials are built by Semaev's own resultant recursion

    S_4(x1, x2, x3, x4) = Res_X( S_3(x1, x2, X), S_3(x3, x4, X) ),

computed here as the 4x4 Sylvester determinant over the Boolean coefficient
ring, NOT from a transcribed closed form: the determinant is the definition, a
ring homomorphism commutes with it, and there is no expansion to get wrong.

Supported m: 2 and 3.
  * m = 2 is S_3(x_1, x_2, R_X) = 0, which is eq. (5) at t = 2 -- the two
    systems COINCIDE there.  That is a fact about the construction, not a defect
    of the control, and the driver records it instead of pretending to two
    independent measurements.
  * m >= 4 needs S_5 and beyond (Sylvester determinants of size 6 and up, with
    coefficients of rapidly growing support).  Not implemented; the driver
    records those cells as `not_implemented` and no verdict is claimed for them.

Variable order: x_1[0..k-1], ..., x_m[0..k-1] -- variable j is bit j, same
convention as boolsys.py, whose primitives this module reuses unchanged.
"""
from __future__ import annotations

import random
import sys
from itertools import permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import boolsys  # noqa: E402
from boolsys import GF2n, fadd, fmul, fsquare, descend, linear_form  # noqa: E402

SUPPORTED_M = (2, 3)


def s3_coeffs_in_X(F: GF2n, a: dict, b: dict, B: int) -> list[dict]:
    """S_3(a, b, X) as [c0, c1, c2] with S_3 = c2 X^2 + c1 X + c0.

    S_3(a,b,X) = (ab + aX + bX)^2 + abX + B
               = (ab)^2 + (a+b)^2 X^2 + (ab) X + B
    (char 2: the cross terms of the square vanish).  X is a genuine polynomial
    variable, so X^2 is not reduced; the Boolean variables inside a and b are.
    """
    ab = fmul(F, a, b)
    c2 = fsquare(F, fadd(a, b))
    c1 = dict(ab)
    c0 = fadd(fsquare(F, ab), {0: B} if B else {})
    return [c0, c1, c2]


def _det(F: GF2n, M: list[list[dict]]) -> dict:
    """Determinant of a square matrix of Boolean-coefficient polynomials.

    Characteristic 2, so every permutation sign is +1 and the Leibniz formula is
    a plain sum of products.  Sizes here are 4x4 (24 terms).
    """
    size = len(M)
    out: dict = {}
    for perm in permutations(range(size)):
        term = {0: 1}
        for i, j in enumerate(perm):
            if not M[i][j]:
                term = {}
                break
            term = fmul(F, term, M[i][j])
        if term:
            out = fadd(out, term)
    return out


def resultant_quadratics(F: GF2n, f: list[dict], g: list[dict]) -> dict:
    """Res_X of two degree-<=2 polynomials in X given as [c0, c1, c2]."""
    a, b, c = f[2], f[1], f[0]
    ap, bp, cp = g[2], g[1], g[0]
    zero: dict = {}
    M = [[a, b, c, zero],
         [zero, a, b, c],
         [ap, bp, cp, zero],
         [zero, ap, bp, cp]]
    return _det(F, M)


def s4(F: GF2n, x1: dict, x2: dict, x3: dict, x4: dict, B: int) -> dict:
    """S_4 = Res_X(S_3(x1,x2,X), S_3(x3,x4,X))."""
    return resultant_quadratics(F, s3_coeffs_in_X(F, x1, x2, B), s3_coeffs_in_X(F, x3, x4, B))


def structure(inst: dict) -> dict:
    eqs = inst["equations"]
    degs = [max((bin(e_m).count("1") for e_m in e), default=-1) for e in eqs]
    n, m, k = inst["n"], inst["m"], inst["k"]
    return {
        "structure": {
            "n_equations": len(eqs),
            "expected_equations": n,
            "n_zero_equations": sum(1 for e in eqs if not e),
            "degree_profile": sorted(degs),
            "max_degree": max(degs),
            "paper_max_degree_bound": m * (m - 1),
            "N": inst["N"],
            "expected_N": m * k,
            "monomials_per_equation": [len(e) for e in eqs],
            "valid": (len(eqs) == n and inst["N"] == m * k and max(degs) <= m * (m - 1)),
        }
    }


def generate(n: int, m: int, k: int, B_mode: str, subspace: str, seed: int, draw: int) -> dict:
    """The eq. (4) system at (n, m, k).  Same curve, same V, same z convention
    and the same seed derivation as boolsys.generate, so the control is matched
    to the chained instance it is compared against."""
    if m not in SUPPORTED_M:
        raise NotImplementedError(
            f"eq. (4) at m={m} needs S_{m+1}; only m in {SUPPORTED_M} is implemented")
    if k <= 0:
        raise ValueError(f"invalid input: k={k}; empty subspace (rejected by design)")
    if k > n:
        raise ValueError(f"invalid input: k={k} > n={n}")
    if B_mode not in ("B_equals_1", "B_random"):
        raise ValueError(B_mode)
    if subspace not in ("low_degree_polynomial", "random_k_dimensional"):
        raise ValueError(subspace)
    modulus, modulus_kind = boolsys.modulus_for(n)
    F = GF2n(n, modulus)
    # identical derivation to the chained instance at t = m, so the control sees
    # the same curve coefficient, the same subspace and the same z
    rng = random.Random(boolsys.derive_seed("EXP-SEMBIN-c2c312", n, m, m, k, B_mode, subspace, seed, draw))
    B = 1 if B_mode == "B_equals_1" else rng.randrange(1, 1 << n)
    basis = [1 << j for j in range(k)] if subspace == "low_degree_polynomial" else boolsys.random_subspace(rng, n, k)
    z = rng.randrange(0, 1 << n)
    N = m * k
    X = [linear_form(basis, i * k) for i in range(m)]
    zc = {0: z} if z else {}
    if m == 2:
        poly = boolsys.s3(F, X[0], X[1], zc, B)
    else:  # m == 3
        poly = s4(F, X[0], X[1], X[2], zc, B)
    equations = descend(poly, n)
    var_names = [f"x{i+1}_{j}" for i in range(m) for j in range(k)]
    assert len(var_names) == N
    inst = {
        "family": "single_S_eq4",
        "n": n, "m": m, "t": m, "k": k, "N": N,
        "B_mode": B_mode, "B": B, "subspace": subspace, "subspace_basis": basis,
        "modulus": modulus, "modulus_kind": modulus_kind, "z": z,
        "seed": seed, "draw": draw,
        "coincides_with_eq5_t2": (m == 2),
        "var_names": var_names,
        "equations": equations,
    }
    inst.update(structure(inst))
    return inst
