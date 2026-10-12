# EXP-PFDR-1b78f7 -- analysis (composition of the whole-run-set review round)

- Experiment: EXP-PFDR-1b78f7, protocol v3 (specification v1 + AMD-20260929-1de84f + AMD-20260929-430f44)
- Hypothesis: H-PFDR-4765e4 (related: H-PFDR-0cc7e8). Question: RQ-PFDR-ae2fba.
- Runs (17):
  - RUN-PFDR-1b78f7-tests
  - RUN-PFDR-1b78f7-tests-amd1de84f
  - RUN-PFDR-1b78f7-reg-off-sweep-20260924
  - RUN-PFDR-1b78f7-reg-off-sweep-mitm-20260926
  - RUN-PFDR-1b78f7-reg-off-sweep-arity-20260926
  - RUN-PFDR-1b78f7-reg-off-sweep-minfill-20260926
  - RUN-PFDR-1b78f7-reg-off-sweep-arity-minfill-20260926
  - RUN-PFDR-1b78f7-reg-off-sweep-arity67-20260928
  - RUN-PFDR-1b78f7-reg-census-sweep-minfill-20260926
  - RUN-PFDR-1b78f7-reg-census-sweep-arity-minfill-20260926
  - RUN-PFDR-1b78f7-census-m3
  - RUN-PFDR-1b78f7-census-m4
  - RUN-PFDR-1b78f7-census-m5
  - RUN-PFDR-1b78f7-rho
  - RUN-PFDR-1b78f7-j0
  - RUN-PFDR-1b78f7-analysis
  - RUN-PFDR-1b78f7-stage-r
- Run-set archives: TASK-20260928-f15632 (R01-R09); TASK-20260929-599b4b (R01a, R10, R11 attempt 1); TASK-20260929-0f66ef (R11 attempt 2 and merged/, R12-R16; commit a32e70808).
- Review round: plan inline on ledger/handoffs/TASK-20260929-accb8e.yaml (handoff.review_plan). Object under review: commit a32e708088c16b46686ea19afaab72910a42d75f. Reports sealed by TASK-20260929-d9bf1b (commit bbb741f98).
  - validator TASK-20260929-accb8e owns J1-J5
  - red team TASK-20260929-f29c96 owns J6-J8 and proves_too_much
- Evidence record: EV-PFDR-1faf10. Decision: DEC-20260929-bbb3a9. Ledger archive of both: TASK-20260929-25f53d.
- This file: DEC-20260929-bbb3a9 NA-14, written on the user decision of 2026-10-01 and archived by TASK-20260929-4ab45d.

This file renders the `analysis` block of EV-PFDR-1faf10 item by item, under its four headings: Observation (OBS-1..OBS-14), Comparison (CMP-1..CMP-6), Inference (INF-1..INF-7) and Limitation. Each item keeps the record's id, text, numbers and citations. Nothing is moved between sections, and nothing is added. No number was recomputed by this Coordinator, which holds no shell. Where this file and the record differ, the record governs.

TW-FLOOR fired. This file, like the record, contains no A7 value, floor ratio or floor-relative reading.

---

## 1. Observation

**OBS-1.** Outcome as frozen (R15, R16; reproduced blind by the validator, J3). R15 returned O-EXCURSION with four excursions among 166 resolved (A, c in {TT, SS}, m, rung) cells, all with z > 0. They are (subgroup, TT, m 3, 28 bits) z 3.660, kappa 1.197; (small_x, SS, 4, 20) z 3.390, kappa 1.250; (dickson, SS, 4, 26) z 3.945, kappa 1.100; and (subgroup, TT, 5, 16) z 4.752, kappa 4.412. Stage R (R16, curves 5..9) gave z 0.298, -1.989, -2.959 and -0.431, so none replicated. The frozen final structural reading is O-NULL with the excursion list attached. O-ALIVE is not met for any (A, c, m): all 14 resolved A2 slopes are negative (-0.22 to -0.11), no interval lies above 0, and every Holm-adjusted p is >= 0.95. The four TT m 4 tests and all TB tests are unresolved.

**OBS-2.** O-GENERIC as frozen. (1a) is met: 50 of 50 medians >= 1.3. (1b) is not met: 9 of 10 |delta| <= 0.03, and subgroup m 5 has delta -0.0375 on n = 54 paired instances, with paired-bootstrap interval [-0.058, -0.017] (red team 06). (2) is met and not falsified: the m = 4 small_x harvest-on exponent is 0.6076 [0.601, 0.614], against the criterion point <= 0.66 and the falsifier lower end > 0.66. HEUR-4765e4-H1 per A6 is rejected at 1% for (TT,3), (TT,4), (TT,5), (TB,3), (SS,4) and (SS,5), and not for (SS,3), (TB,4) or (TB,5). HEUR-4765e4-H3 per A3: rank >= min(n, U)/1.05 fails on every TT instance and on about 10% of SS instances, and permutation stability fails for most TT and SS instances in every arm. Median rho_c >= 0.95 holds for SS at every m (validator J3 Q5, Q9, Q3).

**OBS-3.** Pair multiplicity. Each distinct relation appears as several pair coincidences. Pairs per distinct normalised relation on the random arms (census, complete instances): TT m 3 2.66-3.00 (max 3); TB about 3; TT m 5 7.3-10.8 (max 234); SS m 3 1.56-1.93; SS m 4 4.1-5.4 (max 246); SS m 5 4.2-5.8 (max 294). The pooled within-curve index of dispersion of random pair counts is 2-6 (TT m 3), 10-51 (TT m 5), 2-5 (SS m 3), 44-444 (SS m 4) and 9-32 (SS m 5), against 1 for Poisson. Counted in distinct relations, the random-arm dispersion is 0.9-1.9, except SS m 4 at 13.2 (red team J6, J7 a, 02_bundles, 03, 10).

**OBS-4.** Relation-level recount (red team ALT-a1, alternative pre-registered in attacks/choices.yaml before computing): 0 excursions among 133 resolved computable cells, with 16 blocked by row retention and 49 cells below C_R >= 10 in relation units. The largest discovery z is 2.60 (subgroup, TT, m 3, 28 bits; kappa 1.196), which is 0.25 at Stage R. (dickson, SS, 4, 26) cannot be recounted.

**OBS-5.** Under the other convention alternatives the excursion count moves: exposure-normalised (ALT-b1) 4, the same cells; the structured arm's own variance (ALT-e1) 3; dispersion-floored V (ALT-e2) 1, subgroup TT 3 28 only; SS at stop (ALT-f) 7, a mostly different set; no censoring drop or drop only the affected arm (ALT-d1, d2) 4, identical. The structured arms are NOT more dispersed than the random arms: the pooled residual-variance ratio is 0.31-1.28 (J7 e).

**OBS-6.** Proves-too-much. PTM-1 read the random arms as structured: 19 excursions among 329 resolved pseudo-cells (5.8%), 16 positive, max z 10.77. The structured arms under the same statistic give 18 of 497 (3.6%). At Stage R, 3 of 12 random pseudo-cells have |z| > 3. PTM-2, synthetic null pipeline: E[excursions] 3.9-4.5, and P(replicated anomaly per pipeline) 0.08-0.12 under overdispersed nulls.

**OBS-7.** Detection limit (PTM-3, planted Poisson excess). X is the smallest kappa in {1.1, 1.25, 1.5, 2, 3, 5} with P(leave O-NULL) >= 0.5, at 30-32 bits, weakest arm: TT m 3 1.5; TT m 4 not detectable at any kappa <= 5 (every TT m 4 cell at 30-32 bits is unresolved); TT m 5 2.0; SS m 3 1.25; SS m 4 1.25; SS m 5 2.0. X is in pair units. The compound planted form raised X in 2 of 40 cells and lowered it in none.

**OBS-8.** Stage R one-sided 95% upper bounds on kappa under calibrated nulls (red team 05): subgroup TT m 3 28b 1.10-1.14; subgroup TT m 5 16b 1.42-1.92; small_x SS m 4 20b and dickson SS m 4 26b below 1.00 (the grid floor), in exposure-unnormalised pair units. Their exposure-normalised Stage R z are +0.22 and -2.02, so the SS bounds would be higher; they were not computed.

**OBS-9.** Interval calibration (validator J5, own code, 1000-1500 synthetic series per configuration). stats.bootstrap_slope at 11x5 and 7x5 covers 0.887-0.909 against 0.95. stats.fit_exponent covers 0.913-0.916, and the paired delta bootstrap 0.903-0.909. A2's curve-index bootstrap covers 0.864-0.875, and at delta = 0 its "interval entirely above 0" fires 0.070 against 0.025. Derivation (J5 c): resampling n = 5 units deflates the bootstrap SE by sqrt((n-1)/n) = 0.894, which predicts 0.909-0.913 and explains most of the shortfall.

**OBS-10.** Instrument (validator F-J3-1; red team OBJ-5). harvest.py end_attempt rebuilds an SS x-group only from the first sorted run holding the key, so pairs_raw undercounts C(k', 2) and never overcounts. It affects 1052 of 3056 complete SS blocks at the stop and 328 at A_fix. At A_fix the undercount is small and arm-symmetric (structured vs random 0.11% vs 0.19% at m 3, 0.68% vs 0.75% at m 4, 0.02% vs 0.13% at m 5). Max |dz| is 0.053 where it can be recomputed. The 36 SS cells above 24 bits cannot be recomputed. The defect biases excess coincidence groups slightly toward the null.

**OBS-11.** Seed and order robustness (red team J6 c, MC-1 to MC-3). Every A2 decision element flips in 0 of 200 seeds and 0 of 20 curve orders. The margin is > 35 Monte Carlo s.d. everywhere. (2)'s lower-end MC s.d. is 0.0002 against a margin of 0.059. (1b) is deterministic on the point delta. A1 z, Stage R z and the A4 medians are invariant under reversal and 20 shuffles. The six A6 rejections hold under 200 alternative PIT seed families. Non-rejections near the threshold are seed-fragile: TB|5 rejects under 30% of families.

**OBS-12.** A6 multiplicity and first moment (red team J6 e). P(at least one (class, m) rejected | H1) = 0.144, and P(>= 6 | H1) < 5e-5. The H1 first moment (sum n / sum mu) is within 0-2% for TT|3, TT|5, SS|3, SS|4 and SS|5 (1.002, 1.001, 0.995, 0.998, 1.013). It is 0.80, 0.91 and 0.91 for TB|3, TT|4 and TB|4.

**OBS-13.** TW-FLOOR fired: 73 on-mode instances, and 0 census-mode instances, by key. They are 35 known_log (m 3, 12-24 bits, every curve), 17 j0_coset (m 3), and 21 main-panel generic-arm instances at m = 4 (10) and m = 5 (11), of which 14 are on random arms. R16 has 0 of 160. Keys only (validator J3 tw_floor). No value was read by this Coordinator, and none is reported.

**OBS-14.** Cost charging (validator F-COST-1). A4's ratio is an S_3-count ratio. At 32 bits harvest-on also carries the SS store (medians 12-24 MB), 2.0-2.4 s of harvest time in 2.8-4.4 s per instance, and row-certificate group operations that in census mode can exceed S_3 (m 4, 32 bits: 4.9e7 against 2.1e7).

---

## 2. Comparison

**CMP-1.** Excursions against the calibrated null. Observed 4, all positive, among 166 resolved cells. Under nulls fitted to the random arms' own dispersion (G-NB, G-CP, G-RES) the expected count is 3.5-4.5, and P(>= 4) is 0.47-0.66. P(>= 4, all positive) is 0.10-0.27, and P(max |z| >= 4.75) is 0.35-0.65. The frozen test's own Poisson model gives E 0.34, P(>= 4) 0.0004, and R15's Gaussian tail check 0.000335 (red team J6 a; MC s.e. of P(>= 4) <= 0.0035).

**CMP-2.** Stage R against its null. The per-cell same-sign null replication rate is 0.006-0.056 against the nominal 0.00135, and 0.072-0.082 family-wise over the four cells. Power at the discovery kappa (selection-biased) is 0.12-0.62 for three cells and 0.89-1.00 for subgroup TT m 5. Power at the Stage R kappa is <= 0.03 for every cell (red team 05).

**CMP-3.** Known-null against structured. Under the identical statistic the random arms read as structured excurse at 5.8%, and the structured arms at 3.6% (PTM-1). The known-null objects excurse MORE often.

**CMP-4.** Pair units against relation units. There are 4 excursions in pairs and 0 of 133 computable cells in relations (OBS-4). (small_x, SS, 4, 20) goes from a pair excess of 1410 to a relation excess of 94. About 850 of its excess pairs sit in 2-target bundles counted 90-138 times. (subgroup, TT, 5, 16): 50 pairs from 8 relations against a random mean of 1.67 relations.

**CMP-5.** Census-mode s3 exponents against the committed min_fill sweeps at the same m: every pair of intervals overlaps. Differences are -0.011 to +0.021 (red team MC-6 baseline_consistency).

**CMP-6.** Against the Coordinator's pre-recorded prior (plan coordinator_prior; exposure PD-1). J1-J4 held as expected. J5 broke as expected (0.86-0.92, prior 0.85-0.9). J6 broke in the expected direction but larger than the prior: E 3.5-4.5 against a prior of 1-4, and P(>= 4) 0.47-0.66 against 0.05-0.5. The non-replication was as expected (prior 0.75). J7 overturned the prior in mechanism: the consequential convention is the counting unit with a pair-unit Poisson floor, not a structured-arm dispersion, which does not occur. J8 held as expected. Proves-too-much also overturned two priors: the random arms excurse more often than the structured ones, and Stage R's false-replication rate is not near nominal. Unanticipated by the prior: F-J1-1, F-J3-1/OBJ-5 and the exposure confound. Concurrence on J1-J5 and J8 is weakened by PD-1, since the prior was written after reading the structural parts of the report. The J7 and PTM overturns are the informative results of the round.

---

## 3. Inference (Coordinator)

**INF-1.** O-EXCURSION carries no evidence of structure on this design. Its count is the calibrated null's expected count, and its sign is the null's dominant direction. The excursions vanish in relation units, and the procedure excurses more often on known-null arms (CMP-1, CMP-3, CMP-4). What manufactures them is the pair unit combined with a Poisson variance floor in pair units, estimated from 10 df.

**INF-2.** The Stage R non-replication survives as a scoped non-detection, not as kappa = 1. It bounds kappa per cell (OBS-8). A Stage R replication would have carried a 7-8% family-wise false-alarm rate, so neither branch of the frozen Stage R rule was well calibrated (CMP-2).

**INF-3.** The frozen closure reading (O-NULL, lead 2 closed with the measured band as the obstruction record) is NOT adopted as written. The measured band is miscalibrated, so it is not a valid obstruction record. What the data support is a detection-limited non-detection: no structural excess of kappa >= X per (class, m) at 30-32 bits was detected on the tested arms (OBS-7). Smaller excesses, TT at m = 4 and TB are not covered. The closure question moves to relation units under a calibrated null (DEC-20260929-bbb3a9 NA-5).

**INF-4.** HEUR-4765e4-H1 as formally stated ("per-class coincidence counts are Poisson") is refuted for PAIR counts at the tested scale in six (class, m), as its falsification condition says. The refutation is seed-robust and multiplicity-robust (OBS-11, OBS-12). Its content is the Poisson SHAPE of a count whose units are dependent by construction (OBS-3). The collision model's FIRST MOMENT is not refuted for TT|3, TT|5, SS|3, SS|4 and SS|5, where it matches within 2%. For TB|3, TT|4 and TB|4 the mean itself is 9-20% below H1's. The same A6 reading fires the A6 clause of HEUR-0cc7e8-H1's falsification condition (H-PFDR-0cc7e8), with the same first-moment caveat. Any floor-relative consequence is withheld under TW-FLOOR.

**INF-5.** Prediction 4 for TT and HEUR-4765e4-H3's rank clause fail through the same unit mechanism. At table arity 2 one relation appears as about 3 TT pair rows, so rank is about relations, well under 0.95 of the pair rows on random arms as well. This is a specification mismatch between the hypothesis's row unit and its rank prediction, not a structural finding.

**INF-6.** The generic readings stand as S_3-count statements on this engine: (1a) met; (2) met and not falsified, robust to seed and to the design-evaluated threshold; (1b) not met on a point reading at one base, whose interval straddles the threshold. No speedup statement follows without the uncharged terms of OBS-14. The framing of (2) as the positive control that the IDEA-20260928-ce3ab0 floor is attainable, and any comparison of that exponent with the floor model's (m+1)/(2m) or its design-evaluated values, is FLOOR-RELATIVE. It is withheld and routed to the TW-FLOOR round.

**INF-7.** Every interval-based wording from A2, A4 or stats.bootstrap_slope on five units per rung is weaker than nominal (OBS-9). No decision in this run set flips because of it.

---

## 4. Limitation

- Toy scale, 12..32 bits, generated prime-order curves, one mitm engine (min_fill, default arity), m = 3, 4, 5, five curves per rung, five fresh curves per excursion cell. No deployed-curve implication, universal impossibility or exponent below rho's (TW-SCOPE).
- The calibration figures (family null, Stage R null and power, PTM-2, PTM-3) are one red team's plug-in simulations, with means and dispersion taken from the same random arms. G-CP extrapolates SS m 4 multiplicities from 24 to 26-32 bits. On real known-null data the generators under-predict the excursion count (13.8-15.4 against 19), so the calibrated null rates are, if anything, conservative. No second agent re-ran them.
- The relation-level recount is a review-time alternative convention, not the frozen protocol. It bounds interpretation and changes no frozen reading or success criterion.
- Stage R was run by the producer's session and engine: it is part of this run set, not an independent replication.
- F-J1-1 (solve certificates not re-verifiable) and F-J3-1 (SS counter; not recomputable above 24 bits) as in the validity block.
- Same-model review. Session independence of the reviewers is attested; model independence is not claimed (both served by the same model as producer and Coordinator; red team inference block).
- TW-FLOOR withheld every floor-relative reading. This record is silent on A7 and on the floor.
