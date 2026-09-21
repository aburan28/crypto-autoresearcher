---
id: KN-LIT-5045
type: literature
title: "Multitarget Decryption Failure Attacks"
authors:
  - "Jan-Pieter D’Anvers"
  - "Senne Batsleer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing, pqc, quantum, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Many lattice-based encryption schemes are subject to a very small probability of decryption failures. It has been shown that an adversary can efficiently recover the secret key using a number of ciphertexts that cause such a decryption failure.

## Key claims (as reported)
- In PKC 2019, D’Anvers et al. introduced ‘failure boosting’, a technique to speed up the search for decryption failures.
- In this work we first improve the state-of-the-art multitarget failure boosting attacks.
- We then improve the cost calculation of failure boosting and extend the applicability of these calculations to permit cost calculations of real-world schemes.
- Using our newly developed methodologies we determine the multitarget decryption failure attack cost for all parameter sets of Saber and Kyber, showing among others that the quantum security of Saber can theoretically be reduced from 172 bits to 145 bits in specific circumstances.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/131770011 (1).pdf`
- `downloads/131770011.pdf`
