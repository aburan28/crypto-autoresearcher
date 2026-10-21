# Exact CM discriminants (endosweep_dk_exact_batch3_20261017)

std-curves commit `77fe6e3585ca2c2225b59d7df24b7c775437276f`.  Every factor is proved prime by PARI `isprime`; `pN` is an N-digit prime written out in `dk_exact.json`.  No D_K here was checked against the literature (see the `std-curves` column for the one comparison made).

| curve | p bits | t | 4q−t² digits | factorisation of 4q−t² | squarefree part s | f | D_K | log2 \|D_K\| | least non-scalar degree ≈ \|D_K\|/4 | std-curves |
|:--|--:|--:|--:|:--|:--|:--|:--|--:|--:|:--|
| other/E-382 | 382 | (58 digits) | 116 | 2^2 · 5 · 11 · 48109 · p41 · p69 | (115 digits) | 2 | −(115 digits) | 381.19 | 2^379.19 | no cm_disc |
| nums/numsp384t1 | 384 | (58 digits) | 117 | 2^2 · 5 · 13 · 29 · 18911 · 32957 · p34 · p71 | (116 digits) | 2 | −(116 digits) | 383.97 | 2^381.97 | no cm_disc |
| arkworks/bw6_761 | 761 | (115 digits) | 230 | 2^2 · 3 · 11^2 · 13827131^2 · p35^2 · p72^2 | 3 | (115 digits) | -3 | 1.58 | 1 | no cm_disc |

## Who found each factor the survey did not

Every other factor came from the survey's `PARI factor(N, 2^32)`.  Both parts of a split carry the split's method (the found factor and its cofactor).

* **other/E-382**: p41 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (3059 s wall); p69 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (3059 s wall)
* **nums/numsp384t1**: p34 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (2138 s wall); p71 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (2138 s wall)
* **arkworks/bw6_761**: p35 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (2845 s wall); p72 — CADO-NFS 3.0.0 (git 692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b), cado-nfs.py C -t 4 (2845 s wall)

Excluded (already certified in research/endosweep_nist_20261006/factorizations.jsonl): nist/P-256, nist/P-384, nist/P-521, other/Curve25519.

Excluded (already certified in research/endosweep_dk_exact_20261016/factorizations.jsonl): arkworks/bw6_767, arkworks/ed_on_bw6_761, bls/BLS12-638, bn/bn510, gost/id-tc26-gost-3410-2012-512-paramSetC, nums/ed-255-mers, nums/ed-383-mers, nums/ed-384-mont, nums/numsp256d1, nums/w-255-mers, nums/w-384-mont, nums/w-511-mers, nums/w-512-mont, other/BADA55-R-256, other/MDC201601, other/ssc-288, other/ssc-512, x962/prime239v2.

Excluded (already certified in research/endosweep_dk_exact_batch2_20261016/factorizations.jsonl): arkworks/cp6_782, bn/bn606, brainpool/brainpoolP384r1, nums/ed-382-mont, nums/numsp512t1, oscaa/SM2.
