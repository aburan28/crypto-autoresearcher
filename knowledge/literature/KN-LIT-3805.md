---
id: KN-LIT-3805
type: literature
title: "Fast Leakage Assessment"
authors:
  - "Oscar Reparaz"
  - "Benedikt Gierlichs"
  - "Ingrid Verbauwhede"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a fast technique for performing the computationally heavy part of leakage assessment, in any statistical moment (or other property) of the leakage samples distributions. The proposed technique outperforms by orders of magnitude the approach presented at CHES 2015 by Schneider and Moradi.

## Key claims (as reported)
- We can carry out evaluations that before took 90 CPU-days in 4 CPU-hours (about a 500-fold speed-up).
- As a bonus, we can work with exact arithmetic, we can apply kernel-based density estimation methods, we can employ arbitrary pre-processing functions such as absolute value to power traces, and we can perform information-theoretic leakage assessment.
- Our trick is simple and elegant, and lends itself to an easy and compact implementation.
- We fit a prototype implementation in about 130 lines of C code.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10529188 (1).pdf`
- `downloads/10529188.pdf`
