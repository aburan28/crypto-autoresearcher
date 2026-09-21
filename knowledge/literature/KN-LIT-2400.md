---
id: KN-LIT-2400
type: literature
title: "Algebraic Group Model with Oblivious Sampling"
authors:
  - "Helger Lipmaa"
  - "Roberto Parisella"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, dlp, elliptic-curve, implementation, pairing, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the algebraic group model (AGM), an adversary has to return with each group element a linear representation with respect to input group elements. In many groups, it is easy to sample group elements obliviously without knowing such linear representations.

## Key claims (as reported)
- Since the AGM does not model this, it can be used to prove the security of spurious knowledge assumptions.
- We show several well-known zk-SNARKs use such assumptions.
- We propose AGM with oblivious sampling (AGMOS), an AGM variant where the adversary can access an oracle that allows sampling group elements obliviously from some distribution.
- We show that AGM and AGMOS are different by studying the family of “total knowledge-of-exponent” assumptions, showing that they are all secure in the AGM, but most are not secure in the AGMOS if the DL holds.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14369153 (1).pdf`
- `downloads/14369153.pdf`
