# Exact CM discriminants (endosweep_dk_exact_batch2_20261016)

std-curves commit `77fe6e3585ca2c2225b59d7df24b7c775437276f`.  Every factor is proved prime by PARI `isprime`; `pN` is an N-digit prime written out in `dk_exact.json`.  No D_K here was checked against the literature (see the `std-curves` column for the one comparison made).

| curve | p bits | t | 4q−t² digits | factorisation of 4q−t² | squarefree part s | f | D_K | log2 \|D_K\| | least non-scalar degree ≈ \|D_K\|/4 | std-curves |
|:--|--:|--:|--:|:--|:--|:--|:--|--:|--:|:--|
| oscaa/SM2 | 256 | (39 digits) | 78 | 19 · p36 · p41 | (78 digits) | 1 | −(78 digits) | 257.88 | 2^255.88 | no cm_disc |
| nums/ed-382-mont | 382 | (58 digits) | 116 | 2^2 · 31 · 356399 · p28 · p29 · p52 | (115 digits) | 2 | −(115 digits) | 381.02 | 2^379.02 | no cm_disc |
| brainpool/brainpoolP384r1 | 384 | (58 digits) | 116 | 11^2 · 6857 · 379795560371 · p44 · p55 | (114 digits) | 11 | −(114 digits) | 377.45 | 2^375.45 | no cm_disc |
| nums/numsp512t1 | 512 | (78 digits) | 155 | 2^2 · 23227 · 480647 · 11602586981 · p15 · p18 · p29 · p37 · p38 | (154 digits) | 2 | −(154 digits) | 511.07 | 2^509.07 | no cm_disc |
| bn/bn606 | 606 | (92 digits) | 183 | 3^3 · p14^2 · p34^2 · p44^2 | 3 | (92 digits) | -3 | 1.58 | 1 | no cm_disc |
| arkworks/cp6_782 | 782 | (117 digits) | 236 | 2^10 · 3^3 · 113 · 2879^2 · p22^2 · p33^2 · p58^2 | 339 | (117 digits) | -339 | 8.41 | 85 | no cm_disc |

## Who found each factor the survey did not

Every other factor came from the survey's `PARI factor(N, 2^32)`.  Both parts of a split carry the split's method (the found factor and its cofactor).

* **oscaa/SM2**: p36 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (94 s wall); p41 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (94 s wall)
* **nums/ed-382-mont**: p28 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (113 s wall); p29 — GMP-ECM 7.0.5 B1=250000 (driver tier 3); p52 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (113 s wall)
* **brainpool/brainpoolP384r1**: 379795560371 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p44 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (1018 s wall); p55 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (1018 s wall)
* **nums/numsp512t1**: 11602586981 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p15 — GMP-ECM 7.0.5 B1=50000 (driver tier 2); p18 — PARI factorint (0 s); p29 — PARI factorint (0 s); p37 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (124 s wall); p38 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (124 s wall)
* **bn/bn606**: p14 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p34 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (90 s wall); p44 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (90 s wall)
* **arkworks/cp6_782**: p22 — GMP-ECM 7.0.5 B1=50000 (driver tier 2); p33 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (423 s wall); p58 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (423 s wall)

Excluded (already certified in research/endosweep_nist_20261006/factorizations.jsonl): nist/P-256, nist/P-384, nist/P-521, other/Curve25519.

Excluded (already certified in research/endosweep_dk_exact_20261016/factorizations.jsonl): arkworks/bw6_767, arkworks/ed_on_bw6_761, bls/BLS12-638, bn/bn510, gost/id-tc26-gost-3410-2012-512-paramSetC, nums/ed-255-mers, nums/ed-383-mers, nums/ed-384-mont, nums/numsp256d1, nums/w-255-mers, nums/w-384-mont, nums/w-511-mers, nums/w-512-mont, other/BADA55-R-256, other/MDC201601, other/ssc-288, other/ssc-512, x962/prime239v2.
