# EXP-ECDLP-612fb1 v2 STAGE 4v2 analysis run

Observations only. MEASURED numbers are counts/rates from the runs; MODELED numbers are the
frozen contract's formulas, quoted beside them and never mixed. No hypothesis-level conclusion
is drawn; gate verdicts are reported in the contract's own gate language only.

## Permanent negative fixture check (item g) -- MUST pass before any real-cell G1 verdict
- affine_xorshift: G1 verdict = **FAIL** (slope ok False, cutoff ok False [None-guarded], top-share ok False, static-below ok True)
- permutation: G1 verdict = **FAIL** (slope ok False, cutoff ok False [None-guarded], top-share ok False, static-below ok True)
- Both fixtures scored G1 FAIL, no exception: True
- The real-cell G1 verdicts below are therefore reportable as trustworthy per item (g).

## STAGE 0: a-scan (item h) -- reported before any STAGE 1v2/2v2 cell is interpreted
- seeds: [1, 2, 3, 4, 5]; a-grid: [0.0625, 0.125, 0.1875, 0.25, 0.3125, 0.375, 0.4375, 0.5, 0.625, 0.75, 0.875, 1]; r-grid: [2, 4, 8]
| a | rho_ORACLE(r=2) | rho_ORACLE(r=4) | rho_ORACLE(r=8) |
|---|---|---|---|
| 0.0625 | 0.3856 | 0.5585 | 0.6638 |
| 0.1250 | 0.4759 | 0.6671 | 0.7828 |
| 0.1875 | 0.5124 | 0.6781 | 0.8433 |
| 0.2500 | 0.5744 | 0.7033 | 0.8372 |
| 0.3125 | 0.6335 | 0.7510 | 0.8840 |
| 0.3750 | 0.6598 | 0.7765 | 0.9070 |
| 0.4375 | 0.6703 | 0.7934 | 0.9058 |
| 0.5000 | 0.6897 | 0.8014 | 0.9110 |
| 0.6250 | 0.7092 | 0.8234 | 0.9321 |
| 0.7500 | 0.7302 | 0.8483 | 0.9346 |
| 0.8750 | 0.7519 | 0.8629 | 0.9551 |
| 1.0000 | 0.7563 | 0.8805 | 0.9601 |

### F6_v2 ordering check: rho_ORACLE(a=1/4, r) < rho_ORACLE(a=1/2, r)
- r=2: rho_ORACLE(1/4)=0.5744 vs rho_ORACLE(1/2)=0.6897 -> holds: True
- r=4: rho_ORACLE(1/4)=0.7033 vs rho_ORACLE(1/2)=0.8014 -> holds: True
- r=8: rho_ORACLE(1/4)=0.8372 vs rho_ORACLE(1/2)=0.9110 -> holds: True


## Gates G2 and G3 per N (reported before that N's RESEL-L S1/F1 lines)
### 2^24: seeds [1, 2, 3, 4, 5]
- G2 fixture: MEASURED scaled main cost 1.705 vs PUBLISHED 1.79 +/- 0.18 -> within: True; G2 pass: True
- G3(0.65T) [BINDING]: 5/5 seeds pass (margins ['0.0301', '0.0338', '0.0049', '0.0247', '0.0166']) -> **PASS**
- G3(0.75T) [BINDING]: 5/5 seeds pass (margins ['0.0559', '0.0593', '0.0305', '0.0491', '0.0403']) -> **PASS**
### 2^30: seeds [1, 2, 3, 4, 5]
- G2 fixture: MEASURED scaled main cost 1.727 vs PUBLISHED 1.79 +/- 0.18 -> within: True; G2 pass: True
- G3(0.65T) [INFORMATIONAL]: 5/5 seeds pass (margins ['0.0439', '0.0215', '0.0508', '0.0317', '0.0229']) -> **PASS (informational)**
- G3(0.75T) [INFORMATIONAL]: 5/5 seeds pass (margins ['0.0698', '0.0532', '0.0723', '0.0649', '0.0601']) -> **PASS (informational)**

## Cell 2^24 (T=256, seeds [1, 2, 3, 4, 5], runs ['RUN-ECDLP-612fb1-v2-1v2-s1', 'RUN-ECDLP-612fb1-v2-1v2-s2', 'RUN-ECDLP-612fb1-v2-1v2-s3', 'RUN-ECDLP-612fb1-v2-1v2-s4', 'RUN-ECDLP-612fb1-v2-1v2-s5'])
- non-vacuity guard (item b): STATIC(T) eps_ss(8T)=0.7395 >= 0.5: True; gap to RHO = 0.7344 >= 0.30: True; HOLDS: True
### T_sel = 0.65T
- G3 (item a): PASS
- eps_ss(RESEL-L(0.65T)) - eps_ss(STATIC(T)) at 8T: -0.0008 [-0.0155, 0.0148]
- rho_T(8T): 0.6522; rho_ORACLE(this T_sel exact top share): 0.32096147537231445
- S1_v2: **MET**
- F1_v2: **does not fire**
- FRONTIER TUPLE (item d, headline discipline): T_sel/T=0.65, S_peak/T(bits)=881.0, P/sqrt(NT)=1.2286, L/target=333.11, eps_ss(8T)=0.7387, eps_cum(8T)=0.7078, early-batch penalty=0.0971
- CAP(2T,0.65T) retention (item f): S_peak_bits per seed [49152, 49152, 49152, 49152, 49152] (cap = 49152 bits); S_peak<=c every round all seeds: True; retention: 0.5
- S2_v2 (one-sided, item c): gain_ss(8T)=-0.1641 [-0.18203125, -0.14570312499999993]; RESEL-L gain=0.0809; perturbation/STATIC eps_ss = 0.2494061757719715; S2_v2 MET: **False**
### T_sel = 0.75T
- G3 (item a): PASS
- eps_ss(RESEL-L(0.75T)) - eps_ss(STATIC(T)) at 8T: 0.0324 [0.0164, 0.0465]
- rho_T(8T): 0.6522; rho_ORACLE(this T_sel exact top share): 0.3467709422111511
- S1_v2: **MET**
- F1_v2: **does not fire**
- FRONTIER TUPLE (item d, headline discipline): T_sel/T=0.75, S_peak/T(bits)=901.0, P/sqrt(NT)=1.2286, L/target=321.21, eps_ss(8T)=0.7719, eps_cum(8T)=0.7422, early-batch penalty=0.0578
- CAP(2T,0.75T) retention (item f): S_peak_bits per seed [49152, 49152, 49152, 49152, 49152] (cap = 49152 bits); S_peak<=c every round all seeds: True; retention: 1.096
- S2_v2 (one-sided, item c): gain_ss(8T)=-0.1727 [-0.19062500000000004, -0.154296875]; RESEL-L gain=0.0812; perturbation/STATIC eps_ss = 0.25000000000000006; S2_v2 MET: **False**

## Cell 2^30 (T=1024, seeds [1, 2, 3, 4, 5], runs ['RUN-ECDLP-612fb1-v2-2v2-s1', 'RUN-ECDLP-612fb1-v2-2v2-s2', 'RUN-ECDLP-612fb1-v2-2v2-s3', 'RUN-ECDLP-612fb1-v2-2v2-s4', 'RUN-ECDLP-612fb1-v2-2v2-s5'])
- non-vacuity guard (item b): STATIC(T) eps_ss(8T)=0.7451 >= 0.5: True; gap to RHO = 0.7441 >= 0.30: True; HOLDS: True
### T_sel = 0.65T
- G3 (item a): PASS (informational)
- eps_ss(RESEL-L(0.65T)) - eps_ss(STATIC(T)) at 8T: -0.0127 [-0.0192, -0.0033]
- rho_T(8T): 0.6864
- S1_v2: **NOT MET**
- F1_v2: **does not fire**
- FRONTIER TUPLE (item d, headline discipline): T_sel/T=0.65, S_peak/T(bits)=1004.5, P/sqrt(NT)=1.2599, L/target=1338.47, eps_ss(8T)=0.7324, eps_cum(8T)=0.7085, early-batch penalty=0.0757
- CAP(2T,0.65T) retention (item f): S_peak_bits per seed [221184, 221184, 221184, 221184, 221184] (cap = 221184 bits); S_peak<=c every round all seeds: True; retention: 1.138
- S2_v2 (one-sided, item c): gain_ss(8T)=-0.1697 [-0.17880859375000002, -0.16007136878416436]; RESEL-L gain=0.0631; perturbation/STATIC eps_ss = 0.2535745550043769; S2_v2 MET: **False**
### T_sel = 0.75T
- G3 (item a): PASS (informational)
- eps_ss(RESEL-L(0.75T)) - eps_ss(STATIC(T)) at 8T: 0.0206 [0.0139, 0.0290]
- rho_T(8T): 0.6864
- S1_v2: **MET**
- F1_v2: **does not fire**
- FRONTIER TUPLE (item d, headline discipline): T_sel/T=0.75, S_peak/T(bits)=1029.5, P/sqrt(NT)=1.2599, L/target=1295.18, eps_ss(8T)=0.7657, eps_cum(8T)=0.7391, early-batch penalty=0.0501
- CAP(2T,0.75T) retention (item f): S_peak_bits per seed [221184, 221184, 221184, 221184, 221184] (cap = 221184 bits); S_peak<=c every round all seeds: True; retention: 0.896
- S2_v2 (one-sided, item c): gain_ss(8T)=-0.1593 [-0.1677883811126129, -0.14967045457432251]; RESEL-L gain=0.0679; perturbation/STATIC eps_ss = 0.22823957458718167; S2_v2 MET: **False**

