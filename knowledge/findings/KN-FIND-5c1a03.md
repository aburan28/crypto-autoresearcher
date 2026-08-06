---
id: KN-FIND-5c1a03
type: internal_finding
title: Three-way convergence — H-PSEUDO, Betti-Yield, and Wesolowski transfer all identify the same missing structural ingredient for prime-field ECDLP
tags: [hpseudo, betti-yield, wesolowski, structural-gap, algebraic-structure, prime-field-ecdlp, convergence]
confidence: multiple_independent_analyses
evidence_level: derived
source_refs: [BATCH-085, BATCH-091, BATCH-095, BATCH-096, DEC-20260804-425827, DEC-20260804-4f7da7, DEC-20260804-bfbb09]
internal_refs: [DEC-20260804-425827, DEC-20260804-4f7da7, DEC-20260804-bfbb09]
proof_status: derivation
proof_refs: [knowledge/findings/KN-FIND-5c1a03.md]
added: '2026-08-04'
superseded_by: null
---

## Finding

Three completely independent analyses of prime-field ECDLP complexity all identify the same missing ingredient:

| Analysis | Approach | Missing ingredient |
|----------|----------|-------------------|
| H-PSEUDO (analytic) | 8 character-sum proof methods closed | Algebraic-type Fourier flatness without algebraic mechanism |
| Betti-Yield duality (combinatorial) | Topological lower bounds on complex complexity | Factor base with structured additive density (same as H-PSEUDO) |
| Wesolowski transfer (algebraic) | Quaternion algebra structure required for p^{1/3} theorem | 4D quaternion End(E) structure; absent for ordinary 2D commutative End(E) |

## The convergence

These three analyses approach ECDLP from:
- Analytic (Fourier/character sum theory)
- Combinatorial (algebraic topology, chain complexes)
- Algebraic (endomorphism rings, lattice theory)

All three identify the SAME obstruction: prime-field ECDLP has MINIMAL algebraic structure
(commutative 2D endomorphism ring; non-algebraic factor base forced by Bezout; no quaternion
algebra) while all sub-rho mechanisms require RICHER structure.

## Characterization

**Prime-field ECDLP hardness = minimal algebraic structure:**
- Supersingular breaks at p^{1/3}: has B_{p,∞} (4D quaternion)
- Extension-field beats rho: has algebraic factor base (Frobenius condition)
- Prime-field stays at rho: has only imaginary quadratic order (2D commutative), non-algebraic FB needed

**H-PSEUDO is the precise measure** of the gap: it asks whether the non-algebraic factor base
(forced by Bezout) achieves algebraic-type Fourier flatness — an intrinsically new phenomenon
not provable by any algebraic method.
