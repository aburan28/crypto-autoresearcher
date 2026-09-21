"""
EXP-PMA-001 Module B: independent constructive existence decider.

Independent decision procedure, deliberately NOT sharing any decision logic
with Module A (parity_predicate.py):

  - Module A decides squareness of Delta_ijk in k(t) by factoring numerator
    and denominator into irreducibles and checking valuation parity plus a
    residual-constant Euler-criterion / rational-perfect-square test.
  - Module B decides squareness constructively: a top-down coefficient-
    matching polynomial square-root search (the classical "formal square
    root" recurrence, unrelated to factorization) for the numerator and
    denominator polynomials, plus a constant square root found by brute-force
    enumeration over F_q (finite fields) or integer-sqrt reconstruction over
    Q -- never Euler's criterion. When a square root exists, Module B gets an
    explicit witness rational function h with h^2 = Delta_ijk, which it uses
    to branch over the 8 orientation sign choices, assemble a full candidate
    4x4 matrix, and check all 16 principal minors directly against the
    prescribed table. This is the "branch over all orientation roots,
    assemble candidate matrices, and emit witness matrices" construction
    required by CTRL-PMA4-GROUND-TRUTH.
"""
from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

import sympy
from sympy import QQ, GF

from common import (
    RationalFunction,
    build_p_table,
    q_ij,
    c_ijk,
    delta_ijk,
    ANCHOR_TRIPLES,
    NONEMPTY_SUBSETS,
    t,
)

TWO_CONST = 2


# --------------------------------------------------------------------
# Domain-generic scalar arithmetic (independent of sympy's own Euler
# criterion / factorization machinery -- plain modular / Fraction math).
# --------------------------------------------------------------------
def dom_is_qq(domain) -> bool:
    return domain == QQ


def to_scalar(x, domain):
    if dom_is_qq(domain):
        return Fraction(sympy.Rational(x).p, sympy.Rational(x).q)
    return int(x) % domain.mod


def dom_add(a, b, domain):
    if dom_is_qq(domain):
        return a + b
    return (a + b) % domain.mod


def dom_sub(a, b, domain):
    if dom_is_qq(domain):
        return a - b
    return (a - b) % domain.mod


def dom_mul(a, b, domain):
    if dom_is_qq(domain):
        return a * b
    return (a * b) % domain.mod


def dom_inv(a, domain):
    if dom_is_qq(domain):
        return Fraction(1, 1) / a
    return pow(a, domain.mod - 2, domain.mod)


def dom_zero(domain):
    return Fraction(0) if dom_is_qq(domain) else 0


def dom_one(domain):
    return Fraction(1) if dom_is_qq(domain) else 1


def poly_coeffs_highest_first(poly, domain):
    raw = poly.all_coeffs()
    return [to_scalar(c, domain) for c in raw]


def coeffs_to_scalar_expr(coeffs_highest_first, domain):
    """Rebuild a sympy Poly from a highest-first coefficient list of domain
    scalars (Fraction for QQ, int for GF(q))."""
    if dom_is_qq(domain):
        conv = [sympy.Rational(c.numerator, c.denominator) for c in coeffs_highest_first]
    else:
        conv = [int(c) for c in coeffs_highest_first]
    return sympy.Poly(conv, t, domain=domain)


def formal_poly_sqrt(coeffs_highest_first: List, domain) -> Optional[List]:
    """Constructive top-down coefficient-matching square root of a MONIC
    polynomial given by highest-first coefficients (leading coeff must equal
    domain 1). Returns highest-first coefficients of a monic Q with Q^2 = D,
    or None if no such Q exists. This is the classical formal square-root
    recurrence -- entirely independent of polynomial factorization."""
    deg = len(coeffs_highest_first) - 1
    one = dom_one(domain)
    zero = dom_zero(domain)
    if deg == -1:
        return None  # zero polynomial handled by caller
    if coeffs_highest_first[0] != one:
        return None  # caller must pass a monic polynomial
    if deg % 2 != 0:
        return None
    m = deg // 2
    D = coeffs_highest_first
    Q = [None] * (m + 1)
    Q[0] = one
    two_inv = dom_inv(dom_add(one, one, domain), domain)
    for k in range(1, m + 1):
        s = zero
        for i in range(1, k):
            s = dom_add(s, dom_mul(Q[i], Q[k - i], domain), domain)
        rhs = dom_sub(D[k] if k < len(D) else zero, s, domain)
        Q[k] = dom_mul(rhs, two_inv, domain)
    # verify the remaining (over-determined) coefficients
    for k in range(m + 1, 2 * m + 1):
        s = zero
        lo = max(0, k - m)
        hi = min(m, k)
        for i in range(lo, hi + 1):
            s = dom_add(s, dom_mul(Q[i], Q[k - i], domain), domain)
        expected = D[k] if k < len(D) else zero
        if s != expected:
            return None
    return Q


def constant_sqrt_search(c_scalar, domain) -> Optional[object]:
    """Constructive constant square root: brute-force enumeration over
    F_q, or exact integer/Fraction sqrt reconstruction over Q. Deliberately
    NOT Euler's criterion (that is Module A's method)."""
    zero = dom_zero(domain)
    if c_scalar == zero:
        return zero
    if dom_is_qq(domain):
        frac = Fraction(c_scalar)
        if frac < 0:
            return None
        num, den = frac.numerator, frac.denominator
        rn = int(round(num ** 0.5))
        # exact integer sqrt via math.isqrt-equivalent loop (no library reuse
        # of Module A's sympy.integer_nthroot call)
        rn = _exact_isqrt(num)
        rd = _exact_isqrt(den)
        if rn is None or rd is None:
            return None
        return Fraction(rn, rd)
    else:
        q = domain.mod
        for x in range(q):
            if (x * x) % q == c_scalar % q:
                return x
        return None


def _exact_isqrt(n: int) -> Optional[int]:
    if n < 0:
        return None
    if n == 0:
        return 0
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * mid <= n:
            lo = mid
        else:
            hi = mid - 1
    return lo if lo * lo == n else None


def constructive_sqrt(rf: RationalFunction, domain) -> Tuple[Optional[RationalFunction], str]:
    """Attempt to constructively find h with h^2 = rf (rf canonically
    reduced, denominator monic). Returns (h_as_RationalFunction_or_None,
    diagnostic_reason)."""
    rf = rf.reduced()
    if rf.is_zero():
        return RationalFunction.constant(0, domain), "Delta is identically zero (degenerate; caller must branch this separately, not treat as a square-root success)"

    num, den = rf.num, rf.den
    den_coeffs = poly_coeffs_highest_first(den, domain)  # den is monic already
    Qden = formal_poly_sqrt(den_coeffs, domain)
    if Qden is None:
        return None, "denominator has no monic polynomial square root (formal coefficient-matching recurrence failed or odd degree)"

    lc_num = to_scalar(num.LC(), domain)
    num_coeffs = poly_coeffs_highest_first(num, domain)
    if lc_num == dom_zero(domain):
        return None, "numerator leading coefficient is zero (should not happen for a reduced nonzero numerator)"
    lc_inv = dom_inv(lc_num, domain)
    num0_coeffs = [dom_mul(c, lc_inv, domain) for c in num_coeffs]  # monic-normalized numerator
    Pnum = formal_poly_sqrt(num0_coeffs, domain)
    if Pnum is None:
        return None, "numerator (monic-normalized) has no monic polynomial square root"

    r = constant_sqrt_search(lc_num, domain)
    if r is None:
        return None, f"leading constant {lc_num} has no square root in the constant field (brute-force/isqrt search)"

    Q_poly = coeffs_to_scalar_expr(Qden, domain)
    P_poly = coeffs_to_scalar_expr(Pnum, domain)
    r_poly = sympy.Poly(sympy.Rational(r.numerator, r.denominator) if dom_is_qq(domain) else int(r), t, domain=domain)
    H_num = P_poly * r_poly
    h = RationalFunction(H_num, Q_poly, domain).reduced()
    return h, "constructive square root found"


@dataclass
class BranchResult:
    signs: Tuple[int, int, int]
    matches: bool
    mismatches: List[str] = dc_field(default_factory=list)
    matrix: Optional[Dict[Tuple[int, int], object]] = None


def four_by_four_det(entries: Dict[Tuple[int, int], RationalFunction], idxs: Tuple[int, ...], domain) -> RationalFunction:
    """Direct determinant of the principal submatrix on idxs, via manual
    Laplace expansion (size 0..4). idxs is a sorted tuple of distinct
    indices from {1,2,3,4}. entries[(i,i)] holds diagonal, entries[(i,j)]
    i!=j holds off-diagonal."""
    n = len(idxs)
    if n == 0:
        return RationalFunction.constant(1, domain)
    if n == 1:
        i = idxs[0]
        return entries[(i, i)]
    if n == 2:
        i, j = idxs
        return (entries[(i, i)] * entries[(j, j)]) - (entries[(i, j)] * entries[(j, i)])
    if n == 3:
        i, j, k = idxs
        aii, ajj, akk = entries[(i, i)], entries[(j, j)], entries[(k, k)]
        aij, aji = entries[(i, j)], entries[(j, i)]
        aik, aki = entries[(i, k)], entries[(k, i)]
        ajk, akj = entries[(j, k)], entries[(k, j)]
        term1 = aii * ajj * akk
        term2 = aii * ajk * akj
        term3 = ajj * aik * aki
        term4 = akk * aij * aji
        term5 = aij * ajk * aki
        term6 = aik * akj * aji
        return term1 - term2 - term3 - term4 + term5 + term6
    if n == 4:
        # cofactor expansion along the first row/column i1
        i1, i2, i3, i4 = idxs
        total = None
        for col_drop_pos, col_drop in enumerate(idxs):
            rest = tuple(x for x in idxs if x != col_drop)
            # entry (i1, col_drop)
            entry = entries[(i1, col_drop)]
            minor_idxs_rows = tuple(x for x in idxs if x != i1)
            # build the 3x3 minor deleting row i1 and column col_drop
            sub = {}
            for r_ in minor_idxs_rows:
                for c_ in idxs:
                    if c_ == col_drop:
                        continue
                    sub[(r_, c_)] = entries[(r_, c_)]
            m3 = three_by_three_det_generic(sub, minor_idxs_rows, tuple(x for x in idxs if x != col_drop), domain)
            sign = 1 if col_drop_pos % 2 == 0 else -1
            term = entry * m3
            if sign == -1:
                term = RationalFunction.constant(0, domain) - term
            total = term if total is None else (total + term)
        return total
    raise ValueError("unsupported size")


def three_by_three_det_generic(sub, rows, cols, domain) -> RationalFunction:
    """3x3 determinant of a (possibly non-principal) submatrix given by
    explicit row/col index tuples (both length 3), using entries dict sub
    keyed by (row, col)."""
    r1, r2, r3 = rows
    c1, c2, c3 = cols
    a11, a12, a13 = sub[(r1, c1)], sub[(r1, c2)], sub[(r1, c3)]
    a21, a22, a23 = sub[(r2, c1)], sub[(r2, c2)], sub[(r2, c3)]
    a31, a32, a33 = sub[(r3, c1)], sub[(r3, c2)], sub[(r3, c3)]
    return (
        a11 * (a22 * a33 - a23 * a32)
        - a12 * (a21 * a33 - a23 * a31)
        + a13 * (a21 * a32 - a22 * a31)
    )


def evaluate_instance(d_values, domain, field_label):
    """Module B: independent constructive existence decision for one
    instance. Returns a dict verdict, mirroring parity_predicate's output
    shape but computed via a wholly separate procedure."""
    p_table = build_p_table(d_values, domain)

    q_vals = {}
    for (i, j) in [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]:
        q_vals[(i, j)] = q_ij(p_table, i, j, domain)

    degenerate_reasons = []
    for (i, j, k) in ANCHOR_TRIPLES:
        for pair in [(i, j), (j, k), (k, i)]:
            key = tuple(sorted(pair))
            if q_vals[key].is_zero():
                degenerate_reasons.append(f"q_{pair}=0 in triple {(i,j,k)}")
    if degenerate_reasons:
        return {"verdict": "DEGENERATE", "degenerate_reasons": degenerate_reasons}

    sqrt_results = {}
    for (i, j, k) in ANCHOR_TRIPLES:
        D = delta_ijk(p_table, i, j, k, domain)
        h, reason = constructive_sqrt(D, domain)
        sqrt_results[(i, j, k)] = (h, reason)

    failed_triples = [tri for tri, (h, reason) in sqrt_results.items() if h is None]
    if failed_triples:
        return {
            "verdict": "NOT_EXISTS",
            "reason": "no constructive square root exists for the orientation discriminant in one or more anchor triples",
            "branch_log": {str(tri): sqrt_results[tri][1] for tri in ANCHOR_TRIPLES},
        }

    c_vals = {tri: c_ijk(p_table, tri[0], tri[1], tri[2], domain) for tri in ANCHOR_TRIPLES}
    two_rf = RationalFunction.constant(2, domain)

    branch_results: List[BranchResult] = []
    witness = None

    for s1 in (1, -1):
        for s2 in (1, -1):
            for s3 in (1, -1):
                signs = {ANCHOR_TRIPLES[0]: s1, ANCHOR_TRIPLES[1]: s2, ANCHOR_TRIPLES[2]: s3}
                entries: Dict[Tuple[int, int], RationalFunction] = {}
                for idx in (1, 2, 3, 4):
                    entries[(idx, idx)] = p_table[(idx,)]
                one_rf = RationalFunction.constant(1, domain)
                entries[(1, 2)] = one_rf
                entries[(1, 3)] = one_rf
                entries[(1, 4)] = one_rf
                entries[(2, 1)] = q_vals[(1, 2)]
                entries[(3, 1)] = q_vals[(1, 3)]
                entries[(4, 1)] = q_vals[(1, 4)]

                for tri in ANCHOR_TRIPLES:
                    i, j, k = tri
                    h, _ = sqrt_results[tri]
                    sh = h if signs[tri] == 1 else (RationalFunction.constant(0, domain) - h)
                    c = c_vals[tri]
                    x = (c + sh) / two_rf
                    y = (c - sh) / two_rf
                    # x = a_ij*a_jk*a_ki ; with a_ij=1 => a_jk*a_ki = x ; a_ki known (=q_{ik} via anchor edge)
                    # anchor triples all contain index 1: (1,2,3) -> j,k = 2,3 ; edges from 1
                    if tri == (1, 2, 3):
                        entries[(2, 3)] = x / q_vals[(1, 3)]  # a_23 = x / a_31 ; a_31 = q_13
                        entries[(3, 2)] = y / q_vals[(1, 2)]  # a_32 = y / a_21 ; a_21 = q_12
                    elif tri == (1, 2, 4):
                        entries[(2, 4)] = x / q_vals[(1, 4)]
                        entries[(4, 2)] = y / q_vals[(1, 2)]
                    elif tri == (1, 3, 4):
                        entries[(3, 4)] = x / q_vals[(1, 4)]
                        entries[(4, 3)] = y / q_vals[(1, 3)]

                mismatches = []
                for S in NONEMPTY_SUBSETS:
                    computed = four_by_four_det(entries, S, domain)
                    expected = p_table[S]
                    if computed != expected:
                        mismatches.append(f"{S}: computed={computed} expected={expected}")

                br = BranchResult(signs=(s1, s2, s3), matches=(len(mismatches) == 0), mismatches=mismatches, matrix=dict(entries) if not mismatches else None)
                branch_results.append(br)
                if br.matches and witness is None:
                    witness = entries

    any_match = any(br.matches for br in branch_results)
    if any_match:
        return {
            "verdict": "EXISTS",
            "witness_matrix": {f"{k[0]},{k[1]}": str(v) for k, v in witness.items()},
            "branch_log": [
                {"signs": br.signs, "matches": br.matches, "mismatches": br.mismatches[:3]}
                for br in branch_results
            ],
        }
    else:
        return {
            "verdict": "NOT_EXISTS",
            "reason": "square roots exist for all three anchor discriminants, but no sign combination reproduces all 16 prescribed principal minors",
            "branch_log": [
                {"signs": br.signs, "matches": br.matches, "mismatches": br.mismatches}
                for br in branch_results
            ],
        }
