# Pushing Collision Attacks on SHA-2 to 39 Steps — claims extract

**Provenance:** user-supplied full paper text in conversation on 2026-09-09.
Recorded as `recalled`/`user_supplied` until an independent primary-source
retrieval (ePrint/venue PDF) is attached. This extract freezes the load-bearing
claims for GOAL-SHA2-75ae45; it is not a certificate that any attack works.

## Bibliographic metadata (as stated in the supplied text)

- Title: Pushing Collision Attacks on SHA-2 to 39 Steps
- Authors: Yingxin Li, Zhuolong Zhang, Muzhou Li, Fukang Liu, Haifeng Qian, Jinwei Zhu
- Affiliations: East China Normal University; Shandong University (Qingdao/Jinan); Institute of Science Tokyo
- Keywords: hash function, SHA-2, meet-in-the-middle, collision attack
- Venue/status in supplied text: not given as an ePrint ID; cites CRYPTO 2026 / EUROCRYPT 2026 lineage ([LLWS26], [ZMLM26], etc.)

## Headline results (Table 1, as stated)

| Version | Attack | Steps | Time | Memory | Claim |
| --- | --- | --- | --- | --- | --- |
| SHA-256 | collision | 36 | practical / ~2^57 | negligible | first practical 36-step collision; colliding pair given |
| SHA-256 | collision | 37 | 2^79.1 | negligible | improved vs [LLWS26] |
| SHA-256 | collision | 38 | 2^104.3 | negligible | first theoretical 38-step collision |
| SHA-256 | collision | 39 | 2^168 | — | ineffective (worse than birthday) |
| SHA-512 | collision | 36 | 2^66.2 | negligible | improved |
| SHA-512 | collision | 37 | 2^87 | negligible | improved |
| SHA-512 | collision | 38 | 2^125.4 | negligible | first theoretical 38-step collision |
| SHA-512 | collision | 39 | 2^178 | negligible | first effective 39-step collision |

## Method (as stated)

1. Nonzero message differences only in a fixed local-collision injection pattern shifted by step count (for 38 steps: W7..W11, W15, W16, W23, W25).
2. Refined multi-step SAT/SMT search that minimizes Hamming weight of message differences, then uncontrolled E/A signed differences in stages, before materializing a full characteristic.
3. Memory-efficient on-the-fly meet-in-the-middle fulfillment of differential conditions under the CRYPTO 2026 framework, exploiting characteristics with few/no conditions on early W/E words so matches need little or no stored intermediate solutions.

## Practical certificate stated for 36-step SHA-256 (Table 2)

```
M0
d7c6ac05 3be3567b 33c02b26 3a6dfd82 ed46810e 8dacae35 3e004584 26d29992
39cff659 0acc2223 8e77b3b0 cc7f4bba 9ff3abea 17606f86 ce693676 c3bc18aa
M1
09abc425 0e8b8121 85808046 fadb1bca 394268e3 b9dfbd34 ae156845 74169a81
1ea03337 a3210f16 79b82017 91059d10 97294bab 65ceec9c 89c67ae2 ac5eb7f9
M'1
09abc425 0e8b8121 85808046 fadb1bca 394268e3 99dfbd34 aa556045 54169a81
1fa123bd a3290316 79b82017 91059d10 97294bab 618ee49c a9c67ae2 ac5eb7f9
hash
79df3078 14339285 d39ae368 142866bc ba063acf fa4431c6 a5d74825 c4be00db
```

UNVERIFIED in this repository until an independent FIPS 180-4 36-step compression check re-confirms the pair.

## Explicit non-claims of this extract

- Does not assert that any complexity figure is correct.
- Does not assert that full SHA-256/SHA-512, HMAC, TLS, or Bitcoin are broken.
- Does not substitute for primary-source PDF retrieval or KN-LIT curation.
