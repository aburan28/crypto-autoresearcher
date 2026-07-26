---
id: KN-LIT-1854
type: literature
title: "Round-Based Approximation of (Higher-Order)"
authors:
  - "Differential-Linear Correlation⋆"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/358"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/358"
tags: [cryptanalysis, factoring, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents a new method for approximating the correlations of differential-linear distinguishers. From the perspective of Beyne’s geometric approach, the differential-linear correlation is a corresponding coordinate of the correlation vector associated with the ciphertext multiset, which can be obtained by using the correlation matrix of the 2-wise form of the cipher.

## Key claims (as reported)
- The composite nature of the correlation matrix leads to a round-based approach to approximate the correlation vector.
- This simple approximation is remarkably precise, yielding the most accurate estimation for differential-linear correlations in Ascon thus far and the first DL distinguishers for 6-round Ascon-128a initialization.
- For Present, we present 17-round DL distinguishers, 4 rounds longer than the current record.
- To apply the round-based approach to ciphers with the large Chi (χ) function as nonlinear functions, we derive theorems to handle the correlation propagation for χ and its 2-wise form.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-358.pdf`
