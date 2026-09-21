---
id: KN-LIT-6538
type: literature
title: "Selective Opening Security from Simulatable Data Encapsulation"
authors:
  - "Felix Heuer"
  - "Bertram Poettering"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the realm of public-key encryption, the confidentiality notion of security against selective opening (SO) attacks considers adversaries that obtain challenge ciphertexts and are allowed to adaptively open them, meaning have the corresponding message and randomness revealed. SO security is stronger than IND-CCA and often required when formally arguing towards the security of multi-user applications.

## Key claims (as reported)
- While different ways of achieving SO secure schemes are known, as they generally employ expensive asymmetric building blocks like lossy trapdoor functions or lossy encryption, such constructions are routinely left aside by practitioners and standardization bodies.
- So far, formal arguments towards the SO security of schemes used in practice (e.g., for email encryption) are not known.
- In this work we shift the focus from the asymmetric to the symmetric building blocks of PKE and prove the following statement: If a PKE scheme is composed of a key encapsulation mechanism (KEM) and a blockcipher-based data encapsulation mechanism (DEM), and the DEM has specific combinatorial properties, then the PKE scheme offers SO security in the ideal cipher model.
- Fortunately, as we show, the required properties hold for popular modes of operation like CTR, CBC and CCM.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10031279 (1).pdf`
- `downloads/10031279.pdf`
