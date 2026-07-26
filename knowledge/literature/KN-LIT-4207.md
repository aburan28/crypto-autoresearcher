---
id: KN-LIT-4207
type: literature
title: "High-speed key encapsulation from NTRU"
authors:
  - "Andreas Hülsing"
  - "Joost Rijneveld"
  - "John Schanck"
  - "Peter Schwabe"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, lattice, pqc, protocol, provable-security, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents software demonstrating that the 20year-old NTRU cryptosystem is competitive with more recent latticebased cryptosystems in terms of speed, key size, and ciphertext size. We present a slightly simplified version of textbook NTRU, select parameters for this encryption scheme that target the 128-bit post-quantum security level, construct a KEM that is CCA2-secure in the quantum random oracle model, and present highly optimized software targeting Intel CPUs with the AVX2 vector instruction set.

## Key claims (as reported)
- This software takes only 307 914 cycles for the generation of a keypair, 48 646 for encapsulation, and 67 338 for decapsulation.
- It is, to the best of our knowledge, the first NTRU software with full protection against timing attacks.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10529225 (1).pdf`
- `downloads/10529225.pdf`
