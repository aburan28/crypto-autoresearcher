---
id: KN-LIT-3849b1
type: literature
title: "On random walks for Pollard's rho method"
authors:
  - "Edlyn Teske"
year: 2001
venue: "Mathematics of Computation 70:809-825"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1090/S0025-5718-00-01213-8"
  url: null
tags: [pollard-rho, r-adding-walk, random-walk, walk-constant, baseline, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Extensive experimental comparison of rho iteration functions (original, r-adding, mixed walks) across groups including elliptic curves; the empirical basis for the r-adding walks used in later record computations (e.g. the secp112r1 record used a 16-adding walk; Bos-Costello-Miele use 32- and 1024-adding walks). Bernstein-Lange 2012 later showed such walks still lose a measurable constant through "higher-degree local anti-collisions".

## Key claims (as reported)

- See Teske1998; exact per-walk factors not re-extracted here.

## Relevance to this program

Empirical basis for choosing r ≥ 16–20 in r-adding walks. The program's own KS test rejecting r = 16 against a random function (EV-ECDLP-31e91c) and the walk-constant measurements in the crypto repo (ecc2k130/WALK-CONSTANT.md) are re-measurements in this line, not new phenomena.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
