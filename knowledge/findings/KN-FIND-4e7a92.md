---
id: KN-FIND-4e7a92
type: internal_finding
title: Wesolowski corrected estimator formula — cost accounting for all Elkies steps at operating ell range
tags: [wesolowski, supersingular-isogeny, corrected-estimator, elkies, cost-model, p13, heuristic-1]
added: 2026-08-04
proof_status: derivation
source_goal: GOAL-P13-001
source_batch: BATCH-403f13
source_evidence: EV-WESO-b6ceff
source_decision: DEC-20260804-e19a65
claim_status: derivation
authority: internal_analysis
---

## Finding

The corrected cost estimator for the Wesolowski 2026 supersingular-isogeny attack accounts for ALL Elkies steps at ell in the operating range {47, 101, 151, 211} (not just ell=2 or small ell below the Karatsuba threshold):

```
C_corrected = phi(ell) * C_Phi_ell(p) + C_walk
```

where:
- `phi(ell)` = ell − 1 (number of distinct roots of Phi_ell counted with multiplicity in the supersingular case)
- `C_Phi_ell(p)` = cost of evaluating the classical modular polynomial Phi_ell at a j-invariant mod p; scales as (log p)^alpha with alpha ≈ 1.13 at ell∈{47,101,151,211} (EV-WESO-b6ceff, NC2d-PROPER measurement)
- `C_walk` = cost of the isogeny walk; dominated by Elkies steps

## Evidence basis

NC2d-PROPER (EXP-P13-NC2d) confirmed alpha_primary = 1.1321 at ell∈{47,101,151,211}, with gap |alpha_primary − alpha_null| = 0.0606 < 0.15 (FC-4 not fired). This retires the MECHANISM-INCONSISTENT label on assumption L5 at the operating ell range.

## Scope and limitations

- Measured at p ≤ 2^40 (toy/medium scale). Not validated at cryptographic p.
- alpha = 1.13 is 13% above the theoretical L5 prediction of 1.0. This excess has not been propagated into any margin row in the c-table.
- Heuristic 1 (independence assumption for walk j-invariants) is not validated here. See KN-FIND-d1c853.

## What this does NOT say

- Not a claim that the attack is practical.
- Not a cost estimate at NIST parameters.
- Not a statement about L5 at ell outside the range {47,101,151,211}.
