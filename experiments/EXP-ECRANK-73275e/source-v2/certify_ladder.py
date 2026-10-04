"""Certifier-ladder wrapper for EXP-ECRANK-73275e v2 (IV-1C / R11).

The committed F_l-reduction within-class certifier
(coordination/goals/GOAL-ECQ-002/.../exact_certify.py, byte-identical,
sha256-pinned by ecrank_engine.load_exact_certify) exposes
`certify(a_invariants, points, max_prime=1500, ...)`. The v1
certify76.certify_instance calls it with the DEFAULT max_prime=1500 and
does not expose the bound.

The amendment's IV-1C requires the SAME certification pipeline at a FIXED
three-rung prime-bound ladder (1500 / 10000 / 100000), all rungs reported
for every tuple with op costs. This module reuses v1 certify76.certify_instance
BY IMPORT (the v1 file is not edited) and threads the bound through by
temporarily wrapping the committed module's `certify` entry point with the
requested max_prime. The wrap is restored in a finally block, so the
committed module is left unmodified after each call.

Nothing else about the certificate changes: the same exact on-curve checks,
Mazur witnesses, Kummer tests, sigma-checks, torsion screens, and the same
conservative aggregate. Only the prime search bound of the committed
certifier moves, rung by rung.
"""

import certify76 as C  # v1 module, imported read-only


def certify_instance_ladder(inst, coset, ec, max_prime=1500,
                            mazur_max=12, screen_max=24):
    """certify76.certify_instance with the committed certifier's prime bound
    set to max_prime. Returns the same certificate dict."""
    orig = ec.certify

    def wrapped(ainv, pts, **kw):
        kw.setdefault("max_prime", max_prime)
        return orig(ainv, pts, **kw)

    ec.certify = wrapped
    try:
        return C.certify_instance(inst, coset, ec,
                                  mazur_max=mazur_max, screen_max=screen_max)
    finally:
        ec.certify = orig
