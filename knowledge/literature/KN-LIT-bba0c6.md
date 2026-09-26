---
id: KN-LIT-bba0c6
type: literature
title: "Symmetrized Summation Polynomials: Using Small Order Torsion Points to Speed Up Elliptic Curve Index Calculus"
authors:
  - "Jean-Charles Faugère"
  - "Louise Huot"
  - "Antoine Joux"
  - "Guénaël Renault"
  - "Vanessa Vitse"
year: 2014
venue: "EUROCRYPT 2014, LNCS 8441, pp. 40-57"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1007/978-3-642-55220-5_3"
  url: null
tags: [index-calculus, symmetry, summation-polynomial, torsion, twisted-edwards, extension-field, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Uses the action of rational 2-torsion (and larger small-order torsion) points on summation polynomials to symmetrise them further, which reduces degree and variable count in the PDP for curves having such torsion. For degree-5 curves with cofactor 2, such as ecGFp5, this is the most relevant symmetry-exploitation reference.

## Key claims (as reported)

- Speed-ups in the decomposition step (not re-extracted).

## Relevance to this program

Symmetrized summation polynomials using small-order torsion points. The in-house 2-torsion-symmetrised chains and the ecGFp5 (Z/2)^4 ⋊ S_5 estimate (research/gfp5_deployed_curves_20260920.md) build on it; the crypto repo's symmetrised-coordinates note retracts its novelty against this paper.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-6917 (bulk stub or misattributed entry; see that file's `superseded_by`).
