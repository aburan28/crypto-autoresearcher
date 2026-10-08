# Endomorphism sweep across curves

Every verified prime-field curve of the std-curves database and of the arkworks-rs/curves workspace, scanned for a small CM discriminant (|D_K| <= 2 000 000); for every curve that has one, the cheapest endomorphism (a unit, or the chain sweep's cheapest isogeny chain over a catalogue proved to contain every chain within 2x of it), its construction on the curve, and the modelled best GLV-2 configuration against the best width-w NAF with the curve's own arithmetic. Operation counts (M_eq = M + S), not timings.

- Curves scanned: **202**, of which **47** repeat another entry (same p, j-invariant, order and cofactor; marked in the last table), leaving **155** distinct curves.  With a small CM discriminant: **60**; certified free of any non-scalar endomorphism of degree below 500 000 (|D_K| > 2 000 000): **95**.

## Curves with a cheap endomorphism

| curve | source | p bits | n bits | D_K | h(D) | kind | cheapest | order | chain M_eq (opt / gen) | catalogue complete | verified on points | modelled best baseline | modelled best GLV | ratio | arithmetic |
|:--|:--|--:|--:|--:|--:|:--|:--|:--|--:|:--|:--|:--|:--|--:|:--|
| other/Tom-384 | std-curves | 384 | 384 | -619 | 5 | chain | 4 + ω | 7·5·5 | 80 / 128 | yes (≥ 160 outside; N ≤ 3125, ℓ ≤ 37) | yes (11/11 elements) | jacobian/w6 4932.2 | jacobian/w5 3233.8 | 1.5252 | general a: dbl-2007-bl 1M + 8S + 1M for a |
| bls/Bandersnatch | std-curves | 255 | 253 | -8 | 1 | chain | ω | 2 | 6 / 10 | yes (≥ 12 outside; N ≤ 3, ℓ ≤ 3) | yes (2/2 elements) | jacobian/w5 3286.0 | jacobian/w5 2158.8 | 1.5222 | general a: dbl-2007-bl 1M + 8S + 1M for a (counted on the short Weierstrass model of this edwards curve) |
| mnt/mnt1 | std-curves | 170 | 156 | -19 | 1 | chain | ω | 5 | 12 / 41 | yes (≥ 24 outside; N ≤ 7, ℓ ≤ 7) | yes (2/2 elements) | jacobian/w5 2051.7 | jacobian/w4 1368.1 | 1.4997 | general a: dbl-2007-bl 1M + 8S + 1M for a |
| arkworks/cp6_782 | endosweep_curves_20261006/arkworks | 782 | 377 | -339 | 6 | chain | 4 + ω | 7·3·5 | 65 / 113 | yes (≥ 130 outside; N ≤ 1365, ℓ ≤ 29) | yes (18/18 elements) | jacobian/w6 4467.2 | jacobian/w5 2989.5 | 1.4943 | small a = 5: dbl-2007-bl 1M + 8S |
| mnt/mnt5/2 | std-curves | 240 | 240 | -211 | 3 | chain | 1 + ω | 11·5 | 61 / 122 | yes (≥ 122 outside; N ≤ 475, ℓ ≤ 19) | yes (8/8 elements) | jacobian/w5 3119.7 | jacobian/w5 2131.4 | 1.4636 | general a: dbl-2007-bl 1M + 8S + 1M for a |
| mnt/mnt5/3 | std-curves | 240 | 240 | -211 | 3 | chain | 1 + ω | 11·5 | 61 / 122 | yes (≥ 122 outside; N ≤ 475, ℓ ≤ 19) | yes (8/8 elements) | jacobian/w5 3119.7 | jacobian/w5 2131.4 | 1.4636 | general a: dbl-2007-bl 1M + 8S + 1M for a |
| gost/gost256 | std-curves | 256 | 256 | -915 | 8 | chain | 1 + ω | 11·3·7 | 92 / 158 | yes (≥ 184 outside; N ≤ 11319, ℓ ≤ 47) | yes (15/15 elements) | jacobian/w5 3058.4 | jacobian/w5 2132.5 | 1.4342 | small a = 7: dbl-2007-bl 1M + 8S |
| mnt/mnt3/1 | std-curves | 160 | 160 | -139 | 3 | chain | ω | 7·5 | 49 / 92 | yes (≥ 98 outside; N ≤ 325, ℓ ≤ 13) | yes (10/10 elements) | jacobian/w5 2099.1 | jacobian/w4 1466.5 | 1.4313 | general a: dbl-2007-bl 1M + 8S + 1M for a |
| mnt/mnt3/3 | std-curves | 160 | 160 | -139 | 3 | chain | ω | 7·5 | 49 / 92 | yes (≥ 98 outside; N ≤ 325, ℓ ≤ 13) | yes (10/10 elements) | jacobian/w5 2099.1 | jacobian/w4 1466.5 | 1.4313 | general a: dbl-2007-bl 1M + 8S + 1M for a |
| other/Tom-521 | std-curves | 522 | 521 | -28243 | 24 | chain | 47 + ω | 11·7·11·11 | 228 / 299 | yes (≥ 456 outside; N ≤ 46773881, ℓ ≤ 109) | yes (29/29 elements) | jacobian/w6 5572.6 | jacobian/w5 3913.9 | 1.4238 | isomorphic to an a = -3 model (-3/a is a fourth power): 3M + 5S |
| gost/id-GostR3410-2001-CryptoPro-B-ParamSet | std-curves | 256 | 256 | -619 | 5 | chain | 4 + ω | 7·5·5 | 80 / 128 | yes (≥ 160 outside; N ≤ 3125, ℓ ≤ 37) | yes (11/11 elements) | jacobian/w5 2805.1 | jacobian/w5 1990.0 | 1.4096 | a = -3: dbl-2001-b 3M + 5S |
| mnt/mnt5/1 | std-curves | 240 | 240 | -211 | 3 | chain | 1 + ω | 11·5 | 61 / 122 | yes (≥ 122 outside; N ≤ 475, ℓ ≤ 19) | yes (8/8 elements) | jacobian/w5 2643.6 | jacobian/w5 1890.5 | 1.3984 | isomorphic to an a = -3 model (-3/a is a fourth power): 3M + 5S |
| mnt/mnt2/1 | std-curves | 159 | 159 | -91 | 2 | chain | 1 + ω | 5·5 | 43 / 77 | yes (≥ 86 outside; N ≤ 95, ℓ ≤ 29) | yes (8/8 elements) | jacobian/w5 1779.0 | jacobian/w4 1281.8 | 1.3878 | isomorphic to an a = -3 model (-3/a is a fourth power): 3M + 5S |
| mnt/mnt2/2 | std-curves | 159 | 159 | -91 | 2 | chain | 1 + ω | 5·5 | 43 / 77 | yes (≥ 86 outside; N ≤ 95, ℓ ≤ 29) | yes (8/8 elements) | jacobian/w5 1779.0 | jacobian/w4 1281.8 | 1.3878 | isomorphic to an a = -3 model (-3/a is a fourth power): 3M + 5S |
| mnt/mnt3/2 | std-curves | 160 | 160 | -139 | 3 | chain | ω | 7·5 | 49 / 92 | yes (≥ 98 outside; N ≤ 325, ℓ ≤ 13) | yes (10/10 elements) | jacobian/w5 1784.2 | jacobian/w4 1304.7 | 1.3675 | isomorphic to an a = -3 model (-3/a is a fourth power): 3M + 5S |
| other/Tom-256 | std-curves | 256 | 256 | -4155 | 12 | chain | 2 + ω | 19·5·11 | 161 / 263 | yes (≥ 322 outside; N ≤ 67155, ℓ ≤ 73) | yes (18/18 elements) | jacobian/w5 2815.8 | jacobian/w5 2081.6 | 1.3527 | a = -3: dbl-2001-b 3M + 5S |
| mnt/mnt4 | std-curves | 240 | 240 | -163 | 1 | chain | ω | 41 | 120 / 311 | yes (≥ 240 outside; N ≤ 71, ℓ ≤ 71) | yes (6/6 elements) | jacobian/w5 2640.1 | jacobian/w5 1953.2 | 1.3517 | isomorphic to an a = -3 model (-3/a is a fourth power): 3M + 5S |
| bn/bn606 | std-curves | 606 | 606 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 5839.3 | jacobian/w5 3947.1 | 1.4794 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn638 | std-curves | 638 | 638 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 6132.3 | jacobian/w5 4145.2 | 1.4794 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn574 | std-curves | 574 | 574 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 5541.0 | jacobian/w5 3749.2 | 1.4779 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn542 | std-curves | 542 | 542 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 5238.4 | jacobian/w5 3548.2 | 1.4763 | a = 0: dbl-2009-l 2M + 5S |
| other/Fp512BN | std-curves | 512 | 512 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 4972.5 | jacobian/w5 3370.3 | 1.4754 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn510 | std-curves | 510 | 510 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 4945.4 | jacobian/w5 3356.1 | 1.4736 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn478 | std-curves | 478 | 478 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 4648.8 | jacobian/w5 3155.3 | 1.4733 | a = 0: dbl-2009-l 2M + 5S |
| bls/BLS48-581-G1 | std-curves | 581 | 518 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 5019.0 | jacobian/w5 3408.9 | 1.4723 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn446 | std-curves | 446 | 446 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 4350.2 | jacobian/w5 2958.2 | 1.4706 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn414 | std-curves | 414 | 414 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 4051.2 | jacobian/w5 2757.7 | 1.4691 | a = 0: dbl-2009-l 2M + 5S |
| bls/BLS12-638 | std-curves | 638 | 427 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 4175.1 | jacobian/w5 2843.5 | 1.4683 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn382 | std-curves | 382 | 382 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 3758.7 | jacobian/w5 2563.2 | 1.4664 | a = 0: dbl-2009-l 2M + 5S |
| arkworks/bw6_767 | endosweep_curves_20261006/arkworks | 767 | 381 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 3755.2 | jacobian/w5 2561.4 | 1.4661 | a = 0: dbl-2009-l 2M + 5S |
| arkworks/bw6_761 | endosweep_curves_20261006/arkworks | 761 | 377 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 3717.6 | jacobian/w5 2536.2 | 1.4658 | a = 0: dbl-2009-l 2M + 5S |
| other/Fp384BN | std-curves | 384 | 384 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 3786.0 | jacobian/w5 2583.7 | 1.4654 | a = 0: dbl-2009-l 2M + 5S |
| bls/BLS24-477 | std-curves | 477 | 383 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 3770.8 | jacobian/w5 2573.5 | 1.4652 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn350 | std-curves | 350 | 350 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w6 3457.9 | jacobian/w5 2370.0 | 1.459 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn318 | std-curves | 318 | 318 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 3154.6 | jacobian/w5 2170.8 | 1.4532 | a = 0: dbl-2009-l 2M + 5S |
| bls/BLS12-455 | std-curves | 455 | 305 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 3028.4 | jacobian/w5 2087.6 | 1.4507 | a = 0: dbl-2009-l 2M + 5S |
| bls/BLS12-446 | std-curves | 446 | 299 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2973.6 | jacobian/w5 2057.9 | 1.445 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn286 | std-curves | 286 | 286 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2843.4 | jacobian/w5 1972.3 | 1.4417 | a = 0: dbl-2009-l 2M + 5S |
| other/Tweedledee | std-curves | 255 | 255 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2543.5 | jacobian/w5 1777.1 | 1.4313 | a = 0: dbl-2009-l 2M + 5S |
| arkworks/secq256k1 | endosweep_curves_20261006/arkworks | 256 | 256 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2561.5 | jacobian/w5 1791.0 | 1.4302 | a = 0: dbl-2009-l 2M + 5S |
| arkworks/bn254 | endosweep_curves_20261006/arkworks | 254 | 254 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2540.1 | jacobian/w5 1776.9 | 1.4295 | a = 0: dbl-2009-l 2M + 5S |
| bls/BLS12-381 | std-curves | 381 | 255 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2551.9 | jacobian/w5 1785.2 | 1.4295 | a = 0: dbl-2009-l 2M + 5S |
| other/Tweedledum | std-curves | 255 | 255 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2543.5 | jacobian/w5 1779.4 | 1.4295 | a = 0: dbl-2009-l 2M + 5S |
| other/Fp254BNa | std-curves | 254 | 254 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2535.3 | jacobian/w5 1775.4 | 1.428 | a = 0: dbl-2009-l 2M + 5S |
| other/Fp256BN | std-curves | 256 | 256 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2561.5 | jacobian/w5 1793.8 | 1.428 | a = 0: dbl-2009-l 2M + 5S |
| other/Pallas | std-curves | 255 | 255 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2543.5 | jacobian/w5 1781.1 | 1.428 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn254 | std-curves | 254 | 254 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2535.1 | jacobian/w5 1775.8 | 1.4276 | a = 0: dbl-2009-l 2M + 5S |
| other/Vesta | std-curves | 255 | 255 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2543.5 | jacobian/w5 1781.8 | 1.4275 | a = 0: dbl-2009-l 2M + 5S |
| arkworks/grumpkin | endosweep_curves_20261006/arkworks | 254 | 254 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2540.1 | jacobian/w5 1779.9 | 1.4271 | a = 0: dbl-2009-l 2M + 5S |
| bls/BLS12-377 | std-curves | 377 | 253 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2525.1 | jacobian/w5 1770.2 | 1.4265 | a = 0: dbl-2009-l 2M + 5S |
| secg/secp256k1 | std-curves | 256 | 256 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2561.5 | jacobian/w5 1797.5 | 1.425 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn222 | std-curves | 222 | 222 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2224.5 | jacobian/w4 1566.9 | 1.4197 | a = 0: dbl-2009-l 2M + 5S |
| other/Fp224BN | std-curves | 224 | 224 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2252.0 | jacobian/w4 1587.7 | 1.4184 | a = 0: dbl-2009-l 2M + 5S |
| secg/secp224k1 | std-curves | 224 | 225 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 2253.2 | jacobian/w4 1590.3 | 1.4169 | a = 0: dbl-2009-l 2M + 5S |
| secg/secp160k1 | std-curves | 160 | 161 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 1634.9 | jacobian/w4 1156.0 | 1.4143 | a = 0: dbl-2009-l 2M + 5S |
| wtls/wap-wsg-idm-ecid-wtls9 | std-curves | 160 | 161 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 1634.9 | jacobian/w4 1156.6 | 1.4135 | a = 0: dbl-2009-l 2M + 5S |
| secg/secp192k1 | std-curves | 192 | 192 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 1941.5 | jacobian/w4 1373.7 | 1.4134 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn190 | std-curves | 190 | 190 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 1916.8 | jacobian/w4 1358.4 | 1.4111 | a = 0: dbl-2009-l 2M + 5S |
| bn/bn158 | std-curves | 158 | 158 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w5 1608.6 | jacobian/w4 1145.7 | 1.4041 | a = 0: dbl-2009-l 2M + 5S |
| wtls/wap-wsg-idm-ecid-wtls8 | std-curves | 112 | 113 | -3 | 1 | automorphism | zeta_3 | — | 1 / 1 | — | yes | jacobian/w4 1171.2 | jacobian/w4 835.0 | 1.4026 | a = 0: dbl-2009-l 2M + 5S |

## Every element within 2x of the cheapest, per curve

Each element at its cheapest step order; `verified` is the construction on the curve (closed walk, action as the predicted scalar on a point of order n, GLV-2 reconstruction).

### arkworks/cp6_782 (D = -339, h = 6)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| 4 + ω | 105 | 7·3·5 | 65 | 113 | yes | 1.73 |
| ω | 85 | 17·5 | 79 | 167 | yes | 1.79 |
| 9 + ω | 175 | 7·5·5 | 80 | 128 | yes | 1.74 |
| 2 + ω | 91 | 13·7 | 82 | 152 | yes | 1.65 |
| 10 + ω | 195 | 13·3·5 | 83 | 158 | yes | 2.55 |
| 5 + 2ω | 375 | 5·3·5·5 | 90 | 134 | yes | 3.55 |
| 5 + ω | 115 | 23·5 | 97 | 212 | yes | 2.81 |
| 15 + ω | 325 | 13·5·5 | 98 | 173 | yes | 1.74 |
| 1 + ω | 87 | 29·3 | 100 | 242 | yes | 3.99 |
| 1 + 2ω | 343 | 7·7·7 | 110 | 158 | yes | 2.09 |
| 16 + ω | 357 | 17·3·7 | 110 | 203 | yes | 4.15 |
| 25 + ω | 735 | 7·3·5·7 | 111 | 164 | yes | 6.38 |
| 15 + 2ω | 595 | 17·5·7 | 125 | 218 | yes | 2.86 |
| 20 + 3ω | 1225 | 7·5·5·7 | 126 | 179 | yes | 2.66 |
| 34 + ω | 1275 | 17·3·5·5 | 126 | 224 | yes | 4.49 |
| 11 + 2ω | 483 | 23·3·7 | 128 | 248 | yes | 5.2 |
| 23 + ω | 637 | 13·7·7 | 128 | 203 | yes | 2.97 |
| 1 + 4ω | 1365 | 13·3·5·7 | 129 | 209 | yes | 6.81 |

### bls/Bandersnatch (D = -8, h = 1)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| ω | 2 | 2 | 6 | 10 | yes | 0.08 |
| 1 + ω | 3 | 3 | 6 | 26 | yes | 0.1 |

### gost/gost256 (D = -915, h = 8)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| 1 + ω | 231 | 11·3·7 | 92 | 158 | yes | 1.34 |
| 7 + ω | 285 | 19·3·5 | 101 | 203 | yes | 0.34 |
| 12 + ω | 385 | 11·5·7 | 107 | 173 | yes | 0.59 |
| 22 + ω | 735 | 7·3·5·7 | 111 | 164 | yes | 0.33 |
| 19 + ω | 609 | 29·3·7 | 146 | 293 | yes | 0.77 |
| 3 + 2ω | 931 | 19·7·7 | 146 | 248 | yes | 0.39 |
| 26 + ω | 931 | 19·7·7 | 146 | 248 | yes | 0.37 |
| 29 + 2ω | 1815 | 11·3·5·11 | 153 | 224 | yes | 3.51 |
| 5 + ω | 259 | 37·7 | 154 | 332 | yes | 0.91 |
| 17 + 3ω | 2401 | 7·7·7·7 | 156 | 209 | yes | 0.22 |
| 9 + ω | 319 | 29·11 | 160 | 302 | yes | 0.82 |
| 9 + 2ω | 1015 | 29·5·7 | 161 | 308 | yes | 0.59 |
| 2 + ω | 235 | 47·5 | 169 | 392 | yes | 1.72 |
| 8 + ω | 301 | 43·7 | 172 | 377 | yes | 12.18 |
| 101 + 2ω | 11319 | 11·3·7·7·7 | 184 | 260 | yes | 5.8 |

### gost/id-GostR3410-2001-CryptoPro-B-ParamSet (D = -619, h = 5)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| 4 + ω | 175 | 7·5·5 | 80 | 128 | yes | 0.15 |
| 9 + ω | 245 | 7·5·7 | 95 | 143 | yes | 0.22 |
| 15 + 2ω | 875 | 7·5·5·5 | 111 | 164 | yes | 0.19 |
| 2 + ω | 161 | 23·7 | 112 | 227 | yes | 0.4 |
| ω | 155 | 31·5 | 121 | 272 | yes | 0.66 |
| 20 + ω | 575 | 23·5·5 | 128 | 248 | yes | 0.41 |
| 54 + ω | 3125 | 5·5·5·5·5 | 136 | 185 | yes | 0.15 |
| 5 + ω | 185 | 37·5 | 139 | 317 | yes | 0.94 |
| 39 + ω | 1715 | 7·5·7·7 | 141 | 194 | yes | 0.31 |
| 25 + ω | 805 | 23·5·7 | 143 | 263 | yes | 0.46 |
| 37 + 3ω | 2875 | 23·5·5·5 | 159 | 284 | yes | 0.46 |

### mnt/mnt1 (D = -19, h = 1)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| ω | 5 | 5 | 12 | 41 | yes | 0.03 |
| 1 + ω | 7 | 7 | 18 | 56 | yes | 0.05 |

### mnt/mnt2/1 (D = -91, h = 2)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| 1 + ω | 25 | 5·5 | 43 | 77 | yes | 0.24 |
| 3 + ω | 35 | 7·5 | 49 | 92 | yes | 0.08 |
| ω | 23 | 23 | 66 | 176 | yes | 0.15 |
| 6 + ω | 65 | 13·5 | 67 | 137 | yes | 0.11 |
| -1 + 2ω | 91 | 13·7 | 82 | 152 | yes | 0.06 |
| 2 + ω | 29 | 29 | 84 | 221 | yes | 0.22 |
| 1 + 2ω | 95 | 19·5 | 85 | 182 | yes | 0.21 |
| 8 + ω | 95 | 19·5 | 85 | 182 | yes | 0.2 |

### mnt/mnt2/2 (D = -91, h = 2)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| 1 + ω | 25 | 5·5 | 43 | 77 | yes | 0.22 |
| 3 + ω | 35 | 7·5 | 49 | 92 | yes | 0.08 |
| ω | 23 | 23 | 66 | 176 | yes | 0.16 |
| 6 + ω | 65 | 13·5 | 67 | 137 | yes | 0.1 |
| -1 + 2ω | 91 | 13·7 | 82 | 152 | yes | 0.06 |
| 2 + ω | 29 | 29 | 84 | 221 | yes | 0.22 |
| 1 + 2ω | 95 | 19·5 | 85 | 182 | yes | 0.24 |
| 8 + ω | 95 | 19·5 | 85 | 182 | yes | 0.22 |

### mnt/mnt3/1 (D = -139, h = 3)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| ω | 35 | 7·5 | 49 | 92 | yes | 0.5 |
| 4 + ω | 55 | 11·5 | 61 | 122 | yes | 0.15 |
| 5 + ω | 65 | 13·5 | 67 | 137 | yes | 0.15 |
| 9 + ω | 125 | 5·5·5 | 74 | 113 | yes | 2.08 |
| 6 + ω | 77 | 11·7 | 76 | 137 | yes | 0.08 |
| 5 + 2ω | 175 | 7·5·5 | 80 | 128 | yes | 3.27 |
| 7 + ω | 91 | 13·7 | 82 | 152 | yes | 0.1 |
| 15 + ω | 275 | 11·5·5 | 92 | 158 | yes | 0.82 |
| 14 + ω | 245 | 7·5·7 | 95 | 143 | yes | 1.03 |
| 2 + 3ω | 325 | 13·5·5 | 98 | 173 | yes | 0.94 |

### mnt/mnt3/2 (D = -139, h = 3)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| ω | 35 | 7·5 | 49 | 92 | yes | 0.47 |
| 4 + ω | 55 | 11·5 | 61 | 122 | yes | 0.15 |
| 5 + ω | 65 | 13·5 | 67 | 137 | yes | 0.14 |
| 9 + ω | 125 | 5·5·5 | 74 | 113 | yes | 2.17 |
| 6 + ω | 77 | 11·7 | 76 | 137 | yes | 0.08 |
| 5 + 2ω | 175 | 7·5·5 | 80 | 128 | yes | 3.12 |
| 7 + ω | 91 | 13·7 | 82 | 152 | yes | 0.1 |
| 15 + ω | 275 | 11·5·5 | 92 | 158 | yes | 0.78 |
| 14 + ω | 245 | 7·5·7 | 95 | 143 | yes | 1.04 |
| 2 + 3ω | 325 | 13·5·5 | 98 | 173 | yes | 0.84 |

### mnt/mnt3/3 (D = -139, h = 3)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| ω | 35 | 7·5 | 49 | 92 | yes | 0.44 |
| 4 + ω | 55 | 11·5 | 61 | 122 | yes | 0.16 |
| 5 + ω | 65 | 13·5 | 67 | 137 | yes | 0.15 |
| 9 + ω | 125 | 5·5·5 | 74 | 113 | yes | 2.02 |
| 6 + ω | 77 | 11·7 | 76 | 137 | yes | 0.09 |
| 5 + 2ω | 175 | 7·5·5 | 80 | 128 | yes | 3.07 |
| 7 + ω | 91 | 13·7 | 82 | 152 | yes | 0.22 |
| 15 + ω | 275 | 11·5·5 | 92 | 158 | yes | 0.95 |
| 14 + ω | 245 | 7·5·7 | 95 | 143 | yes | 1.02 |
| 2 + 3ω | 325 | 13·5·5 | 98 | 173 | yes | 0.82 |

### mnt/mnt4 (D = -163, h = 1)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| ω | 41 | 41 | 120 | 311 | yes | 1.14 |
| 1 + ω | 43 | 43 | 126 | 326 | yes | 1.17 |
| 2 + ω | 47 | 47 | 138 | 356 | yes | 1.36 |
| 3 + ω | 53 | 53 | 156 | 401 | yes | 1.87 |
| 4 + ω | 61 | 61 | 180 | 461 | yes | 2.6 |
| 5 + ω | 71 | 71 | 210 | 536 | yes | 3.53 |

### mnt/mnt5/1 (D = -211, h = 3)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| 1 + ω | 55 | 11·5 | 61 | 122 | yes | 0.26 |
| 3 + ω | 65 | 13·5 | 67 | 137 | yes | 0.25 |
| 8 + ω | 125 | 5·5·5 | 74 | 113 | yes | 0.48 |
| 6 + ω | 95 | 19·5 | 85 | 182 | yes | 0.34 |
| 7 + 2ω | 275 | 11·5·5 | 92 | 158 | yes | 0.61 |
| 16 + ω | 325 | 13·5·5 | 98 | 173 | yes | 0.69 |
| 9 + ω | 143 | 13·11 | 112 | 182 | yes | 0.19 |
| -1 + 3ω | 475 | 19·5·5 | 116 | 218 | yes | 0.74 |

### mnt/mnt5/2 (D = -211, h = 3)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| 1 + ω | 55 | 11·5 | 61 | 122 | yes | 0.23 |
| 3 + ω | 65 | 13·5 | 67 | 137 | yes | 0.29 |
| 8 + ω | 125 | 5·5·5 | 74 | 113 | yes | 0.51 |
| 6 + ω | 95 | 19·5 | 85 | 182 | yes | 0.36 |
| 7 + 2ω | 275 | 11·5·5 | 92 | 158 | yes | 0.64 |
| 16 + ω | 325 | 13·5·5 | 98 | 173 | yes | 0.68 |
| 9 + ω | 143 | 13·11 | 112 | 182 | yes | 0.2 |
| -1 + 3ω | 475 | 19·5·5 | 116 | 218 | yes | 0.76 |

### mnt/mnt5/3 (D = -211, h = 3)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| 1 + ω | 55 | 11·5 | 61 | 122 | yes | 0.23 |
| 3 + ω | 65 | 13·5 | 67 | 137 | yes | 0.25 |
| 8 + ω | 125 | 5·5·5 | 74 | 113 | yes | 0.54 |
| 6 + ω | 95 | 19·5 | 85 | 182 | yes | 0.38 |
| 7 + 2ω | 275 | 11·5·5 | 92 | 158 | yes | 0.61 |
| 16 + ω | 325 | 13·5·5 | 98 | 173 | yes | 0.62 |
| 9 + ω | 143 | 13·11 | 112 | 182 | yes | 0.23 |
| -1 + 3ω | 475 | 19·5·5 | 116 | 218 | yes | 0.84 |

### other/Tom-256 (D = -4155, h = 12)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| 2 + ω | 1045 | 19·5·11 | 161 | 263 | yes | 0.36 |
| 52 + ω | 3795 | 23·3·5·11 | 189 | 314 | yes | 0.8 |
| 13 + ω | 1221 | 37·3·11 | 200 | 383 | yes | 1.4 |
| 35 + ω | 2299 | 19·11·11 | 206 | 308 | yes | 0.64 |
| 49 + 2ω | 6655 | 11·5·11·11 | 213 | 284 | yes | 0.42 |
| 16 + ω | 1311 | 23·3·19 | 218 | 338 | yes | 1.89 |
| 19 + ω | 1419 | 43·3·11 | 218 | 428 | yes | 1.78 |
| 85 + ω | 8349 | 23·3·11·11 | 234 | 359 | yes | 1.61 |
| 59 + 2ω | 7755 | 47·3·5·11 | 261 | 494 | yes | 2.29 |
| 7 + ω | 1095 | 73·3·5 | 263 | 608 | yes | 4.48 |
| 40 + ω | 2679 | 47·3·19 | 290 | 518 | yes | 3.25 |
| 97 + ω | 10545 | 37·3·5·19 | 291 | 479 | yes | 2.8 |
| 101 + 3ω | 19855 | 19·5·11·19 | 297 | 404 | yes | 1.13 |
| 6 + ω | 1081 | 47·23 | 304 | 527 | yes | 2.64 |
| 9 + 2ω | 4255 | 37·5·23 | 305 | 488 | yes | 1.53 |
| 19 + 4ω | 17061 | 47·3·11·11 | 306 | 539 | yes | 2.83 |
| 124 + 7ω | 67155 | 37·3·5·11·11 | 307 | 500 | yes | 2.14 |
| 89 + 2ω | 12255 | 43·3·5·19 | 309 | 524 | yes | 2.96 |

### other/Tom-384 (D = -619, h = 5)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| 4 + ω | 175 | 7·5·5 | 80 | 128 | yes | 3.11 |
| 9 + ω | 245 | 7·5·7 | 95 | 143 | yes | 1.57 |
| 15 + 2ω | 875 | 7·5·5·5 | 111 | 164 | yes | 7.64 |
| 2 + ω | 161 | 23·7 | 112 | 227 | yes | 0.9 |
| ω | 155 | 31·5 | 121 | 272 | yes | 1.57 |
| 20 + ω | 575 | 23·5·5 | 128 | 248 | yes | 3.11 |
| 54 + ω | 3125 | 5·5·5·5·5 | 136 | 185 | yes | 9.13 |
| 5 + ω | 185 | 37·5 | 139 | 317 | yes | 2.15 |
| 39 + ω | 1715 | 7·5·7·7 | 141 | 194 | yes | 2.69 |
| 25 + ω | 805 | 23·5·7 | 143 | 263 | yes | 1.89 |
| 37 + 3ω | 2875 | 23·5·5·5 | 159 | 284 | yes | 7.45 |

### other/Tom-521 (D = -28243, h = 24)

| element | norm | order | M_eq optimised | M_eq generic | verified | build s |
|:--|--:|:--|--:|--:|:--|--:|
| 47 + ω | 9317 | 11·7·11·11 | 228 | 299 | yes | 2.64 |
| 113 + ω | 19943 | 37·7·7·11 | 276 | 464 | yes | 5.2 |
| 17 + 2ω | 28567 | 53·7·7·11 | 324 | 584 | yes | 10.35 |
| 184 + 9ω | 607453 | 23·7·7·7·7·11 | 326 | 461 | yes | 4.46 |
| 736 + 3ω | 607453 | 23·7·7·7·7·11 | 326 | 461 | yes | 4.19 |
| 1291 + 24ω | 5764801 | 7·7·7·7·7·7·7·7 | 340 | 413 | yes | 2.43 |
| 131 + ω | 24353 | 71·7·7·7 | 348 | 689 | yes | 18.73 |
| 22 + ω | 7567 | 47·7·23 | 350 | 578 | yes | 11.14 |
| 26 + 5ω | 177331 | 47·7·7·7·11 | 352 | 590 | yes | 8.87 |
| 183 + ω | 40733 | 23·7·11·23 | 354 | 479 | yes | 10.58 |
| 194 + ω | 44891 | 53·7·11·11 | 354 | 614 | yes | 10.88 |
| 705 + 8ω | 954569 | 23·7·7·7·11·11 | 356 | 491 | yes | 4.79 |
| 181 + 4ω | 146461 | 61·7·7·7·7 | 364 | 665 | yes | 11.33 |
| 115 + 2ω | 41699 | 37·7·7·23 | 366 | 554 | yes | 8.52 |
| 69 + ω | 11891 | 47·11·23 | 380 | 608 | yes | 11.64 |
| 20 + 3ω | 64009 | 23·11·11·23 | 384 | 509 | yes | 7.02 |
| 43 + 3ω | 65527 | 37·7·11·23 | 396 | 584 | yes | 13.22 |
| 1129 + 6ω | 1535611 | 37·7·7·7·11·11 | 398 | 596 | yes | 7.15 |
| 229 + ω | 59731 | 53·7·7·23 | 414 | 674 | yes | 12.95 |
| 91 + ω | 15433 | 61·11·23 | 422 | 713 | yes | 12.67 |
| 29 + ω | 7931 | 103·7·11 | 428 | 908 | yes | 39.75 |
| 68 + ω | 11753 | 73·7·23 | 428 | 773 | yes | 21.71 |
| 312 + 5ω | 275429 | 73·7·7·7·11 | 430 | 785 | yes | 19.07 |
| 79 + 2ω | 34643 | 101·7·7·7 | 438 | 914 | yes | 40.85 |
| -1 + 13ω | 1193297 | 71·7·7·7·7·7 | 440 | 791 | yes | 18.39 |
| 2570 + 17ω | 8689219 | 47·7·7·7·7·7·11 | 444 | 692 | yes | 10.0 |
| 36 + ω | 8393 | 109·7·11 | 446 | 953 | yes | 43.47 |
| 1219 + 80ω | 46773881 | 23·7·7·7·7·7·11·11 | 448 | 593 | yes | 5.94 |
| 71 + ω | 12173 | 47·7·37 | 455 | 683 | yes | 19.04 |

## Every curve scanned

| curve | source | p bits | verified | discriminant certificate |
|:--|:--|--:|:--|:--|
| anssi/FRP256v1 | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| arkworks/bls12_377 | endosweep_curves_20261006/arkworks | 377 | True | t^2-4q = (-3) * 587269870971281361444171168277668240640243801025419411456^2; CM field Q(sqrt(-3)) (duplicate of bls/BLS12-377) |
| arkworks/bls12_381 | endosweep_curves_20261006/arkworks | 381 | True | t^2-4q = (-3) * 2310096550715768212670172227226928237551693238409523516757^2; CM field Q(sqrt(-3)) (duplicate of bls/BLS12-381) |
| arkworks/bn254 | endosweep_curves_20261006/arkworks | 254 | True | t^2-4q = (-3) * 147946756881789319010696353538189108491^2; CM field Q(sqrt(-3)) |
| arkworks/bw6_761 | endosweep_curves_20261006/arkworks | 761 | True | t^2-4q = (-3) * 2327979834116721846122857819342346041630394402507777770613906795574054381627779834062290838568927395079900712927242^2; CM field Q(sqrt(-3)) |
| arkworks/bw6_767 | endosweep_curves_20261006/arkworks | 767 | True | t^2-4q = (-3) * 24014457331330004360771232084658496776881756820178521127679311063504543400615179349131886324465919419434285212565506^2; CM field Q(sqrt(-3)) |
| arkworks/cp6_782 | endosweep_curves_20261006/arkworks | 782 | True | t^2-4q = (-339) * 513025011189245362189291037990710422610397276367601556209885360626933410105300729369470840216346069866385567317670496^2; CM field Q(sqrt(-339)) |
| arkworks/curve25519 | endosweep_curves_20261006/arkworks | 255 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of other/Curve25519) |
| arkworks/ed25519 | endosweep_curves_20261006/arkworks | 255 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of other/Curve25519) |
| arkworks/ed_on_bls12_377 | endosweep_curves_20261006/arkworks | 253 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| arkworks/ed_on_bls12_381 | endosweep_curves_20261006/arkworks | 255 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of other/JubJub) |
| arkworks/ed_on_bls12_381_bandersnatch | endosweep_curves_20261006/arkworks | 255 | True | t^2-4q = (-8) * 21482638764116277775478679919733259912^2; CM field Q(sqrt(-8)) (duplicate of bls/Bandersnatch) |
| arkworks/ed_on_bn254 | endosweep_curves_20261006/arkworks | 254 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| arkworks/ed_on_bw6_761 | endosweep_curves_20261006/arkworks | 377 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| arkworks/ed_on_cp6_782 | endosweep_curves_20261006/arkworks | 377 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of arkworks/ed_on_bw6_761) |
| arkworks/ed_on_mnt4_298 | endosweep_curves_20261006/arkworks | 298 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| arkworks/ed_on_mnt4_753 | endosweep_curves_20261006/arkworks | 753 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| arkworks/grumpkin | endosweep_curves_20261006/arkworks | 254 | True | t^2-4q = (-3) * 147946756881789319010696353538189108491^2; CM field Q(sqrt(-3)) |
| arkworks/mnt4_298 | endosweep_curves_20261006/arkworks | 298 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| arkworks/mnt4_753 | endosweep_curves_20261006/arkworks | 753 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| arkworks/mnt6_298 | endosweep_curves_20261006/arkworks | 298 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| arkworks/mnt6_753 | endosweep_curves_20261006/arkworks | 753 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| arkworks/pallas | endosweep_curves_20261006/arkworks | 255 | True | t^2-4q = (-3) * 196462116142286827589391630752301449217^2; CM field Q(sqrt(-3)) (duplicate of other/Pallas) |
| arkworks/secp256k1 | endosweep_curves_20261006/arkworks | 256 | True | t^2-4q = (-3) * 303414439467246543595250775667605759171^2; CM field Q(sqrt(-3)) (duplicate of secg/secp256k1) |
| arkworks/secp256r1 | endosweep_curves_20261006/arkworks | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-256) |
| arkworks/secp384r1 | endosweep_curves_20261006/arkworks | 384 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-384) |
| arkworks/secq256k1 | endosweep_curves_20261006/arkworks | 256 | True | t^2-4q = (-3) * 303414439467246543595250775667605759171^2; CM field Q(sqrt(-3)) |
| arkworks/vesta | endosweep_curves_20261006/arkworks | 255 | True | t^2-4q = (-3) * 196462116142286827589391630752301449217^2; CM field Q(sqrt(-3)) (duplicate of other/Vesta) |
| bls/BLS12-377 | std-curves | 377 | True | t^2-4q = (-3) * 587269870971281361444171168277668240640243801025419411456^2; CM field Q(sqrt(-3)) |
| bls/BLS12-381 | std-curves | 381 | True | t^2-4q = (-3) * 2310096550715768212670172227226928237551693238409523516757^2; CM field Q(sqrt(-3)) |
| bls/BLS12-446 | std-curves | 446 | True | t^2-4q = (-3) * 15180017722556942872710858686172241542425226563119817904740305163606^2; CM field Q(sqrt(-3)) |
| bls/BLS12-455 | std-curves | 455 | True | t^2-4q = (-3) * 287572867293678436974519977531226436303080379672880577582937484382891^2; CM field Q(sqrt(-3)) |
| bls/BLS12-638 | std-curves | 638 | True | t^2-4q = (-3) * 1201199398395787546723127300641679086142518436131015165481254517460567318887250290819436851298997^2; CM field Q(sqrt(-3)) |
| bls/BLS24-477 | std-curves | 477 | True | t^2-4q = (-3) * 604128092931004996153900356638872198640435149234420528912987303159267285^2; CM field Q(sqrt(-3)) |
| bls/BLS48-581-G1 | std-curves | 581 | True | t^2-4q = (-3) * 2470234952045228861226479692223628411074049366373861109485273675792210673668036995939286^2; CM field Q(sqrt(-3)) |
| bls/Bandersnatch | std-curves | 255 | True | t^2-4q = (-8) * 21482638764116277775478679919733259912^2; CM field Q(sqrt(-8)) |
| bn/bn158 | std-curves | 158 | True | t^2-4q = (-3) * 454233058418789397299203^2; CM field Q(sqrt(-3)) |
| bn/bn190 | std-curves | 190 | True | t^2-4q = (-3) * 29710571568175225982381195267^2; CM field Q(sqrt(-3)) |
| bn/bn222 | std-curves | 222 | True | t^2-4q = (-3) * 1943310227059934888513759537528843^2; CM field Q(sqrt(-3)) |
| bn/bn254 | std-curves | 254 | True | t^2-4q = (-3) * 129607518034317099886745702645398241283^2; CM field Q(sqrt(-3)) |
| bn/bn286 | std-curves | 286 | True | t^2-4q = (-3) * 8366863340207706741294993301075392630620163^2; CM field Q(sqrt(-3)) |
| bn/bn318 | std-curves | 318 | True | t^2-4q = (-3) * 548079839685593379889101977298739683457859846211^2; CM field Q(sqrt(-3)) |
| bn/bn350 | std-curves | 350 | True | t^2-4q = (-3) * 35917316178020966140770026339278758006907024019816451^2; CM field Q(sqrt(-3)) |
| bn/bn382 | std-curves | 382 | True | t^2-4q = (-3) * 2353932232174051770881173201697930752584630523839501041667^2; CM field Q(sqrt(-3)) |
| bn/bn414 | std-curves | 414 | True | t^2-4q = (-3) * 154267229207681125708793071161632042239063797942298639324938243^2; CM field Q(sqrt(-3)) |
| bn/bn446 | std-curves | 446 | True | t^2-4q = (-3) * 10109980000181489923001201093401911741712157040574514822068840693771^2; CM field Q(sqrt(-3)) |
| bn/bn478 | std-curves | 478 | True | t^2-4q = (-3) * 662567649291894123450065105820326670768093618471357310296643630025146371^2; CM field Q(sqrt(-3)) |
| bn/bn510 | std-curves | 510 | True | t^2-4q = (-3) * 43422033463993573283847164979847511362163190678038904032036848688647949516803^2; CM field Q(sqrt(-3)) |
| bn/bn542 | std-curves | 542 | True | t^2-4q = (-3) * 2845711812853053972806387468884004947678148350198662474752430713551973652753285123^2; CM field Q(sqrt(-3)) |
| bn/bn574 | std-curves | 574 | True | t^2-4q = (-3) * 186496302581962721809830439849867378820456242583880530431255347119471774686354153144323^2; CM field Q(sqrt(-3)) |
| bn/bn606 | std-curves | 606 | True | t^2-4q = (-3) * 12222215858006915839141401255556695821975177552658946714103472755538745970781531637962639363^2; CM field Q(sqrt(-3)) |
| bn/bn638 | std-curves | 638 | True | t^2-4q = (-3) * 800995136978371572363525747477255032258950408690575773003799464919714074125184154404652534726667^2; CM field Q(sqrt(-3)) |
| brainpool/brainpoolP160r1 | std-curves | 160 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| brainpool/brainpoolP160t1 | std-curves | 160 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of brainpool/brainpoolP160r1) |
| brainpool/brainpoolP192r1 | std-curves | 192 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| brainpool/brainpoolP192t1 | std-curves | 192 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of brainpool/brainpoolP192r1) |
| brainpool/brainpoolP224r1 | std-curves | 224 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| brainpool/brainpoolP224t1 | std-curves | 224 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of brainpool/brainpoolP224r1) |
| brainpool/brainpoolP256r1 | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| brainpool/brainpoolP256t1 | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of brainpool/brainpoolP256r1) |
| brainpool/brainpoolP320r1 | std-curves | 320 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| brainpool/brainpoolP320t1 | std-curves | 320 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of brainpool/brainpoolP320r1) |
| brainpool/brainpoolP384r1 | std-curves | 384 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| brainpool/brainpoolP384t1 | std-curves | 384 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of brainpool/brainpoolP384r1) |
| brainpool/brainpoolP512r1 | std-curves | 512 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| brainpool/brainpoolP512t1 | std-curves | 512 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of brainpool/brainpoolP512r1) |
| gost/gost256 | std-curves | 256 | True | t^2-4q = (-915) * 5814239006315534931045933045806333847^2; CM field Q(sqrt(-915)) |
| gost/gost512 | std-curves | 511 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| gost/id-GostR3410-2001-CryptoPro-A-ParamSet | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| gost/id-GostR3410-2001-CryptoPro-B-ParamSet | std-curves | 256 | True | t^2-4q = (-619) * 4646402506017662432554672533504826433^2; CM field Q(sqrt(-619)) |
| gost/id-GostR3410-2001-CryptoPro-C-ParamSet | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| gost/id-tc26-gost-3410-12-512-paramSetA | std-curves | 512 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| gost/id-tc26-gost-3410-12-512-paramSetB | std-curves | 512 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| gost/id-tc26-gost-3410-2012-256-paramSetA | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| gost/id-tc26-gost-3410-2012-512-paramSetC | std-curves | 512 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| mnt/mnt1 | std-curves | 170 | True | t^2-4q = (-19) * 6915889423298038776451801^2; CM field Q(sqrt(-19)) |
| mnt/mnt2/1 | std-curves | 159 | True | t^2-4q = (-91) * 151115727451828644755795^2; CM field Q(sqrt(-91)) |
| mnt/mnt2/2 | std-curves | 159 | True | t^2-4q = (-91) * 151115727451828644755795^2; CM field Q(sqrt(-91)) |
| mnt/mnt3/1 | std-curves | 160 | True | t^2-4q = (-139) * 151115727451828644749125^2; CM field Q(sqrt(-139)) |
| mnt/mnt3/2 | std-curves | 160 | True | t^2-4q = (-139) * 151115727451828644749125^2; CM field Q(sqrt(-139)) |
| mnt/mnt3/3 | std-curves | 160 | True | t^2-4q = (-139) * 151115727451828644749125^2; CM field Q(sqrt(-139)) |
| mnt/mnt4 | std-curves | 240 | True | t^2-4q = (-163) * 166153499473114484112975882535041529^2; CM field Q(sqrt(-163)) |
| mnt/mnt5/1 | std-curves | 240 | True | t^2-4q = (-211) * 166153499473114484112975882535035935^2; CM field Q(sqrt(-211)) |
| mnt/mnt5/2 | std-curves | 240 | True | t^2-4q = (-211) * 166153499473114484112975882535035935^2; CM field Q(sqrt(-211)) |
| mnt/mnt5/3 | std-curves | 240 | True | t^2-4q = (-211) * 166153499473114484112975882535035935^2; CM field Q(sqrt(-211)) |
| nist/P-192 | std-curves | 192 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nist/P-224 | std-curves | 224 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nist/P-256 | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nist/P-384 | std-curves | 384 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nist/P-521 | std-curves | 521 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/ed-254-mont | std-curves | 254 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/ed-255-mers | std-curves | 255 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/ed-256-mont | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/ed-382-mont | std-curves | 382 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/ed-383-mers | std-curves | 383 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/ed-384-mont | std-curves | 384 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/ed-510-mont | std-curves | 510 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/ed-511-mers | std-curves | 511 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/ed-512-mont | std-curves | 512 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/numsp256d1 | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/numsp256t1 | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/numsp384d1 | std-curves | 384 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/numsp384t1 | std-curves | 384 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/numsp512d1 | std-curves | 512 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/numsp512t1 | std-curves | 512 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/w-254-mont | std-curves | 254 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/w-255-mers | std-curves | 255 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/w-256-mont | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/w-382-mont | std-curves | 382 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/w-383-mers | std-curves | 383 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/w-384-mont | std-curves | 384 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/w-510-mont | std-curves | 510 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/w-511-mers | std-curves | 511 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| nums/w-512-mont | std-curves | 512 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| oakley/192-bit Random ECP Group | std-curves | 192 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-192) |
| oakley/224-bit Random ECP Group | std-curves | 224 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-224) |
| oakley/256-bit Random ECP Group | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-256) |
| oakley/384-bit Random ECP Group | std-curves | 384 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-384) |
| oakley/521-bit Random ECP Group | std-curves | 521 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-521) |
| oscaa/SM2 | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/BADA55-R-256 | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/BADA55-VPR-224 | std-curves | 224 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/BADA55-VPR2-224 | std-curves | 224 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/BADA55-VR-224 | std-curves | 224 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/BADA55-VR-256 | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/BADA55-VR-384 | std-curves | 384 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/Curve1174 | std-curves | 251 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/Curve22103 | std-curves | 221 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/Curve25519 | std-curves | 255 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/Curve383187 | std-curves | 383 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/Curve41417 | std-curves | 414 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/Curve4417 | std-curves | 226 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/Curve448 | std-curves | 448 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/Curve67254 | std-curves | 382 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of other/E-382) |
| other/E-222 | std-curves | 222 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/E-382 | std-curves | 382 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/E-521 | std-curves | 521 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/Ed25519 | std-curves | 255 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of other/Curve25519) |
| other/Ed448 | std-curves | 448 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of other/Curve448) |
| other/Ed448-Goldilocks | std-curves | 448 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/Fp224BN | std-curves | 224 | True | t^2-4q = (-3) * 5192296858534689506442115857736067^2; CM field Q(sqrt(-3)) |
| other/Fp254BNa | std-curves | 254 | True | t^2-4q = (-3) * 126611883464401272127243293666542878721^2; CM field Q(sqrt(-3)) |
| other/Fp254BNb | std-curves | 254 | True | t^2-4q = (-3) * 129607518034317099886745702645398241283^2; CM field Q(sqrt(-3)) (duplicate of bn/bn254) |
| other/Fp256BN | std-curves | 256 | True | t^2-4q = (-3) * 340282366920936614181528116269263699971^2; CM field Q(sqrt(-3)) |
| other/Fp384BN | std-curves | 384 | True | t^2-4q = (-3) * 6277101735386680763835754795151022476645729035004851856003^2; CM field Q(sqrt(-3)) |
| other/Fp512BN | std-curves | 512 | True | t^2-4q = (-3) * 115792089237316195423570985008687840101659558519570290085463645789117669918083^2; CM field Q(sqrt(-3)) |
| other/JubJub | std-curves | 255 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/M-221 | std-curves | 221 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/M-383 | std-curves | 383 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/M-511 | std-curves | 511 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/MDC201601 | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/Pallas | std-curves | 255 | True | t^2-4q = (-3) * 196462116142286827589391630752301449217^2; CM field Q(sqrt(-3)) |
| other/Tom-256 | std-curves | 256 | True | t^2-4q = (-4155) * 7019618127640898221939468283479924503^2; CM field Q(sqrt(-4155)) |
| other/Tom-384 | std-curves | 384 | True | t^2-4q = (-619) * 380201093441490505678902542719199835054253522446560116525^2; CM field Q(sqrt(-619)) |
| other/Tom-521 | std-curves | 522 | True | t^2-4q = (-28243) * 6268055400574841440667156810254912726834973227558374885183820779126439865891^2; CM field Q(sqrt(-28243)) |
| other/Tweedledee | std-curves | 255 | True | t^2-4q = (-3) * 196462116142286827589390971285842952193^2; CM field Q(sqrt(-3)) |
| other/Tweedledum | std-curves | 255 | True | t^2-4q = (-3) * 196462116142286827589390971285842952193^2; CM field Q(sqrt(-3)) |
| other/Vesta | std-curves | 255 | True | t^2-4q = (-3) * 196462116142286827589391630752301449217^2; CM field Q(sqrt(-3)) |
| other/ssc-160 | std-curves | 160 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/ssc-192 | std-curves | 192 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/ssc-224 | std-curves | 224 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/ssc-256 | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/ssc-288 | std-curves | 288 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/ssc-320 | std-curves | 320 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/ssc-384 | std-curves | 384 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| other/ssc-512 | std-curves | 512 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| secg/secp112r1 | std-curves | 112 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| secg/secp112r2 | std-curves | 112 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| secg/secp128r1 | std-curves | 128 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| secg/secp128r2 | std-curves | 128 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| secg/secp160k1 | std-curves | 160 | True | t^2-4q = (-3) * 709316441754974472566021^2; CM field Q(sqrt(-3)) |
| secg/secp160r1 | std-curves | 160 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| secg/secp160r2 | std-curves | 160 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| secg/secp192k1 | std-curves | 192 | True | t^2-4q = (-3) * 34999138709524326971400529393^2; CM field Q(sqrt(-3)) |
| secg/secp192r1 | std-curves | 192 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-192) |
| secg/secp224k1 | std-curves | 224 | True | t^2-4q = (-3) * 2181384198222797443972610423981457^2; CM field Q(sqrt(-3)) |
| secg/secp224r1 | std-curves | 224 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-224) |
| secg/secp256k1 | std-curves | 256 | True | t^2-4q = (-3) * 303414439467246543595250775667605759171^2; CM field Q(sqrt(-3)) |
| secg/secp256r1 | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-256) |
| secg/secp384r1 | std-curves | 384 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-384) |
| secg/secp521r1 | std-curves | 521 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-521) |
| wtls/wap-wsg-idm-ecid-wtls12 | std-curves | 224 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-224) |
| wtls/wap-wsg-idm-ecid-wtls6 | std-curves | 112 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of secg/secp112r1) |
| wtls/wap-wsg-idm-ecid-wtls7 | std-curves | 160 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of secg/secp160r1) |
| wtls/wap-wsg-idm-ecid-wtls8 | std-curves | 112 | True | t^2-4q = (-3) * 22505355654482883^2; CM field Q(sqrt(-3)) |
| wtls/wap-wsg-idm-ecid-wtls9 | std-curves | 160 | True | t^2-4q = (-3) * 602889891024722752429129^2; CM field Q(sqrt(-3)) |
| x962/prime192v1 | std-curves | 192 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-192) |
| x962/prime192v2 | std-curves | 192 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| x962/prime192v3 | std-curves | 192 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| x962/prime239v1 | std-curves | 239 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| x962/prime239v2 | std-curves | 239 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| x962/prime239v3 | std-curves | 239 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 |
| x962/prime256v1 | std-curves | 256 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-256) |
| x963/ansip160k1 | std-curves | 160 | True | t^2-4q = (-3) * 709316441754974472566021^2; CM field Q(sqrt(-3)) (duplicate of secg/secp160k1) |
| x963/ansip160r1 | std-curves | 160 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of secg/secp160r1) |
| x963/ansip160r2 | std-curves | 160 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of secg/secp160r2) |
| x963/ansip192k1 | std-curves | 192 | True | t^2-4q = (-3) * 34999138709524326971400529393^2; CM field Q(sqrt(-3)) (duplicate of secg/secp192k1) |
| x963/ansip224k1 | std-curves | 224 | True | t^2-4q = (-3) * 2181384198222797443972610423981457^2; CM field Q(sqrt(-3)) (duplicate of secg/secp224k1) |
| x963/ansip224r1 | std-curves | 224 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-224) |
| x963/ansip256k1 | std-curves | 256 | True | t^2-4q = (-3) * 303414439467246543595250775667605759171^2; CM field Q(sqrt(-3)) (duplicate of secg/secp256k1) |
| x963/ansip384r1 | std-curves | 384 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-384) |
| x963/ansip521r1 | std-curves | 521 | True | no fundamental discriminant D_K with |D_K| <= 2000000 divides t^2-4q with square cofactor; hence |D_K| > 2000000 and every non-scalar endomorphism has degree >= 500000 (duplicate of nist/P-521) |

