"""p-adic instrument for EXP-ECDLP-a26bde.

Implements, in pure Python with `fractions.Fraction` for exact rational
arithmetic, the division-free p-adic machinery needed for the hard-lift
digit identity: projective scalar multiplication mod p^K, the (t, w)
formal-group chart, the formal logarithm and its compositional inverse,
the unique homomorphic torsion section, and the formal-group digit.

This module is a scoped copy built for EXP-ECDLP-a26bde per
IDEA-20260905-dacf4f's tooling design (shared *design*, not a shared file,
since EXP-ECDLP-1e6502 has not run and has no artifact to reuse). See
experiments/EXP-ECDLP-a26bde/derivation_note.md for the derivation this
code implements.

Every formula here is checked in two independent ways before it is trusted:
  (1) the projective addition/doubling formulas are derived symbolically
      (see derive_formulas.py) and validated against harness/toycurve.py's
      exact-field EllipticCurve.add/.mul over real F_p, for many primes and
      hundreds of random point pairs (see validate_projective.py);
  (2) the formal-group machinery (w-series, log-series, exp-series) is
      checked symbolically (log(0)=0, F(0)=1, log(exp(u))=u to working
      degree) and then numerically via the five self-checks
      (selfchecks.py).

Do not modify harness/toycurve.py; this module only imports it for
independent verification, never for its own arithmetic.
"""
from __future__ import annotations

from fractions import Fraction
from dataclasses import dataclass

WORKING_DEGREE = 80  # D in the task's derivation. Raised from an initial 15
# (see derivation_note.md, BUG-EXP-a26bde-002): each near-identity chart
# operation (to_tw/from_tw applied to a point close to O) divides out a
# redundant common p-power factor whose size compounds through the pipeline
# (n-division, the P - X_S subtraction), consuming working precision faster
# than a single fixed PRECISION_MARGIN can be sized for by inspection alone.
# D=80 pushes the log/exp series truncation error out to p-adic valuation
# ~81, comfortably clear of the empirically measured consumption (see
# instrument.py's PRECISION_MARGIN and the convergence check in
# instrument.torsion_component), and costs under 2 seconds to build once per
# curve (toy scale; well within budget).

# ---------------------------------------------------------------------------
# Projective, division-free elliptic-curve arithmetic mod N = p^K.
#
# Curve: y^2 = x^3 + a x + b.  Point (X:Y:Z) with x=X/Z, y=Y/Z.  Formulas
# derived symbolically in derive_formulas.py from the known-correct affine
# doubling/addition formulas in harness/toycurve.py by substituting x=X/Z,
# y=Y/Z and clearing denominators; validated numerically in
# validate_projective.py against harness/toycurve.py.EllipticCurve over real
# F_p before being trusted here.
# ---------------------------------------------------------------------------

O_PROJ = (0, 1, 0)  # point at infinity


def is_identity(P: tuple[int, int, int]) -> bool:
    X, Y, Z = P
    return Z == 0


def pneg(P: tuple[int, int, int], N: int) -> tuple[int, int, int]:
    X, Y, Z = P
    return (X % N, (-Y) % N, Z % N)


def pdbl(P: tuple[int, int, int], a: int, N: int) -> tuple[int, int, int]:
    """Division-free doubling mod N. Returns O if P is 2-torsion (Y==0 mod p
    would make this degenerate; here we detect Y%N==0 as the practical
    signal, which is what happens when the running point actually IS
    2-torsion in this finite ring)."""
    X1, Y1, Z1 = P
    if Z1 % N == 0:
        return O_PROJ
    if Y1 % N == 0:
        return O_PROJ
    X3 = (2 * Y1 * Z1 * (9 * X1**4 + 6 * a * X1**2 * Z1**2
                          - 8 * X1 * Y1**2 * Z1 + a**2 * Z1**4)) % N
    Y3 = (-27 * X1**6 - 27 * X1**4 * Z1**2 * a + 36 * X1**3 * Y1**2 * Z1
          - 9 * X1**2 * Z1**4 * a**2 + 12 * X1 * Y1**2 * Z1**3 * a
          - 8 * Y1**4 * Z1**2 - Z1**6 * a**3) % N
    Z3 = (8 * Y1**3 * Z1**3) % N
    return (X3, Y3, Z3)


def padd(P1: tuple[int, int, int], P2: tuple[int, int, int], a: int, N: int
          ) -> tuple[int, int, int]:
    """Division-free addition mod N, dispatching to doubling / negation-sum
    special cases when the generic-addition denominator degenerates."""
    if is_identity(P1):
        return P2
    if is_identity(P2):
        return P1
    X1, Y1, Z1 = P1
    X2, Y2, Z2 = P2
    H = (X1 * Z2 - X2 * Z1) % N
    if H % N == 0:
        # same x-coordinate mod N: either the same point (double) or
        # negatives (sum is O). Distinguish by y.
        if (Y1 * Z2 - Y2 * Z1) % N == 0:
            return pdbl(P1, a, N)
        return O_PROJ
    # generic addition, division-free. Derived symbolically (substitute
    # x=X/Z, y=Y/Z into the affine chord formula and clear denominators);
    # validated numerically against harness/toycurve.py in
    # validate_projective.py before being trusted (see check_add3.py-style
    # derivation in the module docstring). NOTE: the sign here is fixed --
    # an earlier derivation pass dropped a minus sign from sympy's
    # `fraction()` normalization and was caught exactly by that numeric
    # validation (recorded as a protocol deviation in the derivation note).
    X3 = (-H * (X1**3 * Z2**3 - X1**2 * X2 * Z1 * Z2**2
                - X1 * X2**2 * Z1**2 * Z2 + X2**3 * Z1**3
                - Y1**2 * Z1 * Z2**3 + 2 * Y1 * Y2 * Z1**2 * Z2**2
                - Y2**2 * Z1**3 * Z2)) % N
    Y3 = (X1**3 * Y1 * Z2**4 - 2 * X1**3 * Y2 * Z1 * Z2**3
          + 3 * X1**2 * X2 * Y2 * Z1**2 * Z2**2 - 3 * X1 * X2**2 * Y1 * Z1**2 * Z2**2
          + 2 * X2**3 * Y1 * Z1**3 * Z2 - X2**3 * Y2 * Z1**4
          - Y1**3 * Z1 * Z2**4 + 3 * Y1**2 * Y2 * Z1**2 * Z2**3
          - 3 * Y1 * Y2**2 * Z1**3 * Z2**2 + Y2**3 * Z1**4 * Z2) % N
    Z3 = (Z1 * Z2 * H**3) % N
    return (X3 % N, Y3 % N, Z3 % N)


def pmul(k: int, P: tuple[int, int, int], a: int, N: int) -> tuple[int, int, int]:
    """Division-free scalar multiplication mod N by double-and-add."""
    if k < 0:
        return pmul(-k, pneg(P, N), a, N)
    result = O_PROJ
    addend = (P[0] % N, P[1] % N, P[2] % N)
    while k > 0:
        if k & 1:
            result = padd(result, addend, a, N)
        addend = pdbl(addend, a, N)
        k >>= 1
    return result


def _int_valuation(x: int, p: int, N: int) -> int:
    """p-adic valuation of x mod N, capped at v_p(N)."""
    x %= N
    cap = 0
    n = N
    while n % p == 0:
        n //= p
        cap += 1
    if x == 0:
        return cap
    v = 0
    while x % p == 0:
        x //= p
        v += 1
    return v


def normalize_proj(P: tuple[int, int, int], N: int, p: int
                    ) -> tuple[tuple[int, int, int], int]:
    """Division-free projective formulas can produce a triple (X:Y:Z) that
    carries a REDUNDANT common factor of p (e.g. subtracting a near-infinity
    point Y from an ordinary point P, where the addition formula's shared
    denominator-clearing factor H has positive valuation even though the
    resulting point is generic). This is a valid projective rescaling, not
    a precision loss at the level of the true p-adic point, but it DOES cost
    working precision here: dividing (X,Y,Z) by their common p^v factor is
    only meaningful mod N/p^v. Returns (normalized triple mod N, v) so the
    caller can confirm v is small enough that N/p^v still meets the required
    working precision (asserted, not assumed, at each call site)."""
    X, Y, Z = (P[0] % N, P[1] % N, P[2] % N)
    if X == 0 and Y == 0 and Z == 0:
        return (X, Y, Z), 0
    v = min(_int_valuation(X, p, N), _int_valuation(Y, p, N), _int_valuation(Z, p, N))
    if v == 0:
        return (X, Y, Z), 0
    pv = p ** v
    if X % pv or Y % pv or Z % pv:
        raise ValueError("normalize_proj: coordinates not all divisible by "
                          "the claimed common valuation -- arithmetic bug")
    return (X // pv, Y // pv, Z // pv), v


def to_tw(P: tuple[int, int, int], N: int, p: int) -> tuple[int, int, int]:
    """(t, w) chart: t=-X/Y, w=-Z/Y. Requires Y a unit mod p after
    normalizing away any redundant common p-power factor (checked). Returns
    (t, w, Nn) where Nn = N / p^v is the WORKING MODULUS actually achieved
    (v digits of precision are consumed by the normalization, and the
    caller must track Nn rather than assume it stayed N)."""
    (X, Y, Z), v = normalize_proj(P, N, p)
    Nn = N // (p ** v)
    if Y % p == 0:
        raise ValueError(f"to_tw: Y not a unit mod p after normalizing "
                          f"(v={v}) (Y={Y % Nn}, p={p}) — genericity "
                          "condition fails, cannot use (t,w) chart")
    Yinv = pow(Y % Nn, -1, Nn)
    t = (-X * Yinv) % Nn
    w = (-Z * Yinv) % Nn
    return (t, w, Nn)


def from_tw(t: int, w: int) -> tuple[int, int, int]:
    """Projective representative (X:Y:Z) = (t : -1 : w) for chart point (t,w)."""
    return (t, -1, w)


def to_affine(P: tuple[int, int, int], N: int, p: int) -> tuple[int, int, int]:
    """Ordinary affine (x,y) = (X/Z, Y/Z), after normalizing away any
    redundant common p-power factor. Requires Z a unit mod p (checked).
    Returns (x, y, Nn), Nn the achieved working modulus (see to_tw)."""
    (X, Y, Z), v = normalize_proj(P, N, p)
    Nn = N // (p ** v)
    if Z % p == 0:
        raise ValueError(f"to_affine: Z not a unit mod p after normalizing "
                          f"(v={v}) (Z={Z % Nn}, p={p})")
    Zinv = pow(Z % Nn, -1, Nn)
    return ((X * Zinv) % Nn, (Y * Zinv) % Nn, Nn)


# ---------------------------------------------------------------------------
# Formal power series with exact Fraction coefficients, index = degree.
# ---------------------------------------------------------------------------

Series = list  # list[Fraction], length D+1, index i = coefficient of t^i


def series_trim(A: Series, D: int) -> Series:
    A = list(A[:D + 1])
    while len(A) < D + 1:
        A.append(Fraction(0))
    return A


def series_add(A: Series, B: Series, D: int) -> Series:
    A, B = series_trim(A, D), series_trim(B, D)
    return [A[i] + B[i] for i in range(D + 1)]


def series_scale(A: Series, c, D: int) -> Series:
    A = series_trim(A, D)
    return [c * A[i] for i in range(D + 1)]


def series_mul(A: Series, B: Series, D: int) -> Series:
    A, B = series_trim(A, D), series_trim(B, D)
    out = [Fraction(0)] * (D + 1)
    for i in range(D + 1):
        if A[i] == 0:
            continue
        for j in range(D + 1 - i):
            if B[j] == 0:
                continue
            out[i + j] += A[i] * B[j]
    return out


def series_pow(A: Series, n: int, D: int) -> Series:
    result = [Fraction(1)] + [Fraction(0)] * D
    base = series_trim(A, D)
    for _ in range(n):
        result = series_mul(result, base, D)
    return result


def series_deriv(A: Series, D: int) -> Series:
    A = series_trim(A, D + 1)
    return [(i + 1) * A[i + 1] for i in range(D + 1)]


def series_integrate(A: Series, D: int) -> Series:
    """Integrate term by term with zero constant: int(sum a_i t^i) = sum a_i/(i+1) t^(i+1)."""
    A = series_trim(A, D - 1 if D > 0 else 0)
    out = [Fraction(0)] * (D + 1)
    for i in range(min(len(A), D)):
        out[i + 1] = A[i] / (i + 1)
    return out


def series_reciprocal(A: Series, D: int) -> Series:
    """1/A as a power series, requires A[0] != 0."""
    A = series_trim(A, D)
    if A[0] == 0:
        raise ValueError("series_reciprocal: constant term is zero")
    inv = [Fraction(0)] * (D + 1)
    inv[0] = 1 / A[0]
    for k in range(1, D + 1):
        s = Fraction(0)
        for i in range(1, k + 1):
            s += A[i] * inv[k - i]
        inv[k] = -inv[0] * s
    return inv


def series_valuation(A: Series) -> int:
    for i, c in enumerate(A):
        if c != 0:
            return i
    return len(A)  # identically zero to this truncation


def series_divide_same_valuation(N: Series, Dn: Series, D: int) -> Series:
    """Divide two power series that share the same (possibly nonzero)
    valuation, e.g. N=(t w' - w), Dn=2w, both with valuation = v_t(w). Shifts
    both down by their common valuation, then does ordinary reciprocal-based
    division on the resulting unit-constant series."""
    vn = series_valuation(N)
    vd = series_valuation(Dn)
    v = min(vn, vd)
    # After shifting by v, at least one of them has a nonzero constant term;
    # the task guarantees F(0)=1, i.e. both N and Dn have EXACTLY the same
    # valuation v_t(w) (checked by the caller).
    if vn != vd:
        raise ValueError(f"series_divide_same_valuation: valuations differ "
                          f"({vn} vs {vd}); numerator and denominator do not "
                          "share the expected common zero")
    Nshift = N[v:] + [Fraction(0)] * v
    Dshift = Dn[v:] + [Fraction(0)] * v
    Nshift, Dshift = series_trim(Nshift, D), series_trim(Dshift, D)
    Dinv = series_reciprocal(Dshift, D)
    return series_mul(Nshift, Dinv, D)


def series_compose(A: Series, B: Series, D: int) -> Series:
    """A(B(t)) truncated to degree D. Requires B[0] == 0 (no constant term)."""
    A, B = series_trim(A, D), series_trim(B, D)
    if B[0] != 0:
        raise ValueError("series_compose: B must have zero constant term")
    result = [Fraction(0)] * (D + 1)
    result[0] = A[0]
    Bpow = [Fraction(1)] + [Fraction(0)] * D  # B^0
    for k in range(1, D + 1):
        Bpow = series_mul(Bpow, B, D)
        if A[k] == 0:
            continue
        for i in range(D + 1):
            if Bpow[i] == 0:
                continue
            result[i] += A[k] * Bpow[i]
    return result


def series_reversion(F: Series, D: int) -> Series:
    """Compositional inverse G of F, where F(t) = t + O(t^2) (F[0]=0, F[1]=1),
    such that F(G(u)) = u mod u^(D+1). Standard coefficient-matching
    algorithm: solving order by order, exploiting that the coefficient of
    u^k in F(G(u)) is g_k (from F's own linear term) plus a polynomial in
    g_2..g_(k-1) that is already fixed once g_k is set to 0.
    """
    F = series_trim(F, D)
    if F[0] != 0 or F[1] != 1:
        raise ValueError("series_reversion: F must satisfy F(t)=t+O(t^2)")
    G = [Fraction(0)] * (D + 1)
    G[1] = Fraction(1)
    for k in range(2, D + 1):
        comp = series_compose(F, G, k)  # G_k currently 0; degrees > k are irrelevant
        d_k = comp[k]
        G[k] = -d_k
    return G
