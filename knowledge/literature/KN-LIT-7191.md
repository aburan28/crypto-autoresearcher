---
id: KN-LIT-7191
type: literature
title: "Toward Basing Fully Homomorphic Encryption on Worst-Case Hardness"
authors:
  - "Craig Gentry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, lattice, mov-fr, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Gentry proposed a fully homomorphic public key encryption scheme that uses ideal lattices. He based the security of his scheme on the hardness of two problems: an average-case decision problem over ideal lattices, and the sparse (or “low-weight”) subset sum problem (SSSP).

## Key claims (as reported)
- We provide a key generation algorithm for Gentry’s scheme that generates ideal lattices according to a “nice” average-case distribution.
- Then, we prove a worst-case / average-case connection that bases Gentry’s scheme (in part) on the quantum hardness of the shortest independent vector problem (SIVP) over ideal lattices in the worst-case.
- (We cannot remove the need to assume that the SSSP is hard.) Our worst-case / average-case connection is the first where the average-case lattice is an ideal lattice, which seems to be necessary to support the security of Gentry’s scheme.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230116 (1).pdf`
- `downloads/62230116 (2).pdf`
- `downloads/62230116 (3).pdf`
- `downloads/62230116.pdf`
