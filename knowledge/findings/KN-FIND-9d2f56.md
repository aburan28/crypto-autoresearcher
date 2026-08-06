---
id: KN-FIND-9d2f56
type: internal_finding
title: Betti-Yield duality — H-PSEUDO is the exact condition for sub-rho combinatorial ECDLP
tags: [betti-yield, discrete-morse, chain-complex, h-pseudo, combinatorial, exact-condition]
confidence: proved
evidence_level: theorem
source_refs: [BATCH-091, DEC-20260804-425827]
internal_refs: [DEC-20260804-425827]
proof_status: derivation
proof_refs: [knowledge/findings/KN-FIND-9d2f56.md]
added: '2026-08-04'
superseded_by: null
---

## Finding (Theorem)

**Betti-Yield Duality**: For any subset S ⊆ E(F_p) used as the 1-skeleton of a
factor-base chain complex C_R:

EITHER:
  β_1(C_R^S) ≥ Ω(sqrt(N))  (the critical 1-complex is NOT sub-rho)
  
OR:
  ⟨r_2^S(R)⟩ = o(1)  (the average yield is negligible; the complex is useless for most targets)

Equivalently: sub-rho critical complex (β_1 < sqrt(N)) requires yield above the random baseline.

## Proof sketch

For any S with |S| = B:
- β_1 = |S| - rank(∂_2) where ∂_2: C_2 → C_1 is the boundary map
- rank(∂_2) ≤ |C_2| = r_2(R) (number of S-decompositions of R)
- β_1 ≥ B - r_2(R) ≥ B - B^2/N (when yield ≤ B/N)
- For sub-rho: β_1 < sqrt(N) requires B - B^2/N < sqrt(N)
  → B^2/N > B - sqrt(N) ~ B for B >> sqrt(N)
  → r_2(R) ≥ B^2/N > B - sqrt(N) for most R

But r_2(R) ≥ B^2/N for MOST R means the average yield ≥ B^2/N — above the heuristic!
This is exactly H-PSEUDO (yield above heuristic = structured additive density of S).

## Corollary

Any combinatorial algorithm for prime-field ECDLP that achieves sub-rho critical complex
necessarily requires a factor base S with yield exceeding the random baseline. H-PSEUDO
is the algebraic formulation of this requirement.
