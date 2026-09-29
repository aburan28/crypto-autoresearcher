# EXP-ECDLP-612fb1 analysis run: CI tables over stages 1,2,3,G

Observations only. MEASURED numbers are counts/rates from the runs; MODELED numbers are the
frozen contract's formulas and published references, quoted beside them and never mixed.

## Gates (reported before any arm)
### 2^20,a=1/2: seeds [1, 2, 3, 4, 5]
- G2 fixture (reported only): MEASURED scaled main cost 1.771 (per seed [1.711, 1.888, 1.579, 1.895, 1.818]) vs PUBLISHED 1.62 +/- 0.16 -> within: True; MEASURED P/sqrt(NT) mean 2.291 vs range None; G2 pass: True
- G1 (GATED): slope(log grid) per seed [-0.62, -0.608, -0.619, -0.616, -0.593] [MODELED Borel under same estimator [-0.613, -0.613, -0.613, -0.613, -0.613]]; within 0.15 of -0.5 all seeds: True; cutoff n_c theta^2/2 [1.548, 0.916, 1.3, 1.157, 0.916] in [0.5,2]: True; top-T share / C_max [0.999, 0.927, 1.022, 0.965, 0.935] in [0.85,1.05]: True; STATIC(T) below top share: True; largest basin in Borel band: [True, True, True, True, True]; G1 literal (all four): True
### 2^20,a=1/4: seeds [1, 2, 3, 4, 5]
- G2 fixture (reported only): MEASURED scaled main cost 1.843 (per seed [1.779, 2.292, 1.587, 1.747, 1.915]) vs PUBLISHED 1.79 +/- 0.18 -> within: True; MEASURED P/sqrt(NT) mean 1.338 vs range [1.05, 1.4]; G2 pass: True
- G1 (GATED): slope(log grid) per seed [-0.637, -0.632, -0.636, -0.636, -0.617] [MODELED Borel under same estimator [-0.63, -0.63, -0.63, -0.63, -0.63]]; within 0.15 of -0.5 all seeds: True; cutoff n_c theta^2/2 [1.03, 1.091, 1.157, 1.3, 0.971] in [0.5,2]: True; top-T share / C_max [1.004, 0.928, 0.997, 0.992, 0.944] in [0.85,1.05]: True; STATIC(T) below top share: True; largest basin in Borel band: [True, True, True, True, True]; G1 literal (all four): True
### 2^24,a=1/2: seeds [1, 2, 3, 4, 5]
- G2 fixture (GATED): MEASURED scaled main cost 1.577 (per seed [1.603, 1.575, 1.538, 1.612, 1.556]) vs PUBLISHED 1.62 +/- 0.16 -> within: True; MEASURED P/sqrt(NT) mean 2.150 vs range None; G2 pass: True
- G1 (information): slope(log grid) per seed [-0.587, -0.58, -0.587, -0.585, -0.587] [MODELED Borel under same estimator [-0.587, -0.587, -0.587, -0.587, -0.587]]; within 0.15 of -0.5 all seeds: True; cutoff n_c theta^2/2 [1.157, 0.864, 0.971, 1.03, 1.03] in [0.5,2]: True; top-T share / C_max [1.014, 0.97, 1.01, 1.001, 0.99] in [0.85,1.05]: True; STATIC(T) below top share: True; largest basin in Borel band: [True, True, True, True, True]; G1 literal (all four): True
### 2^24,a=1/4: seeds [1, 2, 3, 4, 5]
- G2 fixture (GATED): MEASURED scaled main cost 1.705 (per seed [1.728, 1.821, 1.613, 1.695, 1.687]) vs PUBLISHED 1.79 +/- 0.18 -> within: True; MEASURED P/sqrt(NT) mean 1.243 vs range [1.05, 1.4]; G2 pass: True
- G1 (information): slope(log grid) per seed [-0.602, -0.596, -0.599, -0.599, -0.597] [MODELED Borel under same estimator [-0.599, -0.599, -0.599, -0.599, -0.599]]; within 0.15 of -0.5 all seeds: True; cutoff n_c theta^2/2 [1.091, 0.864, 1.03, 1.091, 0.916] in [0.5,2]: True; top-T share / C_max [1.028, 0.968, 1.0, 1.034, 0.982] in [0.85,1.05]: True; STATIC(T) below top share: True; largest basin in Borel band: [True, True, True, True, True]; G1 literal (all four): True
### 2^30,a=1/2: seeds [1, 2, 3, 4, 5]
- G2 fixture (GATED): MEASURED scaled main cost 1.611 (per seed [1.594, 1.669, 1.579, 1.623, 1.595]) vs PUBLISHED 1.62 +/- 0.16 -> within: True; MEASURED P/sqrt(NT) mean 2.116 vs range None; G2 pass: True
### 2^30,a=1/4: seeds [1, 2, 3, 4, 5]
- G2 fixture (GATED): MEASURED scaled main cost 1.727 (per seed [1.714, 1.789, 1.738, 1.707, 1.69]) vs PUBLISHED 1.79 +/- 0.18 -> within: True; MEASURED P/sqrt(NT) mean 1.246 vs range [1.05, 1.4]; G2 pass: True

## Cell 2^20,a=1/2 (T = 64, seeds [1, 2, 3, 4, 5], runs ['RUN-ECDLP-612fb1-006', 'RUN-ECDLP-612fb1-007', 'RUN-ECDLP-612fb1-008', 'RUN-ECDLP-612fb1-009', 'RUN-ECDLP-612fb1-010'])
| quantity | MEASURED point | 95% BCa CI | FROZEN prediction |
|---|---|---|---|
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=4T | -0.0844 | [-0.1094, -0.0578] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(4T) | 0.803 | [0.699, 0.929] | <= 0.75 (CI excluding 1.0) |
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=8T | -0.0844 | [-0.1078, -0.0500] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(8T) | 0.744 | [0.659, 0.850] | [0.45, 0.65] |
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=16T | -0.0625 | [-0.0938, -0.0422] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(16T) | 0.706 | [0.625, 0.816] | <= 0.6 |
| NULL-A(T) gain at 8T | -0.0969 | [-0.1266, -0.0703] | within CI of zero every round: False |
| NULL-A(T/2) gain at 8T | -0.1297 | [-0.1656, -0.1000] | within CI of zero every round: False |
| PHI(0.0) gain at 8T | 0.0000 | [0.0000, 0.0000] | non-decreasing, gain(0)=0 |
| PHI(0.1) gain at 8T | 0.0188 | [0.0062, 0.0406] | non-decreasing, gain(0)=0 |
| PHI(0.25) gain at 8T | 0.0391 | [0.0109, 0.0578] | non-decreasing, gain(0)=0 |
| PHI(0.5) gain at 8T | 0.0500 | [0.0188, 0.0703] | non-decreasing, gain(0)=0 |
| PHI(1.0) gain at 8T | 0.0469 | [0.0172, 0.0719] | non-decreasing, gain(0)=0 |
| gain(RESEL-L, T) at r=2 | 0.0375 | [0.0172, 0.0609] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T) at r=4 | 0.0109 | [-0.0047, 0.0312] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T) at r=8 | 0.0062 | [-0.0109, 0.0156] | strictly decreasing; gain(8) <= 0.03 |
| UPPER - LOWER (T) at 8T | 0.0141 | [0.0047, 0.0311] | < 0.05 (S6); < 0.02 after round 4 |
| gain(RESEL-L, T/2) at r=2 | 0.0469 | [0.0203, 0.0703] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T/2) at r=4 | 0.0187 | [0.0016, 0.0359] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T/2) at r=8 | -0.0016 | [-0.0125, 0.0109] | strictly decreasing; gain(8) <= 0.03 |
| UPPER - LOWER (T/2) at 8T | 0.0156 | [-0.0016, 0.0344] | < 0.05 (S6); < 0.02 after round 4 |
| early-batch penalty (first 10% of 8T) | 0.1412 | [0.1020, 0.1843] | >= 0.08 |
| U_ss (margin 0.02) | > 16T | per seed ['> 16T', '> 16T', '> 16T', '> 16T', '> 16T'] | [4T, 10T] |
| U* (margin 0.02) | > 16T | per seed ['> 16T', '> 16T', '> 16T', '> 16T', '> 16T'] | [8T, 16T] or > 16T |
| STATIC2T single-walk hit rate | 0.4906 | - | MODELED 0.32 |
| STATIC(T) single-walk hit rate | 0.4301 | - | about 0.27 (a=1/4), about 0.42 (a=1/2) |
| RESEL-L(T) hit rate first -> last round | 0.4094 -> 0.5126 | - | to within 0.03 of top-T share (MODELED C_max 0.525) |
| RHO eps_cum(16T) | 0.0412 | - | < 0.02 |
| CAP(4T,T) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |
| CAP(2T,T) retention | 0.958 | - | 4T >= 80%, 2T >= 60% |
| CAP(4T,T/2) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |
| CAP(2T,T/2) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |

- Round-0 identity all arms all seeds: True; NULL-B / PHI(0) bit identity: {'RUN-ECDLP-612fb1-006': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-007': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-008': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-009': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-010': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}}
- S4 exceedance: RESEL-L(T/2): exact exceedance False (max exact-oracle -0.0064, max sampled-oracle 0.1003); RESEL-L(T): exact exceedance False (max exact-oracle -0.0091, max sampled-oracle 0.1134); RESEL-U(T): exact exceedance False (max exact-oracle -0.0053, max sampled-oracle 0.1058)

## Cell 2^20,a=1/4 (T = 64, seeds [1, 2, 3, 4, 5], runs ['RUN-ECDLP-612fb1-001', 'RUN-ECDLP-612fb1-002', 'RUN-ECDLP-612fb1-003', 'RUN-ECDLP-612fb1-004', 'RUN-ECDLP-612fb1-005'])
| quantity | MEASURED point | 95% BCa CI | FROZEN prediction |
|---|---|---|---|
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=4T | -0.0938 | [-0.1281, -0.0641] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(4T) | 0.736 | [0.633, 0.847] | <= 0.75 (CI excluding 1.0) |
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=8T | -0.0641 | [-0.0938, -0.0219] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(8T) | 0.666 | [0.566, 0.750] | [0.45, 0.65] |
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=16T | -0.0656 | [-0.1000, -0.0312] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(16T) | 0.645 | [0.569, 0.726] | <= 0.6 |
| NULL-A(T) gain at 8T | -0.1344 | [-0.1734, -0.1062] | within CI of zero every round: False |
| NULL-A(T/2) gain at 8T | -0.1422 | [-0.1797, -0.1078] | within CI of zero every round: False |
| PHI(0.0) gain at 8T | 0.0000 | [0.0000, 0.0000] | non-decreasing, gain(0)=0 |
| PHI(0.1) gain at 8T | -0.0125 | [-0.0359, 0.0221] | non-decreasing, gain(0)=0 |
| PHI(0.25) gain at 8T | 0.0547 | [0.0234, 0.0828] | non-decreasing, gain(0)=0 |
| PHI(0.5) gain at 8T | 0.0641 | [0.0344, 0.0961] | non-decreasing, gain(0)=0 |
| PHI(1.0) gain at 8T | 0.0875 | [0.0484, 0.1156] | non-decreasing, gain(0)=0 |
| gain(RESEL-L, T) at r=2 | 0.0750 | [0.0453, 0.1063] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T) at r=4 | 0.0203 | [-0.0016, 0.0422] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T) at r=8 | 0.0047 | [-0.0141, 0.0188] | strictly decreasing; gain(8) <= 0.03 |
| UPPER - LOWER (T) at 8T | 0.0312 | [0.0047, 0.0516] | < 0.05 (S6); < 0.02 after round 4 |
| gain(RESEL-L, T/2) at r=2 | 0.0875 | [0.0547, 0.1172] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T/2) at r=4 | 0.0000 | [-0.0308, 0.0172] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T/2) at r=8 | 0.0188 | [0.0016, 0.0388] | strictly decreasing; gain(8) <= 0.03 |
| UPPER - LOWER (T/2) at 8T | 0.0047 | [-0.0188, 0.0297] | < 0.05 (S6); < 0.02 after round 4 |
| early-batch penalty (first 10% of 8T) | 0.1490 | [0.0980, 0.1882] | >= 0.08 |
| U_ss (margin 0.02) | > 16T | per seed ['> 16T', '7T', '> 16T', '15T', '> 16T'] | [4T, 10T] |
| U* (margin 0.02) | > 16T | per seed ['> 16T', '> 16T', '> 16T', '> 16T', '> 16T'] | [8T, 16T] or > 16T |
| STATIC2T single-walk hit rate | 0.3254 | - | MODELED 0.32 |
| STATIC(T) single-walk hit rate | 0.2747 | - | about 0.27 (a=1/4), about 0.42 (a=1/2) |
| RESEL-L(T) hit rate first -> last round | 0.2710 -> 0.3620 | - | to within 0.03 of top-T share (MODELED C_max 0.389) |
| RHO eps_cum(16T) | 0.0217 | - | < 0.02 |
| CAP(4T,T) retention | 0.979 | - | 4T >= 80%, 2T >= 60% |
| CAP(2T,T) retention | 0.917 | - | 4T >= 80%, 2T >= 60% |
| CAP(4T,T/2) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |
| CAP(2T,T/2) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |

- Round-0 identity all arms all seeds: True; NULL-B / PHI(0) bit identity: {'RUN-ECDLP-612fb1-001': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-002': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-003': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-004': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-005': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}}
- S4 exceedance: RESEL-L(T/2): exact exceedance False (max exact-oracle -0.0125, max sampled-oracle 0.0620); RESEL-L(T): exact exceedance False (max exact-oracle -0.0147, max sampled-oracle 0.0750); RESEL-U(T): exact exceedance False (max exact-oracle -0.0042, max sampled-oracle 0.0849)

## Cell 2^24,a=1/2 (T = 256, seeds [1, 2, 3, 4, 5], runs ['RUN-ECDLP-612fb1-018', 'RUN-ECDLP-612fb1-019', 'RUN-ECDLP-612fb1-020', 'RUN-ECDLP-612fb1-021', 'RUN-ECDLP-612fb1-022'])
| quantity | MEASURED point | 95% BCa CI | FROZEN prediction |
|---|---|---|---|
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=4T | -0.0938 | [-0.1063, -0.0820] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(4T) | 0.882 | [0.821, 0.938] | <= 0.75 (CI excluding 1.0) |
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=8T | -0.0594 | [-0.0707, -0.0469] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(8T) | 0.739 | [0.692, 0.806] | [0.45, 0.65] |
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=16T | -0.0496 | [-0.0625, -0.0387] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(16T) | 0.697 | [0.651, 0.748] | <= 0.6 |
| NULL-A(T) gain at 8T | -0.0953 | [-0.1098, -0.0820] | within CI of zero every round: False |
| NULL-A(T/2) gain at 8T | -0.1102 | [-0.1289, -0.0961] | within CI of zero every round: False |
| PHI(0.0) gain at 8T | 0.0000 | [0.0000, 0.0000] | non-decreasing, gain(0)=0 |
| PHI(0.1) gain at 8T | 0.0258 | [0.0160, 0.0355] | non-decreasing, gain(0)=0 |
| PHI(0.25) gain at 8T | 0.0418 | [0.0289, 0.0520] | non-decreasing, gain(0)=0 |
| PHI(0.5) gain at 8T | 0.0543 | [0.0422, 0.0664] | non-decreasing, gain(0)=0 |
| PHI(1.0) gain at 8T | 0.0660 | [0.0531, 0.0784] | non-decreasing, gain(0)=0 |
| gain(RESEL-L, T) at r=2 | 0.0344 | [0.0234, 0.0434] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T) at r=4 | 0.0121 | [0.0055, 0.0184] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T) at r=8 | 0.0055 | [0.0020, 0.0094] | strictly decreasing; gain(8) <= 0.03 |
| UPPER - LOWER (T) at 8T | 0.0039 | [-0.0016, 0.0090] | < 0.05 (S6); < 0.02 after round 4 |
| gain(RESEL-L, T/2) at r=2 | 0.0660 | [0.0516, 0.0777] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T/2) at r=4 | 0.0168 | [0.0082, 0.0258] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T/2) at r=8 | 0.0023 | [-0.0035, 0.0086] | strictly decreasing; gain(8) <= 0.03 |
| UPPER - LOWER (T/2) at 8T | 0.0102 | [0.0009, 0.0168] | < 0.05 (S6); < 0.02 after round 4 |
| early-batch penalty (first 10% of 8T) | 0.1216 | [0.0951, 0.1390] | >= 0.08 |
| U_ss (margin 0.02) | > 16T | per seed ['> 16T', '> 16T', '> 16T', '> 16T', '12T'] | [4T, 10T] |
| U* (margin 0.02) | > 16T | per seed ['> 16T', '> 16T', '> 16T', '> 16T', '> 16T'] | [8T, 16T] or > 16T |
| STATIC2T single-walk hit rate | 0.5041 | - | MODELED 0.32 |
| STATIC(T) single-walk hit rate | 0.4426 | - | about 0.27 (a=1/4), about 0.42 (a=1/2) |
| RESEL-L(T) hit rate first -> last round | 0.4513 -> 0.5201 | - | to within 0.03 of top-T share (MODELED C_max 0.525) |
| RHO eps_cum(16T) | 0.0121 | - | < 0.02 |
| CAP(4T,T) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |
| CAP(2T,T) retention | 1.068 | - | 4T >= 80%, 2T >= 60% |
| CAP(4T,T/2) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |
| CAP(2T,T/2) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |

- Round-0 identity all arms all seeds: True; NULL-B / PHI(0) bit identity: {'RUN-ECDLP-612fb1-018': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-019': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-020': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-021': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-022': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}}
- S4 exceedance: RESEL-L(T/2): exact exceedance False (max exact-oracle -0.0093, max sampled-oracle 0.0416); RESEL-L(T): exact exceedance False (max exact-oracle -0.0127, max sampled-oracle 0.0253); RESEL-U(T): exact exceedance False (max exact-oracle -0.0106, max sampled-oracle 0.0402)

## Cell 2^24,a=1/4 (T = 256, seeds [1, 2, 3, 4, 5], runs ['RUN-ECDLP-612fb1-013', 'RUN-ECDLP-612fb1-014', 'RUN-ECDLP-612fb1-015', 'RUN-ECDLP-612fb1-016', 'RUN-ECDLP-612fb1-017'])
| quantity | MEASURED point | 95% BCa CI | FROZEN prediction |
|---|---|---|---|
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=4T | -0.1090 | [-0.1258, -0.0957] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(4T) | 0.776 | [0.730, 0.816] | <= 0.75 (CI excluding 1.0) |
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=8T | -0.0641 | [-0.0803, -0.0492] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(8T) | 0.654 | [0.620, 0.700] | [0.45, 0.65] |
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=16T | -0.0523 | [-0.0703, -0.0367] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(16T) | 0.619 | [0.584, 0.663] | <= 0.6 |
| NULL-A(T) gain at 8T | -0.1453 | [-0.1629, -0.1289] | within CI of zero every round: False |
| NULL-A(T/2) gain at 8T | -0.1816 | [-0.2023, -0.1629] | within CI of zero every round: False |
| PHI(0.0) gain at 8T | 0.0000 | [0.0000, 0.0000] | non-decreasing, gain(0)=0 |
| PHI(0.1) gain at 8T | -0.0020 | [-0.0156, 0.0090] | non-decreasing, gain(0)=0 |
| PHI(0.25) gain at 8T | 0.0289 | [0.0164, 0.0436] | non-decreasing, gain(0)=0 |
| PHI(0.5) gain at 8T | 0.0531 | [0.0363, 0.0648] | non-decreasing, gain(0)=0 |
| PHI(1.0) gain at 8T | 0.0758 | [0.0617, 0.0912] | non-decreasing, gain(0)=0 |
| gain(RESEL-L, T) at r=2 | 0.0938 | [0.0777, 0.1078] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T) at r=4 | 0.0484 | [0.0371, 0.0609] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T) at r=8 | 0.0141 | [0.0047, 0.0232] | strictly decreasing; gain(8) <= 0.03 |
| UPPER - LOWER (T) at 8T | 0.0020 | [-0.0070, 0.0109] | < 0.05 (S6); < 0.02 after round 4 |
| gain(RESEL-L, T/2) at r=2 | 0.0758 | [0.0621, 0.0930] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T/2) at r=4 | 0.0316 | [0.0184, 0.0418] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T/2) at r=8 | 0.0152 | [0.0066, 0.0234] | strictly decreasing; gain(8) <= 0.03 |
| UPPER - LOWER (T/2) at 8T | 0.0234 | [0.0102, 0.0355] | < 0.05 (S6); < 0.02 after round 4 |
| early-batch penalty (first 10% of 8T) | 0.1461 | [0.1206, 0.1657] | >= 0.08 |
| U_ss (margin 0.02) | > 16T | per seed ['9T', '> 16T', '> 16T', '> 16T', '> 16T'] | [4T, 10T] |
| U* (margin 0.02) | > 16T | per seed ['> 16T', '> 16T', '> 16T', '> 16T', '> 16T'] | [8T, 16T] or > 16T |
| STATIC2T single-walk hit rate | 0.3355 | - | MODELED 0.32 |
| STATIC(T) single-walk hit rate | 0.2894 | - | about 0.27 (a=1/4), about 0.42 (a=1/2) |
| RESEL-L(T) hit rate first -> last round | 0.2981 -> 0.3700 | - | to within 0.03 of top-T share (MODELED C_max 0.389) |
| RHO eps_cum(16T) | 0.0065 | - | < 0.02 |
| CAP(4T,T) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |
| CAP(2T,T) retention | 1.012 | - | 4T >= 80%, 2T >= 60% |
| CAP(4T,T/2) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |
| CAP(2T,T/2) retention | 1.015 | - | 4T >= 80%, 2T >= 60% |

- Round-0 identity all arms all seeds: True; NULL-B / PHI(0) bit identity: {'RUN-ECDLP-612fb1-013': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-014': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-015': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-016': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-017': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}}
- S4 exceedance: RESEL-L(T/2): exact exceedance False (max exact-oracle -0.0157, max sampled-oracle 0.0166); RESEL-L(T): exact exceedance False (max exact-oracle -0.0186, max sampled-oracle 0.0206); RESEL-U(T): exact exceedance False (max exact-oracle -0.0113, max sampled-oracle 0.0241)

## Cell 2^30,a=1/2 (T = 1024, seeds [1, 2, 3, 4, 5], runs ['RUN-ECDLP-612fb1-028', 'RUN-ECDLP-612fb1-029', 'RUN-ECDLP-612fb1-030', 'RUN-ECDLP-612fb1-031', 'RUN-ECDLP-612fb1-032'])
| quantity | MEASURED point | 95% BCa CI | FROZEN prediction |
|---|---|---|---|
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=4T | -0.0740 | [-0.0800, -0.0682] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(4T) | 0.806 | [0.769, 0.846] | <= 0.75 (CI excluding 1.0) |
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=8T | -0.0594 | [-0.0662, -0.0541] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(8T) | 0.738 | [0.715, 0.771] | [0.45, 0.65] |
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=16T | -0.0575 | [-0.0640, -0.0518] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(16T) | 0.713 | [0.692, 0.736] | <= 0.6 |
| NULL-A(T) gain at 8T | -0.0909 | [-0.0979, -0.0840] | within CI of zero every round: False |
| NULL-A(T/2) gain at 8T | -0.1162 | [-0.1240, -0.1077] | within CI of zero every round: False |
| PHI(0.0) gain at 8T | 0.0000 | [0.0000, 0.0000] | non-decreasing, gain(0)=0 |
| PHI(0.1) gain at 8T | 0.0220 | [0.0174, 0.0266] | non-decreasing, gain(0)=0 |
| PHI(0.25) gain at 8T | 0.0298 | [0.0245, 0.0353] | non-decreasing, gain(0)=0 |
| PHI(0.5) gain at 8T | 0.0443 | [0.0389, 0.0505] | non-decreasing, gain(0)=0 |
| PHI(1.0) gain at 8T | 0.0572 | [0.0501, 0.0623] | non-decreasing, gain(0)=0 |
| gain(RESEL-L, T) at r=2 | 0.0335 | [0.0280, 0.0380] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T) at r=4 | 0.0066 | [0.0029, 0.0103] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T) at r=8 | 0.0009 | [-0.0013, 0.0034] | strictly decreasing; gain(8) <= 0.03 |
| UPPER - LOWER (T) at 8T | 0.0003 | [-0.0025, 0.0029] | < 0.05 (S6); < 0.02 after round 4 |
| gain(RESEL-L, T/2) at r=2 | 0.0572 | [0.0494, 0.0620] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T/2) at r=4 | 0.0156 | [0.0115, 0.0206] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T/2) at r=8 | 0.0000 | [-0.0026, 0.0024] | strictly decreasing; gain(8) <= 0.03 |
| UPPER - LOWER (T/2) at 8T | 0.0046 | [0.0014, 0.0094] | < 0.05 (S6); < 0.02 after round 4 |
| early-batch penalty (first 10% of 8T) | 0.1118 | [0.1011, 0.1209] | >= 0.08 |
| U_ss (margin 0.02) | > 16T | per seed ['> 16T', '> 16T', '> 16T', '> 16T', '> 16T'] | [4T, 10T] |
| U* (margin 0.02) | > 16T | per seed ['> 16T', '> 16T', '> 16T', '> 16T', '> 16T'] | [8T, 16T] or > 16T |
| STATIC2T single-walk hit rate | 0.4968 | - | MODELED 0.32 |
| STATIC(T) single-walk hit rate | 0.4409 | - | about 0.27 (a=1/4), about 0.42 (a=1/2) |
| RESEL-L(T) hit rate first -> last round | 0.4344 -> 0.5080 | - | to within 0.03 of top-T share (MODELED C_max 0.525) |
| RHO eps_cum(16T) | 0.0032 | - | < 0.02 |
| CAP(4T,T) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |
| CAP(2T,T) retention | 0.985 | - | 4T >= 80%, 2T >= 60% |
| CAP(4T,T/2) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |
| CAP(2T,T/2) retention | 1.005 | - | 4T >= 80%, 2T >= 60% |

- Round-0 identity all arms all seeds: True; NULL-B / PHI(0) bit identity: {'RUN-ECDLP-612fb1-028': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-029': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-030': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-031': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-032': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}}
- S4 exceedance: RESEL-L(T/2): max pooled hit rate 0.3842, exceeds 0.42: False; RESEL-L(T): max pooled hit rate 0.5139, exceeds 0.42: True; RESEL-U(T): max pooled hit rate 0.5149, exceeds 0.42: True

## Cell 2^30,a=1/4 (T = 1024, seeds [1, 2, 3, 4, 5], runs ['RUN-ECDLP-612fb1-023', 'RUN-ECDLP-612fb1-024', 'RUN-ECDLP-612fb1-025', 'RUN-ECDLP-612fb1-026', 'RUN-ECDLP-612fb1-027'])
| quantity | MEASURED point | 95% BCa CI | FROZEN prediction |
|---|---|---|---|
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=4T | -0.0949 | [-0.1032, -0.0876] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(4T) | 0.780 | [0.748, 0.803] | <= 0.75 (CI excluding 1.0) |
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=8T | -0.0759 | [-0.0829, -0.0679] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(8T) | 0.688 | [0.664, 0.706] | [0.45, 0.65] |
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=16T | -0.0559 | [-0.0641, -0.0485] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(16T) | 0.632 | [0.607, 0.648] | <= 0.6 |
| NULL-A(T) gain at 8T | -0.1375 | [-0.1467, -0.1296] | within CI of zero every round: False |
| NULL-A(T/2) gain at 8T | -0.1673 | [-0.1764, -0.1571] | within CI of zero every round: False |
| PHI(0.0) gain at 8T | 0.0000 | [0.0000, 0.0000] | non-decreasing, gain(0)=0 |
| PHI(0.1) gain at 8T | -0.0006 | [-0.0067, 0.0056] | non-decreasing, gain(0)=0 |
| PHI(0.25) gain at 8T | 0.0320 | [0.0252, 0.0389] | non-decreasing, gain(0)=0 |
| PHI(0.5) gain at 8T | 0.0476 | [0.0403, 0.0546] | non-decreasing, gain(0)=0 |
| PHI(1.0) gain at 8T | 0.0643 | [0.0569, 0.0715] | non-decreasing, gain(0)=0 |
| gain(RESEL-L, T) at r=2 | 0.0800 | [0.0736, 0.0878] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T) at r=4 | 0.0508 | [0.0445, 0.0566] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T) at r=8 | 0.0078 | [0.0028, 0.0113] | strictly decreasing; gain(8) <= 0.03 |
| UPPER - LOWER (T) at 8T | 0.0128 | [0.0087, 0.0182] | < 0.05 (S6); < 0.02 after round 4 |
| gain(RESEL-L, T/2) at r=2 | 0.0643 | [0.0572, 0.0716] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T/2) at r=4 | 0.0301 | [0.0244, 0.0362] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T/2) at r=8 | 0.0089 | [0.0043, 0.0125] | strictly decreasing; gain(8) <= 0.03 |
| UPPER - LOWER (T/2) at 8T | 0.0240 | [0.0179, 0.0304] | < 0.05 (S6); < 0.02 after round 4 |
| early-batch penalty (first 10% of 8T) | 0.1314 | [0.1211, 0.1411] | >= 0.08 |
| U_ss (margin 0.02) | > 16T | per seed ['> 16T', '> 16T', '> 16T', '> 16T', '> 16T'] | [4T, 10T] |
| U* (margin 0.02) | > 16T | per seed ['> 16T', '> 16T', '> 16T', '> 16T', '> 16T'] | [8T, 16T] or > 16T |
| STATIC2T single-walk hit rate | 0.3327 | - | MODELED 0.32 |
| STATIC(T) single-walk hit rate | 0.2892 | - | about 0.27 (a=1/4), about 0.42 (a=1/2) |
| RESEL-L(T) hit rate first -> last round | 0.2857 -> 0.3676 | - | to within 0.03 of top-T share (MODELED C_max 0.389) |
| RHO eps_cum(16T) | 0.0016 | - | < 0.02 |
| CAP(4T,T) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |
| CAP(2T,T) retention | 0.984 | - | 4T >= 80%, 2T >= 60% |
| CAP(4T,T/2) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |
| CAP(2T,T/2) retention | 0.997 | - | 4T >= 80%, 2T >= 60% |

- Round-0 identity all arms all seeds: True; NULL-B / PHI(0) bit identity: {'RUN-ECDLP-612fb1-023': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-024': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-025': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-026': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-ECDLP-612fb1-027': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}}
- S4 exceedance: RESEL-L(T/2): max pooled hit rate 0.2586, exceeds 0.42: False; RESEL-L(T): max pooled hit rate 0.3751, exceeds 0.42: False; RESEL-U(T): max pooled hit rate 0.3821, exceeds 0.42: False

## Stage 3 curve arm TOY-P24-1ca86fe9187c (p = 16777199, N = 16782071, seeds [1, 2, 3], runs ['RUN-ECDLP-612fb1-34', 'RUN-ECDLP-612fb1-35', 'RUN-ECDLP-612fb1-36'])
- certificates: pass count equals solved count in every run: True; seeded-log match in every run: True; per run: RUN-ECDLP-612fb1-34: solved 6626, passed 6626, failed 0; RUN-ECDLP-612fb1-35: solved 6912, passed 6912, failed 0; RUN-ECDLP-612fb1-36: solved 6312, passed 6312, failed 0
- eps_ss(8T) pooled: STATIC(T) 0.7220, STATIC(T/2) 0.5944, RESEL-L(T) 0.8262, RESEL-L(T/2) 0.6732, NULL-A(T/2) 0.4108, RHO 0.0033
- RESEL-L(T/2) - STATIC(T) at 8T on the curve: -0.0488 [-0.0710, -0.0293] (3 seeds)
- NULL-A(T/2) gain at 8T on the curve: -0.1836 [-0.2103, -0.1621]
- transfer check (m) STATIC(T): curve 0.7220 vs generic 2^24 a=1/4 0.7395; difference -0.0174 [-0.0457, 0.0103]; CI contains zero: True
- transfer check (m) RESEL-L(T/2): curve 0.6732 vs generic 2^24 a=1/4 0.6754; difference -0.0022 [-0.0315, 0.0266]; CI contains zero: True
- round-0 identity on the curve: True; RHO collisions eps_cum(8T) 0.0039 (no logarithm derivable, no certificate)

