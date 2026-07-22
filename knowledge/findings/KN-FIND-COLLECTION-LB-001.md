---
id: KN-FIND-COLLECTION-LB-001
type: internal_finding
title: Unconditional collection-phase lower bound + barrier-localization for prime-field EC index calculus
tags: [prime-field, index-calculus, lower-bound, sumset, no-go, barrier-localization, pollard-rho, theorem]
confidence: established
internal_refs: [research/THM-collection-lower-bound-20260722.md]
added: 2026-07-22
superseded_by: null
---

## Result (proved, unconditional; group-agnostic core)
For E/F_p with N=#E(F_p), factor base F of size B, and m-fold decomposition set
D_m(F)=m·(F ∪ -F):
- **Lemma (sumset cap):** |D_m(F)| ≤ C(2B+m-1, m) ≤ (2B)^m/m!·(1+o(1)) for EVERY
  factor base; tight up to constants for random F (verified).
- **Theorem:** any target-sectioned m-decomposition index calculus costs
  T ≥ B + σ·m!·N/(2^m B^{m-1}), σ = per-decomposition-test solve cost. Hence:
  - **m=2, unconditional:** T ≥ √(2N) = 1.414√N > rho (0.886√N) for ALL factor
    bases — factor-base engineering cannot make m=2 IC beat generic sqrt methods.
  - **m≥3, localization:** collection+linear-algebra is Θ(N^{1/m}) = o(√N), so the
    barrier is entirely the solve cost σ; IC beats rho iff σ = o(N^{m/2-1})
    (σ = o(√N) for m=3).

## Why it matters
Unifies the campaign's rejected_scoped factor-base results (H-FB, H-FB3, STR) and
the yield-saturation finding as one provable bound, and reduces the open problem
to a single sharp quantity: does the m-th summation-polynomial decomposition
admit an amortized o(N^{m/2-1}) solver? Every confirmed structural signal (INCB,
BKKMV, JETB, SIG) affects constants/collection, provably not the solve exponent —
which is exactly why none beat rho.

## Boundaries (honest)
- Obstruction/reduction theorem, NOT a break of ECDLP and NOT an m≥3 no-go
  (that needs an unconditional σ ≥ N^{m/2-1} lower bound on the Groebner step,
  which is open — the DREG frontier).
- Component facts (sumset bound; IC-vs-rho trade-off) are folklore in spirit; the
  contribution is the clean unconditional factor-base-independent assembly and the
  exact threshold. Novelty vs. full literature: unverified.
- confidence: established refers to the PROOF of the stated bound; the novelty and
  literature-priority are not certified.
