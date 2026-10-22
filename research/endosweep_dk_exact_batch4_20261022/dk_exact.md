# Exact CM discriminants (endosweep_dk_exact_batch4_20261022)

std-curves commit `77fe6e3585ca2c2225b59d7df24b7c775437276f`.  Every factor is proved prime by PARI `isprime`; `pN` is an N-digit prime written out in `dk_exact.json`.  No D_K here was checked against the literature (see the `std-curves` column for the one comparison made).

| curve | p bits | t | 4q−t² digits | factorisation of 4q−t² | squarefree part s | f | D_K | log2 \|D_K\| | least non-scalar degree ≈ \|D_K\|/4 | std-curves |
|:--|--:|--:|--:|:--|:--|:--|:--|--:|--:|:--|
| nums/numsp384d1 | 384 | (58 digits) | 117 | p50 · p67 | (117 digits) | 1 | −(117 digits) | 385.99 | 2^383.99 | no cm_disc |
| other/Curve41417 | 414 | (63 digits) | 125 | 2^2 · 3607 · p53 · p69 | (125 digits) | 2 | −(125 digits) | 413.21 | 2^411.21 | no cm_disc |
| nums/ed-510-mont | 510 | (77 digits) | 154 | 2^2 · 154799 · p40 · p109 | (154 digits) | 2 | −(154 digits) | 509.23 | 2^507.23 | no cm_disc |
| other/M-511 | 511 | (77 digits) | 155 | 2^4 · 7 · p14 · p39 · p101 | (154 digits) | 2 | −(154 digits) | 510.54 | 2^508.54 | no cm_disc |
| nums/numsp512d1 | 512 | (77 digits) | 155 | 29 · 43 · p33 · p119 | (155 digits) | 1 | −(155 digits) | 513.84 | 2^511.84 | no cm_disc |
| other/E-521 | 521 | (79 digits) | 158 | 2^2 · 47 · 23658857317 · p34 · p53 · p59 | (157 digits) | 2 | −(157 digits) | 520.9 | 2^518.9 | no cm_disc |
| arkworks/ed_on_mnt4_753 | 753 | (113 digits) | 228 | 2^5 · 751 · p21 · p25 · p30 · p149 | (227 digits) | 2 | −(227 digits) | 752.82 | 2^750.82 | no cm_disc |

## Who found each factor the survey did not

Every other factor came from the survey's `PARI factor(N, 2^32)`.  Both parts of a split carry the split's method (the found factor and its cofactor).

* **nums/numsp384d1**: p50 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (4994 s wall); p67 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (4994 s wall)
* **other/Curve41417**: p53 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (1463 s wall); p69 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (1463 s wall)
* **nums/ed-510-mont**: p40 — GMP-ECM 7.0.5 B1=3000000 (driver tier 5); p109 — GMP-ECM 7.0.5 B1=3000000 (driver tier 5)
* **other/M-511**: p14 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p39 — GMP-ECM 7.0.5 B1=3000000 (driver tier 5); p101 — GMP-ECM 7.0.5 B1=3000000 (driver tier 5)
* **nums/numsp512d1**: p33 — GMP-ECM 7.0.5 B1=1000000 (driver tier 4); p119 — GMP-ECM 7.0.5 B1=1000000 (driver tier 4)
* **other/E-521**: 23658857317 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p34 — GMP-ECM 7.0.5 B1=250000 (driver tier 3); p53 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (1179 s wall); p59 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (1179 s wall)
* **arkworks/ed_on_mnt4_753**: p21 — GMP-ECM 7.0.5 B1=50000 (driver tier 2); p25 — GMP-ECM 7.0.5 B1=250000 (driver tier 3); p30 — GMP-ECM 7.0.5 B1=1000000 (driver tier 4); p149 — GMP-ECM 7.0.5 B1=1000000 (driver tier 4)

Excluded (already certified in research/endosweep_nist_20261006/factorizations.jsonl): nist/P-256, nist/P-384, nist/P-521, other/Curve25519.

Excluded (already certified in research/endosweep_dk_exact_20261016/factorizations.jsonl): arkworks/bw6_767, arkworks/ed_on_bw6_761, bls/BLS12-638, bn/bn510, gost/id-tc26-gost-3410-2012-512-paramSetC, nums/ed-255-mers, nums/ed-383-mers, nums/ed-384-mont, nums/numsp256d1, nums/w-255-mers, nums/w-384-mont, nums/w-511-mers, nums/w-512-mont, other/BADA55-R-256, other/MDC201601, other/ssc-288, other/ssc-512, x962/prime239v2.

Excluded (already certified in research/endosweep_dk_exact_batch2_20261016/factorizations.jsonl): arkworks/cp6_782, bn/bn606, brainpool/brainpoolP384r1, nums/ed-382-mont, nums/numsp512t1, oscaa/SM2.

Excluded (already certified in research/endosweep_dk_exact_batch3_20261017/factorizations.jsonl): arkworks/bw6_761, nums/numsp384t1, other/E-382.
