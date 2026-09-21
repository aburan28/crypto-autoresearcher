---
id: KN-FIND-c93d45
type: internal_finding
title: DL circularity obstruction — Weil bound cannot close the arithmetic factor-base yield gap
tags: [weil-bound, character-sum, dl-circularity, semaev, arithmetic-factor-base, obstruction]
confidence: proved
evidence_level: argument
source_refs: [BATCH-067, DEC-20260804-1b22b2]
internal_refs: [DEC-20260804-1b22b2]
proof_status: derivation
proof_refs: [knowledge/findings/KN-FIND-c93d45.md]
added: '2026-08-04'
superseded_by: null
---

## Finding

The Weil bound for elliptic curves CANNOT be applied to prove that the Semaev arithmetic
factor-base (small-x) decomposition yield is bounded by the heuristic B^m/(m!N).

## The precise obstruction (DL circularity)

The yield bound requires bounding the Fourier coefficients:
hat{1_F}(k) = Σ_{P ∈ F} e^{2πi k·DL_G(P)/N}

The exponent k·DL_G(P)/N involves DL_G(P) — the discrete logarithm of P with respect
to generator G. This is a NON-ALGEBRAIC function of the point P (its coordinates x(P), y(P)).
The Weil bound applies only to algebraic characters (functions of x(P), y(P) over F_p).

Therefore: any bound on hat{1_F}(k) from classical exponential sum machinery (Weil,
Katz-Sarnak, Michel-Venkatesh) would require a functional relationship between DL_G(P)
and the algebraic structure of P — which is precisely what ECDLP hardness asserts is
computationally infeasible.

## What this means

1. The arithmetic factor-base gap (Bezout no-go covers algebraic FB; arithmetic FB gap
   remains open) is fundamentally different from an algebraic question.
2. Closing this gap requires either (a) proving H-PSEUDO (a new conjecture), or
   (b) showing that a sub-rho Semaev algorithm exists (which would solve ECDLP).
3. H-PSEUDO itself requires a technique that goes beyond classical algebraic geometry.

## Related: H-PSEUDO empirical evidence

BATCH-073/074 measured max_k |hat{1_F}(k)| / sqrt(B) ≈ 3 at p=1009..4001.
The constant C ≈ 3 shows no growth with p at toy scale, consistent with H-PSEUDO
being true (but not proved).
