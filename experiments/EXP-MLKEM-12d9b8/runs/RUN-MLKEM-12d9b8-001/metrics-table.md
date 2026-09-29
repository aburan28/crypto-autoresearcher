# Metrics table (primary and secondary), per specification.yaml `metrics`

## Primary metric: n_pinned

See `source-pin-note.md`. Working substitution `n := k_mlkem*256`: ML-KEM-512 -> n=512, ML-KEM-768 -> n=768, ML-KEM-1024 -> n=1024.

## Primary metric: Q_table (exact integers, Q = k_mlkem * (k_mlkem*256)^(c+1))

| level | k_mlkem | n | c | Q (exact) | Q digits |
|---|---|---|---|---|---|
| ML-KEM-512 | 2 | 512 | 12 | 332306998946228968225951765070086144 | 36 |
| ML-KEM-512 | 2 | 512 | 13 | 170141183460469231731687303715884105728 | 39 |
| ML-KEM-512 | 2 | 512 | 15 | 44601490397061246283071436545296723011960832 | 44 |
| ML-KEM-512 | 2 | 512 | 20 | 1569275433846670190958947355801916604025588861116008628224 | 58 |
| ML-KEM-768 | 3 | 768 | 12 | 97010136379568226435956560536224661504 | 38 |
| ML-KEM-768 | 3 | 768 | 13 | 74503784739508397902814638491820540035072 | 41 |
| ML-KEM-768 | 3 | 768 | 15 | 43944120330195801284629741333799558205646307328 | 47 |
| ML-KEM-768 | 3 | 768 | 20 | 11741048319931434018289122544363230931132758477212879425634304 | 62 |
| ML-KEM-1024 | 4 | 1024 | 12 | 5444517870735015415413993718908291383296 | 40 |
| ML-KEM-1024 | 4 | 1024 | 13 | 5575186299632655785383929568162090376495104 | 43 |
| ML-KEM-1024 | 4 | 1024 | 15 | 5846006549323611672814739330865132078623730171904 | 49 |
| ML-KEM-1024 | 4 | 1024 | 20 | 6582018229284824168619876730229402019930943462534319453394436096 | 64 |

## Primary metric: variance_formula, m=1/m=2 baseline checks

Var(sum_i c_i*e_i) = sum_i c_i^2 * Var(e_i), e_i ~ CBD(eta) independent; Var(CBD(eta)) = eta/2 exact.

| level | eta (eta1/eta2) | m=1 variance | m=1 expected (eta/2) | pass | m=2 (unit coeffs) variance | m=2 expected (eta) | pass |
|---|---|---|---|---|---|---|---|
| ML-KEM-512 | eta1=3 | 3/2 | 3/2 | True | 3 | 3 | True |
| ML-KEM-512 | eta2=2 | 1 | 1 | True | 2 | 2 | True |
| ML-KEM-768 | eta1=2 | 1 | 1 | True | 2 | 2 | True |
| ML-KEM-768 | eta2=2 | 1 | 1 | True | 2 | 2 | True |
| ML-KEM-1024 | eta1=2 | 1 | 1 | True | 2 | 2 | True |
| ML-KEM-1024 | eta2=2 | 1 | 1 | True | 2 | 2 | True |

**stage1_all_checks_pass: True** (BASELINE-EMBEDDING CONTROL passes at every level and both eta values; per stopping_rules, the run would have stopped at F1 had any check failed.)

## Primary metric: combinatorial_ceiling (exact, (2B+1)^k_mlkem), Extreme-B check per MLKEM-CHG-2 (B in {1, q}, q=3329, NOT searched beyond q)

| level | k_mlkem | q | ceiling at B=1 | ceiling at B=q=3329 |
|---|---|---|---|---|
| ML-KEM-512 | 2 | 3329 | 9 | 44342281 |
| ML-KEM-768 | 3 | 3329 | 27 | 295275249179 |
| ML-KEM-1024 | 4 | 3329 | 81 | 1966237884282961 |

## Primary metric: realizability_verdict (three-way, per level, per swept c), exact numeric margin at B=q (operative ceiling per MLKEM-CHG-2)

| level | c | Q | ceiling(B=1) | ceiling(B=q) | verdict on combinatorial axis | margin (ceiling(B=q) - Q) | approx orders-of-magnitude shortfall |
|---|---|---|---|---|---|---|---|
| ML-KEM-512 | 12 | 332306998946228968225951765070086144 | 9 | 44342281 | UNREALIZABLE | -332306998946228968225951765025743863 | 28 |
| ML-KEM-512 | 13 | 170141183460469231731687303715884105728 | 9 | 44342281 | UNREALIZABLE | -170141183460469231731687303715839763447 | 31 |
| ML-KEM-512 | 15 | 44601490397061246283071436545296723011960832 | 9 | 44342281 | UNREALIZABLE | -44601490397061246283071436545296722967618551 | 36 |
| ML-KEM-512 | 20 | 1569275433846670190958947355801916604025588861116008628224 | 9 | 44342281 | UNREALIZABLE | -1569275433846670190958947355801916604025588861115964285943 | 50 |
| ML-KEM-768 | 12 | 97010136379568226435956560536224661504 | 27 | 295275249179 | UNREALIZABLE | -97010136379568226435956560240949412325 | 26 |
| ML-KEM-768 | 13 | 74503784739508397902814638491820540035072 | 27 | 295275249179 | UNREALIZABLE | -74503784739508397902814638491525264785893 | 29 |
| ML-KEM-768 | 15 | 43944120330195801284629741333799558205646307328 | 27 | 295275249179 | UNREALIZABLE | -43944120330195801284629741333799557910371058149 | 35 |
| ML-KEM-768 | 20 | 11741048319931434018289122544363230931132758477212879425634304 | 27 | 295275249179 | UNREALIZABLE | -11741048319931434018289122544363230931132758477212584150385125 | 50 |
| ML-KEM-1024 | 12 | 5444517870735015415413993718908291383296 | 81 | 1966237884282961 | UNREALIZABLE | -5444517870735015415413991752670407100335 | 24 |
| ML-KEM-1024 | 13 | 5575186299632655785383929568162090376495104 | 81 | 1966237884282961 | UNREALIZABLE | -5575186299632655785383929566195852492212143 | 27 |
| ML-KEM-1024 | 15 | 5846006549323611672814739330865132078623730171904 | 81 | 1966237884282961 | UNREALIZABLE | -5846006549323611672814739330865130112385845888943 | 33 |
| ML-KEM-1024 | 20 | 6582018229284824168619876730229402019930943462534319453394436096 | 81 | 1966237884282961 | UNREALIZABLE | -6582018229284824168619876730229402019930943462532353215510153135 | 48 |

## Overall verdict by level, robustness across full c sweep {12,13,15,20}

| level | verdicts across c sweep | robust single verdict |
|---|---|---|
| ML-KEM-512 | {'12': 'UNREALIZABLE', '13': 'UNREALIZABLE', '15': 'UNREALIZABLE', '20': 'UNREALIZABLE'} | UNREALIZABLE |
| ML-KEM-768 | {'12': 'UNREALIZABLE', '13': 'UNREALIZABLE', '15': 'UNREALIZABLE', '20': 'UNREALIZABLE'} | UNREALIZABLE |
| ML-KEM-1024 | {'12': 'UNREALIZABLE', '13': 'UNREALIZABLE', '15': 'UNREALIZABLE', '20': 'UNREALIZABLE'} | UNREALIZABLE |

**This is the realizability_verdict on the combinatorial-ceiling axis only (independent of stage 0, per MLKEM-CHG-2's own text: "THIS SPECIFIC SUB-CLAIM ... does NOT require stage 0's noise-variance-to-faulty-rate conversion chain to resolve").** Because stage 0 reports NOT COMPUTED (see stage0-disposition.md), the full three-way verdict specification.yaml's success_criterion defines (which is conditioned on stage 0 for the faulty-rate half of outcome (a)/(b)) is: outcomes (a) REALIZABLE and (b) UNREALIZABLE both require stage 0 to be discharged to be asserted in full per success_criterion's own text ("the combinatorial ceiling and, IF stage 0 is discharged, the effective faulty rate both stay within budget" / "fall short"); stage 0 is NOT discharged. The run therefore reports outcome (c): stages 1-3 complete in full (shown above), and the combinatorial-ceiling axis alone already answers UNREALIZABLE at every level and every swept c (astronomically, by 24-50 orders of magnitude at the operative B=q ceiling) -- but the STAGE-0-DEPENDENT faulty-rate half of the three-way verdict is explicitly "NOT COMPUTED: conversion chain unavailable from available sources" per stage0-disposition.md, matching the contract's own outcome-(c) success criterion exactly.


## Secondary metric: trivial_floor_check

The formula-level claim (Q <= k_mlkem => trivially realizable, by taking m=k_mlkem real rows directly with unit coefficients, no combination search needed) holds by construction for every k_mlkem. Within this run's swept c range {12,13,15,20}, Q always vastly exceeds k_mlkem (Q's smallest value, ML-KEM-512 c=12, already has 36 digits vs k_mlkem=2), so the degenerate floor case does not arise for any swept c -- this is reported honestly rather than defaulted, per the control's own "sanity check on the formula's low end" framing.


## Secondary metric: symbol_collision_audit

PASS. See `symbol-collision-audit.md`.


## Secondary metric: stage_0_disposition

NOT COMPUTED: conversion chain unavailable from available sources. See `stage0-disposition.md` for the genuine attempt made and the four sources checked.

