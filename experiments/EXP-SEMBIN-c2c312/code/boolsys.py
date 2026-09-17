#!/usr/bin/env python3
"""boolsys.py -- chained-S_3 Boolean systems of Semaev, ePrint 2015/310, eq. (5),
Weil-descended over F_2, plus the control systems EXP-SEMBIN-c2c312 declares.

Construction (KN-LIT-fa346d Sections 3, 4.5, 4.5.1; frozen text at
inputs/SEMAEV-2015-310/paper_fulltext.md):

  * F_{2^n} = F_2[alpha]/(f), f irreducible of degree n.  Conway polynomial where
    it is computable within a few seconds (n <= 24 here); otherwise the
    lexicographically least irreducible trinomial, else pentanomial ("sparse
    f(X)", the paper's own unstarred-n convention is MAGMA's default or a sparse
    f).  The modulus is recorded per instance.
  * Curve Y^2 + XY = X^3 + A X^2 + B; S_3(x1,x2,x3) = (x1x2+x1x3+x2x3)^2 + x1x2x3 + B
    (eq. 14).  A does not enter S_3.  B = 1 or a random nonzero element.
  * V = span_{F_2}(1, alpha, ..., alpha^{k-1}) ("low_degree_polynomial") or a
    random k-dimensional subspace ("random_k_dimensional").
  * System (5) for the chain length t:
        S_3(u_1, x_1, x_2) = 0,
        S_3(u_i, u_{i+1}, x_{i+2}) = 0   (1 <= i <= t-3),
        S_3(u_{t-2}, x_t, z) = 0,
    with x_i in V (k Boolean coordinates each), u_i in F_{2^n} (n Boolean
    coordinates each), and R_X replaced by a random z in F_{2^n} exactly as
    Section 4.5.1 does ("To simplify computations the X-coordinate R_X of a
    random R was substituted by a random element z").  For t = 2 the system is
    the single equation S_3(x_1, x_2, z) = 0.
  * Weil descent: every F_{2^n}-coefficient c of a Boolean monomial contributes
    that monomial to coordinate equation l for each bit l of c.  This gives
    n(t-1) Boolean equations in N = n(t-2) + k t variables; the paper adds the N
    field equations x^2 + x explicitly (Section 4.5.1), which the msolve writer
    does too.

Monomials are squarefree and stored as int bitmasks; variable j is bit j.
Variable order: u_1[0..n-1], ..., u_{t-2}[0..n-1], x_1[0..k-1], ..., x_t[0..k-1].
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "harness" / "macaulay_fp" / "fixtures"))
from gf2_chained_builder import GF2n, _is_irreducible, conway_polynomial_gf2  # noqa: E402

CONWAY_MAX_N = 24


# --------------------------------------------------------------------------
# modulus
# --------------------------------------------------------------------------

def sparse_irreducible(n: int) -> int:
    """Lexicographically least irreducible trinomial x^n + x^a + 1 (smallest a);
    if none exists, the least irreducible pentanomial x^n + x^a + x^b + x^c + 1
    in lexicographic order of (a, b, c)."""
    for a in range(1, n):
        p = (1 << n) | (1 << a) | 1
        if _is_irreducible(p, n):
            return p
    for a in range(1, n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                p = (1 << n) | (1 << a) | (1 << b) | (1 << c) | 1
                if _is_irreducible(p, n):
                    return p
    raise ValueError(f"no sparse irreducible found for n={n}")


def modulus_for(n: int) -> tuple[int, str]:
    if n <= CONWAY_MAX_N:
        return conway_polynomial_gf2(n), "conway"
    return sparse_irreducible(n), "sparse_least_weight"


# --------------------------------------------------------------------------
# polynomials over F_{2^n} in Boolean (squarefree) monomials: dict mask -> coef
# --------------------------------------------------------------------------

def fadd(p: dict, q: dict) -> dict:
    r = dict(p)
    for m, c in q.items():
        v = r.get(m, 0) ^ c
        if v:
            r[m] = v
        else:
            r.pop(m, None)
    return r


def fmul(F: GF2n, p: dict, q: dict) -> dict:
    r: dict = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = m1 | m2
            v = r.get(m, 0) ^ F.mul(c1, c2)
            if v:
                r[m] = v
            else:
                r.pop(m, None)
    return r


def fsquare(F: GF2n, p: dict) -> dict:
    # (sum c_m m)^2 = sum c_m^2 m in characteristic 2 with m^2 = m
    return {m: F.mul(c, c) for m, c in p.items() if F.mul(c, c)}


def s3(F: GF2n, a: dict, b: dict, c: dict, B: int) -> dict:
    ab, ac, bc = fmul(F, a, b), fmul(F, a, c), fmul(F, b, c)
    s = fadd(fadd(ab, ac), bc)
    r = fadd(fsquare(F, s), fmul(F, ab, c))
    return fadd(r, {0: B})


def descend(p: dict, n: int) -> list[list[int]]:
    eqs: list[set] = [set() for _ in range(n)]
    for m, c in p.items():
        for l in range(n):
            if (c >> l) & 1:
                eqs[l].add(m)
    return [sorted(e) for e in eqs]


def linear_form(basis: list[int], var_offset: int) -> dict:
    """sum_j v_j * bit(var_offset + j) as an F_{2^n}-polynomial in Boolean vars."""
    return {1 << (var_offset + j): v for j, v in enumerate(basis) if v}


# --------------------------------------------------------------------------
# instance generation
# --------------------------------------------------------------------------

def derive_seed(*parts) -> int:
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h[:16], 16)


def random_subspace(rng: random.Random, n: int, k: int) -> list[int]:
    """k random F_2-linearly independent elements of F_{2^n} (as ints)."""
    basis: list[int] = []
    reduced: list[int] = []  # echelon form for independence testing
    while len(basis) < k:
        v = rng.randrange(1, 1 << n)
        w = v
        for r in reduced:
            if (w ^ r) < w:
                w ^= r
        if w == 0:
            continue
        basis.append(v)
        # insert w into echelon list (keep sorted descending by top bit)
        reduced.append(w)
        reduced.sort(reverse=True)
        # re-reduce so that the top bits are distinct
        clean: list[int] = []
        for r in reduced:
            for c in clean:
                if (r ^ c) < r:
                    r ^= c
            if r:
                clean.append(r)
        reduced = sorted(clean, reverse=True)
    return basis


def generate(n: int, m: int, t: int, k: int, B_mode: str, subspace: str,
             seed: int, draw: int) -> dict:
    if t < 2:
        raise ValueError(f"invalid input: t={t}; t = 1 has no equation (rejected by design)")
    if k <= 0:
        raise ValueError(f"invalid input: k={k}; empty subspace (rejected by design)")
    if t > m:
        raise ValueError(f"invalid input: t={t} > m={m}")
    if k > n:
        raise ValueError(f"invalid input: k={k} > n={n}")
    if B_mode not in ("B_equals_1", "B_random"):
        raise ValueError(B_mode)
    if subspace not in ("low_degree_polynomial", "random_k_dimensional"):
        raise ValueError(subspace)
    modulus, modulus_kind = modulus_for(n)
    F = GF2n(n, modulus)
    rng = random.Random(derive_seed("EXP-SEMBIN-c2c312", n, m, t, k, B_mode, subspace, seed, draw))
    B = 1 if B_mode == "B_equals_1" else rng.randrange(1, 1 << n)
    if subspace == "low_degree_polynomial":
        basis = [1 << j for j in range(k)]
    else:
        basis = random_subspace(rng, n, k)
    z = rng.randrange(0, 1 << n)
    N = n * (t - 2) + k * t
    # variable layout
    u_off = [i * n for i in range(t - 2)]
    x_off = [n * (t - 2) + i * k for i in range(t)]
    alpha_basis = [1 << j for j in range(n)]
    U = [linear_form(alpha_basis, o) for o in u_off]
    X = [linear_form(basis, o) for o in x_off]
    zc = {0: z} if z else {}
    field_eqs = []
    if t == 2:
        field_eqs.append(s3(F, X[0], X[1], zc, B))
    else:
        field_eqs.append(s3(F, U[0], X[0], X[1], B))
        for i in range(t - 3):
            field_eqs.append(s3(F, U[i], U[i + 1], X[i + 2], B))
        field_eqs.append(s3(F, U[t - 3], X[t - 1], zc, B))
    equations: list[list[int]] = []
    for p in field_eqs:
        equations.extend(descend(p, n))
    var_names = []
    for i in range(t - 2):
        var_names += [f"u{i+1}_{j}" for j in range(n)]
    for i in range(t):
        var_names += [f"x{i+1}_{j}" for j in range(k)]
    assert len(var_names) == N
    inst = {
        "family": "chained_S3_eq5",
        "n": n, "m": m, "t": t, "k": k, "N": N,
        "B_mode": B_mode, "B": B, "subspace": subspace, "subspace_basis": basis,
        "modulus": modulus, "modulus_kind": modulus_kind, "z": z,
        "seed": seed, "draw": draw,
        "var_names": var_names,
        "equations": equations,
    }
    inst.update(structure(inst))
    return inst


def structure(inst: dict) -> dict:
    eqs = inst["equations"]
    degs = [max((bin(mm).count("1") for mm in e), default=-1) for e in eqs]
    n, t, k = inst["n"], inst["t"], inst["k"]
    expected_eqs = n * (t - 1)
    expected_N = n * (t - 2) + k * t
    expected_deg = 3 if t >= 3 else 2
    return {
        "structure": {
            "n_equations": len(eqs),
            "expected_equations": expected_eqs,
            "n_zero_equations": sum(1 for e in eqs if not e),
            "degree_profile": sorted(degs),
            "max_degree": max(degs),
            "expected_max_degree": expected_deg,
            "N": inst["N"],
            "expected_N": expected_N,
            "monomials_per_equation": [len(e) for e in eqs],
            "valid": (len(eqs) == expected_eqs and inst["N"] == expected_N and max(degs) == expected_deg),
        }
    }


# --------------------------------------------------------------------------
# controls
# --------------------------------------------------------------------------

def matched_null(inst: dict, seed: int) -> dict:
    """Random dense Boolean system of matched shape: same N, same number of
    equations, and per equation the same number of monomials of each degree,
    with the monomials drawn uniformly (the T11-style null of GOAL-DREG-001)."""
    rng = random.Random(derive_seed("matched_null", inst["seed"], inst["draw"], seed))
    N = inst["N"]
    eqs = []
    for e in inst["equations"]:
        by_deg: dict[int, int] = {}
        for mm in e:
            d = bin(mm).count("1")
            by_deg[d] = by_deg.get(d, 0) + 1
        out = set()
        for d, cnt in by_deg.items():
            while sum(1 for mm in out if bin(mm).count("1") == d) < cnt:
                vs = rng.sample(range(N), d)
                mm = 0
                for v in vs:
                    mm |= 1 << v
                out.add(mm)
        eqs.append(sorted(out))
    return {"family": "matched_null", "N": N, "var_names": inst["var_names"],
            "equations": eqs, "n": inst["n"], "m": inst["m"], "t": inst["t"], "k": inst["k"],
            "seed": inst["seed"], "draw": inst["draw"], "null_seed": seed,
            "source_sha256": None}


def known_false(N: int, n_quadratics: int, seed: int) -> dict:
    """Planted degree-2 solution: a random point p, all N linear polynomials
    x_i + p_i, and n_quadratics random quadratics adjusted to vanish at p.  The
    ideal is the maximal ideal of p; a Groebner basis is reached at degree 2 (the
    quadratics are the highest-degree generators and reduce to zero by the linear
    forms at the degree-2 step)."""
    rng = random.Random(derive_seed("known_false", N, n_quadratics, seed))
    p = [rng.randrange(2) for _ in range(N)]
    eqs = []
    for i in range(N):
        e = {1 << i}
        if p[i]:
            e.add(0)
        eqs.append(sorted(e))
    for _ in range(n_quadratics):
        terms = set()
        for _ in range(6):
            a, b = rng.sample(range(N), 2)
            terms ^= {(1 << a) | (1 << b)}
        for _ in range(3):
            terms ^= {1 << rng.randrange(N)}
        # evaluate at p and fix the constant
        val = 0
        for mm in terms:
            if all(p[j] for j in range(N) if (mm >> j) & 1):
                val ^= 1
        if val:
            terms ^= {0}
        eqs.append(sorted(terms))
    return {"family": "known_false_planted_point", "N": N,
            "var_names": [f"v{i}" for i in range(N)], "equations": eqs,
            "planted_point": p, "seed": seed}


# --------------------------------------------------------------------------
# serialization
# --------------------------------------------------------------------------

def canonical_bytes(system: dict) -> bytes:
    """The bytes handed to both instruments: N, variable names, and the ordered
    list of equations, each an ascending list of monomial masks."""
    payload = {"N": system["N"], "var_names": system["var_names"],
               "equations": [sorted(e) for e in system["equations"]]}
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def sha256_of(system: dict) -> str:
    return hashlib.sha256(canonical_bytes(system)).hexdigest()


def mono_str(mask: int, names: list[str]) -> str:
    if mask == 0:
        return "1"
    return "*".join(names[j] for j in range(mask.bit_length()) if (mask >> j) & 1)


def write_msolve(system: dict, path: Path, field_equations: bool = True) -> str:
    """msolve input: variable line, characteristic 2, comma-separated polynomials.
    Returns sha256 of the written file."""
    names = system["var_names"]
    polys = []
    for e in system["equations"]:
        if not e:
            continue
        polys.append("+".join(mono_str(mm, names) for mm in e))
    if field_equations:
        for v in names:
            polys.append(f"{v}^2+{v}")
    if not polys:
        polys.append("0")
    text = ",".join(names) + "\n2\n" + ",\n".join(polys) + "\n"
    path.write_text(text)
    return hashlib.sha256(text.encode()).hexdigest()
