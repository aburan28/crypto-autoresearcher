---
id: KN-LIT-f7558f
type: literature
title: "Using Equivalence Classes to Accelerate Solving the Discrete Logarithm Problem in a Short Interval"
authors:
  - "Steven D. Galbraith"
  - "Raminder S. Ruprai"
year: 2010
venue: "PKC 2010, LNCS 6056, pp. 368-383 (full version ePrint 2010/615)"
identifiers:
  eprint: "iacr:2010/615"
  arxiv: null
  doi: "10.1007/978-3-642-13013-7_22"
  url: null
tags: [pollard-rho, kangaroo, interval-dlp, equivalence-classes, negation-map, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Standard kangaroos cannot use equivalence classes, so this paper builds a Gaudry-Schost variant that exploits fast inversion (negation) for the interval DLP. Walks leaving the search region and fruitless cycles eat part of the gain in practice. It is the peer-reviewed precursor of the "kangaroo with symmetry" (SOTA) methods used by current secp256k1 puzzle solvers.

## Key claims (as reported)

- Heuristic average ~1.36*sqrt(N) group operations for groups with fast inversion (vs ~2*sqrt(N) for classic kangaroo and ~1.71*sqrt(N) for the best prior variant).

## Relevance to this program

Equivalence classes (negation) for interval DLP: ~1.36√N. Baseline for kangaroo-with-symmetry claims, including community 'SOTA' kangaroo solvers.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-7437 (bulk stub or misattributed entry; see that file's `superseded_by`).
