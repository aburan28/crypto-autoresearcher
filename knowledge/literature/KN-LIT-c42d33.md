---
id: KN-LIT-c42d33
type: literature
title: 'When Module Lattice Leaks: Horizontal Fusion Attacks on ML-DSA Implementation'
authors:
- Yuhan Zhao
- Dalin He
- Wei Cheng
- Yuejun Liu
- Jingdian Ming
- Yongbin Zhou
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/1904
identifiers:
  eprint: iacr:2026/1904
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/1904
source:
  citation: 'Yuhan Zhao, Dalin He, Wei Cheng, Yuejun Liu, Jingdian Ming, Yongbin Zhou. When Module Lattice Leaks: Horizontal
    Fusion Attacks on ML-DSA Implementation. Cryptology ePrint Archive 2026/1904, 2026.'
  url: https://eprint.iacr.org/2026/1904
tags:
- ml-dsa
- side-channel
- horizontal-fusion
- masking
- ntt
- key-recovery
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

Reusing ephemeral y across row-wise matrix-vector operations provides multiple known-coefficient leakage instances within each signing. Variance-weighted fusion and an inverse-NTT algebraic sieve lead to the authors’ reported full ML-DSA-87 key recovery with four non-profiled traces on an unprotected implementation, and at most 90 traces against the tested first-order masked implementation.

## Scope and evidence boundary

Physical leakage and the specific unprotected/masked implementations define the scope. Trace counts do not include acquisition setup or demonstrate a signature-only or public-key-only attack.

## Research follow-up

Record tested hardware, exact masking design, signal-to-noise ratio, capture cost and independent-key trials.

Source: [https://eprint.iacr.org/2026/1904](https://eprint.iacr.org/2026/1904); ePrint received 2026-09-07. Abstract and metadata read on 2026-09-26; result not reproduced.
