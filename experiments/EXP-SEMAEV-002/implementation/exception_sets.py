"""Curve selection and predicted-exception-set computation for EXP-SEMAEV-002.

This module is deliberately independent of the polynomial/Newton-polytope
code path (newton_sections.py, corner_classes.py): everything here is exact
group arithmetic on E(F_p) via harness/toycurve.py's EllipticCurve class
(double-and-add, exact modular inverses). No polynomial support extraction
or coefficient formula is used anywhere in this module.

Curve-selection rule (frozen in specification.yaml):
  For a given (m, p), scan (A, B) pairs in increasing max(|A|, |B|) ("radius"),
  and within a radius in a fixed deterministic order (A ascending, then B
  ascending, both taken as residues in [0, p-1] representing the canonical
  integer representative of the field element -- i.e. |A| here means the
  representative of A mod p taken in [0, p-1], since F_p has no native
  absolute value; this is documented explicitly because "|A|,|B|" in a prime
  field requires a convention). The first (A, B) with:
    (1) 4*A^3 + 27*B^2 != 0 mod p            (nonsingular)
    (2) B is a nonzero quadratic residue mod p (so beta = sqrt(B) exists)
    (3) P0 = (0, beta) has ord(P0) >= 2*m - 1
  is selected. beta is the smaller of the two square roots of B mod p
  (canonical choice: min(r, p-r)). The search cap is max(|A|,|B|) <= p; if
  exhausted without success the cell is recorded instance_unavailable.
"""
from __future__ import annotations

from dataclasses import dataclass

from harness.toycurve import EllipticCurve, Point, _sqrt_mod


@dataclass
class CurveSelection:
    m: int
    p: int
    found: bool
    A: int | None = None
    B: int | None = None
    beta: int | None = None
    P0: Point | None = None
    order_P0: int | None = None
    search_pairs_tried: int = 0
    reason_unavailable: str | None = None


def _radius(v: int, p: int) -> int:
    """Balanced-representative "size" of v mod p: min(v, p-v). This is the
    convention this module uses for "|A|", "|B|" in a prime field, where
    there is no native absolute value; documented in the module docstring.
    """
    v %= p
    return min(v, p - v)


def select_curve(m: int, p: int) -> CurveSelection:
    """Deterministic search in increasing max(|A|,|B|), tie-broken by
    (A ascending, B ascending) among the canonical residues [0, p-1].
    """
    pairs = sorted(
        ((max(_radius(A, p), _radius(B, p)), A, B) for A in range(p) for B in range(p)),
    )
    tried = 0
    for _, A, B in pairs:
        tried += 1
        disc = (4 * A ** 3 + 27 * B ** 2) % p
        if disc == 0:
            continue
        if B == 0:
            continue
        if pow(B, (p - 1) // 2, p) != 1:
            continue
        beta = _sqrt_mod(B, p)
        if beta is None:
            continue
        beta = min(beta, (p - beta) % p)
        try:
            E = EllipticCurve(p, A, B)
        except ValueError:
            continue
        P0 = (0, beta)
        if not E.is_on_curve(P0):
            continue
        ordP0 = _point_order(E, P0)
        if ordP0 is None or ordP0 < 2 * m - 1:
            continue
        return CurveSelection(
            m=m, p=p, found=True, A=A, B=B, beta=beta, P0=P0,
            order_P0=ordP0, search_pairs_tried=tried,
        )
    return CurveSelection(
        m=m, p=p, found=False, search_pairs_tried=tried,
        reason_unavailable=f"no (A,B) with max(|A|,|B|)<=p satisfied the selection rule for m={m}, p={p}",
    )


def _point_order(E: EllipticCurve, P: Point) -> int | None:
    """Exact order of P by repeated addition (toy-scale, p small)."""
    if P is None:
        return 1
    Q = P
    k = 1
    limit = E.p + 1 + 2 * (E.p ** 0)  # generous cap; true order <= p+1+2sqrt(p) by Hasse, but we just bound by a large safe cap
    cap = 4 * E.p + 10
    while Q is not None:
        k += 1
        Q = E.add(Q, P)
        if k > cap:
            return None
    return k


def predicted_exception_set(E: EllipticCurve, P0: Point, m: int) -> list[int]:
    """Exc_m(E) = { x([r]P0) : 1 <= r <= m-1, [r]P0 affine }, via group arithmetic only."""
    xs = []
    for r in range(1, m):
        R = E.mul(r, P0)
        if R is not None:
            x = R[0]
            if x not in xs:
                xs.append(x)
    return sorted(xs)
