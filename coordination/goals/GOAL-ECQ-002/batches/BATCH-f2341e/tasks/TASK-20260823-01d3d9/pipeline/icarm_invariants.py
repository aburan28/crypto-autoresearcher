#!/usr/bin/env python3
"""
ICARM leaderboard invariants of an elliptic curve over Q, from a-invariants alone.

Definitions are FIXED by the reproduction check in reproduce_icarm.py, which
recomputes them for curves already on the board and compares digit for digit:

  minimal model   PARI ellminimalmodel
  curve_key       "c4:c6" of the minimal model
  naive_height    log( max(|c4|^3, c6^2) )            of the minimal model
  faltings_height -1/2 * log(A),  A = |Im(conj(w1) w2)| the covolume of the
                  period lattice of the minimal model  (NOTE: this is the
                  board's convention; it carries no (1/12)log|Delta| term --
                  verified against curves 42, 55, 244, 276)
  conductor       PARI ellglobalred(E)[1]
  discriminant    minimal discriminant

Height values are floating point by nature (they are logarithms); the exact
integers c4, c6, Delta, N are also returned so that a reviewer can recompute
them at any precision.  Rank is NOT computed here -- see exact_certify.py.
"""
import math

import cypari

pari = cypari.pari
pari.allocatemem(2 ** 32, silent=True)
pari('default(realprecision,60)')


class InvariantTimeout(Exception):
    """Infrastructure outcome (PARI alarm), never a mathematical result."""


def minimal_model(a_invariants, time_limit=30):
    """Return (minimal a-invariants, PARI curve string) or raise InvariantTimeout."""
    ai = [int(a) for a in a_invariants]
    # cypari turns PARI's alarm() into a Python exception, so the guard is a
    # Python try/except rather than iferr().  A timeout here is an
    # INFRASTRUCTURE outcome and never a statement about the curve.
    try:
        r = pari('alarm(%d,ellminimalmodel(ellinit(%s))[1..5])' % (time_limit, ai))
    except BaseException as e:   # cypari's AlarmInterrupt is not an Exception
        raise InvariantTimeout('ellminimalmodel guard fired after %ds (%s: %s)'
                               % (time_limit, type(e).__name__, e))
    return [int(x) for x in r]


def invariants(a_invariants, time_limit=30, want_conductor=True):
    """All leaderboard invariants of the curve with the given a-invariants."""
    mai = minimal_model(a_invariants, time_limit)
    E = pari('ellinit(%s)' % (mai,))
    c4 = int(pari('%s.c4' % E))
    c6 = int(pari('%s.c6' % E))
    disc = int(pari('%s.disc' % E))
    naive = math.log(max(abs(c4) ** 3, c6 * c6))
    w1 = complex(pari('%s.omega[1]' % E))
    w2 = complex(pari('%s.omega[2]' % E))
    area = abs((w1.conjugate() * w2).imag)
    faltings = -0.5 * math.log(area)
    out = {
        'minimal_a_invariants': mai,
        'curve_key': '%d:%d' % (c4, c6),
        'c4': str(c4), 'c6': str(c6),
        'discriminant': str(disc),
        'naive_height': naive,
        'faltings_height': faltings,
        'period_lattice_covolume': area,
    }
    if want_conductor:
        try:
            n = int(pari('alarm(%d,ellglobalred(%s)[1])' % (time_limit, E)))
        except BaseException:   # AlarmInterrupt is not an Exception
            n = None
        out['conductor'] = str(n) if n is not None else None
        out['log_conductor'] = (float(pari('log(%s)' % n)) if n is not None else None)
        out['conductor_timed_out'] = n is None
    return out
