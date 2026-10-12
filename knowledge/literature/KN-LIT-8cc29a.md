---
id: KN-LIT-8cc29a
type: literature
title: "Brace for impact: ECDLP challenges for quantum cryptanalysis"
authors:
  - "Pierre-Luc Dallaire-Demers"
  - "William Doyle"
  - "Timothy Foo"
year: 2025
venue: "arXiv:2508.14011"
identifiers:
  eprint: null
  arxiv: "2508.14011"
  doi: null
  url: null
tags: [quantum, ecdlp, challenges, benchmarks]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

A difficulty-graded ladder of secp256k1-shaped ECDLP challenges (y^2 = x^3 + 7 over primes from 6 to 256 bits, with NUMS points and no pre-chosen secret). Classical cost is calibrated against Pollard-rho records and quantum cost against Shor resource estimates. It is a ready-made benchmark ladder for classical rho/kangaroo implementations too.

## Key claims (as reported)

- Their scenarios place the 256-bit instance in a 2027-2033 window for quantum attack (authors' assumptions).

## Relevance to this program

ECDLP challenge ladder for quantum cryptanalysis (2025); context for small-curve benchmark design.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-1351 (bulk stub or misattributed entry; see that file's `superseded_by`).
