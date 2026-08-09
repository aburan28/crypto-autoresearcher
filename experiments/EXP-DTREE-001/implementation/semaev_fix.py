"""Local, corrected replacement for harness.semaev.s4_expr.

FINDING (recorded here and restated in implementation.md / the execution
report's anomalies): harness/semaev.py's s4_expr has a variable-collision bug.

    def s4_expr(a, b):
        x4 = sympy.symbols("x4")
        left = s3_expr(a, b).subs(x3, _t)
        right = s3_expr(a, b).subs({x1: x3, x2: x4, x3: _t})   # BUG
        return sympy.resultant(left, right, _t)

sympy's `Basic.subs()` applies a dict of substitutions in the dict's
iteration order UNLESS `simultaneous=True` is passed (this is documented
sympy behavior, not a sympy bug). Here the dict is
`{x1: x3, x2: x4, x3: _t}`: applying `x1 -> x3` first introduces new
occurrences of the symbol `x3`, which the *later* rule `x3 -> _t` in the
same call then also rewrites -- so what was meant to become an independent
free variable `x3` (renamed from the original `x1`) silently collapses into
`_t` instead. The result is a 3-variable expression (`x2` is also lost the
same way in some formulations), not the intended 4-variable S4(x1,x2,x3,x4).

Empirically confirmed (implementation.md "S4 bug"): for a genuine witness
P1, P2, P3 with P1+P2+P3 = S, `harness.semaev.s4_expr(a,b)` evaluated at
(x(P1), x(P2), x(P3), x(S)) is NONZERO (it should be exactly 0 -- S4 must
vanish whenever some signed combination of the four named points sums to the
identity). Adding `simultaneous=True` reproduces the textbook resultant
construction and passed 199/200 direct-witness checks (the one exclusion was
a witness summing to the identity point, which has no x-coordinate and is
correctly out of scope for a polynomial identity in x-coordinates).

This module is intentionally NOT a change to harness/semaev.py -- the
frozen specification's test_boundary.implementation note confines new glue
to experiments/EXP-DTREE-001/, and harness/ is shared code other experiments
depend on (a repair there is the Coordinator's call, not this experiment's).
grep across the tree at the time of this finding shows harness.semaev.s4_expr
is also imported by experiments/EXP-MTIC-001/code/run_mtic.py and
experiments/EXP-FIB-001/driver/decompcost.py; whether either result actually
depended on S4 vanishing correctly (as opposed to some other property of the
expression) is outside this experiment's scope to determine, and is reported
here rather than investigated further.
"""
from __future__ import annotations

import sympy

from harness.semaev import s3_expr, x1, x2, x3, _t

x4 = sympy.symbols("x4")


def s4_expr_fixed(a: int, b: int):
    """The 4th Semaev summation polynomial S4(x1,x2,x3,x4): S4=0 iff some
    sign choice of the 4 points with these x-coordinates sums to the
    identity. Same resultant construction as harness.semaev.s4_expr, with
    simultaneous=True to avoid the substitution-order bug described above.
    """
    left = s3_expr(a, b).subs(x3, _t)
    right = s3_expr(a, b).subs({x1: x3, x2: x4, x3: _t}, simultaneous=True)
    return sympy.resultant(left, right, _t)
