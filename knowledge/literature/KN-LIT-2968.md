---
id: KN-LIT-2968
type: literature
title: "Combinatorially Homomorphic Encryption"
authors:
  - "Yuval Ishai"
  - "Eyal Kushnir"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, lattice]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Homomorphic encryption enables public computation over encrypted data. In the past few decades, homomorphic encryption has become a staple of both the theory and practice of cryptography.

## Key claims (as reported)
- Nevertheless, while there is a general loose understanding of what it means for a scheme to be homomorphic, to date there is no single unifying minimal definition that captures all schemes.
- In this work, we propose a new definition, which we refer to as combinatorially homomorphic encryption, which attempts to give a broad base that captures the intuitive meaning of homomorphic encryption.
- Our notion relates the ability to accomplish some task when given a ciphertext, to accomplishing the same task without the ciphertext, in the context of communication complexity.
- Thus, we say that a scheme is combinatorially homomorphic if there exists a communication complexity problem f (x, y) (where x is Alice’s input and y is Bob’s input) which requires communication c, but can be solved with communication less than c when Alice is given in addition also an encryption Ek (y) of Bob’s input (using Bob’s key k).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14369146 (1).pdf`
- `downloads/14369146.pdf`
