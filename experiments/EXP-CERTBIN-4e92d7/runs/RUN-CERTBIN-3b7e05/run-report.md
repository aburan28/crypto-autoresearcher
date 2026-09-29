# Run report: RUN-CERTBIN-3b7e05 (EXP-CERTBIN-4e92d7, specification version 1)

Generated mechanically by phase 8 of `experiments/EXP-CERTBIN-4e92d7/impl/driver.py`. Every line below is an observation or the mechanical application of a frozen rule. It declares no hypothesis or heuristic supported, refuted, or closed. That judgement belongs to the Reviewer and the Coordinator.

**Run validity status:** `completed_valid`.

Invalidation rules triggered: none. Voided metrics: none.

## Claim tier and scope (verbatim from the specification)

- claim_tier: **toy**
- statement: Scoped measurement of the trace stability of the declared fixed-shape Macaulay (XL-type) elimination, with the declared row order, column order and pivot rule. The family is the m = 2 direct S_3 Weil descent over F_2[t]/(t^17 + t^3 + 1), with V = {deg < 9} and D in {3, 4}, on one random ordinary curve.
- sota_delta: Zero on every ECDLP cost axis. At best the downstream consequence is a per-attempt constant bounded by the measured saving ratio.
- dominated_by: Parallel Pollard rho with the negation map (Frobenius on Koblitz curves), at every Certicom binary size (about 2^{60.9} at ECC2K-130, from KN-LIT-096 via IDEA-20260922-37e02e) and trivially at n = 17. Trace-free per-attempt engines (FES GPU exhaustive search KN-LIT-287; WDSat) are not compared, so no per-attempt Pareto claim is made.
- certificate_kind: none
- affected_vs_safe: No deployed or standardised curve is touched or affected. n = 17 is a measurement sibling of the prime-degree Certicom family and makes no statement about any challenge.

Tested parameters: n = 17 (F_2[t]/(t^17 + t^3 + 1)), m = 2, l = 9 (V = {deg < 9}), D in {3, 4}, one random ordinary curve (curve.json), the declared row order, degrevlex column order (constant last), and pivot rule. No transfer beyond this cell is claimed. Any statement about n = 131 would be extrapolation resting on the untested HEUR-CERTBIN-TS3.

## Arm sizes (non-degenerate test targets) and UNDERPOWERED flags (SR-3)

| family | D | unsat | sat | degenerate | underpowered |
|---|---|---|---|---|---|
| F-S3 | 3 | 386 | 607 | 7 | no |
| F-S3 | 4 | 386 | 607 | 7 | no |
| F-S3-REV | 3 | 386 | 607 | 7 | no |
| F-S3-REV | 4 | 386 | 607 | 7 | no |
| F-PLANT | 3 | 0 | 200 | 0 | UNDERPOWERED unsat |
| F-PLANT | 4 | 0 | 200 | 0 | UNDERPOWERED unsat |
| F-RANDX | 3 | 361 | 634 | 5 | no |
| F-RANDX | 4 | 361 | 634 | 5 | no |
| F-AFF-1 | 3 | 115 | 878 | 7 | no |
| F-AFF-1 | 4 | 115 | 878 | 7 | no |
| F-AFF-2 | 3 | 126 | 867 | 7 | no |
| F-AFF-2 | 4 | 126 | 867 | 7 | no |
| F-AFF-3 | 3 | 127 | 866 | 7 | no |
| F-AFF-3 | 4 | 127 | 866 | 7 | no |
| F-NULLF2 | 3 | 138 | 862 | 0 | no |
| F-NULLF2 | 4 | 138 | 862 | 0 | no |

## Primary cell: M1-M5 at D = 4 (F-S3 and null counterparts)

| family | retention_family T_strict (count/n, ref) | T_set | T_rank | H(T_strict) bits (distinct/N) | h(P_sat) |
|---|---|---|---|---|---|
| F-S3 | 0 (0/386, U1) | 0 | 0.342 | 9.956 (993/993) | 0.964 |
| F-S3-REV | 0 (0/386, U1) | 0 | 0.342 | 9.956 (993/993) | 0.964 |
| F-PLANT | n/a (None/None, None) | n/a | n/a | 7.644 (200/200) | 0 |
| F-RANDX | 0 (0/361, U1) | 0 | 0.3767 | 9.959 (995/995) | 0.945 |
| F-AFF-1 | 0 (0/115, U1) | 0 | 1 | 9.956 (993/993) | 0.5172 |
| F-AFF-2 | 0 (0/126, U1) | 0 | 1 | 9.956 (993/993) | 0.5488 |
| F-AFF-3 | 0 (0/127, U1) | 0 | 1 | 9.956 (993/993) | 0.5516 |
| F-NULLF2 | 0 (0/138, U1) | 0 | 1 | 9.966 (1000/1000) | 0.579 |

M2 (P2 set, F-S3, D = 4, 5 declared references): {"n": 26, "evaluable": true, "median_h": 0.48166078210121455, "frac_in_[0.4,0.6]": 0.5769230769230769, "min_h": 0.0, "max_h": 0.5137254901960784}

M3 (D = 4, T_strict): {"kind": "not_estimable", "value": null, "bootstrap95": null, "per_draw_ratios": [{"draw": 1, "ratio": null, "reason": "denominator 0"}, {"draw": 2, "ratio": null, "reason": "denominator 0"}, {"draw": 3, "ratio": null, "reason": "denominator 0"}]}

M5 (instrument checks): C-FIX: pass, C-SELF: pass, C-ORACLE: pass, C-WIT: pass, C-AFF: pass, C-DET: pass, C-PASS: pass, C-PROPS: pass, C-UNIF: pass, NESTING: pass, HASH_CONTENT: pass, REF_SELF_REPLAY: pass, C-REV: pass, C-NULLS: pass

## Decision rules (mechanical; each names its granularity and D)

- **DR-1** [T_strict, D = 4]: STRICT P-GPU FALSIFIED at this cell
- **DR-2** [T_strict, D = 4]: between
- **DR-3** [T_strict, D = 4]: E2 FALSIFIED
- **DR-4** [fixed-schedule replay of T_ops (P2 set), D = 4]: not supported, not falsified
- **DR-5** [T_strict, D = 4]: not applicable (retention_family not in (0.01, 0.5))
- **DR-6** [T_set pruning (rows not in Z_D; nonzero columns of those rows), D = 4]: one system per SM FAILS; thousands per warp FAILS (pruned dense bytes of maximizing reference = 1267864)
- **DR-7** [T_strict and T_set, D = 4]: strict replay not closed; T_set replay not closed
- **DR-8**: primary cell F-S3, D = 4, T_strict. Every D = 3 and every T_set/T_rank/T_ops reading is SECONDARY.

Maximizing-reference rule used: argmax of unsat-arm T_strict retention over (U1, U2, U3, modal); ties to the first in that order.

## Predictions P1-P9 (frozen thresholds, mechanical comparison)

| id | quantity | outcome | values |
|---|---|---|---|
| P1 | T_strict retention, unsat arm, F-S3, D = 4 | E1 band held (<= 0.01) | retention_family = 0 (0/386, ref U1) |
| P2 | per-pivot hazard (P2 set) | neither (median >= 0.2, < 90% in band) | n = 26, median h = 0.4817, fraction in band = 0.5769 |
| P3 | K / rank per reference (no directional prediction; E2 needs K <= 1) | E2 condition K <= 1 not met by any reference | K = U1:2670, U2:2670, U3:2669, S1:2671, S2:2670, modal:2668; K/rank = U1:0.999, U2:0.999, U3:0.999, S1:1, S2:1, modal:0.999 |
| P4 | Prop. S T_set matches (sat vs unsat ref with 1 in R_D) | held (0 matches) | F-S3 PS2 vacuous at: F-S3/D3 |
| P5 | median f_div per arm (E1: <= 0.1 both arms, no arm difference) | E1 condition on medians held | U1: unsat 0.000374, sat 0.000374, MW p = 0.568; U2: unsat 0.000374, sat 0.000374, MW p = 0.829; U3: unsat 0, sat 0, MW p = 0.525; S1: unsat 0.000374, sat 0.000374, MW p = 0.579; S2: unsat 0.000374, sat 0.000374, MW p = 0.579; modal: unsat 0, sat 0, MW p = 0.789 |
| P6 | retention ratio F-S3 / F-AFF (M3, D = 4, T_strict) | not estimable (E1 [0.5, 2] clause not evaluable) | {"kind": "not_estimable", "value": null} |
| P7 | H(T_strict), D = 4 (E1 >= 8.97; P-GPU needs <= h(P_sat) + 0.1) | E1 threshold met; P-GPU entropy condition not met | H = 9.956 bits, distinct = 993, N = 993, h(P_sat) = 0.964 |
| P8 | saving ratio (<= 10 predicted; < 1.5 closes) | failed (some > 10); DR-7: strict not closed, T_set not closed | saving_strict U1:35.57, U2:35.66, U3:35.08, S1:33.59, S2:35.36, modal:35.03; saving_set U1:1.658, U2:1.658, U3:1.659, S1:1.658, S2:1.659, modal:1.66 |
| P9 | pruned D = 4 sizes vs 32 B / 228 KB (predicted: no full dense D = 4 matrix meets either) | full dense prediction held; DR-6: one-per-SM FAILS, thousands-per-warp FAILS | pruned dense bytes U1:1267864, U2:1267864, U3:1267390, S1:1267864, S2:1267390, modal:1266915 |

## Proposition S: PS2 vacuity

- F-S3/D3: VACUOUS
- F-S3/D4: not vacuous
- F-S3-REV/D3: VACUOUS
- F-S3-REV/D4: not vacuous
- F-RANDX/D3: VACUOUS
- F-RANDX/D4: not vacuous
- F-AFF-1/D3: VACUOUS
- F-AFF-1/D4: VACUOUS
- F-AFF-2/D3: VACUOUS
- F-AFF-2/D4: VACUOUS
- F-AFF-3/D3: VACUOUS
- F-AFF-3/D4: VACUOUS
- F-NULLF2/D3: VACUOUS
- F-NULLF2/D4: VACUOUS

## Coordinator prior (a)-(g) against the data

The prior is qualitative in places. The operational readings used are: (a) as written; (b) 'K >> K_rank' read as K > K_rank for every reference; (c) 'medians near 0.5' read as the median inside the contract's [0.4, 0.6] hazard band; (d) as written, over every reference and both arms for T_rank, and the family maxima for the T_set ordering; (e) 'most' read as more than half of the non-degenerate unsatisfiable arm with D* not reached; (f) saving_set >= 1.5 and saving_strict in [2, 10], with closeness to 1.5 left to the reviewer; (g) as written. The values are given so a reviewer can apply a different reading.

| part | prior statement (paraphrase) | status | observed |
|---|---|---|---|
| (a) | M1 <= 0.01 for every reference at D = 4 and H(T_strict) >= 8.97 | not overturned | M1: U1=0, U2=0, U3=0, modal=0; H = 9.956 |
| (b) | K_rank <= 17 and K >> K_rank at D = 4 | not overturned | U1: K=2670, K_rank=17, U2: K=2670, K_rank=17, U3: K=2669, K_rank=17, S1: K=2671, K_rank=17, S2: K=2670, K_rank=17, modal: K=2668, K_rank=17 |
| (c) | P2 set small; medians near 0.5; the 90%-in-band clause could fail | not overturned | median h = 0.4817, fraction in band = 0.5769, set size 26 |
| (d) | T_rank retention within an arm >= 0.9, and T_set between T_rank and T_strict | OVERTURNED (T_rank < 0.9 for some reference/arm) | T_rank retention (unsat, sat): U1=(0.342, 0.264), U2=(0.342, 0.264), U3=(0.13, 0.301), S1=(0.342, 0.264), S2=(0.13, 0.301), modal=(0.0144, 0.192); family max unsat: T_rank 0.342, T_set 0, T_strict 0 |
| (e) | most unsat instances do NOT reach 1 in R_4; PS2 possibly vacuous; D* mostly not reached | OVERTURNED | unsat arm D* distribution {'4': 324, 'not reached at D <= 4': 62}; PS2 vacuous at D = 4: False; 1-in-R_4 rate unsat = 0.8394 |
| (f) | saving_set >= 1.38 (identity) and just above the 1.5 closure threshold at D = 4; saving_strict between 2 and 10 | OVERTURNED (saving_strict outside [2, 10]) | saving_set U1:1.658, U2:1.658, U3:1.659, S1:1.658, S2:1.659, modal:1.66; saving_strict U1:35.57, U2:35.66, U3:35.08, S1:33.59, S2:35.36, modal:35.03; how close counts as 'just above' is not operationalised here: the values are reported for the reviewer |
| (g) | M3 not estimable or in [0.5, 2] | not overturned | {"kind": "not_estimable", "value": null} |

## Raw-result and cell-summary agreement

raw-result.json was recomputed from the written targets-*.jsonl.gz and pivot-hazards.json files and compared with cell-summary.json on 477 primary-metric items: all agree.

