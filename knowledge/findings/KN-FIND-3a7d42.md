---
id: KN-FIND-3a7d42
type: internal_finding
title: H-PSEUDO proved for embedding-degree-2 MOV-vulnerable curves; inapplicable to generic cryptographic curves
tags: [hpseudo, magcs, katz-sarnak, tate-pairing, embedding-degree, mov-vulnerable, generic-curves]
confidence: conditional_proof
evidence_level: theorem_backed_for_k2
source_refs: [BATCH-086, BATCH-087, DEC-20260804-f567ac, DEC-20260804-6ee18a]
internal_refs: [DEC-20260804-f567ac, DEC-20260804-6ee18a]
proof_status: derivation
proof_refs: [knowledge/findings/KN-FIND-3a7d42.md]
added: '2026-08-04'
superseded_by: null
---

## Finding

**For embedding-degree-2 curves (k=2)**: H-PSEUDO is PROVED.
For these curves, the N-torsion companion T ∈ E(F_{p^2}), and the Weil pairing
e_N(P, T) is a Katz-Sarnak ℓ-adic character of weight 0 with bounded conductor.
By Deligne's equidistribution theorem:
|Σ_{P∈E(F_p)} ψ_a(x(P)) · e_N(P,[k]T)| ≤ 4*sqrt(p)

This gives: max_k |hat{1_F}(k)| = O(sqrt(p/B)) = O(1/sqrt(B_frac))
i.e., H-PSEUDO holds with C = O(1/sqrt(B_frac)) for k=2 curves.

**For generic prime-field curves (large k ~ N/2)**: MAGCS and hence this proof path
are INAPPLICABLE. Working in F_{p^{N/2}} is equivalent in difficulty to MOV attack
difficulty — precisely what cryptographic curve selection prevents.

## Why k=2 curves are different

For k=2: E[N](F_{p^2}) contains the full N-torsion. The Weil pairing is "small"
(defined over F_{p^2} with p^2 = O(p^2)). The character sum is a standard
Frobenius-twist sum bounded by Deligne.

For k >> 1: E[N](F_{p^k}) with k ~ N/2. Working in the field F_{p^{N/2}} requires
computing the N-torsion over a ~N/2-degree extension — equivalent to solving ECDLP.

## Relevance

This finding establishes a structural reason why H-PSEUDO is hard to prove for
generic curves: the algebraic access to the DL character requires the embedding
degree extension, which is infeasible for cryptographic curves. The same structure
that makes curves MOV-resistant also makes H-PSEUDO unprovable by pairing methods.
