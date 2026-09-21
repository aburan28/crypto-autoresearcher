---
id: KN-LIT-6780
type: literature
title: "Square Span Programs with Applications to Succinct NIZK Arguments"
authors:
  - "George Danezis"
  - "Cédric Fournet"
  - "Jens Groth"
  - "Markulf Kohlweiss"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a new characterization of NP using square span programs (SSPs). We first characterize NP as affine map constraints on small vectors.

## Key claims (as reported)
- We then relate this characterization to SSPs, which are similar but simpler than Quadratic Span Programs (QSPs) and Quadratic Arithmetic Programs (QAPs) since they use a single series of polynomials rather than 2 or 3.
- We use SSPs to construct succinct non-interactive zero-knowledge arguments of knowledge.
- For performance, our proof system is defined over Type III bilinear groups; proofs consist of just 4 group elements, verified in just 6 pairings.
- Concretely, using the Pinocchio libraries, we estimate that proofs will consist of 160 bytes verified in less than 6 ms.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730294 (1).pdf`
- `downloads/88730294 (2).pdf`
- `downloads/88730294 (3).pdf`
- `downloads/88730294.pdf`
