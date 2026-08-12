---
id: KN-LIT-7601
type: literature
title: "Cryptanalytic Properties of Mealy Machines"
authors:
  - "Zhongfeng Niu"
  - "Tim Beyne"
  - "Kai Hu"
  - "Meiqin Wang"
year: 2026
venue: 'IACR ePrint 2026/1193 (SECRET-KEY CRYPTOGRAPHY)'
identifiers:
  eprint: iacr:2026/1193
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/1193
tags: [geometric-approach, mealy-machine, s-function, unified-framework, linear, differential, integral, boomerang, differential-linear, symmetric, methodology, adjacent]
confidence: reported
citation_verified: web
added: "2026-07-28"
superseded_by: null
---

## Contribution
A systematic method to compute cryptanalytic properties of arbitrary Mealy machines /
S-functions, giving **a uniform formula covering linear, (quasi-)differential,
(ultrametric) integral, differential-linear, and boomerang properties at once** — any
property compatible with how the function's input and output are split into chunks.

## Key claims (as reported)
- Built on the **geometric approach to cryptanalysis**; the uniform formula applies to any
  chunk-compatible property.
- Worked out for modular addition, the Chi- and ChiChi-functions, and the SHA-1 step
  function.
- Proof-of-concept applications: a boomerang distinguisher for the Subterranean
  permutation; more accurate correlations of conditional linear approximations in
  partitioning-based differential-linear attacks; and a new way to compute the algebraic
  normal form of the inverse of the Chi-function.

## Relevance to this program
Symmetric-key, and **no ECDLP content**. Recorded for the structural point it makes, which
is the exact counterpoint to [[KN-LIT-7595]] and is worth having both sides of on file.

[[KN-LIT-7595]] proceeds by treating the classical attack families as *distinct lenses*
and hunting for a sixth; its central negative result is that no sixth **per-byte-algebraic**
lens exists, argued group-theoretically. This paper goes the other way: it exhibits a
single formalism in which linear, differential, integral, differential-linear, and
boomerang properties are all instances of one computation. **The families being unifiable
under one formula and the families being individually exhausted are compatible claims** —
and together they sharpen what a genuinely new family would have to be. A "new lens" that
turns out to be chunk-compatible in the sense used here is, by this paper's account,
already covered.

For this program the transferable question is whether an analogous unification exists on
the asymmetric side: the ECDLP attack families (generic/rho, index calculus and descent,
isogeny/endomorphism-ring methods, lattice/HNP in the leakage model) are catalogued
separately in the corpus with no shared formalism, and no one has asked whether they admit
one. That is a question, not a lead; nothing here supplies the machinery, since the
geometric approach is built for Boolean/chunked functions on fixed-width state.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved on
2026-07-28 (hence `confidence: reported`). ePrint metadata: last updated 2026-07-27,
category SECRET-KEY CRYPTOGRAPHY.

NOT verified here: the uniform formula and the precise meaning of "chunk-compatible"; the
worked examples; the Subterranean boomerang distinguisher; the conditional-linear
correlation improvement; and the Chi-inverse ANF method. The suggestion of an asymmetric-side
analogue is this program's speculation and is **not** made by the paper.
