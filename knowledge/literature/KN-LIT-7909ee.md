---
id: KN-LIT-7909ee
type: literature
title: 'Every Signing Leaks: Breaking Falcon via Floating-Point Conversion Leakage'
authors:
- Yuanyuan Zhou
- Weijia Wang
- Yiteng Sun
- Yu Yu
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/2124
identifiers:
  eprint: iacr:2026/2124
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/2124
source:
  citation: 'Yuanyuan Zhou, Weijia Wang, Yiteng Sun, Yu Yu. Every Signing Leaks: Breaking Falcon via Floating-Point Conversion
    Leakage. Cryptology ePrint Archive 2026/2124, 2026.'
  url: https://eprint.iacr.org/2026/2124
tags:
- falcon
- fn-dsa
- power-analysis
- floating-point
- gaussian-sampler
- key-recovery
- side-channel
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

Signed-exponent leakage during conversion of a Gaussian center from integer back to floating point in Falcon ffSampling lets a profiled classifier constrain center values. The authors combine maximum-likelihood estimation with subset search and LLL/BKZ, testing power traces from PQClean on an Arm Cortex-M4. They report full Falcon-512 key recovery from 20 (-O0) or 56 (-O3) signatures, and Falcon-1024 from 21 (-O0) or 100 (-O3), with 100% success in the reported experiments.

## Scope and evidence boundary

Physical power traces and the tested implementation are required. These counts are experimental claims with compiler settings, not a classical cryptanalytic reduction against every conforming Falcon/FN-DSA implementation.

## Research follow-up

Preserve trace acquisition, profiling keys, tested boards/compilers and independent-key success counts in any reproduction.

Source: [https://eprint.iacr.org/2026/2124](https://eprint.iacr.org/2026/2124); ePrint received 2026-09-20. Abstract and metadata read on 2026-09-26; result not reproduced.
