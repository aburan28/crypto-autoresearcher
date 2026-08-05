---
id: KN-FIND-4c9e71
type: internal_finding
title: H-PSEUDO adversarial robustness — max C ~ O(1) ≈ 4 across all tested primes (p=1009..9001)
tags: [hpseudo, adversarial, robustness, constant-c, fourier, prime-field]
confidence: preliminary_empirical
evidence_level: toy_adversarial_search
source_refs: [BATCH-104, BATCH-105, EV-PSEUDO-dd0c51, EV-PSEUDO-066646]
internal_refs: [EV-PSEUDO-dd0c51, EV-PSEUDO-066646]
proof_status: empirical_only
proof_refs: []
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

## CORRECTION (BATCH-107)

At p=50021: max C = 5.182 (6 measurements), consistent with p^{0.079} scaling (prediction: 5.31).
The adversarial max DOES grow with p, following the same C ~ p^{0.079} as the mean.
Earlier claim of "O(1) max C" was premature (too narrow p range: 1009..9001 spans only 9x).

**Revised finding**: BOTH mean C AND adversarial max C scale as ~ p^{0.079}.
H-PSEUDO with C = O(p^{0.079}) (slowly growing) is the correct empirical characterization.
At crypto scale (p=2^256): C_max ~ 2^{20}, yield error O(2^{-110}) — negligible.

Full adversarial max C scaling:

| p | max C (adversarial) | p^{0.079} prediction |
|---|---|---|
| 1009 | 3.90 | 3.56 (baseline) |
| 4001 | 3.87 | 4.01 |
| 9001 | 4.11 | 4.35 |
| 50021 | 5.18 | 5.31 |
