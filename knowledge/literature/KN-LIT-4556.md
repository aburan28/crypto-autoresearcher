---
id: KN-LIT-4556
type: literature
title: "Isogeny-based key compression without pairings"
authors:
  - "Geovandro C. C. F. Pereira"
  - "Paulo S. L. M. Barreto"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, dlp, ecdlp, elliptic-curve, endomorphism, finite-field, isogeny, pairing, provable-security, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
SIDH/SIKE-style protocols benefit from key compression to minimize their bandwidth requirements, but proposed key compression mechanisms rely on computing bilinear pairings. Pairing computation is a notoriously expensive operation, and, unsurprisingly, it is typically one of the main efficiency bottlenecks in SIDH key compression, incurring processing time penalties that are only mitigated at the cost of tradeoffs with precomputed tables.

## Key claims (as reported)
- We address this issue by describing how to compress isogeny-based keys without pairings.
- As a bonus, we also substantially reduce the storage requirements of other operations involved in key compression.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/127110165 (1).pdf`
- `downloads/127110165.pdf`
