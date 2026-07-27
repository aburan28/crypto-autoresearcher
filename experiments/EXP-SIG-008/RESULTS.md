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

## GATE 2 — UPDATE (turn 3): closure side COMPLETE (valid); rank side checkpointed
Instrument fix (method drift corrected): D5 closure anchor now uses the PINNED EXP-SIG-003
link semantics — FULL left-kernel bases (kernel_3/kernel_4), monomial multiples into the D5
row space, rank mod K5. Previous quotient-lift variant gave A4_5=242 (drift). ALL anchors
PASS (RUN-EXP-SIG-008-p): quotients 1/32/1,322; rankK5 = 2,093; A3_5 = 242; A4_5 = 444
(== RUN-EXP-SIG-003-b/f canonical; residual_5 = 1,322 - 444 = 878). Infra fixes: m4ri
matrix pickle segfaults when rows*ncols > INT_MAX (base persisted in <=10,000-row parts);
sage RealNumber breaks json.dump (fsafe applied).

sem D6 closure at n=12 seed 2 (RUN-p/q/r/s, valid): nrows = 183,312, ncols = 174,033,
n_vanish = 0, K6 family = 27,156, rankK6_sem = 26,760 (null was 26,792);
F3/F4/F5 = 2,325 / 33,110 / 85,375 images, misses 0/0/0;
A3_6 = 1,515; A4_6 = 3,559; A5 = 15,260 (cumulative union ranks mod K6).

sem D6 rank: STAIRCASE CHECKPOINTED at 36,000/174,033 columns, rank_acc = 31,715
(RUN-EXP-SIG-008-t; unit yields 16,387/18k and 15,328/18k — the sem is NOT
prefix-saturated even in the deg<=5 region, unlike the null; consistent with the genuine
D5 deficit accruing continuously). Resume:
  sage experiments/EXP-SIG-008/SIG8_run.sage --mode rank6 --arm sem --budget 225 \
       --chunk-force 18000 --out <RUN>/raw.json
(work/sem_rank6/ carries committed in this branch; mirror in /tmp/sig8_backup/work/.)
When complete: deficit_6 = 156,520 - rank6; extra_6 = 183,312 - rank6 - 26,760;
residual_6 = extra_6 - 15,260 = 141,292 - rank6.
Interpretation (per Coordinator): null baseline INVALID at this cell, so report BOTH
deficit vs sr_pred (156,520) and delta vs measured null rank 149,410. Early indication:
the sem already trails in the deg<=5 region — a sem rank BELOW 149,410 would mean the
sem's D6 defect exceeds the generic null's at n=12.

## GATE 2 — FINAL (valid, turn 4)
sem D6 rank6 = 138,570 (block-m4ri staircase completed: runs t,u,v,w,x,z,aa,ab,ac,ad
+ verdict emission ae; total staircase work 1,088 s; per-unit pivot yields:
16,387, 15,328, 15,149, 15,159, 14,726, 14,256 per 18k cols; 11,806, 11,095, 11,052,
10,272 per 15k; 3,340 of the final 6,033).
  deficit_6  = 156,520 - 138,570 = 17,950
  kernel_6   = 183,312 - 138,570 = 44,742
  extra_6    = 44,742 - 26,760     = 17,982   (rankK6_sem = 26,760)
  residual_6 = 17,982 - 15,260     = 2,722    (A5 = 15,260; A3_6 = 1,515; A4_6 = 3,559)
Sanity: kernel 44,742 >= rank(K6 u F345) 42,020 (residual >= 0) PASS;
extra - deficit = 32 == rankK6 shortfall vs nrows - sr_pred PASS.
COMPARISON (requested): sem deficit 17,950 vs measured null deficit 7,110 (null rank
149,410) — the sem's D6 defect EXCEEDS the generic null's by 10,840, as predicted from
its non-saturated prefix. The sem-minus-null rank delta: 138,570 vs 149,410.
Interpretation boundary: the null baseline is INVALID at this cell, so residual_6 = 2,722
is NOT admissible as cascade evidence; reported against BOTH baselines (sr_pred 156,520
and null rank 149,410). Rule-8 record: residual_6 = 2,722 at n=12 vs 2,615 at n=9
(EV-SIG-006) — within 4%.
Infra notes: post-reboot /tmp loss (mirror rebuilt), partial-interrupted carry removed,
state.json reconstructed from surviving carries + run logs (rank identity 91,005
verified), repeated mid-turn agent wipes of untracked driver/receipts routed around via
git restores; EXP-SIG-007 automation shared the machine (load ~9-10).
