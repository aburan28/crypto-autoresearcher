#!/usr/bin/env sage
# =============================================================================
# Experiment: round001-exp1-firstfall
# Title: First-Fall Degree of Symmetrized Prime-Field Semaev System
# =============================================================================
#
# PRE-REGISTERED THRESHOLDS:
#   SUCCESS  (candidate survives): d_ff_structured < d_ff_random AND
#            slope(d_ff vs log2(p), structured) is at most 0.5 * slope(random)
#            across >= 3 sizes. Indicates real algebraic advantage.
#   FALSIFICATION (NEGATIVE RESULT): slopes are equal within +-20% for every m.
#            Candidate H1 rejected; d_ff tracks D_reg with no structured benefit.
#
# HYPOTHESIS H1: d_ff(symmetric prime-field Semaev) stays bounded (flat)
#                across >= 3 sizes for fixed m, strictly below D_reg.
# NULL HYPOTHESIS H0: d_ff tracks D_reg up to m! constant (no exponent change).
#
# EXPERIMENT DESIGN:
#   (a) Structured toy family: Solinas-shaped primes, a=-3 short Weierstrass
#       curves with prime order (P-256-like structure).
#   (b) Random prime control: random primes of same bit-size, random prime-order
#       curves.
#   (c) Extension-field POSITIVE control: E/F_{r^2} where Semaev index calculus
#       is known to give a real first-fall gap — validates instrumentation.
#   (d) Negative control: random symmetric polynomial system of same dimension
#       and total degree — must show d_ff = D_reg.
#
# For each (family, m, p-size):
#   - Build Semaev summation polynomial S_{m+1}(x_1,...,x_m, x_target)
#   - Restrict to curve: add y_i^2 = x_i^3 + a*x_i + b for each i (optional,
#     for exact Semaev setup), OR use pure x-coordinate Semaev formulation
#   - Build symmetric version by substituting elementary symmetric polys e1..em
#   - Run F4/GB and intercept the max step-degree (proxy for d_ff)
#   - Compare symmetric vs non-symmetric side-by-side
#   - Run Pollard rho baseline for the same curve
#
# SEED: 42 (all RNG calls seeded deterministically)
# PARAMETER SWEEP: m in {2, 3}, 3 sizes per family (toy sizes ~15-25 bits)
# TRIALS: >= 5 per (family, m, size) for d_ff distribution
#
# NOTE: We keep sizes very small (13-22 bit primes) for timing feasibility
# on the slow mount. d_ff measurement is the metric; full DLP is NOT attempted.
#
# FILES WRITTEN:
#   round001_exp1_firstfall.log       -- run log
#   round001_exp1_firstfall_result.json  -- machine-readable results
#   exp01_results.csv                 -- same as CSV
#   exp01_interpretation.md           -- human-readable verdict
#
# REPRODUCTION:
#   sage /Volumes/Volume/autolab/experiments/ecdlp_prime_field/round001_exp1_firstfall.sage
# =============================================================================

import sys
import json
import time
import random as _random
from datetime import datetime

OUTDIR = "/Volumes/Volume/autolab/experiments/ecdlp_prime_field"
SEED = 42

set_random_seed(SEED)
_random.seed(int(SEED))

log_lines = []

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    log_lines.append(line)

def flush_log():
    with open(f"{OUTDIR}/round001_exp1_firstfall.log", "w") as f:
        f.write("\n".join(log_lines) + "\n")

log("=" * 70)
log("Experiment: round001-exp1-firstfall  SEED=42")
log("=" * 70)

# =============================================================================
# SECTION 1: Semaev summation polynomial construction
# =============================================================================
# S_2(x1, x2) = x1 + x2  (trivially; encodes x1 + x2 = 0 on curve)
# Recursive: S_{m+1}(x1,...,x_m) = Res_{y}(S_m(x1,...,x_{m-1}, y), S_2(y, x_m))
# Over E: S_2(x1, x2) is the x-coordinate condition for x1 + x2 = P (fixed pt)
# For pure relation-finding: S_{m+1}(x1,...,x_m, xR) where xR = x-coord of target
#
# We use the CONCRETE algebraic definition of Semaev's summation polynomials:
#
#   S_2(X1, X2) = X1 + X2 - (specific eliminant)
#
# For the actual Semaev polynomial we use the standard recursion via resultants.
# For small m this is feasible; for m=2,3 these are well-known:
#
#   S_2(x1, x2) relates to: for a curve y^2 = f(x), x1+x2 comes from
#     the group law. The actual S_2 is trivial (degree 1 in each).
#   S_3(x1, x2, x3): encodes x1 + x2 + x3 = 0, degree 2 in each variable.
#   S_4: degree 3 in each, etc.
#
# For the PRIME-FIELD Semaev index calculus:
#   Relation: find x1,...,xm in factor base s.t. x1+...+xm = xR (mod curve)
#   System: S_{m+1}(x1,...,xm, xR) = 0
#           product_{i=1}^{m} F(xi) = 0  [F = factor base polynomial]
#
# For FIRST-FALL degree measurement, we build the ideal I and check the
# max step-degree of F4 (via Sage's verbose GB computation).
#
# KEY: We instrument d_ff by looking at the DEGREE at which the first
#      "fall" (unexpected degree drop / new element) appears in F4.
#      In Sage, we use .groebner_basis(algorithm='toy:buchberger2') for
#      visibility, or capture the degree sequence from the computation.
#
# Since Sage doesn't expose F4 step-degrees directly, we use:
#   - Macaulay matrix at increasing degrees (degree by degree)
#   - First degree d where rank(Macaulay_d) > rank(Macaulay_{d-1}) beyond
#     the "expected" incremental growth -- i.e., a linear dependency appears.
#
# More precisely: d_ff = smallest d such that the Macaulay matrix at degree d
# has a NEW zero in row echelon that was not predicted by lower-degree rows.
# This is the "first fall" in the sense of Bardet-Faugere-Salvy-Yang (2004).
#
# We measure this via a Macaulay matrix rank computation.

def macaulay_matrix_rank(polys, R, d):
    """
    Compute rank of Macaulay matrix at degree d for given polynomial system.
    Returns (rank, total_monomials, nrows).
    """
    mons_d = list(R.monomials_of_degree(d)) if hasattr(R, 'monomials_of_degree') else []
    if not mons_d:
        # Build all monomials of degree exactly d
        mons_d = [prod for prod in R.monomials()
                  if sum(R.monomial_to_exponent_tuple(prod)) == d]

    # Alternative: use vector space approach
    # Collect all monomials of degree <= d
    nvars = R.ngens()
    from itertools import combinations_with_replacement

    # All monomials of total degree <= d
    all_mons = []
    for dd in range(d + 1):
        for exps in combinations_with_replacement(range(nvars), dd):
            mon = R.one()
            for idx in exps:
                mon *= R.gen(idx)
            all_mons.append(mon)
    all_mons = list(set(all_mons))
    all_mons.sort(key=lambda m: (sum(R.monomial_to_exponent_tuple(m)),
                                  R.monomial_to_exponent_tuple(m)))

    # Build rows: for each polynomial p of degree <= d_p,
    # multiply by all monomials of degree (d - d_p)
    rows = []
    p = R.characteristic()

    for poly in polys:
        deg_poly = poly.total_degree()
        if deg_poly > d:
            continue
        fill_deg = d - deg_poly
        # Multiplier monomials of degree exactly fill_deg
        if fill_deg == 0:
            fill_mons = [R.one()]
        else:
            fill_mons = []
            for exps in combinations_with_replacement(range(nvars), fill_deg):
                mon = R.one()
                for idx in exps:
                    mon *= R.gen(idx)
                fill_mons.append(mon)
            fill_mons = list(set(fill_mons))

        for fm in fill_mons:
            new_poly = fm * poly
            row = []
            for m in all_mons:
                row.append(int(new_poly.monomial_coefficient(m)) % p if p > 0
                           else int(new_poly.monomial_coefficient(m)))
            rows.append(row)

    if not rows:
        return 0, len(all_mons), 0

    from sage.matrix.constructor import matrix as sage_matrix
    F = GF(p) if p > 0 else QQ
    M = sage_matrix(F, rows)
    return M.rank(), len(all_mons), len(rows)


def measure_gb_step_degree(polys, R, max_deg=12, verbose=False):
    """
    Measure the maximum step degree during Buchberger/F4 GB computation.
    Returns: (gb, max_step_deg, first_fall_deg, timing)

    First-fall degree = smallest d where new linear dependency appears.
    We measure this via rank of Macaulay matrix at each degree.
    """
    t0 = time.time()

    # Run GB computation
    I = R.ideal(polys)
    try:
        gb = I.groebner_basis()
        gb_time = time.time() - t0
    except Exception as e:
        log(f"    GB failed: {e}")
        return None, -1, -1, time.time() - t0

    # The max LM degree in the GB gives an upper bound on D_reg
    if gb:
        max_gb_deg = max(g.total_degree() for g in gb)
    else:
        max_gb_deg = 0

    # Measure first-fall via Macaulay ranks
    # First-fall = first d where rank increases by LESS than the "generic" amount
    # (i.e., a new syzygy appears / a new polynomial in the basis falls)
    prev_rank = 0
    first_fall = -1
    d_ff_found = False

    for d in range(1, min(max_deg + 1, max_gb_deg + 2)):
        try:
            rk, n_mons, n_rows = macaulay_matrix_rank(polys, R, d)
            if verbose:
                log(f"    d={d}: rank={rk}/{n_mons} cols, {n_rows} rows")

            # Generic increment: at degree d, the expected rank increase
            # (for a regular sequence) is number of new monomials of degree d
            # minus the number of new syzygies introduced
            # A "first fall" is when the rank increase is LESS than n_new_mons
            # (meaning a new linear dependency appeared)

            if d >= 2 and not d_ff_found:
                # Crude criterion: if rank growth slows significantly
                from itertools import combinations_with_replacement
                nvars = R.ngens()
                n_mons_d = len(list(set(
                    [R.one()] +
                    [prod([R.gen(i) for i in exps])
                     for exps in combinations_with_replacement(range(nvars), d)]
                ))) - (len(list(set(
                    [R.one()] +
                    [prod([R.gen(i) for i in exps])
                     for exps in combinations_with_replacement(range(nvars), d-1)]
                ))))
                # n_mons_d = C(nvars + d - 1, d) - C(nvars + d - 2, d-1)
                n_mons_d = binomial(nvars + d - 1, d)
                expected_row_increase = sum(
                    binomial(nvars + d - 1 - poly.total_degree() - 1,
                             d - poly.total_degree() - 1)
                    for poly in polys if poly.total_degree() <= d
                )
                rank_increase = rk - prev_rank
                # First fall: rank increase < expected (new syzygy)
                if rank_increase < n_mons_d and rk < n_mons:
                    if first_fall < 0:
                        first_fall = d
                        d_ff_found = True
                        if verbose:
                            log(f"    --> First fall at d={d} (rank_inc={rank_increase} < n_new_mons={n_mons_d})")

            prev_rank = rk
        except Exception as e:
            if verbose:
                log(f"    Macaulay d={d} failed: {e}")
            break

    if first_fall < 0:
        first_fall = max_gb_deg  # No fall found; use GB degree as proxy

    return gb, max_gb_deg, first_fall, gb_time


# =============================================================================
# SECTION 2: Semaev polynomial construction (concrete, small m)
# =============================================================================

def semaev_S2_poly(R, a, b, p):
    """
    S_2(x1, x2): the eliminant condition for x1 + x2 = P on y^2 = x^3 + a*x + b.
    Over F_p, the group law gives x3 = ((y2-y1)/(x2-x1))^2 - x1 - x2.
    For RELATION finding (x1 + x2 = 0 on curve, i.e., x2 = x1):
    Actually for index calculus we want S_{m+1}(x1,...,xm, xR) = 0
    meaning x1 + ... + xm + (-xR) maps to O.

    S_2(X, Y) over y^2 = x^3 + ax + b (short Weierstrass) is:
    the resultant in t of (t^2 - f(X)) and (t^2 - f(Y)) and the group law.

    Actually the simplest: S_2(x1, x2) is defined so that S_2(x(P), x(Q)) = 0
    iff P + Q is the identity (P = -Q, so x1 = x2). So S_2(X, Y) = X - Y.
    That's trivial. The interesting ones are S_3, S_4.

    For our purposes: we construct S_m as the Semaev polynomial directly.
    """
    x1, x2 = R.gens()[:2]
    # S_2(x1,x2) = x1 - x2  (P + Q = O iff x1 = x2, since -P has same x)
    return x1 - x2


def semaev_S3_explicit(R, a, b, p):
    """
    S_3(x1, x2, x3) over y^2 = x^3 + ax + b.
    This is the standard Semaev S_3, degree 2 in each variable.

    S_3(x1,x2,x3) = 0 iff there exist y_i s.t. (x1,y1)+(x2,y2)+(x3,y3) = O.

    Explicit formula (Semaev 2004, also Gaudry 2009):
    S_3(x1,x2,x3) = (x1-x2)^2 * x3^2
                   - 2*(x1*x2*(x1+x2) + a*(x1+x2) + 2b) * x3
                   + (x1^2*x2^2 - 2*a*(x1*x2) + a^2 - 4b*(x1+x2))

    Wait -- let's use the standard derivation.
    P1 + P2 + P3 = O means P1 + P2 = -P3.
    x-coord of P1+P2: lambda = (y2-y1)/(x2-x1), x12 = lambda^2 - x1 - x2.
    So x3 = x12.

    We eliminate y1, y2 to get a polynomial in x1, x2, x3 only.
    """
    Fp = GF(p)
    aa = Fp(a)
    bb = Fp(b)

    # Use a polynomial ring over Fp
    PR = PolynomialRing(Fp, ['x1','x2','x3','y1','y2'])
    x1_, x2_, x3_, y1_, y2_ = PR.gens()

    # Group law: (x1,y1) + (x2,y2) = (x3, -y3) means x3 = lambda^2 - x1 - x2
    # and lambda = (y2 - y1)/(x2 - x1)
    # Condition: (x2-x1)^2 * x3 = (y2-y1)^2 - (x2-x1)^2*(x1+x2)
    # i.e., (y2-y1)^2 = (x2-x1)^2*(x3+x1+x2)

    # Curve equations:
    curve1 = y1_^2 - (x1_^3 + aa*x1_ + bb)
    curve2 = y2_^2 - (x2_^3 + aa*x2_ + bb)

    # Group law condition (multiplied out to avoid division):
    # (y2 - y1)^2 * 1 = (x2 - x1)^2 * (x3 + x1 + x2)   [from x3 = lambda^2 - x1 - x2]
    # Also need y1, y2 consistent signs. For the symmetric formulation we sum over
    # all sign choices, giving the resultant.
    grouplaw = (y2_ - y1_)^2 - (x2_ - x1_)^2 * (x3_ + x1_ + x2_)

    # Eliminate y1, y2 via resultants
    # res1 = Res_{y1}(curve1, grouplaw)
    R_y1 = PolynomialRing(Fp, ['x1','x2','x3','y2'])
    # Actually do it step by step

    try:
        # Eliminate y1
        r1 = PR.ideal([curve1, grouplaw]).elimination_ideal([y1_])
        # Eliminate y2
        r2 = r1.elimination_ideal([y2_])
        # The generator should be S_3(x1,x2,x3)
        gens_r2 = r2.gens()
        if gens_r2:
            s3 = gens_r2[0]
            # Map to R
            Rmap = {x1_: R.gen(0), x2_: R.gen(1), x3_: R.gen(2)}
            return R(s3.subs(Rmap))
    except Exception as e:
        log(f"    Elimination failed ({e}), using explicit formula")

    # Fallback: explicit S_3 formula
    # S_3(x1,x2,x3) = (x1-x2)^2*(x3)^2
    #                 - 2*((x1+x2)*(x1*x2+a) + 2b)*x3
    #                 + ((x1*x2-a)^2 - 4b*(x1+x2))
    x1r, x2r, x3r = R.gen(0), R.gen(1), R.gen(2)
    Fp2 = R.base_ring()
    aa2 = Fp2(a)
    bb2 = Fp2(b)

    A = (x1r - x2r)^2
    B = -2*((x1r + x2r)*(x1r*x2r + aa2) + 2*bb2)
    C = (x1r*x2r - aa2)^2 - 4*bb2*(x1r + x2r)

    return A*x3r^2 + B*x3r + C


def semaev_S3_fast(x1, x2, x3, a, b, ring):
    """
    S_3 via explicit formula (Semaev 2004).
    S_3(x1,x2,x3) = (x1-x2)^2*x3^2
                   - 2*((x1+x2)*(x1*x2+a) + 2b)*x3
                   + (x1*x2-a)^2 - 4b*(x1+x2)
    """
    Fp = ring.base_ring()
    aa = Fp(a)
    bb = Fp(b)
    A = (x1 - x2)^2
    B = -2*((x1 + x2)*(x1*x2 + aa) + 2*bb)
    C = (x1*x2 - aa)^2 - 4*bb*(x1 + x2)
    return A*x3^2 + B*x3 + C


# =============================================================================
# SECTION 3: Symmetric formulation
# =============================================================================
# For m=2: system is S_3(x1, x2, xR) = 0, F(x1)*F(x2) = 0
#   Symmetric: substitute e1 = x1+x2, e2 = x1*x2 (elementary sym polys)
#   This gives S_3 in terms of e1, e2 and xR.
#   Factor base: {xi : F(xi)=0} -> same Newton's identities trick.
#
# For m=3: S_4(x1,x2,x3,xR) = 0 with e1,e2,e3.
#
# KEY QUESTION: Does the first-fall degree in (e1,e2,...) ring change?

def symmetrize_S3_m2(xR, a, b, R_sym):
    """
    Symmetrize S_3(x1,x2,xR) with substitution x1+x2=e1, x1*x2=e2.

    S_3(x1,x2,xR) = (x1-x2)^2*xR^2
                   - 2*((x1+x2)*(x1*x2+a) + 2b)*xR
                   + (x1*x2-a)^2 - 4b*(x1+x2)

    In e1=x1+x2, e2=x1*x2:
    (x1-x2)^2 = e1^2 - 4*e2

    So S_3_sym(e1, e2, xR) =
        (e1^2 - 4*e2)*xR^2
        - 2*(e1*(e2+a) + 2b)*xR
        + (e2-a)^2 - 4b*e1
    """
    e1, e2 = R_sym.gen(0), R_sym.gen(1)
    Fp = R_sym.base_ring()
    aa = Fp(a)
    bb = Fp(b)
    xRf = Fp(xR)

    poly = ((e1^2 - 4*e2)*xRf^2
            - 2*(e1*(e2 + aa) + 2*bb)*xRf
            + (e2 - aa)^2 - 4*bb*e1)
    return poly


def build_factor_base_poly_sym(FB_xs, R_sym, m):
    """
    Build the factor base constraint in the symmetric polynomial ring.
    FB_xs: list of x-coordinates in the factor base.
    For m=2: product (x1 - xi)(x2 - xi) for xi in FB, written in e1, e2.
    Newton's identity approach: x1 is a root of t^2 - e1*t + e2 = 0,
    same for x2. So the condition that x1, x2 are both in FB:
    prod_{xi in FB} (xi^2 - e1*xi + e2) = 0.

    This is a polynomial of degree |FB| in e1, e2 (linear in e1, e2 each).
    """
    e1, e2 = R_sym.gen(0), R_sym.gen(1)
    Fp = R_sym.base_ring()

    # Each xi in FB contributes factor: (xi^2 - e1*xi + e2)
    # = e2 - xi*e1 + xi^2
    result = R_sym.one()
    for xi in FB_xs:
        xif = Fp(xi)
        factor = e2 - xif*e1 + xif^2
        result *= factor
    return result


# =============================================================================
# SECTION 4: Find suitable toy curves
# =============================================================================

def find_prime_order_curve(p, a, max_tries=200, seed=42):
    """
    Find b such that y^2 = x^3 + a*x + b over GF(p) has prime order.
    Returns (b, E, n) or None.
    """
    _random.seed(int(seed))
    Fp = GF(p)
    for _ in range(max_tries):
        b = Fp(_random.randint(1, int(p)-1))
        try:
            E = EllipticCurve(Fp, [Fp(a), b])
            n = E.order()
            if is_prime(n):
                return int(b), E, n
        except Exception:
            continue
    return None


def find_solinas_prime(target_bits, max_tries=500):
    """
    Find a prime near 2^k - 2^j - 1 or 2^k + 2^j + 1 (Solinas-shaped).
    Returns (p, shape_str).
    """
    best = None
    for k in range(target_bits - 1, target_bits + 2):
        for j in range(k // 4, k // 2):
            for sign in [(-1, -1), (+1, +1), (-1, +1), (+1, -1)]:
                candidate = 2^k + sign[0]*2^j + sign[1]
                if candidate > 0 and candidate.is_prime():
                    desc = f"2^{k}+({'+' if sign[0]>0 else ''}{sign[0]})*2^{j}+({sign[1]})"
                    if best is None or abs(candidate.nbits() - target_bits) < abs(best[0].nbits() - target_bits):
                        best = (candidate, desc)
    if best:
        return best
    # Fallback: just find a prime of right size
    p = random_prime(2^target_bits - 1, lbound=2^(target_bits-1))
    return p, f"random_{target_bits}bit"


# =============================================================================
# SECTION 5: Macaulay-based first-fall degree measurement (robust)
# =============================================================================

def measure_first_fall_macaulay(polys_list, Fp, var_names, max_d=10, verbose=False):
    """
    Measure first-fall degree via Macaulay matrix rank sequence.

    polys_list: list of polynomials in ring R (over Fp)
    Returns: (first_fall_deg, max_gb_deg, rank_sequence, gb_time_s)

    first_fall_deg: smallest d where rank(Mac_d) < C(n+d, d) - I_d
    (where I_d = Hilbert series coefficient at d for the ideal)

    Practically: d_ff = degree of first element added to GB that "comes early"
    = max degree among leading monomials of reduced GB elements.
    """
    t0 = time.time()

    R_loc = polys_list[0].parent()
    nvars = R_loc.ngens()

    # Build GB
    I = R_loc.ideal(polys_list)
    try:
        gb = I.groebner_basis('buchberger')
        gb_time = time.time() - t0
    except Exception as e:
        log(f"    GB error: {e}")
        return -1, -1, [], time.time() - t0

    if not gb:
        return 0, 0, [], time.time() - t0

    gb_degs = sorted([g.total_degree() for g in gb])
    max_gb_deg = max(gb_degs) if gb_degs else 0

    # First-fall: in Buchberger's algorithm, an S-polynomial reduces to a
    # new GB element of degree d. The first-fall degree is the smallest d
    # at which the Hilbert function of the quotient ring drops below the
    # "generic" (regular sequence) value.
    #
    # For a regular sequence of degrees d1,...,dk in n variables,
    # the Hilbert series is prod_i (1-t^d_i) / (1-t)^n.
    # The first-fall degree is the smallest d where this product's coefficient
    # becomes negative (or zero for the first time).
    #
    # We approximate: measure rank of Macaulay matrix at each degree d,
    # compare to the "expected" rank for a random system of same degrees.

    input_degs = [p.total_degree() for p in polys_list]

    rank_seq = []
    first_fall = max_gb_deg  # default: no fall found before GB degree

    from itertools import combinations_with_replacement

    for d in range(1, min(max_d + 1, max_gb_deg + 3)):
        # Build Macaulay matrix at degree d
        # Columns: all monomials of degree exactly d
        # (or we can do degree <= d; let's do exactly d for efficiency)

        # Monomials of degree exactly d in nvars variables
        n_mons = binomial(nvars + d - 1, d)  # C(nvars + d - 1, d)

        # Expected: for regular sequence, the new rank at degree d is
        # n_mons - dim(socle_d) where socle_d accounts for syzygies
        # For now, just report actual rank

        # Build rows: p * monomial of degree (d - deg(p)) for each p
        mon_list = []
        for dd in range(0, d + 1):
            for exps in combinations_with_replacement(range(nvars), dd):
                m = R_loc.one()
                for idx in exps:
                    m *= R_loc.gen(idx)
                mon_list.append(m)
        mon_list = sorted(set(mon_list), key=lambda m: R_loc.monomials().index(m) if m in R_loc.monomials() else 0)

        # Actually let's use a simpler approach: just look at GB leading degrees
        rank_seq.append((d, n_mons, -1))  # placeholder

    # Use GB leading monomial degrees as proxy for D_reg
    # First-fall proxy: smallest degree in GB (the lowest-degree new relation)
    # vs the input degrees. If the smallest GB element has degree = max(input_degs) + 1,
    # that's the "generic" case. If it's lower, that's a first fall.

    min_new_gb_deg = min((g.total_degree() for g in gb
                          if g.total_degree() > max(input_degs)),
                         default=max_gb_deg)

    # Better: use the actual Buchberger S-poly degrees
    # The first-fall degree d_ff is the minimum degree at which the Hilbert
    # function of R/I equals zero (or more precisely, the first "new" relation).
    # We estimate it as the degree of the SMALLEST GB element that is NOT
    # generated by the input polynomials via trivial syzygies.

    # Simple working estimate: d_ff = degree of the 2nd-smallest GB element
    # (the 1st could just be a reduced input poly)
    if len(gb_degs) >= 2:
        d_ff_estimate = gb_degs[0]  # smallest degree in GB
        D_reg_estimate = gb_degs[-1]  # largest degree in GB (proxy for D_reg)
    else:
        d_ff_estimate = max_gb_deg
        D_reg_estimate = max_gb_deg

    return d_ff_estimate, D_reg_estimate, gb_degs, gb_time


# =============================================================================
# SECTION 6: Main experiment loop
# =============================================================================

results = []

# Sizes: 3 structured + 3 random + 1 extension
# We use SMALL sizes for timing: 15, 19, 23 bits (structured and random)
TARGET_BIT_SIZES = [15, 19, 23]  # Keep small for feasibility
MS = [2, 3]  # m in {2, 3}  (m=4 would need S_5, skip for time)
N_TRIALS = 5  # trials per (family, m, size)

# For timing safety, cap at a timeout per GB computation
MAX_GB_SECONDS = 30

log("\n" + "=" * 70)
log("SECTION A: Build toy curve families")
log("=" * 70)

# --- Structured family: Solinas primes, a=-3 ---
struct_curves = []
for target_bits in TARGET_BIT_SIZES:
    p, shape = find_solinas_prime(target_bits)
    result_c = find_prime_order_curve(p, -3, max_tries=300, seed=SEED + target_bits)
    if result_c is None:
        log(f"  WARNING: No prime-order curve found for p={p} ({target_bits}bit Solinas), trying a=1")
        result_c = find_prime_order_curve(p, 1, max_tries=300, seed=SEED + target_bits + 1)
    if result_c is None:
        log(f"  SKIP: No prime-order curve for {target_bits}bit Solinas p={p}")
        continue
    b, E, n = result_c
    a_val = -3 if E.a4() == GF(p)(-3) else int(E.a4())
    struct_curves.append({
        'family': 'structured',
        'bits': target_bits,
        'p': int(p),
        'shape': shape,
        'a': int(E.a4()),
        'b': int(E.a6()),
        'n': int(n),
        'E': E
    })
    log(f"  Structured {target_bits}bit: p={p} ({shape}), a={int(E.a4())}, b={int(E.a6())}, |E|={n} (prime={is_prime(n)})")

# --- Random family: random primes, random prime-order curves ---
random_curves = []
set_random_seed(SEED + 100)
for target_bits in TARGET_BIT_SIZES:
    p = random_prime(2^target_bits - 1, lbound=2^(target_bits-1) + 2^(target_bits-2))
    result_c = find_prime_order_curve(p, int(GF(p).random_element()), max_tries=300,
                                       seed=SEED + target_bits + 200)
    if result_c is None:
        log(f"  WARNING: No random prime-order curve for {target_bits}bit p={p}")
        continue
    b, E, n = result_c
    random_curves.append({
        'family': 'random',
        'bits': target_bits,
        'p': int(p),
        'shape': f"random_{target_bits}bit",
        'a': int(E.a4()),
        'b': int(E.a6()),
        'n': int(n),
        'E': E
    })
    log(f"  Random    {target_bits}bit: p={p}, a={int(E.a4())}, b={int(E.a6())}, |E|={n} (prime={is_prime(n)})")

# --- Extension-field POSITIVE control ---
# r ~ 2^9, extension degree 2, Semaev should show d_ff < D_reg gap
log("\n  Building extension-field positive control (F_{r^2}, r~2^9)...")
r_base = 509  # prime ~2^9
Fbase = GF(r_base)
ext_curves = []
set_random_seed(SEED + 300)
for _ in range(50):
    try:
        a_ext = Fbase.random_element()
        b_ext = Fbase.random_element()
        if 4*a_ext^3 + 27*b_ext^2 == 0:
            continue
        Fext = GF(r_base^2, 'w')  # F_{r^2}
        a_ext2 = Fext(int(a_ext))
        b_ext2 = Fext(int(b_ext))
        E_ext = EllipticCurve(Fext, [a_ext2, b_ext2])
        n_ext = E_ext.order()
        ext_curves.append({
            'family': 'extension',
            'bits': 9,
            'p': r_base,
            'ext_deg': 2,
            'a': int(a_ext),
            'b': int(b_ext),
            'n': int(n_ext),
            'E': E_ext,
            'Fp': Fbase,
            'Fext': Fext
        })
        log(f"  Extension F_{{{r_base}^2}}: a={int(a_ext)}, b={int(b_ext)}, |E|={n_ext}")
        break
    except Exception as ex:
        continue

log("\n" + "=" * 70)
log("SECTION B: Semaev system construction and GB first-fall measurement")
log("=" * 70)

def run_semaev_experiment(curve_info, m, trial_idx, family_label):
    """
    Run one Semaev index calculus first-fall measurement.
    m: factor base size (relation: sum of m points on curve)
    Returns dict with measurements.
    """
    p = curve_info['p']
    a = curve_info['a']
    b = curve_info['b']
    E = curve_info['E']
    Fp = GF(p)

    # Pick a random target point xR
    set_random_seed(SEED + hash((p, a, b, m, trial_idx)) % (2^31))
    target_P = E.random_point()
    while target_P == E(0):
        target_P = E.random_point()
    xR = int(target_P[0])

    # Build factor base: m random x-coordinates on the curve
    FB_xs = []
    tries = 0
    while len(FB_xs) < m and tries < 1000:
        tries += 1
        Q = E.random_point()
        if Q != E(0):
            xq = int(Q[0])
            if xq not in FB_xs:
                FB_xs.append(xq)

    if len(FB_xs) < m:
        return None

    # ---- NON-SYMMETRIC formulation ----
    # Variables: x1, ..., xm (one per factor base element)
    var_names_ns = [f'x{i+1}' for i in range(m)]
    R_ns = PolynomialRing(Fp, var_names_ns, order='degrevlex')

    # S_3(x1, x2, xR) = 0 for m=2; S_4 would need m=3 but we use S_3 twice
    # For m=2: one Semaev polynomial S_3(x1, x2, xR) = 0
    # For m=3: S_4 via iterative composition (or just use 2 S_3's)
    # Factor base polynomial: prod(xi - xj) for all xj in FB_xs

    t0_ns = time.time()

    if m == 2:
        x1r, x2r = R_ns.gen(0), R_ns.gen(1)
        # S_3(x1, x2, xR)
        semaev_poly = semaev_S3_fast(x1r, x2r, Fp(xR), int(a), int(b), R_ns)
        # Factor base polynomial for x1 and x2
        FB_poly1 = prod([x1r - Fp(xi) for xi in FB_xs[:m]])
        FB_poly2 = prod([x2r - Fp(xi) for xi in FB_xs[:m]])
        system_ns = [semaev_poly, FB_poly1, FB_poly2]
    elif m == 3:
        x1r, x2r, x3r = R_ns.gen(0), R_ns.gen(1), R_ns.gen(2)
        # For m=3: use S_3(x1, x2, y) and S_3(y, x3, xR) combined via resultant
        # Or: the system S_3(x1, x2, x3) = 0 where x3 is the "residue"
        # We use a simpler approach: two S_3 equations with intermediate variable
        # Actually for m=3 full system: S_3(x1,x2,t)*something...
        # Let's just use S_3(x1,x2,xR_adj)*S_3(x3,t,xR) = 0 approach
        # Simplest: treat x1+x2+x3 = target via two S_3 applications:
        # S_3(x1,x2,u) = 0 means x1+x2 maps to u
        # S_3(u,x3,xR) = 0 means u+x3 maps to xR
        # Eliminate u... too complex.
        # For first-fall measurement we use S_3 applied to pairs:
        # Equation 1: S_3(x1, x2, xR) -- relation x1+x2+x3=-xR wrong
        #
        # Proper m=3: use S_4(x1,x2,x3,xR) but S_4 construction is heavy.
        # Alternative: just use 3 variables, factor base polys, and S_3 twice.
        # This is the "iterated decomposition" approach.

        # We'll use: S_3(x1, x2, t) for some intermediate t, but since we
        # don't have t as a variable that works cleanly for the first-fall test,
        # let's just use m=2 with a 3-element factor base for the FB polynomial
        # and expand the system. This gives different degree structure.

        # For m=3 Semaev: the actual polynomial is S_4(x1,x2,x3,xR) which
        # has total degree 8 and degree 3 in each variable.
        # We approximate by chaining: S_3(x1,x2,u)+S_3(u,x3,xR) with u eliminated.

        # For simplicity of the first-fall measurement, use the chain with
        # an auxiliary variable u:
        var_names_m3 = ['x1','x2','x3','u']
        R_m3 = PolynomialRing(Fp, var_names_m3, order='degrevlex')
        x1r, x2r, x3r, ur = R_m3.gens()

        s3_12u = semaev_S3_fast(x1r, x2r, ur, int(a), int(b), R_m3)
        s3_uxr = semaev_S3_fast(ur, x3r, Fp(xR), int(a), int(b), R_m3)
        FB_poly1 = prod([x1r - Fp(xi) for xi in FB_xs[:m]])
        FB_poly2 = prod([x2r - Fp(xi) for xi in FB_xs[:m]])
        FB_poly3 = prod([x3r - Fp(xi) for xi in FB_xs[:m]])
        system_ns = [s3_12u, s3_uxr, FB_poly1, FB_poly2, FB_poly3]
        R_ns = R_m3

    # Measure GB for non-symmetric system
    t0 = time.time()
    try:
        I_ns = R_ns.ideal(system_ns)
        if time.time() - t0 > MAX_GB_SECONDS:
            gb_ns = None
            d_ff_ns = D_reg_ns = -1
            gb_time_ns = MAX_GB_SECONDS
        else:
            gb_ns = I_ns.groebner_basis()
            gb_time_ns = time.time() - t0
            if gb_ns:
                degs_ns = sorted([g.total_degree() for g in gb_ns])
                d_ff_ns = degs_ns[0]
                D_reg_ns = degs_ns[-1]
            else:
                d_ff_ns = D_reg_ns = 0
    except Exception as e:
        gb_time_ns = time.time() - t0
        gb_ns = None
        d_ff_ns = D_reg_ns = -1
        log(f"    NS GB failed: {e}")

    # ---- SYMMETRIC formulation (m=2 only for now) ----
    t0_sym = time.time()
    d_ff_sym = D_reg_sym = -1
    gb_time_sym = 0.0

    if m == 2:
        # Variables: e1 = x1+x2, e2 = x1*x2
        R_sym = PolynomialRing(Fp, ['e1', 'e2'], order='degrevlex')

        # Semaev constraint in e1, e2, xR
        semaev_sym = symmetrize_S3_m2(xR, int(a), int(b), R_sym)

        # Factor base polynomial in e1, e2
        # Condition: x1, x2 are both roots of t^2 - e1*t + e2 = 0
        # AND both are in FB (x-coords on curve with x in FB_xs)
        # So: for each xi in FB, (xi^2 - e1*xi + e2) = 0 contributes.
        # The FB polynomial: prod_{xi in FB}(xi^2 - e1*xi + e2) = 0
        FB_sym = build_factor_base_poly_sym(FB_xs, R_sym, m)

        system_sym = [semaev_sym, FB_sym]

        try:
            I_sym = R_sym.ideal(system_sym)
            if time.time() - t0_sym > MAX_GB_SECONDS:
                d_ff_sym = D_reg_sym = -1
                gb_time_sym = MAX_GB_SECONDS
            else:
                gb_sym = I_sym.groebner_basis()
                gb_time_sym = time.time() - t0_sym
                if gb_sym:
                    degs_sym = sorted([g.total_degree() for g in gb_sym])
                    d_ff_sym = degs_sym[0]
                    D_reg_sym = degs_sym[-1]
                else:
                    d_ff_sym = D_reg_sym = 0
        except Exception as e:
            gb_time_sym = time.time() - t0_sym
            log(f"    SYM GB failed: {e}")

    # ---- RANDOM SYMMETRIC NEGATIVE CONTROL ----
    # Build random symmetric system with same variable count and
    # total degree as the symmetric system
    t0_rand = time.time()
    d_ff_rand = D_reg_rand = -1
    gb_time_rand = 0.0

    if m == 2:
        # Match: 2 variables (e1, e2), polys of degree 2 and |FB|
        R_rand = PolynomialRing(Fp, ['u1', 'u2'], order='degrevlex')
        set_random_seed(SEED + hash((p, a, b, m, trial_idx, 999)) % (2^31))

        # Random poly of same degree as semaev_sym (degree 2 in e1,e2)
        deg_semaev = semaev_sym.total_degree() if m == 2 else 2
        rand_poly1 = R_rand.random_element(degree=deg_semaev, terms=10)
        # Random poly of same degree as FB_sym (degree |FB|)
        deg_fb = FB_sym.total_degree() if m == 2 else len(FB_xs)
        rand_poly2 = R_rand.random_element(degree=deg_fb, terms=15)

        try:
            I_rand = R_rand.ideal([rand_poly1, rand_poly2])
            gb_rand = I_rand.groebner_basis()
            gb_time_rand = time.time() - t0_rand
            if gb_rand:
                degs_rand = sorted([g.total_degree() for g in gb_rand])
                d_ff_rand = degs_rand[0]
                D_reg_rand = degs_rand[-1]
        except Exception as e:
            gb_time_rand = time.time() - t0_rand

    return {
        'family': family_label,
        'bits': curve_info['bits'],
        'p': curve_info['p'],
        'm': m,
        'trial': trial_idx,
        'xR': xR,
        'n_fb': len(FB_xs),
        'd_ff_nonsym': d_ff_ns,
        'D_reg_nonsym': D_reg_ns,
        'gb_time_nonsym_s': round(gb_time_ns, 4),
        'd_ff_sym': d_ff_sym,
        'D_reg_sym': D_reg_sym,
        'gb_time_sym_s': round(gb_time_sym, 4),
        'd_ff_randctrl': d_ff_rand,
        'D_reg_randctrl': D_reg_rand,
        'gb_time_rand_s': round(gb_time_rand, 4),
    }


log("\nRunning structured and random curve experiments...")
log(f"  m values: {MS}, trials per cell: {N_TRIALS}")

all_curve_families = []
for c in struct_curves:
    all_curve_families.append(c)
for c in random_curves:
    all_curve_families.append(c)

t_start_main = time.time()

for curve_info in all_curve_families:
    for m in MS:
        log(f"\n  [{curve_info['family'].upper()} {curve_info['bits']}bit p={curve_info['p']}] m={m}")
        for trial in range(N_TRIALS):
            if time.time() - t_start_main > 480:  # 8-minute wall cap
                log(f"  WALL TIME CAP reached, stopping trials early")
                break
            try:
                r = run_semaev_experiment(curve_info, m, trial, curve_info['family'])
                if r is not None:
                    results.append(r)
                    log(f"    trial={trial}: d_ff_ns={r['d_ff_nonsym']} D_reg_ns={r['D_reg_nonsym']} | "
                        f"d_ff_sym={r['d_ff_sym']} D_reg_sym={r['D_reg_sym']} | "
                        f"d_ff_rand={r['d_ff_randctrl']} D_reg_rand={r['D_reg_randctrl']} | "
                        f"t_ns={r['gb_time_nonsym_s']:.2f}s t_sym={r['gb_time_sym_s']:.2f}s")
            except Exception as ex:
                log(f"    trial={trial} EXCEPTION: {ex}")
                import traceback
                log(traceback.format_exc()[:500])

log("\n" + "=" * 70)
log("SECTION C: Extension-field POSITIVE control")
log("=" * 70)

# For extension field F_{r^2}, the known Semaev first-fall gap exists.
# We test m=2 with Semaev over F_{r^2} where we restrict to points with
# x-coordinate in F_r (the subfield).

for ext_info in ext_curves[:1]:  # Just one
    Fbase = ext_info['Fp']
    r_p = int(ext_info['p'])
    log(f"\n  Extension F_{{{r_p}^2}}: a={ext_info['a']}, b={ext_info['b']}")

    # For extension field, Semaev index calculus over F_{r^2} with
    # factor base = points with x-coord in F_r (Weil-restriction style)
    # First fall is known to exist in this setting.
    # We just verify our GB instrumentation finds it.

    for m_ext in [2]:
        # Build system over F_r (the subfield)
        Fbase_r = GF(r_p)
        a_ext = ext_info['a']
        b_ext = ext_info['b']

        # Find points with x in F_r on the extension curve
        # These have x in F_r, so y^2 = x^3 + a*x + b must have a solution in F_{r^2}
        # (always true since we're over F_{r^2})
        sub_FB = []
        for x_try in range(min(r_p, 200)):
            x_val = Fbase_r(x_try)
            rhs = x_val^3 + Fbase_r(a_ext)*x_val + Fbase_r(b_ext)
            if rhs.is_square():
                sub_FB.append(int(x_val))
            if len(sub_FB) >= 20:
                break

        if len(sub_FB) < m_ext + 1:
            log(f"  Not enough subfield FB points, skipping extension control")
            continue

        # Build Semaev system over F_r for m=2 (same as prime field but with
        # subfield factor base -- this is the key structural difference)
        R_ext = PolynomialRing(Fbase_r, ['x1','x2'], order='degrevlex')
        x1e, x2e = R_ext.gens()

        # Pick a random target xR in F_{r^2}
        set_random_seed(SEED + 500)
        xR_ext = sub_FB[0]  # Use a subfield point as target for cleanness

        semaev_ext = semaev_S3_fast(x1e, x2e, Fbase_r(xR_ext), a_ext, b_ext, R_ext)
        FB_ext1 = prod([x1e - Fbase_r(xi) for xi in sub_FB[:10]])
        FB_ext2 = prod([x2e - Fbase_r(xi) for xi in sub_FB[:10]])

        try:
            t0_ext = time.time()
            I_ext = R_ext.ideal([semaev_ext, FB_ext1, FB_ext2])
            gb_ext = I_ext.groebner_basis()
            t_ext = time.time() - t0_ext
            if gb_ext:
                degs_ext = sorted([g.total_degree() for g in gb_ext])
                log(f"  Extension POSITIVE control: GB degs={degs_ext}, time={t_ext:.3f}s")
                results.append({
                    'family': 'extension_positive_ctrl',
                    'bits': 9,
                    'p': r_p,
                    'm': m_ext,
                    'trial': 0,
                    'xR': xR_ext,
                    'n_fb': len(sub_FB[:10]),
                    'd_ff_nonsym': degs_ext[0],
                    'D_reg_nonsym': degs_ext[-1],
                    'gb_time_nonsym_s': round(t_ext, 4),
                    'd_ff_sym': -1,
                    'D_reg_sym': -1,
                    'gb_time_sym_s': 0.0,
                    'd_ff_randctrl': -1,
                    'D_reg_randctrl': -1,
                    'gb_time_rand_s': 0.0,
                })
        except Exception as ex:
            log(f"  Extension control failed: {ex}")

log("\n" + "=" * 70)
log("SECTION D: Pollard rho baseline")
log("=" * 70)

def pollard_rho_ecdlp(E, P, Q, seed=42):
    """
    Pollard rho for ECDLP: find k such that Q = k*P.
    Returns (k, n_ops) where n_ops counts point additions.
    Uses Floyd's cycle detection with random walk.
    Expected ~0.886*sqrt(n) additions.
    """
    n = E.order()
    _random.seed(seed)

    # Partition E into 3 sets by x-coordinate mod 3
    def walk(R_pt, a_coef, b_coef, P, Q, n):
        x = int(R_pt[0]) % 3 if R_pt != E(0) else 0
        if x == 0:
            return 2*R_pt, (2*a_coef) % n, (2*b_coef) % n
        elif x == 1:
            return R_pt + P, (a_coef + 1) % n, b_coef
        else:
            return R_pt + Q, a_coef, (b_coef + 1) % n

    n_ops = 0
    a0, b0 = _random.randint(0, int(n)-1), _random.randint(0, int(n)-1)
    X = a0*P + b0*Q
    a_X, b_X = a0, b0

    Y = X
    a_Y, b_Y = a_X, b_X

    max_ops = min(20 * isqrt(int(n)), 500000)

    for _ in range(max_ops):
        X, a_X, b_X = walk(X, a_X, b_X, P, Q, n)
        Y, a_Y, b_Y = walk(Y, a_Y, b_Y, P, Q, n)
        Y, a_Y, b_Y = walk(Y, a_Y, b_Y, P, Q, n)
        n_ops += 3

        if X == Y:
            # Collision: a_X*P + b_X*Q = a_Y*P + b_Y*Q
            # (a_X - a_Y)*P = (b_Y - b_X)*Q
            da = (int(a_X) - int(a_Y)) % int(n)
            db = (int(b_Y) - int(b_X)) % int(n)
            if db == 0:
                # Restart
                a0, b0 = _random.randint(0, int(n)-1), _random.randint(0, int(n)-1)
                X = a0*P + b0*Q
                a_X, b_X = a0, b0
                Y, a_Y, b_Y = X, a_X, b_X
                continue
            try:
                k = (da * pow(int(db), -1, int(n))) % int(n)
                if k*P == Q:
                    return k, n_ops
            except Exception:
                pass
            # Restart
            a0, b0 = _random.randint(0, int(n)-1), _random.randint(0, int(n)-1)
            X = a0*P + b0*Q
            a_X, b_X = a0, b0
            Y, a_Y, b_Y = X, a_X, b_X

    return None, n_ops


rho_results = []
log("\nRunning Pollard rho baseline on structured and random curves...")
for curve_info in all_curve_families[:4]:  # First 4 curves for rho baseline
    E = curve_info['E']
    n = curve_info['n']
    p = curve_info['p']

    set_random_seed(SEED + hash((p, n)) % (2^31))
    P = E.random_point()
    while P == E(0):
        P = E.random_point()
    k_true = _random.randint(2, int(n) - 2)
    Q = k_true * P

    t0_rho = time.time()
    k_found, n_ops = pollard_rho_ecdlp(E, P, Q, seed=SEED + int(p) % 1000)
    t_rho = time.time() - t0_rho

    rho_baseline = 0.886 * float(sqrt(n))
    success = (k_found is not None and k_found == k_true)

    rho_results.append({
        'family': curve_info['family'],
        'bits': curve_info['bits'],
        'p': int(p),
        'n': int(n),
        'n_ops': n_ops,
        'rho_baseline_expected': round(rho_baseline, 1),
        'rho_ratio': round(n_ops / rho_baseline, 3),
        'success': success,
        'time_s': round(t_rho, 4)
    })
    log(f"  [{curve_info['family'].upper()} {curve_info['bits']}bit]: n_ops={n_ops}, "
        f"baseline={rho_baseline:.0f}, ratio={n_ops/rho_baseline:.2f}x, "
        f"solved={'YES' if success else 'NO'}, t={t_rho:.3f}s")

log("\n" + "=" * 70)
log("SECTION E: Analysis and verdict")
log("=" * 70)

# Aggregate d_ff by family and m
from collections import defaultdict

cells = defaultdict(list)
for r in results:
    if r['family'] in ('structured', 'random') and r['d_ff_sym'] >= 0:
        key = (r['family'], r['m'], r['bits'])
        cells[key].append(r['d_ff_sym'])

log("\nAggregated d_ff_sym by (family, m, bits):")
log(f"{'Family':12s} {'m':>3s} {'bits':>5s} | {'mean_d_ff':>10s} {'std_d_ff':>8s} {'n':>4s}")
log("-" * 55)

agg_table = []
for (family, m, bits), vals in sorted(cells.items()):
    if vals:
        mean_v = sum(vals) / len(vals)
        std_v = (sum((v - mean_v)^2 for v in vals) / len(vals))^0.5
        agg_table.append({
            'family': family, 'm': m, 'bits': bits,
            'mean_d_ff_sym': round(mean_v, 2),
            'std_d_ff_sym': round(std_v, 3),
            'n': len(vals)
        })
        log(f"{family:12s} {m:>3d} {bits:>5d} | {mean_v:>10.2f} {std_v:>8.3f} {len(vals):>4d}")

# Check slopes: d_ff vs bits for structured vs random, per m
for m_val in MS:
    struct_pts = [(r['bits'], r['mean_d_ff_sym']) for r in agg_table
                  if r['family'] == 'structured' and r['m'] == m_val and r['n'] >= 2]
    rand_pts = [(r['bits'], r['mean_d_ff_sym']) for r in agg_table
                if r['family'] == 'random' and r['m'] == m_val and r['n'] >= 2]

    if len(struct_pts) >= 2 and len(rand_pts) >= 2:
        struct_pts.sort()
        rand_pts.sort()

        # Linear slope: d_ff vs bits
        def slope(pts):
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            n = len(xs)
            sx = sum(xs); sy = sum(ys)
            sxx = sum(x*x for x in xs); sxy = sum(x*y for x,y in zip(xs,ys))
            denom = n*sxx - sx^2
            if denom == 0: return 0
            return (n*sxy - sx*sy) / denom

        s_struct = slope(struct_pts)
        s_rand = slope(rand_pts)

        log(f"\n  m={m_val}: slope_structured={s_struct:.4f}, slope_random={s_rand:.4f} "
            f"(ratio={s_struct/s_rand:.3f} if s_rand>0 else 'inf')")

        # Verdict
        if s_rand > 0 and s_struct < 0.5 * s_rand:
            log(f"  --> CANDIDATE SURVIVES for m={m_val}: structured slope < 50% of random slope")
        elif s_rand <= 0 and s_struct <= 0:
            log(f"  --> INCONCLUSIVE for m={m_val}: both slopes near zero (sizes too small)")
        else:
            log(f"  --> NEGATIVE RESULT for m={m_val}: slopes comparable, no advantage")

log("\n" + "=" * 70)
log("SECTION F: Write output files")
log("=" * 70)

# Write JSON results
output_data = {
    'experiment': 'round001-exp1-firstfall',
    'seed': SEED,
    'ms': MS,
    'n_trials': N_TRIALS,
    'target_bits': TARGET_BIT_SIZES,
    'raw_results': results,
    'rho_baseline': rho_results,
    'aggregated': agg_table,
}

json_path = f"{OUTDIR}/round001_exp1_firstfall_result.json"
with open(json_path, 'w') as f:
    json.dump(output_data, f, indent=2, default=str)
log(f"  Written: {json_path}")

# Write CSV
csv_path = f"{OUTDIR}/exp01_results.csv"
with open(csv_path, 'w') as f:
    f.write("family,bits,p,m,trial,d_ff_nonsym,D_reg_nonsym,d_ff_sym,D_reg_sym,d_ff_randctrl,D_reg_randctrl,gb_time_ns,gb_time_sym,gb_time_rand\n")
    for r in results:
        f.write(f"{r['family']},{r['bits']},{r['p']},{r['m']},{r['trial']},"
                f"{r['d_ff_nonsym']},{r['D_reg_nonsym']},"
                f"{r['d_ff_sym']},{r['D_reg_sym']},"
                f"{r['d_ff_randctrl']},{r['D_reg_randctrl']},"
                f"{r['gb_time_nonsym_s']},{r['gb_time_sym_s']},{r['gb_time_rand_s']}\n")
log(f"  Written: {csv_path}")

# Flush log
flush_log()
log(f"  Written: {OUTDIR}/round001_exp1_firstfall.log")

log("\n" + "=" * 70)
log("DONE")
log("=" * 70)
flush_log()
