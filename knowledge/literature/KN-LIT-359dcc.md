---
id: KN-LIT-359dcc
type: literature
title: "Speeding Up Elliptic Curve Discrete Logarithm Computations with Point Halving"
authors:
  - "Fangguo Zhang"
  - "Ping Wang"
year: 2011
venue: "IACR ePrint 2011/461"
identifiers:
  eprint: "iacr:2011/461"
  arxiv: null
  doi: null
  url: null
tags: [pollard-rho, point-halving, binary-field, iteration-function, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

For binary curves, an iteration function built on point halving (cheaper than addition) instead of an r-adding walk, with analysis of the resulting walk.

## Key claims (as reported)

- ~27% faster than previous best single-instance rho on certain NIST binary curves; 12-17% faster when many instances run with Montgomery simultaneous inversion.

## Relevance to this program

Point halving as a cheaper rho step on binary curves. Relevant to binary-field walk design (ECC2K-130); a proposal to 'use halving instead of addition in the walk' is known.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
