---
id: KN-LIT-112bad
type: literature
title: 'Exposing SIMD Parallelism in SQIsign: An AVX-512 Implementation'
authors:
- Weize Wang
- Chutong Wang
- Yu Wu
- Qifan Xue
- Jieyu Zheng
- Yunlei Zhao
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/1713
identifiers:
  eprint: iacr:2026/1713
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/1713
source:
  citation: 'Weize Wang, Chutong Wang, Yu Wu, Qifan Xue, Jieyu Zheng, Yunlei Zhao. Exposing SIMD Parallelism in SQIsign: An
    AVX-512 Implementation. Cryptology ePrint Archive 2026/1713, 2026.'
  url: https://eprint.iacr.org/2026/1713
tags:
- sqisign
- coral
- isogeny
- avx-512
- ifma
- simd
- implementation
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

The authors reorganize ladders, pairings and higher-dimensional isogeny evaluation around AVX-512IFMA vector operations. Against their reference C implementation at NIST level I, key generation, signing and verification improve by 1.76x, 1.71x and 3.18x respectively; incorporating Qlapoti changes key-generation and signing comparisons to 2.90x and 2.69x. The same approach reports CORAL group-action gains of 1.28–1.40x for key generation and 1.92–2.46x for shared-key computation.

## Scope and evidence boundary

Hardware- and baseline-dependent implementation throughput, not a cryptanalytic SQIsign break. The Qlapoti comparisons are distinct from plain SIMD comparisons.

## Research follow-up

Pin CPU ISA, compiler, implementation version and exact Round-3 parameter set before cross-scheme speed comparisons.

Source: [https://eprint.iacr.org/2026/1713](https://eprint.iacr.org/2026/1713); ePrint received 2026-08-17. Abstract and metadata read on 2026-09-26; result not reproduced.
