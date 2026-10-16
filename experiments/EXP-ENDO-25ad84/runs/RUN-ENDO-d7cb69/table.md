# Isogenous-model screen

ells 2,3,5,7,11,13, depth 2, 200 random scalars per cost, |D_K| bound 1048576. Costs are modelled M_eq (M + S) in curvesweep's wNAF model; `persistent` keeps the point on the neighbour, `one-shot` charges forward chain, dual chain, model maps and the scalar adjustment.

| curve | role | bits | h | E model (baseline M_eq) | nodes | best neighbour | path | persistent | one-shot | verified | D_K, conductors | crater GLV one-shot |
|:--|:--|--:|--:|:--|--:|:--|:--|--:|--:|:--|:--|--:|
| control+: 3-isogenous neighbour of NIST P-256 | control+model | 256 | 1 | weierstrass (3329.4) | 24 | weierstrass (2820.8) | 3 | +15.28% | +14.46% | yes (8 k) | > 1048576 |  |
| control+ascent: 11-descendant of a j = 0 curve (256-bit) | control+ascent | 256 | 3 | weierstrass (2796.5) | 57 | weierstrass (2544.5) | 11 | +9.01% | +5.15% | yes (8 k) | -3, f_pi=107347805839776229312674989257559019533, f_E=unresolved | +32.51% via 11 |
| secp256k1 | population | 256 | 1 | weierstrass+GLV(unit) (1793.7) | 2 | weierstrass (3329.4) | 3 | -85.62% | -86.95% |  | -3, f_pi=303414439467246543595250775667605759171, f_E=1 |  |
| NIST P-256 | control- | 256 | 1 | weierstrass (2820.8) | 24 | weierstrass (2820.8) | 5 | +0.00% | -1.70% |  | > 1048576 |  |
| NIST P-384 | population | 384 | 1 | weierstrass (4165.8) | 1 | none |  |  |  |  | > 1048576 |  |
| NIST P-521 | population | 521 | 1 | weierstrass (5574.5) | 18 | weierstrass (5574.5) | 5 | +0.00% | -0.86% |  | > 1048576 |  |
| brainpoolP256r1 | population | 256 | 1 | weierstrass (2816.1) | 23 | weierstrass (2816.1) | 5 | +0.00% | -1.70% |  | > 1048576 |  |
| SM2 | population | 256 | 1 | weierstrass (2820.8) | 5 | weierstrass (2820.8) | 7 | +0.00% | -2.45% |  | > 1048576 |  |
| GOST CryptoPro-A | population | 256 | 1 | weierstrass (2820.8) | 5 | weierstrass (2820.8) | 7 | +0.00% | -2.45% |  | > 1048576 |  |
| GOST CryptoPro-B | population | 256 | 1 | weierstrass (2810.7) | 5 | weierstrass (2810.7) | 5 | +0.00% | -1.71% |  | -619, f_pi=4646402506017662432554672533504826433, f_E=unresolved |  |
| GOST CryptoPro-C | population | 256 | 1 | weierstrass (2815.0) | 8 | weierstrass (2815.0) | 11 | +0.00% | -3.94% |  | > 1048576 |  |
| GOST 2001 test curve | population | 256 | 1 | weierstrass (3063.9) | 64 | weierstrass (2810.7) | 5 | +8.26% | +6.70% | yes (8 k) | -915, f_pi=5814239006315534931045933045806333847, f_E=unresolved |  |
| Curve25519 | control- | 255 | 8 | edwards_a=-1 (2391.2) | 4 | edwards_a=-1 (2391.2) | 2 | +0.00% | -22.54% |  | > 1048576 |  |
| Ed448-Goldilocks | population | 448 | 4 | edwards_a=-1 (4176.9) | 19 | edwards_a=-1 (4176.9) | 2·2 | +0.00% | -22.62% |  | > 1048576 |  |
| Curve1174 | population | 251 | 4 | edwards_a=-1 (2362.2) | 33 | edwards_a=-1 (2362.2) | 2·2 | +0.00% | -23.33% |  | > 1048576 |  |
| Curve41417 | population | 414 | 8 | edwards_a=-1 (3857.8) | 4 | edwards_a=-1 (3857.8) | 2 | +0.00% | -22.21% |  | > 1048576 |  |
| E-521 | population | 521 | 4 | edwards_a=-1 (4845.4) | 20 | edwards_a=-1 (4845.4) | 2·2 | +0.00% | -22.54% |  | > 1048576 |  |
| M-511 | population | 511 | 8 | edwards_a=-1 (4742.3) | 14 | edwards_a=-1 (4742.3) | 2 | +0.00% | -22.10% |  | > 1048576 |  |
| BN254 G1 | population | 254 | 1 | weierstrass+GLV(unit) (1778.7) | 1 | none |  |  |  |  | -3, f_pi=147946756881789319010696353538189108491, f_E=1 |  |
| BLS12-381 G1 | population | 381 | 76329603384216526031706109802092473003 | weierstrass+GLV(unit) (1787.3) | 5 | weierstrass (2810.0) | 11 | -57.22% | -63.43% |  | -3, f_pi=2310096550715768212670172227226928237551693238409523516757, f_E=1 |  |
| anssi/FRP256v1 | population | 256 | 1 | weierstrass (2819.9) | 13 | weierstrass (2819.9) | 7 | +0.00% | -2.45% |  | > 1048576 |  |
| bls/BLS12-377 | population | 377 | 30631250834960419227450344600217059328 | weierstrass+GLV(unit) (1768.7) | 52 | edwards_a=-1 (2394.3) | 2 | -35.37% | -68.56% |  | -3, f_pi=587269870971281361444171168277668240640243801025419411456, f_E=1 |  |
| bls/BLS12-446 | population | 446 | 267785939737784928360481681640896166738700972 | weierstrass+GLV(unit) (2057.3) | 2 | edwards_a=-1 (2823.3) | 2 | -37.23% | -70.63% |  | -3, f_pi=15180017722556942872710858686172241542425226563119817904740305163606, f_E=1 |  |
| bls/BLS12-455 | population | 455 | 1902997377317904285509030108837873050145782443 | weierstrass+GLV(unit) (2087.6) | 50 | weierstrass (3334.2) | 3 | -59.71% | -61.01% |  | -3, f_pi=287572867293678436974519977531226436303080379672880577582937484382891, f_E=1 |  |
| bls/BLS24-477 | population | 477 | 20219334706522233036632757675 | weierstrass+GLV(unit) (2572.5) | 3 | weierstrass (4147.3) | 5 | -61.22% | -63.08% |  | -3, f_pi=604128092931004996153900356638872198640435149234420528912987303159267285, f_E=1 |  |
| bls/Bandersnatch | population | 255 | 4 | edwards_general (2747.0) | 13 | edwards_general (2747.0) | 2 | +0.00% | -16.38% |  | -8, f_pi=21482638764116277775478679919733259912, f_E=unresolved |  |
| bn/bn158 | population | 158 | 1 | weierstrass+GLV(unit) (1138.8) | 1 | none |  |  |  |  | -3, f_pi=454233058418789397299203, f_E=1 |  |
| bn/bn190 | population | 190 | 1 | weierstrass+GLV(unit) (1357.0) | 1 | none |  |  |  |  | -3, f_pi=29710571568175225982381195267, f_E=1 |  |
| bn/bn222 | population | 222 | 1 | weierstrass+GLV(unit) (1570.4) | 5 | weierstrass (2449.4) | 11 | -55.97% | -63.04% |  | -3, f_pi=1943310227059934888513759537528843, f_E=1 |  |
| bn/bn254 | population | 254 | 1 | weierstrass+GLV(unit) (1774.5) | 2 | weierstrass (2792.6) | 3 | -57.37% | -58.89% |  | -3, f_pi=129607518034317099886745702645398241283, f_E=1 |  |
| bn/bn286 | population | 286 | 1 | weierstrass+GLV(unit) (1970.2) | 2 | weierstrass (3133.9) | 3 | -59.06% | -60.44% |  | -3, f_pi=8366863340207706741294993301075392630620163, f_E=1 |  |
| bn/bn318 | population | 318 | 1 | weierstrass+GLV(unit) (2165.9) | 2 | weierstrass (3474.2) | 3 | -60.40% | -61.65% |  | -3, f_pi=548079839685593379889101977298739683457859846211, f_E=1 |  |
| bn/bn350 | population | 350 | 1 | weierstrass+GLV(unit) (2365.3) | 5 | weierstrass (3805.5) | 3 | -60.89% | -62.03% |  | -3, f_pi=35917316178020966140770026339278758006907024019816451, f_E=1 |  |
| bn/bn382 | population | 382 | 1 | weierstrass+GLV(unit) (2565.2) | 2 | weierstrass (4134.1) | 3 | -61.16% | -62.21% |  | -3, f_pi=2353932232174051770881173201697930752584630523839501041667, f_E=1 |  |
| bn/bn414 | population | 414 | 1 | weierstrass+GLV(unit) (2762.9) | 2 | weierstrass (4465.0) | 3 | -61.61% | -62.58% |  | -3, f_pi=154267229207681125708793071161632042239063797942298639324938243, f_E=1 |  |
| bn/bn446 | population | 446 | 1 | weierstrass+GLV(unit) (2958.5) | 1 | none |  |  |  |  | -3, f_pi=10109980000181489923001201093401911741712157040574514822068840693771, f_E=1 |  |
| bn/bn478 | population | 478 | 1 | weierstrass+GLV(unit) (3158.0) | 21 | weierstrass (5125.0) | 3 | -62.29% | -63.14% |  | -3, f_pi=662567649291894123450065105820326670768093618471357310296643630025146371, f_E=1 |  |
| bn/bn510 | population | 510 | 1 | weierstrass+GLV(unit) (3358.4) | 1 | none |  |  |  |  | -3, f_pi=43422033463993573283847164979847511362163190678038904032036848688647949516803, f_E=1 |  |
| brainpool/brainpoolP160r1 | population | 160 | 1 | weierstrass (1792.7) | 18 | weierstrass (1792.7) | 3·3 | +0.00% | -3.29% |  | > 1048576 |  |
| brainpool/brainpoolP192r1 | population | 192 | 1 | weierstrass (2132.4) | 18 | weierstrass (2132.4) | 3 | +0.00% | -1.27% |  | > 1048576 |  |
| brainpool/brainpoolP224r1 | population | 224 | 1 | weierstrass (2478.0) | 4 | weierstrass (2478.0) | 5 | +0.00% | -1.94% |  | > 1048576 |  |
| brainpool/brainpoolP320r1 | population | 320 | 1 | weierstrass (3500.2) | 13 | weierstrass (3500.2) | 5 | +0.00% | -1.37% |  | > 1048576 |  |
| brainpool/brainpoolP384r1 | population | 384 | 1 | weierstrass (4156.2) | 41 | weierstrass (4156.2) | 7 | +0.00% | -1.66% |  | > 1048576 |  |
| brainpool/brainpoolP512r1 | population | 512 | 1 | weierstrass (5474.4) | 13 | weierstrass (5474.4) | 13 | +0.00% | -2.41% |  | > 1048576 |  |
| gost/gost512 | population | 511 | 1 | weierstrass (5461.9) | 13 | weierstrass (5461.9) | 5 | +0.00% | -0.88% |  | > 1048576 |  |
| gost/id-tc26-gost-3410-12-512-paramSetA | population | 512 | 1 | weierstrass (5478.4) | 12 | weierstrass (5478.4) | 7 | +0.00% | -1.26% |  | > 1048576 |  |
| gost/id-tc26-gost-3410-12-512-paramSetB | population | 512 | 1 | weierstrass (5469.9) | 29 | weierstrass (5469.9) | 5 | +0.00% | -0.88% |  | > 1048576 |  |
| gost/id-tc26-gost-3410-2012-256-paramSetA | population | 256 | 4 | edwards_a=-1 (2409.2) | 14 | edwards_a=-1 (2409.2) | 2·2 | +0.00% | -23.16% |  | > 1048576 |  |
| gost/id-tc26-gost-3410-2012-512-paramSetC | population | 512 | 4 | edwards_a=-1 (4758.5) | 4 | edwards_a=-1 (4758.5) | 2·2 | +0.00% | -22.49% |  | > 1048576 |  |
| mnt/mnt1 | population | 170 | 15337 | weierstrass (2054.5) | 1 | none |  |  |  |  | -19, f_pi=6915889423298038776451801, f_E=unresolved |  |
| mnt/mnt2/1 | population | 159 | 1 | weierstrass (1779.2) | 10 | weierstrass (1779.2) | 5 | +0.00% | -2.70% |  | -91, f_pi=151115727451828644755795, f_E=unresolved |  |
| mnt/mnt2/2 | population | 159 | 1 | weierstrass (1779.2) | 10 | weierstrass (1779.2) | 5 | +0.00% | -2.70% |  | -91, f_pi=151115727451828644755795, f_E=unresolved |  |
| mnt/mnt3/1 | population | 160 | 1 | weierstrass (2103.7) | 64 | weierstrass (1788.6) | 5 | +14.98% | +12.70% | yes (8 k) | -139, f_pi=151115727451828644749125, f_E=unresolved |  |
| mnt/mnt3/2 | population | 160 | 1 | weierstrass (1788.6) | 64 | weierstrass (1788.6) | 5 | +0.00% | -2.68% |  | -139, f_pi=151115727451828644749125, f_E=unresolved |  |
| mnt/mnt3/3 | population | 160 | 1 | weierstrass (2103.7) | 64 | weierstrass (1788.6) | 5 | +14.98% | +12.70% | yes (8 k) | -139, f_pi=151115727451828644749125, f_E=unresolved |  |
| mnt/mnt4 | population | 240 | 1 | weierstrass (2644.5) | 1 | none |  |  |  |  | -163, f_pi=166153499473114484112975882535041529, f_E=unresolved |  |
| mnt/mnt5/1 | population | 240 | 1 | weierstrass (2648.2) | 15 | weierstrass (2648.2) | 5 | +0.00% | -1.81% |  | -211, f_pi=166153499473114484112975882535035935, f_E=unresolved |  |
| mnt/mnt5/2 | population | 240 | 1 | weierstrass (3124.4) | 15 | weierstrass (2648.2) | 5 | +15.24% | +13.71% | yes (8 k) | -211, f_pi=166153499473114484112975882535035935, f_E=unresolved |  |
| mnt/mnt5/3 | population | 240 | 1 | weierstrass (3124.4) | 15 | weierstrass (2648.2) | 5 | +15.24% | +13.71% | yes (8 k) | -211, f_pi=166153499473114484112975882535035935, f_E=unresolved |  |
| nist/P-192 | population | 192 | 1 | weierstrass (2138.0) | 12 | weierstrass (2138.0) | 11 | +0.00% | -5.19% |  | > 1048576 |  |
| nist/P-224 | population | 224 | 1 | weierstrass (2478.4) | 20 | weierstrass (2478.4) | 3·3 | +0.00% | -2.38% |  | > 1048576 |  |
| nums/numsp256d1 | population | 256 | 1 | weierstrass (2820.8) | 5 | weierstrass (2820.8) | 13 | +0.00% | -4.68% |  | > 1048576 |  |
| nums/numsp256t1 | population | 256 | 4 | edwards_a=-1 (2408.9) | 20 | edwards_a=-1 (2408.9) | 2·2 | +0.00% | -23.12% |  | > 1048576 |  |
| nums/numsp384d1 | population | 384 | 1 | weierstrass (4165.8) | 25 | weierstrass (4165.8) | 11 | +0.00% | -2.67% |  | > 1048576 |  |
| nums/numsp384t1 | population | 384 | 4 | edwards_a=-1 (3590.8) | 19 | edwards_a=-1 (3590.8) | 2·2 | +0.00% | -22.64% |  | > 1048576 |  |
| nums/numsp512d1 | population | 512 | 1 | weierstrass (5478.4) | 1 | none |  |  |  |  | > 1048576 |  |
| nums/numsp512t1 | population | 512 | 4 | edwards_a=-1 (4758.5) | 4 | edwards_a=-1 (4758.5) | 2·2 | +0.00% | -22.49% |  | > 1048576 |  |
| nums/ed-256-mont | population | 256 | 4 | edwards_a=-1 (2408.8) | 4 | edwards_a=-1 (2408.8) | 2·2 | +0.00% | -23.21% |  | > 1048576 |  |
| nums/ed-254-mont | population | 254 | 4 | edwards_a=-1 (2389.3) | 4 | edwards_a=-1 (2389.3) | 2·2 | +0.00% | -23.06% |  | > 1048576 |  |
| nums/ed-255-mers | population | 255 | 4 | edwards_a=-1 (2399.0) | 4 | edwards_a=-1 (2399.0) | 2·2 | +0.00% | -23.05% |  | > 1048576 |  |
| nums/ed-384-mont | population | 384 | 4 | edwards_a=-1 (3585.8) | 14 | edwards_a=-1 (3585.8) | 2·2 | +0.00% | -22.67% |  | > 1048576 |  |
| nums/ed-382-mont | population | 382 | 4 | edwards_a=-1 (3572.9) | 10 | edwards_a=-1 (3572.9) | 2·2 | +0.00% | -22.73% |  | > 1048576 |  |
| nums/ed-383-mers | population | 383 | 4 | edwards_a=-1 (3581.5) | 10 | edwards_a=-1 (3581.5) | 2·2 | +0.00% | -22.67% |  | > 1048576 |  |
| nums/ed-512-mont | population | 512 | 4 | edwards_a=-1 (4758.1) | 34 | edwards_a=-1 (4758.1) | 2·2 | +0.00% | -22.43% |  | > 1048576 |  |
| nums/ed-510-mont | population | 510 | 4 | edwards_a=-1 (4740.2) | 20 | edwards_a=-1 (4740.2) | 2·2 | +0.00% | -22.51% |  | > 1048576 |  |
| nums/ed-511-mers | population | 511 | 4 | edwards_a=-1 (4749.2) | 6 | edwards_a=-1 (4749.2) | 2·2 | +0.00% | -22.49% |  | > 1048576 |  |
| nums/w-256-mont | population | 256 | 1 | weierstrass (2820.6) | 8 | weierstrass (2820.6) | 7·13 | +0.00% | -8.90% |  | > 1048576 |  |
| nums/w-254-mont | population | 254 | 1 | weierstrass (2798.9) | 8 | weierstrass (3303.5) | 7 | -18.03% | -20.39% |  | > 1048576 |  |
| nums/w-255-mers | population | 255 | 1 | weierstrass (2810.6) | 8 | weierstrass (2810.6) | 11 | +0.00% | -3.95% |  | > 1048576 |  |
| nums/w-384-mont | population | 384 | 1 | weierstrass (4159.7) | 2 | weierstrass (4922.5) | 13 | -18.34% | -21.44% |  | > 1048576 |  |
| nums/w-382-mont | population | 382 | 1 | weierstrass (4143.4) | 8 | weierstrass (4143.4) | 7 | +0.00% | -1.67% |  | > 1048576 |  |
| nums/w-383-mers | population | 383 | 1 | weierstrass (4154.1) | 1 | none |  |  |  |  | > 1048576 |  |
| nums/w-512-mont | population | 512 | 1 | weierstrass (5477.9) | 1 | none |  |  |  |  | > 1048576 |  |
| nums/w-510-mont | population | 510 | 1 | weierstrass (5456.1) | 13 | weierstrass (5456.1) | 11 | +0.00% | -2.03% |  | > 1048576 |  |
| nums/w-511-mers | population | 511 | 1 | weierstrass (5467.4) | 8 | weierstrass (5467.4) | 11 | +0.00% | -2.03% |  | > 1048576 |  |
| other/M-221 | population | 221 | 8 | edwards_a=-1 (2072.5) | 4 | edwards_a=-1 (2072.5) | 2 | +0.00% | -22.77% |  | > 1048576 |  |
| other/M-383 | population | 383 | 8 | edwards_a=-1 (3573.1) | 34 | edwards_a=-1 (3573.1) | 2 | +0.00% | -22.17% |  | > 1048576 |  |
| other/E-222 | population | 222 | 4 | edwards_a=-1 (2089.6) | 4 | edwards_a=-1 (2089.6) | 2·2 | +0.00% | -23.45% |  | > 1048576 |  |
| other/E-382 | population | 382 | 4 | edwards_a=-1 (3572.9) | 9 | edwards_a=-1 (3572.9) | 2·2 | +0.00% | -22.70% |  | > 1048576 |  |
| other/Curve448 | population | 448 | 4 | edwards_a=-1 (4176.9) | 19 | edwards_a=-1 (4176.9) | 2·2 | +0.00% | -22.62% |  | > 1048576 |  |
| other/Curve22103 | population | 221 | 8 | edwards_a=-1 (2072.2) | 10 | edwards_a=-1 (2072.2) | 2 | +0.00% | -22.78% |  | > 1048576 |  |
| other/Curve4417 | population | 226 | 4 | edwards_a=-1 (2128.0) | 37 | edwards_a=-1 (2128.0) | 2·2 | +0.00% | -23.54% |  | > 1048576 |  |
| other/Curve383187 | population | 383 | 8 | edwards_a=-1 (3573.1) | 10 | edwards_a=-1 (3573.1) | 2 | +0.00% | -22.17% |  | > 1048576 |  |
| other/Fp254BNa | population | 254 | 1 | weierstrass+GLV(unit) (1776.7) | 1 | none |  |  |  |  | -3, f_pi=126611883464401272127243293666542878721, f_E=1 |  |
| other/Fp224BN | population | 224 | 1 | weierstrass+GLV(unit) (1588.8) | 5 | weierstrass (2922.8) | 11 | -83.96% | -90.76% |  | -3, f_pi=5192296858534689506442115857736067, f_E=1 |  |
| other/Fp256BN | population | 256 | 1 | weierstrass+GLV(unit) (1795.6) | 1 | none |  |  |  |  | -3, f_pi=340282366920936614181528116269263699971, f_E=1 |  |
| other/Fp384BN | population | 384 | 1 | weierstrass+GLV(unit) (2584.4) | 1 | none |  |  |  |  | -3, f_pi=6277101735386680763835754795151022476645729035004851856003, f_E=1 |  |
| other/Fp512BN | population | 512 | 1 | weierstrass+GLV(unit) (3364.3) | 1 | none |  |  |  |  | -3, f_pi=115792089237316195423570985008687840101659558519570290085463645789117669918083, f_E=1 |  |
| other/ssc-160 | population | 160 | 1 | weierstrass (1792.6) | 8 | weierstrass (1792.6) | 3 | +0.00% | -1.51% |  | > 1048576 |  |
| other/ssc-192 | population | 192 | 1 | weierstrass (2132.9) | 5 | weierstrass (2132.9) | 11 | +0.00% | -5.20% |  | > 1048576 |  |
| other/ssc-224 | population | 224 | 1 | weierstrass (2478.6) | 18 | weierstrass (2478.6) | 5 | +0.00% | -1.94% |  | > 1048576 |  |
| other/ssc-256 | population | 256 | 1 | weierstrass (2818.3) | 7 | weierstrass (2818.3) | 3·3 | +0.00% | -2.09% |  | > 1048576 |  |
| other/ssc-288 | population | 288 | 1 | weierstrass (3160.5) | 25 | weierstrass (3160.5) | 7 | +0.00% | -2.18% |  | > 1048576 |  |
| other/ssc-320 | population | 320 | 1 | weierstrass (3499.1) | 20 | weierstrass (3499.1) | 3 | +0.00% | -0.77% |  | > 1048576 |  |
| other/ssc-384 | population | 384 | 1 | weierstrass (4161.5) | 15 | weierstrass (4161.5) | 3 | +0.00% | -0.65% |  | > 1048576 |  |
| other/ssc-512 | population | 512 | 1 | weierstrass (5476.4) | 9 | weierstrass (5476.4) | 7 | +0.00% | -1.26% |  | > 1048576 |  |
| other/Tweedledum | population | 255 | 1 | weierstrass+GLV(unit) (1780.6) | 1 | none |  |  |  |  | -3, f_pi=196462116142286827589390971285842952193, f_E=1 |  |
| other/Tweedledee | population | 255 | 1 | weierstrass+GLV(unit) (1784.7) | 1 | none |  |  |  |  | -3, f_pi=196462116142286827589390971285842952193, f_E=1 |  |
| other/JubJub | population | 255 | 8 | edwards_a=-1 (2389.1) | 10 | edwards_a=-1 (2389.1) | 2 | +0.00% | -18.84% |  | > 1048576 |  |
| other/Pallas | population | 255 | 1 | weierstrass+GLV(unit) (1777.5) | 2 | weierstrass (3304.7) | 3 | -85.92% | -87.27% |  | -3, f_pi=196462116142286827589391630752301449217, f_E=1 |  |
| other/Vesta | population | 255 | 1 | weierstrass+GLV(unit) (1777.0) | 2 | weierstrass (3304.7) | 3 | -85.97% | -87.32% |  | -3, f_pi=196462116142286827589391630752301449217, f_E=1 |  |
| other/MDC201601 | population | 256 | 4 | edwards_a=-1 (2408.2) | 26 | edwards_a=-1 (2408.2) | 2·2 | +0.00% | -18.44% |  | > 1048576 |  |
| other/BADA55-R-256 | population | 256 | 1 | weierstrass (2819.9) | 17 | weierstrass (2819.9) | 5 | +0.00% | -1.70% |  | > 1048576 |  |
| other/BADA55-VR-224 | population | 224 | 1 | weierstrass (2478.4) | 5 | weierstrass (2922.8) | 13 | -17.93% | -23.14% |  | > 1048576 |  |
| other/BADA55-VR-256 | population | 256 | 1 | weierstrass (2820.8) | 13 | weierstrass (2820.8) | 11 | +0.00% | -3.94% |  | > 1048576 |  |
| other/BADA55-VR-384 | population | 384 | 1 | weierstrass (4165.8) | 8 | weierstrass (4165.8) | 5 | +0.00% | -1.15% |  | > 1048576 |  |
| other/BADA55-VPR-224 | population | 224 | 1 | weierstrass (2922.8) | 13 | weierstrass (2478.4) | 5·5 | +15.20% | +11.44% | yes (8 k) | > 1048576 |  |
| other/BADA55-VPR2-224 | population | 224 | 1 | weierstrass (2922.8) | 5 | weierstrass (2922.8) | 5 | +0.00% | -1.54% |  | > 1048576 |  |
| other/Tom-256 | population | 256 | 1 | weierstrass (2820.8) | 25 | weierstrass (2820.8) | 3 | +0.00% | -0.96% |  | -4155, f_pi=7019618127640898221939468283479924503, f_E=unresolved |  |
| other/Tom-384 | population | 384 | 1 | weierstrass (4929.5) | 45 | weierstrass (4165.8) | 5 | +15.49% | +14.52% | yes (8 k) | -619, f_pi=380201093441490505678902542719199835054253522446560116525, f_E=unresolved |  |
| secg/secp112r1 | population | 112 | 1 | weierstrass (1283.0) | 5 | weierstrass (1283.0) | 7 | +0.00% | -5.38% |  | > 1048576 |  |
| secg/secp112r2 | population | 112 | 4 | edwards_a=-1 (1063.7) | 34 | edwards_a=-1 (1063.7) | 2·2 | +0.00% | -20.87% |  | > 1048576 |  |
| secg/secp128r1 | population | 128 | 1 | weierstrass (1456.7) | 5 | weierstrass (1456.7) | 7 | +0.00% | -4.74% |  | > 1048576 |  |
| secg/secp128r2 | population | 128 | 4 | edwards_a=-1 (1214.9) | 20 | edwards_a=-1 (1214.9) | 2·2 | +0.00% | -25.11% |  | > 1048576 |  |
| secg/secp160k1 | population | 160 | 1 | weierstrass+GLV(unit) (1160.1) | 3 | weierstrass (1792.3) | 7 | -54.50% | -60.44% |  | -3, f_pi=709316441754974472566021, f_E=1 |  |
| secg/secp160r1 | population | 160 | 1 | weierstrass (1792.3) | 8 | weierstrass (1792.3) | 13 | +0.00% | -7.36% |  | > 1048576 |  |
| secg/secp160r2 | population | 160 | 1 | weierstrass (1792.3) | 1 | none |  |  |  |  | > 1048576 |  |
| secg/secp192k1 | population | 192 | 1 | weierstrass+GLV(unit) (1378.8) | 1 | none |  |  |  |  | -3, f_pi=34999138709524326971400529393, f_E=1 |  |
| secg/secp224k1 | population | 224 | 1 | weierstrass+GLV(unit) (1588.0) | 5 | weierstrass (2480.0) | 3·3 | -56.17% | -59.89% |  | -3, f_pi=2181384198222797443972610423981457, f_E=1 |  |
| wtls/wap-wsg-idm-ecid-wtls8 | population | 112 | 1 | weierstrass+GLV(unit) (837.9) | 64 | weierstrass (1283.3) | 3 | -53.16% | -56.38% |  | -3, f_pi=22505355654482883, f_E=1 |  |
| wtls/wap-wsg-idm-ecid-wtls9 | population | 160 | 1 | weierstrass+GLV(unit) (1159.1) | 1 | none |  |  |  |  | -3, f_pi=602889891024722752429129, f_E=1 |  |
| x962/prime192v2 | population | 192 | 1 | weierstrass (2138.0) | 8 | weierstrass (2138.0) | 5 | +0.00% | -2.25% |  | > 1048576 |  |
| x962/prime192v3 | population | 192 | 1 | weierstrass (2138.0) | 8 | weierstrass (2138.0) | 13 | +0.00% | -6.17% |  | > 1048576 |  |
| x962/prime239v1 | population | 239 | 1 | weierstrass (2638.2) | 1 | none |  |  |  |  | > 1048576 |  |
| x962/prime239v2 | population | 239 | 1 | weierstrass (2638.2) | 9 | weierstrass (2638.2) | 5·5 | +0.00% | -4.17% |  | > 1048576 |  |
| x962/prime239v3 | population | 239 | 1 | weierstrass (2638.2) | 2 | weierstrass (3112.8) | 5 | -17.99% | -19.70% |  | > 1048576 |  |
