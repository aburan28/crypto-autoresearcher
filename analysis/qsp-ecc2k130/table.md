# QSP index calculus at n = 131 (ECC2K-130 field): cost surface

Generic sqrt(2^131) = 2^65.5; recorded rho estimate 2^60.9 (KN-LIT-096).

ord_131(2) = 130; Phi_131 irreducible over F_2: True; 2^131 - 1 = 263 * 10350794431055162386718619237468234569.

## n' at which some cell has beta <= 1 (a QSP is *definable*)

15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130

## n' at which beta < 1/(2 kappa) = 0.1025 (Prop 8 asymptotic generic-beating region)

66, 67

## Cheapest cells (Theorem 3.2 with every factor kept)

| selection | n' | d | m | orbits | alpha | beta | log2 attempts | log2 Rojas/attempt | log2 relation phase | log2 lin. alg. | log2 total | log2 resultant floor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| min total, any (d=2 rows are linearized-only) | 66 | 2 | 2 | 1 | 1.008 | 0.030 | 66.0 | 55.6 | 121.6 | 133.0 | 133.0 | 133.0 |
| min total, beta<=1, not excluded | 66 | 3 | 2 | 1 | 1.008 | 0.048 | 66.0 | 67.0 | 133.0 | 133.0 | 133.0 | 133.0 |
| min floor, any (d=2 rows are linearized-only) | 33 | 2 | 4 | 1 | 1.008 | 0.120 | 36.6 | 212.0 | 248.6 | 68.0 | 248.6 | 68.0 |
| min floor, beta<=1, not excluded | 33 | 3 | 4 | 1 | 1.008 | 0.191 | 36.6 | 257.7 | 294.3 | 68.0 | 294.3 | 68.0 |
| min total, Frobenius orbits (L in F_2[X], Koblitz) | 66 | 3 | 2 | 131 | 1.008 | 0.048 | 59.0 | 67.0 | 126.0 | 118.9 | 126.0 | 118.9 |
| min floor, Frobenius orbits (L in F_2[X], Koblitz) | 33 | 3 | 4 | 131 | 1.008 | 0.191 | 29.6 | 257.7 | 287.2 | 53.9 | 287.2 | 60.6 |

## Selected cells (n' with n = 131 = -1 mod n', the Lemma 4.1 best case, at their smallest m)

| n' | d | m | orbits | excluded (linearized) | alpha | beta | log2 attempts | log2 M(E) | log2 relation phase | log2 lin. alg. | log2 total | log2 floor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11 | 2 | 12 | 1 | False | 1.008 | 1.083 | 38.8 | 264.0 | 1872.5 | 25.6 | 1872.5 | 302.8 |
| 11 | 2 | 12 | 131 | False | 1.008 | 1.083 | 31.8 | 264.0 | 1865.4 | 11.5 | 1865.4 | 295.8 |
| 11 | 3 | 12 | 1 | False | 1.008 | 1.716 | 38.8 | 341.2 | 2283.2 | 25.6 | 2283.2 | 380.1 |
| 11 | 3 | 12 | 131 | False | 1.008 | 1.716 | 31.8 | 341.2 | 2276.1 | 11.5 | 2276.1 | 373.0 |
| 12 | 2 | 11 | 1 | True | 1.008 | 0.910 | 36.3 | 220.0 | 1579.3 | 27.5 | 1579.3 | 256.3 |
| 12 | 2 | 11 | 131 | True | 1.008 | 0.910 | 29.2 | 220.0 | 1572.3 | 13.4 | 1572.3 | 249.2 |
| 12 | 3 | 11 | 1 | False | 1.008 | 1.442 | 36.3 | 284.3 | 1924.4 | 27.5 | 1924.4 | 320.6 |
| 12 | 3 | 11 | 131 | False | 1.008 | 1.442 | 29.2 | 284.3 | 1917.4 | 13.4 | 1917.4 | 313.6 |
| 22 | 2 | 6 | 1 | True | 1.008 | 0.271 | 30.5 | 60.0 | 497.7 | 46.6 | 497.7 | 90.5 |
| 22 | 2 | 6 | 131 | True | 1.008 | 0.271 | 23.5 | 60.0 | 490.6 | 32.5 | 490.6 | 83.5 |
| 22 | 3 | 6 | 1 | False | 1.008 | 0.429 | 30.5 | 77.5 | 600.3 | 46.6 | 600.3 | 108.0 |
| 22 | 3 | 6 | 131 | False | 1.008 | 0.429 | 23.5 | 77.5 | 593.3 | 32.5 | 593.3 | 101.0 |
| 33 | 2 | 4 | 1 | True | 1.008 | 0.120 | 36.6 | 24.0 | 248.6 | 68.0 | 248.6 | 68.0 |
| 33 | 2 | 4 | 131 | True | 1.008 | 0.120 | 29.6 | 24.0 | 241.6 | 53.9 | 241.6 | 53.9 |
| 33 | 3 | 4 | 1 | False | 1.008 | 0.191 | 36.6 | 31.0 | 294.3 | 68.0 | 294.3 | 68.0 |
| 33 | 3 | 4 | 131 | False | 1.008 | 0.191 | 29.6 | 31.0 | 287.2 | 53.9 | 287.2 | 60.6 |
| 44 | 2 | 3 | 1 | True | 1.008 | 0.068 | 45.6 | 12.0 | 167.2 | 89.6 | 167.2 | 89.6 |
| 44 | 2 | 3 | 131 | True | 1.008 | 0.068 | 38.6 | 12.0 | 160.2 | 75.5 | 160.2 | 75.5 |
| 44 | 3 | 3 | 1 | False | 1.008 | 0.107 | 45.6 | 15.5 | 192.9 | 89.6 | 192.9 | 89.6 |
| 44 | 3 | 3 | 131 | False | 1.008 | 0.107 | 38.6 | 15.5 | 185.9 | 75.5 | 185.9 | 75.5 |
| 66 | 2 | 2 | 1 | True | 1.008 | 0.030 | 66.0 | 4.0 | 121.6 | 133.0 | 133.0 | 133.0 |
| 66 | 2 | 2 | 131 | True | 1.008 | 0.030 | 59.0 | 4.0 | 114.6 | 118.9 | 118.9 | 118.9 |
| 66 | 3 | 2 | 1 | False | 1.008 | 0.048 | 66.0 | 5.2 | 133.0 | 133.0 | 133.0 | 133.0 |
| 66 | 3 | 2 | 131 | False | 1.008 | 0.048 | 59.0 | 5.2 | 126.0 | 118.9 | 126.0 | 118.9 |

## [EP21] Proposition 8 asymptotic exponent, evaluated at n = 131 (m >> 1 regime; NOT reachable at n = 131, see rows above)

| beta | alpha_beta | exponent | log2 cost | < 65.5 | < 60.9 |
|---|---|---|---|---|---|
| 1.0 | 0.103 | 0.949 | 124.3 | False | False |
| 0.99994 | 0.103 | 0.949 | 124.3 | False | False |
| 0.8 | 0.128 | 0.936 | 122.6 | False | False |
| 0.75 | 0.137 | 0.932 | 122.0 | False | False |
| 0.7 | 0.146 | 0.927 | 121.4 | False | False |
| 0.6 | 0.171 | 0.915 | 119.8 | False | False |
| 0.4 | 0.256 | 0.872 | 114.2 | False | False |
| 0.2 | 0.513 | 0.744 | 97.4 | False | False |
| 0.15 | 0.684 | 0.658 | 86.2 | False | False |
| 0.1025 | 1.000 | 0.500 | 65.5 | True | False |
| 0.1 | 1.025 | 0.487 | 63.8 | True | False |
| 0.0958 | 1.070 | 0.465 | 60.9 | True | True |

## Multiplicative QSP census (r | 2^131 - 1, |V| >= 2^(n'-1))

- r=263, n'=9, |V|/2^n'=0.516, beta=12.874
- r=10350794431055162386718619237468234569, n'=123, |V|/2^n'=0.973, beta=1.020

## Published additive families containing n = 131

{
 "additive_hits": [
  {
   "family": "Type 1bis",
   "n_prime": 130,
   "beta": 0.9999408284023669
  }
 ],
 "multiplicative_families_at_p_2": {
  "family_1_needs_even_n": false,
  "family_2_p_equals_kn_plus_k_minus_1_with_p_2": false,
  "family_3_p_equals_kn_minus_k_minus_neg1_pow_n_with_p_2": false
 }
}

## Linearized QSPs: Theorem 1 and Lemma 2 of [EP21]

{
 "beta_min": 0.75,
 "alpha_beta_at_kappa_4.876": 0.13672409078479628,
 "exponent": 0.9316379546076019,
 "log2_cost_at_n_131": 122.04457205359584,
 "kappa_needed_for_alpha_beta_gt_1_at_beta_0.75": 0.6666666666666666,
 "lemma2_max_n_prime_for_l": {
  "1": 11,
  "2": 16,
  "3": 21,
  "4": 24,
  "5": 26,
  "6": 30,
  "7": 31,
  "8": 32,
  "9": 36,
  "10": 40,
  "11": 41
 },
 "note": "[EP21] Section 4.4 says kappa < 1.5 would give alpha_beta > 1 at beta = 3/4; from alpha_beta = 1/(2 kappa beta) that requires kappa < 2/3, not 1.5. Recorded as a discrepancy in the source text, not adjudicated here."
}
