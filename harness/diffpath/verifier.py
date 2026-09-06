"""The PATH CONFORMANCE VERIFIER.

Given a path object and a message pair, decide step-by-step conformance and
evaluate the sufficient-condition set, SEPARATELY: conformance is "the pair
really induces these per-step differences", conditions are "the pair really
pins the bits the path says it needs".  Merging the two would hide which of the
path and the condition set is at fault when a pair fails.

The conformance predicate DOES NOT READ THE BLOCK INDEX.  That is generator
E6's first clause, and `conforms()` takes no block-index parameter at all, so
the property is structural rather than promised.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import primitives as P
from .pathobj import PathObject


@dataclass
class Conformance:
    conforming: bool
    steps_total: int
    steps_matching: int
    first_mismatch_step: int | None
    conditions_total: int
    conditions_satisfied: bool
    conditions_failed: int


def conforms(obj: PathObject, cv, m, mp) -> Conformance:
    """Step-by-step conformance of (m, mp) at chaining value cv to `obj`."""
    if obj.path_data is None:
        raise ValueError(
            f"{obj.id}: pointer entry (status={obj.status}) has no path data "
            f"and is never verified or canonicalised")
    comp = P.COMPRESS[obj.primitive]
    tr = comp(tuple(cv), list(m))
    trp = comp(tuple(cv), list(mp))
    a, b = obj.step_range

    matching = 0
    first_bad = None
    for k, i in enumerate(range(a, b + 1)):
        if P.sub32(trp.q[i], tr.q[i]) == obj.step_delta[k]:
            matching += 1
        elif first_bad is None:
            first_bad = i

    failed = 0
    for c in obj.conditions:
        src = tr.t if c.operand == "t" else tr.q
        if c.operand == "q":
            val = (tr.q[c.step - 1] if c.step >= 1 else cv[1])
        else:
            val = src[c.step]
        if ((val >> c.bit) & 1) != c.value:
            failed += 1

    n = b - a + 1
    return Conformance(
        conforming=(matching == n),
        steps_total=n, steps_matching=matching, first_mismatch_step=first_bad,
        conditions_total=len(obj.conditions),
        conditions_satisfied=(failed == 0), conditions_failed=failed,
    )


def degenerate_baseline(rng, primitive: str, steps: int) -> Conformance:
    """CTL-BASE's degenerate baseline.

    A seeded random pair, and the actual per-step differential THAT PAIR
    induces.  The verifier must report 100% conformance.  Every verifier must
    pass this before an interesting input is shown to it; a verifier that fails
    here is broken and no later number it produces means anything.
    """
    from .pathobj import plant_from_pair, seeded_pair
    cv, m, mp = seeded_pair(rng, primitive)
    obj = plant_from_pair("CTL-BASE-degenerate", primitive, cv, m, mp, (0, steps - 1))
    return conforms(obj, cv, m, mp)
