#!/usr/bin/env python3
"""
The ICARM naive-height convention, computed from a-invariants ALONE in exact
integer arithmetic, plus global-minimality settlement.

h = log max(|c4|^3, c6^2).  c4 and c6 are exact integers; only the final
logarithm is floating point, and it is taken as 3*log|c4| or 2*log|c6| so that
no intermediate ever overflows.  No height reported anywhere in this task is
computed any other way.
"""
import math

import cypari

pari = cypari.pari


def c_invariants(ai):
    a1, a2, a3, a4, a6 = [int(x) for x in ai]
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    c4 = b2 * b2 - 24 * b4
    c6 = -b2 ** 3 + 36 * b2 * b4 - 216 * b6
    disc = -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6
    return c4, c6, disc


def naive_height_from_ainvs(ai):
    """log max(|c4|^3, |c6|^2) from a-invariants alone, exact c4/c6."""
    c4, c6, disc = c_invariants(ai)
    l4 = 3 * math.log(abs(c4)) if c4 else float('-inf')
    l6 = 2 * math.log(abs(c6)) if c6 else float('-inf')
    return max(l4, l6), c4, c6, disc


def curve_key(ai):
    c4, c6, _ = c_invariants(ai)
    return '%d:%d' % (c4, c6)


def is_globally_minimal(ai):
    """True iff PARI's minimal model has the same c4 and c6."""
    m = pari('ellminimalmodel(ellinit(%s))[1..5]' % ([int(x) for x in ai],))
    mai = [int(x) for x in m]
    return curve_key(mai) == curve_key(ai), mai
