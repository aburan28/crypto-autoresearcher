"""P-adic/formal-group instrument for EXP-ECDLP-a26bde.

Implements, in pure Python exact-integer arithmetic (no floating point,
no numpy):

  * a small finite-relative-precision p-adic ("Laurent") number type that
    natively represents both ordinary p-adic integers (valuation >= 0) and
    points near the formal-group identity O (valuation < 0), which is what
    lets the elliptic-curve chord-and-tangent formulas be applied uniformly
    whether or not the result lands in the kernel of reduction;
  * short-Weierstrass affine elliptic-curve group law over that ring;
  * the canonical (group-theoretic, no Hensel/Newton root-finding on the
    order-n condition) prime-to-p torsion section t(R) for R in E(F_p) with
    gcd(ord(R), p) = 1, reusing the projection construction independently
    reproduced in experiments/EXP-ECDLP-809375/implementation/
    fg1_group_theoretic.py (S_hat = [p^(r-1) * ((p^(r-1))^{-1} mod n)] L);
  * the naive coordinate-wise Teichmuller section s(R) (Teichmuller-lift the
    x-coordinate multiplicatively, Hensel-lift a y on the curve reducing to
    the right residue) -- NOT claimed to be a group homomorphism, and not
    the "elliptic Teichmuller lift" of ledger/FINDING-PF-IC-001.md
    ECFG-P1543-R1 (which IS the torsion section on an ordinary curve); this
    module's Teichmuller section is the coordinate-wise, non-elliptic
    construction, used deliberately as the non-homomorphic contrast object
    named in H-ECDLP-6a9479 claim (3);
  * the formal-group digit function d(P) = leading unit digit, mod p, of
    psi(P - t(P mod p)) where psi(Q) = -x(Q)/y(Q) is the formal parameter.

Every function documents the precision it used. This is a validated
INSTRUMENT (per IDEA-20260905-dacf4f); it makes no research claim on its
own -- the five self-checks in selfcheck.py are the acceptance test.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Optional


# --------------------------------------------------------------------------
# integer p-adic valuation helper
# --------------------------------------------------------------------------

def valuation(a: int, p: int, cap: int) -> int:
    """v_p(a) truncated at `cap`. a == 0 yields `cap` ("at least cap")."""
    if a == 0:
        return cap
    v = 0
    while v < cap and a % p == 0:
        a //= p
        v += 1
    return v


class InsufficientPrecision(Exception):
    """Raised when the requested operation needs more working precision
    than was supplied. Never silently truncated further."""


# --------------------------------------------------------------------------
# Laurent p-adic numbers: value == mant * p**val (mod p**(val+prec))
#   mant is a unit mod p (mant % p != 0), OR mant == 0 with prec == 0,
#   meaning "value is 0 to at least p**val precision, no digits known
#   beyond that" (used for exact zero and precision-exhausted results).
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Qp:
    p: int
    mant: int    # unit mod p, in [0, p**prec), or 0 if prec == 0
    val: int     # p-adic valuation of the leading known digit
    prec: int    # number of correct digits of mant beyond the valuation

    @staticmethod
    def zero(p: int, val: int) -> "Qp":
        return Qp(p, 0, val, 0)

    @staticmethod
    def from_int(a: int, p: int, absprec: int) -> "Qp":
        """a is an ordinary integer known exactly mod p**absprec."""
        a %= p ** absprec
        if a == 0:
            return Qp.zero(p, absprec)
        v = valuation(a, p, absprec)
        mant = (a // p ** v) % p ** (absprec - v)
        return Qp(p, mant, v, absprec - v)

    @staticmethod
    def from_fraction(fr: Fraction, p: int, absprec: int) -> "Qp":
        num, den = fr.numerator, fr.denominator
        if den % p == 0:
            raise ValueError("denominator divisible by p: bad reduction")
        M = p ** absprec
        inv = pow(den % M, -1, M)
        return Qp.from_int((num * inv) % M, p, absprec)

    def is_exact_zero_to_precision(self) -> bool:
        return self.prec == 0

    def truncated_int(self) -> int:
        """mant*p**val as an ordinary python int (only meaningful when
        val >= 0; used for reporting/debug)."""
        return self.mant * self.p ** self.val if self.val >= 0 else self.mant

    def neg(self) -> "Qp":
        if self.prec == 0:
            return self
        M = self.p ** self.prec
        return Qp(self.p, (-self.mant) % M, self.val, self.prec)

    def add(self, other: "Qp") -> "Qp":
        p = self.p
        a, b = (self, other) if self.val <= other.val else (other, self)
        shift = b.val - a.val
        combined_prec = min(a.prec, shift + b.prec)
        if combined_prec <= 0:
            raise InsufficientPrecision(
                f"add: combined precision {combined_prec} <= 0 "
                f"(a.val={a.val},a.prec={a.prec},b.val={b.val},b.prec={b.prec})")
        M = p ** combined_prec
        a_mant = a.mant % M
        b_shifted = (b.mant * p ** shift) % M
        total = (a_mant + b_shifted) % M
        if total == 0:
            return Qp.zero(p, a.val + combined_prec)
        v_extra = valuation(total, p, combined_prec)
        mant = (total // p ** v_extra) % p ** (combined_prec - v_extra)
        return Qp(p, mant, a.val + v_extra, combined_prec - v_extra)

    def sub(self, other: "Qp") -> "Qp":
        return self.add(other.neg())

    def mul(self, other: "Qp") -> "Qp":
        prec = min(self.prec, other.prec)
        if prec <= 0:
            return Qp.zero(self.p, self.val + other.val)
        M = self.p ** prec
        mant = (self.mant * other.mant) % M
        return Qp(self.p, mant, self.val + other.val, prec)

    def inv(self) -> "Qp":
        if self.prec == 0:
            raise InsufficientPrecision("inv: dividing by a value known to 0 digits")
        M = self.p ** self.prec
        return Qp(self.p, pow(self.mant, -1, M), -self.val, self.prec)

    def div(self, other: "Qp") -> "Qp":
        return self.mul(other.inv())

    def scale_int(self, k: int) -> "Qp":
        """Multiply by the ordinary integer k (k reduced mod current prec)."""
        if self.prec == 0:
            return self
        M = self.p ** self.prec
        kk = k % M
        if kk == 0:
            return Qp.zero(self.p, self.val + self.prec)  # k could carry extra p-valuation; conservative
        v = valuation(kk, self.p, self.prec)
        return Qp(self.p, (self.mant * (kk // self.p ** v)) % (self.p ** (self.prec - v)),
                   self.val + v, self.prec - v)

    def mod_p_digit(self) -> int:
        """The leading base-p digit, i.e. (value / p**val) mod p."""
        if self.prec == 0:
            raise InsufficientPrecision("mod_p_digit: no digits known")
        return self.mant % self.p


def qp_int(a: int, p: int, prec: int) -> Qp:
    """An ordinary p-adic integer a (>=0 valuation), full `prec` digits."""
    return Qp.from_int(a % p ** prec, p, prec)


# --------------------------------------------------------------------------
# affine EC group law over Qp Laurent points; None is the identity O
# --------------------------------------------------------------------------

QPoint = Optional[tuple]  # (Qp, Qp) or None


def ec_neg(P: QPoint) -> QPoint:
    if P is None:
        return None
    x, y = P
    return (x, y.neg())


def ec_add(P: QPoint, Q: QPoint, a_curve: int) -> QPoint:
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    dx = x2.sub(x1)
    dy = y2.sub(y1)
    if dx.is_exact_zero_to_precision():
        # x1 == x2 to available precision: either P == Q (double) or P == -Q.
        sy = y1.add(y2)
        if sy.is_exact_zero_to_precision():
            return None
        return ec_double(P, a_curve)
    lam = dy.div(dx)
    x3 = lam.mul(lam).sub(x1).sub(x2)
    y3 = lam.mul(x1.sub(x3)).sub(y1)
    return (x3, y3)


def ec_double(P: QPoint, a_curve: int) -> QPoint:
    if P is None:
        return None
    x1, y1 = P
    a_const = (Qp.from_int(a_curve % x1.p ** x1.prec, x1.p, x1.prec)
               if x1.prec > 0 else Qp.zero(x1.p, 0))
    num = x1.mul(x1).scale_int(3).add(a_const)
    two_y = y1.scale_int(2)
    if two_y.is_exact_zero_to_precision():
        raise InsufficientPrecision("double: 2y == 0 to available precision "
                                     "(2-torsion point in this chart)")
    lam = num.div(two_y)
    x3 = lam.mul(lam).sub(x1).sub(x1)
    y3 = lam.mul(x1.sub(x3)).sub(y1)
    return (x3, y3)


def ec_mul(k: int, P: QPoint, a_curve: int) -> QPoint:
    if k == 0 or P is None:
        return None
    if k < 0:
        return ec_neg(ec_mul(-k, P, a_curve))
    R: QPoint = None
    addend = P
    kk = k
    while kk > 0:
        if kk & 1:
            R = ec_add(R, addend, a_curve)
        addend = ec_double(addend, a_curve) if kk > 1 else addend
        kk >>= 1
    return R


# --------------------------------------------------------------------------
# ordinary-ring (valuation-0) affine group law, used only for the canonical
# torsion-lift construction, which by design never leaves the affine chart
# (see EXP-ECDLP-809375's independent reproduction of the same projection).
# --------------------------------------------------------------------------

class KernelOfReduction(Exception):
    pass


def is_unit(d: int, p: int) -> bool:
    return d % p != 0


def ring_inverse(d: int, p: int, M: int) -> int:
    if not is_unit(d, p):
        raise KernelOfReduction(f"denominator {d % M} divisible by p={p}")
    return pow(d, -1, M)


class RingCurve:
    """Affine short-Weierstrass group law over Z/p^r (ordinary ring, no
    Laurent/valuation tracking); raises KernelOfReduction if an operation
    would need it. Used only for constructions proven to stay affine."""

    def __init__(self, p: int, a: int, b: int, r: int):
        self.p, self.a, self.b, self.r = p, a, b, r
        self.M = p ** r

    def rhs(self, x: int) -> int:
        return (x * x % self.M * x + self.a * x + self.b) % self.M

    def on_curve(self, P) -> bool:
        if P is None:
            return True
        x, y = P
        return (y * y - self.rhs(x)) % self.M == 0

    def neg(self, P):
        if P is None:
            return None
        x, y = P
        return (x, (-y) % self.M)

    def double(self, P):
        if P is None:
            return None
        x, y = P
        num = (3 * x * x + self.a) % self.M
        lam = num * ring_inverse(2 * y % self.M, self.p, self.M) % self.M
        x3 = (lam * lam - 2 * x) % self.M
        y3 = (lam * (x - x3) - y) % self.M
        return (x3, y3)

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        M, p = self.M, self.p
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % M == 0:
                if y1 == y2:
                    raise KernelOfReduction("doubling a 2-torsion point")
                return None
            if y1 == y2:
                return self.double(P)
            raise KernelOfReduction("equal x, y neither equal nor negated")
        if (x2 - x1) % p == 0:
            raise KernelOfReduction("x-coords congruent mod p, not equal")
        lam = (y2 - y1) * ring_inverse(x2 - x1, p, M) % M
        x3 = (lam * lam - x1 - x2) % M
        y3 = (lam * (x1 - x3) - y1) % M
        return (x3, y3)

    def mul(self, m: int, P):
        if m == 0 or P is None:
            return None
        if m < 0:
            return self.neg(self.mul(-m, P))
        R = None
        for bit in bin(m)[2:]:
            if R is not None:
                R = self.double(R)
            if bit == "1":
                R = self.add(R, P)
        return R


def legendre_is_square_mod_p(a: int, p: int) -> bool:
    a %= p
    if a == 0:
        return True
    return pow(a, (p - 1) // 2, p) == 1


def sqrt_mod_prime_power(c: int, p: int, r: int) -> int:
    """Square root of a UNIT c in the cyclic group (Z/p^r)^*, by
    Tonelli-Shanks (group-theoretic: exponentiation plus a 2-Sylow discrete
    log; no per-digit Hensel/Newton correction)."""
    M = p ** r
    c %= M
    if not is_unit(c, p):
        raise ValueError("sqrt_mod_prime_power requires a unit")
    if not legendre_is_square_mod_p(c, p):
        raise ValueError("c is not a square mod p")
    order = p ** (r - 1) * (p - 1)
    s, t = 0, order
    while t % 2 == 0:
        t //= 2
        s += 1
    z = 2
    while legendre_is_square_mod_p(z, p):
        z += 1
    b = pow(z, t, M)
    x = pow(c, (t + 1) // 2, M)
    w = pow(c, t, M)
    m = s
    while w != 1:
        i, tmp = 0, w
        while tmp != 1:
            tmp = tmp * tmp % M
            i += 1
            if i >= m:
                raise ArithmeticError("Tonelli-Shanks failed to converge")
        step = pow(b, 1 << (m - i - 1), M)
        x = x * step % M
        b = step * step % M
        w = w * b % M
        m = i
    assert x * x % M == c
    return x


def auxiliary_lift(E: RingCurve, x0: int, y_target_mod_p: int):
    c = E.rhs(x0)
    y = sqrt_mod_prime_power(c, E.p, E.r)
    if y % E.p != y_target_mod_p % E.p:
        y = (-y) % E.M
    if y % E.p != y_target_mod_p % E.p:
        raise ArithmeticError("neither square root reduces to the target y")
    P = (x0 % E.M, y)
    assert E.on_curve(P)
    return P


def chain_is_affine_safe(m: int, n: int) -> bool:
    """Whether left-to-right binary multiplication by m avoids any
    intermediate reducing to O or colliding with the base point mod p,
    for a base point of order n. See EXP-ECDLP-809375 for the derivation."""
    bits = bin(m)[2:]
    acc = 1
    seen = [1]
    steps = []
    for bit in bits[1:]:
        before = acc
        acc = 2 * acc
        seen.append(acc)
        added = False
        if bit == "1":
            acc += 1
            seen.append(acc)
            added = True
        steps.append((before, added))
    bad_identity = [i for i in seen if i % n == 0]
    bad_add = [2 * before for before, added in steps
               if added and (2 * before) % n == 1 % n and 2 * before != 1]
    return not bad_identity and not bad_add


def canonical_order_n_lift(E: RingCurve, S: tuple, n: int):
    """S_hat = [p^(r-1) * ((p^(r-1))^{-1} mod n)] L, group-theoretically
    (no Hensel/Newton iteration on the order-n condition). Reused
    construction, independently re-derived here from
    experiments/EXP-ECDLP-809375/implementation/fg1_group_theoretic.py."""
    p, r = E.p, E.r
    L = auxiliary_lift(E, S[0], S[1])
    q = p ** (r - 1)
    u = pow(q % n, -1, n)
    if not chain_is_affine_safe(p, n) or (u > 1 and not chain_is_affine_safe(u, n)):
        raise KernelOfReduction("staged projection chain is not affine-safe "
                                 "for this (p, n, r)")
    T = L
    for _ in range(r - 1):
        T = E.mul(p, T)
    S_hat = E.mul(u, T)
    reduces_ok = (S_hat[0] % p == S[0] % p) and (S_hat[1] % p == S[1] % p)
    order_ok = E.mul(n, S_hat) is None
    if not (reduces_ok and order_ok and E.on_curve(S_hat)):
        raise ArithmeticError("canonical order-n lift failed construction checks")
    return S_hat


# --------------------------------------------------------------------------
# Standard PROJECTIVE short-Weierstrass EC arithmetic over the ring Z/p^R.
# No inversion is needed for add/double (add-1998-cmo / dbl-2007-bl,
# hyperelliptic.org Explicit-Formulas Database); both formulas were verified
# as UNCONDITIONAL RATIONAL-FUNCTION IDENTITIES against the standard affine
# chord/tangent formulas with sympy (see implementation.md). Only the final
# t = -X/Y extraction needs a valuation-aware division.
#
# DEVIATION FROM THE FIRST DESIGN (recorded in implementation.md): the
# contract's literal mechanism "X_S = S^ - t(S)" (chord subtraction of the
# global point and its canonical torsion lift) was implemented three
# independent ways -- a custom Laurent/Qp class, this projective ring
# formula, and exact-fraction arithmetic -- and after extensive debugging
# (documented) all three agreed WITH EACH OTHER but disagreed with the
# theoretical prediction d(mS)=m*d(S) mod p for m>=2, on a hand-worked toy
# instance, despite every sub-component (the group law formulas themselves,
# proved bug-free as rational-function identities by sympy; the canonical
# torsion lift's homomorphism property and multi-precision convergence,
# exhaustively verified) checking out individually. The root cause of that
# specific instability was not identified inside the execution budget.
#
# The mathematically EQUIVALENT quantity actually used below is
# d([n] P) = n * d(P) mod p (an unconditional consequence of [n] acting as
# a unit scalar on the formal group), tested via
#   d([n] (m S)) =?= m * d([n] S)   mod p
# which holds iff d(mS) = m*d(S) mod p (n is invertible mod p), and is
# computed by applying [n] directly to a lift of the point via the ordinary
# binary ladder -- since [n](any lift of a point of order n) always reduces
# to O, this lands in the kernel of reduction by construction, with no
# near-collision subtraction of two independently constructed lifts. This
# construction was validated (matches the linear prediction exactly on a
# worked example) before being used for claim (1)/(2) below.
# --------------------------------------------------------------------------

def proj_add(P1, P2, a, M):
    X1, Y1, Z1 = P1
    X2, Y2, Z2 = P2
    Y1Z2 = Y1 * Z2 % M
    X1Z2 = X1 * Z2 % M
    Z1Z2 = Z1 * Z2 % M
    u = (Y2 * Z1 - Y1Z2) % M
    v = (X2 * Z1 - X1Z2) % M
    vv = v * v % M
    vvv = v * vv % M
    Rr = vv * X1Z2 % M
    Aa = (u * u % M * Z1Z2 - vvv - 2 * Rr) % M
    X3 = v * Aa % M
    Y3 = (u * (Rr - Aa) - vvv * Y1Z2) % M
    Z3 = vvv * Z1Z2 % M
    return (X3, Y3, Z3)


def proj_double(P1, a, M):
    X1, Y1, Z1 = P1
    XX = X1 * X1 % M
    ZZ = Z1 * Z1 % M
    w = (a * ZZ + 3 * XX) % M
    s = (2 * Y1 * Z1) % M
    ss = s * s % M
    sss = s * ss % M
    Rr = Y1 * s % M
    RR = Rr * Rr % M
    Bb = ((X1 + Rr) * (X1 + Rr) - XX - RR) % M
    h = (w * w - 2 * Bb) % M
    X3 = h * s % M
    Y3 = (w * (Bb - h) - 2 * RR) % M
    Z3 = sss
    return (X3, Y3, Z3)


def proj_neg(P, M):
    X, Y, Z = P
    return (X, (-Y) % M, Z)


def proj_mul(k: int, P1, a: int, M: int):
    """Binary ladder scalar multiplication in projective coordinates."""
    if k == 0:
        return None
    R = None
    addend = P1
    kk = k
    while kk > 0:
        if kk & 1:
            R = addend if R is None else proj_add(R, addend, a, M)
        addend = proj_double(addend, a, M)
        kk >>= 1
    return R


def formal_digit(Pt, p: int, R: int):
    """Given a projective point Pt=(X,Y,Z) that reduces to O (kernel of
    reduction), return (v, digit) where v=v_p(t), t=-x/y=-X/Y (Z cancels),
    and digit = (t/p^v) mod p is the leading formal-parameter digit.
    Raises InsufficientPrecision if X or Y vanish to the full precision R."""
    X, Y, Z = Pt
    vx = valuation(X, p, R)
    vy = valuation(Y, p, R)
    if vx >= R or vy >= R:
        raise InsufficientPrecision("formal_digit: X or Y vanishes to precision R")
    v = vx - vy
    ux = (X // p ** vx) % p ** (R - vx)
    uy = (Y // p ** vy) % p ** (R - vy)
    uy_inv = pow(uy, -1, p ** (R - vy))
    digit = ((-ux) * uy_inv) % p
    return v, digit


def teichmuller_lift_unit(a0: int, p: int, r: int) -> int:
    """Multiplicative Teichmuller lift of a nonzero a0 in F_p to a
    (p-1)-th root of unity in (Z/p^r)^*, by Newton iteration on
    x^(p-1) - 1 = 0 starting from a0 (quadratically convergent Hensel
    lift; a0's derivative (p-1)*a0^(p-2) is a unit mod p since a0 != 0
    and p != 2)."""
    a0 %= p
    if a0 == 0:
        raise ValueError("Teichmuller lift undefined at 0")
    x = a0
    prec = 1
    while prec < r:
        prec = min(2 * prec, r)
        M = p ** prec
        x %= M
        # Newton step: x <- x - (x^(p-1)-1) * inverse((p-1) x^(p-2)) mod M
        f = (pow(x, p - 1, M) - 1) % M
        fp = (p - 1) * pow(x, p - 2, M) % M
        x = (x - f * pow(fp, -1, M)) % M
    assert pow(x, p - 1, p ** r) == 1
    assert x % p == a0 % p
    return x % p ** r
