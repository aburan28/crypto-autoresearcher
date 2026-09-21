---
id: KN-LIT-4686
type: literature
title: "Leakage-Resilient Cryptography From the Inner-Product Extractor"
authors:
  - "Stefan Dziembowski"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a generic method to secure various widely-used arbitrary cryptosystems against side-channel leakage, as long as the leakage adheres three restrictions: rst, it is bounded per observation but in total can be arbitrary large. Second, memory parts leak , and, third, the randomness that is used for certain operations comes from a simple (non-uniform) distribution.

## Key claims (as reported)
- As a fundamental building block, we construct a scheme to store a cryptographic secret such that it remains hidden, even given arbitrary continuous leakage from the storage.
- To this end, we use a randomized encoding and develop a method to securely these encodings even in the presence of leakage.
- We then show that our encoding scheme exhibits an e cient additive homomorphism which can be used to protect important cryptographic tasks such as identi cation, signing and encryption.
- More precisely, we propose implementations of the Okamoto identi cation scheme, and of an ElGamal-based cryptosystem with security against continuous leakage, as long as the leakage adheres the above mentioned restrictions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/70730694 (1).pdf`
- `downloads/70730694 (2).pdf`
- `downloads/70730694 (3).pdf`
- `downloads/70730694.pdf`
