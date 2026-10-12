---
id: KN-LIT-ae78e5
type: literature
title: "Can we Beat the Square Root Bound for ECDLP over F_{p^2} via Representations?"
authors:
  - "Claire Delaplace"
  - "Alexander May"
year: 2019
venue: "NuTMiC 2019; ePrint 2019/800"
identifiers:
  eprint: "iacr:2019/800"
  arxiv: null
  doi: null
  url: null
tags: [index-calculus, pollard-rho, representations, extension-field, p^2, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

A 4-list representation-technique algorithm for ECDLP over F_{p^2} that reduces the problem to multivariate polynomial zero-testing (via summation-type conditions) and bivariate multi-evaluation. It is currently slower than rho, but all lists have size only p^{3/4}, so a faster list construction would give o(p). This is the cleanest "combinatorial + algebraic" attempt at beating sqrt for quadratic extensions.

## Key claims (as reported)

- p^{1.314} (vs rho O(p) in terms of field size p for E(F_{p^2})); intermediate lists of size p^{3/4}.

## Relevance to this program

Representation technique for ECDLP over F_{p^2}: p^{1.314}, worse than rho's O(p). A proposal to 'beat √ with representations/subset-sum techniques' is this paper's negative.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
