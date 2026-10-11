"""
Independent second checker for EXP-CRYPTO-9225d2.

Authored from experiments/EXP-CRYPTO-9225d2/specification.yaml ALONE. No other
file in this repository (not the existing independent_checker.py, not
arithmetic.py, not any report/manifest/ledger record) was read while writing
this module. See independence-report-v2.yaml for the required attestation.

Structural independence from the specification's own main-arithmetic route
--------------------------------------------------------------------------
specification.arithmetic (the producer route this checker must NOT reuse)
represents points as Jacobian-style triples (X, Y, Z) with the stated
coordinate convention x=X/Z^2, y=Y/Z^3, and computes ADD via the EFD-style
"rescale_finite" + "common_z_formula" sequence and DOUBLE via the EFD
dbl-2007-bl polynomial (XX, YY, YYYY, ZZ, V, W, T, ...). Both routes share no
step names, no intermediate variables and, most importantly, a structurally
different mathematical object: a Jacobian triple's group law is closed under
an equivalence class of representatives (X,Y,Z) ~ (r^2 X, r^3 Y, rZ), while
the classical affine slope law below operates directly on the unique
canonical representative (x, y) with no free scaling parameter and no Z
coordinate at all. Formally: the Jacobian route computes seven M + two S of
"rescale" work purely to cancel denominators, then a further 5 M + 2 S "common
Z" step, and only ever inverts a field element once, at the very end, in
normalize(). The affine route below inverts a field element inside *every*
non-exceptional ADD and DOUBLE call (via Fermat's little theorem, not extended
Euclid — see inv_mod below), and never introduces a Z coordinate or a
rescale/common-Z step at all. These are two different algorithms computing the
same group law, not a renaming of one algorithm.

Everything below is a pure implementation. No function here is ever called
from this file; no fixture, certificate, curve point or scalar is fabricated
or exercised. See independence-report-v2.yaml's no_scientific_run_attestation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

# An affine point is represented as either the sentinel `Identity` (a
# distinct tag, never an unchecked (0,0,0)-style arbitrary triple, matching
# specification.arithmetic.coordinate_convention's requirement that identity
# use a distinct tag) or a finite tuple (x, y) of canonical residues mod p.

Identity = None  # distinct sentinel object; finite points are (x, y) tuples
AffinePoint = Optional[Tuple[int, int]]


@dataclass(frozen=True)
class Curve:
    """A short Weierstrass curve y^2 = x^3 + a*x + b over F_p."""

    p: int
    a: int
    b: int


def is_identity(point: AffinePoint) -> bool:
    return point is None


# ---------------------------------------------------------------------------
# Independent field arithmetic.
#
# specification.arithmetic.field_api.I specifies the PRODUCER's inversion
# method exactly: "extended Euclid on (p,a), with quotient floor(r0/r1),
# simultaneous remainder/coefficient updates". specification.arithmetic.checker
# requires "independent field arithmetic" for this second checker, so this
# module deliberately takes a structurally different algorithmic route to
# inversion: Fermat's little theorem, x^(p-2) mod p, which needs no gcd
# recursion, no remainder sequence and no back-substitution of Bezout
# coefficients at all.
# ---------------------------------------------------------------------------


def inv_mod(x: int, p: int) -> int:
    """Invert a nonzero residue x modulo prime p via Fermat's little theorem.

    Structurally independent of an extended-Euclid inverse: no quotient/
    remainder recursion, no coefficient back-substitution. Zero is an error,
    matching specification.arithmetic.field_api.I's "Zero is an error."
    """
    xr = x % p
    if xr == 0:
        raise ValueError("cannot invert zero residue")
    return pow(xr, p - 2, p)


def canonical(x: int, p: int) -> int:
    return x % p


# ---------------------------------------------------------------------------
# Independent affine point arithmetic: classical slope formulas.
# ---------------------------------------------------------------------------


def negate(point: AffinePoint, curve: Curve) -> AffinePoint:
    if is_identity(point):
        return Identity
    x, y = point
    return (x % curve.p, (-y) % curve.p)


def affine_double(point: AffinePoint, curve: Curve) -> AffinePoint:
    """DOUBLE via the standard tangent-slope formula lam=(3x^2+a)/(2y)."""
    p = curve.p
    if is_identity(point):
        # DOUBLE(O) = O; specification.doubling.exceptional: "O returns O".
        return Identity
    x1, y1 = point
    if y1 % p == 0:
        # finite Y=0 returns O before any polynomial/slope calls, matching
        # specification.doubling.exceptional: "finite Y=0 returns O before
        # polynomial calls."
        return Identity
    lam = ((3 * x1 * x1 + curve.a) * inv_mod((2 * y1) % p, p)) % p
    x3 = (lam * lam - 2 * x1) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3 % p, y3 % p)


def affine_add(p1: AffinePoint, p2: AffinePoint, curve: Curve) -> AffinePoint:
    """ADD via the classical slope formula lam=(y2-y1)/(x2-x1)."""
    p = curve.p
    if is_identity(p1):
        # specification.addition.identity: "Return the other point after
        # validating its tag; count the branch and copies but no field calls."
        return p2
    if is_identity(p2):
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if (x1 - x2) % p == 0:
        if (y1 + y2) % p == 0:
            # specification.addition.exceptional_after_rescaling: "If U1=U2
            # and V1=-V2, return O." (affine analogue: same x, opposite y.)
            return Identity
        if (y1 - y2) % p == 0:
            # "If U1=U2 and V1=V2, DOUBLE the original first point ... the
            # equality branch takes precedence when both Y values are zero
            # and its doubling returns O."
            return affine_double(p1, curve)
        # "Any remaining same-X case is invalid input."
        raise ValueError("invalid input: identical x, unrelated y (non-canonical)")
    lam = ((y2 - y1) * inv_mod((x2 - x1) % p, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3 % p, y3 % p)


def scalar_multiply(k: int, point: AffinePoint, curve: Curve) -> AffinePoint:
    """Independent scalar-loop implementation: MSB-first double-and-add.

    Mirrors the high-level algorithm shape described in
    specification.arithmetic.scalar_algorithm (start at O, DOUBLE every bit,
    ADD on set bits) but is executed entirely through the affine slope
    routines above, never through the producer's Jacobian ADD/DOUBLE.
    """
    if k < 0:
        raise ValueError("negative scalars are not supported by this checker")
    result: AffinePoint = Identity
    if k == 0:
        return result
    for bit in bin(k)[2:]:
        result = affine_double(result, curve)
        if bit == "1":
            result = affine_add(result, point, curve)
    return result


def points_equal(p1: AffinePoint, p2: AffinePoint, curve: Curve) -> bool:
    if is_identity(p1) or is_identity(p2):
        return is_identity(p1) and is_identity(p2)
    x1, y1 = p1
    x2, y2 = p2
    return (x1 - x2) % curve.p == 0 and (y1 - y2) % curve.p == 0


# ---------------------------------------------------------------------------
# specification.arithmetic.checker.exceptional_controls:
#   "O+O, O+G, G+O, G+(-G), G+G, DOUBLE(O), and the order-two point (0,0) on
#   each reduced a=1 curve; compare each to independent affine arithmetic.
#   They are fixed checks inside fixture admission, not extra rho samples."
# ---------------------------------------------------------------------------


def run_generator_exceptional_controls(curve: Curve, generator: Tuple[int, int]) -> dict:
    """Evaluate the six generator-relative exceptional controls.

    Returns a dict of control name -> (result, expected-identity boolean or
    point), computed purely from the affine routines above. Does not fetch,
    fabricate, or assume any specific curve/generator; the caller supplies
    `curve` and `generator` (e.g. secp256k1's G, or a reduced rung's G).
    """
    g = generator
    neg_g = negate(g, curve)
    double_g = affine_double(g, curve)

    o_plus_o = affine_add(Identity, Identity, curve)
    o_plus_g = affine_add(Identity, g, curve)
    g_plus_o = affine_add(g, Identity, curve)
    g_plus_neg_g = affine_add(g, neg_g, curve)
    g_plus_g = affine_add(g, g, curve)
    double_o = affine_double(Identity, curve)

    return {
        "O+O": {"result": o_plus_o, "expected_identity": True,
                "passes": is_identity(o_plus_o)},
        "O+G": {"result": o_plus_g, "expected": g,
                "passes": points_equal(o_plus_g, g, curve)},
        "G+O": {"result": g_plus_o, "expected": g,
                "passes": points_equal(g_plus_o, g, curve)},
        "G+(-G)": {"result": g_plus_neg_g, "expected_identity": True,
                   "passes": is_identity(g_plus_neg_g)},
        "G+G": {"result": g_plus_g, "expected": double_g,
                "passes": points_equal(g_plus_g, double_g, curve)},
        "DOUBLE(O)": {"result": double_o, "expected_identity": True,
                      "passes": is_identity(double_o)},
    }


def run_order_two_point_control(curve: Curve) -> dict:
    """(0,0) on a reduced a=1 curve E: y^2 = x^3 + x (+ b, b=0 per spec's
    rho.group_construction, which states "Use E:y^2=x^3+x over F_p").

    (0,0) satisfies y^2=0=x^3+a*x+b when a is arbitrary and b=0, since both
    sides are 0 at x=0. Its doubling must return O because its Y coordinate
    is zero, per specification.doubling.exceptional, which independently
    certifies it as a 2-torsion (order-two) point.
    """
    if curve.a != 1 or curve.b != 0:
        raise ValueError(
            "order-two control is only defined, per specification.rho."
            "group_construction, for the reduced curves E: y^2=x^3+x (a=1, b=0)"
        )
    p = curve.p
    point = (0, 0)
    lhs = (point[1] * point[1]) % p
    rhs = (point[0] ** 3 + curve.a * point[0] + curve.b) % p
    on_curve = lhs == rhs
    doubled = affine_double(point, curve)
    return {
        "point": point,
        "on_curve": on_curve,
        "double_result": doubled,
        "passes": on_curve and is_identity(doubled),
    }


# ---------------------------------------------------------------------------
# Structural (guarded, non-executing) interfaces.
#
# specification.rho.group_construction.prime_certificates describes
# "Complete recursively checked factorization-based Pocklington certificates,
# with trial-division base cases below 65536; retain all factors, witnesses
# and full-factor product checks." specification.rho.independent_check
# describes replaying a stored trail's "ordered transition digest, step
# count, endpoint/censor reason and all DP/round events" from its "public
# start and frozen walk law."
#
# Neither function below is given a real certificate or trail in this task
# (zero scientific runs, no fixture). Both therefore raise RuntimeError
# rather than fabricate a verification result. Their signatures and
# docstrings document the checks a genuine implementation would perform.
# ---------------------------------------------------------------------------


def verify_pocklington_certificate(N: int, certificate: dict) -> bool:
    """Structural interface for independently verifying a Pocklington
    primality certificate for N, per specification.rho.group_construction.
    prime_certificates.

    A genuine implementation would: recursively verify each declared factor's
    own certificate (or trial-division base case below 65536), check the
    supplied witness for Pocklington's theorem at each level, and verify the
    full-factor product equals N-1 (or the relevant cofactor) exactly.

    Guarded: this task supplies no real certificate, so this function always
    refuses rather than fabricate a pass/fail.
    """
    raise RuntimeError(
        "verify_pocklington_certificate requires a genuine recursively "
        "checked factorization certificate (factors, witnesses, full-factor "
        "product checks) that was not supplied in this zero-execution "
        "implementation-review task; refusing to fabricate a verification "
        "result."
    )


def trial_division_primality_base_case(n: int) -> bool:
    """Pure trial-division primality check for base cases below 65536, as
    named by specification.rho.group_construction.prime_certificates. This
    function needs no external certificate/trail input (only the integer n
    itself), so it is not guarded — but per this task's zero-execution
    discipline it is never called anywhere in this module or elsewhere.
    """
    if n < 2:
        return False
    if n < 65536:
        i = 2
        while i * i <= n:
            if n % i == 0:
                return False
            i += 1
        return True
    raise ValueError("trial_division_primality_base_case is only defined below 65536")


def replay_rho_trail(trail_row: dict, walk_key: bytes, curve: Curve,
                      generator: Tuple[int, int], target: AffinePoint) -> dict:
    """Structural interface for the independent affine rho-trail replay
    described in specification.rho.independent_check: "replays every
    completed trail from its public start and frozen walk law, checking the
    digest, endpoints, coefficient recurrence, first qualifying DP, and
    long-trail stopping point. It also reconstructs coordinator event order
    and the recovery."

    A genuine implementation would replay the trail's transitions using the
    affine_add/affine_double routines above (with the stated branch/DP/hash
    rules from specification.rho.transition), recompute the ordered
    transition digest, and compare every field to `trail_row`.

    Guarded: this task supplies no real trail row, walk key, curve, or Q, so
    this function always refuses rather than fabricate a replay result.
    """
    raise RuntimeError(
        "replay_rho_trail requires a genuine rho-trails.jsonl row, walk_key, "
        "curve/generator, and target Q from a real fixture, none of which "
        "exist in this zero-execution implementation-review task; refusing "
        "to fabricate a replay result."
    )
