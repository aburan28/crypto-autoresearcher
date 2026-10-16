# RM family on fast Kummer surfaces: survey

Primes 1000 < p < 1600, seed 20261008, 541.0 s.  All counts are exact (FFT point counts, rounded and checked); every figure here is measured.

| | RM family D_5 + t | control A: g + t, g random | control B: random split f |
|:--|--:|--:|--:|
| primes p = +-1 (mod 5) | 44 | 44 | 44 |
| nonsingular members (p, t) | 56630 | 56686 | 1891 |
| f splits completely (all of J[2] rational) | 5628 | 456 | 1891 |
| ... and 16 divides #J and #J_twist | 5628 | 456 | 1891 |
| ... and #J/16 prime | 859 | 21 | 80 |
| ... and #J_twist/16 prime | 863 | 37 | 103 |
| ... both (twist-secure) | 247 | 7 | 20 |
| char. poly. factors over Q(sqrt5), all members | 56630 | 507 | 67 |
| char. poly. factors over Q(sqrt5), split members | 5628 | 15 | 67 |
| hit rate given split (Wilson 95%) | 0.1526 [0.1435, 0.1623] | 0.0461 [0.0303, 0.0694] | 0.0423 [0.0341, 0.0523] |
| twist-secure rate given split (Wilson 95%) | 0.0439 [0.0388, 0.0496] | 0.0154 [0.0075, 0.0313] | 0.0106 [0.0069, 0.0163] |
| split fraction | 0.0994 | 0.0080 | 1 (by construction) |
| 2-adic valuation of #J over split members | 4: 4027, 6: 1178, 8: 314, 10: 74, 12: 16, 14: 7, 16: 4, 18: 7, 20: 1 | 4: 159, 5: 108, 6: 101, 7: 34, 8: 25, 9: 16, 10: 8, 11: 1, 12: 1, 13: 1, 14: 2 | 4: 669, 5: 480, 6: 336, 7: 189, 8: 113, 9: 58, 10: 21, 11: 13, 12: 6, 13: 2, 14: 4 |

Closed-form splitting criterion vs root count, RM family: 0 disagreements.
PARI hyperellcharpoly spot checks: {'done': 12, 'agree': 12, 'available': True}.

Inert primes p = +-2 (mod 5) in the range: {"primes": 39, "members_scanned": 50861, "split": 0, "d5_is_permutation_all": true, "rm_factor_members": 0, "members_counted": 4188}

## Explicit RM on points

* p = 1009 (p mod 5 = 4), t = 11: #J = 988016 = 16 * 61751, eigenvalue of T on J[l] = 248; all checks pass: True
  * T(P) on J for 40 rational points: True
  * T(T(P)) + T(P) - P = 0 on 21 points with split image: True
  * J[2] rational: 16 distinct sums of four Weierstrass divisors, each killed by 2: True
  * l * D = 0: True
  * T acts on J[l] as a root of X^2 + X - 1 mod l: True
  * 2-dim decomposition k = k1 + k2*lambda reconstructs kD: True
* p = 1021 (p mod 5 = 1), t = 40: #J = 1072976 = 16 * 67061, eigenvalue of T on J[l] = 16700; all checks pass: True
  * T(P) on J for 40 rational points: True
  * T(T(P)) + T(P) - P = 0 on 14 points with split image: True
  * J[2] rational: 16 distinct sums of four Weierstrass divisors, each killed by 2: True
  * l * D = 0: True
  * T acts on J[l] as a root of X^2 + X - 1 mod l: True
  * 2-dim decomposition k = k1 + k2*lambda reconstructs kD: True

## Examples (first hits)

| p | t | #J | l = #J/16 | twist l prime | v (a - a' = v sqrt5) |
|--:|--:|--:|--:|:--|--:|
| 1009 | 11 | 988016 | 61751 | False | 4 |
| 1009 | 46 | 956464 | 59779 | False | 4 |
| 1009 | 259 | 1022864 | 63929 | False | 32 |
| 1009 | 317 | 1110896 | 69431 | True | 4 |
| 1009 | 368 | 948496 | 59281 | True | 12 |
| 1009 | 641 | 948496 | 59281 | True | 12 |
| 1021 | 40 | 1072976 | 67061 | False | 16 |
| 1021 | 55 | 1035344 | 64709 | True | 28 |
| 1021 | 122 | 1044304 | 65269 | True | 12 |
| 1021 | 144 | 1067536 | 66721 | False | 36 |
| 1021 | 148 | 1044304 | 65269 | True | 12 |
| 1021 | 188 | 1067536 | 66721 | False | 36 |

## Payoff ceiling (modelled)

1-D ladder: `b` steps of xDBL + xADD; 2-D chain: `b/2` steps of xDBL + 2 xADD; rho = xADD/xDBL.

| rho | speed-up |
|--:|--:|
| 0.5 | 1.500 |
| 0.75 | 1.400 |
| 1.0 | 1.333 |
| 1.25 | 1.286 |
| 1.5 | 1.250 |

p = 2^127 - 1: p = 2 (mod 5): z -> z^5 is a bijection on F_p^* and on the norm-one torus, so D_5 permutes F_p and x^5 - 5x^3 + 5x + t has exactly one root in F_p for EVERY t; no member of the family over F_{2^127-1} has rational J[2] (theorem; checked exhaustively on every inert prime of the survey range).
