# EXP-SIG-008 — analysis (Executor record, no status verdicts)

Cell: boolean chained Semaev system, m = t = 3, n = 12 (nb = 24), seed 2 — the canonical
recorded D5 cell (EV-SIG-003). Git f6fa31b, dirty tree. All runs RUN-EXP-SIG-008-a…k.

## Gate 3 — support-induced share of the sem-D5 deficit at n = 12 — FINAL

- sem D5 anchor reproduced through the EXP-SIG-008 instrument (RUN-c): rank 28,097,
  sr_pred(12,5) 29,418, deficit 1,321, extra 1,322, rankK5 2,093, kernel 3,415,
  nrows 31,512, ncols 46,709 — every figure identical to the recorded EV-SIG-003 values.
- N1 null (column-matched, RUN-b) at D3/D4/D5 (RUN-c): rank == sr_pred at every degree
  (312/312, 3,834/3,834, 29,418/29,418), extra = 0, deficit = 0. N1 D4 pinned cross-check pass.
- **Support-induced share of the sem-D5 deficit at n = 12 = 0 / 1,321 = 0.0%.**
  The entire 1,321 deficit is genuine (not attributable to the N1 support bias).
- Contrast: at n = 9 the same construction attributed 369 of 909 = 40.6% of the sem-D5
  deficit to the null's own support bias (EV-SIG-006). That confound does NOT reproduce
  at n = 12 — it is size-dependent and vanishes.

## Gate 1 — column-matched D6 null baseline vs sr_pred(12,6) = 156,520 — CENSORED (checkpointed)

Established (valid):

- sr_pred(12,6) = 156,520 reproduced from the semiregular formula; freeze degree = 7 (RUN-a).
- Null D6 column set == sem D6 column set EXACTLY (174,033 == 174,033, set equality, RUN-b;
  rows-level equality re-confirmed, RUN-d). Null nrows6 = 183,312 (tall matrix).
- rankK6_null = 26,792 == nrows6 − sr_pred (RUN-d), so extra_6 = 0 iff rank6 == 156,520.
- n_vanish = 0; K6 family size = 27,156 (quad-quad 19,866 + quad-cubic 3,600 +
  cubic-cubic 66 + principal-quad 3,612 + principal-cubic 12).

Pending (checkpointed at 138,000 / 174,033 columns = 79.3%, rank_acc = 124,719):

Per-unit pivot yields k (columns processed in degree order, deg ≤ 5 first — the deg ≤ 5
prefix of the null is exactly rank-saturated, consistent with extra = 0 at D5):

| cols        | k      | yield  |
|-------------|--------|--------|
| 0–12,000    | 12,000 | 100.0% |
| 12–24,000   | 12,000 | 100.0% |
| 24–36,000   | 11,990 |  99.9% |
| 36–60,000   | 23,248 |  96.9% |
| 60–84,000   | 22,017 |  91.7% |
| 84–102,000  | 15,836 |  88.0% |
| 102–120,000 | 15,430 |  85.7% |
| 120–138,000 | 12,198 |  67.8% |

Cumulative column-prefix shortfall at 138,000 cols = 13,281. To land on the freeze-theory
prediction the remaining 36,033 columns must yield 31,801 pivots (88.3%) while the trend
is falling — the outcome is genuinely uncertain from the prefix and MUST NOT be
pre-judged: the verdict is exactly rank6 vs 156,520 (equivalently extra_6 vs 0), from the
completed staircase only. Resume: state `work/null_rank6/state.json` (carries
sha256-verified, resume-safe; ~2 invocations of 18,000 columns, final partial unit 12,033).

## Gate 2 — first admissible sem residual_6/deficit_6 at n = 12 — CENSORED (not started)

Not launched (budget consumed by gate 1). AGENTS rule 5: absence of gate-2 data is not
evidence. Resume path (self-staging, resume-safe):
1. `sage experiments/EXP-SIG-008/SIG8_run.sage --mode sems1 --budget 225 --out <RUN>/raw.json`
   (stage 1 computes the D5 closure anchor — asserts rankK5 = 2,093, A3_5 = 242, A4_5 = 444,
   quotient sizes 1/32/1,322; then rows6 sem, rankK6_sem, F3/F4/F5 images)
2. `sage experiments/EXP-SIG-008/SIG8_run.sage --mode sems2 --budget 225 --out <RUN>/raw.json`
   (rankK6/A3_6/A4_6/A5)
3. `sage experiments/EXP-SIG-008/SIG8_run.sage --mode rank6 --arm sem --budget 225 --out <RUN>/raw.json`
   (repeat until `done`; checkpointed like the null arm)

## Structural records (new, n = 12, seed 2)

- sem D6 column coverage: 174,033 / 190,051 possible deg ≤ 6 columns = 91.57%
  (thinning continues from the D5 series value 84.2%). deg ≤ 5 columns COMPLETE.
- sem D6 degree histogram of columns: 1 / 24 / 276 / 2,024 / 10,626 / 42,504 / 118,578.
- eq-support histograms: 12 cubics over degrees {0,1,2,3} (support sizes 13–105);
  12 quads over {0,1,2} (sizes 13–33).
- Safe column pools (di, d): (2,1): 24, (2,2): 47, (3,1): 24, (3,2): 276, (3,3): 904.

## Rule-8 unexpected observations (recorded, not explained)

1. N1 D5 extra = 0 at n = 12 vs 369 at n = 9 — the support-bias confound is
   size-dependent and vanishes at the larger size.
2. |V_N1| = 2 at n = 12 vs 0 at n = 9 (violating column pairs in the greedy null).
3. nrows6 (183,312) > ncols6 (174,033): the D6 summand-matrix is tall.
4. Null staircase per-unit pivot yield drops steeply in the sextic column region
   (67.8% in the last completed unit) — whether the total lands on, above-trend, or
   below sr_pred = 156,520 is the pending gate-1 verdict.
5. Staircase echelonize cost is non-monotone (21.5 s at 12–24k cols vs 13.3 s at
   120–138k) — pivot structure changes with column degree.

## Boundaries

- Toy scale: n = 12, seed 2, boolean m = t = 3 only. AGENTS rule 7: no crypto-scale claim.
- Gate 1 is a column-prefix checkpoint, not a result; gate 2 not started.
- RUN-e is failed_infrastructure (turn-timeout kill during a carry save) — rule 5.
- Status transitions (supported/weakened/…) are reserved to the Coordinator.
