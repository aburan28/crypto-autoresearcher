# EXP-SIG-008 — FINAL RESULTS (preserved-in-git record)
Cell: boolean chained Semaev m=t=3, n=12 (nb=24), seed 2. Executor: Executor-SIG8, 2026-07-24.
Original run receipts a..n were destroyed mid-session by external `git clean`/branch hops
(other cursor/* agents on this shared repo), ~16:36-16:58 local. All numbers below were
recorded live in the session transcript from stdout of the valid runs; carry .pkl evidence
survived the first wipe and its sha256 was verified before the second wipe took work/.

## GATE 1 (FINAL, measured): null D6 rank = 149,410 vs sr_pred(12,6) = 156,520
deficit_6 = 7,110; kernel = 183,312-149,410 = 33,902; rankK6_null = 26,792; extra_6 = 7,110 != 0
=> column-matched D6 null baseline INVALID at n=12 seed 2; freeze theory's "valid at D6 for
n>=12" prediction FALSIFIED at this cell (status decision reserved to Coordinator).
Null: ncols 174,033 == sem exactly (set equality); nrows 183,312 (tall); n_vanish 0;
K6 family 27,156; |V_N1| = 2. Per-unit pivot yields k:
12000, 12000, 11990, 23248/24k, 22017/24k, 15836/18k, 15430/18k, 12198/18k, 14552/18k,
7219/12k, 2920/6033 (sum 149,410).

## GATE 3 (FINAL): support-induced share of sem-D5 deficit at n=12 = 0/1,321 = 0.0%
sem D5 anchor == EV-SIG-003: rank 28,097, sr_pred(12,5) 29,418, deficit 1,321, extra 1,322,
rankK5 2,093, kernel 3,415, nrows 31,512, ncols 46,709. N1 null D3/D4/D5: rank == sr_pred
(312/3,834/29,418), extra 0, deficit 0. Contrast n=9: 369/909 = 40.6% (EV-SIG-006) —
confound is size-dependent, vanishes at n=12.

## GATE 2 (CENSORED, not evidence — AGENTS rule 5)
sems1 stage 1: quotient anchors PASS (1/32/1,322), rankK5 = 2,093 PASS, A3_5 = 242 PASS,
A4_5 = 242 != recorded 444 -> HALT "method/instrument drift" (implementation issue in the
reimplemented closure path, f4_5 image contributed 0; suspect images_of_int/lift4 for D4->D5;
pinned instrument semantics to be re-derived from src/h013_f5_signatures.sage).
sem rows6/rankK6/residual_6/deficit_6 NOT computed.
Resume (after fixing A4_5): sage experiments/EXP-SIG-008/SIG8_run.sage.py --mode sems1 --out <RUN>/raw.json
then --mode sems2, then --mode rank6 --arm sem --budget 225 (repeat until done).

## Structural records (n=12 seed 2)
sr_pred(12,6) = 156,520, freeze degree 7; sem D6 ncols 174,033 (deg hist 1/24/276/2,024/
10,626/42,504/118,578; deg<=5 complete; coverage 91.57% of 190,051); sem D5 ncols 46,709.
Safe pools (di,d): (2,1) 24, (2,2) 47, (3,1) 24, (3,2) 276, (3,3) 904.
Runs: a gate+build1 (valid); b N1 construction (valid); c gate3 (valid); d null rows6+rankK6
(valid); e failed_infrastructure (turn timeout); f..n null staircase checkpoints + final
(valid); o sems1 anchor halt (valid negative control); q..t artifact-regeneration reruns
(q gate, r build2 — r's raw.json committed here; s/t destroyed mid-regeneration).
Driver: experiments/EXP-SIG-008/SIG8_run.sage(.py) (pinned src/ hashes: h013_f5_signatures.sage
1ba96fe4, semaev_tree.py e9f1681b, ic_first_fall_fast.py f1c98bd8, macaulay_export.py c00b8aad).
