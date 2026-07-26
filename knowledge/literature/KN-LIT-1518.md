---
id: KN-LIT-1518
type: literature
title: "A correlation duet: Correlation attacks on correlation generators"
authors:
  - "Antoine Joux"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1126"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1126"
tags: [cryptanalysis, finite-field, lattice, pairing, prime-field, provable-security, quantum, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Pseudo-random correlation generators based on the QuasiAbelian syndrome decoding problem were first attacked in an article published at Asiacrypt 2025, using compressed sensing. In this paper, we revisit the security of the problem using a more traditional cryptanalytic tool, namely correlation attacks.

## Key claims (as reported)
- As a result, we get a new cryptanalysis which outperforms the attack from Asiacrypt 2025 in several directions.
- It allows recovery of secret error polynomials with larger Hamming weights, runs approximately 1 000 times faster and uses 1 000 times less memory over F3 .
- Over F4 , the speed-up and memory gain are even higher.
- Due to this new attack, it becomes necessary to entirely revisit the parameters of several pseudo-random correlation generator proposals, including FOLEAGE.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1126.pdf`
