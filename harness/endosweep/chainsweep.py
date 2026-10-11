"""Chain sweep: every isogeny-chain realisation of the cheap endomorphisms of one curve.

``sweep.py`` prices an endomorphism as the sum of its prime-degree isogeny
steps and ranks elements; ``explicit.py`` builds one element on the curve.
This module does the whole family for one curve with complex multiplication
and turns it into a frozen input for a native measurement:

1. **catalogue** -- every primitive non-scalar element ``a + b*omega`` of the
   maximal order whose norm is at most ``nmax`` and has no prime factor above
   ``lmax``, one representative per {units} x {conjugation} orbit, with the
   prime-degree steps of its chain;
2. **orders** -- every distinct ordering of those steps.  All orderings give
   the same endomorphism (``E[(alpha)]`` factors through the prime ideals in
   any order) but walk through different curves, so they have different
   constants and, once the first step is specialised to an affine input,
   different costs;
3. **build** -- each (element, ordering) is constructed on the curve by
   ``explicit.build_chain_endomorphism`` with omega's eigenvalue pinned and
   the element itself (not its conjugate) required, and verified on points,
   including a GLV-2 reconstruction;
4. **cost** -- an operation count that mirrors, statement by statement, the
   chain evaluators of the crypto repository's CryptoPro-B module
   (``generic``: projective Horner with powers of ``Z`` at every step, the
   evaluator measured in aburan28/crypto#1408; ``optimised``: Jacobian
   coordinates, Horner that skips the monic leading coefficients, the first
   step specialised to the affine input ``Z = 1``, and the isomorphism back
   to ``E`` as one multiplication of ``Z``), and the same for the scalar
   multiplications around it;
5. **completeness** -- a lower bound on the cost of any chain outside the
   catalogue's bounds, so that the catalogue provably contains every chain
   within a stated factor of the cheapest;
6. **export** -- the rational-map constants (Kohel form ``N``, ``psi``, ``M``
   per step), GLV basis and test vectors of every ordering within that
   factor, as one JSON file for the native measurement.

Nothing here is a timing.  The chain op counts are exact for the evaluators
they mirror (they count what that code does); the scalar-multiplication
counts are expectations over random scalars, simulated with the same wNAF
recoding and the real lattice bases.  The native benchmark measures all of
them independently with a counting build.

    python -m harness.endosweep.chainsweep --out-dir research/endosweep_chainsweep_20261006
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import random
import statistics
import time
from math import gcd
from dataclasses import asdict, dataclass, field

from sympy import factorint, isprime

from . import explicit as EX
from . import lattice as LA
from . import quadorder as QO
from .targets import deployed_targets, verify
from .toyverify import Curve

FORMAT = "endosweep-chainsweep/1"
GENERATOR = "harness/endosweep/chainsweep.py"
VARIANTS = ("generic", "optimised")

# Fermat inversion a^(p-2) in the crypto repository's CryptoPro-B field: one
# squaring per bit of p - 2 (256) and one multiplication per set bit (8).
INV_OPS = (8, 256)


# ---------------------------------------------------------------------------
# operation counts that mirror crypto: src/ecc/cryptopro_b_point.rs
# ---------------------------------------------------------------------------

def step_ops(ell: int, variant: str, first: bool) -> tuple[int, int]:
    """(multiplications, squarings) of one ell-step of a chain evaluator.

    ``generic`` (``PreparedChain::apply`` of crypto#1408): projective P^2
    coordinates; powers ``Z^2 .. Z^(3s)`` (3s-1 M), homogeneous Horner
    ``acc*X + c_i*Z^(d-i)`` for psi, N, M of degrees s, ell, 3s (2 M per
    degree), ``psi^3 = psi^2*psi`` (1S + 1M), and ``X' = N*psi, Y' = Y*M,
    Z' = Z*psi^3`` (3 M).  The first step is not specialised.

    ``optimised``: Jacobian coordinates ``x = X/Z^2, y = Y/Z^3``.  With the
    polynomials homogenised in ``(X, Z^2)`` a step is ``X' = N, Y' = Y*M,
    Z' = Z*psi`` (no ``psi^3``, no ``N*psi``): one squaring ``Z^2``, its powers
    up to ``(Z^2)^(3s)`` (3s-1 M), Horner that starts from ``X + c_(d-1)*Z^2``
    because psi, N and M are monic (2d-1 M each), and 2 M for the outputs.
    The first step has an affine input (``Z = 1``): plain monic Horner
    (s-1, ell-1, 3s-1 M), ``X' = N, Z' = psi`` free, ``Y' = y*M`` (1 M).
    """
    if ell < 3 or ell % 2 == 0:
        raise ValueError("odd prime steps only")
    s = (ell - 1) // 2
    if variant == "generic":
        return (3 * s - 1) + 2 * s + 2 * ell + 6 * s + 1 + 3, 1
    if variant == "optimised":
        if first:
            return (s - 1) + (ell - 1) + (3 * s - 1) + 1, 0
        return (3 * s - 1) + (2 * s - 1) + (2 * ell - 1) + (6 * s - 1) + 2, 1
    raise ValueError(f"unknown variant {variant!r}")


def tail_ops(variant: str) -> tuple[int, int]:
    """After the last step: the isomorphism back to E and the Jacobian output.

    ``generic``: ``X*u^2, Y*u^3`` (2 M), then projective to Jacobian
    ``(X*Z, Y*Z^2, Z)`` (1S + 2M).
    ``optimised``: the output is already Jacobian, and ``(u^2 X, u^3 Y, Z)`` is
    the same point as ``(X, Y, Z/u)``, so the isomorphism is one
    multiplication by the precomputed ``u^-1``.
    """
    if variant == "generic":
        return 4, 1
    if variant == "optimised":
        return 1, 0
    raise ValueError(f"unknown variant {variant!r}")


def chain_ops(order: list[int] | tuple[int, ...], variant: str) -> dict:
    M = S = 0
    for i, ell in enumerate(order):
        m, s = step_ops(ell, variant, i == 0)
        M += m
        S += s
    m, s = tail_ops(variant)
    M += m
    S += s
    return {"M": M, "S": S, "I": 0, "M_eq": M + S}


def m_eq(c: dict) -> float:
    """Multiplication-equivalents: a squaring is a multiplication in this field
    (``mont_sqr`` is ``mont_mul``), and an inversion is counted through its
    own squarings and multiplications (already inside M and S)."""
    return c["M"] + c["S"]


DBL = (3, 5)          # dbl-2001-b
ADD = (11, 5)         # add-2007-bl
MADD = (7, 4)         # madd-2007-bl


def wnaf_digits(k: int, w: int) -> list[int]:
    """Least-significant first; the same recoding as ``wnaf_digits`` in Rust."""
    if not 2 <= w <= 7:
        raise ValueError("w in 2..=7")
    digits = []
    mod, half = 1 << w, 1 << (w - 1)
    while k:
        if k & 1:
            m = k & (mod - 1)
            d = m - mod if m >= half else m
            k -= d
        else:
            d = 0
        digits.append(d)
        k >>= 1
    return digits


def _batch_affine_ops(n: int) -> tuple[int, int]:
    # prefix products n M; inversion; back-substitution 2(n-1) M; 3M + 1S per point
    return n + INV_OPS[0] + 2 * (n - 1) + 3 * n, INV_OPS[1] + n


def _table_ops(w: int) -> tuple[int, int]:
    count = 1 << (w - 2)
    if count == 1:
        return 0, 0
    return DBL[0] + (count - 1) * ADD[0], DBL[1] + (count - 1) * ADD[1]


def baseline_ops(k: int, w: int, table: str) -> dict:
    """``scalar_mul_wnaf`` (affine table) or its Jacobian-table twin, for one scalar."""
    d = wnaf_digits(k, w)
    nz = sum(1 for x in d if x)
    M, S = _table_ops(w)
    if table == "affine":
        bm, bs = _batch_affine_ops(1 << (w - 2))
        M, S = M + bm, S + bs
        add = MADD
    elif table == "jacobian":
        add = ADD
    else:
        raise ValueError(table)
    # the top digit is non-zero and lands on the identity for free
    M += (len(d) - 1) * DBL[0] + (nz - 1) * add[0]
    S += (len(d) - 1) * DBL[1] + (nz - 1) * add[1]
    return {"M": M, "S": S, "I": 1 if table == "affine" else 0}


def glv_ops(k1: int, k2: int, w: int, table: str, chain: dict) -> dict:
    """``scalar_mul_glv`` (affine tables) or its Jacobian-table twin, with the
    chain's own count for phi(P); the decomposition has no field operations."""
    d1, d2 = wnaf_digits(abs(k1), w), wnaf_digits(abs(k2), w)
    L = max(len(d1), len(d2))
    nz = sum(1 for x in d1 if x) + sum(1 for x in d2 if x)
    # additions that land on the identity: the first non-zero digit at the
    # top position (the top of the longer expansion is always non-zero)
    top_free = 1
    tm, ts = _table_ops(w)
    M, S = 2 * tm + chain["M"], 2 * ts + chain["S"]
    if table == "affine":
        bm, bs = _batch_affine_ops(2 * (1 << (w - 2)))
        M, S = M + bm, S + bs
        add = MADD
    elif table == "jacobian":
        add = ADD
    else:
        raise ValueError(table)
    M += (L - 1) * DBL[0] + (nz - top_free) * add[0]
    S += (L - 1) * DBL[1] + (nz - top_free) * add[1]
    return {"M": M, "S": S, "I": 1 if table == "affine" else 0}


# ---------------------------------------------------------------------------
# catalogue
# ---------------------------------------------------------------------------

def class_number(D: int) -> int:
    """Number of reduced primitive forms (a, b, c) of discriminant D < 0."""
    h = 0
    a = 1
    while 3 * a * a <= -D:
        for b in range(-a + 1, a + 1):
            if (b * b - D) % (4 * a):
                continue
            c = (b * b - D) // (4 * a)
            if c < a or (c == a and b < 0):
                continue
            if gcd(gcd(a, abs(b)), c) == 1:
                h += 1
        a += 1
    return h


def split_or_ramified(D: int, ell: int) -> bool:
    return isprime(ell) and QO.kronecker_symbol_disc(D, ell) != -1


def catalogue(D: int, nmax: int, lmax: int) -> list[dict]:
    """Every primitive non-scalar element with norm <= nmax and all prime
    factors <= lmax, one per {units} x {conjugation} orbit (exact search)."""
    out = []
    for N in range(2, nmax + 1):
        fac = factorint(N)
        if max(fac) > lmax:
            continue
        for el in QO.elements_of_norm(D, N):
            steps = []
            for ell in sorted(fac):
                steps += [ell] * fac[ell]
            out.append({"a": el.a, "b": el.b, "norm": N, "steps": steps})
    return out


def distinct_orders(steps: list[int]) -> list[tuple[int, ...]]:
    return sorted(set(itertools.permutations(steps)))


def best_order(steps: list[int], variant: str) -> tuple[tuple[int, ...], dict]:
    orders = distinct_orders(steps)
    costs = {o: chain_ops(o, variant) for o in orders}
    o = min(orders, key=lambda x: (costs[x]["M_eq"], x))
    return o, costs[o]


def outside_lower_bound(D: int, nmax: int, lmax: int, variant: str) -> dict:
    """Least cost of any chain that is NOT in ``catalogue(D, nmax, lmax)``.

    A primitive element's norm is a product of split primes and at most one
    ramified prime (an inert prime would divide the element).  Outside the
    catalogue an element either (i) has a step of degree ``ell > lmax`` or
    (ii) has all steps ``<= lmax`` and norm ``> nmax``.  Every step costs at
    least as much as it would in the cheapest position, so (i) costs at least
    the cheapest-position cost of the smallest admissible ``ell > lmax`` plus
    the tail; (ii) is bounded by the cheapest multiset of admissible primes
    ``<= lmax`` with product ``> nmax``, found by exhaustive search (the
    search ranges over all multisets, realised as norms or not, so it is a
    lower bound).
    """
    ell = lmax + 1
    while not split_or_ramified(D, ell):
        ell += 1
    first = step_ops(ell, variant, True)
    later = step_ops(ell, variant, False)
    tail = tail_ops(variant)
    bound_i = min(sum(first), sum(later)) + sum(tail)
    primes = [q for q in range(3, lmax + 1) if split_or_ramified(D, q)]
    best = [None]

    def cost(ms):
        return chain_ops(best_order(list(ms), variant)[0], variant)["M_eq"]

    def dfs(start, ms, prod):
        if ms:
            c_lower = cost(ms)      # adding steps never lowers the cost
            if best[0] is not None and c_lower >= best[0][0]:
                return
            if prod > nmax:
                best[0] = (c_lower, list(ms))
                return
        for i in range(start, len(primes)):
            dfs(i, ms + [primes[i]], prod * primes[i])

    dfs(0, [], 1)
    bound_ii, witness = best[0]
    return {"variant": variant, "large_step": {"ell": ell, "bound": bound_i},
            "large_norm": {"bound": bound_ii, "cheapest_multiset": witness},
            "bound": min(bound_i, bound_ii)}


# ---------------------------------------------------------------------------
# rational maps of one step (Kohel form), from the kernel polynomial
# ---------------------------------------------------------------------------

def _pderiv(f, p):
    return EX._trim([(i * c) % p for i, c in enumerate(f)][1:]) if len(f) > 1 else [0]


def rational_map_polys(E: Curve, h: list[int], ell: int):
    """(N, psi, M) with x' = N/psi^2 and y' = y*M/psi^3, computed from h by traces.

    Same construction as research/endosweep_20261005/export_chain_constants.py
    (which produced the frozen inputs of aburan28/crypto#1408), checked here
    against the trace evaluation of ``explicit.KernelIsogeny`` at random
    points, and N, psi, M are asserted monic.
    """
    p, a, b = E.p, E.a, E.b
    s = len(h) - 1
    iso = EX.KernelIsogeny(E, h, ell)
    ps = iso.ps

    def trace(f):
        f = EX.pmod(f, h, p)
        return sum(c * ps[k] for k, c in enumerate(f)) % p

    Q = []
    for k in range(s):
        Qk = [0] * (s - k)
        for j in range(k + 1, s + 1):
            Qk[j - 1 - k] = h[j] % p
        Q.append(EX._trim(Qk))
    vT = EX._trim([2 * a % p, 0, 6 % p])
    uT = EX._trim([4 * b % p, 4 * a % p, 0, 4 % p])
    V = EX._trim([trace(EX.pmul(vT, Q[k], p)) for k in range(s)]) if s else [0]
    R = [[0] for _ in range(2 * s - 1)] if s else [[0]]
    for i in range(s):
        for j in range(s):
            R[i + j] = EX.padd(R[i + j], EX.pmul(Q[i], Q[j], p), p)
    U = EX._trim([trace(EX.pmul(uT, R[k], p)) for k in range(2 * s - 1)]) if s else [0]
    psi2 = EX.pmul(h, h, p)
    N = EX.padd(EX.padd(EX.pmul([0, 1], psi2, p), EX.pmul(V, h, p), p), U, p)
    M = EX.psub(EX.pmul(_pderiv(N, p), h, p), EX.pscale(EX.pmul(N, _pderiv(h, p), p), 2, p), p)
    if len(N) - 1 != ell or len(h) - 1 != s or len(M) - 1 != 3 * s:
        raise AssertionError("unexpected degrees of the rational-map polynomials")
    if (N[-1], h[-1], M[-1]) != (1, 1, 1):
        raise AssertionError("N, psi and M are expected to be monic")
    rng = random.Random(1)
    for _ in range(3):
        P = E.point(rng.randrange(1 << 30))
        img = iso(P)
        x0, y0 = P
        den = pow(sum(c * pow(x0, i, p) for i, c in enumerate(h)) % p, -1, p)
        Xn = sum(c * pow(x0, i, p) for i, c in enumerate(N)) * den * den % p
        Yn = y0 * sum(c * pow(x0, i, p) for i, c in enumerate(M)) % p * pow(den, 3, p) % p
        if img != (Xn, Yn):
            raise AssertionError("rational-map polynomials disagree with the trace evaluation")
    return N, h, M


# ---------------------------------------------------------------------------
# build, verify, export
# ---------------------------------------------------------------------------

@dataclass
class ChainRow:
    element: list[int]
    norm: int
    order: list[int]
    found: bool = False
    matched_element: list[int] | None = None
    eigenvalue: str | None = None
    babai_bound_bits: int | None = None
    max_coeff_bits_checked: int | None = None
    ops: dict = field(default_factory=dict)
    build_seconds: float = 0.0
    exported: bool = False
    note: str = ""


def _target(name: str):
    T = next(t for t in deployed_targets() if t.name.lower() == name.lower())
    verify(T)
    if not T.verified:
        raise RuntimeError(f"{name}: {T.verification}")
    D = QO.small_discriminant_scan(QO.frobenius_discriminant(T.q, T.trace), 2_000_000).found
    if D is None:
        raise RuntimeError(f"{name} has no small CM discriminant")
    return T, D


def export_chain(T, D: int, res: EX.ChainResult, omega_root: int, *, vectors: int, seed: int) -> dict:
    """The native-measurement record of one built chain (all values re-checked)."""
    p, a, b, n, h = T.p, T.coeffs["a"] % T.p, T.coeffs["b"] % T.p, T.n, T.h
    E = Curve(p, a, b)
    steps, maps, cur = [], [], E
    for ell, hpoly in zip(res.steps, res.kernel_polys):
        N, psi, M = rational_map_polys(cur, hpoly, ell)
        iso = EX.KernelIsogeny(cur, hpoly, ell)
        steps.append({
            "ell": ell,
            "domain": {"a": hex(cur.a), "b": hex(cur.b)},
            "codomain": {"a": hex(iso.codomain.a), "b": hex(iso.codomain.b)},
            "psi": [hex(c) for c in psi],
            "N": [hex(c) for c in N],
            "M": [hex(c) for c in M],
        })
        maps.append(iso)
        cur = iso.codomain
    if cur.j() != E.j():
        raise AssertionError("the chain does not return to j(E)")
    u = res.isomorphism_u
    u2, u3 = u * u % p, pow(u, 3, p)
    if (pow(u, 4, p) * cur.a - a) % p or (pow(u, 6, p) * cur.b - b) % p:
        raise AssertionError("iso_u does not map the last codomain to E")

    def phi(P):
        for m in maps:
            P = m(P)
        return (u2 * P[0] % p, u3 * P[1] % p)

    lam = res.eigenvalue
    red = LA.reduce([1, lam], n)
    rng = random.Random(seed)
    tvs = []
    for i in range(vectors):
        Q = EX.point_of_order(E, n, h, 100 + 37 * i + seed % 1000)
        img = phi(Q)
        if E.mul(lam, Q) != img:
            raise AssertionError("phi(P) != lambda*P on a test vector")
        k = rng.randrange(1, n)
        k1, k2 = red.decompose(k)
        kQ = E.mul(k, Q)
        if E.add(E.mul(k1, Q), E.mul(k2, img)) != kQ:
            raise AssertionError("GLV reconstruction failed on a test vector")
        tvs.append({"P": [hex(Q[0]), hex(Q[1])], "phiP": [hex(img[0]), hex(img[1])],
                    "k": hex(k), "k1": str(k1), "k2": str(k2), "kP": [hex(kQ[0]), hex(kQ[1])]})
    ea, eb = res.element
    return {
        "id": f"{ea}{'+' if eb >= 0 else '-'}{abs(eb)}w/{'.'.join(map(str, res.steps))}",
        "element": [ea, eb],
        "matched_element": list(res.matched_element),
        "norm": res.degree,
        "order": list(res.steps),
        "eigenvalue": hex(lam),
        "glv_basis": [[str(x) for x in row] for row in red.basis],
        "babai_bound_bits": red.babai_bound.bit_length(),
        "model_ops": {v: chain_ops(res.steps, v) for v in VARIANTS},
        "steps": steps,
        "isomorphism_u": hex(u),
        "test_vectors": tvs,
    }


def run(target: str = "GOST CryptoPro-B", *, nmax: int = 20000, lmax: int = 61,
        export_factor: float = 2.0, vectors: int = 2, seed: int = 20261006,
        progress=None) -> dict:
    T, D = _target(target)
    p, a, b, n, h = T.p, T.coeffs["a"] % T.p, T.coeffs["b"] % T.p, T.n, T.h
    roots = QO.omega_eigenvalues(D, n)
    omega_root = roots[0]
    cat = catalogue(D, nmax, lmax)
    rows: list[ChainRow] = []
    built: dict[tuple, EX.ChainResult] = {}
    for el in cat:
        for order in distinct_orders(el["steps"]):
            t0 = time.time()
            row = ChainRow([el["a"], el["b"]], el["norm"], list(order))
            try:
                res = EX.build_chain_endomorphism(p, a, b, n, h, D, (el["a"], el["b"]),
                                                  curve_name=T.name, steps=list(order),
                                                  conjugates=False, omega_root=omega_root)
            except Exception as exc:          # recorded, never silently dropped
                row.note = f"build raised {type(exc).__name__}: {exc}"
                res = None
            row.build_seconds = round(time.time() - t0, 3)
            row.ops = {v: chain_ops(order, v) for v in VARIANTS}
            if res is not None:
                row.found = res.found
                row.note = row.note or res.note
                if res.found:
                    row.matched_element = list(res.matched_element)
                    row.eigenvalue = hex(res.eigenvalue)
                    row.babai_bound_bits = res.glv_check["babai_bound_bits"]
                    row.max_coeff_bits_checked = res.glv_check["max_coeff_bits"]
                    built[(el["a"], el["b"], order)] = res
            rows.append(row)
            if progress:
                progress(row)
    # consistency: every ordering of one element acts as the same scalar up to sign
    eig: dict[tuple, set] = {}
    for r in rows:
        if r.found:
            lam = int(r.eigenvalue, 16)
            eig.setdefault(tuple(r.element), set()).add(min(lam, n - lam))
    consistent = all(len(v) == 1 for v in eig.values())
    best = min(r.ops["optimised"]["M_eq"] for r in rows if r.found)
    limit = export_factor * best
    chains = []
    for r in rows:
        if r.found and r.ops["optimised"]["M_eq"] <= limit:
            res = built[(r.element[0], r.element[1], tuple(r.order))]
            chains.append(export_chain(T, D, res, omega_root, vectors=vectors,
                                       seed=seed + len(chains)))
            r.exported = True
    bounds = {v: outside_lower_bound(D, nmax, lmax, v) for v in VARIANTS}
    return {
        "format": FORMAT,
        "generator": GENERATOR,
        "target": T.name,
        "p": hex(p), "a": hex(a), "b": hex(b), "n": hex(n), "cofactor": h,
        "D_K": D, "class_number": class_number(D),
        "omega_root": hex(omega_root),
        "omega_root_note": "omega = (1 + sqrt(D))/2 acts on the order-n subgroup as this root of "
                           "x^2 - x + (1 - D)/4 mod n; every element is matched relative to it",
        "bounds": {"nmax": nmax, "lmax": lmax, "export_factor": export_factor,
                   "best_optimised_M_eq": best, "export_limit_M_eq": limit,
                   "outside_lower_bound": bounds},
        "eigenvalues_consistent_across_orders": consistent,
        "rows": [asdict(r) for r in rows],
        "chains": chains,
    }


# ---------------------------------------------------------------------------
# expected totals of the native arms (the measurement's preregistered model)
# ---------------------------------------------------------------------------

def scalar_mult_model(result: dict, *, widths=(3, 4, 5, 6, 7), samples: int = 400,
                      seed: int = 7) -> dict:
    """Expected field-operation counts of every native arm, by simulation.

    The same seeded random scalars are recoded exactly as the Rust code does;
    GLV halves come from Babai rounding against each chain's real basis.
    Returned per configuration: mean M, S, I and M-equivalents.
    """
    n = int(result["n"], 16)
    rng = random.Random(seed)
    ks = [rng.randrange(1, n) for _ in range(samples)]
    out = {"samples": samples, "seed": seed, "baseline": {}, "glv": {}}
    for table in ("affine", "jacobian"):
        for w in widths:
            cs = [baseline_ops(k, w, table) for k in ks]
            out["baseline"][f"{table}/w{w}"] = _mean_ops(cs)
    for ch in result["chains"]:
        red = LA.reduce([1, int(ch["eigenvalue"], 16)], n)
        halves = [red.decompose(k) for k in ks]
        per = {}
        for variant in VARIANTS:
            cops = ch["model_ops"][variant]
            for table in ("affine", "jacobian"):
                for w in widths:
                    cs = [glv_ops(k1, k2, w, table, cops) for k1, k2 in halves]
                    per[f"{variant}/{table}/w{w}"] = _mean_ops(cs)
        out["glv"][ch["id"]] = per
    return out


def _mean_ops(cs: list[dict]) -> dict:
    M = statistics.fmean(c["M"] for c in cs)
    S = statistics.fmean(c["S"] for c in cs)
    I = statistics.fmean(c["I"] for c in cs)
    return {"M": round(M, 2), "S": round(S, 2), "I": round(I, 3), "M_eq": round(M + S, 2)}


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

def _id(r: dict) -> str:
    a, b = r["element"]
    return f"{a} {'+' if b >= 0 else '-'} {abs(b)}ω"


def markdown(result: dict, model: dict) -> str:
    rows = result["rows"]
    B = result["bounds"]
    L = []
    L.append(f"# Chain sweep: {result['target']}, D_K = {result['D_K']}")
    L.append("")
    L.append("Generated by `harness/endosweep/chainsweep.py`; every number is recomputed by that "
             "module and every chain was built on the curve and verified on points.  Counts are "
             "field multiplications (M) and squarings (S) of the crypto repository's CryptoPro-B "
             "evaluators; `M_eq = M + S` because a squaring is a multiplication in that field.  "
             "No timing is produced here.")
    L.append("")
    L.append("## Catalogue and completeness")
    L.append("")
    nel = len({tuple(r['element']) for r in rows})
    L.append(f"- Elements: every primitive non-scalar `a + bω` with norm ≤ {B['nmax']} and every prime "
             f"factor ≤ {B['lmax']}, one per {{±1}} × {{conjugation}} orbit: **{nel}** elements, "
             f"**{len(rows)}** step orderings.")
    nf = sum(1 for r in rows if r["found"])
    L.append(f"- Built and verified on points (closed walk, eigenvalue, GLV-2 reconstruction): "
             f"**{nf} of {len(rows)}**.")
    L.append(f"- Every ordering of one element acts as the same scalar up to sign: "
             f"**{'yes' if result['eigenvalues_consistent_across_orders'] else 'NO'}**.")
    L.append(f"- Cheapest chain (optimised evaluator): **{B['best_optimised_M_eq']} M_eq**.  Exported for "
             f"the native measurement: every ordering within {B['export_factor']}× of it "
             f"(≤ {B['export_limit_M_eq']:.0f} M_eq): **{len(result['chains'])}** orderings.")
    for v in VARIANTS:
        ob = B["outside_lower_bound"][v]
        L.append(f"- Completeness, `{v}` evaluator: any chain outside the bounds costs at least "
                 f"**{ob['bound']} M_eq** (a step of degree ≥ {ob['large_step']['ell']}: "
                 f"≥ {ob['large_step']['bound']}; norm > {B['nmax']} with small steps: "
                 f"≥ {ob['large_norm']['bound']}, cheapest multiset "
                 f"{'·'.join(map(str, ob['large_norm']['cheapest_multiset']))}).")
    L.append("")
    L.append("## Every element, at its cheapest ordering")
    L.append("")
    L.append("| element | norm | steps | orderings | cheapest ordering (optimised) | optimised M_eq | "
             "generic M_eq | Babai bound bits | verified orderings | exported |")
    L.append("|:--|--:|:--|--:|:--|--:|--:|--:|--:|--:|")
    by_el: dict[tuple, list] = {}
    for r in rows:
        by_el.setdefault(tuple(r["element"]), []).append(r)
    ordered = sorted(by_el.items(), key=lambda kv: min(r["ops"]["optimised"]["M_eq"] for r in kv[1]))
    for el, rs in ordered:
        best_r = min(rs, key=lambda r: (r["ops"]["optimised"]["M_eq"], r["order"]))
        gen = min(r["ops"]["generic"]["M_eq"] for r in rs)
        bits = {r["babai_bound_bits"] for r in rs if r["babai_bound_bits"]}
        L.append(f"| {_id(rs[0])} | {rs[0]['norm']} | {'·'.join(map(str, sorted(rs[0]['order'])))} | "
                 f"{len(rs)} | {'·'.join(map(str, best_r['order']))} | {best_r['ops']['optimised']['M_eq']} | "
                 f"{gen} | {','.join(map(str, sorted(bits))) or '—'} | "
                 f"{sum(1 for r in rs if r['found'])}/{len(rs)} | {sum(1 for r in rs if r['exported'])} |")
    L.append("")
    L.append("## The exported orderings (native-measurement set)")
    L.append("")
    L.append("| chain | element | order | generic M | generic S | optimised M | optimised S | optimised M_eq | "
             "Babai bound bits |")
    L.append("|:--|:--|:--|--:|--:|--:|--:|--:|--:|")
    for ch in sorted(result["chains"], key=lambda c: (c["model_ops"]["optimised"]["M_eq"], c["id"])):
        g, o = ch["model_ops"]["generic"], ch["model_ops"]["optimised"]
        L.append(f"| `{ch['id']}` | {_id(ch)} | {'·'.join(map(str, ch['order']))} | {g['M']} | {g['S']} | "
                 f"{o['M']} | {o['S']} | {o['M_eq']} | {ch['babai_bound_bits']} |")
    L.append("")
    L.append("## Expected totals of the native arms (model, not a measurement)")
    L.append("")
    L.append(f"Mean over {model['samples']} seeded random scalars, recoded exactly as the Rust code does; "
             "GLV halves from Babai rounding against each chain's own basis.  M_eq per scalar "
             "multiplication; the decomposition (big-integer, no field operations) is not included.")
    L.append("")
    base = model["baseline"]
    best_base_key = min(base, key=lambda k: base[k]["M_eq"])
    L.append("| arm | M_eq | ratio best-baseline / arm |")
    L.append("|:--|--:|--:|")
    for key in sorted(base, key=lambda k: base[k]["M_eq"]):
        L.append(f"| baseline {key} | {base[key]['M_eq']:.0f} | {base[best_base_key]['M_eq'] / base[key]['M_eq']:.3f} |")
    best_chain = min(result["chains"], key=lambda c: (c["model_ops"]["optimised"]["M_eq"], c["id"]))
    per = model["glv"][best_chain["id"]]
    for key in sorted(per, key=lambda k: per[k]["M_eq"]):
        L.append(f"| GLV `{best_chain['id']}` {key} | {per[key]['M_eq']:.0f} | "
                 f"{base[best_base_key]['M_eq'] / per[key]['M_eq']:.3f} |")
    L.append("")
    return "\n".join(L) + "\n"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="every chain realisation of the cheap endomorphisms of a curve")
    ap.add_argument("--target", default="GOST CryptoPro-B")
    ap.add_argument("--nmax", type=int, default=20000)
    ap.add_argument("--lmax", type=int, default=61)
    ap.add_argument("--export-factor", type=float, default=2.0)
    ap.add_argument("--vectors", type=int, default=2)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)

    def progress(row):
        print(f"{row.element[0]:4d} {row.element[1]:3d} N={row.norm:6d} {'·'.join(map(str, row.order)):16s} "
              f"{'ok ' if row.found else 'FAIL'} {row.build_seconds:6.2f}s {row.note}", flush=True)

    result = run(args.target, nmax=args.nmax, lmax=args.lmax, export_factor=args.export_factor,
                 vectors=args.vectors, progress=progress)
    model = scalar_mult_model(result)
    chains_path = os.path.join(args.out_dir, "chains.constants.json")
    with open(chains_path, "w") as f:
        json.dump({k: v for k, v in result.items() if k != "rows"}, f, indent=1)
        f.write("\n")
    cat_path = os.path.join(args.out_dir, "catalogue.json")
    with open(cat_path, "w") as f:
        json.dump({k: v for k, v in result.items() if k != "chains"}, f, indent=1)
        f.write("\n")
    model_path = os.path.join(args.out_dir, "model.json")
    with open(model_path, "w") as f:
        json.dump(model, f, indent=1)
        f.write("\n")
    with open(os.path.join(args.out_dir, "catalogue.md"), "w") as f:
        f.write(markdown(result, model))
    sums = {os.path.basename(pth): sha256_file(pth) for pth in (chains_path, cat_path, model_path)}
    with open(os.path.join(args.out_dir, "SHA256SUMS"), "w") as f:
        for name, digest in sorted(sums.items()):
            f.write(f"{digest}  {name}\n")
    nf = sum(1 for r in result["rows"] if r["found"])
    print(json.dumps({"rows": len(result["rows"]), "verified": nf, "exported": len(result["chains"]),
                      "best_optimised_M_eq": result["bounds"]["best_optimised_M_eq"],
                      "consistent": result["eigenvalues_consistent_across_orders"], **sums}, indent=1))
    return 0 if nf == len(result["rows"]) and result["eigenvalues_consistent_across_orders"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
