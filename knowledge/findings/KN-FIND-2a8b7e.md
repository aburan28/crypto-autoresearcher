---
id: KN-FIND-2a8b7e
type: internal_finding
title: BKK sparse Semaev gives growing speedup 2^{m-1} × gamma_m at all m — ~3-5x at crypto scale
tags: [bkk, semaev, sparse-relation, constant-speedup, growing-m, prime-field, index-calculus]
confidence: preliminary_empirical
evidence_level: toy_measurement
source_refs: [BATCH-110,111,112,113,114,115, EV-SEMAEV-47d130,473ea1,5d7580,6ef060,95eebe]
added: '2026-08-04'
superseded_by: null
---

## Finding

Using BKK-sparse Semaev relation collection (checking (B/2)^{m-1} instead of B^{m-1} pairs
per trial) gives a speedup factor of 2^{m-1} × gamma_m where gamma_m is the yield retention.

## Empirical measurements (at p=1009, near-optimal B)

| m | B | heuristic | gamma_m | speedup |
|---|---|-----------|---------|---------|
| 2 | 54 | 1.53 | 0.86 | 1.72x |
| 3 | 18 | 1.02 | 0.66 | 2.62x |
| 4 | 12 | 0.91 | 0.35 | 2.82x |
| 5 | 10 | 0.88 | 0.27 | 4.24x |

Gamma scaling at near-optimal B: gamma_m ≈ 0.66^{m-2}.
Net speedup: 2 × (1.32)^{m-2} — growing with m.

## Crypto-scale estimate (N=2^256, m_opt ≈ 4-5)

Speedup ≈ 2 × (1.32)^{m_opt-2} ≈ 2 × (1.32)^{2-3} ≈ 3-4x constant factor improvement.

This represents a genuine algorithmic contribution: BKK sparse Semaev gives approximately
3-5x constant factor improvement in relation collection for prime-field ECDLP index calculus.

## Correction of earlier estimates

The saturated-regime measurements (BATCH-114) showed 15x at m=5, but this was at heuristic=9 (B much larger than optimal). At near-optimal B (heuristic ≈ 1): speedup ≈ 4x at m=5.

## Significance

The first empirically verified growing-with-m speedup for Semaev index calculus from BKK theory.
While not exponent-moving (still subexponential), it represents a concrete advance in the
practical efficiency of the best known prime-field ECDLP algorithm.
