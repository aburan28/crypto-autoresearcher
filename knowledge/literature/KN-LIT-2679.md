---
id: KN-LIT-2679
type: literature
title: "Better Bootstrapping in Fully Homomorphic Encryption"
authors:
  - "Craig Gentry"
  - "Shai Halevi"
  - "Nigel P. Smart"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, fhe, implementation, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Gentry’s bootstrapping technique is currently the only known method of obtaining a “pure” fully homomorphic encryption (FHE) schemes, and it may offers performance advantages even in cases that do not require pure FHE (e.g., when using the noise-control technique of Brakerski-Gentry-Vaikuntanathan). The main bottleneck in bootstrapping is the need to evaluate homomorphically the reduction of one integer modulo another.

## Key claims (as reported)
- This is typically done by emulating a binary modular reduction circuit, using bit operations on binary representation of integers.
- We present a simpler approach that bypasses the homomorphic modularreduction bottleneck to some extent, by working with a modulus very close to a power of two.
- Our method is easier to describe and implement than the generic binary circuit approach, and we expect it to be faster in practice (although we did not implement it yet).
- In some cases it also allows us to store the encryption of the secret key as a single ciphertext, thus reducing the size of the public key.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72930001 (1).pdf`
- `downloads/72930001 (2).pdf`
- `downloads/72930001 (3).pdf`
- `downloads/72930001.pdf`
