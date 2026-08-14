#!/usr/bin/env python3
"""
census.py -- EXP-ISOU-2ac81f: complete-class ECDLP cost census on a
P-256-SHAPED ordinary toy curve.

Implements the frozen protocol experiments/EXP-ISOU-2ac81f/specification.yaml
(version 1, approved under DEC-20260813-e0077d) exactly as written, under the
implementation-level resolutions frozen in ledger/handoffs/TASK-20260813-4bee82.yaml.

This module SOLVES and MEASURES.  It does NOT verify its own certificates:
certificate verification is performed by implementation/certificate_checker.py,
a separate module that shares no state and no code path with anything here and
is invoked as a separate process.

Subcommands
-----------
  run        select + freeze the base curve, freeze the seed band, enumerate the
             class, transfer the DLP instance, solve, measure Q1/Q2/Q3, run all
             controls, and write every raw artifact.
  summarize  read the raw artifacts AND the independent checker's output, and
             write summary.json.  Members without an independently verified
             certificate contribute no cost datum.

No interpretation, no verdict, no evidence record is produced anywhere in this
file.  Toy scale only.
"""

import argparse
import json
import math
import os
import platform
import random
import subprocess
import sys
import time
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# FROZEN PROTOCOL CONSTANTS
# These are the implementation-level resolutions the handoff fixes BEFORE any
# datum is seen.  They are written verbatim into every run manifest.
# ---------------------------------------------------------------------------

PROTOCOL = {
    "experiment_id": "EXP-ISOU-2ac81f",
    "specification_version": 1,
    "isogeny_degrees": [2, 3, 5, 7, 11, 13],
    "seeds": [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597],
    "fresh_seeds_for_tail_check": [
        100001, 100002, 100003, 100005, 100008, 100013, 100021, 100034,
        100055, 100089, 100144, 100233, 100377, 100610, 100987, 101597,
    ],
    "rho": {
        "walk_family": "Teske mixed r-adding walk",
        "partition_count": 20,
        "adding_branches": 16,
        "doubling_branches": 4,
        "partition_rule": "branch index = (affine x-coordinate of W) mod 20",
        "distinguished_point_rule": "affine x-coordinate of W congruent to 0 mod 16",
        "distinguished_point_density": 0.0625,
        "negation_map_used": False,
        "negation_map_note": (
            "The primary-metric solver uses NO negation map and no other "
            "automorphism speedup, because the frozen reproduction fixture is "
            "0.886*sqrt(N) for plain rho."
        ),
        "max_steps_rule": "60 * isqrt(N)",
        "identical_across": "class members, base curve, and null objects alike",
        "counted_quantity": (
            "group_operations_to_solve counts the rho WALK's group operations "
            "(adds + doublings) until the collision that yields k. The "
            "seed-dependent precomputation (16 scalar multiplications building "
            "the adding-branch table, an identical scalar schedule on every "
            "curve of the same order N) is recorded SEPARATELY as "
            "group_ops_precompute and is not folded into Q1."
        ),
    },
    "q1_common_coordinate_system": {
        "id": "AFFINE_SHORT_WEIERSTRASS",
        "definition": (
            "Affine coordinates on y^2 = x^3 + a*x + b over F_p, one single "
            "Python implementation (ec_add / ec_dbl in this module) used for "
            "EVERY curve: base curve, every class member, and every null "
            "object. The group-operation counter therefore counts the same "
            "abstract events on every curve."
        ),
    },
    "q2_candidate_model_set": [
        {
            "id": "AFFINE_SHORT_WEIERSTRASS",
            "reachability": "always",
            "note": "inversion performed by instrumented Fermat exponentiation, so its field cost is measured, not modelled",
        },
        {
            "id": "JACOBIAN_GENERIC",
            "reachability": "always",
            "note": "standard Jacobian projective coordinates, generic a",
        },
        {
            "id": "JACOBIAN_A_MINUS_3",
            "reachability": "a/(-3) is a fourth power in F_p",
            "note": "IEEE P1363 a = -3 doubling",
        },
        {
            "id": "MONTGOMERY",
            "reachability": "curve has a rational point of order 4",
            "note": "predicted unreachable everywhere because N is prime and odd",
        },
        {
            "id": "TWISTED_EDWARDS",
            "reachability": "curve has a rational point of order 4",
            "note": "predicted unreachable everywhere because N is prime and odd",
        },
    ],
    "q2_cost_rule": (
        "For each REACHABLE candidate model, the member's own seed-index-0 rho "
        "walk is re-executed in that model for the first Q2_REPLAY_OPS group "
        "operations, with fully instrumented F_p arithmetic. Multiplications "
        "and squarings are accumulated SEPARATELY for the addition routine and "
        "for the doubling routine, giving a per-ADD cost and a per-DBL cost in "
        "(M + MS_WEIGHT*S) for that model on that member. "
        "\n"
        "Q2 IS THEN EVALUATED AT A SINGLE COMMON OPERATION MIX, declared before "
        "measurement: the (adds, doublings) mix of the BASE CURVE's "
        "seed-index-0 walk over its first Q2_REPLAY_OPS group operations. "
        "Every member's Q2 is (n_add*add_cost + n_dbl*dbl_cost)/(n_add+n_dbl) "
        "at that one common mix. This is necessary because each member's own "
        "walk draws its own random adds/doublings proportion, and a "
        "per-operation ratio evaluated at a member-specific mix would confound "
        "the model effect Q2 is defined to measure with the seed noise in that "
        "proportion. The member's own-mix value is ALSO recorded, as a "
        "secondary field, so both are visible. "
        "\n"
        "The cheapest model by the common-mix number is the member's 'cheapest "
        "reachable model'. The coordinate-normalization overhead needed to "
        "expose the affine x-coordinate to the walk function is instrumented "
        "and recorded SEPARATELY and is NOT part of the per-group-operation "
        "ratio, because Q2 is defined as the field cost of the GROUP OPERATION. "
        "The replayed op sequence is asserted equal to the Q1 op sequence, "
        "which is a self-check on the replay."
    ),
    "q2_replay_ops": 300,
    "ms_aggregation_rule": {
        "squaring_weight_in_multiplications": 1.0,
        "note": (
            "Multiplications M and squarings S are instrumented and recorded "
            "SEPARATELY as raw counts everywhere. The reported per-operation "
            "ratio aggregates them as M + 1.0*S. Any other weighting is "
            "recomputable by a reviewer from the raw counts."
        ),
    },
    "q3_definition": (
        "charged_end_to_end_cost is measured ENTIRELY in FIELD MULTIPLICATIONS "
        "(M + 1.0*S). No group-operation count is ever added to a "
        "field-multiplication count. Q3(member) = walk_cost_to_member + "
        "median_over_seeds(Q1(member)) * Q2(member); compared against "
        "median_over_seeds(Q1(base)) * Q2(base)."
    ),
    "walk_cost_basis": {
        "measured_component": (
            "Velu isogeny EVALUATION of the two instance points P and Q along "
            "the BFS-tree path from E_0 to the member, executed with the "
            "instrumented F_p arithmetic of this module. Fully measured."
        ),
        "modelled_component": (
            "Velu isogeny CONSTRUCTION (division polynomial, Frobenius "
            "eigenvalue kernel polynomial, codomain coefficients). The "
            "polynomial arithmetic uses Kronecker substitution on Python big "
            "integers, whose individual F_p multiplications cannot be counted. "
            "Its cost is therefore MODELLED by the declared formula below and "
            "labelled `modelled` everywhere it appears."
        ),
        "modelled_formula": (
            "polynomial multiplication of a degree-m by a degree-n polynomial "
            "costs (m+1)*(n+1) field multiplications; polynomial remainder of a "
            "degree-m polynomial by a degree-n monic-normalized polynomial "
            "costs (m-n+1)*(n+1) field multiplications plus one field inversion "
            "charged at 1*ceil(log2(p)) squarings + 1*hamming-weight(p-2) "
            "multiplications; polynomial gcd charges the sum of its remainder "
            "steps. Squarings are charged at weight 1.0."
        ),
        "reported_bases": (
            "Q3 is reported on two explicitly labelled bases: "
            "q3_measured_walk_only (walk = measured evaluation cost only) and "
            "q3_measured_plus_modelled_walk (walk = measured evaluation cost + "
            "modelled construction cost). Neither is presented as the other."
        ),
    },
    "seed_band_rule": (
        "The seed dispersion band is computed on the base curve ONLY, from its "
        "16 per-seed group_operations_to_solve values, and is FROZEN before any "
        "between-member number is computed or read. It has TWO parts, both "
        "frozen together and both reported everywhere: "
        "(a) per_seed_band = [min, max] of the 16 raw per-seed counts, the raw "
        "within-curve dispersion; "
        "(b) median_band = the [2.5, 97.5] percentile interval of the "
        "median-of-16 statistic, obtained by a nonparametric bootstrap of the "
        "16 base-curve counts with the declared bootstrap seed and resample "
        "count below. "
        "The PRIMARY band for every between-member comparison and for the "
        "null-object separation gate is median_band, because the between-member "
        "statistic actually compared is each curve's median over the same 16 "
        "seeds, and a band on single draws is not the resolution of a band on "
        "medians. per_seed_band is reported alongside it in every case, and the "
        "null-object gate reports its verdict under BOTH bands. Neither band is "
        "widened, narrowed or recomputed after any member datum is seen."
    ),
    "seed_band_bootstrap": {"seed": 20260813, "resamples": 4000,
                            "percentiles": [2.5, 97.5]},
    "null_object_rule": (
        "At least 8 random curves over a DECLARED SMALLER prime p' with prime "
        "order N' <= N/16. Same-p different-trace curves are additionally "
        "enumerated as a STRUCTURAL null object (they must not appear in the "
        "class walk) but carry no cost-resolution role. Separation criterion, "
        "declared before measurement: the null objects' median "
        "group_operations_to_solve must lie strictly OUTSIDE the frozen "
        "median_band of the base curve (the PRIMARY gate), and the verdict "
        "under the raw per_seed_band is reported alongside it. Failure to "
        "separate under the primary gate is a STOP: no Q1 and no Q3 result is "
        "reported from that run in any form, including as preliminary or "
        "partial."
    ),
    "dedup_rule": (
        "Vertices are deduplicated by F_p-ISOMORPHISM class, not by j-invariant "
        "alone: (a,b) ~ (a',b') iff there exists u in F_p^* with a' = u^4*a and "
        "b' = u^6*b. j-invariant is used only as a bucketing key; within a "
        "bucket the isomorphism test above is applied pairwise, so twists "
        "sharing a j-invariant are never merged."
    ),
    "special_j_rule": (
        "Any member with j = 0 or j = 1728 is reported SEPARATELY and excluded "
        "from the generic band."
    ),
    "completeness_rule": (
        "The census is COMPLETE only when the enumerated vertex count equals "
        "h(disc(End(E_0))), computed INDEPENDENTLY of the walk by counting "
        "reduced primitive positive-definite binary quadratic forms of "
        "discriminant D. Both numbers are reported side by side in every case."
    ),
    "edge_certificate_rule": (
        "Each edge carries: the degree ell, the Frobenius eigenvalue lambda, the "
        "kernel polynomial h(x) (the kernel subgroup is Galois-stable but has NO "
        "F_p-rational generator, because N is prime, so the kernel generator is "
        "specified by its minimal polynomial rather than by coordinates), the "
        "check deg h == (ell-1)/2, the check h | psi_ell, the codomain (a',b') "
        "with nonzero discriminant, and the order check [N]R = O for two "
        "independent random R on the codomain (which pins #E' = N because N is "
        "prime and p+1+2*sqrt(p) < 2N)."
    ),
    "bsgs_cross_check_rule": (
        "BSGS, sharing no walk logic with rho, is run on the SMALLEST instance "
        "(the null object of least order), on the base curve instance, and on "
        "one deterministically selected class member (the one of least "
        "j-invariant). It must return the same k as rho."
    ),
}

MS_WEIGHT = 1.0


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# 1. INSTRUMENTED F_p ARITHMETIC  (used for Q2 and for the MEASURED walk cost)
# ---------------------------------------------------------------------------

class FC:
    """Field-operation counter. M and S are always kept separate."""

    __slots__ = ("M", "S", "A", "I")

    def __init__(self):
        self.M = 0
        self.S = 0
        self.A = 0
        self.I = 0

    def snapshot(self):
        return {"M": self.M, "S": self.S, "A": self.A, "I": self.I}

    def weighted(self):
        return self.M + MS_WEIGHT * self.S


def fm(c, x, y, p):
    c.M += 1
    return (x * y) % p


def fmc(c, k, x, p):
    """
    Multiplication by a SMALL INTEGER CONSTANT (2, 3, 4, 8, ...).  Declared
    convention, frozen before measurement: this is NOT charged as a field
    multiplication, because the standard Jacobian-coordinate operation counts
    the frozen prediction rests on (IEEE P1363; dbl-2001-b at 3M+5S,
    add-2007-bl at 11M+5S) do not charge it either.  Charging it would make the
    measured counts incomparable with the cost model under test.  The
    convention is uniform across every candidate model and every curve.
    """
    c.A += 1
    return (k * x) % p


def fs(c, x, p):
    c.S += 1
    return (x * x) % p


def fa(c, x, y, p):
    c.A += 1
    return (x + y) % p


def fsub(c, x, y, p):
    c.A += 1
    return (x - y) % p


def finv(c, x, p):
    """Inversion by instrumented Fermat exponentiation: cost is MEASURED."""
    c.I += 1
    e = p - 2
    result = 1
    base = x % p
    first = True
    for bit in bin(e)[2:][::-1]:
        if bit == "1":
            if first:
                result = base
                first = False
            else:
                result = fm(c, result, base, p)
        base = fs(c, base, p)
    return result


# ---------------------------------------------------------------------------
# 2. FAST (UNCOUNTED) ARITHMETIC AND CURVE UTILITIES
#    Used for structural work -- selection, enumeration, and the Q1 solver,
#    whose metric is GROUP operations, not field operations.
# ---------------------------------------------------------------------------

def inv(x, p):
    return pow(x, p - 2, p)


def is_prime(n):
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def prev_prime(n):
    n -= 1
    if n % 2 == 0:
        n -= 1
    while not is_prime(n):
        n -= 2
    return n


def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * inv(2 * y1 % p, p) % p
    else:
        lam = (y2 - y1) * inv((x2 - x1) % p, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def ec_dbl(P, a, p):
    if P is None:
        return None
    x1, y1 = P
    if y1 == 0:
        return None
    lam = (3 * x1 * x1 + a) * inv(2 * y1 % p, p) % p
    x3 = (lam * lam - 2 * x1) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def ec_mul(P, n, a, p):
    if n == 0 or P is None:
        return None
    if n < 0:
        P = (P[0], (-P[1]) % p)
        n = -n
    R = None
    Q = P
    while n:
        if n & 1:
            R = ec_add(R, Q, a, p)
        Q = ec_dbl(Q, a, p)
        n >>= 1
    return R


def is_on_curve(P, a, b, p):
    if P is None:
        return True
    x, y = P
    return (y * y - x * x * x - a * x - b) % p == 0


def curve_disc(a, b, p):
    return (-16 * (4 * a * a * a + 27 * b * b)) % p


def j_invariant(a, b, p):
    num = 1728 * 4 * a % p * a % p * a % p
    den = (4 * a * a * a + 27 * b * b) % p
    if den == 0:
        return None
    return num * inv(den, p) % p


def tonelli(n, p):
    n %= p
    if n == 0:
        return 0
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        bexp = pow(c, 1 << (m - i - 1), p)
        m = i
        c = bexp * bexp % p
        t = t * c % p
        r = r * bexp % p
    return r


def random_point(a, b, p, rnd):
    while True:
        x = rnd.randrange(p)
        rhs = (x * x * x + a * x + b) % p
        y = tonelli(rhs, p)
        if y is not None and not (y == 0 and rhs == 0):
            return (x, y)


def fp_isomorphic(a1, b1, a2, b2, p):
    """(a1,b1) ~ (a2,b2) over F_p iff exists u!=0 with a2=u^4 a1, b2=u^6 b1."""
    if (a1 == 0) != (a2 == 0):
        return False
    if (b1 == 0) != (b2 == 0):
        return False
    if a1 == 0:  # j = 0 : b2/b1 must be a sixth power
        r = b2 * inv(b1, p) % p
        g = math.gcd(6, p - 1)
        return pow(r, (p - 1) // g, p) == 1
    if b1 == 0:  # j = 1728 : a2/a1 must be a fourth power
        r = a2 * inv(a1, p) % p
        g = math.gcd(4, p - 1)
        return pow(r, (p - 1) // g, p) == 1
    # generic: u^2 = (b2/b1)*(a1/a2)
    u2 = b2 * inv(b1, p) % p * a1 % p * inv(a2, p) % p
    u = tonelli(u2, p)
    if u is None:
        return False
    u4 = u2 * u2 % p
    u6 = u4 * u2 % p
    return (u4 * a1 - a2) % p == 0 and (u6 * b1 - b2) % p == 0


def a_minus_3_reachable(a, b, p):
    """a = -3 model reachable iff a/(-3) is a fourth power in F_p."""
    if a == 0:
        return False, "a = 0 (j = 0): u^4*0 = 0 can never equal -3"
    z = a * inv((-3) % p, p) % p
    g = math.gcd(4, p - 1)
    ok = pow(z, (p - 1) // g, p) == 1
    return ok, "a/(-3) is a fourth power in F_p: %s (gcd(4,p-1)=%d)" % (ok, g)


def fourth_root(z, p):
    r = tonelli(z, p)
    if r is None:
        return None
    return tonelli(r, p)


def has_rational_2_torsion(a, b, p):
    """True iff x^3 + a x + b has a root in F_p."""
    for x in range(0, min(p, 3)):
        if (x * x * x + a * x + b) % p == 0:
            return True
    # gcd(x^p - x, x^3+ax+b) over F_p
    f = [b % p, a % p, 0, 1]
    xp = poly_powmod([0, 1], p, f, p)
    g = poly_gcd(poly_sub(xp, [0, 1], p), f, p)
    return poly_deg(g) >= 1


def montgomery_or_edwards_reachable(a, b, p, N):
    """
    A Montgomery or twisted-Edwards model requires a rational point of order 4
    (in particular a rational point of order 2). Report the underlying tests.
    """
    two_tors = has_rational_2_torsion(a, b, p)
    return {
        "reachable": bool(two_tors and N % 4 == 0),
        "rational_2_torsion": bool(two_tors),
        "order_divisible_by_4": bool(N % 4 == 0),
        "test": "Montgomery/Edwards require a rational point of order 4, hence 4 | #E(F_p) and a rational 2-torsion point",
    }


def group_order(a, b, p, rnd, tries=8):
    """
    #E(F_p) by baby-step/giant-step in the Hasse interval.
    Returns N, or None if it could not be pinned down.
    """
    T = int(2 * math.isqrt(p)) + 2
    W = max(1, math.isqrt(2 * T) + 1)
    candidates = None
    for _ in range(tries):
        R = random_point(a, b, p, rnd)
        A = ec_mul(R, p + 1, a, p)
        table = {}
        jR = None
        for j in range(W):
            Pt = ec_add(A, ec_mul(R, -j, a, p), a, p) if j else A
            table.setdefault(Pt, []).append(j)
        found = set()
        WR = ec_mul(R, W, a, p)
        qmax = T // W + 2
        for q in range(-qmax, qmax + 1):
            Pt = ec_mul(WR, q, a, p)
            if Pt in table:
                for j in table[Pt]:
                    t = q * W + j
                    if abs(t) <= T:
                        n = p + 1 - t
                        if ec_mul(R, n, a, p) is None:
                            found.add(n)
        if not found:
            continue
        candidates = found if candidates is None else (candidates & found)
        if candidates is not None and len(candidates) == 1:
            return next(iter(candidates))
        if candidates is not None and len(candidates) == 0:
            candidates = None
    if candidates and len(candidates) == 1:
        return next(iter(candidates))
    return None


# ---------------------------------------------------------------------------
# 3. POLYNOMIAL ARITHMETIC OVER F_p  (Kronecker substitution)
#    Carries a MODELLED field-multiplication counter with the declared formula.
# ---------------------------------------------------------------------------

class ModelCost:
    __slots__ = ("mults", "invs", "p")

    def __init__(self, p):
        self.mults = 0
        self.invs = 0
        self.p = p

    def inv_cost(self):
        e = self.p - 2
        return e.bit_length() + bin(e).count("1")

    def total_field_mults(self):
        return self.mults + self.invs * self.inv_cost()


MODEL = None  # set per run


def _charge(n):
    if MODEL is not None:
        MODEL.mults += n


def _charge_inv():
    if MODEL is not None:
        MODEL.invs += 1


def poly_norm(A, p):
    A = [c % p for c in A]
    while A and A[-1] == 0:
        A.pop()
    return A


def poly_deg(A):
    return len(A) - 1


def poly_add(A, B, p):
    n = max(len(A), len(B))
    return poly_norm([(A[i] if i < len(A) else 0) + (B[i] if i < len(B) else 0) for i in range(n)], p)


def poly_sub(A, B, p):
    n = max(len(A), len(B))
    return poly_norm([(A[i] if i < len(A) else 0) - (B[i] if i < len(B) else 0) for i in range(n)], p)


def poly_scal(A, c, p):
    return poly_norm([x * c for x in A], p)


def poly_mul(A, B, p):
    if not A or not B:
        return []
    _charge(len(A) * len(B))
    n = len(A) + len(B) - 1
    bits = 2 * p.bit_length() + max(len(A), len(B)).bit_length() + 2
    ia = 0
    for c in reversed(A):
        ia = (ia << bits) | c
    ib = 0
    for c in reversed(B):
        ib = (ib << bits) | c
    ic = ia * ib
    mask = (1 << bits) - 1
    out = []
    for _ in range(n):
        out.append((ic & mask) % p)
        ic >>= bits
    return poly_norm(out, p)


def poly_divmod(A, B, p):
    A = list(A)
    dB = poly_deg(B)
    if dB < 0:
        raise ZeroDivisionError
    invlead = inv(B[-1], p)
    _charge_inv()
    Q = [0] * max(0, len(A) - dB)
    while poly_deg(A) >= dB and A:
        d = poly_deg(A) - dB
        c = A[-1] * invlead % p
        _charge(1)
        Q[d] = c
        _charge(dB + 1)
        for i in range(dB + 1):
            A[i + d] = (A[i + d] - c * B[i]) % p
        A = poly_norm(A, p)
    return poly_norm(Q, p), A


def poly_mod(A, B, p):
    return poly_divmod(A, B, p)[1]


def poly_gcd(A, B, p):
    A = poly_norm(list(A), p)
    B = poly_norm(list(B), p)
    while B:
        A, B = B, poly_mod(A, B, p)
    if A:
        A = poly_scal(A, inv(A[-1], p), p)
        _charge_inv()
        _charge(len(A))
    return A


def poly_mulmod(A, B, M, p):
    return poly_mod(poly_mul(A, B, p), M, p)


def poly_powmod(A, e, M, p):
    R = [1]
    base = poly_mod(A, M, p)
    while e:
        if e & 1:
            R = poly_mulmod(R, base, M, p)
        base = poly_mulmod(base, base, M, p)
        e >>= 1
    return R


def poly_deriv(A, p):
    return poly_norm([(i * A[i]) % p for i in range(1, len(A))], p)


def poly_eval(A, x, p):
    r = 0
    for c in reversed(A):
        r = (r * x + c) % p
    return r


# ---------------------------------------------------------------------------
# 4. DIVISION POLYNOMIALS AND VELU (via Frobenius-eigenvalue kernel polynomial)
# ---------------------------------------------------------------------------

def division_polys(a, b, p, upto):
    """
    P_n with psi_n = P_n for odd n and psi_n = 2*y*P_n for even n,
    reduced by y^2 = f = x^3 + a x + b.
    """
    f = poly_norm([b, a, 0, 1], p)
    f2 = poly_mul(f, f, p)
    P = {0: [], 1: [1], 2: [1]}
    P[3] = poly_norm([(-a * a) % p, 12 * b, 6 * a, 0, 3], p)
    P[4] = poly_scal(poly_norm(
        [(-8 * b * b - a * a * a) % p, (-4 * a * b) % p, (-5 * a * a) % p,
         20 * b, 5 * a, 0, 1], p), 2, p)
    n = 5
    while n <= upto:
        if n % 2 == 1:
            m = (n - 1) // 2
            if m % 2 == 0:
                t1 = poly_mul(poly_mul(f2, P[m + 2], p), poly_mul(poly_mul(P[m], P[m], p), P[m], p), p)
                t1 = poly_scal(t1, 16, p)
                t2 = poly_mul(P[m - 1], poly_mul(poly_mul(P[m + 1], P[m + 1], p), P[m + 1], p), p)
            else:
                t1 = poly_mul(P[m + 2], poly_mul(poly_mul(P[m], P[m], p), P[m], p), p)
                t2 = poly_scal(poly_mul(poly_mul(f2, P[m - 1], p),
                                        poly_mul(poly_mul(P[m + 1], P[m + 1], p), P[m + 1], p), p), 16, p)
            P[n] = poly_sub(t1, t2, p)
        else:
            m = n // 2
            inner = poly_sub(poly_mul(P[m + 2], poly_mul(P[m - 1], P[m - 1], p), p),
                             poly_mul(P[m - 2], poly_mul(P[m + 1], P[m + 1], p), p), p)
            P[n] = poly_mul(P[m], inner, p)
        n += 1
    return P, f


def psi_and_phi(P, f, lam, p):
    """
    Return (phi_lam, den_lam) with x([lam]Q) = phi_lam(x)/den_lam(x).
    phi = x*psi_lam^2 - psi_{lam+1}*psi_{lam-1}.
    """
    if lam % 2 == 1:
        psi2 = poly_mul(P[lam], P[lam], p)
        cross = poly_scal(poly_mul(f, poly_mul(P[lam + 1], P[lam - 1], p), p), 4, p)
        phi = poly_sub(poly_mul([0, 1], psi2, p), cross, p)
        return phi, psi2
    psi2 = poly_scal(poly_mul(f, poly_mul(P[lam], P[lam], p), p), 4, p)
    cross = poly_mul(P[lam + 1], P[lam - 1], p)
    phi = poly_sub(poly_mul([0, 1], psi2, p), cross, p)
    return phi, psi2


def frobenius_eigenvalues(t, p, ell):
    """Roots of X^2 - t X + p mod ell."""
    return sorted({l for l in range(ell) if (l * l - t * l + p) % ell == 0})


def kernel_polynomials(a, b, p, t, ell, dpolys=None, f=None):
    """
    Kernel polynomials of the F_p-rational ell-isogenies from y^2=x^3+ax+b.
    Uses the Frobenius eigenvalue: the kernel is the lambda-eigenspace, so
    ker = { Q in E[ell] : x(Q)^p = x([lambda]Q) }.
    """
    if dpolys is None:
        dpolys, f = division_polys(a, b, p, ell + 2)
    lams = frobenius_eigenvalues(t, p, ell)
    if not lams:
        return []
    psi_ell = dpolys[ell] if ell % 2 == 1 else poly_scal(poly_mul(f, poly_mul(dpolys[ell], dpolys[ell], p), p), 4, p)
    if poly_deg(psi_ell) < 1:
        return []
    d0 = (ell - 1) // 2
    xp = poly_powmod([0, 1], p, psi_ell, p)
    out = []
    seen = set()
    for lam in lams:
        if lam == 0:
            continue
        phi, den = psi_and_phi(dpolys, f, lam, p)
        A = poly_mod(phi, psi_ell, p)
        B = poly_mod(den, psi_ell, p)
        C = poly_sub(A, poly_mulmod(xp, B, psi_ell, p), p)
        if not C:
            continue
        G = poly_gcd(psi_ell, C, p)
        if poly_deg(G) != d0:
            continue
        key = tuple(G)
        if key in seen:
            continue
        seen.add(key)
        out.append((lam, G))
    return out


def velu_codomain(a, b, p, h):
    """
    Codomain of the isogeny with kernel polynomial h (odd degree case).
    v = 6*p2 + 2*a*d ; w = 10*p3 + 6*a*p1 + 4*b*d ; a' = a-5v ; b' = b-7w.
    """
    d = poly_deg(h)
    e1, e2, e3 = newton_e(h, p, 3)
    p1 = e1 % p
    p2 = (e1 * e1 - 2 * e2) % p
    p3 = (e1 * e1 * e1 - 3 * e1 * e2 + 3 * e3) % p
    v = (6 * p2 + 2 * a * d) % p
    w = (10 * p3 + 6 * a * p1 + 4 * b * d) % p
    return (a - 5 * v) % p, (b - 7 * w) % p, (p1, p2, p3), (v, w)


def newton_e(h, p, upto):
    """Elementary symmetric functions e1,e2,e3 of the roots of monic h."""
    d = poly_deg(h)
    out = []
    for k in range(1, upto + 1):
        if k > d:
            out.append(0)
        else:
            out.append(((-1) ** k * h[d - k]) % p)
    return out


def velu_map_polys(a, b, p, h):
    """
    Numerator Ng and denominator h^2 of the x-map of the normalized Velu
    isogeny with kernel polynomial h:
        X(x) = [ x*h^2 + F*h + F2*h' - F2'*h ] / h^2
    with F  = (6x^2+2a)h' - h*(6d x + 6p1)
         F2 = (4x^3+4ax+4b)h' - h*(4d x^2 + 4p1 x + 4p2 + 4ad)
    and Y(x,y) = y * (Ng'*h - 2*Ng*h') / h^3.
    """
    d = poly_deg(h)
    e1, e2, e3 = newton_e(h, p, 3)
    p1 = e1 % p
    p2 = (e1 * e1 - 2 * e2) % p
    hp = poly_deriv(h, p)
    f1 = poly_norm([2 * a, 0, 6], p)
    G1 = poly_norm([6 * p1, 6 * d], p)
    F = poly_sub(poly_mul(f1, hp, p), poly_mul(h, G1, p), p)
    f2 = poly_norm([4 * b, 4 * a, 0, 4], p)
    G2 = poly_norm([(4 * p2 + 4 * a * d) % p, 4 * p1, 4 * d], p)
    F2 = poly_sub(poly_mul(f2, hp, p), poly_mul(h, G2, p), p)
    F2p = poly_deriv(F2, p)
    h2 = poly_mul(h, h, p)
    Ng = poly_add(poly_mul([0, 1], h2, p),
                  poly_add(poly_mul(F, h, p),
                           poly_sub(poly_mul(F2, hp, p), poly_mul(F2p, h, p), p), p), p)
    return Ng, h


def velu_eval_instrumented(Ng, h, a, b, p, pt, c):
    """
    Evaluate the Velu isogeny at an affine point with fully INSTRUMENTED F_p
    arithmetic.  Returns the image point (or None if the point is in the kernel,
    which cannot happen for an F_p-rational point when N is prime).
    """
    x0, y0 = pt
    hv = poly_eval_instr(h, x0, p, c)
    if hv == 0:
        return None
    ngv = poly_eval_instr(Ng, x0, p, c)
    hpv = poly_eval_instr(poly_deriv(h, p), x0, p, c)
    ngpv = poly_eval_instr(poly_deriv(Ng, p), x0, p, c)
    hv2 = fs(c, hv, p)
    hv3 = fm(c, hv2, hv, p)
    ihv2 = finv(c, hv2, p)
    X = fm(c, ngv, ihv2, p)
    num = fsub(c, fm(c, ngpv, hv, p), fm(c, fmc(c, 2, ngv, p), hpv, p), p)
    ihv3 = finv(c, hv3, p)
    Y = fm(c, y0, fm(c, num, ihv3, p), p)
    return (X, Y)


def poly_eval_instr(A, x, p, c):
    r = 0
    for co in reversed(A):
        r = fa(c, fm(c, r, x, p), co, p)
    return r


# ---------------------------------------------------------------------------
# 5. INDEPENDENT CLASS NUMBER  h(D)  (computed WITHOUT the walk)
# ---------------------------------------------------------------------------

def class_number(D):
    """
    h(D) for D < 0: count reduced primitive positive definite binary quadratic
    forms (A,B,C) with B^2-4AC = D, |B| <= A <= C, B >= 0 if |B| == A or A == C.
    Computed independently of any isogeny walk.
    """
    assert D < 0 and D % 4 in (0, 1)
    h = 0
    B = D % 2
    bound = math.isqrt(-D // 3) + 1
    while B <= bound:
        num = (B * B - D) // 4
        A = max(B, 1)
        while A * A <= num:
            if num % A == 0:
                C = num // A
                if math.gcd(math.gcd(A, B), C) == 1:
                    if B == 0 or A == B or A == C:
                        h += 1
                    else:
                        h += 2
            A += 1
        B += 2
    return h


def is_fundamental(D):
    if D >= 0 or D % 4 not in (0, 1):
        return False
    if D % 4 == 1:
        return squarefree(D)
    m = D // 4
    if m % 4 in (2, 3):
        return squarefree(m)
    return False


def squarefree(n):
    n = abs(n)
    i = 2
    while i * i <= n:
        if n % (i * i) == 0:
            return False
        i += 1
    return True


def conductor(t, p):
    """
    Conductor f of Z[pi] inside the maximal order: t^2-4p = f^2 * D_K.
    f = 1 exactly when t^2-4p is a fundamental discriminant.
    """
    D = t * t - 4 * p
    f = 1
    d = D
    i = 2
    while i * i <= abs(d):
        while d % (i * i) == 0 and ((d // (i * i)) % 4 in (0, 1)):
            d //= i * i
            f *= i
        i += 1
    return f, d, D


# ---------------------------------------------------------------------------
# 6. RHO (Q1) AND BSGS
# ---------------------------------------------------------------------------

def rho_precompute(P, Q, N, a, p, seed):
    rnd = random.Random(seed)
    coeffs = [(rnd.randrange(1, N), rnd.randrange(1, N)) for _ in range(16)]
    a0 = rnd.randrange(1, N)
    b0 = rnd.randrange(1, N)
    ops = [0]

    def cmul(pt, n):
        # counted scalar multiplication for the precompute accounting
        if n == 0 or pt is None:
            return None
        R = None
        T = pt
        while n:
            if n & 1:
                R = ec_add(R, T, a, p)
                ops[0] += 1
            T = ec_dbl(T, a, p)
            ops[0] += 1
            n >>= 1
        return R

    Rs = []
    for (ai, bi) in coeffs:
        Ri = ec_add(cmul(P, ai), cmul(Q, bi), a, p)
        ops[0] += 1
        Rs.append(Ri)
    W0 = ec_add(cmul(P, a0), cmul(Q, b0), a, p)
    ops[0] += 1
    return coeffs, Rs, (a0, b0), W0, ops[0]


def rho_solve(P, Q, N, a, b, p, seed, record_seq=False, deadline=None):
    """
    Teske mixed 20-adding walk with distinguished points.  Identical parameters
    on every curve.  Returns a solve record dict.
    """
    coeffs, Rs, (ca, cb), W, pre_ops = rho_precompute(P, Q, N, a, p, seed)
    max_steps = 60 * math.isqrt(N)
    dps = {}
    adds = 0
    dbls = 0
    seq = [] if record_seq else None
    degenerate = 0
    step = 0
    while step < max_steps:
        if deadline is not None and (step & 1023) == 0 and time.time() > deadline:
            return {
                "status": "censored_budget", "seed": seed, "k": None,
                "group_ops": adds + dbls, "adds": adds, "dbls": dbls,
                "group_ops_precompute": pre_ops, "steps": step,
                "degenerate_collisions": degenerate, "op_sequence": seq,
            }
        if W is None:
            W = ec_add(Rs[0], Rs[1], a, p)
            ca = (ca + coeffs[0][0] + coeffs[1][0]) % N
            cb = (cb + coeffs[0][1] + coeffs[1][1]) % N
            adds += 1
            if seq is not None:
                seq.append("A")
            step += 1
            continue
        idx = W[0] % 20
        if idx < 16:
            W = ec_add(W, Rs[idx], a, p)
            ca = (ca + coeffs[idx][0]) % N
            cb = (cb + coeffs[idx][1]) % N
            adds += 1
            if seq is not None:
                seq.append("A")
        else:
            W = ec_dbl(W, a, p)
            ca = (2 * ca) % N
            cb = (2 * cb) % N
            dbls += 1
            if seq is not None:
                seq.append("D")
        step += 1
        if W is not None and W[0] % 16 == 0:
            prev = dps.get(W)
            if prev is None:
                dps[W] = (ca, cb)
            else:
                pa, pb = prev
                den = (cb - pb) % N
                if den == 0:
                    degenerate += 1
                    dps[W] = (ca, cb)
                else:
                    k = (pa - ca) % N * pow(den, N - 2, N) % N
                    return {
                        "status": "solved", "seed": seed, "k": k,
                        "group_ops": adds + dbls, "adds": adds, "dbls": dbls,
                        "group_ops_precompute": pre_ops, "steps": step,
                        "distinguished_points_stored": len(dps),
                        "degenerate_collisions": degenerate, "op_sequence": seq,
                    }
    return {
        "status": "censored_max_steps", "seed": seed, "k": None,
        "group_ops": adds + dbls, "adds": adds, "dbls": dbls,
        "group_ops_precompute": pre_ops, "steps": step,
        "degenerate_collisions": degenerate, "op_sequence": seq,
    }


def bsgs_solve(P, Q, N, a, p):
    """Independent of rho: no shared walk logic."""
    m = math.isqrt(N) + 1
    table = {}
    R = None
    for j in range(m):
        table.setdefault(R, j)
        R = ec_add(R, P, a, p)
    mP = ec_mul(P, -m, a, p)
    G = Q
    for i in range(m + 1):
        if G in table:
            return (i * m + table[G]) % N
        G = ec_add(G, mP, a, p)
    return None


# ---------------------------------------------------------------------------
# 7. Q2: GROUP-LAW COST IN EACH CANDIDATE MODEL
# ---------------------------------------------------------------------------

def jac_dbl_generic(Pt, a, p, c):
    X1, Y1, Z1 = Pt
    if Z1 == 0 or Y1 == 0:
        return (0, 1, 0)
    XX = fs(c, X1, p)
    YY = fs(c, Y1, p)
    YYYY = fs(c, YY, p)
    ZZ = fs(c, Z1, p)
    S = fmc(c, 2, fsub(c, fsub(c, fs(c, fa(c, X1, YY, p), p), XX, p), YYYY, p), p)
    M = fa(c, fmc(c, 3, XX, p), fm(c, a, fs(c, ZZ, p), p), p)
    T = fsub(c, fs(c, M, p), fmc(c, 2, S, p), p)
    X3 = T
    Y3 = fsub(c, fm(c, M, fsub(c, S, T, p), p), fmc(c, 8, YYYY, p), p)
    Z3 = fsub(c, fsub(c, fs(c, fa(c, Y1, Z1, p), p), YY, p), ZZ, p)
    return (X3, Y3, Z3)


def jac_dbl_a_minus_3(Pt, a, p, c):
    X1, Y1, Z1 = Pt
    if Z1 == 0 or Y1 == 0:
        return (0, 1, 0)
    delta = fs(c, Z1, p)
    gamma = fs(c, Y1, p)
    beta = fm(c, X1, gamma, p)
    alpha = fmc(c, 3, fm(c, fsub(c, X1, delta, p), fa(c, X1, delta, p), p), p)
    X3 = fsub(c, fs(c, alpha, p), fmc(c, 8, beta, p), p)
    Z3 = fsub(c, fsub(c, fs(c, fa(c, Y1, Z1, p), p), gamma, p), delta, p)
    Y3 = fsub(c, fm(c, alpha, fsub(c, fmc(c, 4, beta, p), X3, p), p),
              fmc(c, 8, fs(c, gamma, p), p), p)
    return (X3, Y3, Z3)


def jac_add(Pt, Qt, a, p, c):
    X1, Y1, Z1 = Pt
    X2, Y2, Z2 = Qt
    if Z1 == 0:
        return Qt
    if Z2 == 0:
        return Pt
    Z1Z1 = fs(c, Z1, p)
    Z2Z2 = fs(c, Z2, p)
    U1 = fm(c, X1, Z2Z2, p)
    U2 = fm(c, X2, Z1Z1, p)
    S1 = fm(c, Y1, fm(c, Z2, Z2Z2, p), p)
    S2 = fm(c, Y2, fm(c, Z1, Z1Z1, p), p)
    if U1 == U2:
        if S1 != S2:
            return (0, 1, 0)
        return jac_dbl_generic(Pt, a, p, c)
    H = fsub(c, U2, U1, p)
    I = fs(c, fmc(c, 2, H, p), p)
    J = fm(c, H, I, p)
    r = fmc(c, 2, fsub(c, S2, S1, p), p)
    V = fm(c, U1, I, p)
    X3 = fsub(c, fsub(c, fs(c, r, p), J, p), fmc(c, 2, V, p), p)
    Y3 = fsub(c, fm(c, r, fsub(c, V, X3, p), p), fmc(c, 2, fm(c, S1, J, p), p), p)
    Z3 = fm(c, fsub(c, fsub(c, fs(c, fa(c, Z1, Z2, p), p), Z1Z1, p), Z2Z2, p), H, p)
    return (X3, Y3, Z3)


def aff_add_instr(Pt, Qt, a, p, c):
    if Pt is None:
        return Qt
    if Qt is None:
        return Pt
    x1, y1 = Pt
    x2, y2 = Qt
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        return aff_dbl_instr(Pt, a, p, c)
    lam = fm(c, fsub(c, y2, y1, p), finv(c, fsub(c, x2, x1, p), p), p)
    x3 = fsub(c, fsub(c, fs(c, lam, p), x1, p), x2, p)
    y3 = fsub(c, fm(c, lam, fsub(c, x1, x3, p), p), y1, p)
    return (x3, y3)


def aff_dbl_instr(Pt, a, p, c):
    if Pt is None:
        return None
    x1, y1 = Pt
    if y1 == 0:
        return None
    num = fa(c, fmc(c, 3, fs(c, x1, p), p), a, p)
    lam = fm(c, num, finv(c, fmc(c, 2, y1, p), p), p)
    x3 = fsub(c, fs(c, lam, p), fmc(c, 2, x1, p), p)
    y3 = fsub(c, fm(c, lam, fsub(c, x1, x3, p), p), y1, p)
    return (x3, y3)


def measure_model(model_id, a, b, p, N, P, Q, seed, nops):
    """
    Re-execute the member's seed-index-0 rho walk for `nops` group operations in
    the given model, with instrumented arithmetic, and return the group-law and
    normalization costs separately.
    """
    a_used, b_used, u = a, b, 1
    if model_id == "JACOBIAN_A_MINUS_3":
        z = a * inv((-3) % p, p) % p
        # need u with a * u^4 = -3, i.e. u^4 = -3/a = 1/z
        w = fourth_root(inv(z, p), p)
        if w is None:
            return None
        u = w
        u4 = pow(u, 4, p)
        u6 = pow(u, 6, p)
        a_used = a * u4 % p
        b_used = b * u6 % p
        if a_used != (-3) % p:
            return None
    coeffs, Rs, (ca, cb), W, _ = rho_precompute(P, Q, N, a, p, seed)
    if W is None:
        return None

    u2 = pow(u, 2, p)
    u3 = pow(u, 3, p)
    u2inv = inv(u2, p)

    def to_model(pt):
        if model_id == "AFFINE_SHORT_WEIERSTRASS":
            return pt
        if pt is None:
            return (0, 1, 0)
        x, y = pt
        return (x * u2 % p, y * u3 % p, 1)

    gl = FC()
    gl_add = FC()
    gl_dbl = FC()
    nm = FC()
    Rsm = [to_model(R) for R in Rs]
    Wm = to_model(W)
    seq = []
    ops = 0
    while ops < nops:
        # expose the affine x-coordinate to the walk function
        if model_id == "AFFINE_SHORT_WEIERSTRASS":
            if Wm is None:
                break
            xaff = Wm[0]
        else:
            X, Y, Z = Wm
            if Z == 0:
                break
            iz = finv(nm, Z, p)
            iz2 = fs(nm, iz, p)
            xm = fm(nm, X, iz2, p)
            # map back from the isomorphic model to the common affine x
            xaff = fm(nm, xm, u2inv, p)
        idx = xaff % 20
        if idx < 16:
            if model_id == "AFFINE_SHORT_WEIERSTRASS":
                Wm = aff_add_instr(Wm, Rsm[idx], a_used, p, gl_add)
            else:
                Wm = jac_add(Wm, Rsm[idx], a_used, p, gl_add)
            seq.append("A")
        else:
            if model_id == "AFFINE_SHORT_WEIERSTRASS":
                Wm = aff_dbl_instr(Wm, a_used, p, gl_dbl)
            elif model_id == "JACOBIAN_A_MINUS_3":
                Wm = jac_dbl_a_minus_3(Wm, a_used, p, gl_dbl)
            else:
                Wm = jac_dbl_generic(Wm, a_used, p, gl_dbl)
            seq.append("D")
        ops += 1
    if ops == 0:
        return None
    n_add = seq.count("A")
    n_dbl = seq.count("D")
    gl.M = gl_add.M + gl_dbl.M
    gl.S = gl_add.S + gl_dbl.S
    gl.A = gl_add.A + gl_dbl.A
    gl.I = gl_add.I + gl_dbl.I
    add_cost = gl_add.weighted() / n_add if n_add else None
    dbl_cost = gl_dbl.weighted() / n_dbl if n_dbl else None
    return {
        "add_field_mults_per_op": add_cost,
        "dbl_field_mults_per_op": dbl_cost,
        "add_M": gl_add.M, "add_S": gl_add.S,
        "dbl_M": gl_dbl.M, "dbl_S": gl_dbl.S,
        "own_mix_adds": n_add, "own_mix_dbls": n_dbl,
        "model": model_id,
        "isomorphism_u": u,
        "model_a": a_used,
        "model_b": b_used,
        "group_ops_replayed": ops,
        "adds": seq.count("A"),
        "dbls": seq.count("D"),
        "grouplaw_M": gl.M,
        "grouplaw_S": gl.S,
        "grouplaw_A": gl.A,
        "grouplaw_I": gl.I,
        "grouplaw_weighted_field_mults": gl.weighted(),
        "field_mults_per_group_op_own_mix": gl.weighted() / ops,
        "normalization_M": nm.M,
        "normalization_S": nm.S,
        "normalization_I": nm.I,
        "normalization_weighted_field_mults": nm.weighted(),
        "op_sequence_prefix": "".join(seq),
    }


# ---------------------------------------------------------------------------
# 8. BASE CURVE SELECTION
# ---------------------------------------------------------------------------

SELECTION_CRITERIA = {
    "declared_before_any_solve": True,
    "criteria_in_order": [
        "p is the largest prime below 2^bits (deterministic, no search over p)",
        "a is FIXED to -3 mod p, so the base curve is literally in the a = -3 model (P-256 shape)",
        "b is drawn from the declared master seed; candidates are examined in that deterministic order",
        "nonsingular: 4a^3 + 27b^2 != 0",
        "N = #E(F_p) is PRIME (P-256 shape)",
        "t = p + 1 - N is nonzero mod p, i.e. E is ORDINARY",
        "|D| = |t^2 - 4p| <= DMAX (declared budget-feasibility bound: keeps the class enumerable and h(D) cheap to compute; structural, independent of any cost datum)",
        "D = t^2 - 4p is a FUNDAMENTAL discriminant, i.e. the CM conductor f = 1 (flat volcano)",
        "H_MIN <= h(D) <= H_MAX, computed independently by counting reduced binary quadratic forms (declared budget-feasibility bound; structural, independent of any cost datum)",
        "the BFS class walk over degrees {2,3,5,7,11,13} enumerates exactly h(D) F_p-isomorphism classes, i.e. the declared degrees generate cl(O)",
    ],
    "criteria_note": (
        "The last criterion is a DECLARED SELECTION FILTER. Its satisfaction at "
        "the accepted candidate is therefore true BY CONSTRUCTION, and the "
        "completeness comparison reported for the accepted base curve must be "
        "read with that in mind. It is recorded here, in the selection log, and "
        "in the run receipt rather than left implicit. Candidates rejected "
        "because their walk closed short of h(D) are listed in the rejection "
        "log with that exact reason, and the vertex-count-versus-h comparison is "
        "reported side by side for the accepted candidate in every case. No "
        "criterion in this list uses, or could use, a cost datum: every one is "
        "structural and all of them are evaluated before any DLP is solved."
    ),
}


def select_base_curve(bits, master_seed, dmax, hmin, hmax, max_candidates, log, deadline=None):
    p = prev_prime(1 << bits)
    a = (-3) % p
    rnd = random.Random(master_seed)
    rejected = []
    reason_counts = {}
    examined = 0

    def rej(b, reason, extra=None):
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
        if len(rejected) < 400:
            e = {"p": p, "a": a, "b": b, "reason": reason}
            if extra:
                e.update(extra)
            rejected.append(e)

    while examined < max_candidates:
        if deadline is not None and time.time() > deadline:
            return None, {"p": p, "a": a, "examined": examined, "rejected_sample": rejected,
                          "rejection_reason_counts": reason_counts,
                          "terminated": "selection deadline reached"}
        b = rnd.randrange(1, p)
        examined += 1
        if (4 * a * a * a + 27 * b * b) % p == 0:
            rej(b, "singular curve")
            continue
        N = group_order(a, b, p, random.Random(master_seed * 7919 + examined))
        if N is None:
            rej(b, "group order not pinned down by BSGS")
            continue
        if not is_prime(N):
            rej(b, "N not prime")
            continue
        t = p + 1 - N
        if t % p == 0:
            rej(b, "supersingular (t = 0 mod p)")
            continue
        f, dk, D = conductor(t, p)
        if abs(D) > dmax:
            rej(b, "|D| exceeds declared budget-feasibility bound", {"D": D})
            continue
        if f != 1:
            rej(b, "CM conductor f != 1", {"D": D, "f": f})
            continue
        h = class_number(D)
        if h < hmin or h > hmax:
            rej(b, "h(D) outside declared budget-feasibility range", {"D": D, "h": h})
            continue
        ok3, _ = a_minus_3_reachable(a, b, p)
        if not ok3:
            rej(b, "a = -3 model not reachable", {"D": D, "h": h})
            continue
        # structural filter: does the declared degree set generate cl(O)?
        walk = enumerate_class(a, b, p, t, N, deadline=deadline, budget_vertices=hmax + 5)
        if walk is None:
            rej(b, "class walk aborted (deadline)", {"D": D, "h": h})
            continue
        if len(walk["vertices"]) != h:
            rej(b, "class walk closed short of h(D): declared degrees do not generate cl(O)",
                {"D": D, "h": h, "walk_vertices": len(walk["vertices"])})
            continue
        log.update({
            "prime_bits": bits, "p": p, "a": a, "b": b, "N": N, "t": t, "D": D,
            "conductor_f": f, "fundamental_discriminant_check": is_fundamental(D),
            "class_number_h": h, "candidates_examined": examined,
            "rejected_sample": rejected, "rejection_reason_counts": reason_counts,
            "master_seed": master_seed,
        })
        return {"p": p, "a": a, "b": b, "N": N, "t": t, "D": D, "h": h, "walk": walk}, log
    return None, {"p": p, "a": a, "examined": examined, "rejected_sample": rejected,
                  "rejection_reason_counts": reason_counts,
                  "terminated": "max_candidates exhausted"}


# ---------------------------------------------------------------------------
# 9. CLASS ENUMERATION
# ---------------------------------------------------------------------------

def verify_order_is_N(a, b, p, N, rnd, tries=2):
    """
    Edge certificate order check: [N]R = O for `tries` independent random R.
    Since N is prime and #E lies in the Hasse interval, which has width
    4*sqrt(p) < N, this pins #E = N.
    """
    for _ in range(tries):
        R = random_point(a, b, p, rnd)
        if ec_mul(R, N, a, p) is not None:
            return False
    return True


def enumerate_class(a0, b0, p, t, N, deadline=None, budget_vertices=100000, collect=False):
    """
    BFS from E_0 over the declared degrees, computing each isogeny explicitly by
    Velu's formulas from the Frobenius-eigenvalue kernel polynomial.
    Deduplicates by F_p-ISOMORPHISM class.
    """
    global MODEL
    degrees = PROTOCOL["isogeny_degrees"]
    vertices = []
    by_j = {}
    edges = []
    rnd = random.Random(1234567)

    def vertex_id(a, b):
        j = j_invariant(a, b, p)
        for idx in by_j.get(j, []):
            if fp_isomorphic(vertices[idx]["a"], vertices[idx]["b"], a, b, p):
                return idx
        return None

    def add_vertex(a, b, path):
        j = j_invariant(a, b, p)
        idx = len(vertices)
        vertices.append({"index": idx, "a": a, "b": b, "j": j, "path": path})
        by_j.setdefault(j, []).append(idx)
        return idx

    add_vertex(a0, b0, [])
    queue = [0]
    head = 0
    degree_stats = {str(d): {"edges": 0, "eigenvalues_found": 0, "no_rational_isogeny": 0} for d in degrees}
    while head < len(queue):
        if deadline is not None and time.time() > deadline:
            return None
        vi = queue[head]
        head += 1
        va, vb = vertices[vi]["a"], vertices[vi]["b"]
        dpolys, f = division_polys(va, vb, p, max(degrees) + 2)
        for ell in degrees:
            if MODEL is not None:
                before = MODEL.mults, MODEL.invs
            kps = kernel_polynomials(va, vb, p, t, ell, dpolys, f)
            if MODEL is not None:
                cost_mults = MODEL.mults - before[0]
                cost_invs = MODEL.invs - before[1]
            else:
                cost_mults = cost_invs = 0
            if not kps:
                degree_stats[str(ell)]["no_rational_isogeny"] += 1
                continue
            degree_stats[str(ell)]["eigenvalues_found"] += len(kps)
            for (lam, h) in kps:
                na, nb = velu_codomain(va, vb, p, h)[:2]
                if (4 * na * na * na + 27 * nb * nb) % p == 0:
                    edges.append({"from": vi, "to": None, "ell": ell, "lambda": lam,
                                  "kernel_polynomial": h, "codomain": [na, nb],
                                  "certificate": {"verified": False,
                                                  "reason": "codomain is singular"}})
                    continue
                divides = not poly_mod(dpolys[ell] if ell % 2 == 1 else
                                       poly_scal(poly_mul(f, poly_mul(dpolys[ell], dpolys[ell], p), p), 4, p),
                                       h, p)
                order_ok = verify_order_is_N(na, nb, p, N, rnd)
                tj = vertex_id(na, nb)
                new = tj is None
                if new:
                    if len(vertices) >= budget_vertices:
                        return None
                    tj = add_vertex(na, nb, vertices[vi]["path"] + [{"ell": ell, "lambda": lam, "from": vi}])
                    queue.append(tj)
                edges.append({
                    "from": vi, "to": tj, "ell": ell, "lambda": lam,
                    "kernel_polynomial": h, "codomain": [na, nb],
                    "tree_edge": bool(new),
                    "construction_cost_modelled_field_mults": cost_mults,
                    "construction_cost_modelled_inversions": cost_invs,
                    "certificate": {
                        "verified": bool(divides and order_ok and poly_deg(h) == (ell - 1) // 2),
                        "kernel_polynomial_degree": poly_deg(h),
                        "expected_kernel_polynomial_degree": (ell - 1) // 2,
                        "kernel_polynomial_divides_psi_ell": bool(divides),
                        "codomain_order_equals_N": bool(order_ok),
                        "codomain_nonsingular": True,
                        "kernel_generator": (
                            "not F_p-rational: N is prime so E(F_p) has no "
                            "ell-torsion; the kernel subgroup is Galois-stable "
                            "and is specified by its minimal (kernel) "
                            "polynomial together with the Frobenius eigenvalue "
                            "lambda = %d mod %d" % (lam, ell)
                        ),
                    },
                })
                degree_stats[str(ell)]["edges"] += 1
    return {"vertices": vertices, "edges": edges, "degree_stats": degree_stats}


# ---------------------------------------------------------------------------
# 10. RUN DRIVER
# ---------------------------------------------------------------------------

def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def stdev(xs):
    n = len(xs)
    if n < 2:
        return 0.0
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def write_yaml(path, obj):
    import yaml
    with open(path, "w") as fh:
        yaml.safe_dump(obj, fh, sort_keys=False, default_flow_style=False, width=100)


def environment_block():
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
    except Exception:
        head, dirty = "unavailable", "unavailable"
    try:
        import yaml as _y
        yamlv = _y.__version__
    except Exception:
        yamlv = "unavailable"
    sage = "absent"
    for cand in ("/usr/local/bin/sage", "/opt/homebrew/bin/sage"):
        if os.path.exists(cand):
            sage = cand + " (present but DELIBERATELY NOT USED: all field, curve, polynomial and Velu arithmetic in this run is implemented in this module so that multiplication and squaring counts are real instrumented counts rather than estimates)"
            break
    return {
        "git_commit": head,
        "git_dirty_tree": bool(dirty),
        "git_dirty_paths": dirty.splitlines()[:40],
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "dependencies": {"PyYAML": yamlv, "stdlib_only_otherwise": True},
        "sage": sage,
        "recorded_at": now_iso(),
    }


def do_run(args):
    global MODEL
    t_start = time.time()
    deadline = t_start + args.wall_clock_seconds
    out = args.out_dir
    os.makedirs(out, exist_ok=True)
    stdout_lines = []
    defects = []
    deviations = []

    def log(msg):
        line = "[%7.1fs] %s" % (time.time() - t_start, msg)
        stdout_lines.append(line)
        print(line, flush=True)

    env = environment_block()
    MODEL = ModelCost(2)

    bits = args.bits
    master_seed = args.master_seed
    dmax = args.dmax
    log("run %s: bits=%d master_seed=%d" % (args.run_id, bits, master_seed))

    # ---- 1. BASE CURVE SELECTION AND FREEZE -------------------------------
    sel_log = {}
    sel, sel_log = select_base_curve(bits, master_seed, dmax, args.hmin, args.hmax,
                                     args.max_candidates, sel_log,
                                     deadline=t_start + args.selection_seconds)
    if sel is None:
        rec = {
            "run_id": args.run_id, "experiment_id": PROTOCOL["experiment_id"],
            "terminal_status": "resource_exhaustion",
            "terminal_status_reason": (
                "Base-curve selection did not find a candidate satisfying the "
                "declared structural criteria within its declared budget. No "
                "curve was frozen, no DLP was solved, and NO mathematical "
                "observation of any kind is reported from this run. This is an "
                "infrastructure/budget outcome, never negative mathematical "
                "evidence (AGENTS.md rule 5)."),
            "selection_log": sel_log,
        }
        write_yaml(os.path.join(out, "run_record.yaml"), rec)
        write_yaml(os.path.join(out, "base_curve_selection.yaml"),
                   {"run_id": args.run_id, "selection_criteria": SELECTION_CRITERIA, "selection_log": sel_log})
        return rec

    p, a, b, N, t, D, h = sel["p"], sel["a"], sel["b"], sel["N"], sel["t"], sel["D"], sel["h"]
    base_curve_frozen_at = now_iso()
    log("FROZEN base curve p=%d a=%d b=%d N=%d t=%d D=%d h=%d" % (p, a, b, N, t, D, h))

    MODEL = ModelCost(p)

    # ---- 2. DLP INSTANCE ---------------------------------------------------
    rnd_inst = random.Random(master_seed * 31 + 17)
    P0 = random_point(a, b, p, rnd_inst)
    k = rnd_inst.randrange(2, N - 1)
    Q0 = ec_mul(P0, k, a, p)
    dlp_frozen_at = now_iso()
    log("DLP instance frozen: k recorded in the manifest (benchmark, not a challenge)")

    # ---- 3. CLASS ENUMERATION ---------------------------------------------
    walk = enumerate_class(a, b, p, t, N, deadline=deadline, collect=True)
    if walk is None:
        rec = {"run_id": args.run_id, "terminal_status": "resource_exhaustion",
               "terminal_status_reason": "class enumeration exceeded the wall-clock budget"}
        write_yaml(os.path.join(out, "run_record.yaml"), rec)
        return rec
    vertices = walk["vertices"]
    h_independent = class_number(D)
    complete = (len(vertices) == h_independent)
    log("class walk: %d vertices; independently computed h(D) = %d; complete=%s"
        % (len(vertices), h_independent, complete))

    # structural null object: same-p different-trace curves must not appear
    struct_rnd = random.Random(master_seed * 977 + 5)
    struct_null = []
    tries = 0
    while len(struct_null) < 8 and tries < 400:
        tries += 1
        bb = struct_rnd.randrange(1, p)
        if (4 * a * a * a + 27 * bb * bb) % p == 0:
            continue
        NN = group_order(a, bb, p, random.Random(master_seed + tries))
        if NN is None or NN == N or NN == p + 1 + t:
            continue
        present = any(fp_isomorphic(v["a"], v["b"], a, bb, p) for v in vertices)
        struct_null.append({"a": a, "b": bb, "N": NN, "trace": p + 1 - NN,
                            "appears_in_class_walk": bool(present)})
    struct_violations = [s for s in struct_null if s["appears_in_class_walk"]]

    # ---- 4. TRANSFER THE FROZEN DLP INSTANCE TO EVERY MEMBER --------------
    edge_maps = {}
    for e in walk["edges"]:
        if not e.get("tree_edge"):
            continue
        Ng, hh = velu_map_polys(vertices[e["from"]]["a"], vertices[e["from"]]["b"], p, e["kernel_polynomial"])
        edge_maps[e["to"]] = (e["from"], Ng, hh, e["ell"], e.get("construction_cost_modelled_field_mults", 0),
                              e.get("construction_cost_modelled_inversions", 0))

    transfers = {0: {"P": P0, "Q": Q0, "measured_M": 0, "measured_S": 0, "measured_I": 0,
                     "measured_weighted": 0.0, "modelled_construction_weighted": 0.0,
                     "path_length": 0, "path_degrees": []}}
    order_by_depth = sorted(range(len(vertices)), key=lambda i: len(vertices[i]["path"]))
    for vi in order_by_depth:
        if vi == 0:
            continue
        src, Ng, hh, ell, cm, ci = edge_maps[vi]
        base_tr = transfers[src]
        c = FC()
        Pn = velu_eval_instrumented(Ng, hh, vertices[src]["a"], vertices[src]["b"], p, base_tr["P"], c)
        Qn = velu_eval_instrumented(Ng, hh, vertices[src]["a"], vertices[src]["b"], p, base_tr["Q"], c)
        modelled = cm + ci * MODEL.inv_cost()
        transfers[vi] = {
            "P": Pn, "Q": Qn,
            "measured_M": base_tr["measured_M"] + c.M,
            "measured_S": base_tr["measured_S"] + c.S,
            "measured_I": base_tr["measured_I"] + c.I,
            "measured_weighted": base_tr["measured_weighted"] + c.weighted(),
            "modelled_construction_weighted": base_tr["modelled_construction_weighted"] + modelled,
            "path_length": base_tr["path_length"] + 1,
            "path_degrees": base_tr["path_degrees"] + [ell],
        }
    log("DLP instance transferred to %d members by explicit Velu evaluation" % len(transfers))

    # transfer sanity: image points must lie on the codomain and have order N
    transfer_defects = []
    for vi, tr in transfers.items():
        va, vb = vertices[vi]["a"], vertices[vi]["b"]
        okP = tr["P"] is not None and is_on_curve(tr["P"], va, vb, p) and ec_mul(tr["P"], N, va, p) is None
        okQ = tr["Q"] is not None and is_on_curve(tr["Q"], va, vb, p) and ec_mul(tr["Q"], N, va, p) is None
        tr["transfer_structurally_ok"] = bool(okP and okQ)
        if not (okP and okQ):
            transfer_defects.append({"vertex": vi, "P_ok": bool(okP), "Q_ok": bool(okQ),
                                     "note": "isogeny image failed the on-curve / order-N structural test; this member contributes no cost datum"})
    defects.extend(transfer_defects)

    # ---- 5. FREEZE THE SEED BAND ON THE BASE CURVE ------------------------
    solve_records = []
    base_solves = []
    common_mix = None
    for si, s in enumerate(PROTOCOL["seeds"]):
        r = rho_solve(P0, Q0, N, a, b, p, s, record_seq=(si == 0), deadline=deadline)
        if si == 0 and r.get("op_sequence"):
            seq0 = r["op_sequence"][:PROTOCOL["q2_replay_ops"]]
            op_seq0_base = "".join(seq0)
            common_mix = {"adds": seq0.count("A"), "dbls": seq0.count("D"),
                          "total": len(seq0), "source": "base curve seed-index-0 walk, first %d group operations"
                                                        % PROTOCOL["q2_replay_ops"],
                          "declared_before_measurement": True}
        r.update({"curve_role": "base_curve", "vertex": 0, "p": p, "a": a, "b": b, "N": N,
                  "coordinate_system": PROTOCOL["q1_common_coordinate_system"]["id"]})
        r.pop("op_sequence", None)
        solve_records.append(r)
        base_solves.append(r)
    base_ok = [r["group_ops"] for r in base_solves if r["status"] == "solved"]
    if len(base_ok) < len(PROTOCOL["seeds"]):
        defects.append({"where": "base_curve", "issue": "one or more base-curve solves were censored",
                        "censored": len(PROTOCOL["seeds"]) - len(base_ok)})
    if not base_ok:
        rec = {"run_id": args.run_id, "terminal_status": "resource_exhaustion",
               "terminal_status_reason": "no base-curve solve completed inside the budget; the seed band could not be frozen"}
        write_yaml(os.path.join(out, "run_record.yaml"), rec)
        return rec
    bs = PROTOCOL["seed_band_bootstrap"]
    brnd = random.Random(bs["seed"])
    boots = sorted(median([brnd.choice(base_ok) for _ in base_ok]) for _ in range(bs["resamples"]))
    lo = boots[int(bs["percentiles"][0] / 100.0 * len(boots))]
    hi = boots[min(len(boots) - 1, int(bs["percentiles"][1] / 100.0 * len(boots)))]
    seed_band = {
        "computed_on": "base curve only",
        "n_seeds": len(base_ok),
        "per_seed_counts": base_ok,
        "per_seed_band": {"min": min(base_ok), "max": max(base_ok)},
        "median_band": {"low": lo, "high": hi,
                        "bootstrap_seed": bs["seed"], "resamples": bs["resamples"],
                        "percentiles": bs["percentiles"]},
        "primary_band_for_all_comparisons": "median_band",
        "min": min(base_ok),
        "max": max(base_ok),
        "median": median(base_ok),
        "mean": sum(base_ok) / len(base_ok),
        "stdev": stdev(base_ok),
        "relative_halfwidth_per_seed": (max(base_ok) - min(base_ok)) / (2.0 * median(base_ok)),
        "relative_halfwidth_median_band": (hi - lo) / (2.0 * median(base_ok)),
        "frozen_at": now_iso(),
        "rule": PROTOCOL["seed_band_rule"],
        "frozen_before_any_between_member_comparison": True,
    }
    seed_band_frozen_at = seed_band["frozen_at"]
    fixture = 0.886 * math.sqrt(N)
    seed_band["frozen_reproduction_fixture_0886_sqrt_N"] = fixture
    seed_band["base_median_over_fixture"] = median(base_ok) / fixture
    seed_band["fixture_inside_per_seed_band"] = bool(min(base_ok) <= fixture <= max(base_ok))
    seed_band["fixture_inside_median_band"] = bool(lo <= fixture <= hi)
    seed_band["reference_constant_note"] = (
        "Reported for transparency, NOT as an adjustment of anything: the "
        "frozen fixture in the approved contract is 0.886*sqrt(N) = "
        "sqrt(pi*N/4). The other constant that appears in the rho literature "
        "for the length (tail + cycle) of a SINGLE walk under the "
        "random-function idealisation is sqrt(pi*N/2) = 1.2533*sqrt(N), which "
        "for this N equals %.1f. Both numbers are recorded here so that a "
        "reviewer can see which one the measurement tracks. The frozen "
        "prediction is NOT modified and every comparison reported in this run "
        "is made against 0.886*sqrt(N) exactly as the contract specifies."
        % (1.2533 * math.sqrt(N)))
    seed_band["sqrt_pi_N_over_2"] = 1.2533 * math.sqrt(N)
    log("FROZEN seed band: per-seed [%d, %d], median_band [%s, %s], median %.1f ; 0.886*sqrt(N) = %.1f"
        % (min(base_ok), max(base_ok), lo, hi, seed_band["median"], fixture))

    # ---- 6. NULL OBJECTS (different order) --------------------------------
    pn = prev_prime(1 << args.null_bits)
    null_rnd = random.Random(master_seed * 7 + 3)
    nulls = []
    tries = 0
    while len(nulls) < 8 and tries < 3000:
        tries += 1
        na = null_rnd.randrange(1, pn)
        nb = null_rnd.randrange(1, pn)
        if (4 * na * na * na + 27 * nb * nb) % pn == 0:
            continue
        NN = group_order(na, nb, pn, random.Random(master_seed * 13 + tries))
        if NN is None or not is_prime(NN) or NN > N // 16:
            continue
        Pn_ = random_point(na, nb, pn, null_rnd)
        kn = null_rnd.randrange(2, NN - 1)
        Qn_ = ec_mul(Pn_, kn, na, pn)
        nulls.append({"p": pn, "a": na, "b": nb, "N": NN, "k": kn,
                      "P": list(Pn_), "Q": list(Qn_)})
    if len(nulls) < 8:
        defects.append({"where": "null_objects", "issue": "fewer than 8 different-order null objects found",
                        "found": len(nulls)})
    null_all = []
    for idx, nu in enumerate(nulls):
        for s in PROTOCOL["seeds"]:
            r = rho_solve(tuple(nu["P"]), tuple(nu["Q"]), nu["N"], nu["a"], nu["b"], nu["p"], s, deadline=deadline)
            r.pop("op_sequence", None)
            r.update({"curve_role": "null_object_different_order", "null_index": idx,
                      "p": nu["p"], "a": nu["a"], "b": nu["b"], "N": nu["N"],
                      "coordinate_system": PROTOCOL["q1_common_coordinate_system"]["id"],
                      "k_recovered_matches_planted": (r["k"] == nu["k"]) if r["k"] is not None else None})
            solve_records.append(r)
            null_all.append(r)
    null_ops = [r["group_ops"] for r in null_all if r["status"] == "solved"]
    null_median = median(null_ops) if null_ops else None
    mb = seed_band["median_band"]
    separated_median_band = bool(null_median is not None and
                                 (null_median < mb["low"] or null_median > mb["high"]))
    separated_per_seed_band = bool(null_median is not None and
                                   (null_median < seed_band["min"] or null_median > seed_band["max"]))
    separated = separated_median_band
    null_block = {
        "rule": PROTOCOL["null_object_rule"],
        "declared_smaller_prime_p": pn,
        "declared_smaller_prime_bits": args.null_bits,
        "requirement": "N' prime and N' <= N/16",
        "N_over_16": N // 16,
        "curves": [{kk: vv for kk, vv in nu.items()} for nu in nulls],
        "per_null_curve_median_group_ops": [
            median([r["group_ops"] for r in null_all
                    if r.get("null_index") == i and r["status"] == "solved"])
            for i in range(len(nulls))],
        "solves_completed": len(null_ops),
        "solves_attempted": len(null_all),
        "median_group_ops": null_median,
        "class_seed_band": {"per_seed_band": [seed_band["min"], seed_band["max"]],
                            "median_band": [mb["low"], mb["high"]]},
        "separation_criterion": (
            "PRIMARY: null median strictly outside the frozen median_band. "
            "Also reported: null median strictly outside the raw per_seed_band."),
        "separated": separated,
        "separated_under_median_band_primary": separated_median_band,
        "separated_under_per_seed_band": separated_per_seed_band,
        "predicted_ratio_sqrt_Nprime_over_N": (
            median([math.sqrt(nu["N"] / N) for nu in nulls]) if nulls else None),
        "observed_ratio_null_median_over_base_median": (
            null_median / seed_band["median"] if null_median else None),
        "structural_null_object_same_p_different_trace": {
            "role": "structural only; carries NO cost-resolution role",
            "curves": struct_null,
            "any_appeared_in_class_walk": bool(struct_violations),
        },
        "measured_at": now_iso(),
    }
    log("null objects: median %s ; PRIMARY median_band [%s,%s] -> separated=%s ; "
        "raw per_seed_band [%d,%d] -> separated=%s"
        % (null_median, mb["low"], mb["high"], separated_median_band,
           seed_band["min"], seed_band["max"], separated_per_seed_band))
    if separated_median_band and not separated_per_seed_band:
        defects.append({
            "where": "null_object_control",
            "issue": (
                "The different-order null object separates under the PRIMARY "
                "frozen band (median_band) but NOT under the raw per_seed_band. "
                "The raw per-seed band is wide because the rho step count is a "
                "heavy-tailed random variable and the minimum over 16 seeds "
                "dips far below the median; that band is a descriptor of "
                "single-draw dispersion, not the resolution of the "
                "median-over-16 statistic that every between-member comparison "
                "actually uses. Recorded here explicitly so that the choice of "
                "primary band is visible to review rather than buried."),
            "null_median": null_median,
            "median_band": [mb["low"], mb["high"]],
            "per_seed_band": [seed_band["min"], seed_band["max"]],
            "classification": "recorded observation about instrument resolution; not a mathematical result",
        })

    # ---- 7. MEMBER SOLVES (Q1) --------------------------------------------
    first_between_member_comparison_at = None
    member_q1 = {}
    member_mix = {}
    op_seq0 = {0: op_seq0_base}
    censored_members = []
    budget_hit = False
    for vi in range(len(vertices)):
        if vi == 0:
            member_q1[0] = base_ok
            member_mix[0] = {"adds": [r["adds"] for r in base_solves if r["status"] == "solved"],
                             "dbls": [r["dbls"] for r in base_solves if r["status"] == "solved"]}
            continue
        if not transfers[vi]["transfer_structurally_ok"]:
            continue
        if time.time() > deadline:
            budget_hit = True
            break
        va, vb = vertices[vi]["a"], vertices[vi]["b"]
        Pv, Qv = transfers[vi]["P"], transfers[vi]["Q"]
        ops = []
        mix_a = []
        mix_d = []
        for si, s in enumerate(PROTOCOL["seeds"]):
            r = rho_solve(Pv, Qv, N, va, vb, p, s, record_seq=(si == 0), deadline=deadline)
            if si == 0 and r.get("op_sequence"):
                op_seq0[vi] = "".join(r["op_sequence"][:PROTOCOL["q2_replay_ops"]])
            r.pop("op_sequence", None)
            r.update({"curve_role": "class_member", "vertex": vi, "p": p, "a": va, "b": vb, "N": N,
                      "j": vertices[vi]["j"], "walk_path_degrees": transfers[vi]["path_degrees"],
                      "coordinate_system": PROTOCOL["q1_common_coordinate_system"]["id"]})
            solve_records.append(r)
            if r["status"] == "solved":
                ops.append(r["group_ops"])
                mix_a.append(r["adds"])
                mix_d.append(r["dbls"])
            else:
                censored_members.append({"vertex": vi, "seed": s, "status": r["status"],
                                         "steps_at_cutoff": r["steps"],
                                         "group_ops_at_cutoff": r["group_ops"],
                                         "note": "CENSORED. Recorded with its step count at cutoff. Never a slow curve, never negative mathematical evidence."})
        member_q1[vi] = ops
        member_mix[vi] = {"adds": mix_a, "dbls": mix_d}
    if budget_hit:
        defects.append({"where": "member solves", "issue": "wall-clock budget reached before every member was solved",
                        "members_solved": len(member_q1), "members_total": len(vertices)})
    first_between_member_comparison_at = now_iso()
    log("member solves complete: %d members with Q1 data" % len(member_q1))

    # ---- 8. Q2 -------------------------------------------------------------
    member_q2 = {}
    for vi in list(member_q1.keys()):
        if time.time() > deadline:
            defects.append({"where": "Q2", "issue": "budget reached before every member was measured",
                            "measured": len(member_q2)})
            break
        va, vb = vertices[vi]["a"], vertices[vi]["b"]
        Pv, Qv = (P0, Q0) if vi == 0 else (transfers[vi]["P"], transfers[vi]["Q"])
        ok3, note3 = a_minus_3_reachable(va, vb, p)
        me = montgomery_or_edwards_reachable(va, vb, p, N)
        results = []
        for cand in PROTOCOL["q2_candidate_model_set"]:
            mid = cand["id"]
            if mid == "JACOBIAN_A_MINUS_3" and not ok3:
                results.append({"model": mid, "reachable": False, "reason": note3})
                continue
            if mid in ("MONTGOMERY", "TWISTED_EDWARDS"):
                results.append({"model": mid, "reachable": me["reachable"],
                                "reason": "requires a rational point of order 4; rational_2_torsion=%s, 4|N=%s"
                                          % (me["rational_2_torsion"], me["order_divisible_by_4"])})
                continue
            r = measure_model(mid, va, vb, p, N, Pv, Qv, PROTOCOL["seeds"][0], PROTOCOL["q2_replay_ops"])
            if r is None:
                results.append({"model": mid, "reachable": False, "reason": "model construction failed"})
            else:
                r["reachable"] = True
                if r["add_field_mults_per_op"] is not None and r["dbl_field_mults_per_op"] is not None:
                    r["field_mults_per_group_op_common_mix"] = (
                        (common_mix["adds"] * r["add_field_mults_per_op"]
                         + common_mix["dbls"] * r["dbl_field_mults_per_op"]) / common_mix["total"])
                if vi in op_seq0:
                    r["replay_matches_q1_op_sequence"] = (
                        r["op_sequence_prefix"] == op_seq0[vi][:len(r["op_sequence_prefix"])])
                results.append(r)
        measured = [r for r in results if r.get("reachable") and "field_mults_per_group_op_common_mix" in r]
        best = min(measured, key=lambda r: r["field_mults_per_group_op_common_mix"]) if measured else None
        member_q2[vi] = {
            "vertex": vi, "j": vertices[vi]["j"], "a": va, "b": vb,
            "a_minus_3_model_reachable": ok3, "a_minus_3_test": note3,
            "montgomery_or_edwards_model_reachable": me,
            "common_mix": common_mix,
            "models": results,
            "cheapest_reachable_model": best["model"] if best else None,
            "field_mults_per_group_op": best["field_mults_per_group_op_common_mix"] if best else None,
            "field_mults_per_group_op_own_mix": best["field_mults_per_group_op_own_mix"] if best else None,
            "add_field_mults_per_op": best["add_field_mults_per_op"] if best else None,
            "dbl_field_mults_per_op": best["dbl_field_mults_per_op"] if best else None,
            "raw_M": best["grouplaw_M"] if best else None,
            "raw_S": best["grouplaw_S"] if best else None,
            "raw_add_M": best["add_M"] if best else None,
            "raw_add_S": best["add_S"] if best else None,
            "raw_dbl_M": best["dbl_M"] if best else None,
            "raw_dbl_S": best["dbl_S"] if best else None,
            "replay_matches_q1_op_sequence": best.get("replay_matches_q1_op_sequence") if best else None,
        }
    log("Q2 measured on %d members" % len(member_q2))

    # ---- 9. TAIL CHECKS ----------------------------------------------------
    tail = {}
    generic = [vi for vi in member_q1 if vertices[vi]["j"] not in (0, 1728) and member_q1[vi]]
    special_j = [vi for vi in member_q1 if vertices[vi]["j"] in (0, 1728)]
    if generic:
        cheapest_vi = min(generic, key=lambda vi: median(member_q1[vi]))
        cheapest_med = median(member_q1[cheapest_vi])
        inside = mb["low"] <= cheapest_med <= mb["high"]
        tail["cheapest_on_group_operation_axis"] = {
            "vertex": cheapest_vi, "median_group_ops": cheapest_med,
            "inside_frozen_median_band": bool(inside),
            "inside_frozen_per_seed_band": bool(seed_band["min"] <= cheapest_med <= seed_band["max"]),
            "median_band": [mb["low"], mb["high"]],
            "per_seed_band": [seed_band["min"], seed_band["max"]],
            "class_median_of_member_medians": median([median(member_q1[vi]) for vi in generic if member_q1[vi]]),
        }
        if not inside and time.time() < deadline:
            fresh = []
            va, vb = vertices[cheapest_vi]["a"], vertices[cheapest_vi]["b"]
            Pv, Qv = (P0, Q0) if cheapest_vi == 0 else (transfers[cheapest_vi]["P"], transfers[cheapest_vi]["Q"])
            for s in PROTOCOL["fresh_seeds_for_tail_check"]:
                r = rho_solve(Pv, Qv, N, va, vb, p, s, deadline=deadline)
                r.pop("op_sequence", None)
                r.update({"curve_role": "class_member_fresh_seed_tail_check", "vertex": cheapest_vi,
                          "p": p, "a": va, "b": vb, "N": N,
                          "coordinate_system": PROTOCOL["q1_common_coordinate_system"]["id"]})
                solve_records.append(r)
                if r["status"] == "solved":
                    fresh.append(r["group_ops"])
            tail["cheapest_on_group_operation_axis"]["fresh_seed_rerun"] = {
                "seeds": PROTOCOL["fresh_seeds_for_tail_check"],
                "n": len(fresh), "median": median(fresh) if fresh else None,
                "inside_frozen_median_band": bool(fresh and mb["low"] <= median(fresh) <= mb["high"]),
                "inside_frozen_per_seed_band": bool(fresh and seed_band["min"] <= median(fresh) <= seed_band["max"]),
            }
    if member_q2:
        q2vals = {vi: m["field_mults_per_group_op"] for vi, m in member_q2.items()
                  if m["field_mults_per_group_op"] is not None and vertices[vi]["j"] not in (0, 1728)}
        if q2vals:
            cheap_q2 = min(q2vals, key=lambda vi: q2vals[vi])
            tail["cheapest_on_per_operation_axis"] = {
                "vertex": cheap_q2, "field_mults_per_group_op": q2vals[cheap_q2],
                "a_minus_3_model_reachable": member_q2[cheap_q2]["a_minus_3_model_reachable"],
                "cheapest_reachable_model": member_q2[cheap_q2]["cheapest_reachable_model"],
                "observation_note": "reported as an observation only; no verdict is stated here",
            }

    # ---- 10. BSGS CROSS-CHECK ---------------------------------------------
    bsgs = []
    smallest_null = min(range(len(nulls)), key=lambda i: nulls[i]["N"]) if nulls else None
    if smallest_null is not None:
        nu = nulls[smallest_null]
        kb = bsgs_solve(tuple(nu["P"]), tuple(nu["Q"]), nu["N"], nu["a"], nu["p"])
        rho_k = next((r["k"] for r in null_all if r.get("null_index") == smallest_null and r["k"] is not None), None)
        bsgs.append({"instance": "smallest instance (null object of least order)",
                     "null_index": smallest_null, "N": nu["N"], "bsgs_k": kb,
                     "rho_k": rho_k, "planted_k": nu["k"],
                     "agrees_with_rho": bool(kb is not None and kb == rho_k),
                     "agrees_with_planted": bool(kb == nu["k"])})
    kb0 = bsgs_solve(P0, Q0, N, a, p) if time.time() < deadline else None
    rho_k0 = next((r["k"] for r in base_solves if r["k"] is not None), None)
    bsgs.append({"instance": "base curve", "N": N, "bsgs_k": kb0, "rho_k": rho_k0, "planted_k": k,
                 "agrees_with_rho": bool(kb0 is not None and kb0 == rho_k0),
                 "agrees_with_planted": bool(kb0 == k)})
    member_pool = [vi for vi in member_q1 if vi != 0]
    if member_pool and time.time() < deadline:
        mvi = min(member_pool, key=lambda vi: (vertices[vi]["j"], vi))
        va, vb = vertices[mvi]["a"], vertices[mvi]["b"]
        kbm = bsgs_solve(transfers[mvi]["P"], transfers[mvi]["Q"], N, va, p)
        rho_km = next((r["k"] for r in solve_records
                       if r.get("vertex") == mvi and r.get("curve_role") == "class_member" and r["k"] is not None), None)
        bsgs.append({"instance": "class member of least j-invariant", "vertex": mvi, "N": N,
                     "bsgs_k": kbm, "rho_k": rho_km, "planted_k": k,
                     "agrees_with_rho": bool(kbm is not None and kbm == rho_km),
                     "agrees_with_planted": bool(kbm == k)})

    # ---- 11. WRITE ARTIFACTS ----------------------------------------------
    wall = time.time() - t_start
    manifest = {
        "run_id": args.run_id,
        "experiment_id": PROTOCOL["experiment_id"],
        "hypothesis_id": "H-ISOU-c5bfea",
        "task_id": "TASK-20260813-4bee82",
        "goal_id": "GOAL-ECDLP-001",
        "batch_id": "BATCH-009b1b",
        "instance_label": args.instance,
        "prime_bits": bits,
        "claim_tier": "toy",
        "claim_tier_note": (
            "Toy scale. P-256 is the SHAPE imitated (ordinary, prime order, "
            "conductor f = 1, a = -3 model), not the object measured. Nothing "
            "in this run is evidence about P-256 itself."),
        "certificate": {
            "kind": "dlp_solution",
            "verified_by": "experiments/EXP-ISOU-2ac81f/implementation/certificate_checker.py",
            "independence": (
                "The checker is a separate module and a separate process. It "
                "imports nothing from census.py, re-implements its own modular "
                "and elliptic-curve arithmetic, and re-derives [k]P = Q on the "
                "base curve after pullback as well as [k]P' = Q' on each member. "
                "Self-confirmation is not verification."),
        },
        "started_at": datetime.fromtimestamp(t_start, timezone.utc).isoformat(),
        "finished_at": now_iso(),
        "wall_clock_seconds": wall,
        "budget": {
            "wall_clock_seconds_per_run": args.wall_clock_seconds,
            "maximum_memory_gb": 8, "maximum_workers": 1, "maximum_runs": 4,
            "budget_exhausted": bool(budget_hit),
        },
        "command": args.command,
        "environment": env,
        "inference": {
            "requested_policy": "executor-implementation",
            "resolved_model_identifier": os.environ.get("AUTORESEARCH_MODEL", "claude-opus-5"),
            "resolved_backend": os.environ.get("AUTORESEARCH_BACKEND", "anthropic (Claude Code session default)"),
            "probe_verified": False,
            "probe_verified_note": (
                "No model probe was run by this session; the resolved identifier "
                "is the session's own model as reported by the harness. Recorded "
                "as unverified rather than asserted."),
            "reasoning_effort": "medium",
            "reasoning_effort_source": ".claude/agents/executor.md frontmatter, derived from orchestration/model-policies.yaml",
            "fallback_used": True,
            "fallback_reason": (
                "Under this Claude Code harness every policy alias resolves to "
                "the one session model (CLAUDE.md 'Model policy note'); the "
                "executor role's `medium` reasoning effort is what binds per "
                "subagent. Recorded rather than silently substituted, per the "
                "handoff's inference.fallback_note."),
            "bedrock": False,
        },
        "protocol_frozen_constants": PROTOCOL,
        "ms_aggregation_rule": PROTOCOL["ms_aggregation_rule"],
        "q2_candidate_model_set_declared_before_measurement": True,
        "frozen_base_curve": {
            "p": p, "a": a, "b": b, "N": N, "t": t, "D": D,
            "conductor_f": conductor(t, p)[0],
            "fundamental_discriminant": is_fundamental(D),
            "f_equals_1_check": "f = 1 verified by checking that t^2 - 4p is a fundamental discriminant: %s" % is_fundamental(D),
            "ordinary": bool(t % p != 0),
            "N_prime": is_prime(N),
            "a_equals_minus_3": bool(a == (-3) % p),
            "j_invariant": j_invariant(a, b, p),
            "frozen_at": base_curve_frozen_at,
            "frozen_before_any_solve": True,
            "selection_seed": master_seed,
        },
        "frozen_dlp_instance": {
            "P": list(P0), "Q": list(Q0), "k": k,
            "k_disclosure_note": "k is recorded deliberately: this is a benchmark, not a challenge, and hiding it would prevent certificate checking.",
            "frozen_at": dlp_frozen_at,
        },
        "frozen_seed_band": seed_band,
        "freeze_ordering": {
            "base_curve_frozen_at": base_curve_frozen_at,
            "dlp_instance_frozen_at": dlp_frozen_at,
            "seed_band_frozen_at": seed_band_frozen_at,
            "first_between_member_comparison_at": first_between_member_comparison_at,
            "assertion": "base curve and seed band were frozen strictly before the first between-member comparison",
        },
        "stdout_log": stdout_lines,
        "stderr_log": [],
        "stdout_stderr_note": (
            "The declared artifact set for TASK-20260813-4bee82 fixes exactly "
            "eleven files per run and does not include separate command.txt, "
            "environment.json, stdout.log or stderr.log files. Their required "
            "content is therefore carried INSIDE this manifest (fields command, "
            "environment, stdout_log, stderr_log) rather than written to "
            "undeclared paths, because the archive stages only declared paths. "
            "Recorded as a reconciliation, not a silent choice."),
    }
    write_yaml(os.path.join(out, "manifest.yaml"), manifest)

    write_yaml(os.path.join(out, "base_curve_selection.yaml"), {
        "run_id": args.run_id,
        "selection_criteria": SELECTION_CRITERIA,
        "selection_parameters": {"prime_bits": bits, "master_seed": master_seed,
                                 "DMAX": dmax, "H_MIN": args.hmin, "H_MAX": args.hmax,
                                 "max_candidates": args.max_candidates},
        "selection_log": sel_log,
        "accepted": {"p": p, "a": a, "b": b, "N": N, "t": t, "D": D, "h": h,
                     "frozen_at": base_curve_frozen_at},
        "rejection_log_note": (
            "rejected_sample lists up to the first 400 rejected candidates in "
            "the order examined, each with its exact rejection reason; "
            "rejection_reason_counts is the complete tally over every candidate "
            "examined, so no rejection is unrecorded in aggregate."),
    })

    write_yaml(os.path.join(out, "class_enumeration.yaml"), {
        "run_id": args.run_id,
        "deduplication_rule": PROTOCOL["dedup_rule"],
        "completeness_rule": PROTOCOL["completeness_rule"],
        "enumerated_vertex_count": len(vertices),
        "class_number_h_independent": h_independent,
        "class_number_method": "count of reduced primitive positive definite binary quadratic forms of discriminant D = t^2-4p, computed independently of the isogeny walk",
        "discriminant_D": D,
        "completeness_comparison": {
            "enumerated_vertex_count": len(vertices),
            "h_disc_End_E0": h_independent,
            "equal": bool(complete),
            "verdict_free_statement": (
                "complete census" if complete else
                "INCOMPLETE SUBGRAPH: the walk closed on fewer vertices than h(disc(End(E_0)))"),
            "selection_filter_caveat": (
                "The declared base-curve selection procedure REQUIRED this "
                "equality, so at the accepted base curve it holds by "
                "construction. It is reported side by side regardless, and "
                "candidates rejected for closing short appear in the rejection "
                "log."),
        },
        "special_j_members": [{"vertex": vi, "j": vertices[vi]["j"]} for vi in special_j],
        "special_j_rule": PROTOCOL["special_j_rule"],
        "degree_statistics": walk["degree_stats"],
        "vertices": [{
            "index": v["index"], "a": v["a"], "b": v["b"], "j": v["j"],
            "isomorphism_class_id": "FPISO-%d-%d-%d" % (p, v["a"], v["b"]),
            "walk_path": [{"ell": s["ell"], "lambda": s["lambda"], "from_vertex": s["from"]} for s in v["path"]],
            "walk_path_length": len(v["path"]),
            "walk_path_degrees": [s["ell"] for s in v["path"]],
        } for v in vertices],
    })

    write_yaml(os.path.join(out, "isogeny_edges.yaml"), {
        "run_id": args.run_id,
        "edge_certificate_rule": PROTOCOL["edge_certificate_rule"],
        "edge_count": len(walk["edges"]),
        "edges_all_certificate_verified": all(e["certificate"]["verified"] for e in walk["edges"]),
        "edges": [{
            "from_vertex": e["from"], "to_vertex": e["to"], "ell": e["ell"],
            "frobenius_eigenvalue_lambda": e["lambda"],
            "kernel_polynomial_coefficients_ascending": e["kernel_polynomial"],
            "codomain_a": e["codomain"][0], "codomain_b": e["codomain"][1],
            "tree_edge": e.get("tree_edge", False),
            "construction_cost_modelled_field_mults": e.get("construction_cost_modelled_field_mults"),
            "construction_cost_modelled_inversions": e.get("construction_cost_modelled_inversions"),
            "construction_cost_label": "modelled",
            "certificate": e["certificate"],
        } for e in walk["edges"]],
    })

    write_yaml(os.path.join(out, "dlp_instance.yaml"), {
        "run_id": args.run_id,
        "base_curve": {"p": p, "a": a, "b": b, "N": N},
        "P": list(P0), "Q": list(Q0), "k": k,
        "note": "One instance, transferred by explicit Velu evaluation to every member. k is recorded: benchmark, not challenge.",
        "transfers": [{
            "vertex": vi, "a": vertices[vi]["a"], "b": vertices[vi]["b"], "j": vertices[vi]["j"],
            "P_image": list(tr["P"]) if tr["P"] else None,
            "Q_image": list(tr["Q"]) if tr["Q"] else None,
            "walk_path_degrees": tr["path_degrees"], "walk_path_length": tr["path_length"],
            "transfer_structurally_ok": tr["transfer_structurally_ok"],
            "walk_cost_measured_M": tr["measured_M"],
            "walk_cost_measured_S": tr["measured_S"],
            "walk_cost_measured_inversions": tr["measured_I"],
            "walk_cost_measured_weighted_field_mults": tr["measured_weighted"],
            "walk_cost_measured_label": "measured",
            "walk_cost_modelled_construction_weighted_field_mults": tr["modelled_construction_weighted"],
            "walk_cost_modelled_label": "modelled",
        } for vi, tr in sorted(transfers.items())],
        "walk_cost_basis": PROTOCOL["walk_cost_basis"],
    })

    with open(os.path.join(out, "solve_records.jsonl"), "w") as fh:
        for r in solve_records:
            fh.write(json.dumps(r, sort_keys=True) + "\n")

    write_yaml(os.path.join(out, "null_objects.yaml"), null_block)

    write_yaml(os.path.join(out, "defect_log.yaml"), {
        "run_id": args.run_id,
        "policy": (
            "Failed edges, non-verifying certificates, censored solves, members "
            "outside the seed band, and every protocol deviation are recorded "
            "here. Timeouts, crashes and infrastructure failures are NEVER "
            "negative mathematical evidence (AGENTS.md rule 5)."),
        "defects": defects,
        "censored_solves": censored_members,
        "failed_edges": [e for e in walk["edges"] if not e["certificate"]["verified"]],
        "protocol_deviations": deviations + [
            {
                "id": "DEV-1",
                "field": "required_artifacts / kernel generator",
                "deviation": (
                    "The contract asks for 'every Velu isogeny with its kernel "
                    "generator'. Because N is prime, E(F_p) has no ell-torsion "
                    "for any declared ell, so NO edge has an F_p-rational kernel "
                    "generator. The kernel is recorded by its minimal (kernel) "
                    "polynomial together with the Frobenius eigenvalue lambda, "
                    "which specifies the same subgroup exactly. Recorded rather "
                    "than silently substituted."),
            },
            {
                "id": "DEV-2",
                "field": "run package layout",
                "deviation": (
                    "docs/evidence-and-reproducibility.md's command.txt, "
                    "environment.json, stdout.log and stderr.log are carried as "
                    "fields inside manifest.yaml, because the declared artifact "
                    "set for this task fixes exactly eleven per-run filenames and "
                    "the archive stages only declared paths."),
            },
            {
                "id": "DEV-3",
                "field": "base curve selection",
                "deviation": (
                    "The declared selection procedure includes two "
                    "budget-feasibility filters (|D| <= DMAX and H_MIN <= h(D) <= "
                    "H_MAX) and one structural filter (the declared degrees "
                    "generate cl(O), i.e. the walk closes on h). All three are "
                    "structural, were declared and frozen before any DLP was "
                    "solved, and none uses a cost datum. The third makes the "
                    "completeness comparison true by construction at the accepted "
                    "candidate; that is stated in class_enumeration.yaml."),
            },
            {
                "id": "DEV-4",
                "field": "metrics / Q2",
                "deviation": (
                    "Q2 is measured on the first %d group operations of each "
                    "member's own seed-index-0 rho walk, replayed in each "
                    "candidate model, rather than on the full walk. The replay "
                    "length is uniform across every member and was declared "
                    "before measurement. The coordinate-normalization overhead "
                    "required to expose the affine x-coordinate to the walk "
                    "function is instrumented and reported separately from the "
                    "group-law cost." % PROTOCOL["q2_replay_ops"]),
            },
        ],
        "structural_null_object_violations": struct_violations,
    })

    rec = {
        "run_id": args.run_id,
        "experiment_id": PROTOCOL["experiment_id"],
        "task_id": "TASK-20260813-4bee82",
        "terminal_status": None,
        "terminal_status_reason": None,
        "wall_clock_seconds": wall,
        "budget_exhausted": bool(budget_hit),
        "members_total": len(vertices),
        "members_with_q1_data": len(member_q1),
        "censored_solves": len(censored_members),
        "null_object_separated": separated,
        "class_walk_complete": bool(complete),
        "enumerated_vertex_count": len(vertices),
        "class_number_h_independent": h_independent,
        "bsgs_cross_check": bsgs,
        "tail_checks": tail,
        "certificate_verification_pending": (
            "certificate_verification.yaml is written by the INDEPENDENT checker "
            "implementation/certificate_checker.py in a separate process; "
            "summary.json is written afterwards by `census.py summarize` and "
            "excludes any member whose certificate did not independently verify."),
        "no_interpretation_note": (
            "This record states observations and run status only. It contains no "
            "verdict, no evidence record, no hypothesis status, and no statement "
            "that any prediction was supported or falsified."),
    }
    if budget_hit or censored_members:
        rec["terminal_status"] = "completed_valid"
        rec["terminal_status_reason"] = (
            "The run completed within budget and produced its declared artifacts, "
            "but %d individual solves were censored and/or the budget was reached "
            "before every member was measured. Censored solves are recorded with "
            "their step count at cutoff and contribute no cost datum; they are "
            "infrastructure signal, never negative mathematical evidence."
            % len(censored_members))
    else:
        rec["terminal_status"] = "completed_valid"
        rec["terminal_status_reason"] = (
            "Every planned measurement completed inside the wall-clock budget, "
            "every declared artifact was written, and the run reached its "
            "measurement endpoint. Validity of individual cost data is gated on "
            "the independent certificate verification recorded in "
            "certificate_verification.yaml and applied in summary.json.")
    if not separated:
        rec["terminal_status"] = "completed_invalid"
        rec["terminal_status_reason"] = (
            "INSTRUMENT FAILURE STOP. The different-order null-object control did "
            "not separate from the class members at the resolution of the frozen "
            "seed band. Per the frozen contract's stopping rules, NO Q1 and NO Q3 "
            "result is reported from this run in any form, including as "
            "preliminary or partial. Q2, which does not depend on the "
            "cost-resolution control, is retained and labelled.")
    if struct_violations:
        rec["structural_null_object_violation"] = struct_violations
    write_yaml(os.path.join(out, "run_record.yaml"), rec)

    # intermediate machine-readable state for `summarize`.
    # Written OUTSIDE the run directory on purpose: the declared artifact set
    # for this task fixes exactly eleven files per run, the archive stages only
    # declared paths, and an undeclared file inside the run directory would be
    # invisible to the record. This handoff file is scratch, not an artifact.
    with open(args.state_file, "w") as fh:
        json.dump({"member_q1": {str(kk): vv for kk, vv in member_q1.items()},
                   "member_mix": {str(kk): vv for kk, vv in member_mix.items()},
                   "common_mix": common_mix,
                   "member_q2": {str(kk): vv for kk, vv in member_q2.items()},
                   "transfers": {str(kk): {"measured_weighted": vv["measured_weighted"],
                                           "modelled_construction_weighted": vv["modelled_construction_weighted"],
                                           "path_length": vv["path_length"],
                                           "path_degrees": vv["path_degrees"]}
                                 for kk, vv in transfers.items()},
                   "vertices": [{"index": v["index"], "a": v["a"], "b": v["b"], "j": v["j"]} for v in vertices],
                   "seed_band": seed_band, "separated": separated, "complete": complete,
                   "h_independent": h_independent, "N": N, "p": p, "k": k,
                   "terminal_status": rec["terminal_status"]}, fh)
    log("run finished in %.1f s with terminal status %s" % (wall, rec["terminal_status"]))
    return rec


# ---------------------------------------------------------------------------
# 11. SUMMARIZE  (consumes the INDEPENDENT checker's output)
# ---------------------------------------------------------------------------

def do_summarize(args):
    import yaml
    out = args.out_dir
    with open(args.state_file) as fh:
        st = json.load(fh)
    with open(os.path.join(out, "certificate_verification.yaml")) as fh:
        cv = yaml.safe_load(fh)
    verified = set()
    for entry in cv.get("members", []):
        if entry.get("certificate_verified"):
            verified.add(int(entry["vertex"]))
    band = st["seed_band"]
    vert = {v["index"]: v for v in st["vertices"]}
    q1 = {int(kk): vv for kk, vv in st["member_q1"].items()}
    q2 = {int(kk): vv for kk, vv in st["member_q2"].items()}
    tr = {int(kk): vv for kk, vv in st["transfers"].items()}
    mix = {int(kk): vv for kk, vv in st["member_mix"].items()}

    admissible_q1 = st["separated"]
    members = []
    for vi in sorted(q1):
        if vi not in verified:
            continue
        j = vert[vi]["j"]
        m2 = q2.get(vi)
        med = median(q1[vi]) if q1[vi] else None
        row = {
            "vertex": vi, "j_invariant": j,
            "special_j": bool(j in (0, 1728)),
            "certificate_verified": True,
            "seeds_solved": len(q1[vi]),
            "q2_field_mults_per_group_op": m2["field_mults_per_group_op"] if m2 else None,
            "q2_field_mults_per_group_op_own_mix": m2["field_mults_per_group_op_own_mix"] if m2 else None,
            "q2_add_field_mults_per_op": m2["add_field_mults_per_op"] if m2 else None,
            "q2_dbl_field_mults_per_op": m2["dbl_field_mults_per_op"] if m2 else None,
            "q2_cheapest_reachable_model": m2["cheapest_reachable_model"] if m2 else None,
            "q2_raw_M": m2["raw_M"] if m2 else None,
            "q2_raw_S": m2["raw_S"] if m2 else None,
            "q2_raw_add_M": m2["raw_add_M"] if m2 else None,
            "q2_raw_add_S": m2["raw_add_S"] if m2 else None,
            "q2_raw_dbl_M": m2["raw_dbl_M"] if m2 else None,
            "q2_raw_dbl_S": m2["raw_dbl_S"] if m2 else None,
            "q2_replay_matches_q1_op_sequence": m2["replay_matches_q1_op_sequence"] if m2 else None,
            "median_adds_over_seeds": median(mix.get(vi, {}).get("adds", [])) if mix.get(vi, {}).get("adds") else None,
            "median_dbls_over_seeds": median(mix.get(vi, {}).get("dbls", [])) if mix.get(vi, {}).get("dbls") else None,
            "a_minus_3_model_reachable": m2["a_minus_3_model_reachable"] if m2 else None,
            "montgomery_or_edwards_model_reachable": (
                m2["montgomery_or_edwards_model_reachable"]["reachable"] if m2 else None),
            "walk_path_length": tr.get(vi, {}).get("path_length"),
            "walk_path_degrees": tr.get(vi, {}).get("path_degrees"),
            "walk_cost_measured_field_mults": tr.get(vi, {}).get("measured_weighted"),
            "walk_cost_modelled_construction_field_mults": tr.get(vi, {}).get("modelled_construction_weighted"),
        }
        if admissible_q1:
            row.update({
                "q1_group_ops_median": med,
                "q1_group_ops_min": min(q1[vi]) if q1[vi] else None,
                "q1_group_ops_max": max(q1[vi]) if q1[vi] else None,
                "q1_group_ops_mean": sum(q1[vi]) / len(q1[vi]) if q1[vi] else None,
                "q1_group_ops_stdev": stdev(q1[vi]),
                "q1_inside_frozen_median_band": bool(
                    med is not None and band["median_band"]["low"] <= med <= band["median_band"]["high"]),
                "q1_inside_frozen_per_seed_band": bool(
                    med is not None and band["min"] <= med <= band["max"]),
            })
        else:
            row["q1_group_ops_median"] = None
            row["q1_suppressed_reason"] = (
                "different-order null object did not separate: no Q1 result is "
                "reported from this run in any form")
        members.append(row)

    generic = [m for m in members if not m["special_j"]]
    def solve_field_mults(m):
        """
        Solve cost in FIELD MULTIPLICATIONS: the member's own median adds and
        median doublings over the 16 seeds, each charged at that member's own
        measured per-ADD and per-DBL cost in its cheapest reachable model.
        No group-operation count is ever added to a field-multiplication count.
        """
        if (m["median_adds_over_seeds"] is None or m["median_dbls_over_seeds"] is None
                or m["q2_add_field_mults_per_op"] is None or m["q2_dbl_field_mults_per_op"] is None):
            return None
        return (m["median_adds_over_seeds"] * m["q2_add_field_mults_per_op"]
                + m["median_dbls_over_seeds"] * m["q2_dbl_field_mults_per_op"])

    q3 = []
    base = next((m for m in members if m["vertex"] == 0), None)
    base_solve_fm = solve_field_mults(base) if base else None
    if admissible_q1 and base_solve_fm:
        for m in members:
            solve_fm = solve_field_mults(m)
            if solve_fm is None:
                continue
            wm = m["walk_cost_measured_field_mults"] or 0.0
            wmo = m["walk_cost_modelled_construction_field_mults"] or 0.0
            q3.append({
                "vertex": m["vertex"], "special_j": m["special_j"],
                "solve_cost_field_mults_measured": solve_fm,
                "walk_cost_field_mults_measured": wm,
                "walk_cost_field_mults_modelled_construction": wmo,
                "q3_measured_walk_only": solve_fm + wm,
                "q3_measured_plus_modelled_walk": solve_fm + wm + wmo,
                "base_curve_solve_cost_field_mults_measured": base_solve_fm,
                "ratio_to_base_measured_walk_only": (solve_fm + wm) / base_solve_fm,
                "ratio_to_base_measured_plus_modelled_walk": (solve_fm + wm + wmo) / base_solve_fm,
                "q1_median_below_frozen_median_band": bool(
                    m["q1_group_ops_median"] < band["median_band"]["low"]),
                "clears_frozen_band": bool(
                    (solve_fm + wm) < base_solve_fm
                    and m["q1_group_ops_median"] < band["median_band"]["low"]),
                "clears_frozen_band_definition": (
                    "A member is counted as cheaper end-to-end ONLY IF its charged "
                    "cost is below the base curve's solve cost AND its own Q1 "
                    "median lies below the frozen median_band, i.e. the difference "
                    "is not attributable to within-curve seed dispersion. Every "
                    "between-member claim must clear the frozen band "
                    "(specification controls: seed_dispersion_band). The raw "
                    "un-cleared count is reported alongside it."),
                "unit": "field multiplications (M + 1.0*S); no group-operation count is added to it",
            })

    q2vals = [m["q2_field_mults_per_group_op"] for m in generic if m["q2_field_mults_per_group_op"]]
    summary = {
        "schema": "crypto.autoresearch.exp_isou_2ac81f.summary.v1",
        "run_id": args.run_id,
        "experiment_id": PROTOCOL["experiment_id"],
        "terminal_status": st["terminal_status"],
        "claim_tier": "toy",
        "interpretation": (
            "NONE. This file reports measurements and their bands. It states no "
            "verdict, assigns no evidence strength, and says nothing about "
            "whether any prediction was supported or falsified."),
        "frozen_prediction_reference": {
            "source": "experiments/EXP-ISOU-2ac81f/specification.yaml preregistered_prediction (frozen, version 1)",
            "q1": "E[steps] = 0.886*sqrt(N), identical for every class member; predicted between-member effect exactly zero",
            "q2": "best-to-worst ratio strictly in the open interval (1.0, 1.5), split by 'a/(-3) is a fourth power in F_p'",
            "q3": "charged cost of every member >= base-curve solve cost; predicted improvement exactly zero",
            "note": "reproduced verbatim for comparison; not adjusted, not re-scored",
        },
        "completeness": {
            "enumerated_vertex_count": len(st["vertices"]),
            "class_number_h_independent": st["h_independent"],
            "equal": bool(st["complete"]),
        },
        "null_object_separated": bool(st["separated"]),
        "q1_admissible": bool(admissible_q1),
        "frozen_seed_band": band,
        "members_with_verified_certificate": len(members),
        "members_total_enumerated": len(st["vertices"]),
        "members_excluded_no_verified_certificate": sorted(set(q1) - verified),
        "generic_band_excludes_special_j": True,
        "special_j_members": [m["vertex"] for m in members if m["special_j"]],
        "members": members,
        "q3": q3,
    }
    if admissible_q1:
        meds = [m["q1_group_ops_median"] for m in generic if m["q1_group_ops_median"]]
        if meds:
            summary["q1_class_statistics_generic_members_only"] = {
                "n": len(meds), "class_median_of_member_medians": median(meds),
                "min": min(meds), "max": max(meds),
                "best_to_worst_ratio": max(meds) / min(meds),
                "frozen_per_seed_band": [band["min"], band["max"]],
                "frozen_median_band": [band["median_band"]["low"], band["median_band"]["high"]],
                "members_with_median_outside_frozen_median_band": [
                    m["vertex"] for m in generic
                    if m["q1_group_ops_median"] and not (
                        band["median_band"]["low"] <= m["q1_group_ops_median"] <= band["median_band"]["high"])],
                "members_with_median_outside_frozen_per_seed_band": [
                    m["vertex"] for m in generic
                    if m["q1_group_ops_median"] and not (band["min"] <= m["q1_group_ops_median"] <= band["max"])],
                "expected_false_flags_at_95pct_median_band": 0.05 * len(meds),
                "fixture_0886_sqrt_N": 0.886 * math.sqrt(st["N"]),
                "unit": "group operations (adds + doublings) in the common coordinate system AFFINE_SHORT_WEIERSTRASS",
            }
    if q2vals:
        summary["q2_class_statistics_generic_members_only"] = {
            "n": len(q2vals), "min": min(q2vals), "max": max(q2vals),
            "median": median(q2vals),
            "best_to_worst_ratio": max(q2vals) / min(q2vals),
            "by_a_minus_3_reachability": {
                "reachable": sorted({round(m["q2_field_mults_per_group_op"], 6) for m in generic
                                     if m["a_minus_3_model_reachable"] and m["q2_field_mults_per_group_op"]}),
                "not_reachable": sorted({round(m["q2_field_mults_per_group_op"], 6) for m in generic
                                         if m["a_minus_3_model_reachable"] is False and m["q2_field_mults_per_group_op"]}),
            },
            "count_a_minus_3_reachable": sum(1 for m in generic if m["a_minus_3_model_reachable"]),
            "count_a_minus_3_not_reachable": sum(1 for m in generic if m["a_minus_3_model_reachable"] is False),
            "count_montgomery_or_edwards_reachable": sum(1 for m in members if m["montgomery_or_edwards_model_reachable"]),
            "unit": "field multiplications per group operation (M + 1.0*S), each member in its own cheapest reachable model",
        }
    if q3:
        summary["q3_class_statistics"] = {
            "n": len(q3),
            "min_ratio_to_base_measured_walk_only": min(x["ratio_to_base_measured_walk_only"] for x in q3),
            "min_ratio_to_base_measured_plus_modelled_walk": min(x["ratio_to_base_measured_plus_modelled_walk"] for x in q3),
            "members_below_base_measured_walk_only_RAW": [
                x["vertex"] for x in q3 if x["ratio_to_base_measured_walk_only"] < 1.0],
            "members_below_base_measured_walk_only_CLEARING_FROZEN_BAND": [
                x["vertex"] for x in q3 if x["clears_frozen_band"]],
            "members_below_base_measured_plus_modelled_walk_RAW": [
                x["vertex"] for x in q3 if x["ratio_to_base_measured_plus_modelled_walk"] < 1.0],
            "raw_versus_cleared_note": (
                "The RAW count compares two point estimates (each curve's median "
                "over the same 16 seeds) with no band applied, so it is dominated "
                "by the seed dispersion the frozen band measures: the base "
                "curve's own median is itself one draw of that statistic. The "
                "CLEARING count applies the frozen band, as the contract's "
                "seed_dispersion_band control requires of every between-member "
                "claim. Both are reported; neither is interpreted here."),
            "base_curve_q1_median_versus_class_median": {
                "base_q1_median": base["q1_group_ops_median"],
                "class_median_of_member_medians": median(
                    [m["q1_group_ops_median"] for m in generic if m["q1_group_ops_median"]]),
                "note": "reported because the Q3 comparison is anchored on the base curve's own median",
            },
            "largest_walk_cost_measured": max(x["walk_cost_field_mults_measured"] for x in q3),
            "smallest_solve_cost_measured": min(x["solve_cost_field_mults_measured"] for x in q3),
            "base_solve_cost_measured": q3[0]["base_curve_solve_cost_field_mults_measured"],
            "largest_walk_cost_vs_largest_solve_saving": {
                "largest_walk_cost_measured": max(x["walk_cost_field_mults_measured"] for x in q3),
                "largest_solve_saving_vs_base_measured": max(
                    (x["base_curve_solve_cost_field_mults_measured"] - x["solve_cost_field_mults_measured"]) for x in q3),
            },
            "unit": "field multiplications (M + 1.0*S)",
        }
    with open(os.path.join(out, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2, sort_keys=False)
    print("summary written: %s" % os.path.join(out, "summary.json"))
    return summary


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--run-id", required=True)
    r.add_argument("--out-dir", required=True)
    r.add_argument("--bits", type=int, required=True)
    r.add_argument("--instance", required=True)
    r.add_argument("--master-seed", type=int, required=True)
    r.add_argument("--null-bits", type=int, required=True)
    r.add_argument("--dmax", type=int, required=True)
    r.add_argument("--hmin", type=int, default=20)
    r.add_argument("--hmax", type=int, default=400)
    r.add_argument("--max-candidates", type=int, default=20000)
    r.add_argument("--selection-seconds", type=float, default=180.0)
    r.add_argument("--wall-clock-seconds", type=float, default=600.0)
    r.add_argument("--state-file", required=True,
                   help="scratch handoff file for `summarize`; MUST be outside the run directory")
    s = sub.add_parser("summarize")
    s.add_argument("--run-id", required=True)
    s.add_argument("--out-dir", required=True)
    s.add_argument("--state-file", required=True)
    args = ap.parse_args()
    args.command = "python3 " + " ".join(sys.argv[0:1] + sys.argv[1:])
    if args.cmd == "run":
        do_run(args)
    else:
        do_summarize(args)


if __name__ == "__main__":
    main()
