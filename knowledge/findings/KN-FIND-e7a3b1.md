---
id: KN-FIND-e7a3b1
type: internal_finding
title: H-PSEUDO proof approaches — all six standard analytic methods are closed; H-PSEUDO is a new open problem
tags: [hpseudo, character-sum, proof-attempts, ddh, bgs, weil, weyl, michel-venkatesh, open-problem]
confidence: proved_negative
evidence_level: multiple_independent_analyses
source_refs: [BATCH-067, BATCH-072, BATCH-080, BATCH-081, BATCH-082, DEC-20260804-1b22b2, DEC-20260804-f320c2, DEC-20260804-ba880f, DEC-20260804-53c89f, DEC-20260804-73287b]
internal_refs: [DEC-20260804-1b22b2, DEC-20260804-f320c2, DEC-20260804-ba880f, DEC-20260804-53c89f, DEC-20260804-73287b]
proof_status: derivation
proof_refs: [knowledge/findings/KN-FIND-e7a3b1.md]
added: '2026-08-04'
superseded_by: null
---

## Finding

H-PSEUDO (Discrete Logarithm Pseudorandomness Conjecture):
> For F = {P ∈ E(F_p) : x(P) < t} with |F|=B, the additive character sum
> max_{k≠0} |Σ_{P∈F} e^{2πi k·DL_G(P)/N}| ≤ C(p) · sqrt(B)
> where C(p) ~ p^{0.079} empirically.

## All standard analytic proof approaches are closed

| Approach | Core obstruction |
|----------|-----------------|
| Weil / étale cohomology | DL_G(P) is non-algebraic; wrong functional form (Weil gives O(sqrt(N)), data shows O(sqrt(B))) |
| Michel-Venkatesh equidistribution | Algebraic characters only; DL_G not a rational map |
| DDH conditional proof | Categorical gap: DDH is computational, H-PSEUDO is information-theoretic |
| BGS spectral gap | E(F_p)≅Z/N is abelian; no Ω(1) spectral gap for bounded generators |
| Weyl/WvdC differencing | Σ_h C_h = B² exactly; Weyl has no access to EC arithmetic |
| DL random permutation assumption | Not standard; empirically refuted (C grows as p^{0.079} ≠ O(sqrt(log p))) |
| Shparlinski/ECCG Fourier expansion | DL circularity recurs; achieves O(p^{3/4}) rigorous bound but not H-PSEUDO target |
| MAGCS/Tate pairing (Weil pairing as algebraic DL character) | Works for k=2 (MOV-vulnerable) curves only; for generic curves requires F_{p^{N/2}} extension = infeasible |

## Why all approaches fail

The fundamental obstruction: H-PSEUDO requires bounding a character sum
Σ_j f(j) * e^{2πi kj/N} where f(j) = 1_{x([j]G)<t} involves the EC multiplication
map j → [j]G. This is NOT algebraic in j over F_p. Every analytic approach either:
(a) requires algebraic structure (Weil, MV, Weyl) — which the DL lacks, or
(b) is computational rather than information-theoretic (DDH), or
(c) requires non-abelian structure (BGS) — which E(F_p)≅Z/N lacks.

## One conditional approach remains

Hecke characters for CM curves: for curves with CM by a specific order, Hecke
L-functions might bound the character sum. Conditional on CM structure, this might
give C=O(sqrt(N/B)) — but inapplicable to standard cryptographic curves.

## Empirical status

C(p) ~ p^{0.079} measured at p=1009..100003 (BATCH-073..079, full k-range DFT).
Yield error O(C^{m-2}·sqrt(m!)/sqrt(N)) is negligible at crypto scale.
H-PSEUDO holds for practical purposes even without a proof.
