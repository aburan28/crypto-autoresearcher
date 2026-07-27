---
id: KN-LIT-2945
type: literature
title: "Collision of random walks and a refined analysis of attacks on the discrete logarithm problem"
authors:
  - "Shuji Kijima"
  - "Ravi Montenegro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, dlp, elliptic-curve, pairing, pollard-rho]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Some of the most efficient algorithms for finding the discrete logarithm involve pseudo-random implementations of Markov chains, with one or more “walks” proceeding until a collision occurs, i.e. some state is visited a second time. In this paper we develop a method for determining the expected time until the first collision.

## Key claims (as reported)
- We use our technique to examine three methods for solving discrete-logarithm problems: Pollard’s Kangaroo, Pollard’s Rho, and a few versions of Gaudry-Schost.
- For the Kangaroo method we prove new and fairly precise matching upper and lower bounds.
- For the Rho method we prove the first rigorous non-trivial lower bound, and under a mild assumption show matching upper and lower bounds.
- Our Gaudry-Schost results are heuristic, but improve on the prior limited understanding of this method.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90200136 (1).pdf`
- `downloads/90200136 (2).pdf`
- `downloads/90200136 (3).pdf`
- `downloads/90200136 (4).pdf`
- `downloads/90200136.pdf`
