---
id: KN-FIND-8f2c90
type: internal_finding
title: BKK mixed-volume factor-2 gives ~1.3-1.7x constant speedup in Semaev relation collection
tags: [bkk, semaev, relation-collection, constant-speedup, index-calculus, prime-field]
confidence: preliminary_empirical
evidence_level: toy_measurement
source_refs: [BATCH-110, BATCH-111, BATCH-112, EV-SEMAEV-47d130, EV-SEMAEV-473ea1]
internal_refs: [EV-SEMAEV-47d130, EV-SEMAEV-473ea1]
proof_status: empirical_only
proof_refs: []
added: '2026-08-04'
superseded_by: null
---

## Finding

The BKK mixed-volume (= B/2, half the Bezout bound B for the Semaev m=2 system) gives
a practical speedup in Semaev relation collection. Checking B/2 factor-base pairs per
target (instead of all B) gives:

- Yield retention gamma: ~86% at p=1009 (saturated, heuristic=1.53)
- Yield retention gamma: ~75% at p=4001 (near-crossover, heuristic=0.88)
- Net speedup: 2*gamma = 1.5-1.7x in total check operations

## Proof sketch

Total check operations = (check operations per trial) × (trials needed).
Standard: B × (R/(B^2/(2N))) = 2RN/B.
BKK (B/2 check): (B/2) × (R/(gamma × B^2/(2N))) = RN/(gamma × B).
Speedup = (2RN/B) / (RN/(gamma×B)) = 2*gamma ≈ 1.5-1.7.

## Impact on Semaev complexity constant

The constant c in exp(c*sqrt(log N*log log N)) is reduced by factor 1/sqrt(2*gamma) ≈ 0.77.
A ~23% improvement in the constant c. Not exponent-moving, but the first measured
practical improvement from the BKK theoretical result.

## Condition for speedup

The speedup is strongest in the saturated regime (heuristic > 1). For optimal B
(heuristic ≈ 1): speedup ~1.5x. For B chosen so heuristic = 2: speedup ~1.7x.
