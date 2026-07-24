---
id: KN-TECH-026
type: technique
title: Higher-dimensional (Kani) embedding attacks - glue-and-split
tags: [kani, glue-and-split, abelian-variety, higher-dimensional-isogeny, sidh-attack, torsion-points, cryptanalysis, adjacent]
confidence: reported
complexity: classical polynomial time (Robert, dim 4/8, provable); heuristic poly / subexponential in dim 2 depending on starting curve
applicability: reconstructing a secret isogeny from its degree and its action on a known torsion basis
source_refs: [KN-LIT-065, KN-LIT-067, KN-LIT-068]
added: 2026-07-23
superseded_by: null
---

## Method
Given a secret isogeny phi of known degree and its images phi(P), phi(Q) on a
known torsion basis (exactly SIDH's public data, KN-TECH-025), build an auxiliary
isogeny between PRODUCTS of elliptic curves (or higher-dimensional abelian
varieties) whose reducibility is governed by Kani's theorem (KN-LIT-068). By
"glue-and-split," the auxiliary isogeny is computable and reveals phi:
- **Dimension 2** (Castryck-Decru, KN-LIT-065): embed into a principally
  polarized abelian surface via a (2,2)-isogeny chain; heuristic poly-time, needs
  a special/known-endomorphism starting curve (relaxed to subexponential for
  arbitrary curves, KN-LIT-066).
- **Dimension 4 or 8** (Robert, KN-LIT-067): the reducible structure ALWAYS
  exists, giving provable polynomial time in all cases.

## Complexity indicator
The embedding dimension is the dial: higher dimension guarantees decomposability,
converting a heuristic/conditional attack into an unconditional polynomial-time
one. The cost is polynomial in the input size (isogeny degree in unary-ish /
log q), aside from small parameter-dependent factorizations.

## Relevance to this program
A striking template: a pure-math reducibility theorem (Kani, 1997) becomes a
cryptanalytic engine that turns auxiliary torsion data into a polynomial-time
break (KN-OPEN-015). The abelian-variety / Jacobian machinery overlaps the
program's genus-2 / Prym / cover-transfer work. Adjacent to the ECDLP mission.

## Applicability limits
Requires BOTH the isogeny degree AND its action on a known torsion basis; without
the torsion images (CGL, CSIDH, SQIsign) the embedding cannot be built. Computing
high-dimensional isogenies is polynomial but concretely heavy. The technique
recovers a specific isogeny, not a solution to generic path-finding (KN-OPEN-013).
