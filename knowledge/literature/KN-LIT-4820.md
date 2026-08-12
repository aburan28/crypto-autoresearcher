---
id: KN-LIT-4820
type: literature
title: "LP Solutions of Vectorial Integer Subset Sums – Cryptanalysis of Galbraith’s Binary Matrix LWE"
authors:
  - "Gottfried Herold"
  - "Alexander May"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, mov-fr, pqc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider Galbraith’s space efficient LWE variant, where the (m × n)-matrix A is binary. In this binary case, solving a vectorial subset sum problem over the integers allows for decryption.

## Key claims (as reported)
- We show how to solve this problem using (Integer) Linear Programming.
- Our attack requires only a fraction of a second for all instances in a regime for m that cannot be attacked by current lattice algorithms.
- E.g. we are able to solve 100 instances of Galbraith’s small LWE challenge (n, m) = (256, 400) all in a fraction of a second.
- We also show under a mild assumption that instances with m ≤ 2n can be broken in polynomial time via LP relaxation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/101740001 (1).pdf`
- `downloads/101740001 (2).pdf`
- `downloads/101740001 (3).pdf`
- `downloads/101740001 (4).pdf`
- `downloads/101740001.pdf`
