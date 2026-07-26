---
id: KN-LIT-2936
type: literature
title: "Cofactorization on Graphics Processing Units"
authors:
  - "Andrea Miele"
  - "Joppe W. Bos"
  - "Thorsten Kleinjung"
  - "Arjen K. Lenstra"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, elliptic-curve, factoring, number-theory, pairing, rsa, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show how the cofactorization step, a compute-intensive part of the relation collection phase of the number field sieve (NFS), can be farmed out to a graphics processing unit. Our implementation on a GTX 580 GPU, which is integrated with a state-of-the-art NFS implementation, can serve as a cryptanalytic co-processor for several Intel i7-3770K quad-core CPUs simultaneously.

## Key claims (as reported)
- This allows those processors to focus on the memory-intensive sieving and results in more useful NFSrelations found in less time.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310110 (1).pdf`
- `downloads/87310110 (2).pdf`
- `downloads/87310110 (3).pdf`
- `downloads/87310110.pdf`
