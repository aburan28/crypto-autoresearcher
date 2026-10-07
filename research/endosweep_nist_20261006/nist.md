# NIST curves through the endomorphism sweep

FIPS 186-4's fifteen curves and the Montgomery and Edwards curves of SP 800-186 as std-curves has them.  `D_K` is exact where 4q - t^2 is completely factored into primes (the factorisation is in `nist.json`); the degree column is the smallest norm of an element of the maximal order outside Z, a lower bound on the degree of every endomorphism outside Z.

| curve | field | verified | D_K | log2 abs(D_K) | f | smallest non-scalar degree | cheapest endomorphism |
|:--|:--|:--|--:|--:|--:|--:|:--|
| nist/P-192 | F_p, p of 192 bits | True | −(59 digits) | 193.94 | 1 | 2^191.94 | none (every non-scalar endomorphism has at least the degree shown) |
| nist/P-224 | F_p, p of 224 bits | True | −(67 digits) | 222.49 | 3 | 2^220.49 | none (every non-scalar endomorphism has at least the degree shown) |
| nist/P-256 | F_p, p of 256 bits | True | −(78 digits) | 257.98 | 1 | 2^255.98 | none (every non-scalar endomorphism has at least the degree shown) |
| nist/P-384 | F_p, p of 384 bits | True | −(117 digits) | 385.98 | 1 | 2^383.98 | none (every non-scalar endomorphism has at least the degree shown) |
| nist/P-521 | F_p, p of 521 bits | True | −(158 digits) | 522.98 | 1 | 2^520.98 | none (every non-scalar endomorphism has at least the degree shown) |
| nist/K-163 | F_2^163, x^163 + x^7 + x^6 + x^3 + 1 | True | -7 | 2.81 | (25 digits) | 2 | Frobenius tau, degree 2 (inseparable): 2 squarings affine, 3 in Lopez-Dahab |
| nist/K-233 | F_2^233, x^233 + x^74 + 1 | True | -7 | 2.81 | (35 digits) | 2 | Frobenius tau, degree 2 (inseparable): 2 squarings affine, 3 in Lopez-Dahab |
| nist/K-283 | F_2^283, x^283 + x^12 + x^7 + x^5 + 1 | True | -7 | 2.81 | (42 digits) | 2 | Frobenius tau, degree 2 (inseparable): 2 squarings affine, 3 in Lopez-Dahab |
| nist/K-409 | F_2^409, x^409 + x^87 + 1 | True | -7 | 2.81 | (62 digits) | 2 | Frobenius tau, degree 2 (inseparable): 2 squarings affine, 3 in Lopez-Dahab |
| nist/K-571 | F_2^571, x^571 + x^10 + x^5 + x^2 + 1 | True | -7 | 2.81 | (86 digits) | 2 | Frobenius tau, degree 2 (inseparable): 2 squarings affine, 3 in Lopez-Dahab |
| nist/B-163 | F_2^163, x^163 + x^7 + x^6 + x^3 + 1 | True | −(49 digits) | 162.46 | 1 | 2^160.46 | none (every non-scalar endomorphism has at least the degree shown) |
| nist/B-233 | F_2^233, x^233 + x^74 + 1 | True | −(71 digits) | 232.85 | 1 | 2^230.85 | none (every non-scalar endomorphism has at least the degree shown) |
| nist/B-283 | F_2^283, x^283 + x^12 + x^7 + x^5 + 1 | True | −(86 digits) | 284.8 | 1 | 2^282.8 | none (every non-scalar endomorphism has at least the degree shown) |
| nist/B-409 | F_2^409, x^409 + x^87 + 1 | True | −(124 digits) | 410.99 | 1 | 2^408.99 | none (every non-scalar endomorphism has at least the degree shown) |
| nist/B-571 | F_2^571, x^571 + x^10 + x^5 + x^2 + 1 | True | abs(D_K) ≥ 2058683930000000 | ≥ 50.87 | | ≥ 514670982500000 | none below degree 514670982500000 (partial factorisation) |
| other/Curve25519 | F_p, p of 255 bits | True | −(77 digits) | 254.65 | 2 | 2^252.65 | none (every non-scalar endomorphism has at least the degree shown) |
| other/Ed25519 (same curve as other/Curve25519) | F_p, p of 255 bits | True | −(77 digits) | 254.65 | 2 | 2^252.65 | none (every non-scalar endomorphism has at least the degree shown) |
| other/Curve448 | F_p, p of 448 bits | True | −(135 digits) | 447.53 | 2 | 2^445.53 | none (every non-scalar endomorphism has at least the degree shown) |
| other/Ed448 (same curve as other/Curve448) | F_p, p of 448 bits | True | −(135 digits) | 447.53 | 2 | 2^445.53 | none (every non-scalar endomorphism has at least the degree shown) |
| other/Ed448-Goldilocks | F_p, p of 448 bits | True | −(135 digits) | 447.53 | 2 | 2^445.53 | none (every non-scalar endomorphism has at least the degree shown) |

## Binary curves: counted scalar multiplication

Mean field multiplications (M) and squarings (S) per `k·G` over random scalars, counted on the arithmetic executed (Lopez-Dahab coordinates, affine tables from one batched Itoh-Tsujii inversion). M_eq is given with squarings free and with squarings as dear as multiplications, the two ends of what a polynomial-basis implementation pays.

| curve | best wNAF (S free) | M_eq | best TNAF (S free) | M_eq | ratio | best wNAF (S = M) | M_eq | best TNAF (S = M) | M_eq | ratio | results agree |
|:--|:--|--:|:--|--:|--:|:--|--:|:--|--:|--:|:--|
| nist/K-163 | wnaf/w4 | 797.2 | tnaf/w4 | 313.0 | 2.547 | wnaf/w4 | 2109.8 | tnaf/w4 | 1313.6 | 1.606 | True (32 scalars) |
| nist/K-233 | wnaf/w4 | 1115.5 | tnaf/w4 | 426.8 | 2.614 | wnaf/w4 | 2984.1 | tnaf/w4 | 1843.8 | 1.618 | True (32 scalars) |
| nist/K-283 | wnaf/w5 | 1336.2 | tnaf/w4 | 498.2 | 2.682 | wnaf/w5 | 3599.0 | tnaf/w4 | 2210.1 | 1.628 | True (32 scalars) |
| nist/K-409 | wnaf/w5 | 1881.2 | tnaf/w5 | 672.2 | 2.799 | wnaf/w5 | 5130.1 | tnaf/w5 | 3166.1 | 1.62 | True (32 scalars) |
| nist/K-571 | wnaf/w5 | 2597.0 | tnaf/w5 | 892.8 | 2.909 | wnaf/w5 | 7122.8 | tnaf/w5 | 4330.2 | 1.645 | True (32 scalars) |
| nist/B-163 | wnaf/w4 | 959.2 | — | — | — | wnaf/w4 | 2271.8 | — | — | — | True (32 scalars) |
| nist/B-233 | wnaf/w4 | 1352.5 | — | — | — | wnaf/w4 | 3226.4 | — | — | — | True (32 scalars) |
| nist/B-283 | wnaf/w5 | 1626.9 | — | — | — | wnaf/w5 | 3895.9 | — | — | — | True (32 scalars) |
| nist/B-409 | wnaf/w5 | 2303.2 | — | — | — | wnaf/w5 | 5563.2 | — | — | — | True (32 scalars) |
| nist/B-571 | wnaf/w5 | 3170.5 | — | — | — | wnaf/w5 | 7698.3 | — | — | — | True (32 scalars) |

## Every configuration counted

### nist/K-163

| configuration | M | S | inversions | M sd | precompute M | precompute S |
|:--|--:|--:|--:|--:|--:|--:|
| wnaf/w2 | 919.59 | 1230.19 | 1.0 | 35.54 | 0.0 | 0.0 |
| wnaf/w3 | 829.44 | 1331.62 | 2.0 | 24.98 | 22.0 | 173.0 |
| wnaf/w4 | 797.25 | 1312.53 | 2.0 | 18.64 | 54.0 | 195.0 |
| wnaf/w5 | 817.72 | 1328.25 | 2.0 | 21.54 | 118.0 | 239.0 |
| wnaf/w6 | 910.22 | 1390.94 | 2.0 | 20.09 | 246.0 | 327.0 |
| wnaf/w7 | 1142.94 | 1552.09 | 2.0 | 16.06 | 502.0 | 503.0 |
| tnaf/w2 | 446.75 | 915.44 | 1.0 | 27.49 | 0.0 | 0.0 |
| tnaf/w3 | 357.25 | 1019.66 | 2.0 | 19.94 | 19.0 | 174.0 |
| tnaf/w4 | 313.0 | 1000.59 | 2.0 | 10.72 | 45.0 | 201.0 |
| tnaf/w5 | 344.5 | 1064.28 | 2.0 | 9.79 | 121.0 | 291.0 |
| tnaf/w6 | 467.5 | 1235.16 | 2.0 | 6.61 | 273.0 | 483.0 |
| tnaf/w7 | 810.25 | 1702.06 | 2.0 | 7.41 | 641.0 | 967.0 |

### nist/K-233

| configuration | M | S | inversions | M sd | precompute M | precompute S |
|:--|--:|--:|--:|--:|--:|--:|
| wnaf/w2 | 1292.03 | 1750.5 | 1.0 | 37.46 | 0.0 | 0.0 |
| wnaf/w3 | 1172.81 | 1904.12 | 2.0 | 24.39 | 23.0 | 243.0 |
| wnaf/w4 | 1115.47 | 1868.62 | 2.0 | 20.07 | 55.0 | 265.0 |
| wnaf/w5 | 1117.12 | 1871.22 | 2.0 | 14.29 | 119.0 | 309.0 |
| wnaf/w6 | 1198.88 | 1928.75 | 2.0 | 16.29 | 247.0 | 397.0 |
| wnaf/w7 | 1421.16 | 2081.62 | 2.0 | 13.3 | 503.0 | 573.0 |
| tnaf/w2 | 635.75 | 1309.28 | 1.0 | 32.46 | 0.0 | 0.0 |
| tnaf/w3 | 493.5 | 1450.75 | 2.0 | 24.2 | 20.0 | 244.0 |
| tnaf/w4 | 426.75 | 1417.06 | 2.0 | 15.01 | 46.0 | 271.0 |
| tnaf/w5 | 437.25 | 1465.19 | 2.0 | 13.47 | 122.0 | 361.0 |
| tnaf/w6 | 547.5 | 1630.44 | 2.0 | 9.68 | 274.0 | 553.0 |
| tnaf/w7 | 883.75 | 2093.47 | 2.0 | 7.55 | 642.0 | 1037.0 |

### nist/K-283

| configuration | M | S | inversions | M sd | precompute M | precompute S |
|:--|--:|--:|--:|--:|--:|--:|
| wnaf/w2 | 1587.22 | 2140.81 | 1.0 | 44.59 | 0.0 | 0.0 |
| wnaf/w3 | 1426.53 | 2316.62 | 2.0 | 26.05 | 24.0 | 293.0 |
| wnaf/w4 | 1345.44 | 2267.06 | 2.0 | 18.07 | 56.0 | 315.0 |
| wnaf/w5 | 1336.25 | 2262.78 | 2.0 | 13.24 | 120.0 | 359.0 |
| wnaf/w6 | 1409.19 | 2315.0 | 2.0 | 11.61 | 248.0 | 447.0 |
| wnaf/w7 | 1624.5 | 2464.59 | 2.0 | 12.21 | 504.0 | 623.0 |
| tnaf/w2 | 745.5 | 1577.25 | 1.0 | 38.47 | 0.0 | 0.0 |
| tnaf/w3 | 587.75 | 1758.31 | 2.0 | 22.52 | 21.0 | 294.0 |
| tnaf/w4 | 498.25 | 1711.81 | 2.0 | 13.38 | 47.0 | 321.0 |
| tnaf/w5 | 504.0 | 1756.31 | 2.0 | 12.49 | 123.0 | 411.0 |
| tnaf/w6 | 605.0 | 1914.66 | 2.0 | 11.62 | 275.0 | 603.0 |
| tnaf/w7 | 931.75 | 2372.78 | 2.0 | 8.24 | 643.0 | 1087.0 |

### nist/K-409

| configuration | M | S | inversions | M sd | precompute M | precompute S |
|:--|--:|--:|--:|--:|--:|--:|
| wnaf/w2 | 2293.78 | 3100.41 | 1.0 | 48.32 | 0.0 | 0.0 |
| wnaf/w3 | 2054.91 | 3354.72 | 2.0 | 30.03 | 24.0 | 419.0 |
| wnaf/w4 | 1922.62 | 3272.19 | 2.0 | 27.35 | 56.0 | 441.0 |
| wnaf/w5 | 1881.22 | 3248.84 | 2.0 | 18.69 | 120.0 | 485.0 |
| wnaf/w6 | 1932.28 | 3289.34 | 2.0 | 15.57 | 248.0 | 573.0 |
| wnaf/w7 | 2127.06 | 3424.25 | 2.0 | 13.38 | 504.0 | 749.0 |
| tnaf/w2 | 1089.0 | 2297.25 | 1.0 | 45.83 | 0.0 | 0.0 |
| tnaf/w3 | 838.25 | 2544.97 | 2.0 | 28.0 | 21.0 | 420.0 |
| tnaf/w4 | 703.25 | 2470.22 | 2.0 | 22.7 | 47.0 | 447.0 |
| tnaf/w5 | 672.25 | 2493.81 | 2.0 | 14.07 | 123.0 | 537.0 |
| tnaf/w6 | 745.25 | 2634.0 | 2.0 | 10.79 | 275.0 | 729.0 |
| tnaf/w7 | 1058.5 | 3082.0 | 2.0 | 11.03 | 643.0 | 1213.0 |

### nist/K-571

| configuration | M | S | inversions | M sd | precompute M | precompute S |
|:--|--:|--:|--:|--:|--:|--:|
| wnaf/w2 | 3241.09 | 4360.84 | 1.0 | 45.02 | 0.0 | 0.0 |
| wnaf/w3 | 2886.56 | 4702.94 | 2.0 | 35.06 | 26.0 | 581.0 |
| wnaf/w4 | 2686.53 | 4579.62 | 2.0 | 20.37 | 58.0 | 603.0 |
| wnaf/w5 | 2597.0 | 4525.81 | 2.0 | 21.4 | 122.0 | 647.0 |
| wnaf/w6 | 2611.53 | 4540.84 | 2.0 | 16.16 | 250.0 | 735.0 |
| wnaf/w7 | 2780.75 | 4660.75 | 2.0 | 14.89 | 506.0 | 911.0 |
| tnaf/w2 | 1525.25 | 3215.81 | 1.0 | 47.06 | 0.0 | 0.0 |
| tnaf/w3 | 1167.0 | 3557.38 | 2.0 | 28.41 | 23.0 | 582.0 |
| tnaf/w4 | 965.5 | 3440.97 | 2.0 | 25.8 | 49.0 | 609.0 |
| tnaf/w5 | 892.75 | 3437.44 | 2.0 | 16.66 | 125.0 | 699.0 |
| tnaf/w6 | 939.5 | 3562.91 | 2.0 | 17.08 | 277.0 | 891.0 |
| tnaf/w7 | 1222.75 | 3990.38 | 2.0 | 12.75 | 645.0 | 1375.0 |

### nist/B-163

| configuration | M | S | inversions | M sd | precompute M | precompute S |
|:--|--:|--:|--:|--:|--:|--:|
| wnaf/w2 | 1079.38 | 1230.19 | 1.0 | 37.22 | 0.0 | 0.0 |
| wnaf/w3 | 989.75 | 1331.62 | 2.0 | 27.28 | 23.0 | 173.0 |
| wnaf/w4 | 959.25 | 1312.53 | 2.0 | 21.08 | 57.0 | 195.0 |
| wnaf/w5 | 983.38 | 1328.25 | 2.0 | 24.82 | 125.0 | 239.0 |
| wnaf/w6 | 1082.88 | 1390.94 | 2.0 | 24.17 | 261.0 | 327.0 |
| wnaf/w7 | 1331.5 | 1552.09 | 2.0 | 19.62 | 533.0 | 503.0 |

### nist/B-233

| configuration | M | S | inversions | M sd | precompute M | precompute S |
|:--|--:|--:|--:|--:|--:|--:|
| wnaf/w2 | 1528.62 | 1757.38 | 1.0 | 38.67 | 0.0 | 0.0 |
| wnaf/w3 | 1409.12 | 1909.91 | 2.0 | 24.07 | 24.0 | 243.0 |
| wnaf/w4 | 1352.5 | 1873.94 | 2.0 | 21.7 | 58.0 | 265.0 |
| wnaf/w5 | 1358.62 | 1877.94 | 2.0 | 17.21 | 126.0 | 309.0 |
| wnaf/w6 | 1450.38 | 1938.44 | 2.0 | 16.59 | 262.0 | 397.0 |
| wnaf/w7 | 1685.25 | 2088.5 | 2.0 | 15.89 | 534.0 | 573.0 |

### nist/B-283

| configuration | M | S | inversions | M sd | precompute M | precompute S |
|:--|--:|--:|--:|--:|--:|--:|
| wnaf/w2 | 1873.62 | 2147.53 | 1.0 | 44.63 | 0.0 | 0.0 |
| wnaf/w3 | 1711.62 | 2322.25 | 2.0 | 26.17 | 25.0 | 293.0 |
| wnaf/w4 | 1633.25 | 2273.31 | 2.0 | 18.31 | 59.0 | 315.0 |
| wnaf/w5 | 1626.88 | 2269.03 | 2.0 | 14.15 | 127.0 | 359.0 |
| wnaf/w6 | 1706.62 | 2320.47 | 2.0 | 13.06 | 263.0 | 447.0 |
| wnaf/w7 | 1939.5 | 2472.09 | 2.0 | 16.24 | 535.0 | 623.0 |

### nist/B-409

| configuration | M | S | inversions | M sd | precompute M | precompute S |
|:--|--:|--:|--:|--:|--:|--:|
| wnaf/w2 | 2716.5 | 3114.62 | 1.0 | 49.7 | 0.0 | 0.0 |
| wnaf/w3 | 2474.88 | 3366.91 | 2.0 | 28.98 | 25.0 | 419.0 |
| wnaf/w4 | 2338.75 | 3280.47 | 2.0 | 27.85 | 59.0 | 441.0 |
| wnaf/w5 | 2303.25 | 3259.94 | 2.0 | 17.59 | 127.0 | 485.0 |
| wnaf/w6 | 2359.38 | 3296.84 | 2.0 | 16.94 | 263.0 | 573.0 |
| wnaf/w7 | 2570.62 | 3435.03 | 2.0 | 16.11 | 535.0 | 749.0 |

### nist/B-571

| configuration | M | S | inversions | M sd | precompute M | precompute S |
|:--|--:|--:|--:|--:|--:|--:|
| wnaf/w2 | 3785.12 | 4349.28 | 1.0 | 52.21 | 0.0 | 0.0 |
| wnaf/w3 | 3444.62 | 4699.19 | 2.0 | 33.48 | 27.0 | 581.0 |
| wnaf/w4 | 3250.62 | 4577.91 | 2.0 | 22.22 | 61.0 | 603.0 |
| wnaf/w5 | 3170.5 | 4527.84 | 2.0 | 18.7 | 129.0 | 647.0 |
| wnaf/w6 | 3193.38 | 4543.81 | 2.0 | 20.48 | 265.0 | 735.0 |
| wnaf/w7 | 3381.25 | 4665.91 | 2.0 | 16.35 | 537.0 | 911.0 |

