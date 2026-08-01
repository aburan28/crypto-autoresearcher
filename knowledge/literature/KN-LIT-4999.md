---
id: KN-LIT-4999
type: literature
title: "Multi-Key Homomophic Encryption from TFHE"
authors:
  - "Hao Chen"
  - "Ilaria Chillotti"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we propose a Multi-Key Homomorphic Encryption (MKHE) scheme by generalizing the low-latency homomorphic encryption by Chillotti et al. Our scheme can evaluate a binary gate on ciphertexts encrypted under different keys followed by a bootstrapping.

## Key claims (as reported)
- The biggest challenge to meeting the goal is to design a multiplication between a bootstrapping key of a single party and a multi-key RLWE ciphertext.
- We propose two different algorithms for this hybrid product.
- Our first method improves the ciphertext extension by Mukherjee and Wichs (EUROCRYPT 2016) to provide better performance.
- The other one is a whole new approach which has advantages in storage, complexity, and noise growth.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210155 (1).pdf`
- `downloads/119210155.pdf`
