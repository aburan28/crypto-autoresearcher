---
id: KN-LIT-7169
type: literature
title: "Time-Space Tradeoffs and Short Collisions in Merkle-Damgård Hash Functions"
authors:
  - "David Cash"
  - "Andrew Drucker"
  - "Hoeteck Wee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study collision-finding against Merkle-Damgård hashing in the random-oracle model by adversaries with an arbitrary S-bit auxiliary advice input about the random oracle and T queries. Recent work showed that such adversaries can find collisions (with respect to a random IV) with advantage Ω(ST 2 /2n ), where n is the output length, beating the birthday bound by a factor of S.

## Key claims (as reported)
- These attacks were shown to be optimal.
- We observe that the collisions produced are very long, on the order of T blocks, which would limit their practical relevance.
- We prove several results related to improving these attacks to find shorter collisions.
- We first exhibit a simple attack for finding B-block-long collisions achieving advantage Ω̃(ST B/2n ).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171319 (1).pdf`
- `downloads/12171319.pdf`
