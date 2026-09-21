---
id: KN-LIT-2554
type: literature
title: "Anonymous Tokens with Private Metadata Bit"
authors:
  - "Ben Kreuter"
  - "Tancrède Lepoint"
  - "Michele Orrù"
  - "Mariana P. Raykova"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a cryptographic construction for anonymous tokens with private metadata bit, called PMBTokens. This primitive enables an issuer to provide a user with a lightweight, single-use anonymous trust token that can embed a single private bit, which is accessible only to the party who holds the secret authority key and is private with respect to anyone else.

## Key claims (as reported)
- Our construction generalizes and extends the functionality of Privacy Pass (PETS’18) with this private metadata bit capability.
- It provides unforgeability, unlinkability, and privacy for the metadata bit properties based on the DDH and CTDH assumptions in the random oracle model.
- Both Privacy Pass and PMBTokens rely on non-interactive zero-knowledge proofs (NIZKs).
- We present new techniques to remove the need for NIZKs, while still achieving unlinkability.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171145 (1).pdf`
- `downloads/12171145.pdf`
