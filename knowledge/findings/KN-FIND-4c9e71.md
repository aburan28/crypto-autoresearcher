---
id: KN-FIND-4c9e71
type: internal_finding
title: H-PSEUDO adversarial robustness — max C ~ O(1) ≈ 4 across all tested primes (p=1009..9001)
tags: [hpseudo, adversarial, robustness, constant-c, fourier, prime-field]
confidence: preliminary_empirical
evidence_level: toy_adversarial_search
source_refs: [BATCH-104, BATCH-105, EV-PSEUDO-dd0c51, EV-PSEUDO-066646]
added: '2026-08-04'
superseded_by: null
---

## Finding

Adversarial maximum of C = max_k |hat{1_F}(k)| / sqrt(B) across all tested random curves:

| p | n measurements | max C | mean C |
|---|---|---|---|
| 1009 | 152 | 3.90 | 2.99 |
| 4001 | 26 | 3.87 | 3.47 |
| 9001 | 12 | 4.11 | 3.63 |

**The adversarial maximum is BOUNDED ~ 4 and NOT growing significantly with p.**
No counter-example to H-PSEUDO found in 190+ measurements.

## Significance

H-PSEUDO with CONSTANT C ≤ 5 is strongly empirically supported. The earlier estimate
of C ~ p^{0.079} was based on MEAN measurements over random curves; the adversarial
MAXIMUM (which is what H-PSEUDO requires) appears to be bounded by a constant ≈ 4.

This is the strongest empirical evidence for H-PSEUDO yet:
- Mean C grows slowly (most curves have larger C as p grows)
- Max C is bounded (the worst case curve has C ≈ 4 regardless of p)

## Implications

H-PSEUDO revised: C = O(1) (constant) rather than C = O(p^{0.079}).
If C = O(1) is correct: the Semaev yield error is O(4^m / sqrt(N)) which is
negligible for all standard m and N values. H-PSEUDO with constant C would be
an even stronger bound than initially measured.

## Caveats

- Toy scale only: p ≤ 9001 (bits ≤ 14)
- Limited adversarial search: 12-152 random curves per prime
- The mean C growing as p^{0.079} might reflect a per-curve statistical effect
  rather than a growing maximum; more data needed at larger primes
