---
id: KN-LIT-6661
type: literature
title: "Simple Proofs of Space-Time and Rational Proofs of Storage"
authors:
  - "Tal Moran"
  - "Ilan Orlov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new cryptographic primitive: Proofs of SpaceTime (PoSTs) and construct an extremely simple, practical protocol for implementing these proofs. A PoST allows a prover to convince a verifier that she spent a “space-time” resource (storing data—space—over a period of time).

## Key claims (as reported)
- Formally, we define the PoST resource as a trade-off between CPU work and space-time (under reasonable cost assumptions, a rational user will prefer to use the lower-cost space-time resource over CPU work).
- Compared to a proof-of-work, a PoST requires less energy use, as the “difficulty” can be increased by extending the time period over which data is stored without increasing computation costs.
- Our definition is very similar to “Proofs of Space” [ePrint 2013/796, 2013/805] but, unlike the previous definitions, takes into account amortization attacks and storage duration.
- Moreover, our protocol uses a very different (and much simpler) technique, making use of the fact that we explicitly allow a space-time tradeoff, and doesn’t require any non-standard assumptions (beyond random oracles).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940422 (1).pdf`
- `downloads/116940422.pdf`
