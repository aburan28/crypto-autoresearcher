---
id: KN-LIT-1471
type: literature
title: "Simplified Meet-in-the-middle Preimage Attacks on AES-based Hashing Mathieu Degré"
authors:
  - "Univ Rennes"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/2213"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/2213"
tags: [cryptanalysis, hash, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The meet-in-the-middle (MITM) attack is a powerful cryptanalytic technique leveraging time-memory tradeoffs to break cryptographic primitives. Initially introduced for block cipher cryptanalysis, it has since been extended to hash functions, particularly preimage attacks on AES-based compression functions.

## Key claims (as reported)
- Over the years, various enhancements such as superposition MITM (Bao et al., CRYPTO 2022) and bidirectional propagations have significantly improved MITM attacks, but at the cost of increasing complexity of automated search models.
- In this work, we propose a unified mixed integer linear programming (MILP) model designed to improve the search for optimal pre-image MITM attacks against AES-based compression functions.
- Our model generalizes previous approaches by simplifying both the modeling and the corresponding attack algorithm.
- In particular, it ensures that all identified attacks are valid.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-2213.pdf`
