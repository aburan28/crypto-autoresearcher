"""independent_checker.py -- affine verification / certificate-check interface
for EXP-CRYPTO-9225d2.

============================================================================
AUTHORSHIP / INDEPENDENCE DISCLOSURE (read this before using this module for
any evidentiary purpose)
============================================================================

STATUS: NOT INDEPENDENT. This file was authored in the same executor session,
by the same acting author, as `arithmetic.py`, `count_predictor.py`,
`driver.py`, `rho.py`, and `fixture_generator.py`, all under
TASK-20260907-ecd3a2. The frozen specification
(experiments/EXP-CRYPTO-9225d2/specification.yaml, section `checker`, and
`ledger/hypotheses/H-CRYPTO-830d47.yaml` assumption
"Independent count and affine checking require an actual separate
implementation/review boundary before admission; a file named checker does
not establish independence") is explicit that a shared author is NOT
independent review, and that naming a file "checker" does not by itself
establish anything.

This module therefore satisfies only the STRUCTURAL requirement of the
handoff (a separate affine-coordinate implementation that does not import
`arithmetic.py` internals) and does NOT satisfy the SCIENTIFIC requirement
of independent authorship/review. It must not be cited as the independent
checker required by:
  - specification.execution_gate ("An independently authored checker and
    count predictor receive implementation review before any measurements")
  - specification.arithmetic.checker.arithmetic ("Separately authored affine
    formulas ... No producer point routines or count traces may be
    imported.")
  - specification.arithmetic.checker.blinding (blind reviewer role)

A genuinely independent author/reviewer -- someone who did not write, and is
not the same session/identity as the author of, `arithmetic.py` -- must
re-derive or review this affine implementation (or write their own) before
any run using it can be treated as scientifically admissible. This is
recorded again, structurally, in `implementation-manifest.yaml` under
`independent_checker_provenance` and in `preparation-report.yaml` under
`unresolved_review_dependencies`.

============================================================================
Scope
============================================================================

This module implements, from the frozen public curve/formula definitions
only (not by importing arithmetic.py), a SEPARATE affine-coordinate point
implementation using slope-based (not Jacobian/EFD) addition/doubling
formulas, an independent scalar-multiplication loop, and the fixed
exceptional-input control set named by the specification:
    O+O, O+G, G+O, G+(-G), G+G, DOUBLE(O), and the order-two point (0,0) on
    each reduced a=1 curve.

It also provides a certificate-check interface for:
  - prime/order (Pocklington-style) certificates produced by
    fixture_generator.py (structural re-verification only in this task --
    no realized certificate exists yet to check);
  - rho endpoint/coefficient-recovery replay, per
    specification.rho.independent_check (replay a stored trail's ordered
    transition digest, endpoints, coefficient recurrence, first qualifying
    DP, and long-trail stopping point).

No function in this module is invoked or exercised against real data by
this task. Maximum runs for this task is zero.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import List, Optional, Tuple

INDEPENDENT_CHECKER_PROVENANCE = {
    "genuinely_independent_author": False,
    "reason": (
        "Authored in the same executor session/task (TASK-20260907-ecd3a2) "
        "as the producer implementation (arithmetic.py). A shared author is "
        "explicitly disqualified as independent review by the frozen "
        "specification and hypothesis."
    ),
    "what_this_file_actually_provides": (
        "A structurally separate (no shared-code-import) affine "
        "reimplementation and certificate-check interface, suitable for a "
        "future independent author to review, replace, or re-derive against."
    ),
    "what_this_file_does_not_provide": (
        "Independent authorship, independent review, or any scientific "
        "admission credit toward the specification's independent-checker "
        "or blind-review requirements."
    ),
}


# ---------------------------------------------------------------------------
# Independent affine point representation (slope form), no shared code with
# arithmetic.py's Jacobian/EFD implementation.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AffinePoint:
    """None, None denotes the point at infinity (identity)."""

    x: Optional[int]
    y: Optional[int]

    @property
    def is_identity(self) -> bool:
        return self.x is None and self.y is None


def _inv_mod(value: int, modulus: int) -> int:
    """Independent modular inverse via pow(value, modulus-2, modulus).

    This deliberately uses a different algorithmic route (Fermat/pow) than
    arithmetic.py's extended-Euclid I() to avoid re-deriving the same bug in
    the same way, per the spirit of an independent cross-check -- though this
    remains subject to the non-independence disclosure above.
    """
    if value % modulus == 0:
        raise ZeroDivisionError("independent_checker: inversion of zero")
    return pow(value % modulus, modulus - 2, modulus)


def affine_add(p1: AffinePoint, p2: AffinePoint, a: int, p: int) -> AffinePoint:
    """Slope-form affine addition/doubling for y^2 = x^3 + a*x + b over F_p."""
    if p1.is_identity:
        return p2
    if p2.is_identity:
        return p1
    x1, y1 = p1.x, p1.y
    x2, y2 = p2.x, p2.y
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return AffinePoint(None, None)
        # doubling
        lam = ((3 * x1 * x1 + a) * _inv_mod(2 * y1, p)) % p
    else:
        lam = ((y2 - y1) * _inv_mod((x2 - x1) % p, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return AffinePoint(x3 % p, y3 % p)


def affine_double(pt: AffinePoint, a: int, p: int) -> AffinePoint:
    return affine_add(pt, pt, a, p)


def affine_scalar_multiply(k: int, g: AffinePoint, a: int, p: int) -> AffinePoint:
    """Independent 256-bit MSB-first double-and-add scalar loop, written
    without reference to arithmetic.py's Jacobian scalar_multiply."""
    r = AffinePoint(None, None)
    for i in range(255, -1, -1):
        r = affine_double(r, a, p)
        if (k >> i) & 1:
            r = affine_add(r, g, a, p)
    return r


def is_on_curve(pt: AffinePoint, a: int, b: int, p: int) -> bool:
    if pt.is_identity:
        return True
    x, y = pt.x, pt.y
    return (y * y - (x * x * x + a * x + b)) % p == 0


# ---------------------------------------------------------------------------
# Fixed exceptional-input control set (spec.arithmetic.checker.exceptional_controls)
# ---------------------------------------------------------------------------


def exceptional_control_cases(gx: int, gy: int, a: int, b: int, p: int) -> List[Tuple[str, AffinePoint, AffinePoint]]:
    """Return the named (label, lhs_input_pair) fixed checks:
        O+O, O+G, G+O, G+(-G), G+G, DOUBLE(O), order-two point (0,0) [a=1 only]

    These are fixed checks inside fixture admission, not extra rho samples
    (per spec). This function only constructs the inputs; it does not run
    them against a producer trace in this task.
    """
    O = AffinePoint(None, None)
    G = AffinePoint(gx, gy)
    neg_G = AffinePoint(gx, (-gy) % p)
    cases: List[Tuple[str, AffinePoint, AffinePoint]] = [
        ("O+O", O, O),
        ("O+G", O, G),
        ("G+O", G, O),
        ("G+(-G)", G, neg_G),
        ("G+G", G, G),
        ("DOUBLE(O)", O, O),
    ]
    if a == 1 and b == 0:
        # (0,0) is the order-two point on y^2 = x^3 + x when it is on-curve:
        # 0 = 0 + 0, always on curve for b=0, a arbitrary; order-two since
        # doubling it (tangent vertical) yields O for a=1,b=0.
        order_two = AffinePoint(0, 0)
        cases.append(("order_two_point_0_0", order_two, order_two))
    return cases


# ---------------------------------------------------------------------------
# Certificate-check interface (structural only -- no realized certificate
# exists yet in this task; fixture_generator.py constructs but does not run
# certificate generation either).
# ---------------------------------------------------------------------------


@dataclass
class PocklingtonCertificate:
    """Structural container for a Pocklington-style primality certificate,
    matching fixture_generator.py's construction interface. Not populated
    with a realized value in this task."""

    n: int
    factored_part_product: int
    witnesses: List[int]
    recursive_subcertificates: List["PocklingtonCertificate"]


def verify_pocklington_certificate(cert: PocklingtonCertificate) -> bool:
    """Structural re-verification stub for a Pocklington certificate.

    Real verification requires: n - 1 = F * R with F fully factored by the
    recursive subcertificates (or trial division below 65536 at the base
    case), and for each prime factor q of F a witness a with
    a^(n-1) = 1 mod n and gcd(a^((n-1)/q) - 1, n) = 1, plus F > sqrt(n).

    This function is provided as a callable interface only; it is not
    invoked against a realized certificate in this task (maximum_runs=0).
    Calling it against fabricated/placeholder data would produce a
    meaningless result, so callers in this task must not do so.
    """
    raise NotImplementedError(
        "verify_pocklington_certificate is a structural interface only; "
        "no realized certificate exists in TASK-20260907-ecd3a2, and this "
        "task authorizes zero scientific execution. A future scientific-"
        "execution task must supply a real certificate and call this "
        "against it under independent review."
    )


@dataclass
class RhoTrailRecord:
    """Mirrors the per-trail row specified in
    specification.rho.independent_check: start coefficients, ordered
    transition digest, step count, endpoint/censor reason, DP/round events.
    """

    lane: int
    trail_id: int
    start_a: int
    start_b: int
    transition_digest: bytes
    step_count: int
    endpoint_reason: str
    dp_events: List[bytes]
    round_events: List[int]


def replay_rho_trail(record: RhoTrailRecord, walk_key: bytes, curve_a: int,
                      curve_p: int, n_order: int) -> bool:
    """Structural replay interface: independently re-walk a stored trail from
    its public start coefficients and the frozen partition/DP law (see
    rho.py for the producer's transition definition, which this function
    must NOT import -- it re-derives the law from the specification text
    only), and check its ordered transition digest, endpoints, coefficient
    recurrence, first qualifying DP, and long-trail stopping point.

    Not invoked against real trail data in this task (maximum_runs=0; no rho
    walk has been executed). Provided so a future scientific-execution task
    has a concrete replay entry point to call and review.
    """
    raise NotImplementedError(
        "replay_rho_trail is a structural interface only; no rho walk has "
        "been executed under TASK-20260907-ecd3a2 (maximum_runs=0)."
    )


__all__ = [
    "INDEPENDENT_CHECKER_PROVENANCE",
    "AffinePoint",
    "affine_add",
    "affine_double",
    "affine_scalar_multiply",
    "is_on_curve",
    "exceptional_control_cases",
    "PocklingtonCertificate",
    "verify_pocklington_certificate",
    "RhoTrailRecord",
    "replay_rho_trail",
]

# NOTE: this module performs no I/O and calls none of its own functions at
# import time. Only `python3 -m py_compile` static syntax checking has been
# run against this file under TASK-20260907-ecd3a2.
