# RUN-FROB-91ee9c-51bc02 -- report

Task: TASK-20260921-51bc02. Experiment: EXP-FROB-91ee9c, specification.yaml
version 1 as amended by DEC-20260921-e81e25 (version 2). This run computes,
and only computes, the already-frozen C2_non_stable_matched_dimension,
C3_random_matched_cardinality and C4_matched_null_curve controls against the
SECOND eligible object curve of FROB-SPLIT-q11n5 (A=1, B=2, N=10061) and
FROB-EQDEG-q19n5 (A=1, B=1, N=117991), plus an internal object-arm
consistency check against RUN-FROB-91ee9c-7119f2's already-recorded values
for these same two curves. FROB-NOLATTICE-q13n5's second curve and
FROB-EXT-q13n7 are explicitly out of scope (unchanged from the amendment).

No hypothesis status is asserted, changed, or implied anywhere in this
document. This is a measurement report; the strictly-smaller/not verdicts
below are exact reported facts about the tested instances only, per the
frozen success_criterion clause (6) / falsification_criterion clause (c)
definitions in specification.yaml, and are handed to
/review-evidence unadjudicated.

## 1. Object-arm consistency check (both cells)

Both curves' object arms were recomputed from scratch (field construction,
Frobenius matrix, atomic-factor kernels, curve/generator search restricted to
the already-identified (A,B,N), full tuple enumeration over the whole
prime-order subgroup) and compared against RUN-FROB-91ee9c-7119f2's recorded
curve-index-1 values.

| Cell | Recomputed I | Target I (prior run) | Recomputed m=1 ratio | Target m=1 ratio | Recomputed m=2 [2,2] ratio | Target m=2 [2,2] ratio | Match |
|---|---|---|---|---|---|---|---|
| FROB-SPLIT-q11n5 | 2055/451 | 2055/451 | 206733/41 | 206733/41 | 5533/5 | 5533/5 | EXACT |
| FROB-EQDEG-q19n5 | 6152/861 | 6152/861 | 12097908/205 | 12097908/205 | 82593/10 | 82593/10 | EXACT |

**Result: no instrument invalidation.** Both cells reproduce
RUN-FROB-91ee9c-7119f2's recorded curve-index-1 object-arm values exactly, so
this run proceeded to compute the control battery per the amendment's terms.
The independent checker (checker.py, no Sage, no import of implementation.py)
re-derived the same I and endpoint values from the raw (U_neg, p_m) pairs
independently and confirmed agreement (`work/checker-report.json`,
`consistency_checks_agree: true` on both cells).

Only two of the 15 achievable set-partitions of the atomic factors are
`ok` (non-`empty_base`) for either curve: the coarsest single-slot
partition (m=1, dim 4) and the balanced two-slot partition (m=2, dims
[2,2]). All 13 other partitions have at least one empty block for this
curve's generator (`status: empty_base`), reported and never dropped
(IR-9), matching the object-arm structure already established for these
curves in the prior run.

## 2. C2 (non-pi-stable matched-dimension) spread, per cell

C2's non-stable subspaces are constructed once per distinct slot dimension
present in the achievable partitions (here: dimension 4 and dimension 2),
found by the frozen lexicographic-first search over standard-basis subsets
of the target dimension whose span is not pi-invariant. This construction is
purely a function of (q, n, M) -- i.e. of the CELL, not of the curve -- but
membership counts (`size_B_W`) are curve-specific (computed against this
curve's own generator/subgroup).

| Cell | C2 witness dims used | C2 argmax ratio | C2 argmin ratio | C2 spread | Object spread | C2 < object? |
|---|---|---|---|---|---|---|
| FROB-SPLIT-q11n5 | {2, 4} | 1219775/242 | 20120/9 | 4365/1936 (~2.255) | 2055/451 (~4.557) | **YES, strictly smaller** |
| FROB-EQDEG-q19n5 | {2, 4} | 354085/6 | 85215/16 | 24632/2223 (~11.081) | 6152/861 (~7.145) | **NO -- C2 spread is LARGER than the object's** |

FROB-EQDEG-q19n5's C2 spread exceeding the object arm's spread is exactly
the falsification_criterion clause (c) condition ("any of the C2, C3 or C4
control arms shows a spread greater than or equal to the object arm's in the
same cell"), reported here as a measured fact for the reviewer, with no
verdict drawn on H-FROB-d93575 from this run.

## 3. C3 (random matched-cardinality) spread, per cell, both seeds

C3 replaces each object slot B_j by a uniformly seeded, negation-closed
random subset of <G>\{O} of EXACTLY the same cardinality |B_j|, drawn
without replacement per the frozen construction. U_neg is therefore
IDENTICAL to the object arm's U_neg for every matched partition by
construction (independently re-verified by checker.py:
`C3_C4_U_neg_matched_cardinality_ok: true` on both cells) -- any difference
in the ratio is entirely a difference in p_m, exactly as the control's
`isolates` clause states.

| Cell | Seed | Argmax ratio | Argmin ratio | C3 spread | Object spread | C3 < object? |
|---|---|---|---|---|---|---|
| FROB-SPLIT-q11n5 | 2026091401 | 206733/41 | 5533/5 | 2055/451 | 2055/451 | NO -- EQUAL |
| FROB-SPLIT-q11n5 | 2026091402 | 206733/41 | 5533/5 | 2055/451 | 2055/451 | NO -- EQUAL |
| FROB-EQDEG-q19n5 | 2026091401 | 12097908/205 | 82593/10 | 6152/861 | 6152/861 | NO -- EQUAL |
| FROB-EQDEG-q19n5 | 2026091402 | 12097908/205 | 82593/10 | 6152/861 | 6152/861 | NO -- EQUAL |

Both seeds, both cells: C3's spread is EXACTLY EQUAL to the object arm's
spread, not strictly smaller. This is a structural consequence measured
directly, not an artifact: for these two curves, both the m=1 and the m=2
[2,2] partitions have small enough block cardinalities relative to N that
`prod_tuple_count == distinct_targets` (no pairwise-sum collisions) on BOTH
the object arm and the random-matched arm at every ok partition, on both
seeds. Because U_neg is guaranteed identical (matched cardinality) and the
distinct-target counts came out identical as well (measured, not assumed),
the ratio of ratios that defines "spread" cancels the (N-1) denominator
exactly, producing spread_C3 = spread_object bit for bit. This is a first-
class measured observation and is reported as such; it satisfies
falsification_criterion clause (c)'s "greater than or equal to" condition
via the equality branch, on both cells and both seeds.

## 4. C4 (matched null curve) spread, per cell, both seeds

C4 uses a GEOMETRIC null curve E' (A'=z+a, B'=z+b, lexicographic scan,
rejecting singular curves and any curve with j' in the subfield F_q, first
prime N' of exponent 1 with N/2 <= N' <= 2N) matched to THIS curve's own N
(the window is per-curve, since the eligibility window in
specification.yaml's C4 design is stated in terms of the object curve under
test). The two cells' null curves are therefore each freshly searched here
(not reused from RUN-FROB-91ee9c-7119f2, whose C4 was matched to curve index
0's N, a different window):

| Cell | Null curve (a, b) | N' | Rejected before acceptance |
|---|---|---|---|
| FROB-SPLIT-q11n5 | a=0, b=3 (A'=z, B'=z+3) | 10079 | 3 candidates |
| FROB-EQDEG-q19n5 | a=0, b=1 (A'=z, B'=z+1) | 123833 | 1 candidate |

| Cell | Seed | C4 spread | Object spread | C4 < object? |
|---|---|---|---|---|
| FROB-SPLIT-q11n5 | 2026091401 | 2055/451 | 2055/451 | NO -- EQUAL |
| FROB-SPLIT-q11n5 | 2026091402 | 2055/451 | 2055/451 | NO -- EQUAL |
| FROB-EQDEG-q19n5 | 2026091401 | 6152/861 | 6152/861 | NO -- EQUAL |
| FROB-EQDEG-q19n5 | 2026091402 | 6152/861 | 6152/861 | NO -- EQUAL |

Same structural explanation as C3 (section 3): C4 also matches cardinality
exactly (guaranteeing identical U_neg), and the measured distinct-target
counts on the null curve's own subgroup came out identical to the object's
at every ok partition (again because the block sizes here are small
relative to N and N' alike, so no pairwise-sum collisions occur on either
curve). Because spread is a ratio of ratios in which the (N-1)/(N'-1)
denominators cancel, C4's spread reproduces the object arm's spread exactly,
on both cells and both seeds, DESPITE using a different curve and a
different subgroup order (N'=10079 vs N=10061 for FROB-SPLIT-q11n5). This is
reported as a measured structural fact, with the explicit claim_limit
already on record in specification.yaml (C4 changes both the curve and the
subfield structure, so it does not by itself isolate Frobenius causality).

## 5. Summary table: strictly-smaller verdicts, both (cell, curve) pairs

| Cell (curve) | Object spread | C2 < object | C3 < object (seed1) | C3 < object (seed2) | C4 < object (seed1) | C4 < object (seed2) |
|---|---|---|---|---|---|---|
| FROB-SPLIT-q11n5 (A=1,B=2,N=10061) | 2055/451 | **TRUE** | FALSE (equal) | FALSE (equal) | FALSE (equal) | FALSE (equal) |
| FROB-EQDEG-q19n5 (A=1,B=1,N=117991) | 6152/861 | **FALSE (larger)** | FALSE (equal) | FALSE (equal) | FALSE (equal) | FALSE (equal) |

On neither of these two curves do ALL THREE of C2, C3 and C4 show a
strictly-smaller spread than the object arm. This bears directly on
success_criterion clause (6) ("in every completed cell the spread ... on
each of the C2, C3 and C4 control arms is STRICTLY SMALLER than the object
arm's spread") and on falsification_criterion clause (c) (any control arm
showing spread >= the object's). No verdict on clause (6)/(c), on
H-FROB-d93575, or on EXP-FROB-91ee9c's success/falsification status is drawn
here; that adjudication belongs to /review-evidence, combining this run's
evidence with RUN-FROB-91ee9c-7119f2's.

## 6. Independent checker (C8)

`checker.py` (pure Python/stdlib, no Sage, no import of implementation.py /
core.py / lattice.py) independently:
- reconstructed the lexicographically-first monic irreducible field modulus
  for both cells and confirmed it matches the driver's `field_modulus`
  string exactly;
- recomputed #E(F_{11^5}) for the FROB-SPLIT-q11n5 curve (A=1,B=2) by
  brute-force point counting via the Euler quadratic-residue criterion
  (161051-element field, affordable in pure Python) and confirmed the
  recomputed order (160976) matches the driver's; the analogous full
  recount for FROB-EQDEG-q19n5 (2,476,099-element field) is explicitly
  disclosed as `skipped_too_large_for_pure_python_full_reenumeration_this_session`,
  not silently omitted;
- re-verified every reported `cost_ratio_neg` value at extra=0 across the
  object, C2, C3 (both seeds) and C4 (both seeds) arms, on both cells, from
  the raw (U_neg, p_m) pairs, via independent `fractions.Fraction`
  arithmetic: 12 checks per cell, 0 mismatches;
- re-verified that C3 and C4's U_neg is identical to the object arm's U_neg
  for every matched partition (the defining structural guarantee of those
  constructions): 0 mismatches on either cell;
- independently recomputed the object-arm I, spread and both endpoints, and
  confirmed agreement with the driver's `object_arm_consistency_check`
  outcome on both cells;
- independently recomputed every reported spread (object, C2, C3-by-seed,
  C4-by-seed) and the strictly-smaller verdicts; results agree with
  aggregate.py's verdicts table above exactly (`work/checker-report.json`).

C8: **PASS** on every check performed, with the one disclosed scale-driven
skip noted above (consistent with the discipline already used in
RUN-FROB-91ee9c-7119f2's checker.py).

## 7. Timing and resource use

| Cell | Wall seconds | CPU seconds | Peak RSS bytes |
|---|---|---|---|
| FROB-SPLIT-q11n5 | 4.29 | 5.60 | 249,757,696 |
| FROB-EQDEG-q19n5 | 46.67 | 47.92 | 257,003,520 |

Both well under the 8 GiB machine-protection cap; no checkpoint was
triggered. No fabricated zero time on any cell.

## 8. Scope discipline

- FROB-NOLATTICE-q13n5's second curve: explicitly excluded per
  DEC-20260921-e81e25's rationale (field-level {0,4} achievable-dimension
  fact, independent of which curve is measured). Not computed here.
- FROB-EXT-q13n7: unchanged, remains `not_run_resource` from
  RUN-FROB-91ee9c-7119f2; not touched by this run.
- RUN-FROB-91ee9c-7119f2 itself: not re-run, not re-scored, not edited.
  Every number in section 1's "Target" columns above is read directly from
  that run's committed metrics.json / cost-model.json, not recomputed by
  fabrication.

## 9. Deviations

None. No protocol deviation, infrastructure failure or unexpected
implementation issue occurred during this run. The one genuinely
unanticipated OBSERVATION -- that C3 and C4's spreads reproduce the object
arm's spread exactly rather than merely being smaller, on both cells and
both seeds, for a specific algebraic reason (Section 3/4) -- is not a
protocol deviation; it is exactly the kind of measured outcome
falsification_criterion clause (c) exists to catch, and it is preserved
here in full rather than adjusted, re-run, or omitted.
