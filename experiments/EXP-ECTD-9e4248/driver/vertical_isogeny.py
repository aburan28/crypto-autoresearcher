"""
vertical_isogeny.py -- vertical (conductor-q, q in {17,19,23,29,31}) Velu-isogeny
construction. NEW driver code (per the handoff), but built almost entirely by
REUSING reused/isogeny.py's find_all_roots, velu_codomain, and
verify_order_preserved UNCHANGED (these are fully general in ell already -- the
ONLY reason reused/isogeny.py's own kernel_representative_sets couldn't be reused
unchanged for q>=17 is that it calls reused/divpoly.torsion_poly, which hardcodes
psi_2..psi_7 only). This module is therefore a thin, deliberately-minimal wrapper:
`kernel_representative_sets_q` is byte-for-byte the same algorithm as
reused/isogeny.kernel_representative_sets's odd-ell branch, with the single line
that computes the torsion polynomial swapped to call divpoly_ext.torsion_poly_general
(the new, validated, higher-degree division-polynomial builder) instead.
"""
from .reused import fp, semaev, isogeny
from . import divpoly_ext


def kernel_representative_sets_q(q, a, b, p, rng):
    """Same contract as reused/isogeny.kernel_representative_sets, generalized to
    any odd prime q (not just {3,5,7}) via divpoly_ext.torsion_poly_general."""
    a %= p
    b %= p
    d = (q - 1) // 2
    poly = divpoly_ext.torsion_poly_general(q, a, b, p)
    roots = isogeny.find_all_roots(poly, p, rng)
    root_set = set(roots)
    used = set()
    reps = []
    for r in roots:
        if r in used:
            continue
        try:
            mult = semaev.x_multiples(r, a, b, p, d)
        except ZeroDivisionError:
            used.add(r)
            continue
        vals = set(mult.values())
        if not vals.issubset(root_set):
            used.add(r)
            continue
        if len(vals) != d:
            used.add(r)
            continue
        used |= vals
        reps.append(frozenset(vals))
    return reps


# velu_codomain and verify_order_preserved are reused UNCHANGED -- re-exported here
# for a single, self-documenting import point in vertical.py.
velu_codomain = isogeny.velu_codomain
verify_order_preserved = isogeny.verify_order_preserved
