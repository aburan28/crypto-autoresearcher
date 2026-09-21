---
id: KN-LIT-6023
type: literature
title: "Public-Key Encryption in the Bounded-Retrieval Model"
authors:
  - "Daniel Wichs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct the first public-key encryption scheme in the Bounded-Retrieval Model (BRM), providing security against various forms of adversarial “key leakage” attacks. In this model, the adversary is allowed to learn arbitrary information about the decryption key, subject only to the constraint that the overall amount of “leakage” is bounded by at most ` bits.

## Key claims (as reported)
- The goal of the BRM is to design cryptographic schemes that can flexibly tolerate arbitrarily leakage bounds ` (few bits or many Gigabytes), by only increasing the size of secret key proportionally, but keeping all the other parameters — including the size of the public key, ciphertext, encryption/decryption time, and the number of secret-key bits accessed during decryption — small and independent of `.
- As our main technical tool, we introduce the concept of an Identity-Based Hash Proof System (IB-HPS), which generalizes the notion of hash proof systems of Cramer and Shoup [CS02] to the identity-based setting.
- We give three different constructions of this primitive based on: (1) bilinear groups, (2) lattices, and (3) quadratic residuosity.
- As a result of independent interest, we show that an IB-HPS almost immediately yields an Identity-Based Encryption (IBE) scheme which is secure against (small) partial leakage of the target identity’s decryption key.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320229 (1).pdf`
- `downloads/66320229 (2).pdf`
- `downloads/66320229 (3).pdf`
- `downloads/66320229.pdf`
