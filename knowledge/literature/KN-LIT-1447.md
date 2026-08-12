---
id: KN-LIT-1447
type: literature
title: "PaCo: Bootstrapping for CKKS via Partial CoeffToSlot"
authors:
  - "Jean-Sébastien Coron(B)"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/886"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/886"
tags: [fhe, finite-field, lattice, mov-fr, pairing, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce PaCo, a novel and efficient bootstrapping procedure for the CKKS homomorphic encryption scheme, where PaCo stands for (Bootstrapping via) Partial CoeffToSlot. At a high level, PaCo reformulates the CKKS decryption equation in terms of blind rotations and modular additions.

## Key claims (as reported)
- This reformulated decryption circuit is then evaluated homomorphically within the CKKS framework.
- Our approach makes use of the circle group in the complex plane to simulate modular additions via complex multiplication, and utilizes alternative polynomial ring structures to support blind rotations.
- These ring structures are enabled by a variant of the CoeffToSlot operation, which we call a partial CoeffToSlot.
- This yields a new bootstrapping approach within CKKS, achieving a computational complexity which is logarithmic in the number of complex slots.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-886.pdf`
