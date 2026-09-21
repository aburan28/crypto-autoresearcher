---
id: KN-LIT-6004
type: literature
title: "Public Key Compression and Modulus Switching for Fully Homomorphic Encryption over the Integers"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a compression technique that reduces the public key size of van Dijk, Gentry, Halevi and Vaikuntanathan’s (DGHV) fully homomorphic scheme over the integers from Õ(λ7 ) to Õ(λ5 ). Our variant remains semantically secure, but in the random oracle model.

## Key claims (as reported)
- We obtain an implementation of the full scheme with a 10.1 MB public key instead of 802 MB using similar parameters as in [7].
- Additionally we show how to extend the quadratic encryption technique of [7] to higher degrees, to obtain a shorter public-key for the basic scheme.
- This paper also describes a new modulus switching technique for the DGHV scheme that enables to use the new FHE framework without bootstrapping from Brakerski, Gentry and Vaikuntanathan with the DGHV scheme.
- Finally we describe an improved attack against the Approximate GCD Problem on which the DGHV scheme is based, with complexity Õ(2ρ ) instead of Õ(23ρ/2 ).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72370441 (1).pdf`
- `downloads/72370441 (2).pdf`
- `downloads/72370441 (3).pdf`
- `downloads/72370441.pdf`
