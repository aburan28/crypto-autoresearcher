"""Matched-ordered-base control.

Reuses split-regime (t1,t2) VALUES already computed in Stage 1 (excluding
stratum i/ii). For each such value with t1 != t2, both orderings (t1,t2)
and (t2,t1) are run through arm (a)'s core Frobenius-permutation machinery
directly on the given ordered pair (`arm_a.classify_from_t_pair`) -- i.e.
WITHOUT re-deriving t1,t2 from a symmetric (e1,e2) and without any
tau-identification step. Reports the realized cycle-type counts.

IMPLEMENTATION NOTE / DECLARED INTERPRETATION (see implementation.md): the
frozen contract names the forced outcome as "reproducing KN-FIND-a8990a
Theorem B" and, read against that finding, Theorem B concerns the regular
(Z/2)^2 action on the ROOTS of S_3(t1,t2,T) (an order-4 group acting
transitively, hence fixed-point-free on every non-identity element -- no
2.1.1 possible by construction of a *regular* action), a distinct object
from Phi(e1,e2)'s four points {P1,-P1,P2,-P2} that arm (a) builds. The
control's own paragraph, however, literally instructs classifying "the SAME
labelled four-point object" from the ordered (t1,t2) pair. This module
implements that literal instruction (arm (a)'s own four-point machinery,
fed an ordered pair rather than a symmetric derivation) and reports
whatever cycle types are actually realized, without adjusting the forced
value or suppressing a mismatch -- a mismatch is reported as an anomaly
requiring the Coordinator's attention, per `falsification_criterion` (e),
not resolved here.
"""
from __future__ import annotations

import arm_a


def cycle_type_of_class(cls: str) -> str:
    return {
        "identity": "1^4",
        "sigma_i": "2.1.1",
        "sigma1_sigma2": "2^2",
        "block_swap_involution": "2^2",
        "four_cycle": "4",
    }[cls]


def run(p, A, B, split_t_pairs, fp2, fp4):
    """`split_t_pairs` is an iterable of (t1, t2) integer pairs (t_level=0,
    split regime, t1 != t2, off strata i/ii) already produced by Stage 1's
    arm (a) pass for this (p,A,B) cell."""
    from collections import Counter
    cycle_counts = Counter()
    n_instances = 0
    for (t1, t2) in split_t_pairs:
        for (a1, a2) in ((t1, t2), (t2, t1)):
            r = arm_a.classify_from_t_pair(p, A, B, a1, a2, 0, fp2, fp4)
            if r["stratum"] != "none":
                # Should not occur (caller already filtered strata i/ii),
                # but record defensively rather than silently skip.
                cycle_counts["excluded_stratum_" + r["stratum"]] += 1
                continue
            cycle_counts[cycle_type_of_class(r["class"])] += 1
            n_instances += 1
    return {"cycle_type_counts": dict(cycle_counts), "n_instances": n_instances}
