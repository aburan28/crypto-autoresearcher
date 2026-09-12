"""arithmetic.py -- frozen field/point producer for EXP-CRYPTO-9225d2.

STATUS: source preparation only. No function in this module is invoked,
benchmarked, or self-tested by this task (TASK-20260907-ecd3a2). Maximum
runs for this task is zero; nothing here has been executed to produce a
measured count, a timing, or a fixture. A later, separately authorized
scientific-execution task must actually run this code under the admitted
cgroup/host contract before any count is a measurement.

Authorship / independence note (read before trusting anything downstream):
This file, `independent_checker.py`, and `count_predictor.py` in this same
delivery were drafted by the SAME author/session (the executor session for
TASK-20260907-ecd3a2). That means the checker and predictor in THIS PACKAGE
are NOT yet the independently authored/reviewed implementations the frozen
specification (experiments/EXP-CRYPTO-9225d2/specification.yaml, sections
`checker` and `execution_gate`) requires before any measurement counts as
scientific admission evidence. See `preparation-report.yaml` for the exact
outstanding independent-review obligation.

Scope preserved exactly from the frozen specification (no narrowing):
  - Field API boundary: M (multiply), S (square), I (invert) are separate
    counted API operations. I is charged once at the API boundary; internal
    Euclidean-algorithm integer multiplications/divisions are logged as
    separate non-field integer work, never as additional M/S.
  - Linear operations (add, sub, neg, small-integer scaling by 2/3/8,
    canonical reduction) are counted separately from M/S/I and are EXCLUDED
    from the GOE ruler numerator but still charged/logged (spec:
    goe_ruler.excluded_from_scalar_ruler_but_charged).
  - EFD-style Jacobian addition (common-Z rescaling variant) and doubling
    (dbl-2007-bl specialization for a=0 and the reduced a=1 curves) formulas,
    exactly as specified, including exceptional branches.
  - Variable-time binary (double-and-add), MSB-first, 256-bit scalar
    multiplication -- NOT constant-time, NOT a co-Z ladder.
  - Final affine normalization: 3M + 1S + 1I, all charged.
  - The "planted" top-level-multiplication-duplication variant, with its
    exact count identity M_planted = 2*M_reference, S_planted = S_reference,
    I_planted = I_reference for the same input/branch trace, and an ordered
    SHA-256 integrity sink consuming both serialized products.

No operand-is-one optimization is applied anywhere (spec: field_api.validation).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Optional, Tuple

# ---------------------------------------------------------------------------
# Curve parameters (secp256k1), copied verbatim from specification.arithmetic.curve
# ---------------------------------------------------------------------------

SECP256K1_P = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16
)
SECP256K1_A = 0
SECP256K1_B = 7
SECP256K1_GX = int(
    "79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798", 16
)
SECP256K1_GY = int(
    "483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8", 16
)
SECP256K1_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16
)
SECP256K1_COFACTOR = 1


@dataclass
class CurveParams:
    """A short-Weierstrass curve y^2 = x^3 + a*x + b over F_p.

    The reduced rho subgroup curves (E: y^2 = x^3 + x, i.e. a=1, b=0) use
    this same structure with their own certified p, N and generator, per
    specification.rho.group_construction. Realized reduced-curve instances
    are produced by fixture_generator.py, never invented here.
    """

    p: int
    a: int
    b: int


SECP256K1 = CurveParams(p=SECP256K1_P, a=SECP256K1_A, b=SECP256K1_B)


# ---------------------------------------------------------------------------
# Counted field API
# ---------------------------------------------------------------------------


@dataclass
class OperationCounters:
    """Separate tallies as required by specification.arithmetic.field_api and
    specification.goe_ruler.excluded_from_scalar_ruler_but_charged.

    `M`, `S`, `I` are the GOE-ruler-relevant field API call counts.
    `linear_ops` covers add/sub/neg/small-integer-scale/canonical-reduction.
    `integer_work` covers I's internal extended-Euclid multiplications and
    divisions (never folded into M/S).
    `branch_copy_ops` covers exceptional-branch bookkeeping (identity
    returns, tag checks, copies) that carry no field call.
    `hash_calls` / `sink_bytes` are non-field bookkeeping for the planted
    integrity sink and, in rho.py, for partition/DP hashing.
    """

    M: int = 0
    S: int = 0
    I: int = 0
    linear_ops: int = 0
    integer_work: int = 0
    branch_copy_ops: int = 0
    hash_calls: int = 0
    sink_bytes: int = 0

    def add(self, other: "OperationCounters") -> None:
        self.M += other.M
        self.S += other.S
        self.I += other.I
        self.linear_ops += other.linear_ops
        self.integer_work += other.integer_work
        self.branch_copy_ops += other.branch_copy_ops
        self.hash_calls += other.hash_calls
        self.sink_bytes += other.sink_bytes

    def raw_goe_rational(self) -> Tuple[int, int]:
        """Exact rational raw_GOE = (M + S + 100*I) / 16, as (numerator, 16).

        Spec: goe_ruler.formula and goe_ruler.exact_representation -- compare
        as exact rationals before any decimal rendering.
        """
        numerator = self.M + self.S + 100 * self.I
        return numerator, 16


class FieldElement:
    """A canonical residue modulo a given prime, with a bound counter set.

    Every arithmetic method below records its own API-boundary call into the
    `counters` object passed at construction/operation time. This class does
    not memoize or special-case operand==1, per field_api.validation.
    """

    __slots__ = ("value", "p")

    def __init__(self, value: int, p: int):
        # Canonicalization is itself charged as a linear/reduction op by the
        # caller when appropriate; the constructor only stores a canonical
        # residue and does not itself emit a counted API call.
        if not (0 <= value < p):
            value = value % p
        self.value = value
        self.p = p

    # -- field API, each a distinct counted operation -----------------

    def mul(self, other: "FieldElement", counters: OperationCounters) -> "FieldElement":
        if self.p != other.p:
            raise ValueError("mismatched modulus")
        counters.M += 1
        return FieldElement((self.value * other.value) % self.p, self.p)

    def sqr(self, counters: OperationCounters) -> "FieldElement":
        counters.S += 1
        return FieldElement((self.value * self.value) % self.p, self.p)

    def inv(self, counters: OperationCounters) -> "FieldElement":
        """Extended Euclidean inversion of a nonzero canonical residue.

        Charges exactly one I at the API boundary (spec: field_api.I).
        Internal quotient/remainder/coefficient updates are logged as
        `integer_work`, never as additional M/S. Zero is an error, per spec.
        """
        if self.value == 0:
            raise ZeroDivisionError("inversion of zero is an error (field_api.I)")
        r0, r1 = self.p, self.value
        s0, s1 = 0, 1
        while r1 != 0:
            q = r0 // r1
            counters.integer_work += 1  # the quotient floor(r0/r1)
            r0, r1 = r1, r0 - q * r1
            counters.integer_work += 1  # simultaneous remainder update
            s0, s1 = s1, s0 - q * s1
            counters.integer_work += 1  # simultaneous coefficient update
        counters.I += 1
        return FieldElement(s0 % self.p, self.p)

    # -- linear operations, separately counted, excluded from GOE numerator --

    def add(self, other: "FieldElement", counters: OperationCounters) -> "FieldElement":
        counters.linear_ops += 1
        return FieldElement((self.value + other.value) % self.p, self.p)

    def sub(self, other: "FieldElement", counters: OperationCounters) -> "FieldElement":
        counters.linear_ops += 1
        return FieldElement((self.value - other.value) % self.p, self.p)

    def neg(self, counters: OperationCounters) -> "FieldElement":
        counters.linear_ops += 1
        return FieldElement((-self.value) % self.p, self.p)

    def scale_small(self, k: int, counters: OperationCounters) -> "FieldElement":
        """Scale by a small explicit integer constant (2, 3, or 8) using
        explicit additions/doublings, never a silently-counted field M
        (spec: field_api.linear_operations)."""
        if k not in (2, 3, 8):
            raise ValueError("scale_small is only defined for constants 2, 3, 8")
        acc = self
        # k as repeated doubling/addition, each step a counted linear op.
        if k == 2:
            return acc.add(acc, counters)
        if k == 3:
            doubled = acc.add(acc, counters)
            return doubled.add(acc, counters)
        if k == 8:
            d1 = acc.add(acc, counters)
            d2 = d1.add(d1, counters)
            d3 = d2.add(d2, counters)
            return d3
        raise AssertionError("unreachable")

    def is_zero(self) -> bool:
        return self.value == 0

    def equals(self, other: "FieldElement") -> bool:
        return self.p == other.p and self.value == other.value


# ---------------------------------------------------------------------------
# Jacobian points (X, Y, Z) with Z affine convention x = X/Z^2, y = Y/Z^3
# ---------------------------------------------------------------------------


@dataclass
class JacobianPoint:
    X: FieldElement
    Y: FieldElement
    Z: FieldElement
    is_identity: bool = False  # distinct tag, never an unchecked (0,0,0)


def identity_point(p: int) -> JacobianPoint:
    zero = FieldElement(0, p)
    return JacobianPoint(zero, zero, zero, is_identity=True)


def affine_to_jacobian(x: int, y: int, p: int) -> JacobianPoint:
    return JacobianPoint(FieldElement(x, p), FieldElement(y, p), FieldElement(1, p), is_identity=False)


# ---------------------------------------------------------------------------
# EFD-style common-Z rescaling addition (spec: arithmetic.addition)
# ---------------------------------------------------------------------------


def point_add(p1: JacobianPoint, p2: JacobianPoint, curve: CurveParams,
              counters: OperationCounters) -> JacobianPoint:
    """Full ADD with rescale-to-common-Z, exactly per specification.

    identity: return the other point after validating its tag; count the
      branch and copies but no field calls.
    rescale_finite: seven M and two S, charged even if a coordinate is one.
    exceptional_after_rescaling: equal-U/equal-V -> DOUBLE(first point),
      retaining rescale cost; equal-U/opposite-V -> O, retaining rescale cost;
      equality branch takes precedence when both Y are zero.
    common_z_formula: generic full ADD costs twelve M and four S total
      (seven+two rescale, plus five M and two S common-Z work) before output
      normalization.
    """
    p_mod = curve.p

    if p1.is_identity:
        counters.branch_copy_ops += 1
        return JacobianPoint(p2.X, p2.Y, p2.Z, is_identity=p2.is_identity)
    if p2.is_identity:
        counters.branch_copy_ops += 1
        return JacobianPoint(p1.X, p1.Y, p1.Z, is_identity=p1.is_identity)

    # rescale_finite: seven M and two S
    z1sq = p1.Z.sqr(counters)
    z2sq = p2.Z.sqr(counters)
    z1cube = z1sq.mul(p1.Z, counters)
    z2cube = z2sq.mul(p2.Z, counters)
    U1 = p1.X.mul(z2sq, counters)
    V1 = p1.Y.mul(z2cube, counters)
    U2 = p2.X.mul(z1sq, counters)
    V2 = p2.Y.mul(z1cube, counters)
    Z = p1.Z.mul(p2.Z, counters)

    if U1.equals(U2):
        counters.branch_copy_ops += 1
        if V1.equals(V2):
            # DOUBLE the original first point, retaining the rescale cost above.
            return point_double(p1, curve, counters)
        # equal-U opposite-V (including both-zero handled by equality branch
        # above, whose doubling returns O): return identity.
        return identity_point(p_mod)
    # any remaining same-X case would be invalid input; not checked here
    # (the frozen spec treats it as invalid input, not a silent branch).

    h = U2.sub(U1, counters)
    j = V2.sub(V1, counters)
    A = h.sqr(counters)
    B = U1.mul(A, counters)
    C = U2.mul(A, counters)
    D = j.sqr(counters)
    X3 = D.sub(B, counters).sub(C, counters)
    BX3 = B.sub(X3, counters)
    CB = C.sub(B, counters)
    Y3 = j.mul(BX3, counters).sub(V1.mul(CB, counters), counters)
    Z3 = Z.mul(h, counters)

    return JacobianPoint(X3, Y3, Z3, is_identity=False)


# ---------------------------------------------------------------------------
# EFD dbl-2007-bl doubling, specialized per spec.arithmetic.doubling
# ---------------------------------------------------------------------------


def point_double(pt: JacobianPoint, curve: CurveParams,
                  counters: OperationCounters) -> JacobianPoint:
    """Doubling with the two frozen specializations:

    a=0 (secp256k1): omit only ZZ^2, retaining ZZ for Z3 -> one M, seven S.
    a=1 (reduced rho curves): compute Z4=S(ZZ), W=3*XX+Z4 -> one M, eight S.
    No multiplication by `a` is introduced in either specialization.
    """
    p_mod = curve.p
    if pt.is_identity:
        counters.branch_copy_ops += 1
        return identity_point(p_mod)
    if pt.Y.is_zero():
        counters.branch_copy_ops += 1
        return identity_point(p_mod)

    XX = pt.X.sqr(counters)
    YY = pt.Y.sqr(counters)
    YYYY = YY.sqr(counters)
    ZZ = pt.Z.sqr(counters)

    x_plus_yy = pt.X.add(YY, counters)
    s1 = x_plus_yy.sqr(counters)
    s1 = s1.sub(XX, counters).sub(YYYY, counters)
    V = s1.scale_small(2, counters)

    if curve.a == 0:
        W = XX.scale_small(3, counters)  # a*ZZ^2 term omitted for a=0
    elif curve.a == 1:
        Z4 = ZZ.sqr(counters)
        W = XX.scale_small(3, counters).add(Z4, counters)
    else:
        raise ValueError("only the a=0 and a=1 specializations are frozen by spec")

    T = W.sqr(counters).sub(V.scale_small(2, counters), counters)
    X3 = T
    Y3 = W.mul(V.sub(T, counters), counters).sub(YYYY.scale_small(8, counters), counters)
    Z3 = pt.Y.add(pt.Z, counters).sqr(counters).sub(YY, counters).sub(ZZ, counters)

    return JacobianPoint(X3, Y3, Z3, is_identity=False)


# ---------------------------------------------------------------------------
# Normalization (spec: arithmetic.normalization) -- 3M, 1S, 1I
# ---------------------------------------------------------------------------


def normalize(pt: JacobianPoint, curve: CurveParams,
              counters: OperationCounters) -> Tuple[Optional[int], Optional[int]]:
    """Return canonical affine (x, y), or (None, None) for the identity.

    Charges exactly 3 M, 1 S, 1 I for a finite point; identity has no
    inversion (spec.arithmetic.normalization).
    """
    if pt.is_identity:
        counters.branch_copy_ops += 1
        return None, None
    zi = pt.Z.inv(counters)
    z2 = zi.sqr(counters)
    z3 = z2.mul(zi, counters)
    x = pt.X.mul(z2, counters)
    y = pt.Y.mul(z3, counters)
    return x.value, y.value


# ---------------------------------------------------------------------------
# Variable-time binary (double-and-add) scalar multiplication
# ---------------------------------------------------------------------------


def scalar_multiply(k: int, gx: int, gy: int, curve: CurveParams,
                     counters: OperationCounters) -> JacobianPoint:
    """Exactly 256-bit MSB-first double-and-add, per spec.arithmetic.scalar_algorithm.

    Uses exactly 256 bits regardless of the scalar's actual bit length
    (leading zero bits still perform DOUBLE(O) branch/copy work, per the
    frozen 'exactly 256 bits, most significant first' instruction).

    Normalization is a DELIBERATE CALLER RESPONSIBILITY, not part of this
    routine's own charged-count contract (C8 resolution, branch b): this
    function returns the raw, unnormalized Jacobian point `R`. Although
    spec.arithmetic.scalar_algorithm's prose sentence "Normalize the final R
    once" appears in the same paragraph as this algorithm's description, that
    final 3M+1S+1I normalization charge is intentionally NOT folded into
    scalar_multiply's own M/S/I tally here. A caller that needs canonical
    affine coordinates (or the normalization charge counted against a
    specific cell) must call `normalize(R, curve, counters)` explicitly on
    the returned point, using the same `counters` object if the normalization
    cost is to be attributed to this same job/cell. See
    implementation-manifest.yaml's revise_fixes_20260912.summary.C8 for the
    corresponding manifest-level statement of this choice. `scalar_multiply_null` and
    `scalar_multiply_planted` inherit this same caller-responsibility
    contract, for consistency across all three routine variants.
    """
    R = identity_point(curve.p)
    base = affine_to_jacobian(gx, gy, curve.p)
    for i in range(255, -1, -1):
        R = point_double(R, curve, counters)
        bit = (k >> i) & 1
        if bit == 1:
            R = point_add(R, base, curve, counters)
    return R


# ---------------------------------------------------------------------------
# Planted top-level-multiplication-duplication variant
# ---------------------------------------------------------------------------


@dataclass
class PlantedMulResult:
    value: "FieldElement"
    sink_digest: bytes


def planted_mul(a: FieldElement, b: FieldElement, counters: OperationCounters,
                 sink_state: bytearray) -> FieldElement:
    """Replace one top-level M(a,b) with two separate M evaluations, compare,
    and feed both serialized results into an ordered SHA-256 integrity sink
    before returning the first (spec.arithmetic.planted.definition).

    Exact count identity for the same input/branch trace, relative to the
    unplanted reference routine that calls `FieldElement.mul` once per
    top-level M:
        M_planted   = 2 * M_reference
        S_planted   = S_reference
        I_planted   = I_reference
    Do NOT duplicate operations inside S or I (per spec).
    """
    r1 = a.mul(b, counters)
    r2 = a.mul(b, counters)
    if r1.value != r2.value:
        raise RuntimeError(
            "planted duplication produced disagreeing top-level products; "
            "this is an exact-count/output integrity failure, not a timing event"
        )
    counters.hash_calls += 1
    payload = r1.value.to_bytes(32, "big") + r2.value.to_bytes(32, "big")
    counters.sink_bytes += len(payload)
    sink_state.extend(hashlib.sha256(bytes(sink_state) + payload).digest())
    return r1


def planted_expected_factor(m_ref: int, s_ref: int, i_ref: int) -> Tuple[int, int]:
    """Exact rational expected weighted-overhead factor as (numerator, denominator):
        (2*M_reference + S_reference + 100*I_reference)
        / (M_reference + S_reference + 100*I_reference)
    (spec.arithmetic.planted.expected_factor). Not evaluated against any
    fixture in this task -- interface/formula only.
    """
    denom = m_ref + s_ref + 100 * i_ref
    numer = 2 * m_ref + s_ref + 100 * i_ref
    return numer, denom


# ---------------------------------------------------------------------------
# Planted scalar-multiplication composition (C9 completion, branch a)
#
# These three functions mirror point_add / point_double / scalar_multiply
# structurally, term for term and branch for branch, with the sole change
# that every top-level M(a,b) call site is routed through `planted_mul`
# (which itself performs two separate M evaluations, a comparison, and an
# ordered SHA-256 integrity-sink update) instead of calling
# `FieldElement.mul` directly. S and I call sites are unchanged, per
# spec.arithmetic.planted.definition's "do not duplicate operations inside S
# or I." This realizes M_planted = 2*M_reference, S_planted = S_reference,
# I_planted = I_reference for the same input/branch trace
# (spec.arithmetic.planted.exact_count_identity), at the level of a full
# 256-bit scalar multiplication, not only the low-level primitive above.
# ---------------------------------------------------------------------------


def point_add_planted(p1: JacobianPoint, p2: JacobianPoint, curve: CurveParams,
                       counters: OperationCounters, sink_state: bytearray) -> JacobianPoint:
    """Planted mirror of `point_add`: identical identity/rescale/exceptional/
    common-Z branch structure (including the C6-corrected Y3 formula
    Y3 = M(j, B-X3) - M(V1, C-B)), with each of the twelve top-level M call
    sites of a generic full ADD routed through `planted_mul` instead of
    `FieldElement.mul`. S call sites (`sqr`) and linear ops are unchanged.
    """
    p_mod = curve.p

    if p1.is_identity:
        counters.branch_copy_ops += 1
        return JacobianPoint(p2.X, p2.Y, p2.Z, is_identity=p2.is_identity)
    if p2.is_identity:
        counters.branch_copy_ops += 1
        return JacobianPoint(p1.X, p1.Y, p1.Z, is_identity=p1.is_identity)

    # rescale_finite: seven M (planted) and two S
    z1sq = p1.Z.sqr(counters)
    z2sq = p2.Z.sqr(counters)
    z1cube = planted_mul(z1sq, p1.Z, counters, sink_state)
    z2cube = planted_mul(z2sq, p2.Z, counters, sink_state)
    U1 = planted_mul(p1.X, z2sq, counters, sink_state)
    V1 = planted_mul(p1.Y, z2cube, counters, sink_state)
    U2 = planted_mul(p2.X, z1sq, counters, sink_state)
    V2 = planted_mul(p2.Y, z1cube, counters, sink_state)
    Z = planted_mul(p1.Z, p2.Z, counters, sink_state)

    if U1.equals(U2):
        counters.branch_copy_ops += 1
        if V1.equals(V2):
            return point_double_planted(p1, curve, counters, sink_state)
        return identity_point(p_mod)

    h = U2.sub(U1, counters)
    j = V2.sub(V1, counters)
    A = h.sqr(counters)
    B = planted_mul(U1, A, counters, sink_state)
    C = planted_mul(U2, A, counters, sink_state)
    D = j.sqr(counters)
    X3 = D.sub(B, counters).sub(C, counters)
    BX3 = B.sub(X3, counters)
    CB = C.sub(B, counters)
    Y3 = planted_mul(j, BX3, counters, sink_state).sub(
        planted_mul(V1, CB, counters, sink_state), counters
    )
    Z3 = planted_mul(Z, h, counters, sink_state)

    return JacobianPoint(X3, Y3, Z3, is_identity=False)


def point_double_planted(pt: JacobianPoint, curve: CurveParams,
                          counters: OperationCounters, sink_state: bytearray) -> JacobianPoint:
    """Planted mirror of `point_double`: identical exceptional/polynomial
    branch structure and both a=0/a=1 specializations, with the single
    top-level M call site (Y3 = M(W, V-T) - 8*YYYY) routed through
    `planted_mul` instead of `FieldElement.mul`.
    """
    p_mod = curve.p
    if pt.is_identity:
        counters.branch_copy_ops += 1
        return identity_point(p_mod)
    if pt.Y.is_zero():
        counters.branch_copy_ops += 1
        return identity_point(p_mod)

    XX = pt.X.sqr(counters)
    YY = pt.Y.sqr(counters)
    YYYY = YY.sqr(counters)
    ZZ = pt.Z.sqr(counters)

    x_plus_yy = pt.X.add(YY, counters)
    s1 = x_plus_yy.sqr(counters)
    s1 = s1.sub(XX, counters).sub(YYYY, counters)
    V = s1.scale_small(2, counters)

    if curve.a == 0:
        W = XX.scale_small(3, counters)  # a*ZZ^2 term omitted for a=0
    elif curve.a == 1:
        Z4 = ZZ.sqr(counters)
        W = XX.scale_small(3, counters).add(Z4, counters)
    else:
        raise ValueError("only the a=0 and a=1 specializations are frozen by spec")

    T = W.sqr(counters).sub(V.scale_small(2, counters), counters)
    X3 = T
    Y3 = planted_mul(W, V.sub(T, counters), counters, sink_state).sub(
        YYYY.scale_small(8, counters), counters
    )
    Z3 = pt.Y.add(pt.Z, counters).sqr(counters).sub(YY, counters).sub(ZZ, counters)

    return JacobianPoint(X3, Y3, Z3, is_identity=False)


def scalar_multiply_planted(k: int, gx: int, gy: int, curve: CurveParams,
                             counters: OperationCounters, sink_state: bytearray) -> JacobianPoint:
    """Planted composition mirroring `scalar_multiply`/`scalar_multiply_null`'s
    structure (C9 completion): identical 256-bit MSB-first double-and-add
    control flow, threading `planted_mul` into every top-level M call site of
    the full scalar multiplication via `point_add_planted`/
    `point_double_planted`, giving M_planted = 2*M_reference for the same
    input/branch trace (spec.arithmetic.planted.exact_count_identity). The
    caller supplies `sink_state`, the ordered SHA-256 integrity-sink buffer
    (spec.arithmetic.planted.definition), so sink evolution can be bound to
    an entire scalar multiplication (or a whole job) rather than reset per
    call.

    Like `scalar_multiply`, this function returns the raw unnormalized
    Jacobian point `R`; normalization is a deliberate caller responsibility
    (C8 resolution, branch b -- see `scalar_multiply`'s docstring), not part
    of this routine's own charged-count contract.
    """
    R = identity_point(curve.p)
    base = affine_to_jacobian(gx, gy, curve.p)
    for i in range(255, -1, -1):
        R = point_double_planted(R, curve, counters, sink_state)
        bit = (k >> i) & 1
        if bit == 1:
            R = point_add_planted(R, base, curve, counters, sink_state)
    return R


# ---------------------------------------------------------------------------
# Null-control scalar routine placeholder
# ---------------------------------------------------------------------------


def scalar_multiply_null(k: int, gx: int, gy: int, curve: CurveParams,
                          counters: OperationCounters) -> JacobianPoint:
    """The 'null' routine is the same unplanted algorithm as `scalar_multiply`,
    applied to a distinct domain-separated scalar stream (spec: deterministic_
    bytes.scalar_domains -- 'null uses GOE9225/null/scalar'). Stream
    generation itself belongs to fixture_generator.py, not here; this
    function exists so driver.py can bind a distinct callable per routine
    label without conflating null-stream generation with the reference
    formula implementation.
    """
    return scalar_multiply(k, gx, gy, curve, counters)


__all__ = [
    "SECP256K1",
    "SECP256K1_N",
    "SECP256K1_GX",
    "SECP256K1_GY",
    "CurveParams",
    "OperationCounters",
    "FieldElement",
    "JacobianPoint",
    "identity_point",
    "affine_to_jacobian",
    "point_add",
    "point_double",
    "normalize",
    "scalar_multiply",
    "scalar_multiply_null",
    "planted_mul",
    "planted_expected_factor",
    "point_add_planted",
    "point_double_planted",
    "scalar_multiply_planted",
]

# NOTE: this module performs no I/O, spawns no process, and calls none of its
# own functions at import time. Nothing above has been executed as part of
# TASK-20260907-ecd3a2; only `python3 -m py_compile` static syntax checking
# has been run against this file (see preparation-report.yaml).
