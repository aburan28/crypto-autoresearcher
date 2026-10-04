---
id: KN-LIT-95d1e4
type: literature
title: "Summation Polynomial Algorithms for Elliptic Curves in Characteristic Two"
authors:
  - "Steven D. Galbraith"
  - "Shishay W. Gebregiyorgis"
year: 2014
venue: "INDOCRYPT 2014, LNCS 8885, pp. 409-427; ePrint 2014/806"
identifiers:
  eprint: "iacr:2014/806"
  arxiv: null
  doi: "10.1007/978-3-319-13039-2_24"
  url: null
tags: [index-calculus, binary-field, summation-polynomial, symmetry, sat, groebner, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Practical study for prime n. It uses binary Edwards variables invariant under a large group to lower summation-polynomial degree, a symmetry-breaking factor base, and SAT solvers as an alternative to Groebner bases. This is the key crossover data point for binary curves: rho remains much faster than any summation-polynomial method for F_{2^n} of reasonable size, including for oracle-assisted static-DH variants.

## Key claims (as reported)

- Qualitative: rho "still much faster" than index calculus over prime-degree F_{2^n} of reasonable size (their experiments).

## Relevance to this program

Summation-polynomial algorithms in characteristic 2 (symmetries, 2-torsion/halving, SAT experiments); concludes rho is still much faster at reasonable sizes. Baseline for every binary PDP measurement in the three repos. Full text frozen at inputs/GG-2014-806.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-439 (bulk stub or misattributed entry; see that file's `superseded_by`).
