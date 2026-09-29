# EXP-PFDR-5726af — analysis (Stage 4, zero compute)

Task TASK-20260903-b0727c (Executor). Every table below is generated from the
run packages under `runs/` (`raw-result.json`, `manifest.yaml`) by a read-only
summariser; residuals are `observed - frozen` with the frozen values read from
`stage0-predictions.yaml`
(sha256 `e5198d84094fa299933e0f8bbe6c7bcc41e37cce42a9d58854ce5df6cf339e94`).
**Observations only.** The "verdict" in section K restates each frozen
criterion with the observed value; it is not a judgment on H-PFDR-4148b8, which
belongs to the Reviewer and the Coordinator. Scope: d = 2, m in {2, 3},
s in {2..6} (m = 2) and {4, 5} (m = 3), p in {4099, 65537}, the shared F_p
meter, per-layer convention, D_max = D_null + 1; nothing transfers to
cryptographic s.

Conventions: D_null = floor((ms + me)/2) + 1 (this contract); the 84cdb7
convention ceil((ms + 2m)/2) is shown beside it and never used for scoring.
"fall_dim" is rank(M_D) - rank(H_D) of the per-layer rows mu * S~ in B.

## A. Run tally

| run id | status | wall_seconds (wrapper) | peak RSS (MB) | certificate | valid |
|---|---|---|---|---|---|
| RUN-PFDR-5726af-htop | completed_valid | 3.729 | 73 | none / verified=True | True |
| RUN-PFDR-5726af-hwil | completed_valid | 0.467 | 58 | none / verified=True | True |
| RUN-PFDR-5726af-m2-s2-gate | completed_valid | 0.304 | 58 | decomposition / verified=True | True |
| RUN-PFDR-5726af-m2-s3 | completed_valid | 0.594 | 58 | decomposition / verified=True | True |
| RUN-PFDR-5726af-m2-s4 | completed_valid | 4.933 | 59 | decomposition / verified=True | True |
| RUN-PFDR-5726af-m2-s5 | completed_valid | 111.457 | 77 | decomposition / verified=True | True |
| RUN-PFDR-5726af-m2-s6 | completed_valid | 1267.883 | 126 | decomposition / verified=True | True |
| RUN-PFDR-5726af-m3-s4 | completed_valid | 2.778 | 71 | decomposition / verified=True | True |
| RUN-PFDR-5726af-m3-s5 | completed_valid | 128.228 | 407 | decomposition / verified=True | True |
| RUN-PFDR-5726af-nearby-s3 | completed_valid | 0.425 | 58 | none / verified=True | True |

## B. Semaev arm per cell against the frozen prediction (residual = observed - frozen)

| cell | run | frozen (d_ff, fall_dim) | observed d_ff values (12 draws; 2 at m=3) | observed fall_dim values | residuals d_ff / fall_dim | NULL-3 identical | D_null | gap | oracle | certs | top form = c prod ell^e | stop-at-first-fall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (2,2,2) | RUN-PFDR-5726af-m2-s2-gate | (5, 4) | [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5] | [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4] | [0] / [0] | True | 5 (84cdb7: 4) | 0 | True | True | True | False |
| (2,2,3) | RUN-PFDR-5726af-m2-s3 | (5, 4) | [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5] | [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4] | [0] / [0] | True | 6 (84cdb7: 5) | 1 | True | True | True | False |
| (2,2,4) | RUN-PFDR-5726af-m2-s4 | (6, 10) | [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6] | [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10] | [0] / [0] | True | 7 (84cdb7: 6) | 1 | None | True | True | False |
| (2,2,5) | RUN-PFDR-5726af-m2-s5 | (6, 10) | [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6] | [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10] | [0] / [0] | True | 8 (84cdb7: 7) | 2 | None | True | True | False |
| (2,2,6) | RUN-PFDR-5726af-m2-s6 | (7, 28) | [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7] | [28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28] | [0] / [0] | True | 9 (84cdb7: 8) | 2 | None | True | True | True |
| (3,2,4) | RUN-PFDR-5726af-m3-s4 | (13, 12) | [13, 13] | [12, 12] | [0] / [0] | True | 13 (84cdb7: 9) | 0 | None | True | True | True |
| (3,2,5) | RUN-PFDR-5726af-m3-s5 | (13, 12) | [13, 13] | [12, 12] | [0] / [0] | True | 14 (84cdb7: 11) | 1 | None | True | True | True |

## C. NULL-2 (block-factored) per cell: (d_ff, fall_dim) per (p, seed) and NULL-2 minus Semaev

| cell | NULL-2 (p, seed) -> (d_ff, fall_dim) | P3 all zero | nonzero entries (count) | example nonzero |
|---|---|---|---|---|
| (2,2,2) | (4099,7)->(5,1); (4099,11)->(5,1); (4099,13)->(5,1); (4099,17)->(5,1); (4099,19)->(5,1); (65537,7)->(5,1); (65537,11)->(5,1); (65537,13)->(5,1); (65537,17)->(5,1); (65537,19)->(5,1) | False | 60 | {'curve_seed': 1101, 'd_ff_diff': 0, 'fall_dim_diff': -3, 'p': 4099, 'seed': 7, 'target_seed': 1} |
| (2,2,3) | (4099,7)->(5,4); (4099,11)->(5,4); (4099,13)->(5,4); (4099,17)->(5,4); (4099,19)->(5,4); (65537,7)->(5,4); (65537,11)->(5,4); (65537,13)->(5,4); (65537,17)->(5,4); (65537,19)->(5,4) | True | 0 |  |
| (2,2,4) | (4099,7)->(6,10); (4099,11)->(6,10); (4099,13)->(6,10); (4099,17)->(6,10); (4099,19)->(6,10); (65537,7)->(6,10); (65537,11)->(6,10); (65537,13)->(6,10); (65537,17)->(6,10); (65537,19)->(6,10) | True | 0 |  |
| (2,2,5) | (4099,7)->(6,10); (4099,11)->(6,10); (4099,13)->(6,10); (4099,17)->(6,10); (4099,19)->(6,10); (65537,7)->(6,10); (65537,11)->(6,10); (65537,13)->(6,10); (65537,17)->(6,10); (65537,19)->(6,10) | True | 0 |  |
| (2,2,6) | (4099,7)->(7,28); (4099,11)->(7,28); (4099,13)->(7,28); (4099,17)->(7,28); (4099,19)->(7,28); (65537,7)->(7,28); (65537,11)->(7,28); (65537,13)->(7,28); (65537,17)->(7,28); (65537,19)->(7,28) | True | 0 |  |
| (3,2,4) | (65537,7)->(13,1); (65537,11)->(13,1); (65537,13)->(13,1); (65537,17)->(13,1); (65537,19)->(13,1) | False | 10 | {'curve_seed': 1101, 'd_ff_diff': 0, 'fall_dim_diff': -11, 'p': 65537, 'seed': 7, 'target_seed': 1} |
| (3,2,5) | (65537,7)->(13,12); (65537,11)->(13,12); (65537,13)->(13,12); (65537,17)->(13,12); (65537,19)->(13,12) | True | 0 |  |

## D. NULL-1 (support-matched) per cell

| cell | frozen D_null | d_ff histogram | computed / planned | at D_null | below D_null | no fall by D_max (censored) | wall-guard censored | criterion 3 (majority at D_null, none below) | F4 (any at Semaev value) |
|---|---|---|---|---|---|---|---|---|---|
| (2,2,2) | 5 | {'5': 60} | 60 / 60 | 60 | 0 | 0 | 0 | True | True |
| (2,2,3) | 6 | {'6': 60} | 60 / 60 | 60 | 0 | 0 | 0 | True | False |
| (2,2,4) | 7 | {'7': 60} | 60 / 60 | 60 | 0 | 0 | 0 | True | False |
| (2,2,5) | 8 | {'8': 60} | 60 / 60 | 60 | 0 | 0 | 0 | True | False |
| (2,2,6) | 9 | {'9': 60} | 60 / 60 | 60 | 0 | 0 | 0 | True | False |
| (3,2,4) | 13 | {'13': 10} | 10 / 10 | 10 | 0 | 0 | 0 | True | True |
| (3,2,5) | 14 | {'14': 10} | 10 / 10 | 10 | 0 | 0 | 0 | True | False |

## E. NULL-1 fall_dim at d_ff per cell (distinct values)

- (2,2,2): [(5, 4)]
- (2,2,3): [(6, 14)]
- (2,2,4): [(7, 48)]
- (2,2,5): [(8, 165)]
- (2,2,6): [(9, 572)]
- (3,2,4): [(13, 12)]
- (3,2,5): [(14, 90)]

## F. Full rank profiles of the frozen-fixture draw (p = 4099, curve seed 1101, target seed 1) per cell (D: rows, ncols_full, ncols_top, full_rank, top_rank, fall_dim)

- (2,2,2) (p=4099, curve 1101: a=527, b=72, target 1: x_R=2374; generator terms 16): [(4, 1, 16, 1, 1, 1, 0), (5, 4, 16, 0, 4, 0, 4), (6, 6, 16, 0, 6, 0, 6)]
- (2,2,3) (p=4099, curve 1101: a=527, b=72, target 1: x_R=2374; generator terms 49): [(4, 1, 57, 15, 1, 1, 0), (5, 6, 63, 6, 6, 2, 4), (6, 15, 64, 1, 15, 1, 14), (7, 20, 64, 0, 20, 0, 20)]
- (2,2,4) (p=4099, curve 1101: a=527, b=72, target 1: x_R=2374; generator terms 121): [(4, 1, 163, 70, 1, 1, 0), (5, 8, 219, 56, 8, 8, 0), (6, 28, 247, 28, 28, 18, 10), (7, 56, 255, 8, 56, 8, 48), (8, 70, 256, 1, 70, 1, 69)]
- (2,2,5) (p=4099, curve 1101: a=527, b=72, target 1: x_R=2374; generator terms 256): [(4, 1, 386, 210, 1, 1, 0), (5, 10, 638, 252, 10, 10, 0), (6, 45, 848, 210, 45, 35, 10), (7, 120, 968, 120, 120, 52, 68), (8, 210, 1013, 45, 210, 35, 175), (9, 252, 1023, 10, 252, 10, 242)]
- (2,2,6) (p=4099, curve 1101: a=527, b=72, target 1: x_R=2374; generator terms 484): [(4, 1, 794, 495, 1, 1, 0), (5, 12, 1586, 792, 12, 12, 0), (6, 66, 2510, 924, 66, 66, 0), (7, 220, 3302, 792, 220, 192, 28)]
- (3,2,4) (p=65537, curve 1101: a=5623, b=46432, target 1: x_R=15; generator terms 4096): [(12, 1, 4096, 1, 1, 1, 0), (13, 12, 4096, 0, 12, 0, 12)]
- (3,2,5) (p=65537, curve 1101: a=5623, b=46432, target 1: x_R=15; generator terms 29791): [(12, 1, 32647, 455, 1, 1, 0), (13, 15, 32752, 105, 15, 3, 12)]

## G. sol(D) covariate (Semaev arm; IDEA-20260806-7ea402; recorded, not claimed)

- (2,2,2): N_sol per draw [2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2]; d_solve per draw (None = not reached by D_max) [None, None, None, None, None, None, None, None, None, None, None, None]
- (2,2,3): N_sol per draw [2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2]; d_solve per draw (None = not reached by D_max) [None, None, None, None, None, None, None, None, None, None, None, None]
- (2,2,4): N_sol per draw [2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2]; d_solve per draw (None = not reached by D_max) [None, None, None, None, None, None, None, None, None, None, None, None]
- (2,2,5): N_sol per draw [2, 6, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2]; d_solve per draw (None = not reached by D_max) [None, None, None, None, None, None, None, None, None, None, None, None]
- (2,2,6): N_sol per draw not computed; d_solve per draw (None = not reached by D_max) not computed
- (3,2,4): N_sol per draw not computed; d_solve per draw (None = not reached by D_max) not computed
- (3,2,5): N_sol per draw not computed; d_solve per draw (None = not reached by D_max) not computed

## H. Nearby objects at (2, 2, 3)

- MIXED-BLOCK (36 = 12 draws x 3 seeds): d_ff histogram {'6': 36}; fall_dim values (distinct) [14]; frozen: d_ff 6 (>= 1 above 5); all >= 6: True; F5 (any = 5): False
- NON-MONOMIAL-TOP reading A (S_3 + ell_1^4): d_ff values [5]; reading B (homogeneous top only): [5]; note: x_1^4 = ell_1^4 has zero degree-4 part in 3 squarefree digit variables (a_i^2 = 0 kills every degree-4 monomial of one block), so the top form collapses to x_1^2 x_2^2
- MIXED-BLOCK distinct rank profiles (D, rows, full, top, fall): [((4, 1, 1, 1, 0), (5, 6, 6, 6, 0), (6, 15, 15, 1, 14), (7, 20, 20, 0, 20))]

## I. H-WIL direct rank table

- cells: 112 (s in 2..8, all j with j+2 <= s, p in {4099, 65537}, ell in {digit, unit}); all full rank: True; meter top_rank == independent sympy rank everywhere: True; below maximum: []
- tail check (square maps j + 2 = s - j): all full rank: True

| p | s | j | ell | rank (meter) | rank (independent) | expected min(C(s,j), C(s,j+2)) | square map |
|---|---|---|---|---|---|---|---|
| 4099 | 2 | 0 | digit | 1 | 1 | 1 | yes |
| 4099 | 3 | 0 | digit | 1 | 1 | 1 |  |
| 4099 | 3 | 1 | digit | 1 | 1 | 1 |  |
| 4099 | 4 | 0 | digit | 1 | 1 | 1 |  |
| 4099 | 4 | 1 | digit | 4 | 4 | 4 | yes |
| 4099 | 4 | 2 | digit | 1 | 1 | 1 |  |
| 4099 | 5 | 0 | digit | 1 | 1 | 1 |  |
| 4099 | 5 | 1 | digit | 5 | 5 | 5 |  |
| 4099 | 5 | 2 | digit | 5 | 5 | 5 |  |
| 4099 | 5 | 3 | digit | 1 | 1 | 1 |  |
| 4099 | 6 | 0 | digit | 1 | 1 | 1 |  |
| 4099 | 6 | 1 | digit | 6 | 6 | 6 |  |
| 4099 | 6 | 2 | digit | 15 | 15 | 15 | yes |
| 4099 | 6 | 3 | digit | 6 | 6 | 6 |  |
| 4099 | 6 | 4 | digit | 1 | 1 | 1 |  |
| 4099 | 7 | 0 | digit | 1 | 1 | 1 |  |
| 4099 | 7 | 1 | digit | 7 | 7 | 7 |  |
| 4099 | 7 | 2 | digit | 21 | 21 | 21 |  |
| 4099 | 7 | 3 | digit | 21 | 21 | 21 |  |
| 4099 | 7 | 4 | digit | 7 | 7 | 7 |  |
| 4099 | 7 | 5 | digit | 1 | 1 | 1 |  |
| 4099 | 8 | 0 | digit | 1 | 1 | 1 |  |
| 4099 | 8 | 1 | digit | 8 | 8 | 8 |  |
| 4099 | 8 | 2 | digit | 28 | 28 | 28 |  |
| 4099 | 8 | 3 | digit | 56 | 56 | 56 | yes |
| 4099 | 8 | 4 | digit | 28 | 28 | 28 |  |
| 4099 | 8 | 5 | digit | 8 | 8 | 8 |  |
| 4099 | 8 | 6 | digit | 1 | 1 | 1 |  |
| 65537 | 2 | 0 | digit | 1 | 1 | 1 | yes |
| 65537 | 3 | 0 | digit | 1 | 1 | 1 |  |
| 65537 | 3 | 1 | digit | 1 | 1 | 1 |  |
| 65537 | 4 | 0 | digit | 1 | 1 | 1 |  |
| 65537 | 4 | 1 | digit | 4 | 4 | 4 | yes |
| 65537 | 4 | 2 | digit | 1 | 1 | 1 |  |
| 65537 | 5 | 0 | digit | 1 | 1 | 1 |  |
| 65537 | 5 | 1 | digit | 5 | 5 | 5 |  |
| 65537 | 5 | 2 | digit | 5 | 5 | 5 |  |
| 65537 | 5 | 3 | digit | 1 | 1 | 1 |  |
| 65537 | 6 | 0 | digit | 1 | 1 | 1 |  |
| 65537 | 6 | 1 | digit | 6 | 6 | 6 |  |
| 65537 | 6 | 2 | digit | 15 | 15 | 15 | yes |
| 65537 | 6 | 3 | digit | 6 | 6 | 6 |  |
| 65537 | 6 | 4 | digit | 1 | 1 | 1 |  |
| 65537 | 7 | 0 | digit | 1 | 1 | 1 |  |
| 65537 | 7 | 1 | digit | 7 | 7 | 7 |  |
| 65537 | 7 | 2 | digit | 21 | 21 | 21 |  |
| 65537 | 7 | 3 | digit | 21 | 21 | 21 |  |
| 65537 | 7 | 4 | digit | 7 | 7 | 7 |  |
| 65537 | 7 | 5 | digit | 1 | 1 | 1 |  |
| 65537 | 8 | 0 | digit | 1 | 1 | 1 |  |
| 65537 | 8 | 1 | digit | 8 | 8 | 8 |  |
| 65537 | 8 | 2 | digit | 28 | 28 | 28 |  |
| 65537 | 8 | 3 | digit | 56 | 56 | 56 | yes |
| 65537 | 8 | 4 | digit | 28 | 28 | 28 |  |
| 65537 | 8 | 5 | digit | 8 | 8 | 8 |  |
| 65537 | 8 | 6 | digit | 1 | 1 | 1 |  |

(the `unit` rows, ell = sum a_i, are identical integer-for-integer and are in raw-result.json)

## J. Ladder tail check: gap D_null - d_ff per cell

- (2,2,2): gap 0
- (2,2,3): gap 1
- (2,2,4): gap 1
- (2,2,5): gap 2
- (2,2,6): gap 2
- (3,2,4): gap 0
- (3,2,5): gap 1

## K. Frozen criteria restated with the observed values (observation, not judgment)

Success criterion of the contract, at the deciding cell (2, 2, 3):

| # | frozen criterion | observed |
|---|---|---|
| 1 | every Semaev draw has d_ff = 5 and fall_dim = 4 | 12 of 12 draws (5, 4); residual 0 / 0 |
| 2 | NULL-2 equals the Semaev arm on both integers at every draw | 0 / 0 difference at all 12 draws x 5 seeds (10 distinct null objects) |
| 3 | NULL-1 has d_ff = 6 in the majority of seeds with no seed below 6 | 60 of 60 seeds at 6; none below; fall_dim 14 at all |
| 4 | the mixed-block nearby object has d_ff = 6 | 36 of 36 at 6 (fall_dim 14) |
| 5 | H-WIL full rank at every (s, j, p) | 112 of 112 cells at min(C(s,j), C(s,j+2)); square maps full rank |

Ladder extension (s in {2, 4, 5, 6}): Semaev (5,4), (6,10), (6,10), (7,28) on
every draw = frozen; NULL-1 at 5, 7, 8, 9 on every seed = frozen D_null;
NULL-2 = Semaev on both integers at s = 4, 5, 6; at s = 2 NULL-2 has d_ff 5
(= Semaev) but fall_dim 1 (Semaev 4). Gap D_null - d_ff = 0, 1, 1, 2, 2 at
s = 2..6 (frozen tail check 1, 1, 2, 2 at s = 3..6).

Secondary m = 3 (gated open by H-TOP, c = 1): (3,2,4) both targets (13, 12) =
frozen, NULL-1 13 = D_null, NULL-2 d_ff 13 but fall_dim 1; (3,2,5) both
targets (13, 12) = frozen, NULL-1 14 = D_null, NULL-2 (13, 12) = Semaev.

Falsification criteria, each restated with the observation:

| id | frozen condition | observed |
|---|---|---|
| F1 | a Semaev draw at the deciding cell with d_ff != 5 or fall_dim != 4 | none (0 of 12) |
| F2 | NULL-2 differs from the Semaev arm on any draw (deciding cell) | none at the deciding cell (0 of 60 pairs). At the boundary cells (2,2,2) and (3,2,4) the fall_dim integer differs (1 vs 4; 1 vs 12) with d_ff equal; at every strict-early-fall cell including the "next s" both integers coincide. Recorded as anomaly A-NULL2-BOUNDARY-FALLDIM in execution-report.yaml. |
| F4 | NULL-1 falls at the Semaev value (deciding cell) | no (60 of 60 at 6). At boundary cells NULL-1 and Semaev coincide at D_null, which is the frozen prediction for both arms there. |
| F5 | the mixed-block object returns 5 | no (36 of 36 at 6) |
| H-WIL below maximum | any cell | none |
| F3 (hypothesis) | H-TOP fails at m = 3 | no; single monomial, c = 1 |

The NEARBY-NON-MONOMIAL-TOP object (non-blocking) does not realise a
non-monomial top form at s = 3 (x_1^4 -> ell_1^4 has no degree-4 part in three
squarefree variables), and returned d_ff 5 in both readings; the frozen
expectation "between the block value and D_null" is not testable by this
object at s = 3.

## L. What was not measured

- Full rank profiles above d_ff at (2,2,6), (3,2,4), (3,2,5) (stop at first
  fall, D-STOP-FIRST); sol(D) at n > 10.
- m = 4 H-TOP (S_5); the m = 3 fixture at p = 4099; any s outside the ladder.
- The same-instance frozen-fixture comparison with EXP-PFDR-fd901a (the two
  executions drew different instances from the same seeds; profiles agree).
