---
id: KN-LIT-cc9e69
type: literature
title: New algorithms for quaternion ideals in SQIsign
authors:
- Antonin Leroux
- Sina Schaeffler
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/2153
identifiers:
  eprint: iacr:2026/2153
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/2153
source:
  citation: Antonin Leroux, Sina Schaeffler. New algorithms for quaternion ideals in SQIsign. Cryptology ePrint Archive 2026/2153,
    2026.
  url: https://eprint.iacr.org/2026/2153
tags:
- sqisign
- isogeny
- quaternion
- ideal-arithmetic
- integer-bounds
- constant-time
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

A normalized representation and specialized quaternion-ideal algorithms for the Deuring correspondence when p is 3 mod 4 reduce the size of intermediate integers. For the latest SQIsign implementation, the authors give an O(p^4) worst-case integer bound under an experimentally verified assumption about response-sampling lattice reduction, improving previous bounds by at least an O(p^2) factor as reported in the abstract. The implementation replaces GMP with fixed-size integers without reported performance overhead.

## Scope and evidence boundary

This is an arithmetic and bounded-integer improvement, not a reduction in the hardness of the endomorphism-ring problem or a claimed end-to-end signing speedup. The stated proof is conditional on the named experimentally verified assumption.

## Research follow-up

Benchmark fixed-size integer operations and peak limb sizes against the precise Round-3 SQIsign code and Qlapoti path, recording failure and constant-time behavior separately.

Source: [https://eprint.iacr.org/2026/2153](https://eprint.iacr.org/2026/2153); ePrint received 2026-09-22. Abstract and metadata read on 2026-09-26; result not reproduced.
