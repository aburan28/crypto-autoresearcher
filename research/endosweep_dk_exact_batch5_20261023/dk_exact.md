# Exact CM discriminants (endosweep_dk_exact_batch5_20261023)

std-curves commit `77fe6e3585ca2c2225b59d7df24b7c775437276f`.  Every factor is proved prime by PARI `isprime`; `pN` is an N-digit prime written out in `dk_exact.json`.  No D_K here was checked against the literature (see the `std-curves` column for the one comparison made).

| curve | p bits | t | 4q−t² digits | factorisation of 4q−t² | squarefree part s | f | D_K | log2 \|D_K\| | least non-scalar degree ≈ \|D_K\|/4 | std-curves |
|:--|--:|--:|--:|:--|:--|:--|:--|--:|--:|:--|
| gost/gost512 | 511 | (77 digits) | 155 | 19870558523 · p71 · p74 | (155 digits) | 1 | −(155 digits) | 512.0 | 2^510.0 | no cm_disc |

## Who found each factor the survey did not

Every other factor came from the survey's `PARI factor(N, 2^32)`.  Both parts of a split carry the split's method (the found factor and its cofactor).

* **gost/gost512**: 19870558523 — GMP-ECM 7.0.5 B1=11000 (driver tier 1); p71 — FactorDB (external; finder not recorded; fetched 2026-10-22T23:04:32.541251Z); p74 — FactorDB (external; finder not recorded; fetched 2026-10-22T23:04:32.541251Z)

Excluded (already certified in research/endosweep_nist_20261006/factorizations.jsonl): nist/P-256, nist/P-384, nist/P-521, other/Curve25519.

Excluded (already certified in research/endosweep_dk_exact_20261016/factorizations.jsonl): arkworks/bw6_767, arkworks/ed_on_bw6_761, bls/BLS12-638, bn/bn510, gost/id-tc26-gost-3410-2012-512-paramSetC, nums/ed-255-mers, nums/ed-383-mers, nums/ed-384-mont, nums/numsp256d1, nums/w-255-mers, nums/w-384-mont, nums/w-511-mers, nums/w-512-mont, other/BADA55-R-256, other/MDC201601, other/ssc-288, other/ssc-512, x962/prime239v2.

Excluded (already certified in research/endosweep_dk_exact_batch2_20261016/factorizations.jsonl): arkworks/cp6_782, bn/bn606, brainpool/brainpoolP384r1, nums/ed-382-mont, nums/numsp512t1, oscaa/SM2.

Excluded (already certified in research/endosweep_dk_exact_batch3_20261017/factorizations.jsonl): arkworks/bw6_761, nums/numsp384t1, other/E-382.

Excluded (already certified in research/endosweep_dk_exact_batch4_20261022/factorizations.jsonl): arkworks/ed_on_mnt4_753, nums/ed-510-mont, nums/numsp384d1, nums/numsp512d1, other/Curve41417, other/E-521, other/M-511.
