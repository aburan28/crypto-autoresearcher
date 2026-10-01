# Run report: RUN-CERTBIN-6d92b5 (EXP-CERTBIN-3f06d1, specification version 1)

Generated mechanically by phase 9 of `experiments/EXP-CERTBIN-3f06d1/impl/driver.py`. Every line is an observation or the mechanical application of a frozen rule. It declares no hypothesis or heuristic supported, refuted, replicated in the official sense, or closed; RR verdict strings are the frozen rule labels. That judgement belongs to the Reviewer and the Coordinator.

**Run validity status:** `completed_valid`.

## Claim tier and scope (verbatim from the specification)

- claim_tier: toy
- statement: Replication at n = 17 (f = t^17 + t^3 + 1), m = 2, l = 9, D in {3, 4}, with the Stage-1 fixed-shape Macaulay elimination, at three cells: R1 (new random ordinary curve, h = 2, polynomial V), R2 (new random ordinary curve, h = 4, polynomial V), R3 (Stage-1 curve A = 97044, B = 126251 with a uniformly random 9-dimensional V).
- sota_delta: zero on every ECDLP cost axis
- dominated_by: Parallel Pollard rho with the negation map (about 160 group operations at q near 2^15). Per attempt at m = 2: oracle A (2^9 = 512 quadratic root-findings), which decides satisfiability and returns the solutions, dominates the D = 4 Macaulay solve (OBJ-9). FES GPU exhaustive search (KN-LIT-287) and WDSat not compared.
- certificate_kind: unsatisfiability_certificate (instrument only; PS0')
- affected_vs_safe: No deployed or standardized curve is touched or affected.

Tested parameters: n = 17 (F_2[t]/(t^17 + t^3 + 1)), m = 2, l = 9, D in {3, 4}, the Stage-1 fixed-shape Macaulay elimination (declared row order, descending degrevlex columns, constant last, smallest-original-row pivot rule), cells R1, R2, R3 below. Nothing is claimed for other n, other curves or V, other orders or pivot rules, regime B, or any deployed curve.

## Cells

| cell | A | B | #E | h | q | V | dim W (F-S3 hull) | 0 in H | C-TR |
|---|---|---|---|---|---|---|---|---|---|
| R1 | 32835 | 114224 | 130538 | 2 | 65269 | polynomial | 16 | False | FAIL (data) |
| R2 | 75036 | 36745 | 130868 | 4 | 32717 | polynomial | 16 | True | FAIL (data) |
| R3 | 97044 | 126251 | 130412 | 4 | 32603 | random RREF | 16 | True | FAIL (data) |

## Arm sizes (non-degenerate) and UNDERPOWERED flags (SR-3), D = 4

| cell | family | unsat | sat | degenerate | flags |
|---|---|---|---|---|---|
| R1 | F-S3 | 379 | 618 | 3 | - |
| R1 | F-S3-REV | 94 | 105 | 1 | UNDERPOWERED unsat |
| R1 | F-PLANT | 0 | 200 | 0 | UNDERPOWERED unsat |
| R1 | F-RANDX | 372 | 623 | 5 | - |
| R1 | F-AFF-1 | 144 | 853 | 3 | - |
| R1 | F-NULLF2 | 144 | 856 | 0 | - |
| R2 | F-S3 | 308 | 687 | 5 | - |
| R2 | F-S3-REV | 58 | 142 | 0 | UNDERPOWERED unsat |
| R2 | F-PLANT | 0 | 200 | 0 | UNDERPOWERED unsat |
| R2 | F-RANDX | 354 | 642 | 4 | - |
| R2 | F-AFF-1 | 142 | 853 | 5 | - |
| R2 | F-NULLF2 | 139 | 861 | 0 | - |
| R3 | F-S3 | 409 | 587 | 4 | - |
| R3 | F-S3-REV | 89 | 110 | 1 | UNDERPOWERED unsat |
| R3 | F-PLANT | 0 | 200 | 0 | UNDERPOWERED unsat |
| R3 | F-RANDX | 358 | 637 | 5 | - |
| R3 | F-AFF-1 | 122 | 874 | 4 | - |
| R3 | F-NULLF2 | 143 | 857 | 0 | - |

## Primary readings per cell (F-S3, D = 4)

### R1

- M1 (T_strict unsat retention): U1 0/379 CP95 [0.0000, 0.0097]; U2 0/379 CP95 [0.0000, 0.0097]; U3 0/379 CP95 [0.0000, 0.0097]; modal 0/334 CP95 [0.0000, 0.0110]
- M1f median f_div (unsat, sat): U1 (0.000374, 0); U2 (0, 0); U3 (0, 0); S1 (0.000375, 0); S2 (0, 0); modal (0, 0)
- M1k (K_rank / K_rank_hull / dim W / dim Sigma_H): U1 17/16/16/0; U2 17/16/16/0; U3 17/16/16/0; S1 17/16/16/0; S2 17/16/16/0; modal 17/16/16/0
- M2R TS1R: m = 20, o = 0, P[Bin(m, 0.001) >= o] = 1 (log10 0); n_rep = 39, all h = 0: True
- M-R4: F-S3 unsat 1 in R_4 281/379 = 0.7414 CP95 [0.6942, 0.7848]; nulls: F-AFF-1 0/144 CP95 [0.0000, 0.0253]; F-NULLF2 0/144 CP95 [0.0000, 0.0253]
- x(2E) split (F-RANDX unsat, D = 4): x2E 62/78; xE_not_2E 59/93; twist 132/201; exact one-sided Fisher p = 0.009092
- M3: rule (2) zero, value 0
- **RR-1** [R1; F-S3, T_strict, D = 4]: DIRECTION REPLICATES
- **RR-2** [R1; F-S3, D = 4]: HULL RANK FULL
- **RR-3** [R1; F-S3, T_strict (f_div), D = 4]: EARLY DIVERGENCE REPLICATES
- **RR-4** [R1; F-S3, D = 4]: SUPPORTED
- **RR-5** [R1; F-S3, D = 4]: LOWER; nulls: NULLS CLEAN
- **RR-6** [R1; F-RANDX (unsat arm), D = 4]: MODULATION REPLICATES
- **RR-7** [R1; F-S3, T_strict, D = 4]: E2 FALSIFIED
- **RR-8**: ALL CONTROLS PASS

### R2

- M1 (T_strict unsat retention): U1 0/308 CP95 [0.0000, 0.0119]; U2 0/308 CP95 [0.0000, 0.0119]; U3 0/308 CP95 [0.0000, 0.0119]; modal 0/283 CP95 [0.0000, 0.0130]
- M1f median f_div (unsat, sat): U1 (0, 0); U2 (0, 0); U3 (0, 0); S1 (0.000374, 0.000374); S2 (0, 0); modal (0, 0.000374)
- M1k (K_rank / K_rank_hull / dim W / dim Sigma_H): U1 17/16/16/0; U2 17/16/16/0; U3 17/16/16/0; S1 17/16/16/0; S2 17/16/16/0; modal 17/16/16/0
- M2R TS1R: m = 24, o = 0, P[Bin(m, 0.001) >= o] = 1 (log10 0); n_rep = 181, all h = 0: True
- M-R4: F-S3 unsat 1 in R_4 262/308 = 0.8506 CP95 [0.8059, 0.8885]; nulls: F-AFF-1 0/142 CP95 [0.0000, 0.0256]; F-NULLF2 0/139 CP95 [0.0000, 0.0262]
- x(2E) split (F-RANDX unsat, D = 4): x2E 63/78; xE_not_2E 39/74; twist 144/202; exact one-sided Fisher p = 0.008938
- M3: rule (1) not_estimable, value n/a
- **RR-1** [R2; F-S3, T_strict, D = 4]: DIRECTION REPLICATES
- **RR-2** [R2; F-S3, D = 4]: HULL RANK FULL
- **RR-3** [R2; F-S3, T_strict (f_div), D = 4]: EARLY DIVERGENCE REPLICATES
- **RR-4** [R2; F-S3, D = 4]: SUPPORTED
- **RR-5** [R2; F-S3, D = 4]: REPLICATES; nulls: NULLS CLEAN
- **RR-6** [R2; F-RANDX (unsat arm), D = 4]: MODULATION REPLICATES
- **RR-7** [R2; F-S3, T_strict, D = 4]: E2 FALSIFIED
- **RR-8**: ALL CONTROLS PASS

### R3

- M1 (T_strict unsat retention): U1 0/409 CP95 [0.0000, 0.0090]; U2 0/409 CP95 [0.0000, 0.0090]; U3 0/409 CP95 [0.0000, 0.0090]; modal 0/367 CP95 [0.0000, 0.0100]
- M1f median f_div (unsat, sat): U1 (0, 0); U2 (0, 0); U3 (0, 0); S1 (0, 0); S2 (0, 0); modal (0, 0)
- M1k (K_rank / K_rank_hull / dim W / dim Sigma_H): U1 17/16/16/0; U2 17/16/16/0; U3 17/16/16/0; S1 17/16/16/0; S2 17/16/16/0; modal 17/16/16/0
- M2R TS1R: m = 22, o = 0, P[Bin(m, 0.001) >= o] = 1 (log10 0); n_rep = 8, all h = 0: True
- M-R4: F-S3 unsat 1 in R_4 0/409 = 0 CP95 [0.0000, 0.0090]; nulls: F-AFF-1 0/122 CP95 [0.0000, 0.0298]; F-NULLF2 0/143 CP95 [0.0000, 0.0255]
- x(2E) split (F-RANDX unsat, D = 4): x2E 0/93; xE_not_2E 0/93; twist 0/172; exact one-sided Fisher p = 1
- M3: rule (1) not_estimable, value n/a
- **RR-1** [R3; F-S3, T_strict, D = 4]: DIRECTION REPLICATES
- **RR-2** [R3; F-S3, D = 4]: HULL RANK FULL
- **RR-3** [R3; F-S3, T_strict (f_div), D = 4]: EARLY DIVERGENCE REPLICATES
- **RR-4** [R3; F-S3, D = 4]: SUPPORTED
- **RR-5** [R3; F-S3, D = 4]: LOWER; nulls: NULLS CLEAN
- **RR-6** [R3; F-RANDX (unsat arm), D = 4]: ABSENT
- **RR-7** [R3; F-S3, T_strict, D = 4]: E2 FALSIFIED
- **RR-8**: ALL CONTROLS PASS

## Composite (RR-9) and primary set (RR-10)

- H-CERTBIN-a73f1c: REPLICATED (direction and obstruction)
- H-CERTBIN-5e71c9 C2: RATE CURVE- OR V-DEPENDENT: R1 LOWER, R3 LOWER
- H-CERTBIN-7c3a18: KR1 {'R1': 'HULL RANK FULL', 'R2': 'HULL RANK FULL', 'R3': 'HULL RANK FULL'}; TS1R {'R1': 'SUPPORTED', 'R2': 'SUPPORTED', 'R3': 'SUPPORTED'}
- RR-10: primary = RR-1, RR-2, RR-3 and RR-5 at D = 4 on F-S3; everything else is secondary.

## Pre-registered prediction (formula) against the data

| cell | retention_family < 0.5 (pred. <= 0.01) | K_rank_hull = dim W all refs | median f_div <= 0.1 both arms | TS1R | 1-in-R_4 CP95 overlaps [0.799, 0.875] | null CP95 upper <= 0.05 | x(2E) Fisher p < 0.01 |
|---|---|---|---|---|---|---|---|
| R1 | 0 (< 0.5; <= 0.01) | HULL RANK FULL | EARLY DIVERGENCE REPLICATES | SUPPORTED | LOWER | NULLS CLEAN | MODULATION REPLICATES |
| R2 | 0 (< 0.5; <= 0.01) | HULL RANK FULL | EARLY DIVERGENCE REPLICATES | SUPPORTED | REPLICATES | NULLS CLEAN | MODULATION REPLICATES |
| R3 | 0 (< 0.5; <= 0.01) | HULL RANK FULL | EARLY DIVERGENCE REPLICATES | SUPPORTED | LOWER | NULLS CLEAN | ABSENT |

## Coordinator prior (a)-(e) against the data (mechanical readings)

- (a) RR-1 replicates at all three cells: held ({'R1': 'DIRECTION REPLICATES', 'R2': 'DIRECTION REPLICATES', 'R3': 'DIRECTION REPLICATES'})
- (b) RR-2 holds at all three cells: held ({'R1': 'HULL RANK FULL', 'R2': 'HULL RANK FULL', 'R3': 'HULL RANK FULL'})
- (c) TS1R SUPPORTED where evaluable: held ({'R1': 'SUPPORTED', 'R2': 'SUPPORTED', 'R3': 'SUPPORTED'}; m per cell: {'R1': 20, 'R2': 24, 'R3': 22})
- (d) R2 REPLICATES / R1 least certain / R3 either way: observed {'R1': 'LOWER', 'R2': 'REPLICATES', 'R3': 'LOWER'}
- (e) x(2E) modulation replicates at R2, less sure at R1: observed {'R1': 'MODULATION REPLICATES', 'R2': 'MODULATION REPLICATES', 'R3': 'ABSENT'}

## Instrument checks (M5)

Global: C-FIX: pass, C-SELF: pass, C-PROV: pass, C-NULLS_code_path: pass
- R1: C-ORACLE: pass, C-WIT: pass, C-AFF: pass, C-FORMS: pass, C-SURV: pass, C-HZERO: pass, C-TR: FAIL, C-DET: pass, C-PASS: pass, C-PROPS: pass, C-REV: pass, C-NULLS: pass, NESTING: pass, HASH_CONTENT: pass, REF_SELF_REPLAY: pass, C-SELF_cell: pass
- R2: C-ORACLE: pass, C-WIT: pass, C-AFF: pass, C-FORMS: pass, C-SURV: pass, C-HZERO: pass, C-TR: FAIL, C-DET: pass, C-PASS: pass, C-PROPS: pass, C-REV: pass, C-NULLS: pass, NESTING: pass, HASH_CONTENT: pass, REF_SELF_REPLAY: pass, C-SELF_cell: pass
- R3: C-ORACLE: pass, C-WIT: pass, C-AFF: pass, C-FORMS: pass, C-SURV: pass, C-HZERO: pass, C-TR: FAIL, C-DET: pass, C-PASS: pass, C-PROPS: pass, C-REV: pass, C-NULLS: pass, NESTING: pass, HASH_CONTENT: pass, REF_SELF_REPLAY: pass, C-SELF_cell: pass

Count of controls that can fail: ['C-FIX', 'C-SELF', 'C-PROV', 'C-ORACLE', 'C-WIT', 'C-AFF', 'C-FORMS', 'C-SURV', 'C-HZERO', 'C-TR (as data)', 'C-DET', 'C-PASS', 'C-PROPS', 'C-REV', 'C-NULLS'] (all declared controls; C-TR failure is data).

## Raw-result and cell-summary agreement

raw-result.json was recomputed from the written targets-<cell>-<family>.jsonl.gz and pivot-hazards-<cell>.json files by separate code and compared with cell-summary.json on 1008 primary-metric items: all agree.

