---
id: KN-FIND-d1c853
type: internal_finding
title: "Wesolowski Heuristic-1 pairing rule \u2014 walk length vs smooth-norm pair\
  \ count (unvalidated empirically)"
tags:
- wesolowski
- supersingular-isogeny
- heuristic-1
- smooth-norm
- walk-length
- pairing-rule
- p13
- unvalidated
added: 2026-08-04
proof_status: derivation
claim_status: derivation_only_heuristic_unvalidated
source_goal: GOAL-P13-001
source_batch: BATCH-403f13
source_evidence: EV-WESO-b6ceff
source_decision: DEC-20260804-e19a65
authority: internal_analysis
confidence: provisional
internal_refs:
- EV-WESO-b6ceff
- DEC-20260804-e19a65
- EV-WESO-001
proof_refs: []
---

## Finding (derivation-level, Heuristic 1 not empirically validated)

The pairing rule between walk length and expected smooth-norm count under Wesolowski's Heuristic 1 is:

```
N_pairs ≈ exp(H_1 × n_walk)
```

where:
- `n_walk = 3 × ceil(log2 p)` is the prescribed walk length
- `H_1` is the Heuristic 1 constant, which asserts that j-invariants visited by a random ell-isogeny walk behave as approximately independent uniform samples over the supersingular j-invariants mod p
- Under H_1, the probability that any given step produces a smooth-norm denominator is approximately `P_0 = B_opt^{-1}` where `B_opt` is the smoothness bound

## Derivation basis

This rule is derived directly from the paper's Section 4, cross-checked with EV-WESO-001's observation: "the paper's five concrete (time, memory) pairs reproduce only within 0.05-3.51 bits (partial control failure, honestly disclosed)." The pairing rule itself is not disputed; it is the constant H_1 that requires empirical validation.

## Critical caveat

**Heuristic 1 has NOT been empirically validated.** NC-3/NC-6 (the Heuristic 1 tail validation experiment) failed with an infrastructure error in BATCH-403f13. The j-invariant distribution test was not executed.

The pairing rule is promoted at derivation level ONLY. Any concrete-cost claim resting on H_1 carries this open qualification as the dominant uncertainty. Per `docs/target-result-profile.md`: "every heuristic is numbered, formally stated, given a random-model justification, and paired with a falsification condition and a validation plan." The validation plan exists (EXP-P13-NC36/specification.yaml); the empirical pass does not.

## What this does NOT say

- Not evidence that Heuristic 1 holds.
- Not a security claim or break attempt.
- Not a complete cost model (alpha excess not propagated; k constant not retrieved from Wesolowski body).
