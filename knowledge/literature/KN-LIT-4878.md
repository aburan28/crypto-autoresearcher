---
id: KN-LIT-4878
type: literature
title: "MD4 is Not One-Way"
authors:
  - "Gaëtan Leurent"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
MD4 is a hash function introduced by Rivest in 1990. It is still used in some contexts, and the most commonly used hash functions (MD5, SHA-1, SHA-2) are based on the design principles of MD4.

## Key claims (as reported)
- MD4 has been extensively studied and very efficient collision attacks are known, but it is still believed to be a one-way function.
- In this paper we show a partial pseudo-preimage attack on the compression function of MD4, using some ideas from previous cryptanalysis of MD4.
- We can choose 64 bits of the output for the cost of 232 compression function computations (the remaining bits are randomly chosen by the preimage algorithm).
- This gives a preimage attack on the compression function of MD4 with complexity 296 , and we extend it to an attack on the full MD4 with complexity 2102 .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/50860419 (1).pdf`
- `downloads/50860419 (2).pdf`
- `downloads/50860419 (3).pdf`
- `downloads/50860419.pdf`
