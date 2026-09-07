# EXP-ECDLP-612fb1 analysis run: CI tables over stages G

Observations only. MEASURED numbers are counts/rates from the runs; MODELED numbers are the
frozen contract's formulas and published references, quoted beside them and never mixed.

## Gates (reported before any arm)
### 2^20,a=1/4: seeds [1, 2, 3]
- G2 fixture (reported only): MEASURED scaled main cost 50.211 (per seed [52.886, 51.056, 47.048]) vs PUBLISHED 1.79 +/- 0.18 -> within: False; MEASURED P/sqrt(NT) mean 0.909 vs range [1.05, 1.4]; G2 pass: False
- G1 (GATED): slope(log grid) per seed [-1.582, -1.649, -1.637] [MODELED Borel under same estimator [-0.63, -0.63, -0.63]]; within 0.15 of -0.5 all seeds: False; cutoff n_c theta^2/2 [None, None, None] in [0.5,2]: False; top-T share / C_max [0.068, 0.064, 0.065] in [0.85,1.05]: False; STATIC(T) below top share: True; largest basin in Borel band: [False, False, False]; G1 literal (all four): False

## Cell 2^20,a=1/4 (T = 64, seeds [1, 2, 3], runs ['RUN-RT-90e7cf-permutation-s1', 'RUN-RT-90e7cf-permutation-s2', 'RUN-RT-90e7cf-permutation-s3'])
| quantity | MEASURED point | 95% BCa CI | FROZEN prediction |
|---|---|---|---|
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=4T | -0.0208 | [-0.0417, -0.0078] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(4T) | 0.717 | [0.572, 4.000] | <= 0.75 (CI excluding 1.0) |
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=8T | -0.0208 | [-0.0417, -0.0078] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(8T) | 1.000 | [0.612, 2.370] | [0.45, 0.65] |
| eps_ss(RESEL-L(T/2)) - eps_ss(STATIC(T)) at U=16T | -0.0182 | [-0.0365, -0.0026] | S1 at 8T: upper >= 0 and point >= -0.03; F1 at 16T: upper < 0 |
| rho_T(16T) | 0.713 | [0.561, 1.719] | <= 0.6 |
| NULL-A(T) gain at 8T | -0.0052 | [-0.0208, 0.0078] | within CI of zero every round: False |
| NULL-A(T/2) gain at 8T | -0.0026 | [-0.0156, 0.0104] | within CI of zero every round: False |
| PHI(0.0) gain at 8T | 0.0000 | [0.0000, 0.0000] | non-decreasing, gain(0)=0 |
| PHI(0.1) gain at 8T | 0.0000 | [0.0000, 0.0000] | non-decreasing, gain(0)=0 |
| PHI(0.25) gain at 8T | 0.0000 | [0.0000, 0.0000] | non-decreasing, gain(0)=0 |
| PHI(0.5) gain at 8T | -0.0026 | [-0.0104, 0.0000] | non-decreasing, gain(0)=0 |
| PHI(1.0) gain at 8T | -0.0026 | [-0.0130, 0.0052] | non-decreasing, gain(0)=0 |
| gain(RESEL-L, T) at r=2 | 0.0000 | [-0.0156, 0.0104] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T) at r=4 | -0.0026 | [-0.0182, 0.0026] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T) at r=8 | -0.0052 | [-0.0154, 0.0000] | strictly decreasing; gain(8) <= 0.03 |
| UPPER - LOWER (T) at 8T | -0.0130 | [-0.0495, 0.0078] | < 0.05 (S6); < 0.02 after round 4 |
| gain(RESEL-L, T/2) at r=2 | -0.0026 | [-0.0130, 0.0052] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T/2) at r=4 | -0.0052 | [-0.0104, 0.0000] | strictly decreasing; gain(8) <= 0.03 |
| gain(RESEL-L, T/2) at r=8 | 0.0000 | [0.0000, 0.0000] | strictly decreasing; gain(8) <= 0.03 |
| UPPER - LOWER (T/2) at 8T | -0.0182 | [-0.0417, -0.0052] | < 0.05 (S6); < 0.02 after round 4 |
| early-batch penalty (first 10% of 8T) | 0.0196 | [0.0000, 0.0392] | >= 0.08 |
| U_ss (margin 0.02) | 2T | per seed ['2T', '2T', '8T'] | [4T, 10T] |
| U* (margin 0.02) | 2T | per seed ['2T', '2T', '> 16T'] | [8T, 16T] or > 16T |
| STATIC2T single-walk hit rate | 0.0166 | - | MODELED 0.32 |
| STATIC(T) single-walk hit rate | 0.0118 | - | about 0.27 (a=1/4), about 0.42 (a=1/2) |
| RESEL-L(T) hit rate first -> last round | 0.0133 -> 0.0175 | - | to within 0.03 of top-T share (MODELED C_max 0.389) |
| RHO eps_cum(16T) | 0.0007 | - | < 0.02 |
| CAP(4T,T) retention | None | - | 4T >= 80%, 2T >= 60% |
| CAP(2T,T) retention | None | - | 4T >= 80%, 2T >= 60% |
| CAP(4T,T/2) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |
| CAP(2T,T/2) retention | 1.0 | - | 4T >= 80%, 2T >= 60% |

- Round-0 identity all arms all seeds: True; NULL-B / PHI(0) bit identity: {'RUN-RT-90e7cf-permutation-s1': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-RT-90e7cf-permutation-s2': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}, 'RUN-RT-90e7cf-permutation-s3': {'NULL-B(T)': True, 'NULL-B(T/2)': True, 'PHI(0.0,T/2)': True}}
- S4 exceedance: RESEL-L(T/2): exact exceedance False (max exact-oracle -0.0060, max sampled-oracle 0.0024); RESEL-L(T): exact exceedance False (max exact-oracle -0.0119, max sampled-oracle 0.0039); RESEL-U(T): exact exceedance False (max exact-oracle -0.0074, max sampled-oracle 0.0081)

