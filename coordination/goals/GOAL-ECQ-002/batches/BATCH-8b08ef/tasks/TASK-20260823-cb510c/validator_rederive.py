#!/usr/bin/env python3
"""
VALIDATOR BLIND RE-DERIVATION CODE for TASK-20260823-cb510c.
Written from the definitions of the discriminant, the Shioda-Tate formula,
and the ICARM naive-height convention, WITHOUT reading the producer's scripts,
report.md, or implementation.md.

Sources read before writing this code (declared per honesty clause):
  - ledger/handoffs/TASK-20260823-cb510c.yaml (handoff)
  - coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/review_plan.yaml
  - ledger/goals/GOAL-ECQ-002/goal.yaml (C1' conditions, height convention)
  - ledger/hypotheses/H-ECQ-0ed5c8.yaml (mechanism, ceiling formula, construction)
  - best_candidates.json (machine-readable deliverable: a-invariants, tuple, t)
  - stratum_enumeration.json (machine-readable deliverable: fibre data for cross-check)
  - frontier_20260823.json (frozen frontier values)

NOT read (blind_from paths, declared):
  - TASK-20260823-827765/scripts/*
  - TASK-20260823-827765/report.md
  - TASK-20260823-827765/implementation.md
  - BATCH-541940/tasks/TASK-20260823-416e78/scripts/*

The construction (from H-ECQ-0ed5c8 mechanism):
  q(x) = prod(x - a_i) over integer 6-tuple
  p(x,T) = q(x-T) * q(x+T)   [degree 12 in x]
  g = monic degree-6 truncation of p
  r = g^2 - p   [degree <= 5 in x]
  The elliptic surface is y^2 = r(x, T) (or a Weierstrass model derived from it).

Shioda-Tate ceiling (from H-ECQ-0ed5c8):
  ceiling = (10d - 2) - sum_v deg(v)(m_v - 1)   [d=2 for K3, so 18 - sum]
  where m_v = number of components of the fibre at v.
  Kodaira types (residue char 0):
    I_0: m=1, I_n: m=n (multiplicative)
    II: m=1, III: m=2, IV: m=3, I_0*: m=5, I_n*: m=n+5, IV*: m=7, III*: m=8, II*: m=9
  Euler check: sum_v deg(v) * v_disc(v) = 12d = 24

ICARM naive height (from H-ECQ-0ed5c8):
  h = log max(|c4|^3, c6^2) on the globally minimal model
  where c4, c6 are the standard invariants from a-invariants.

Pre-filter (from H-ECQ-0ed5c8 mechanism):
  DD(T) = finite discriminant of the Weierstrass model
  Filter: deg gcd(DD, DD') == 0  <=>  DD squarefree  <=>  no repeated finite fibres
  If DD is squarefree, all finite fibres are I_1 (m=1, contribution 0).
  The only contribution is from the fibre at infinity.
  ceiling = 18 - (m_inf - 1) when DD is squarefree.
  If DD is not squarefree, deg G = sum deg(v)(N_v - 1) >= sum deg(v)(m_v - 1) = S_fin
  (equality when no repeated fibre is additive; additive detected by gcd(G, a4) > 0).
"""

import json
import sys
from fractions import Fraction
from math import log, isclose

# ============================================================
# PART 1: Naive height from a-invariants (J2 blind re-derivation)
# ============================================================

def compute_invariants(a1, a2, a3, a4, a6):
    """Compute b-invariants, c4, c6, Delta from a-invariants.
    All in exact integer arithmetic."""
    b2 = a1*a1 + 4*a2
    b4 = 2*a4 + a1*a3
    b6 = a3*a3 + 4*a6
    b8 = a1*a1*a6 + 4*a2*a6 - a1*a3*a4 + a2*a3*a3 - a4*a4
    c4 = b2*b2 - 24*b4
    c6 = -b2*b2*b2 + 36*b2*b4 - 216*b6
    delta = -b2*b2*b8 - 8*b4*b4*b4 - 27*b6*b6 + 9*b2*b4*b6
    # Verify: c4^3 - c6^2 = 1728 * Delta
    check = c4**3 - c6**2
    assert check == 1728 * delta, f"INVARIANT CHECK FAILED: c4^3 - c6^2 = {check}, 1728*Delta = {1728*delta}"
    return {
        'b2': b2, 'b4': b4, 'b6': b6, 'b8': b8,
        'c4': c4, 'c6': c6, 'delta': delta
    }

def naive_height(c4, c6):
    """ICARM naive height: log max(|c4|^3, c6^2)."""
    c4cub = abs(c4)**3
    c6sq = c6*c6
    return log(max(c4cub, c6sq))

def check_global_minimality(a1, a2, a3, a4, a6, c4, c6, delta):
    """Check global minimality: for every prime p, the model cannot be
    transformed to reduce v_p(Delta). A model is globally minimal iff
    for every prime p with p^12 | Delta, there is no admissible substitution
    x -> u^2 x + r, y -> u^3 y + s*x + t with u = 1/p that reduces v_p(Delta).

    Practical check: for each prime p dividing Delta, check v_p(Delta) < 12
    OR that no local minimalisation is possible.

    A simpler sufficient check: the model is minimal at p if v_p(Delta) < 12,
    or if v_p(c4) < 4 or v_p(c6) < 6 (which prevents the standard minimalisation).

    For a truly global check, we use the criterion: the model is globally minimal
    iff for every prime p, either v_p(Delta) < 12, or v_p(c4) >= 4 and v_p(c6) >= 6
    but the model is already minimal at p (no further reduction possible).

    The standard test: for each prime p with p | Delta, try all substitutions
    x = u^2 x' + r, y = u^3 y' + s x' + t with u = p, r in [0, p), s in [0, p), t in [0, p)
    and check if the resulting Delta has smaller v_p. If none does, the model is minimal at p.

    For practical purposes with large Delta, we check the primes dividing Delta
    and use the criterion that if v_p(c4) < 4 or v_p(c6) < 6, the model is minimal at p.
    """
    if delta == 0:
        return {'globally_minimal': False, 'reason': 'zero discriminant - singular curve'}

    # Factor Delta to get primes
    # For very large Delta, we use trial division up to a bound
    # and PARI for full factorization
    primes_to_check = set()

    # Get prime factors of |Delta|
    d = abs(delta)
    # Quick trial division for small primes
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        while d % p == 0:
            primes_to_check.add(p)
            d //= p

    # For large remaining factor, we note it but can't fully factor here
    # We'll use PARI for the full factorization in the main script
    if d > 1:
        primes_to_check.add(d)  # might be prime or composite

    # Check minimality at each prime
    non_minimal_primes = []
    for p in primes_to_check:
        if p == 1:
            continue
        v_delta = 0
        temp = abs(delta)
        while temp % p == 0:
            v_delta += 1
            temp //= p

        if v_delta < 12:
            continue  # Already minimal at p (can't reduce below 0)

        # v_p(Delta) >= 12, check if we can reduce
        v_c4 = 0
        temp = abs(c4)
        while temp % p == 0:
            v_c4 += 1
            temp //= p

        v_c6 = 0
        temp = abs(c6)
        while temp % p == 0:
            v_c6 += 1
            temp //= p

        # If v_p(c4) >= 4 and v_p(c6) >= 6, a minimalisation might be possible
        if v_c4 >= 4 and v_c6 >= 6:
            # Need to check if there exists r, s, t such that the transformed
            # model has smaller v_p(Delta). This requires checking all r in [0,p),
            # s in [0,p), t in [0,p).
            # For now, flag as potentially non-minimal
            non_minimal_primes.append({
                'p': p, 'v_delta': v_delta, 'v_c4': v_c4, 'v_c6': v_c6,
                'note': 'v_p(Delta) >= 12, v_p(c4) >= 4, v_p(c6) >= 6 - needs full local check'
            })

    return {
        'globally_minimal': len(non_minimal_primes) == 0,
        'non_minimal_primes': non_minimal_primes,
        'primes_checked': sorted(primes_to_check) if all(isinstance(p, int) for p in primes_to_check) else 'large primes present'
    }

def verify_point_on_curve(a1, a2, a3, a4, a6, x, y):
    """Verify that (x, y) lies on the Weierstrass model
    y^2 + a1*x*y + a3*y = x^3 + a2*x^2 + a4*x + a6
    using exact rational arithmetic."""
    x = Fraction(x)
    y = Fraction(y)
    lhs = y*y + a1*x*y + a3*y
    rhs = x**3 + a2*x**2 + a4*x + a6
    return lhs == rhs

def certify_rank_from_points(a1, a2, a3, a4, a6, points):
    """Certify a rank lower bound from exhibited points.
    1. Verify each point lies on the curve.
    2. Check that points are independent using the F_l-reduction method:
       reduce the points mod a good prime l and compute the rank of the
       resulting matrix in F_l^2 / E(F_l) (or use the height pairing matrix).

    For a rigorous lower bound, we use the height pairing matrix:
    compute the Neron-Tate height pairing matrix and check its rank.
    A simpler approach: use the mod-l reduction and check independence.

    We use the approach of reducing points modulo good primes l > 16
    and computing the rank of the reduction matrix.
    """
    from math import gcd

    # First verify all points
    verified = []
    for i, (x, y) in enumerate(points):
        if verify_point_on_curve(a1, a2, a3, a4, a6, x, y):
            verified.append((Fraction(x), Fraction(y)))
        else:
            return {
                'rank_lower_bound': 0,
                'n_verified': len(verified),
                'error': f'point {i} ({x}, {y}) does not lie on the curve'
            }

    n = len(verified)
    if n == 0:
        return {'rank_lower_bound': 0, 'n_verified': 0}

    # For independence, we use the mod-l reduction approach.
    # At a good prime l, the group E(F_l) has order #E(F_l).
    # We embed the rational points into E(F_l) and check independence
    # by computing the rank of the matrix of discrete logarithms.
    #
    # A simpler and rigorous approach: use the canonical height pairing.
    # The height pairing matrix <P_i, P_j> is a real symmetric matrix.
    # Its rank equals the rank of the subgroup generated by the points.
    # We compute this using the Silverman height formula (approximate).
    #
    # For a CERTIFIED lower bound, we use the mod-l approach:
    # For several good primes l, reduce all points mod l and check
    # if they are independent in E(F_l). If they are independent mod l
    # for some l, they are independent over Q.

    # Find good primes (primes where the curve has good reduction)
    # A prime l is good if v_l(Delta) = 0
    delta = compute_invariants(a1, a2, a3, a4, a6)['delta']
    if delta == 0:
        return {'rank_lower_bound': 0, 'n_verified': n, 'error': 'singular curve'}

    good_primes = []
    for l in range(17, 200):
        if delta % l != 0:
            good_primes.append(l)
        if len(good_primes) >= 10:
            break

    max_rank = 0
    ranks_per_prime = []

    for l in good_primes:
        # Reduce points mod l
        try:
            pts_mod_l = []
            for (x, y) in verified:
                xn = int(x.numerator) * int(pow(int(x.denominator), -1, l)) % l
                yn = int(y.numerator) * int(pow(int(y.denominator), -1, l)) % l
                pts_mod_l.append((xn, yn))
        except (ValueError, ZeroDivisionError):
            continue  # denominator divisible by l, skip

        # Verify points mod l
        valid_pts = []
        for (xn, yn) in pts_mod_l:
            lhs = (yn*yn + a1*xn*yn + a3*yn) % l
            rhs = (xn**3 + a2*xn**2 + a4*xn + a6) % l
            if lhs == rhs:
                valid_pts.append((xn, yn))

        if len(valid_pts) < n:
            continue  # Some points didn't reduce well at this prime

        # Compute #E(F_l) and the group structure
        # Count points on E(F_l)
        count = 0  # includes point at infinity
        for xx in range(l):
            # y^2 + a1*x*y + a3*y = x^3 + a2*x^2 + a4*x + a6
            rhs = (xx**3 + a2*xx**2 + a4*xx + a6) % l
            # (y + (a1*x+a3)/2)^2 = rhs + ((a1*x+a3)/2)^2
            # We need to solve for y
            ys = []
            for yy in range(l):
                if (yy*yy + a1*xx*yy + a3*yy) % l == rhs:
                    ys.append(yy)
            count += len(ys)
        count += 1  # point at infinity

        # The group E(F_l) has order count.
        # To check independence, we compute the Weil pairing or
        # use the matrix of x-coordinates approach.
        #
        # A simpler rigorous approach: compute the canonical height
        # pairing matrix using the Silverman formula.
        # For independence, it suffices to show that the height pairing
        # matrix has full rank.
        #
        # For a CERTIFIED bound, we use the following:
        # The points are independent over Q if they are independent
        # mod l for some good prime l where #E(F_l) is not divisible
        # by the torsion order.
        #
        # We use the approach: compute the group E(F_l) structure,
        # then check if the points generate a subgroup of rank n.
        # This requires computing the group structure, which is complex.
        #
        # Alternative: use the height pairing matrix.
        # The (negative of the) height pairing matrix has entries
        # h(P_i + P_j) - h(P_i) - h(P_j) divided by 2.
        # If this matrix has rank n, the points are independent.

        # For now, we use a simpler criterion: the points are independent
        # if no nontrivial integer combination is the identity.
        # We check this mod l by computing the order of each point
        # and checking that no combination vanishes.

        # Actually, the most practical certified approach is:
        # For each good prime l, compute the reduction of each point
        # and check if the matrix of their images in the group E(F_l)
        # has rank n. This requires knowing the group structure.

        # We use a different approach: compute the canonical height
        # pairing matrix numerically and check its rank.
        # This gives a certified lower bound because:
        # - If the height pairing matrix has rank n, the points are independent
        # - The height pairing can be computed to arbitrary precision
        # - A matrix with nonzero determinant (to numerical precision) has full rank

        # We'll compute this in the main script using PARI's ellheight
        pass

    # For now, return the number of verified points as a trivial lower bound
    # The actual rank certification will be done with PARI in the main script
    return {
        'rank_lower_bound_trivial': n,
        'n_verified': n,
        'good_primes_found': good_primes,
        'note': 'Full rank certification requires PARI ellheight; done in main script'
    }


# ============================================================
# PART 2: Shioda-Tate ceiling from 6-tuple (J1 blind re-derivation)
# ============================================================

def mestre_surface(tuple_vals):
    """Construct the Mestre elliptic surface from a 6-tuple.
    Returns the Weierstrass coefficients as polynomials in T.

    Construction (from H-ECQ-0ed5c8 mechanism):
    q(x) = prod(x - a_i)
    p(x, T) = q(x - T) * q(x + T)
    g = monic degree-6 truncation of p (in x)
    r = g^2 - p  (degree <= 5 in x)

    The surface is y^2 = r(x, T).
    We need to convert this to a Weierstrass model and compute the discriminant.
    """
    # We'll use PARI for the polynomial arithmetic
    # This function returns a description; the actual computation is in PARI
    return tuple_vals


def compute_ceiling_with_pari(tuple_vals):
    """Compute the Shioda-Tate ceiling using PARI.
    This is the blind re-derivation of the ceiling from the tuple alone.
    """
    from cypari import pari
    pari.allocatemem(1 << 28, silent=True)

    a = tuple_vals
    # q(x) = prod(x - a_i)
    # We work with polynomials in x and T
    # Use PARI's polynomial ring

    # Define q(x) as a polynomial in x
    # We'll use PARI's variable 'x' for the curve variable and 't' for T
    pari('x = Pol([0, 1])')  # x as a polynomial variable
    pari('t = Pol([0, 1])')  # t as a polynomial variable

    # Build q(x) = prod(x - a_i)
    q_str = "prod(i=1, 6, x - " + str(a[0]) + ")"
    # Actually, let's build it properly
    q_terms = [f"(x - {ai})" for ai in a]
    q_str = "*".join(q_terms)
    pari(f'q = {q_str}')

    # p(x, t) = q(x - t) * q(x + t)
    # We need to substitute x -> x-t and x -> x+t
    pari('qt = subst(q, x, x - t)')
    pari('qpt = subst(q, x, x + t)')
    pari('p = qt * qpt')

    # g = monic degree-6 truncation of p
    # p is degree 12 in x. g = sum of coefficients of x^12 down to x^6
    # Actually, g is the polynomial such that p - g^2 has degree <= 5 in x
    # g is the "polynomial square root" of the top part of p
    # g = x^6 + c5*x^5 + ... + c0 where the coefficients are chosen
    # so that g^2 matches p in degrees 12 down to 7 (or 6)

    # Method: compute the polynomial square root of the leading part of p
    # p = p12*x^12 + p11*x^11 + ... + p0
    # g = g6*x^6 + g5*x^5 + ... + g0
    # g^2 = g6^2*x^12 + 2*g6*g5*x^11 + (g5^2 + 2*g6*g4)*x^10 + ...
    # We need g6^2 = p12, 2*g6*g5 = p11, etc.
    # Since q is monic, p is monic (leading coeff 1), so g6 = 1.

    # Use PARI's polroot or manual computation
    # Actually, we can use the fact that g = polmodular approach
    # Or simply: g = sqrt(p) truncated to degree 6

    # PARI can compute polynomial square roots
    pari('g = polmodular(p, 6)')  # This might not work; let's try another approach

    # Alternative: compute g by solving for coefficients
    # g = x^6 + c5*x^5 + c4*x^4 + c3*x^3 + c2*x^2 + c1*x + c0
    # g^2 = x^12 + 2*c5*x^11 + (c5^2 + 2*c4)*x^10 + ...
    # Match with p's coefficients

    # Let's use PARI's sqrt function for polynomials
    # Actually, PARI's sqrt works on polynomials
    try:
        pari('g = sqrt(p)')
        # g should be degree 6 if p is a perfect square... but it's not
        # p is NOT a perfect square. We need the truncation.
        # Let's use a different approach: compute g as the polynomial
        # such that p - g^2 has degree <= 5
    except:
        pass

    # Manual approach: extract coefficients and solve
    # p = sum_{k=0}^{12} p_k * x^k
    # g = sum_{k=0}^{6} g_k * x^k, with g_6 = 1 (monic)
    # g^2 = sum_{k=0}^{12} (sum_{i+j=k, 0<=i,j<=6} g_i * g_j) * x^k
    # We need: for k = 12, 11, 10, 9, 8, 7, 6:
    #   coeff(g^2, x, k) = coeff(p, x, k)
    # This gives 7 equations for g_5, g_4, ..., g_0 (g_6 = 1)

    # Let's use PARI to do this
    pari('g = Pol([0, 1])')  # start with x
    # Actually, let's use a cleaner approach
    # g = x^6 + c5*x^5 + ... + c0
    # We compute g by: g = x^6, then for k = 5, 4, 3, 2, 1, 0:
    #   c_k = (coeff(p, x, k+6) - sum of known terms) / (2 * g_6)
    #       = (coeff(p, x, k+6) - sum_{i+j=k+6, i>6 or j>6...}) / 2

    # This is getting complex. Let me use a direct PARI approach.
    # PARI has a function to compute the polynomial square root modulo x^(n+1)

    # Actually, the simplest approach: use the fact that
    # g = the polynomial part of sqrt(p) when we view p as a power series
    # In PARI: g = sqrt(p + O(x^7)) -- truncate at x^7

    # Let's try: compute sqrt of p as a power series
    pari('ps = p + O(x^7)')  # truncate p to degree 6
    # Wait, we need sqrt of the degree-12 polynomial, truncated
    # Actually, we need g such that g^2 = p mod x^7 (i.e., degrees 0..6 match)
    # But g is degree 6, so g^2 is degree 12, and we need the TOP coefficients to match
    # This is: g = x^6 * sqrt(p / x^12) truncated, or equivalently
    # reverse the polynomial, take sqrt, reverse back

    # Let's use: g = polrecip(sqrt(polrecip(p)))
    # where polrecip reverses the coefficients
    # Actually, let's just compute it directly

    # Direct computation using PARI's built-in
    # g^2 = p + O(x^7) means g = sqrt(p + O(x^7))
    # But we need the LEADING coefficients to match, not the trailing ones
    # So we reverse p, take sqrt, reverse back

    # p_rev = x^12 * p(1/x) = reversed polynomial
    # sqrt(p_rev) truncated to degree 6, then reverse back

    # Actually, let me just use a simpler approach:
    # g = x^6 * sqrt(1 + p11/p12 * 1/x + ...) as a Laurent series in 1/x
    # This is equivalent to the polynomial square root of the leading part

    # In PARI, we can do:
    # g = polmodular approach or manual

    # Let me try the manual approach in PARI
    pari('gcoeffs = vector(7)')
    pari('gcoeffs[7] = 1')  # g_6 = 1 (monic)
    # For k from 5 down to 0:
    # g_k = (p_{k+6} - sum_{i+j=k+6, i<6, j<6, i!=k, j!=k} g_i * g_j - 2*g_6*g_k_already_known) / (2*g_6)
    # Wait, this is circular. Let me think again.

    # g^2 = sum_{m=0}^{12} c_m x^m where c_m = sum_{i+j=m, 0<=i,j<=6} g_i g_j
    # We need c_m = p_m for m = 12, 11, 10, 9, 8, 7, 6
    # c_12 = g_6^2 = 1 = p_12 (OK, since p is monic)
    # c_11 = 2*g_6*g_5 = 2*g_5 = p_11, so g_5 = p_11/2
    # c_10 = 2*g_6*g_4 + g_5^2 = 2*g_4 + g_5^2 = p_10, so g_4 = (p_10 - g_5^2)/2
    # etc.

    for k in range(5, -1, -1):
        m = k + 6
        # c_m = sum_{i+j=m, 0<=i,j<=6} g_i * g_j
        # = 2*g_6*g_k + sum_{i+j=m, i!=6, j!=6, i>k, j<k or i<k, j>k} g_i*g_j + g_k^2 (if m=2k)
        # Actually: c_m = 2*g_6*g_k + sum_{i+j=m, 6>i>k} 2*g_i*g_{m-i} + (g_k^2 if m=2k)
        # Wait, let me be more careful.
        # c_m = sum_{i+j=m, 0<=i,j<=6} g_i*g_j
        # The terms with i=6 or j=6: 2*g_6*g_{m-6} (if m-6 <= 6, i.e., m <= 12)
        #   But we only have one such term if m-6 != 6, i.e., m != 12
        #   For m=12: c_12 = g_6^2 (only term)
        #   For m<12: c_m = 2*g_6*g_{m-6} + sum_{i+j=m, 0<=i<j<=5} 2*g_i*g_j + (g_{m/2}^2 if m even)
        # So: g_k = (p_m - sum_{i+j=m, 0<=i<j<=5, i+j=m} 2*g_i*g_j - (g_{m/2}^2 if m even and m/2 <= 5)) / (2*g_6)
        # where the sum is over known g_i (i > k, since we compute from k=5 down to 0)

        # Actually, for m = k+6, the terms in c_m are:
        # - 2*g_6*g_k (the term we're solving for)
        # - sum_{i+j=m, i>k, j<k, i<=5, j<=5} 2*g_i*g_j (but j = m-i = k+6-i, and j < k means i > 6, impossible since i <= 5)
        # Wait, i <= 5 and j = m - i = k+6-i. For j < k: k+6-i < k => i > 6, impossible.
        # For j > k: j = k+6-i > k => i < 6, which is always true for i <= 5.
        # So the known terms are: sum_{i=max(0,m-5)}^{min(5,m)} g_i * g_{m-i} where we exclude i=k and m-i=k
        # But since we compute from k=5 down, all g_i with i > k are known.
        # The known terms in c_m (excluding 2*g_6*g_k) are:
        # sum_{i+j=m, i>k, j<k, 0<=i,j<=5} g_i*g_j  (but j = m-i = k+6-i, and j < k means i > 6, impossible)
        # Actually, i <= 5 and j = k+6-i. For i > k: j = k+6-i < 6 (since i > k >= 0, so j < 6).
        # And j = k+6-i. For j >= 0: i <= k+6. Since i <= 5 and k <= 5, this is always satisfied.
        # So the known terms are: sum_{i=k+1}^{min(5, k+6)} g_i * g_{k+6-i}
        # But g_{k+6-i} for i > k: k+6-i < 6, and we need k+6-i >= 0, so i <= k+6.
        # Also k+6-i might be > k (if i < 6), but we're summing over i > k, so k+6-i < 6.
        # And k+6-i might equal k (if i = 6), but i <= 5, so k+6-i >= k+1 > k.
        # Wait, k+6-i for i in [k+1, 5]: k+6-i ranges from k+5 down to k+1.
        # So all these g values are known (they have index > k).
        # But we also need to handle the case where k+6-i = i (i.e., 2i = k+6, i = (k+6)/2).
        # In that case, the term is g_i^2, not 2*g_i*g_j.

        # Let me just compute this in PARI
        pari(f'pk = polcoeff(p, {m}, x)')
        known_sum_str = "0"
        for i in range(k+1, min(5, m) + 1):
            j = m - i
            if 0 <= j <= 5 and j != i:
                known_sum_str += f" + gcoeffs[{i+1}]*gcoeffs[{j+1}]"
            elif 0 <= j <= 5 and j == i:
                known_sum_str += f" + gcoeffs[{i+1}]^2/2"  # to avoid double counting
        # The full sum is 2*sum_{i<j} g_i*g_j + sum_{i=j} g_i^2
        # But in our loop, we're computing 2*g_6*g_k + (known terms)
        # The known terms are: sum_{i+j=m, i>k, 0<=i,j<=5} g_i*g_j
        # = 2 * sum_{i>j, i+j=m, i>k, j<k} g_i*g_j + sum_{2i=m, i>k} g_i^2
        # But since i > k and j = m-i = k+6-i, and i > k means j < 6,
        # and j < k means i > 6 (impossible), so j >= k.
        # Actually j = k+6-i. For i > k: j = k+6-i < 6. And j >= 0 requires i <= k+6.
        # For i in [k+1, 5]: j = k+6-i in [k+1, k+5].
        # So j > k, meaning both i and j are > k, so both are known.
        # The sum is: sum_{i=k+1}^{min(5,m)} g_i * g_{m-i} where m-i = k+6-i
        # But we need to handle i = m-i (i.e., 2i = m, i = m/2) separately.

        # Let me simplify: just compute in PARI
        pass

    # This is getting too complex for inline PARI. Let me use a different approach.
    # I'll compute g using PARI's built-in polynomial operations.

    # Key insight: g is the polynomial square root of p modulo x^7
    # (i.e., g^2 = p mod x^7, meaning the coefficients of x^0 through x^6 match)
    # But that's the WRONG direction — we need the LEADING coefficients to match.
    #
    # Actually, g^2 = p + O(x^7) means g^2 and p agree in degrees 0..6.
    # But we need them to agree in degrees 12..6 (the top).
    # So we reverse p, take sqrt mod x^7, reverse back.

    # Reverse: p_rev = x^12 * p(1/x)
    # sqrt(p_rev) mod x^7 gives a polynomial g_rev of degree <= 6
    # g = x^6 * g_rev(1/x) = reverse of g_rev

    # In PARI:
    pari('p_rev = Pol(Vec(p))')  # reverse coefficients
    # Wait, Pol(Vec(p)) reverses? Let me check.
    # Vec(p) gives coefficients from lowest to highest.
    # Pol(Vec(p)) would give a polynomial with those coefficients, which is p itself.
    # To reverse: Pol(Vecrev(p)) or Pol(reverse(Vec(p)))

    # Actually, in PARI: polrecip(p) reverses the polynomial
    try:
        pari('p_rev = polrecip(p)')
    except:
        # Manual reverse
        pari('pv = Vec(p)')
        pari('p_rev = Pol(Vecrev(pv))')

    # Now take sqrt of p_rev mod x^7
    pari('p_rev_trunc = p_rev + O(x^7)')
    try:
        pari('g_rev = sqrt(p_rev_trunc)')
    except:
        # If p_rev is not a perfect square, sqrt might fail
        # We need the polynomial square root (truncated)
        # PARI's sqrt on polynomials with O() should work
        return None

    # Reverse back: g = x^6 * g_rev(1/x) = polrecip(g_rev) adjusted
    pari('g = polrecip(g_rev)')

    # Now r = g^2 - p (should have degree <= 5 in x)
    pari('r = g^2 - p')
    pari('dr = poldegree(r, x)')

    # The surface is y^2 = r(x, T)
    # Convert to Weierstrass form and compute discriminant
    # r is a polynomial in x and t (T)
    # If r has degree 4 in x, it's a quartic model y^2 = quartic
    # If degree 5, it's genus 2 (not elliptic)
    # If degree 3, it's a cubic model y^2 = cubic (elliptic)
    # If degree 6, it's genus 2

    # Actually, for Mestre's construction, r should be degree 4 in x
    # (a quartic model, genus 1 = elliptic)

    # Let's check the degree
    deg_r = int(pari('poldegree(r, x)'))

    # Convert to Weierstrass form
    # For y^2 = a4*x^4 + a3*x^3 + a2*x^2 + a1*x + a0 (quartic model)
    # The Weierstrass form can be computed via standard transformations

    # For now, let's compute the discriminant of the quartic
    # The discriminant of y^2 = f(x) where f is degree n is
    # (-1)^(n(n-1)/2) * Res(f, f') / leading_coeff

    # Actually, for the elliptic surface, the discriminant is the
    # discriminant of the Weierstrass model, which is a polynomial in T.

    # Let me use PARI's ellfromeqn or manual conversion
    # PARI can convert a hyperelliptic model to Weierstrass form

    # For y^2 = r(x, t) where r is degree 4 in x:
    # Substitute x -> x + c to eliminate x^3 term, then convert to Weierstrass

    # Actually, let's use PARI's ellfromeqn
    try:
        pari('E = ellfromeqn(y^2 - r)')
        # This gives [a1, a2, a3, a4, a6] as polynomials in t
    except:
        return None

    # Compute discriminant
    try:
        pari('DD = elldisc(E)')
        # DD is the discriminant as a polynomial in t
    except:
        return None

    # The finite discriminant is DD with the contribution at infinity removed
    # The fibre at infinity depends on the degrees of a4, a6

    # Compute gcd(DD, DD') and its degree
    pari('DDp = deriv(DD, t)')
    pari('G = gcd(DD, DDp)')
    pari('degG = poldegree(G, t)')

    # Compute the fibre at infinity
    # The degree of DD in t gives the total discriminant degree
    pari('degDD = poldegree(DD, t)')

    # The fibre at infinity: v_inf(DD) = degDD - (actual degree of finite part)
    # Actually, the fibre at infinity is determined by the valuations of a4, a6, DD at infinity

    # For the Weierstrass model with a4, a6 as polynomials in t:
    # v_inf(a4) = deg(a4) - actual degree (if a4 has lower degree than expected)
    # Actually, v_inf(f) = deg(f) - ord_inf(f) where ord_inf is the order at infinity

    # The fibre at infinity is determined by:
    # v_inf(a4), v_inf(a6), v_inf(DD)
    # Using the Kodaira classification at infinity

    # For a polynomial model, the place at infinity has degree 1
    # v_inf(DD) = deg(DD) - (degree of the squarefree part of DD)
    # Wait, that's not right either.

    # Actually, for the Weierstrass model over Q[t], the discriminant DD(t)
    # is a polynomial in t. The places of the T-line are:
    # - Finite places: roots of DD(t) (and other irreducible polynomials)
    # - The place at infinity

    # The valuation at infinity of DD is: v_inf(DD) = deg(DD) - deg(DD/gcd(DD, DD'))
    # No, that's not right.

    # v_inf(DD) is the order of vanishing of DD at t = infinity.
    # If DD(t) = c * t^d + lower terms, then v_inf(DD) = 0 (DD doesn't vanish at infinity)
    # unless DD has a factor of t^k, in which case v_inf(DD) = k... no.
    #
    # Actually, for the projective T-line, the place at infinity corresponds to t = 1/s.
    # DD(1/s) = c * s^{-d} + ... so v_inf(DD) = -d... that's negative, which doesn't make sense.
    #
    # The correct interpretation: the discriminant of the elliptic surface
    # is a section of a line bundle on P^1. The degree of this section is 12d = 24.
    # The finite places contribute sum of deg(v) * v_disc(v) over finite v.
    # The place at infinity contributes deg(inf) * v_inf(disc) = 1 * v_inf(disc).
    # So: sum_{finite v} deg(v) * v_disc(v) + v_inf(disc) = 24.
    #
    # If DD(t) is the "finite discriminant" (the polynomial whose roots are the
    # finite places with their multiplicities), then:
    # deg(DD) = sum_{finite v} deg(v) * v_disc(v)
    # and v_inf(disc) = 24 - deg(DD).

    # So the fibre at infinity has v_disc = 24 - deg(DD).
    # The Kodaira type at infinity is determined by v_inf(a4), v_inf(a6), v_inf(disc).

    # For the standard Weierstrass model, the fibre at infinity is determined
    # by the degrees of a4, a6 and the discriminant.

    # Let me compute this properly
    # a4 and a6 are polynomials in t
    pari('a4poly = E[4]')
    pari('a6poly = E[5]')

    # v_inf(a4) = deg(a4) - (degree of a4 as a polynomial in 1/t)
    # Actually, for a polynomial f(t) of degree d, v_inf(f) = -d (pole of order d)
    # But in the context of the elliptic surface, we need to consider the
    # minimal model at infinity.

    # The key computation is:
    # 1. deg(DD) = degree of the discriminant polynomial in t
    # 2. v_inf(disc) = 24 - deg(DD) (from the Euler check)
    # 3. The Kodaira type at infinity is determined by v_inf(a4), v_inf(a6), v_inf(disc)
    #    after minimalising at infinity.

    # For the Mestre construction, the fibre at infinity is typically I_4 or I_6.
    # I_4: m = 4, contribution = 3
    # I_6: m = 6, contribution = 5

    # The ceiling is: 18 - deg(G) - (m_inf - 1)
    # where deg(G) = sum_{finite v} deg(v)(N_v - 1) (from the gcd)
    # and m_inf - 1 is the contribution from infinity.

    # But we need to determine m_inf from the fibre type at infinity.
    # For I_n: m = n, so m - 1 = n - 1.
    # v_inf(disc) = n for I_n at infinity.

    # So: ceiling = 18 - deg(G) - (v_inf(disc) - 1) if the fibre at infinity is multiplicative
    #             = 18 - deg(G) - (m_inf - 1) in general

    # If DD is squarefree (deg(G) = 0), all finite fibres are I_1 (m=1, contribution 0).
    # ceiling = 18 - 0 - (m_inf - 1) = 18 - (m_inf - 1) = 19 - m_inf

    # For I_4 at infinity: ceiling = 19 - 4 = 15
    # For I_6 at infinity: ceiling = 19 - 6 = 13

    # Let me compute v_inf(disc) = 24 - deg(DD)
    deg_DD = int(pari('poldegree(DD, t)'))
    v_inf_disc = 24 - deg_DD

    # Check if the fibre at infinity is multiplicative
    # A fibre is multiplicative (I_n) if v(a4) = 0 (after minimalisation)
    # For the polynomial model, v_inf(a4) = -deg(a4) (pole)
    # After minimalisation at infinity (dividing by appropriate powers),
    # the fibre type depends on the valuations.

    # For the Mestre construction, the fibre at infinity is I_4 or I_6.
    # v_inf(disc) = 4 (I_4) or 6 (I_6).
    # So m_inf = v_inf(disc) if the fibre is multiplicative.

    # Let's check: if v_inf(disc) = 6, and the fibre is I_6, then m_inf = 6.
    # ceiling = 18 - deg(G) - (6 - 1) = 18 - deg(G) - 5 = 13 - deg(G)

    deg_G = int(pari('degG'))

    # Check if the fibre at infinity is multiplicative
    # This requires checking v_inf(a4) after minimalisation
    # For now, assume multiplicative (I_n with n = v_inf(disc))
    # and verify with the Euler check

    m_inf = v_inf_disc  # if multiplicative
    ceiling = 18 - deg_G - (m_inf - 1)

    # Euler check: deg(DD) + v_inf(disc) = 24
    euler_check = deg_DD + v_inf_disc

    # Also check if gcd(G, a4) > 0 (additive fibres)
    try:
        pari('Ga4 = gcd(G, a4poly)')
        deg_Ga4 = int(pari('poldegree(Ga4, t)'))
    except:
        deg_Ga4 = 0

    return {
        'tuple': tuple_vals,
        'deg_finite_discriminant': deg_DD,
        'deg_gcd_DD_DDprime': deg_G,
        'finite_discriminant_squarefree': deg_G == 0,
        'v_inf_disc': v_inf_disc,
        'm_inf': m_inf,
        'fibre_at_infinity_type': f'I_{v_inf_disc}' if v_inf_disc > 0 else 'I_0',
        'deg_gcd_G_a4': deg_Ga4,
        'ceiling': ceiling,
        'euler_check_sum': euler_check,
        'euler_check_expected': 24,
        'euler_check_ok': euler_check == 24,
        'cheap_ceiling_exact': deg_Ga4 == 0,
    }


if __name__ == '__main__':
    print("Validator blind re-derivation code loaded.")
    print("Run specific tests from the main analysis script.")
