---
id: KN-LIT-7305
type: literature
title: "Two-Pass Authenticated Key Exchange with"
authors:
  - "Explicit Authentication"
  - "Tight Security"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a generic construction of 2-pass authenticated key exchange (AKE) scheme with explicit authentication from key encapsulation mechanism (KEM) and signature (SIG) schemes. We improve the security model due to Gjøsteen and Jager [Crypto2018] to a stronger one.

## Key claims (as reported)
- In the strong model, if a replayed message is accepted by some user, the authentication of AKE is broken.
- We define a new security notion named “IND-mCPA with adaptive reveals” for KEM.
- When the underlying KEM has such a security and SIG has unforgeability with adaptive corruptions, our construction of AKE equipped with counters as states is secure in the strong model, and stateless AKE without counter is secure in the traditional model.
- We also present a KEM possessing tight “IND-mCPA security with adaptive reveals” from the Computation Diffie-Hellman assumption in the random oracle model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491414 (1).pdf`
- `downloads/12491414.pdf`
