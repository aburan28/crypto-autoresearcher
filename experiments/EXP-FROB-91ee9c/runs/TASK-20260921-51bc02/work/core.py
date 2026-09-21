"""
Core library for EXP-FROB-91ee9c driver, built on SageMath.
All probabilities/ratios reported as fractions.Fraction (exact rationals).
"""
from sage.all import GF, PolynomialRing, EllipticCurve, matrix, vector, Integer, Zmod, factor
from fractions import Fraction
from itertools import product
import random
import time
import sys


def find_first_irreducible(q, n):
    F = GF(q)
    R = PolynomialRing(F, 'x')
    for coeffs in product(range(q), repeat=n):
        poly = R(list(coeffs) + [1])
        if poly.is_irreducible():
            return poly
    raise RuntimeError("no irreducible found")


def field_setup(q, n):
    g = find_first_irreducible(q, n)
    K = GF(q ** n, name='z', modulus=g)
    return K, g


def elt_to_vec_list(elt, q, n):
    v = elt.polynomial().list()
    v = [int(c) for c in v] + [0] * (n - len(v))
    return v


def enc_elt(elt, q, n):
    v = elt_to_vec_list(elt, q, n)
    s = 0
    for i in range(n - 1, -1, -1):
        s = s * q + v[i]
    return s


def order_ext_trace(a, q, n):
    """Lucas recurrence for s_n = alpha^n+beta^n given trace a over F_q."""
    a = Integer(a); q = Integer(q)
    s0, s1 = Integer(2), a
    if n == 0:
        return s0
    for k in range(2, n + 1):
        s0, s1 = s1, a * s1 - q * s0
    return s1


def frobenius_matrix(K, z, q, n):
    F = GF(q)
    cols = []
    for i in range(n):
        b = z ** i
        img = b ** q
        cols.append(elt_to_vec_list(img, q, n))
    M = matrix(F, n, n, lambda r, c: cols[c][r])
    return M


def poly_of_matrix(poly, M, F):
    n = M.nrows()
    result = matrix.zero(F, n, n)
    coeffs = poly.list()
    Mp = matrix.identity(F, n)
    for c in coeffs:
        result += c * Mp
        Mp = Mp * M
    return result


def factor_xn_minus_1(q, n):
    F = GF(q)
    R = PolynomialRing(F, 'x')
    xx = R.gen()
    h = xx ** n - 1
    sqfree = h.is_squarefree()
    facs = list(h.factor())
    return xx, h, sqfree, facs


def object_search(q, n, K, M, F, want_curves=2, log=None):
    """Enumerate (A,B) lexicographically over F_q, apply eligibility rule.
    Returns (accepted_list, rejected_list)."""
    accepted = []
    rejected = []
    for A in range(q):
        for B in range(q):
            reason = None
            if (4 * A ** 3 + 27 * B ** 2) % q == 0:
                reason = "singular"
            if reason is None:
                Eq_curve = EllipticCurve(GF(q), [A, B])
                Eq_order = Eq_curve.order()
                a = q + 1 - Eq_order
                if a % q == 0:
                    reason = "supersingular"
            if reason is not None:
                rejected.append({"A": A, "B": B, "reason": reason})
                continue
            an = order_ext_trace(a, q, n)
            Eqn_order = q ** n + 1 - an
            fac = factor(Eqn_order)
            primes_exp1 = sorted([int(p) for p, e in fac if e == 1], reverse=True)
            N = None
            for p in primes_exp1:
                if p < 17:
                    continue
                if Eq_order % p == 0:
                    continue
                N = p
                break
            if N is None:
                rejected.append({"A": A, "B": B, "reason": "no_eligible_N",
                                  "Eq_order": int(Eq_order), "Eqn_order": int(Eqn_order)})
                continue
            # solve mu^2 - a mu + q = 0 mod N
            Zn = Zmod(N)
            aN = Zn(a); qN = Zn(q)
            disc = aN ** 2 - 4 * qN
            sqrts = disc.sqrt(extend=False, all=True)
            if not sqrts:
                rejected.append({"A": A, "B": B, "reason": "no_sqrt_mod_N", "N": N})
                continue
            mu_candidates = [(aN + s) / 2 for s in sqrts]
            mu_n_matches = [m for m in mu_candidates if m.multiplicative_order() == n]
            if not mu_n_matches:
                rejected.append({"A": A, "B": B, "reason": "no_mu_order_n", "N": N,
                                  "mu_orders": [int(m.multiplicative_order()) for m in mu_candidates]})
                continue
            # build curve over K, find G, verify Frobenius eigenvalue directly
            EK = EllipticCurve(K, [A, B])
            cofactor = Eqn_order // N
            if Eqn_order % N != 0:
                rejected.append({"A": A, "B": B, "reason": "cofactor_not_exact"})
                continue
            j_inv = EK.j_invariant()
            # scan affine points lexicographically by enc(x) then enc(y)
            Gpt = None
            scanned = 0
            for xvec in product(range(q), repeat=n):
                # build field element from vec (a_0 + a_1 z + ...)
                elt = K(0)
                pw = K(1)
                zgen = K.gen()
                for i in range(n):
                    if xvec[i]:
                        elt += xvec[i] * pw
                    pw *= zgen
                rhs = elt ** 3 + A * elt + B
                scanned += 1
                if rhs.is_square():
                    y0 = rhs.sqrt()
                    ys = sorted([y0, -y0], key=lambda e: enc_elt(e, q, n))
                    for y in ys:
                        P = EK(elt, y)
                        cP = cofactor * P
                        if not cP.is_zero():
                            Gpt = cP
                            break
                    if Gpt is not None:
                        break
                if scanned > q ** n:
                    break
            if Gpt is None:
                rejected.append({"A": A, "B": B, "reason": "no_generator_found", "N": N})
                continue
            ordG = Gpt.order()
            if ordG != N:
                rejected.append({"A": A, "B": B, "reason": "generator_order_mismatch",
                                  "expected_N": N, "actual_order": int(ordG)})
                continue

            def frob_pt(P):
                return EK(P[0] ** q, P[1] ** q)

            piG = frob_pt(Gpt)
            verified_mu = None
            for m in mu_n_matches:
                if piG == Integer(int(m)) * Gpt:
                    verified_mu = int(m)
                    break
            if verified_mu is None:
                rejected.append({"A": A, "B": B, "reason": "frobenius_eigenvalue_mismatch", "N": N})
                continue
            accepted.append({
                "A": A, "B": B, "j_invariant": str(j_inv),
                "Eq_order": int(Eq_order), "Eqn_order": int(Eqn_order),
                "trace_a": int(a), "N": int(N), "cofactor": int(cofactor),
                "mu": verified_mu, "ord_mu": n,
                "G": (str(Gpt[0]), str(Gpt[1])),
                "G_enc": (enc_elt(Gpt[0], q, n), enc_elt(Gpt[1], q, n)),
            })
            if log is not None:
                log.write(f"accepted curve A={A} B={B} N={N} j={j_inv}\n")
            distinct_j = set(c["j_invariant"] for c in accepted)
            if len(distinct_j) >= want_curves:
                # need exactly `want_curves` DISTINCT j-invariants; stop once achieved
                # keep only first occurrence per distinct j-invariant, in order found
                break
    # reduce accepted to first curve per distinct j-invariant, preserving order, cap at want_curves
    seen = set()
    final = []
    for c in accepted:
        if c["j_invariant"] in seen:
            continue
        seen.add(c["j_invariant"])
        final.append(c)
        if len(final) >= want_curves:
            break
    return final, rejected
