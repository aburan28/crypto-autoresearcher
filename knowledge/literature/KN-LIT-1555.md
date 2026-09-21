---
id: KN-LIT-1555
type: literature
title: "Asynchronous Lagrange-Based"
authors:
  - "Alain Passelègue"
  - "Damien Stehlé"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/973"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/973"
tags: [cryptanalysis, fhe, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study t-out-of-n threshold fully homomorphic encryption (ThFHE) based on Shamir secret sharing (SSS) in the asynchronous setting. A central bottleneck for SSS-based ThFHE is that Lagrange reconstruction during distributed decryption can amplify noise, forcing a substantially larger ciphertext modulus to maintain correctness.

## Key claims (as reported)
- In this work, we revisit SSS-based ThFHE and give a rigorous analysis of the correctness and simulation-security constraints that govern parameter choices.
- We then compare families of Lagrange interpolation points through the lens of these constraints.
- Our main contributions are analytic bounds that closely track empirical behavior and significantly reduce the modulus overhead required for distributed decryption.
- For example, for n = 512, our analysis reduces this modulus overhead (in bits) by 30% for t = n/2 and by up to 90% for t close to n, compared to prior parameterizations.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-973.pdf`
