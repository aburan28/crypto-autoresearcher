---
id: KN-LIT-6349
type: literature
title: "Rubato: Noisy Ciphers for Approximate Homomorphic Encryption"
authors:
  - "Jincheol Ha"
  - "Seongkwang Kim⋆"
  - "Byeonghak Lee"
  - "Jooyoung Lee⋆⋆"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, lattice, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A transciphering framework converts a symmetric ciphertext into a homomorphic ciphertext on the server-side, reducing computational and communication overload on the client-side. In Asiacrypt 2021, Cho et al. proposed the RtF framework that supports approximate computation.

## Key claims (as reported)
- In this paper, we propose a family of noisy ciphers, dubbed Rubato, with a novel design strategy of introducing noise to a symmetric cipher of a low algebraic degree.
- With this strategy, the multiplicative complexity of the cipher is significantly reduced, compared to existing HE-friendly ciphers, without degrading the overall security.
- More precisely, given a moderate block size (16 to 64), Rubato enjoys a low multiplicative depth (2 to 5) and a small number of multiplications per encrypted word (2.1 to 6.25) at the cost of slightly larger ciphertext expansion (1.26 to 1.31).
- The security of Rubato is supported by comprehensive analysis including symmetric and LWE cryptanalysis.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760256 (1).pdf`
- `downloads/132760256.pdf`
