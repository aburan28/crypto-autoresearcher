---
id: KN-LIT-2526
type: literature
title: "Analysis of SHA-512/224 and SHA-512/256"
authors:
  - "Christoph Dobraunig"
  - "Maria Eichlseder"
  - "Florian Mendel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, lattice, pairing, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In 2012, NIST standardized SHA-512/224 and SHA-512/256, two truncated variants of SHA-512, in FIPS 180-4. These two hash functions are faster than SHA-224 and SHA-256 on 64-bit platforms, while maintaining the same hash size and claimed security level.

## Key claims (as reported)
- So far, no third-party analysis of SHA-512/224 or SHA-512/256 has been published.
- In this work, we examine the collision resistance of stepreduced versions of SHA-512/224 and SHA-512/256 by using differential cryptanalysis in combination with sophisticated search tools.
- We are able to generate practical examples of free-start collisions for 44-step SHA-512/224 and 43-step SHA-512/256.
- Thus, the truncation performed by these variants on their larger state allows us to attack several more rounds compared to the untruncated family members.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520180 (1).pdf`
- `downloads/94520180.pdf`
