# Exact CM discriminants (endosweep_dk_exact_20261016)

std-curves commit `77fe6e3585ca2c2225b59d7df24b7c775437276f`.  Every factor is proved prime by PARI `isprime`; `pN` is an N-digit prime written out in `dk_exact.json`.  No D_K here was checked against the literature (see the `std-curves` column for the one comparison made).

| curve | p bits | t | 4q−t² digits | factorisation of 4q−t² | squarefree part s | f | D_K | log2 \|D_K\| | least non-scalar degree ≈ \|D_K\|/4 | std-curves |
|:--|--:|--:|--:|:--|:--|:--|:--|--:|--:|:--|
| x962/prime239v2 | 239 | (37 digits) | 73 | 5^2 · 11 · 5830789 · p24 · p40 | (71 digits) | 5 | −(71 digits) | 235.78 | 2^233.78 | cm_disc and conductor: agrees |
| nums/ed-255-mers | 255 | (39 digits) | 78 | 2^2 · 443 · 647 · 40193 · p31 · p36 | (77 digits) | 2 | −(77 digits) | 254.77 | 2^252.77 | no cm_disc |
| nums/w-255-mers | 255 | (39 digits) | 78 | 13 · 17 · 739 · p27 · p46 | (78 digits) | 1 | −(78 digits) | 256.83 | 2^254.83 | cm_disc and conductor: agrees |
| nums/numsp256d1 | 256 | (38 digits) | 78 | 984952349 · p23 · p47 | (78 digits) | 1 | −(78 digits) | 258.0 | 2^256.0 | cm_disc and conductor: agrees |
| other/BADA55-R-256 | 256 | (39 digits) | 78 | 5^2 · p20 · p58 | (77 digits) | 5 | −(77 digits) | 252.69 | 2^250.69 | cm_disc and conductor: agrees |
| other/MDC201601 | 256 | (39 digits) | 77 | 2^2 · 7 · 1423 · 75193 · p27 · p42 | (77 digits) | 2 | −(77 digits) | 253.2 | 2^251.2 | no cm_disc |
| other/ssc-288 | 288 | (44 digits) | 87 | 29 · 239 · 30092263963 · p26 · p47 | (87 digits) | 1 | −(87 digits) | 288.16 | 2^286.16 | cm_disc and conductor: agrees |
| arkworks/ed_on_bw6_761 | 377 | (57 digits) | 114 | 2^5 · 83 · 139 · 179 · 383 · 7349 · p15 · p28 · p58 | (113 digits) | 2 | −(114 digits) | 376.51 | 2^374.51 | no cm_disc |
| nums/ed-383-mers | 383 | (58 digits) | 116 | 2^2 · 2819 · 1322369 · 526459501063 · 828591709009 · p15 · p26 · p43 | (116 digits) | 2 | −(116 digits) | 382.96 | 2^380.96 | no cm_disc |
| nums/ed-384-mont | 384 | (58 digits) | 117 | 2^2 · 13 · p17 · p24 · p75 | (116 digits) | 2 | −(116 digits) | 383.45 | 2^381.45 | no cm_disc |
| nums/w-384-mont | 384 | (58 digits) | 117 | 13 · 128191201 · 152102048827 · p18 · p29 · p50 | (117 digits) | 1 | −(117 digits) | 385.43 | 2^383.43 | no cm_disc |
| bn/bn510 | 510 | (77 digits) | 154 | 3 · 1307^2 · p37^2 · p37^2 | 3 | (77 digits) | -3 | 1.58 | 1 | cm_disc and conductor: agrees |
| nums/w-511-mers | 511 | (77 digits) | 155 | 7 · 1721 · p30 · p122 | (155 digits) | 1 | −(155 digits) | 512.85 | 2^510.85 | no cm_disc |
| gost/id-tc26-gost-3410-2012-512-paramSetC | 512 | (77 digits) | 155 | 2^2 · 139 · 149 · 2702671 · p20 · p124 | (155 digits) | 2 | −(155 digits) | 511.71 | 2^509.71 | no cm_disc |
| nums/w-512-mont | 512 | (77 digits) | 155 | 241 · 2178797 · p15 · p27 · p106 | (155 digits) | 1 | −(155 digits) | 513.85 | 2^511.85 | no cm_disc |
| other/ssc-512 | 512 | (78 digits) | 155 | 7^2 · 19 · 23 · 47 · 149 · 10955913739 · p23 · p114 | (153 digits) | 7 | −(153 digits) | 507.44 | 2^505.44 | no cm_disc |
| bls/BLS12-638 | 638 | (33 digits) | 193 | 3 · 7^2 · 67^4 · 79^2 · 5563^2 · 2099837^2 · 13273591^2 · p18^2 · p22^2 · p34^2 | 3 | (97 digits) | -3 | 1.58 | 1 | cm_disc and conductor: agrees |
| arkworks/bw6_767 | 767 | (116 digits) | 232 | 2^2 · 3 · 7^4 · 67^2 · 3607^2 · 2757659^2 · p16^2 · p22^2 · p65^2 | 3 | (116 digits) | -3 | 1.58 | 1 | no cm_disc |

## Who found each factor the survey did not

Every other factor came from the survey's `PARI factor(N, 2^32)`.  Both parts of a split carry the split's method (the found factor and its cofactor).

* **x962/prime239v2**: p24 — GMP-ECM 7.0.5 B1=50000 (driver tier 2); p40 — GMP-ECM 7.0.5 B1=50000 (driver tier 2)
* **nums/ed-255-mers**: p31 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (37 s wall); p36 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (37 s wall)
* **nums/w-255-mers**: p27 — GMP-ECM 7.0.5 B1=50000 (driver tier 2); p46 — GMP-ECM 7.0.5 B1=50000 (driver tier 2)
* **nums/numsp256d1**: p23 — GMP-ECM 7.0.5 B1=50000 (driver tier 2); p47 — GMP-ECM 7.0.5 B1=50000 (driver tier 2)
* **other/BADA55-R-256**: p20 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p58 — GMP-ECM 7.0.5 B1=11000 (driver tier 1)
* **other/MDC201601**: p27 — GMP-ECM 7.0.5 B1=50000 (driver tier 2); p42 — GMP-ECM 7.0.5 B1=50000 (driver tier 2)
* **other/ssc-288**: 30092263963 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p26 — GMP-ECM 7.0.5 B1=250000 (driver tier 3); p47 — GMP-ECM 7.0.5 B1=250000 (driver tier 3)
* **arkworks/ed_on_bw6_761**: p15 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p28 — GMP-ECM 7.0.5 B1=250000 (driver tier 3); p58 — GMP-ECM 7.0.5 B1=250000 (driver tier 3)
* **nums/ed-383-mers**: 526459501063 — GMP-ECM 7.0.5 B1=250000 (driver tier 3); 828591709009 — GMP-ECM 7.0.5 B1=50000 (driver tier 2); p15 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p26 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (33 s wall); p43 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (33 s wall)
* **nums/ed-384-mont**: p17 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p24 — GMP-ECM 7.0.5 B1=50000 (driver tier 2); p75 — GMP-ECM 7.0.5 B1=50000 (driver tier 2)
* **nums/w-384-mont**: 152102048827 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p18 — GMP-ECM 7.0.5 B1=50000 (driver tier 2); p29 — GMP-ECM 7.0.5 B1=250000 (driver tier 3); p50 — GMP-ECM 7.0.5 B1=250000 (driver tier 3)
* **bn/bn510**: p37 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (68 s wall); p37 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (68 s wall)
* **nums/w-511-mers**: p30 — GMP-ECM 7.0.5 B1=250000 (driver tier 3); p122 — GMP-ECM 7.0.5 B1=250000 (driver tier 3)
* **gost/id-tc26-gost-3410-2012-512-paramSetC**: p20 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p124 — GMP-ECM 7.0.5 B1=11000 (driver tier 1)
* **nums/w-512-mont**: p15 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p27 — GMP-ECM 7.0.5 B1=250000 (driver tier 3); p106 — GMP-ECM 7.0.5 B1=250000 (driver tier 3)
* **other/ssc-512**: 10955913739 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p23 — GMP-ECM 7.0.5 B1=50000 (driver tier 2); p114 — GMP-ECM 7.0.5 B1=50000 (driver tier 2)
* **bls/BLS12-638**: p18 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p22 — GMP-ECM 7.0.5 B1=50000 (driver tier 2); p34 — GMP-ECM 7.0.5 B1=50000 (driver tier 2)
* **arkworks/bw6_767**: p16 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p22 — GMP-ECM 7.0.5 B1=50000 (driver tier 2); p65 — GMP-ECM 7.0.5 B1=50000 (driver tier 2)

Excluded (already certified in research/endosweep_nist_20261006/factorizations.jsonl): nist/P-256, nist/P-384, nist/P-521, other/Curve25519.
