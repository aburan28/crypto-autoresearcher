---
id: KN-LIT-2633
type: literature
title: "Authenticated Key Exchange from Ideal Lattices Jiang Zhang1 , Zhenfeng Zhang1, , Jintai Ding2,3"
authors:
  - "Michael Snook"
  - "Özgür Dagdelen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, pairing, pqc, protocol, provable-security, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we present a practical and provably secure two-pass authenticated key exchange protocol over ideal lattices, which is conceptually simple and has similarities to the Diffie-Hellman based protocols such as HMQV (CRYPTO 2005) and OAKE (CCS 2013). Our method does not involve other cryptographic primitives—in particular, it does not use signatures—which simplifies the protocol and enables us to base the security directly on the hardness of the ring learning with errors problem.

## Key claims (as reported)
- The security is proven in the Bellare-Rogaway model with weak perfect forward secrecy in the random oracle model.
- We also give a one-pass variant of our two-pass protocol, which might be appealing in specific applications.
- Several concrete choices of parameters are provided, and a proof-of-concept implementation shows that our protocols are indeed practical.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560281 (1).pdf`
- `downloads/90560281.pdf`
