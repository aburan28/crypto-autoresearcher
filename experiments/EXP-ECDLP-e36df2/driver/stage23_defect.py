"""Reimplementation, for Stage 0 only, of a26bde/driver/stage23.py's
digit_of_point_minus_torsion and FormalGroup construction, using ONLY the
frozen, unmodified primitives imported via frozen_ref (padic.pmul, padd,
pneg, is_identity, to_tw, valuation_modp, instrument.eval_series_mod,
instrument._exponent, formalgroup.FormalGroup). This is new code (permitted
by specification.yaml: "New code required beyond reuse"), not a copy of
stage23.py's own file (which is not in the explicitly-reusable list), but
its logic intentionally matches stage23.py's digit_of_point_minus_torsion
line for line so Stage 0's regression check reproduces exactly the
computation that produced a26bde's committed d_mS values -- using the
UNMODIFIED instrument.eval_series_mod (not fastseries's cached-evaluation
optimization), since Stage 0 is the validity gate for that optimization's
own downstream use and must not depend on it.
"""
from __future__ import annotations

from frozen_ref import (
    FormalGroup, pmul, padd, pneg, is_identity, to_tw, eval_series_mod,
    valuation_modp, _exponent, PrecisionInsufficient,
)

WORKING_DEGREE = 80


def build_formal_group(A: int, B: int) -> FormalGroup:
    return FormalGroup(A, B, D=WORKING_DEGREE)


def digit_of_point_minus_torsion(p, Kreq, pt_full, t_S_affine_big, m_mod_n,
                                  A, fg, v_known, margin=30):
    """Byte-for-byte the same computation as
    a26bde/driver/stage23.py:digit_of_point_minus_torsion."""
    Nbig = p ** (Kreq + margin)
    t_S_proj = (t_S_affine_big[0] % Nbig, t_S_affine_big[1] % Nbig, 1)
    t_mS_proj = pmul(m_mod_n, t_S_proj, A, Nbig)
    pt_proj = (pt_full[0] % Nbig, pt_full[1] % Nbig, 1)
    diff = padd(pt_proj, pneg(t_mS_proj, Nbig), A, Nbig)
    if is_identity(diff):
        raise PrecisionInsufficient("digit_of_point_minus_torsion: diff is "
                                     "identity -- degenerate or insufficient margin")
    t2, w2, N2 = to_tw(diff, Nbig, p)
    K2 = _exponent(N2, p)
    if v_known >= K2:
        raise PrecisionInsufficient("digit_of_point_minus_torsion: v_known "
                                     ">= achieved precision; raise margin")
    ell = eval_series_mod(fg.log, t2, N2, p)
    d = ((ell % (p ** K2)) // (p ** v_known)) % p
    return d
