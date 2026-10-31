# EXP-PFDR-bb0d26: analysis of the second independent review round (BATCH-924d2c)

This is the analysis of review round BATCH-924d2c, composed by DEC-20261029-8d9b43 into EV-PFDR-28183c.
The plan is `coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-924d2c/review-plan.yaml`, opened by
DEC-20261029-8b2734. Experiment EXP-PFDR-bb0d26 (v1, approved by DEC-20261022-f1efde) tests H1 of
H-PFDR-727bfc. Goal GOAL-PFDR-fd09e0, question RQ-PFDR-ae2fba.

A first, independent round of the same run set, REVIEW-PFDR-bb0d26-20261029, merged to main before this
round was archived. Its composition is DEC-20261029-01405d (support; EV-PFDR-07d608, strong;
KN-FIND-c81e5b; `experiments/EXP-PFDR-bb0d26/analysis.md`). Neither round saw the other. This file does
not replace that analysis; it records the second round.

Runs: RUN-PFDR-e44a19 (selftest), RUN-PFDR-4d8c71 (census-toy-main), RUN-PFDR-243425 (analyze-main),
RUN-PFDR-cd03e2 (census-toy-rep, 0 jobs) and RUN-PFDR-089edc (analyze-final). All five are under
`experiments/EXP-PFDR-bb0d26/runs/` and were archived by TASK-20261022-207893 (commit e85a8dbe1a).

Reports of this round:

- J1, blind re-derivation:
  `coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-924d2c/reviews/TASK-20261029-2c7b52/report.yaml`
- J2a and J2b, validator VAL-20261029-2e327b:
  `coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-924d2c/reviews/TASK-20261029-e54312/report.yaml`
- J3a, J3b and the proves-too-much objects, red team RT-20261029-fa71c4:
  `coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-924d2c/reviews/TASK-20261029-11526b/report.yaml`,
  with `outputs/scope-and-wording.md` and `outputs/power-table.json`

The sections below are kept separate:

- Observation reports what was recorded and recomputed.
- Comparison sets it against the frozen thresholds, the blind re-derivation, the first round and the prior.
- Inference says what follows and what does not.
- Limitation states the scope.

## Observation

O-1. The recorded reading (RUN-PFDR-089edc `analysis.json`, stage final):

- `/outcome` is O-NULL and `/headline` is SUPPORT_SCOPED.
- 44 cells are null and 1 is invalid: b20-r3-n4096, where the main-census jobs c = 6, 30, 42 and 47 are
  degenerate, leaving 46 of 50 curves ok.
- `/fraction_valid` is 44/45, `/flagged_cells` is empty and `/powered_cells` is 44.
- `/calibration` has n 44, mean -0.26757 and sd 0.97357, and passes.
- `/largest_abs_z` is -3.1315, at b24-r1-n2048.
- RUN-PFDR-243425 reads O-NULL, and RUN-PFDR-cd03e2 ran 0 jobs.

O-2. Per-cell values (`/cells`):

- The largest |kappa - 1| is 0.0414, at b28-r1-n256 (ci95 [1.00996, 1.07428], 1440 curves).
- The smallest kappa is 0.96490, at b28-r2-n512 (ci95 [0.93684, 0.99350]).
- Every ci95 lies inside [0.90, 1.10].
- Six intervals exclude 1: b20-r1-n4096, b20-r3-n256, b24-r1-n2048, b24-r3-n2048, b28-r1-n256 and
  b28-r2-n512.
- The smallest plant_kappa is 1.2885 and the smallest plant_z is 21.93.

O-3. J1 (blind) holds:

- 6657 records pass 22 invariants with 0 violations.
- S is exact, and M and V are exact rationals.
- 44 cells are null and 1 is invalid; the gate passes; fraction_valid is 44/45; the flagged set is empty.
- The reading is O-NULL at both stages and the headline is SUPPORT_SCOPED.
- None of 1536 ambiguity combinations changes any of these.
- J1's calibration set includes the invalid cell (n 45, mean -0.27164, population sd 0.96307).

O-4. J2a and J2b hold:

- J2a replays analyze-main, analyze-final and the selftest byte-identically under CPython 3.11.17, and
  within tolerance under 3.13.17 (max relative difference 6.47e-11).
- check.py exits 0 on all five runs under both interpreters.
- 374 digest bindings and 608 integrity checks show 0 failures.
- J2b recounts 33 hash-preselected jobs by disjoint code, 27 of them with n >= 1024 and the planted arm
  included: 462 of 462 fields match.
- 31 adversarial kernel cases agree.
- PARI certifies all 1580 curve orders.
- Each of the 4 degenerate jobs carries a certified short relation u.P = O.

O-5. J3a (power-table.json):

- The flag rule (|kappa - 1| >= 0.10 AND |z| > 4) flags a true +-10% departure with probability 0.50 at
  all 44 cells.
- The z test alone reaches 0.9707 to 1.0.
- P(read null | +-10%) is at most 0.0033.
- x_c = max(|ci95 - 1|) is at most 0.0743, at most 0.0052 at n >= 2048 and at most 0.0012 at n = 4096.
- Calibration is consistent with chance (p 0.076), and so is the tail (P(max |z| >= 3.13) about 0.074).
- No pooled stratum reaches |z| > 3. Heterogeneity Q is 70.1 on 43 degrees of freedom.

O-6. J3b:

- PTM-1 is flagged at 44/44 cells and reaches O-STRUCT through the pseudo-replication.
- PTM-2 at 1.15 is flagged 16/16. PTM-2 at 1.10 is flagged 25/64, read intermediate 39/64 and read null
  0/64.
- PTM-3 is flagged 6/6 where it can be built. The counting floor kappa >= 0.912 at b20-r2-n4096 prevents
  it there.
- PTM-5 is flagged 16/16.
- PTM-4a and PTM-4c (label-describable sets) read null at 8/8 cells.
- No ok job in an r >= 2 cell has a duplicate skip.

O-7. Unexpected observations:

- (a) 4 degenerate curves in b20-r3-n4096, against 0.73 to 0.89 expected.
- (b) Sum of z^2 = 71.4 across cells, against 46.6 +- 8.4 for the null replicates, and not coherent
  across halves.
- (c) The b28-r1-n256 interval excludes 1, with an excess of 0.11 coincidences per set.
- (d) The b24-r1-n2048 deficit of about 0.1%.
- (e) The dense-cell plant gives kappa = 1 + 0.959 f.
- (f) Six of 44 intervals exclude 1.
- (g) The calibration-set ambiguity of O-3.

## Comparison

C-1. Against the frozen rules:

- The gate passes (|mean| 0.268 <= 0.35; sd 0.974 in [0.75, 1.25]).
- 44/45 cells are valid, every valid cell is null and none is flagged.
- Hence O-NULL and SUPPORT_SCOPED. The selftest passed and check.py exits 0 on all five runs.

C-2. Blind against the record:

- Coordinator reading at printed precision: S 44/44, M 44/44, z 44/44, classes 45/45.
- Top-level mechanical compare: 353 comparisons at relative 1e-9 and 45/45 classes, with 0 mismatches
  (`archives/TASK-20261029-d7284b/na1-compare.txt`).
- The ci95 intervals agree by class outcome.
- One localized difference: the calibration set and powered count (45 versus 44). It comes from the
  specification's "over powered cells". Both readings are admissible, and the gate passes under both.

C-3. Against the design's power sentence: "above 0.95" is claimed. The rule actually delivers 0.50, and
the 0.95 holds for the z test alone (RC-1).

C-4. Against the proves-too-much signature:

- There is no sensitivity defect.
- The shortfall at 1.10 is structural and general.
- PTM-4a and PTM-4c defeat the inference "kappa near 1, hence no label predicate".

C-5. Against the first round (REVIEW-PFDR-bb0d26-20261029; DEC-20261029-8d9b43 cross_round_comparison).

The rounds concur on:

- validity and reproduction;
- the scope: proper boxes, 44/45 cells, h = 2 only, the 5% tolerance;
- the flag-power correction, with O-NULL protected because a true 10% excess reads intermediate;
- the refusal of the label-describable and KN-OPEN-020 wording, with KN-OPEN-020 kept open;
- the over-dispersion and the six |z| > 2 cells.

This round adds:

- label-describable null controls built as objects, where the first round argued the point;
- the boundary objects PTM-2, PTM-3 and PTM-5, and the counting floor;
- PTM-1 routed to O-STRUCT;
- x_c and absolute per-set bounds;
- the 1536-combination ambiguity sweep;
- PARI certification of all 1580 curves, a 33-job recount and 31 kernel cases;
- RC-2;
- the degenerate-count excess;
- a second byte-exact replay under 3.11.17.

The first round adds:

- an exact replay under the recorded 3.11.15, including census-toy-rep;
- calibration-gate power;
- shared-curve correlation;
- the missing group-to-label control.

The rounds differ on two points:

- strength: strong there, preliminary here;
- this round's pre-committed mapping, which sends a general power shortfall to analyzed. The first round
  never adopted it.

C-6. Against this round's prior:

- J1, J2a and J2b matched.
- J3a was a miss of magnitude and mechanism: computable before any data, and missed at design, at
  approval and by both rounds' priors.
- J3b matched and was wider than expected.
- The prior's strength expectation ("below replicated; KN-FIND unlikely") matches this round and
  disagrees with the first round's grade.

## Inference

I-1. The run set is valid. Two independent rounds reproduce its reading blind, by exact replay and by
disjoint recount.

I-2. The narrowest supported statement:

> On generated prime-order ordinary toy curves E/F_p with p of 20, 24 and 28 bits (main seed block
> 8,100,000 + c, j != 0, 1728; RUN-PFDR-4d8c71, RUN-PFDR-089edc), for x-label sets of rank r <= 3
> log-GAPs built as specified (independent uniformly random base points, one representative per +-c,
> lexicographic half-box fill, injective boxes), of size 256 <= n <= 4096, the pooled nontrivial pair-sum
> coincidence count matches that of uniform label sets of the same size on the same curves within the
> measured per-cell 95% interval at each of the 44 assessable cells (|kappa - 1| <= x_c, x_c <= 0.0743,
> <= 0.0052 at n >= 2048, <= 0.0012 at n = 4096; b20-r3-n4096 not assessable). H1 as operationalised is
> not contradicted; the literal random-model statement is not established; nothing follows about
> label-describability, membership predicates, other statistics, shapes or labelings, larger n or p, or
> any standardized curve. One main seed block.

This statement lies inside EV-PFDR-07d608's scoped claim.

I-3. The quantity that bounds the null is x_c, not the flag power. A true 10% departure would read
intermediate, not null.

I-4. Not supported (EV-PFDR-28183c F1 to F6):

- F1: "scoped closure of label-describable ... bases".
- F2: "KN-OPEN-020 ... not opened by a label predicate".
- F3: the idea's "no low-complexity label predicate".
- F4: the hypothesis's first falsification condition.
- F5: the design's power sentence.
- F6: "independent uniform", read as established.

I-5. Status. Taken alone, this round's pre-committed mapping would record analyzed. Its premise, that a
departure could hide in the null, is refuted by both rounds. A local rule of a round unaware of the
other does not reverse a valid, reviewed support. DEC-20261029-8d9b43 therefore concurs with
supported, makes no status transition, and discloses the departure (PD-C7).

I-6. Strength. Evidence resting on one census, at toy scale, with a weak calibration gate, a mis-stated
flag power and unexplained over-dispersion is preliminary. The hierarchy ranks replicated below strong,
and EV-PFDR-f6b76c is the precedent. Reviews reproduce analyses, not runs.

DEC-20261029-8d9b43 R-2 therefore decides two corrections:

- CORR-A: EV-PFDR-07d608's strength becomes preliminary.
- CORR-B: KN-FIND-c81e5b's promotion basis is recorded as unmet, pending a full-grid replication. Its
  content is unchanged.

These are not a contradiction of evidence, so rule 12 is not engaged.

I-7. No lane is closed. KN-OPEN-020, IDEA-20261017-bbc53e and LEAD-ICP-coincidence-harvest-structured-base
stay as they were.

## Limitation

L-1. Scale. Toy scale, one main seed block and one run set; two reviews are not two runs. The
cryptographic regime, where E[C] is far below 1, is not covered. The absolute per-set sensitivity is at
best 0.09 to 0.19 coincidences per set.

L-2. Construction. Injective boxes only. Not tested: folded or structured bases, ranks above 3,
j = 0 or 1728 curves, y-labels, other box shapes, h >= 3, and the base of IDEA-20261017-bbc53e.

L-3. Dependence and conventions. Cells at the same bits share curves. The bootstrap convention comes
from run.py. The over-dispersion is unexplained.

L-4. Citations. RUN-PFDR-243425 and RUN-PFDR-089edc keep their scoped citability (DEC-20261029-5554ee;
rescope is DEC-20261029-01405d NA-6). The p^(1/2) citation is a misattributed pointer (RC-2).

L-5. Independence. One model served every session. J1's blindness rests on instruction and a tree
without history. The independence checker fails on the committed batch because of the format of J1's
sources_read (PD-C1). R-2 is a grading judgement by the composer of the sibling round, disclosed as such.
