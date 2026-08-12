---
id: KN-TECH-007
type: technique
title: BKK bound and sparse / polyhedral elimination (mixed volume)
tags: [bkk, mixed-volume, newton-polytope, sparse-elimination, polyhedral-homotopy, sparse-resultant, solving]
confidence: established
complexity: isolated toric roots bounded by MV(Newton polytopes), generically exact; polyhedral homotopy tracks MV paths; often << Bezout for sparse systems
applicability: solving/counting solutions of sparse polynomial systems by their monomial support rather than total degree
source_refs: [KN-LIT-014, KN-LIT-015]
added: 2026-07-21
superseded_by: null
---

## Method
For a system of n Laurent polynomials in n variables, the Bernstein-Kushnirenko-
Khovanskii (BKK) theorem (KN-LIT-014) bounds the number of isolated solutions in
(C*)^n by the *mixed volume* MV(P_1,...,P_n) of the Newton polytopes P_i,
generically with equality. Two solver families realize this count:
- **Polyhedral homotopy** (Huber-Sturmfels, KN-LIT-015): a generic lifting
  induces a fine mixed subdivision; each mixed cell gives a binomial start
  system; the homotopy tracks exactly MV paths (numerical, over C).
- **Sparse (toric) resultants** (Canny-Emiris): elimination via a resultant
  matrix sized by the mixed subdivision -- exact-arithmetic, much smaller than
  dense Macaulay/Bezout matrices.

## Complexity indicator (the measurable)
The driver is MV vs the Bezout number (product of total degrees). For a sparse
system with proper-subpolytope support, MV << Bezout, so support-aware solving
can be dramatically cheaper. The saturation test -- is MV/Bezout near 1? -- is
decidable at small scale and decides whether the method helps at all.

## Program usage
The candidate route for solving Semaev decomposition systems (KN-TECH-002) below
the dense composed-resultant cost the program measured (exponent ~1.979). The
program's BKK experiments (RQ-BKK-001, RQ-BKKMV-001, KN-OPEN-004) compute the
exact Semaev Newton polytopes and MV, cross-check MV against brute-force F_p
solution counts, and compare which Bezout baseline (total-degree vs multigraded
box) is saturated. NOTE: mixed volume caps all BKK-based algorithms, so the MV
arithmetic bounds the method even where polyhedral homotopy (a complex-analytic
path tracker) is not directly usable over F_p.

## Applicability limits
Polyhedral homotopy is numerical (over C); over F_p the transferable content is
the mixed-volume count and mixed-subdivision structure, realized via sparse
resultants or support-aware evaluation. If the Semaev polytopes are Newton-
saturated (full box support), MV = Bezout and sparse == dense -- the method
gives nothing (the candidate's own disproof track).
