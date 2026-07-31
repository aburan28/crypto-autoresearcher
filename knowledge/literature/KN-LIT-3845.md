---
id: KN-LIT-3845
type: literature
title: "Faster index calculus for the medium prime case"
authors:
  - "Application to -bit"
  - "bit finite fields"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, factoring, finite-field, hyperelliptic, index-calculus, number-theory, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Many index calculus algorithms generate multiplicative relations between smoothness basis elements by using a process called Sieving. This process allows us to quickly filter potential candidate relations, without spending too much time to consider bad candidates.

## Key claims (as reported)
- However, from an asymptotic point of view, there is not much difference between sieving and straightforward testing of candidates.
- The reason is that even when sieving, some small amount of time is spent for each bad candidate.
- Thus, asymptotically, the total number of candidates contributes to the complexity.
- In this paper, we introduce a new technique: Pinpointing, which allows us to construct multiplicative relations much faster, thus reducing the asymptotic complexity of relations’ construction.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/78810175 (1).pdf`
- `downloads/78810175 (2).pdf`
- `downloads/78810175 (3).pdf`
- `downloads/78810175.pdf`
