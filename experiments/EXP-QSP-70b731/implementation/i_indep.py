"""I_indep — independent instrument for N_K(L) from STATEMENT + derivation (A).

Derivation (A) from H-QSP-cd0c90 / IDEA-20260916-3f7a1c (those records only;
KN-TECH-54c38e and EXP-QSP-33b442 implementation were not read):

  L = X^{2^{n'}} + lambda(X),  n = q n' + r,  0 <= r < n'.
  For lambda in F_2[X], every K-root x of L satisfies
      x^{2^{k n'}} = lambda^{∘k}(x)  for k >= 1,
  and with y := x^{2^r},
      H(y) = 0  where  H(Y) := Y^{2^{n'-r}} + lambda^{∘(q+1)}(Y).
  Completeness: every K-root of L maps to a K-root of H.
  Soundness: closing test x^{2^r} = y with L(x) = 0 recovers the K-roots of L.
  Bound: N_K(L) <= deg H = max(2^{n'-r}, d^{q+1}) when H != 0.

Paths:
  (A-H)   deg H <= H_DEGREE_MAX: build H, take K-roots, closing test.
  (A-toy) n <= 20: STATEMENT brute-force over K.
  (A-L)   otherwise with tractable deg L: independent deg-gcd count (and root
          list when N <= ROOT_LIST_MAX).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import gf2_poly as gp
from candidates import bound_A, qr_decomposition
from field_f2n import FieldF2n

H_DEGREE_MAX = 300_000
ROOT_LIST_MAX = 512


def passes_L(F: FieldF2n, x: int, lam: int, n_prime: int) -> bool:
    return F.pow(x, 1 << n_prime) == F.eval_f2_poly(lam, x)


def closing_x_from_y(F: FieldF2n, y: int, r: int) -> int:
    """Unique x in K with x^{2^r} = y: x = y^{2^{n-r}}."""
    if r == 0:
        return y
    return F.frobenius(y, F.n - r)


def build_H(lam: int, n: int, n_prime: int) -> Tuple[int, int, int, int]:
    """Return (H, q, r, bound)."""
    q, r = qr_decomposition(n, n_prime)
    mu = gp.iterate_compose(lam, q + 1)
    H = gp.monomial(1 << (n_prime - r)) ^ mu
    return H, q, r, bound_A(n, n_prime, gp.degree(lam))


def _independent_gcd_count(lam: int, n: int, n_prime: int) -> int:
    """Duplicate deg-gcd loop (does not call i_direct)."""
    bound = 1 << n_prime
    L = gp.monomial(bound) ^ lam
    x = gp.monomial(1)
    for _ in range(n):
        x = gp.mod_pow2_x_plus_lam(gp.square(x), n_prime, lam)
    h = x ^ gp.monomial(1)
    if h == 0:
        return bound
    return gp.degree(gp.gcd(L, h))


def roots_of_f2_poly_in_K(poly: int, F: FieldF2n) -> List[int]:
    """List distinct K-roots of a GF(2)-coeff poly (small-n scan or factor)."""
    n = F.n
    g = gp.make_monic(gp.gcd_with_field_poly(poly, n))
    if gp.degree(g) <= 0:
        return []
    if n <= 20:
        return [x for x in F.all_elements() if F.eval_f2_poly(g, x) == 0]
    if gp.degree(g) > ROOT_LIST_MAX:
        return []
    irreps = gp.factor_squarefree_splitting(g, n)
    roots: List[int] = []
    for fac in irreps:
        d = gp.degree(fac)
        if d == 1:
            roots.append(fac & 1)  # X+b monic => root b
        elif d > 1:
            alpha = _find_one_root_iso(fac, F)
            if alpha is None:
                continue
            x = alpha
            for _ in range(d):
                roots.append(x)
                x = F.square(x)
    return sorted(set(roots))


def _find_one_root_iso(fac: int, F: FieldF2n) -> Optional[int]:
    """One root of same-degree irreducible via random minpoly match in E=F_2[w]/(fac)."""
    import random

    d = gp.degree(fac)
    if d != F.n:
        if F.n <= 20:
            return next((x for x in F.all_elements() if F.eval_f2_poly(fac, x) == 0), None)
        return None
    P = gp.make_monic(F.modulus)
    rng = random.Random(0xC0FFEE ^ d)

    def minpoly(beta: int) -> int:
        vecs = []
        x = 1
        for _ in range(d + 1):
            vecs.append([(x >> j) & 1 for j in range(d)])
            x = gp.mod(gp.mul(x, beta), fac)
        rows = [list(r) for r in zip(*vecs)]
        pivots = {}
        r = 0
        R, C = d, d + 1
        for c in range(C):
            piv = next((i for i in range(r, R) if rows[i][c]), None)
            if piv is None:
                continue
            rows[r], rows[piv] = rows[piv], rows[r]
            for i in range(R):
                if i != r and rows[i][c]:
                    rows[i] = [a ^ b for a, b in zip(rows[i], rows[r])]
            pivots[c] = r
            r += 1
            if r == R:
                break
        for c in range(C):
            if c not in pivots:
                dep = [0] * C
                dep[c] = 1
                for pc, pr in pivots.items():
                    if rows[pr][c]:
                        dep[pc] = 1
                poly = 0
                for i, bit in enumerate(dep):
                    if bit:
                        poly ^= 1 << i
                return gp.make_monic(poly)
        return 0

    beta = None
    for _ in range(512):
        cand = rng.getrandbits(d) or 1
        if minpoly(cand) == P:
            beta = cand
            break
    if beta is None:
        return None
    # Invert iso: φ(z)=beta; find α=φ^{-1}(w)
    w_elem = 2
    vecs = []
    x = 1
    for _ in range(d):
        vecs.append([(x >> j) & 1 for j in range(d)])
        x = gp.mod(gp.mul(x, beta), fac)
    target = [(w_elem >> j) & 1 for j in range(d)]
    M = [list(row) + [target[i]] for i, row in enumerate(zip(*vecs))]
    pivots = {}
    r = 0
    for c in range(d):
        piv = next((i for i in range(r, d) if M[i][c]), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        for i in range(d):
            if i != r and M[i][c]:
                M[i] = [a ^ b for a, b in zip(M[i], M[r])]
        pivots[c] = r
        r += 1
    c_bits = [0] * d
    for c, pr in pivots.items():
        c_bits[c] = M[pr][d]
    alpha = 0
    for i, bit in enumerate(c_bits):
        if bit:
            alpha ^= 1 << i
    if F.eval_f2_poly(fac, alpha) == 0:
        return alpha
    return None


def count_via_H(lam: int, n: int, n_prime: int,
                F: Optional[FieldF2n] = None) -> Dict[str, Any]:
    F = F or FieldF2n.for_n(n)
    H, q, r, bnd = build_H(lam, n, n_prime)
    if gp.degree(H) < 0:
        raise ValueError("H is zero polynomial")
    if gp.degree(H) > H_DEGREE_MAX:
        raise ValueError(f"H degree {gp.degree(H)} exceeds H_DEGREE_MAX")
    # For counting via (A) without always materialising every y-root in K:
    # when n is large, use deg gcd(H, Y^{2^n}-Y) as |{y}| then apply closing
    # only when that count is small enough to list.
    y_count = gp.degree(gp.gcd_with_field_poly(H, n))
    passing: List[int] = []
    slack = 0
    roots_listed = False
    if n <= 20 or y_count <= ROOT_LIST_MAX:
        y_roots = roots_of_f2_poly_in_K(H, F)
        roots_listed = True
        for y in y_roots:
            x = closing_x_from_y(F, y, r)
            if F.frobenius(x, r) == y and passes_L(F, x, lam, n_prime):
                passing.append(x)
            else:
                slack += 1
        passing = sorted(set(passing))
        N = len(passing)
    else:
        # Bound-level observation only — must not claim a listed N from H without
        # closing. Fall through by raising so measure_indep uses A-L.
        raise ValueError(f"H has {y_count} K-roots; too many to close-test in v1")
    return {
        "instrument": "I_indep",
        "path": "A-H",
        "N": N,
        "roots": passing if roots_listed else None,
        "slack": slack,
        "bound": bnd,
        "q": q,
        "r": r,
        "H_degree": gp.degree(H),
        "y_root_count": y_count,
        "n": n,
        "n_prime": n_prime,
        "lambda": lam,
        "lambda_hex": format(lam, "x"),
    }


def count_via_enumeration(lam: int, n: int, n_prime: int,
                          F: Optional[FieldF2n] = None) -> Dict[str, Any]:
    F = F or FieldF2n.for_n(n)
    if n > 20:
        raise ValueError("A-toy only for n <= 20")
    q, r = qr_decomposition(n, n_prime)
    bnd = bound_A(n, n_prime, gp.degree(lam))
    roots = [x for x in F.all_elements() if passes_L(F, x, lam, n_prime)]
    return {
        "instrument": "I_indep",
        "path": "A-toy",
        "N": len(roots),
        "roots": roots,
        "slack": None,
        "bound": bnd,
        "q": q,
        "r": r,
        "n": n,
        "n_prime": n_prime,
        "lambda": lam,
        "lambda_hex": format(lam, "x"),
    }


def count_via_L_listing(lam: int, n: int, n_prime: int,
                        F: Optional[FieldF2n] = None) -> Dict[str, Any]:
    F = F or FieldF2n.for_n(n)
    q, r = qr_decomposition(n, n_prime)
    bnd = bound_A(n, n_prime, gp.degree(lam))
    if n <= 20:
        roots = [x for x in F.all_elements() if passes_L(F, x, lam, n_prime)]
        return {
            "instrument": "I_indep",
            "path": "A-L-enum",
            "N": len(roots),
            "roots": roots,
            "slack": 0,
            "bound": bnd,
            "q": q,
            "r": r,
            "n": n,
            "n_prime": n_prime,
            "lambda": lam,
            "lambda_hex": format(lam, "x"),
            "listing_complete": True,
            "root_list_deferred": False,
        }
    N = _independent_gcd_count(lam, n, n_prime)
    roots: Optional[List[int]] = None
    listing_complete = N == 0
    slack = 0
    deferred = N > ROOT_LIST_MAX
    if 0 < N <= ROOT_LIST_MAX:
        L = gp.monomial(1 << n_prime) ^ lam
        g = gp.gcd_with_field_poly(L, n)
        listed = roots_of_f2_poly_in_K(g, F)
        verified = sorted({x for x in listed if passes_L(F, x, lam, n_prime)})
        roots = verified
        listing_complete = len(verified) == N
        slack = max(0, len(listed) - len(verified))
    return {
        "instrument": "I_indep",
        "path": "A-L",
        "N": N,
        "roots": roots,
        "slack": slack,
        "bound": bnd,
        "q": q,
        "r": r,
        "n": n,
        "n_prime": n_prime,
        "lambda": lam,
        "lambda_hex": format(lam, "x"),
        "listing_complete": listing_complete,
        "root_list_deferred": deferred,
    }


def measure_indep(lam: int, n: int, n_prime: int,
                  F: Optional[FieldF2n] = None) -> Dict[str, Any]:
    """Select I_indep path by tractability."""
    d = gp.degree(lam)
    q, r = qr_decomposition(n, n_prime)
    h_deg = max(1 << (n_prime - r), d ** (q + 1) if d >= 0 else 0)
    if n <= 20:
        return count_via_enumeration(lam, n, n_prime, F)
    if h_deg <= H_DEGREE_MAX:
        try:
            return count_via_H(lam, n, n_prime, F)
        except Exception as exc:  # noqa: BLE001
            out = count_via_L_listing(lam, n, n_prime, F)
            out["H_fallback_reason"] = str(exc)
            return out
    return count_via_L_listing(lam, n, n_prime, F)
