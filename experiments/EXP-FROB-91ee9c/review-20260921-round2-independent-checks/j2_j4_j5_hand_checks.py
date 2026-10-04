"""
Independent checks for TASK-20260921-1dba2a's review (Round 2) of
EXP-FROB-91ee9c, combining RUN-FROB-91ee9c-7119f2 and the new
RUN-FROB-91ee9c-51bc02, joints J2, J4 and J5.

STATUS: WRITTEN BUT NOT EXECUTED IN THIS SESSION. The reviewing Coordinator
session had no Bash / code-execution tool available (Read/Write/Edit/Grep/
Glob only). Every number this script computes was instead verified by hand
arithmetic, shown inline in analysis.md's "Round 2, Section 0" and
cross-cited against RUN-FROB-91ee9c-51bc02's report.md and
work/checker-report.json. This file is provided so a session WITH execution
access can mechanically re-run these checks against the committed run
artifacts; it imports nothing from implementation.py, checker.py or
aggregate.py in either run directory, per the handoff's instruction to
create fresh, non-reused independent-check code for the blind_rederivation
joint specifically.

Do not treat the absence of an execution log for this file as evidence of
anything; it is a disclosed tooling limitation of this review round (see
review-20260921-round2-attestation.yaml's "note" field), not a run result
and not a claim.
"""

from fractions import Fraction


def cost_ratio_neg(U_neg_num: int, U_neg_den: int, p_m_num: int, p_m_den: int,
                    extra: int = 0) -> Fraction:
    """cost_ratio_neg = (U_neg + 1 + extra) / p_m, exactly as
    specification.yaml's metrics.primary defines it, from the raw
    (U_neg, p_m) rational pairs recorded per partition per arm in
    RUN-FROB-91ee9c-51bc02/metrics.json's `measured` object."""
    U_neg = Fraction(U_neg_num, U_neg_den)
    p_m = Fraction(p_m_num, p_m_den)
    return (U_neg + 1 + extra) / p_m


# =========================================================================
# FROB-SPLIT-q11n5, curve A=1, B=2, N=10061
# Raw (U_neg, p_m) pairs read from metrics.json's `measured.FROB-SPLIT-q11n5`
# object_arm_partitions / C2_arm_partitions / C3_arm_by_seed /
# C4_partitions_by_seed, BEFORE opening report.md, cost-model.json or
# work/checker-report.json.
# =========================================================================

split_object_m1 = cost_ratio_neg(820, 2, 820, 10060)
split_object_m2 = cost_ratio_neg(20, 2, 100, 10060)
assert split_object_m1 == Fraction(206733, 41), split_object_m1
assert split_object_m2 == Fraction(5533, 5), split_object_m2
split_object_spread = split_object_m1 / split_object_m2
assert split_object_spread == Fraction(2055, 451), split_object_spread

split_c2_m1 = cost_ratio_neg(968, 2, 968, 10060)
split_c2_m2 = cost_ratio_neg(6, 2, 18, 10060)
assert split_c2_m1 == Fraction(1219775, 242), split_c2_m1
assert split_c2_m2 == Fraction(20120, 9), split_c2_m2
split_c2_spread = split_c2_m1 / split_c2_m2
assert split_c2_spread == Fraction(4365, 1936), split_c2_spread
assert split_c2_spread < split_object_spread   # C2 strictly smaller on SPLIT

# C3, both seeds identical (matched cardinality; single-slot m=1 tie is
# forced by construction -- see the structural note below)
split_c3_m1 = cost_ratio_neg(820, 2, 820, 10060)
split_c3_m2 = cost_ratio_neg(20, 2, 100, 10060)
split_c3_spread = split_c3_m1 / split_c3_m2
assert split_c3_spread == split_object_spread == Fraction(2055, 451)
# C3 does NOT show a strictly smaller spread: exact tie, both seeds.

# C4 (N'=10079), both seeds identical
split_c4_m1 = cost_ratio_neg(820, 2, 820, 10078)
split_c4_m2 = cost_ratio_neg(20, 2, 100, 10078)
assert split_c4_m1 == Fraction(2071029, 410), split_c4_m1
assert split_c4_m2 == Fraction(55429, 50), split_c4_m2
split_c4_spread = split_c4_m1 / split_c4_m2
assert split_c4_spread == split_object_spread == Fraction(2055, 451)
# C4 does NOT show a strictly smaller spread: exact tie, both seeds --
# an algebraic NECESSITY here, since C4's distinct_targets match the
# object's exactly on both ok partitions (see structural note below), so
# the only difference (the N'-1 vs N-1 denominator) is a constant scalar
# that cancels exactly in the max/min spread ratio.

# J4: collision counts, FROB-SPLIT-q11n5
split_c2_m2_block_product = 6 * 6
split_c2_m2_distinct_targets = 18
split_object_m2_block_product = 10 * 10
split_object_m2_distinct_targets = 100
assert split_c2_m2_distinct_targets < split_c2_m2_block_product   # C2 collides (2x)
assert split_object_m2_distinct_targets == split_object_m2_block_product  # object: zero collisions
assert split_c2_m2_block_product < split_object_m2_block_product   # C2's product IS smaller here
# On SPLIT: smaller construction (C2) collides MORE than the larger
# (object/C3/C4) -- argues AGAINST a pure scale-artifact reading.


# =========================================================================
# FROB-EQDEG-q19n5, curve A=1, B=1, N=117991
# =========================================================================

eqdeg_object_m1 = cost_ratio_neg(6150, 2, 6150, 117990)
eqdeg_object_m2 = cost_ratio_neg(40, 2, 300, 117990)
assert eqdeg_object_m1 == Fraction(12097908, 205), eqdeg_object_m1
assert eqdeg_object_m2 == Fraction(82593, 10), eqdeg_object_m2
eqdeg_object_spread = eqdeg_object_m1 / eqdeg_object_m2
assert eqdeg_object_spread == Fraction(6152, 861), eqdeg_object_spread

eqdeg_c2_m1 = cost_ratio_neg(6156, 2, 6156, 117990)
eqdeg_c2_m2 = cost_ratio_neg(24, 2, 288, 117990)
assert eqdeg_c2_m1 == Fraction(354085, 6), eqdeg_c2_m1
assert eqdeg_c2_m2 == Fraction(85215, 16), eqdeg_c2_m2
eqdeg_c2_spread = eqdeg_c2_m1 / eqdeg_c2_m2
assert eqdeg_c2_spread == Fraction(24632, 2223), eqdeg_c2_spread
assert eqdeg_c2_spread > eqdeg_object_spread   # C2 is LARGER, not smaller, on EQDEG

eqdeg_c3_m1 = cost_ratio_neg(6150, 2, 6150, 117990)
eqdeg_c3_m2 = cost_ratio_neg(40, 2, 300, 117990)
eqdeg_c3_spread = eqdeg_c3_m1 / eqdeg_c3_m2
assert eqdeg_c3_spread == eqdeg_object_spread == Fraction(6152, 861)
# C3 exact tie, both seeds.

eqdeg_c4_m1 = cost_ratio_neg(6150, 2, 6150, 123832)
eqdeg_c4_m2 = cost_ratio_neg(40, 2, 300, 123832)
eqdeg_c4_spread = eqdeg_c4_m1 / eqdeg_c4_m2
assert eqdeg_c4_spread == eqdeg_object_spread == Fraction(6152, 861)
# C4 exact tie, both seeds -- again an algebraic necessity given matching
# distinct_targets on both ok partitions.

# J4: collision counts, FROB-EQDEG-q19n5
eqdeg_c2_m2_block_product = 24 * 24
eqdeg_c2_m2_distinct_targets = 288
eqdeg_object_m2_block_product = 10 * 30
eqdeg_object_m2_distinct_targets = 300
assert eqdeg_c2_m2_distinct_targets < eqdeg_c2_m2_block_product   # C2 collides (2x)
assert eqdeg_object_m2_distinct_targets == eqdeg_object_m2_block_product  # object: zero collisions
assert eqdeg_c2_m2_block_product > eqdeg_object_m2_block_product   # C2's product is LARGER here -- the REVERSE of SPLIT
# On EQDEG: the LARGER construction (C2) collides while the SMALLER
# (object/C3/C4) does not -- this IS the review plan's own named PTM-2(ii)
# firing condition ("the collision-count pattern reversing so that smaller
# constructions collide LESS, consistent with a pure scale-artifact
# story"). This CONTRADICTS the handoff's own coordinator_prior, which
# asserted the SPLIT-cell pattern ("smaller product, more collisions")
# held "on BOTH cells" -- it does not.


# =========================================================================
# J3 verdict table (success_criterion clause (6) / falsification clause (c))
# =========================================================================

verdicts = {
    ("FROB-SPLIT-q11n5", "C2"): split_c2_spread < split_object_spread,
    ("FROB-SPLIT-q11n5", "C3"): split_c3_spread < split_object_spread,
    ("FROB-SPLIT-q11n5", "C4"): split_c4_spread < split_object_spread,
    ("FROB-EQDEG-q19n5", "C2"): eqdeg_c2_spread < eqdeg_object_spread,
    ("FROB-EQDEG-q19n5", "C3"): eqdeg_c3_spread < eqdeg_object_spread,
    ("FROB-EQDEG-q19n5", "C4"): eqdeg_c4_spread < eqdeg_object_spread,
}
assert verdicts[("FROB-SPLIT-q11n5", "C2")] is True
assert verdicts[("FROB-SPLIT-q11n5", "C3")] is False
assert verdicts[("FROB-SPLIT-q11n5", "C4")] is False
assert verdicts[("FROB-EQDEG-q19n5", "C2")] is False
assert verdicts[("FROB-EQDEG-q19n5", "C3")] is False
assert verdicts[("FROB-EQDEG-q19n5", "C4")] is False
# success_criterion clause (6) (ALL of C2/C3/C4 strictly smaller, EVERY
# completed cell) is NOT MET in either cell.
assert not all(verdicts.values())


# =========================================================================
# Structural note (independent of J4/PTM-2): the m=1 endpoint is forced
# =========================================================================
# For C3 (matched cardinality), at m=1 there is exactly one slot, so
# p_1 = |B_1| / (N - 1) is a pure function of cardinality and N alone --
# there is no "combining multiple blocks" step in which a collision could
# occur. Since C3's m=1 slot is constructed at EXACTLY the object's
# cardinality, C3's m=1 ratio is IDENTICAL to the object's m=1 ratio by
# construction, in every cell, regardless of any structural difference:
assert split_c3_m1 == split_object_m1
assert eqdeg_c3_m1 == eqdeg_object_m1
# For C4, the m=1 ratio differs from the object's only by the constant
# factor (N'-1)/(N-1) (same numerator cardinality, different denominator):
assert split_c4_m1 / split_object_m1 == Fraction(10078, 10060)
assert eqdeg_c4_m1 / eqdeg_object_m1 == Fraction(123832, 117990)
# This constant cancels exactly in the spread ratio, so C3's and C4's
# capacity to show a strictly smaller spread reduces entirely to whether
# the ONE finest (argmin) partition collides more on the object than on
# the control -- a single collide/don't-collide comparison, not a richer
# statistic.


print("All independent hand-checks in this file are consistent with the "
      "values reported in RUN-FROB-91ee9c-51bc02's report.md and "
      "work/checker-report.json, and with metrics.json's own raw `measured` "
      "(U_neg, p_m) pairs; THIS SCRIPT ITSELF WAS NOT EXECUTED THIS SESSION "
      "(no Bash/code-execution tool available to the reviewing Coordinator).")
