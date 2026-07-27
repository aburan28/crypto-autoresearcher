---
id: KN-LIT-4560
type: literature
title: "Jack L.H.Crawford Queen Mary Univ. of London"
authors:
  - "Craig Gentry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mov-fr]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe our recent experience, building a system that uses fully-homomorphic encryption (FHE) to approximate the coefficients of a logistic-regression model, built from genomic data. The aim of this project was to examine the feasibility of a solution that operates “deep within the bootstrapping regime,” solving a problem that appears too hard to be addressed just with somewhat-homomorphic encryption.

## Key claims (as reported)
- As part of this project, we implemented optimized versions of many “bread and butter” FHE tools.
- These tools include binary arithmetic, comparisons, partial sorting, and low-precision approximation of “complicated functions” such as reciprocals and logarithms.
- Our eventual solution can handle thousands of records and hundreds of fields, and it takes a few hours to run.
- To achieve this performance we had to be extremely frugal with expensive bootstrapping and data-movement operations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/real-work.pdf`
