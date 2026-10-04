---
id: KN-LIT-b901b9
type: literature
title: Optimal Bucket Set Construction for Multi-scalar Multiplication with Endomorphisms
authors:
- Nam Hoai Le
- Francesco Sica
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/1902
identifiers:
  eprint: iacr:2026/1902
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/1902
source:
  citation: Nam Hoai Le, Francesco Sica. Optimal Bucket Set Construction for Multi-scalar Multiplication with Endomorphisms.
    Cryptology ePrint Archive 2026/1902, 2026.
  url: https://eprint.iacr.org/2026/1902
tags:
- elliptic-curve
- msm
- endomorphism
- pippenger
- buckets
- bls12-381
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

The authors optimize bucket sets and Hamiltonian traversal for endomorphism-assisted multi-scalar multiplication. Relative to Luo–Fu–Gong they report average 67% less storage and 7% fewer curve operations (up to 10.6%). For BLS12-381 with 2^10–2^21 points they report an average 6% improvement over Pippenger and up to 15.8% lower storage; a separate comparison improves FKSX by about 7%.

## Scope and evidence boundary

These are different baselines and batching sizes for MSM, not a faster single rho walk or a reduced ECDLP exponent. Reported operation reductions and performance should not be interchanged without hardware measurements.

## Research follow-up

Test only where batch MSM is actually used in relation generation or proof workloads, including preprocessing and memory traffic.

Source: [https://eprint.iacr.org/2026/1902](https://eprint.iacr.org/2026/1902); ePrint received 2026-09-06. Abstract and metadata read on 2026-09-26; result not reproduced.
