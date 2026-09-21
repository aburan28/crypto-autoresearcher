# Coordinator check: NAGAO-1994 takes NO cell on ANY metric

Author: orchestrating session (Coordinator), after TASK-20260823-f88f54 returned.
Status: triage input for the ledger archive. Not evidence; the reviewers have not seen it.

## Why this was run

TASK-20260823-f88f54 measured reachability against ONE metric, naive height, because that is what
H-ECQ-a609f8 pre-declared. But the ICARM board keeps a record per (rank threshold x METRIC) —
naive height, Faltings height, log conductor, discriminant. A curve that misses on one metric can
still hold a cell on another. Not checking would have left the campaign's central question half
answered, and would have left open an obvious way to later claim a cell on a metric nobody had
pre-declared.

## Result: every metric, every certified curve, NONE taken

Certified ranks are LOWER bounds from exhibited points in exact arithmetic (RUN-ECQNAG-f88f54-009).
Each row is compared against the frozen frontier cell AT ITS OWN certified rank threshold.

| curve | r>= | naive h | cell   | gap    | Faltings | cell  | gap   | log N | cell  | gap   |
|-------|-----|---------|--------|--------|----------|-------|-------|-------|-------|-------|
| t=62  | 12  | 109.505 | 69.339 | +40.17 | 6.993    | 3.811 | +3.18 | 90.35 | 57.76 | +32.58|
| t=1   | 14  | 119.534 | 85.189 | +34.35 | 7.702    | 5.131 | +2.57 | 98.09 | 73.66 | +24.43|
| t=2   | 11  | 111.217 | 61.507 | +49.71 | 7.005    | 3.041 | +3.96 | 74.61 | 51.25 | +23.36|
| t=0   |  6  | 124.400 | 30.376 | +94.02 | 8.109    | 0.583 | +7.53 | 57.30 | 22.37 | +34.93|

CELLS TAKEN: **NONE**. Not one metric, not one rank threshold. The closest approach anywhere is
t=1 on Faltings height, still +2.57 adrift.

Conductors are the producer's; log N computed here from the exact integers. Comparisons use the
FROZEN baseline frontier_20260823.json, not the values mis-transcribed into H-ECQ-a609f8 (see
CORRECTION-predeclared-target-values.md).

## What this suggests, offered as a hypothesis and NOT as a finding

Two families have now been measured against the small-curve cells and both fail by wide margins:

  MESTRE_SPEC min naive height by rank: 206.81(12) 136.69(13) 134.43(14) 118.77(15) ...
  NAGAO       min naive height in box : 109.505, flat, lower envelope does not descend

Meanwhile the r>=12/13/14 cells are held at 69.34 / 75.76 / 85.19 by curves the BATCH-f2341e red
team attributed to different programs — #244 being the only rank-14 output of the Elkies JMM23
program, which stops at 14.

The pattern that suggests: HIGH RANK AND SMALL SIZE ARE SERVED BY DIFFERENT METHOD CLASSES.
Specialising a high-rank Q(t) family buys rank cheaply and pays for it in size; the small-curve
cells appear to be held by direct search over small curves, which buys size cheaply and cannot
reach high rank. If that is right, then NO amount of work on the specialisation axis takes those
cells, and this campaign's entire A2 premise — that a high-rank base is the lever for the
size-relative board — is wrong at the root rather than wrong in its choice of family.

THIS IS NOT ESTABLISHED. It rests on two families, one of them measured in a single box, and on a
program attribution derived from free-text commentary that was itself unreplicated. It is exactly
the kind of claim the red team should attack, and it is written here so that it can be attacked
rather than absorbed. The decisive test is cheap and is named in the next-action.
