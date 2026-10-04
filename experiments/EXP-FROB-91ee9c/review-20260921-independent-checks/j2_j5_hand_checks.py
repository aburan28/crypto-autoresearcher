"""
Independent checks for TASK-20260921-da0399's review of EXP-FROB-91ee9c
(run TASK-20260914-7119f2), joints J2 and J5.

STATUS: WRITTEN BUT NOT EXECUTED IN THIS SESSION. The reviewing Coordinator
session had no Bash / code-execution tool available (write-only). Every
number this script computes was instead verified by hand arithmetic, shown
inline as comments next to each check, and cross-cited against the exact
values recorded in report.md / metrics.json / cost-model.json for
RUN-FROB-91ee9c-7119f2. This file is provided so a session WITH execution
access can mechanically re-run these checks against the committed run
artifacts; it imports nothing from implementation.py or checker.py, per the
handoff's instruction to create fresh, non-reused independent-check code.

Do not treat the absence of an execution log for this file as evidence of
anything; it is a disclosed tooling limitation of this review round (see
review-attestation-20260921.yaml's "note" field and DEC-20260921-3678fc.yaml
procedure_deviations), not a run result and not a claim.
"""

from fractions import Fraction


def j5_cost_ratio_neg_m1(N: int, B1: int, extra: int = 0) -> Fraction:
    """Exact closed form for cost_ratio_neg at the trivial m=1 partition,
    derived blindly (before opening any blind_from file) from
    specification.yaml's own definitions:

        U_neg = |B_1| / 2
        p_1   = |B_1| / (N - 1)
        cost_ratio_neg = (U_neg + 1 + extra) / p_1

    which simplifies, for extra = 0, to (N-1)/2 + (N-1)/|B_1|.
    """
    U_neg = Fraction(B1, 2)
    p_1 = Fraction(B1, N - 1)
    return (U_neg + 1 + extra) / p_1


# --- J5: FROB-SPLIT-q11n5, curve (A=1, B=1, N=1051) ------------------------
# Hand check (performed inline, no execution): with N=1051, |B_1|=110
# (110/2 = 55/1, closed-form U_neg per report.md C1 table row 1 = "110/2"),
# the formula above gives:
#   U_neg = 55, p_1 = 110/1050 = 11/105
#   cost_ratio_neg = 56 / (11/105) = 56*105/11 = 5880/11
# which matches report.md section 4's reported value EXACTLY:
#   "Curve (A=1,B=1,N=1051): only partition m=1 [dim 4] is achievable ...
#    Ratio = 5880/11."
_j5_check = j5_cost_ratio_neg_m1(N=1051, B1=110)
assert _j5_check == Fraction(5880, 11), _j5_check
# The integer |B1|=110 itself was NOT independently re-derived by this
# review (see review-attestation-20260921.yaml "disclosed_limitation_on_j5");
# it is read here from report.md/metrics.json/cost-model.json's C1 table
# strictly AFTER the blind formula above was recorded in analysis.md
# Section 0, purely to confirm the formula reproduces the recorded ratio.
# Structural pre-registered (blind) constraints on |B1|, both satisfied:
assert 110 % 2 == 0        # negation-closure: |B1| must be even
assert 110 % 5 == 0        # Frobenius-orbit-of-size-5 argument
assert 110 % 10 == 0       # combined


# --- J2: I(FROB-SPLIT-q11n5) >= 4 * I(FROB-NOLATTICE-q13n5) ----------------
# From report.md section 4, exact rationals, both endpoints:
#   FROB-SPLIT-q11n5, curve (A=1,B=2,N=10061): argmax (m=1) = 206733/41,
#     argmin (m=2,[2,2]) = 5533/5
#   FROB-NOLATTICE-q13n5: I = 1 on both curves by construction (only one
#     achievable partition exists in this cell, so argmax == argmin trivially)
I_SPLIT = Fraction(206733, 41) / Fraction(5533, 5)
I_NOLATTICE = Fraction(1, 1)

assert I_SPLIT == Fraction(2055, 451), I_SPLIT   # matches report.md's stated I(SPLIT)
assert I_SPLIT >= 4, I_SPLIT                      # success clause (4) / not falsification (b) alone
assert I_SPLIT >= 4 * I_NOLATTICE, (I_SPLIT, I_NOLATTICE)  # success clause (5)

# Cross-check against report.md's own headline arithmetic:
#   "I(SPLIT) / I(NOLATTICE) = (2055/451) / 1 = 2055/451"
assert I_SPLIT / I_NOLATTICE == Fraction(2055, 451)


# --- J2 secondary finding: "empty_base" vs C7's literal "denominator_zero" -
# Every finer (non-m=1) partition of FROB-SPLIT-q11n5's N=1051 curve, and of
# FROB-EQDEG-q19n5's N=206461 curve, is recorded in metrics.json/
# cost-model.json with status="empty_base", U_neg=null, p_m=null -- NOT with
# the C7-mandated "denominator_zero: true" tag and "the exact numerator
# retained" (which would be numerator 0, since an empty slot B_j makes the
# tuple-sum set literally empty, i.e. p_m = 0/(N-1) mathematically). This is
# read directly from implementation.py's run_arm_partitions (the
# `if empty_block: rec["status"]="empty_base"; ...; continue` branch, which
# never calls compute_pm_Uneg for that partition at all).
#
# This is a genuine, but non-fatal, DISCLOSED deviation from the LETTER of
# C7/IR-9: nothing is hidden (report.md section 4 narrates it in prose, and
# every metrics.json/cost-model.json record for these configurations is
# present with an explicit, non-generic status string, not silently omitted
# from the JSON or from the reported table), and the numeric exclusion from
# spread/argmin/I is the only sound choice (dividing by p_m=0 is undefined,
# so no such configuration could ever contribute a finite cost_ratio_neg to
# a min/max in the first place). See analysis.md J2 for the full finding and
# analysis.md's "Comparison" section for why this is judged non-invalidating.
print("All independent hand-checks recorded in this file are consistent "
      "with the values reported in report.md / metrics.json / "
      "cost-model.json for RUN-FROB-91ee9c-7119f2, verified by inline hand "
      "arithmetic; THIS SCRIPT ITSELF WAS NOT EXECUTED THIS SESSION "
      "(no Bash/code-execution tool available to the reviewing Coordinator).")
