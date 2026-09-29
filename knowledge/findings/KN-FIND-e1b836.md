---
id: KN-FIND-e1b836
type: internal_finding
title: "Mestre's rank-12 quartic construction is capped at Shioda-Tate 15, not 18, and its high-ceiling stratum is a density obstruction rather than a coupling"
tags: [mestre-construction, shioda-tate, shioda-tate-ceiling, density-obstruction, pre-filter, tuple-search, icarm, naive-height, rank-12, fiber-census]
confidence: derivation_recomputed_independently_by_two_reviewers_plus_exhaustive_census_reproduced_on_two_implementations
evidence_level: derivation_plus_exhaustive_census_plus_one_empirical_rate_table
source_refs: [RUN-ECQTUP-416e78-003, RUN-ECQTUP-416e78-004, RUN-ECQTUP-416e78-005, RUN-ECQTUP-416e78-006, RUN-ECQTUP-416e78-008, RUN-ECQTUP-416e78-010, RUN-ECQTUP-416e78-011, RUN-ECQTUP-416e78-012, RUN-ECQTUP-416e78-013, GOAL-ECQ-002]
internal_refs: [RQ-ECQ-80f23c, H-ECQ-8b600d, H-ECQ-0ed5c8, EV-ECQ-8ee697, DEC-20260823-ee9162]
proof_status: derivation
proof_status_reason: >-
  The fibre census and per-family ceilings are derivations re-computed
  independently by two reviewers from scratch on 8 and 6 families and
  arithmetically on all 13391, with the Euler check
  sum(deg * v_disc) = 24 = 12d passing in every case checked, and the ceiling
  identity confirmed a third time from the deliverable. The density figures
  are exhaustive counts reproduced on two implementations. The rate table
  rests on one implementation and is empirical.
proof_refs:
  - coordination/goals/GOAL-ECQ-002/batches/BATCH-541940/tasks/TASK-20260823-416e78/results/
  - coordination/goals/GOAL-ECQ-002/batches/BATCH-541940/tasks/TASK-20260823-416e78/report.md
review_refs:
  - coordination/goals/GOAL-ECQ-002/batches/BATCH-541940/tasks/TASK-20260823-e96bb6/validation_report.md
  - coordination/goals/GOAL-ECQ-002/batches/BATCH-541940/tasks/TASK-20260823-33a825/objections.yaml
  - coordination/goals/GOAL-ECQ-002/batches/BATCH-541940/archives/TASK-20260823-1f16e5/receipt.yaml
added: '2026-08-24'
superseded_by: null
---

# Capped at 15, not 18; the high-ceiling stratum is a density obstruction

## Scope (verbatim, binding)

> Scoped to Mestre's rank-12 quartic construction over admissible canonical
> integer 6-tuples of spread <= 74 exhaustively plus 312 sampled to spread
> 600, measured on one fixed 73-value T-box with |t| <= 800, under the ICARM
> naive-height convention, with rank as a LOWER bound from exhibited points
> in exact arithmetic, on PARI 2.15.4 / cypari 2.5.6 / Python 3.11.15. No
> statement is made about other constructions, other fibrations, or all
> rational t. Rank >= 31 over Q remains an open world record and nothing here
> is progress toward it.

## Statement

Over an exhaustive census of 13077 admissible canonical integer 6-tuples of
spread <= 74 (plus 314 further families), EVERY family of Mestre's
construction carries a multiplicative fibre at T = infinity of type I_4
(13352 of 13391) or I_6 (39), so the construction's Shioda-Tate cap is 15
and never the generic elliptic-K3 18; the per-family ceiling is exactly
18 - sum(m_v - 1) on 13391 of 13391 families, and what varies between tuples
is the number of REDUCIBLE FINITE fibres, not the fibre at infinity. Only 90
of 13077 (0.688 percent) reach ceiling >= 13, and exactly one of those has
log P2 below 5, two below 6 and twelve below 7. A higher ceiling does NOT
cost envelope: with coefficient content and class size matched, every
high-ceiling class sits at or below the size-matched generic minimum and the
fitted ceiling coefficient is -0.30 per unit. The usable consequence is a
FREE PRE-FILTER: a family can host rank 12 only if its discriminant is
squarefree or nearly so over the finite T-line, which is one resultant on a
degree-20 polynomial and cheaper than a single one of the 73 height
evaluations it replaces, and which cuts the exhaustive measurement set from
13077 families to 90.

## Worked instance

Tuple (0, 20, 40, 45, 52, 77) at t = 23 gives the minimal model
[0, 0, 0, -75951713419, 5158556462007754] with c4 = 3645682244112,
c6 = -4456992783174699456, proved globally minimal, naive height
86.77369390941135 and certified rank >= 12; the same family's envelope
minimum is at t = 4 with h = 69.28330998318052 at certified rank 8, i.e.
within one family the envelope minimum and the rank-12 locus are 17.49 log
units apart.

## What must not be written into this entry

That the tuple lever is closed; that a higher ceiling costs envelope; that
families of ceiling <= 11 cannot host a rank-12 specialisation; that the
required null contrasts rank 11 against rank 0; or any figure from
report.md sections 2, 3 or 5.

## Status at writing

BATCH-8b08ef (EXP-ECQ-0e0cbb) searched the low-content corner of the
high-ceiling stratum that this census measured the density of but never
searched. Its result is BRANCH C: coverage of the target stratum is 138/146
(0.9452) and of the BATCH-541940 unfinished set is 38/5549 (0.0068), so the
load-bearing negative is NOT finished at full coverage - the coverage
fraction and the population count are the result, and the zero observed
below the benchmark is, under the contract's pre-declared informativeness
test, consistent with the measured rate and not informative about it.
Nothing here says the lever is closed or the stratum is empty.
