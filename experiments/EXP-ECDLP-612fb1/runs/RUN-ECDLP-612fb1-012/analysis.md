# EXP-ECDLP-612fb1 analysis run: CI tables over stages G

Observations only. MEASURED numbers are counts/rates from the runs; MODELED numbers are the
frozen contract's formulas and published references, quoted beside them and never mixed.

## Gates (reported before any arm)
### 2^20,a=1/2: seeds [1, 2, 3, 4, 5]
- G2 fixture (reported only): MEASURED scaled main cost 1.771 (per seed [1.711, 1.888, 1.579, 1.895, 1.818]) vs PUBLISHED 1.62 +/- 0.16 -> within: True; MEASURED P/sqrt(NT) mean 2.291 vs range None; G2 pass: True
- G1 (GATED): slope(log grid) per seed [-0.62, -0.608, -0.619, -0.616, -0.593] [MODELED Borel under same estimator [-0.613, -0.613, -0.613, -0.613, -0.613]]; within 0.15 of -0.5 all seeds: True; cutoff n_c theta^2/2 [1.548, 0.916, 1.3, 1.157, 0.916] in [0.5,2]: True; top-T share / C_max [0.999, 0.927, 1.022, 0.965, 0.935] in [0.85,1.05]: True; STATIC(T) below top share: True; largest basin in Borel band: [True, True, True, True, True]; G1 literal (all four): True
### 2^20,a=1/4: seeds [1, 2, 3, 4, 5]
- G2 fixture (reported only): MEASURED scaled main cost 1.843 (per seed [1.779, 2.292, 1.587, 1.747, 1.915]) vs PUBLISHED 1.79 +/- 0.18 -> within: True; MEASURED P/sqrt(NT) mean 1.338 vs range [1.05, 1.4]; G2 pass: True
- G1 (GATED): slope(log grid) per seed [-0.637, -0.632, -0.636, -0.636, -0.617] [MODELED Borel under same estimator [-0.63, -0.63, -0.63, -0.63, -0.63]]; within 0.15 of -0.5 all seeds: True; cutoff n_c theta^2/2 [1.03, 1.091, 1.157, 1.3, 0.971] in [0.5,2]: True; top-T share / C_max [1.004, 0.928, 0.997, 0.992, 0.944] in [0.85,1.05]: True; STATIC(T) below top share: True; largest basin in Borel band: [True, True, True, True, True]; G1 literal (all four): True

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

