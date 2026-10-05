# Analysis EXP-BINSTD-88a926 / H-BINSTD-2cea8d

Review task TASK-20261004-20300d. Decision DEC-20261004-99b0d1.
Evidence EV-BINSTD-66a996. Amazon Bedrock was not selected.

## Observation

Stage 0, RUN-BINSTD-e61a1c, outcome O-STAGE0-OK. Group order 130972.
Density relative error 0. Empty-pool hits 0. Twin add and twin order both
hold. The run manifest is completed_valid. The receipt is
output_validated, return code 0, check return code 0. Certificate kind
is none. `claims.exponent_move` is false. Code commit
ab3495f2ad40558aecf268458320a3a69dab4ac7, dirty false.

Stage 1, RUN-BINSTD-20e8f7, outcome O-SUPPORT. One cell: n=17, m=2,
N=96, 200 attempts, walk false. Hits are 22 normal-basis, 20
polynomial-basis, 16 uniform. Certificate failures are 0 on every arm.
The Stage-1 manifest certificate kind is decomposition and verified is
true. The receipt is output_validated, return code 0, check return code
0. `claims.exponent_move` is false. RESULTS.md and
stage1/three-arm-yield.json record the same outcome and the same hit
counts.

## Comparison

Hit-count ratios computed before opening `implementation/` are 22/20 =
1.1, 22/16 = 1.375, and 20/16 = 1.25. Each lies in the frozen band
[0.7, 1.4]. The stored `ratio_nb_over_pb` is the quotient of the
attempt-normalized rates 0.11/0.1, which prints as 1.0999999999999999,
one unit in the last place below 22/20. That stored value is also
inside [0.7, 1.4]. 22/16 and 20/16 match the archived floats exactly.

`min(1.297754385964912, 0.13690972222222222)` is
0.13690972222222222, which is at most 0.5. `decide()` returns
O-INCONCLUSIVE only when that minimum is above 0.5, so the M1 value
1.297754385964912 does not select O-INCONCLUSIVE while M2 is
0.13690972222222222.

`sum_{k=0..4} C(17,k) = 1+17+136+680+2380 = 3214`. Divided by `2^17 =
131072` this is 0.0245208740234375, equal to the archived density
0.0245208740234375 (exact fraction 1607/65536).

A Stage-1 replay from `/tmp/review-binstd-88a926`, after deleting that
copy's stage-1 JSON and RESULTS.md, returned O-SUPPORT with hits 22,
20, 16. The archived RESULTS.md and stage-1 JSON in the repository
kept their pre-replay hashes.

## Inference

O-SUPPORT is the frozen in-band label: twin checks hold, certificates
pass, the density matches, the empty pool is empty, the uniform
minimum is at most 0.5, and every pairwise ratio is inside [0.7, 1.4].
H1 is not rejected at this one cell. The official reading is support of
that scoped label, strength preliminary, claim tier toy, proof status
empirical_only. Hypothesis H-BINSTD-2cea8d moves from approved to
supported. Experiment EXP-BINSTD-88a926 moves from approved to
analyzed. The supported status records this one-cell label.

## Limitation

The observation is one n=17 cell, m=2, N=96, 200 attempts, walk false.
It is the scoped O-SUPPORT label. It carries no exponent. Stage 2 is
not authorized by DEC-20261004-99b0d1. The cell stays at n=17. The goal
head GOAL-ECDLP2M-001 is unedited. PD-1: one coordinator task owns J1,
J2, and J3; no separate validator or red-team ran. Strength preliminary
is below replicated and strong, so this decision promotes no KN-FIND.
