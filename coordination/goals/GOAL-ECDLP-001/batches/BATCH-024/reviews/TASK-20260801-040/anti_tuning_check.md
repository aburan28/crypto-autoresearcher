# TASK-20260801-040 anti-tuning check

Verdict: **REVISE**, despite the durable-order and threshold-reproduction
checks passing.

## Git ordering and immutable content

I ran `git merge-base --is-ancestor` after the original BATCH-024 commits were
restored into reachable history:

- TASK-20260801-034 contract snapshot
  `36141a951a09bb340a19dc68406f98628294ad71` is an ancestor of
  TASK-20260801-036 calibration snapshot
  `e60f4fbeca7c5f9277e6559833ba716fb78d24cc` (exit 0).
- The calibration snapshot is an ancestor of TASK-20260801-039 reading-rule
  snapshot `f7513991896ed0173c6d4fbca5f42e160ce9b436` (exit 0).
- `specification.yaml` has no diff from the contract snapshot through the
  reading-rule snapshot.
- The current hashes match the receipts: specification
  `e4a977f...e20d`, driver `c83e9e9...ef3d8`, reading rule
  `360d4f1...12e32`, imported EQD driver `bdb2601...b02f`, and archived EQD
  null array `284ca32...019`.

Thus ATS-DEP-1.1's durable ordering and ATS-DEP-1.5's driver binding are
verifiable in current Git. The earlier squash-only history did not retain
those objects; this review did not treat receipt prose as a substitute and
re-ran the checks only after the commits became reachable.

## Independent threshold recomputation

I loaded each named `replicate_values` array in
`experiments/EXP-EQD-001/results/calib/null_replicate_statistics.json`, checked
length 200, sorted it independently and selected zero-based index 198. Every
value equals both EV-EQD-001's archived order statistic and RR-DEP-1's applied
threshold exactly:

| bits | statistic | recomputed 199th ascending |
|---:|---|---:|
| 16 | STAT-CHI-16 | 315.4755320010126 |
| 16 | STAT-CHI-64 | 4345.885305765976 |
| 16 | STAT-KS1-E1 | 0.006191903131115506 |
| 16 | STAT-KS1-E2 | 0.00623012475538165 |
| 20 | STAT-CHI-16 | 326.2209621328956 |
| 20 | STAT-CHI-64 | 4293.229704961268 |
| 20 | STAT-KS1-E1 | 0.006841670743639949 |
| 20 | STAT-KS1-E2 | 0.00631421232876711 |

All eight comparisons are exact floating-point equality; no fresh secondary
order statistic was substituted.

## No post-calibration inventory change

Machine comparison of the frozen specification branches with the reading-rule
copies gives exact condition and disposition equality for D-0, D-1, D-5, D-2,
D-3 and D-4, in the same order. The inventory remains:

- statistics: CHI-16, CHI-64, KS1-E1, KS1-E2;
- certifying subset: CHI-16, CHI-64, KS1-E1;
- RHO ladder: nine original rungs;
- CELL ladder: six original rungs;
- BLOCK ladder: three original rungs;
- cuts: rho_star 0.05 and eps_star 0.02;
- branches: no addition, deletion, merge or reorder.

The three calibration result files contain no `OBJ-REAL`, deterministic
factor-base list, `DEP-LADDER-RHO`, `DEP-LADDER-CELL` or
`DEP-LADDER-BLOCK` entry. The run record's tripwire is false and its rung list
is empty. ATS-DEP-1.3 passes structurally.

## Anchor pre-disclosure

ATS-DEP-1 clause 6 was honored as written. The comonotone anchor, its 20-rep
budget, its non-rung/non-decisional role, and the warning that it partially
foreshadows power were all present in the TASK-20260801-034 specification
commit before TASK-20260801-036 measured it. The reading rule does not promote
the anchor to a ladder rung or certified class.

## Why ATS-DEP-1 still does not pass

RR-DEP-1 froze `OPEN-RR-DEP-1-A` after calibration and calls two incompatible
D-5 readings admissible. The aggregate reading was not present as a frozen
statistic or threshold in the contract. Leaving the choice open after seeing
the 1-of-20 value is the latitude ATS-DEP-1.4 forbids, even though the file
honestly discloses the problem.

Source semantics select the literal per-exceedance reading independently of
the value: DEP-CAL-E consists of comparisons; each comparison has rejection
booleans; the contract says “a rejection is an implementation defect.” The
archived nonzero rejection then makes D-5 fire. A Reviewer selecting that
meaning is not authority to waive the branch or authorize measurement.

D-1 independently retains post-result latitude because “beyond sampling
noise” has no frozen mechanical definition. Repair requires a versioned
pre-measurement amendment; it cannot be supplied by commentary after the
arrays exist.

