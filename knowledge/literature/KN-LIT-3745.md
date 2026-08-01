---
id: KN-LIT-3745
type: literature
title: "Extending Oblivious Transfer with Low Communication via Key-Homomorphic PRFs"
authors:
  - "Peter Scholl"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new approach to extending oblivious transfer with communication complexity that is logarithmic in the security parameter. Our method only makes black-box use of the underlying cryptographic primitives, and can achieve security against an active adversary with almost no overhead on top of passive security.

## Key claims (as reported)
- This results in the first oblivious transfer protocol with sublinear communication and active security, which does not require any non-black-box use of cryptographic primitives.
- Our main technique is a novel twist on the classic OT extension of Ishai et al.
- (Crypto 2003), using an additively key-homomorphic PRF to reduce interaction.
- We first use this to construct a protocol for a large batch of 1-out-of-n OTs on random inputs, with amortized o(1) communication.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10770191 (1).pdf`
- `downloads/10770191 (2).pdf`
- `downloads/10770191 (3).pdf`
- `downloads/10770191 (4).pdf`
- `downloads/10770191.pdf`
