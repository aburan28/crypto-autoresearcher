---
id: KN-LIT-3264
type: literature
title: "Cryptanalysis of the EMD Mode of Operation"
authors:
  - "Antoine Joux"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we study the security of the Encrypt-MaskDecrypt mode of operation, also called EMD, which was recently proposed for applications such as disk-sector encryption. The EMD mode transforms an ordinary block cipher operating on n–bit blocks into a tweakable block cipher operating on large blocks of size nm bits.

## Key claims (as reported)
- We first show that EMD is not a secure tweakable block cipher and then describe efficient attacks in the context of disk-sector encryption.
- We note that the parallelizable variant of EMD, called EME that was proposed at the same time is also subject to these attacks.
- In the course of developing one of the attacks, we revisit Wagner’s generalized birthday algorithm and show that in some special cases it performs much more efficiently than in the general case.
- Due to the large scope of applicability of this algorithm, even when restricted to these special cases, we believe that this result is of independent interest.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/26560001 (1).pdf`
- `downloads/26560001 (2).pdf`
- `downloads/26560001.pdf`
