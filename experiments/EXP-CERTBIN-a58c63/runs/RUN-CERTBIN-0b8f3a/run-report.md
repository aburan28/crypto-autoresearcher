# Run report: EXP-CERTBIN-a58c63 / RUN-CERTBIN-0b8f3a

Observations and mechanically applied decision rules only. No hypothesis status, evidence record or knowledge entry is written or implied here. Verdict strings are the rule outputs defined in the frozen specification (DB-1..DB-12); adjudication belongs to the review round and the Coordinator.

## Claim tier and scope (verbatim from the specification)

- claim_tier: toy
- statement: Trace-stability and competence measurement of the declared fixed-shape Macaulay eliminations (regime A over F_2 after descent; regime B over F_{2^n}) for the m = 2 direct S_3 system with polynomial-basis V, at the four cells above, on one curve per n.
- sota_delta: zero on every ECDLP cost axis
- dominated_by: Per attempt: oracle A (2^l quadratic root-findings: 32 at l = 5, 64 at l = 6) decides satisfiability and returns the solutions; it dominates a 2028 x 2278 or 3276 x 2278 elimination over F_{2^n} by orders of magnitude (OBJ-9). For the DLP: parallel Pollard rho with the negation map (about 2^8 to 2^9 group operations at these n). Joux-Vitse F4' (KN-LIT-673219) is the only source-verified trace-reuse constant (2.43x-3.40x over F_{p^5}); FES GPU (KN-LIT-287) and WDSat are not compared.
- affected_vs_safe: No deployed or standardized curve is touched or affected.

A "STABLE" regime-B verdict at l = 6 (D = 66) is not a P-GPU result (DB-7; Lemma B-S (d)). No GPU was run. Python/numpy wall time is not GPU cost.

## Validity

- status: **completed_valid**
- run-voiding failures: none
- partial invalidations: none
- protocol version: 2 (specification v1 + AMD-20260924-3a9f06, sha256 805b307f9257ac7484f5d7a1d248e4dbfcd3ac41ae38bdfffb1f7943ec7886c7, commit 8a1d5558e2f75f7e9984b3ab1d05eda5381ba58c)
- schedule: C_std; basis: C-PILOT consequence (AMD C-16): C-PILOT is recorded as FAILED pre-run because version-1 frozen streams were drawn in dev before the decision; the count schedule is C_std regardless; T_proj is reported but not binding (T_proj = 3822 s single-worker, not binding)
- raw-result agrees with cell-summary on every recomputed primary count: True

## Protocol version 2 changes that bind a verdict (AMD-20260924-3a9f06 C-13)

- C-1/C-2 (ruling 1): first-match classification R0-R6; E3 success = R3 COLUMN at the target's own first non-pivot column. Binds MB2, MB5, DB-5 and hence DB-7 at the l = 5 cells. The rejected PREFIX-first reading is reported as E3_prefix_first_sensitivity in cell-summary.json and feeds no rule.
- C-3 (C-CLASS / INV-10), C-4/C-5 (C-REPLAYB v2 / INV-5 v2): bind the validity of DB-3, DB-4, DB-5, DB-11.
- C-6/C-7: K_B by the T_strict-guided computation on one S_probe stream; K_B(cell) = sum over unsat references (DB-3, DB-4).
- C-8/C-9: F-SAT/F-PLANT exhaustion stops; the E3 arm is their union by x_R; DB-5 UNDERPOWERED below 100; DB-7 NOT EVALUABLE on a void or underpowered conjunct.
- C-11/C-12: per-family modal; C-DELTA/C-RANKB also on the regime-B nulls (DB-8, M3).
- C-14/C-16: 18 retired seeds replaced by old + 10000; the count schedule is C_std by C-PILOT's own consequence.
- C-25: DB-5 and DB-7 at the l = 5 cells become exploratory_only if the review round finds that ruling 1 chose between two readings that both test C3. The coordinator prior (a)-(g) below is scored as written; it was not updated, and dev outputs (not frozen outputs) were seen before protocol version 2 was fixed.

## Decision rules per cell

### n17-l6

- **DB-1** (B D = 66 T_strict): STABLE
- **DB-2** (B D = 66 ): DOES NOT DECIDE AT THIS D
- **DB-3** (B D = 66 ): CONSISTENT
- **DB-5** (B D = 66 ): NOT EVALUABLE
- **DB-6** (  ): CONTRAST CONFIRMED
- **DB-7** (  ): P-GPU NOT SUPPORTED AT THIS CELL
- **DB-8** (  ): GENERIC STABILITY
- **DB-10** (A D = 4 ): KR1/RR-2: HULL RANK FULL; TS1R/RR-4: SUPPORTED; P-C3: HOLDS
- **DB-11** (  ): INDEPENDENT
- **DB-9**: {'B': {'maximizing_ref': 'U1', 'pruned_dense_bytes': 13859352, 'saving_strict': 603836.1858224364, 'one_system_per_SM': 'FAILS', 'thousands_per_warp': 'FAILS', 'strict_replay_closed_(saving_strict<1.5)': False, 'D': 66}, 'A': {'maximizing_ref': 'U1', 'pruned_dense_bytes': 63794.0, 'saving_strict': 11.537875591045324, 'one_system_per_SM': 'SURVIVES', 'thousands_per_warp': 'FAILS', 'strict_replay_closed_(saving_strict<1.5)': False, 'D': 4}}
- DB-7 failing conjuncts: ['DB-2 = DOES NOT DECIDE AT THIS D', 'DB-5 = NOT EVALUABLE']

### n19-l6

- **DB-1** (B D = 66 T_strict): STABLE
- **DB-2** (B D = 66 ): DOES NOT DECIDE AT THIS D
- **DB-3** (B D = 66 ): CONSISTENT
- **DB-5** (B D = 66 ): NOT EVALUABLE
- **DB-6** (  ): CONTRAST CONFIRMED
- **DB-7** (  ): P-GPU NOT SUPPORTED AT THIS CELL
- **DB-8** (  ): GENERIC STABILITY
- **DB-10** (A D = 4 ): KR1/RR-2: HULL RANK FULL; TS1R/RR-4: SUPPORTED; P-C3: HOLDS
- **DB-11** (  ): INDEPENDENT
- **DB-9**: {'B': {'maximizing_ref': 'U1', 'pruned_dense_bytes': 13859352, 'saving_strict': 603836.1858224364, 'one_system_per_SM': 'FAILS', 'thousands_per_warp': 'FAILS', 'strict_replay_closed_(saving_strict<1.5)': False, 'D': 66}, 'A': {'maximizing_ref': 'U1', 'pruned_dense_bytes': 63794.0, 'saving_strict': 11.30112461833147, 'one_system_per_SM': 'SURVIVES', 'thousands_per_warp': 'FAILS', 'strict_replay_closed_(saving_strict<1.5)': False, 'D': 4}}
- DB-7 failing conjuncts: ['DB-2 = DOES NOT DECIDE AT THIS D', 'DB-5 = NOT EVALUABLE']

### n17-l5

- **DB-1** (B D = 66 T_strict): STABLE
- **DB-2** (B D = 66 ): DECIDES
- **DB-3** (B D = 66 ): CONSISTENT
- **DB-5** (B D = 66 ): E3 HOLDS
- **DB-6** (  ): CONTRAST CONFIRMED
- **DB-7** (  ): P-GPU (STRICT REPLAY) SURVIVES IN REGIME B AT THIS CELL
- **DB-8** (  ): GENERIC STABILITY
- **DB-10** (A D = 4 ): KR1/RR-2: HULL RANK FULL; TS1R/RR-4: SUPPORTED; P-C3: HOLDS
- **DB-11** (  ): INDEPENDENT
- **DB-9**: {'B': {'maximizing_ref': 'U1', 'pruned_dense_bytes': 15567852, 'saving_strict': 40.93753870368621, 'one_system_per_SM': 'FAILS', 'thousands_per_warp': 'FAILS', 'strict_replay_closed_(saving_strict<1.5)': False, 'D': 66}, 'A': {'maximizing_ref': 'U1', 'pruned_dense_bytes': 16497.0, 'saving_strict': 8.257055545568937, 'one_system_per_SM': 'SURVIVES', 'thousands_per_warp': 'FAILS', 'strict_replay_closed_(saving_strict<1.5)': False, 'D': 4}}
- DB-7 failing conjuncts: []

### n19-l5

- **DB-1** (B D = 66 T_strict): STABLE
- **DB-2** (B D = 66 ): DECIDES
- **DB-3** (B D = 66 ): CONSISTENT
- **DB-5** (B D = 66 ): E3 HOLDS
- **DB-6** (  ): CONTRAST CONFIRMED
- **DB-7** (  ): P-GPU (STRICT REPLAY) SURVIVES IN REGIME B AT THIS CELL
- **DB-8** (  ): GENERIC STABILITY
- **DB-10** (A D = 4 ): KR1/RR-2: HULL RANK FULL; TS1R/RR-4: SUPPORTED; P-C3: HOLDS
- **DB-11** (  ): INDEPENDENT
- **DB-9**: {'B': {'maximizing_ref': 'U1', 'pruned_dense_bytes': 15567852, 'saving_strict': 40.93731029504703, 'one_system_per_SM': 'FAILS', 'thousands_per_warp': 'FAILS', 'strict_replay_closed_(saving_strict<1.5)': False, 'D': 66}, 'A': {'maximizing_ref': 'U1', 'pruned_dense_bytes': 16497.0, 'saving_strict': 7.961848635235732, 'one_system_per_SM': 'SURVIVES', 'thousands_per_warp': 'FAILS', 'strict_replay_closed_(saving_strict<1.5)': False, 'D': 4}}
- DB-7 failing conjuncts: []

### DB-4 (n-scaling at fixed l)

- l6: UNRESOLVED; interval 0..inf; inputs {'x19': 0, 'N19': 999, 'x17': 0, 'N17': 987, 'K_B_sum_19': 6, 'K_B_sum_17': 6, 'K_B_definition': "sum over the cell's unsat references (AMD C-7); None if any is not estimable"}; (K_B19/K_B17)/4 = 0.25; consistent: True
- l5: UNRESOLVED; interval 0..inf; inputs {'x19': 0, 'N19': 999, 'x17': 0, 'N17': 994, 'K_B_sum_19': 333, 'K_B_sum_17': 333, 'K_B_definition': "sum over the cell's unsat references (AMD C-7); None if any is not estimable"}; (K_B19/K_B17)/4 = 0.25; consistent: True

DB-12 primary/secondary: {'primary': ['DB-1, DB-2, DB-5, DB-6, DB-7 at (17, 6) and (17, 5)', 'DB-3 at every cell', 'DB-4 per l'], 'secondary': ['every n = 19 verdict other than DB-3/DB-4', 'every T_set, T_rank, T_ops, D = 3, null or cross-family reading']}

## Pre-registered predictions: observed values against the frozen thresholds

### n17-l6
- PB-1 regime-B T_strict retention_family (unsat): 1 (min 1); threshold >= 0.9
- PB-2 break counts vs Poisson 99.9%: U1: X = 0, K_B = 2, interval [0, 1], inside = True; U2: X = 0, K_B = 2, interval [0, 1], inside = True; U3: X = 0, K_B = 2, interval [0, 1], inside = True
- PB-4 E3 (pooled, per unsat ref): U1: 0/358; U2: 0/358; U3: 0/358 (evaluable: False)
- PB-5 unsat arm 1 in R_66: 0/987; rank distribution {2028: 987}
- PB-6 / PC-3 regime-A T_strict retention_family (D = 4): 0
- PC-1 K_rank_hull vs dim W (D = 4): U1: 16/16; U2: 16/16; U3: 16/16; S1: 16/16; S2: 16/16; modal: 16/16
- PC-2 TS1R (F-S3, D = 4): m = 22, o = 0, P = 1.0, RR-4: SUPPORTED
- PB-7 regime-B pruned dense bytes (maximizing ref U1): 13859352 (full 13859352); saving_strict 6.038e+05
- TS2G delta tail: {'min_delta_unsat_F-S3': 126, 'threshold_2^(l+1)-2': 126, 'n_below': 0, 'n': 987, 'fraction_below': 0.0, 'TS2G_falsified_(>1%)': False}

### n19-l6
- PB-1 regime-B T_strict retention_family (unsat): 1 (min 1); threshold >= 0.9
- PB-2 break counts vs Poisson 99.9%: U1: X = 0, K_B = 2, interval [0, 1], inside = True; U2: X = 0, K_B = 2, interval [0, 1], inside = True; U3: X = 0, K_B = 2, interval [0, 1], inside = True
- PB-4 E3 (pooled, per unsat ref): U1: 0/355; U2: 0/355; U3: 0/355 (evaluable: False)
- PB-5 unsat arm 1 in R_66: 0/999; rank distribution {2028: 999}
- PB-6 / PC-3 regime-A T_strict retention_family (D = 4): 0
- PC-1 K_rank_hull vs dim W (D = 4): U1: 18/18; U2: 18/18; U3: 18/18; S1: 18/18; S2: 18/18; modal: 18/18
- PC-2 TS1R (F-S3, D = 4): m = 19, o = 0, P = 1.0, RR-4: SUPPORTED
- PB-7 regime-B pruned dense bytes (maximizing ref U1): 13859352 (full 13859352); saving_strict 6.038e+05
- TS2G delta tail: {'min_delta_unsat_F-S3': 125, 'threshold_2^(l+1)-2': 126, 'n_below': 1, 'n': 999, 'fraction_below': 0.001001001001001001, 'TS2G_falsified_(>1%)': False}

### n17-l5
- PB-1 regime-B T_strict retention_family (unsat): 1 (min 1); threshold >= 0.9
- PB-2 break counts vs Poisson 99.9%: U1: X = 0, K_B = 111, interval [0, 5], inside = True; U2: X = 0, K_B = 111, interval [0, 5], inside = True; U3: X = 0, K_B = 111, interval [0, 5], inside = True
- PB-4 E3 (pooled, per unsat ref): U1: 221/221; U2: 221/221; U3: 221/221 (evaluable: True)
- PB-5 unsat arm 1 in R_66: 994/994; rank distribution {2278: 994}
- PB-6 / PC-3 regime-A T_strict retention_family (D = 4): 0
- PC-1 K_rank_hull vs dim W (D = 4): U1: 16/16; U2: 16/16; U3: 16/16; S1: 16/16; S2: 16/16; modal: 16/16
- PC-2 TS1R (F-S3, D = 4): m = 22, o = 0, P = 1.0, RR-4: SUPPORTED
- PB-7 regime-B pruned dense bytes (maximizing ref U1): 15567852 (full 22388184); saving_strict 40.94
- TS2G delta tail: {'min_delta_unsat_F-S3': 62, 'threshold_2^(l+1)-2': 62, 'n_below': 0, 'n': 994, 'fraction_below': 0.0, 'TS2G_falsified_(>1%)': False}

### n19-l5
- PB-1 regime-B T_strict retention_family (unsat): 1 (min 1); threshold >= 0.9
- PB-2 break counts vs Poisson 99.9%: U1: X = 0, K_B = 111, interval [0, 3], inside = True; U2: X = 0, K_B = 111, interval [0, 3], inside = True; U3: X = 0, K_B = 111, interval [0, 3], inside = True
- PB-4 E3 (pooled, per unsat ref): U1: 245/245; U2: 245/245; U3: 245/245 (evaluable: True)
- PB-5 unsat arm 1 in R_66: 999/999; rank distribution {2278: 999}
- PB-6 / PC-3 regime-A T_strict retention_family (D = 4): 0
- PC-1 K_rank_hull vs dim W (D = 4): U1: 18/18; U2: 18/18; U3: 18/18; S1: 18/18; S2: 18/18; modal: 18/18
- PC-2 TS1R (F-S3, D = 4): m = 15, o = 0, P = 1.0, RR-4: SUPPORTED
- PB-7 regime-B pruned dense bytes (maximizing ref U1): 15567852 (full 22388184); saving_strict 40.94
- TS2G delta tail: {'min_delta_unsat_F-S3': 62, 'threshold_2^(l+1)-2': 62, 'n_below': 0, 'n': 999, 'fraction_below': 0.0, 'TS2G_falsified_(>1%)': False}

## Coordinator prior (a)-(g): observed items

Reported as the observed quantity beside each prior item; whether an item is 'overturned' is stated only where the prior names a checkable outcome.
- n17-l6: (a) C-DELTA pass True, C-RANKB pass True; (b) DB-2 DOES NOT DECIDE AT THIS D; (c) DB-1 STABLE; (d) DB-3 CONSISTENT; (e) DB-5 NOT EVALUABLE; (f) DB-6 CONTRAST CONFIRMED; (g) DB-7 P-GPU NOT SUPPORTED AT THIS CELL
- n19-l6: (a) C-DELTA pass True, C-RANKB pass True; (b) DB-2 DOES NOT DECIDE AT THIS D; (c) DB-1 STABLE; (d) DB-3 CONSISTENT; (e) DB-5 NOT EVALUABLE; (f) DB-6 CONTRAST CONFIRMED; (g) DB-7 P-GPU NOT SUPPORTED AT THIS CELL
- n17-l5: (a) C-DELTA pass True, C-RANKB pass True; (b) DB-2 DECIDES; (c) DB-1 STABLE; (d) DB-3 CONSISTENT; (e) DB-5 E3 HOLDS; (f) DB-6 CONTRAST CONFIRMED; (g) DB-7 P-GPU (STRICT REPLAY) SURVIVES IN REGIME B AT THIS CELL
- n19-l5: (a) C-DELTA pass True, C-RANKB pass True; (b) DB-2 DECIDES; (c) DB-1 STABLE; (d) DB-3 CONSISTENT; (e) DB-5 E3 HOLDS; (f) DB-6 CONTRAST CONFIRMED; (g) DB-7 P-GPU (STRICT REPLAY) SURVIVES IN REGIME B AT THIS CELL

## Instrument checks (M5)

- C-SELF: True
- C-FIX: True
- C-PROV: True
- C-DET: True
- C-PILOT: False
- PS0prime_verifier: True
- n17-l6: C-ORACLE True, C-WIT True, C-DELTA True, C-RANKB True, C-BREAK True, C-REPLAYB True, C-CLASS True, C-12_nulls_Lemma_B-S True, C-AFF True, C-FORMS True, C-SURV True, C-HZERO True, C-TR True, C-PASS True, C-REV True, C-PROPS True, nesting True, C-NULLS True
- n19-l6: C-ORACLE True, C-WIT True, C-DELTA True, C-RANKB True, C-BREAK True, C-REPLAYB True, C-CLASS True, C-12_nulls_Lemma_B-S True, C-AFF True, C-FORMS True, C-SURV True, C-HZERO True, C-TR True, C-PASS True, C-REV True, C-PROPS True, nesting True, C-NULLS True
- n17-l5: C-ORACLE True, C-WIT True, C-DELTA True, C-RANKB True, C-BREAK True, C-REPLAYB True, C-CLASS True, C-12_nulls_Lemma_B-S True, C-AFF True, C-FORMS True, C-SURV True, C-HZERO True, C-TR True, C-PASS True, C-REV True, C-PROPS True, nesting True, C-NULLS True
- n19-l5: C-ORACLE True, C-WIT True, C-DELTA True, C-RANKB True, C-BREAK True, C-REPLAYB True, C-CLASS True, C-12_nulls_Lemma_B-S True, C-AFF True, C-FORMS True, C-SURV True, C-HZERO True, C-TR True, C-PASS True, C-REV True, C-PROPS True, nesting True, C-NULLS True

Every failure is listed verbatim in instrument-checks.json. Deviations and interpretations: implementation.md and trial-plan-v1.json (interpretations).
