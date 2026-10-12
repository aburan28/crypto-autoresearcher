---
id: KN-LIT-81c4b3
type: literature
title: Recovering SNOVA Secret Keys from Biased Vinegar Sampling
authors:
- Ward Beullens
- Basil Hess
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/2154
identifiers:
  eprint: iacr:2026/2154
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/2154
source:
  citation: Ward Beullens, Basil Hess. Recovering SNOVA Secret Keys from Biased Vinegar Sampling. Cryptology ePrint Archive
    2026/2154, 2026.
  url: https://eprint.iacr.org/2026/2154
tags:
- snova
- uov
- multivariate
- lpn
- bkw
- vinegar-bias
- key-recovery
- implementation-attack
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

For six odd-characteristic alternative parameter sets in Round-3 SNOVA, reduction of uniform bytes modulo a power of q biases vinegar sampling. The authors turn the signature leakage (at most 0.086 bits per variable) into a q-ary LPN instance of dimension o*l. They report practical full secret-key recovery on four affected sets with 9–180 million signatures and at most 16 minutes using BKW and Fourier hypothesis testing. Their naive attack estimates 2^90–2^130 operations for the six sets, below the claimed 170–331-bit costs.

## Scope and evidence boundary

This applies to the stated six alternative parameter sets and the biased signer; it is not a generic UOV break. The four practical experiments and the remaining cost projections have different evidence levels. Uniform vinegar sampling is the authors’ proposed fix.

## Research follow-up

Reproduce the exact Round-3 sampler and affected parameter IDs; retain signature count, acquisition time, computation and memory separately before comparing to the 2026 PQC target agenda.

Source: [https://eprint.iacr.org/2026/2154](https://eprint.iacr.org/2026/2154); ePrint received 2026-09-22. Abstract and metadata read on 2026-09-26; result not reproduced.
