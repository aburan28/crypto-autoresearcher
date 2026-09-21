---
id: KN-LIT-6600
type: literature
title: "Short-output universal hash functions and"
authors:
  - "Long Hoang Nguyen"
  - "A.W. Roscoe"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, hash, implementation, lattice, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Message authentication codes usually require the underlining universal hash functions to have a long output so that the probability of successfully forging messages is low enough for cryptographic purposes. To take advantage of fast operation on word-size parameters in modern processors, long-output universal hashing schemes can be securely constructed by concatenating several different instances of a short-output primitive.

## Key claims (as reported)
- In this paper, we describe a new method for short-output universal hash function termed digest() suitable for very fast software implementation and applicable to secure message authentication.
- The method possesses a higher level of security relative to other well-studied and computationally efficient short-output universal hashing schemes.
- Suppose that the universal hash output is fixed at one word of b bits, then the collision probability of ours is 21−b compared to 6 × 2−b of MMH, whereas 2−b/2 of NH within UMAC is far away from optimality.
- In addition to message authentication codes, we show how short-output universal hashing is applicable to manual authentication protocols where universal hash keys are used in a very different and interesting way.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/75490330 (1).pdf`
- `downloads/75490330 (2).pdf`
- `downloads/75490330 (3).pdf`
- `downloads/75490330.pdf`
