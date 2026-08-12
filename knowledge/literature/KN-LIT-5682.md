---
id: KN-LIT-5682
type: literature
title: "Optimizing S-box Implementations for Several Criteria using SAT Solvers"
authors:
  - "Ko Stoffelen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, implementation, mov-fr, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We explore the feasibility of applying SAT solvers to optimizing implementations of small functions such as S-boxes for multiple optimization criteria, e.g., the number of nonlinear gates and the number of gates. We provide optimized implementations for the S-boxes used in Ascon, ICEPOLE, Joltik/Piccolo, Keccak/Ketje/Keyak, LAC, Minalpher, PRIMATEs, Prøst, and RECTANGLE, most of which are candidates in the secound round of the CAESAR competition.

## Key claims (as reported)
- We then suggest a new method to optimize for circuit depth and we make tooling publicly available to find efficient implementations for several criteria.
- Furthermore, we illustrate with the 5-bit S-box of PRIMATEs how multiple optimization criteria can be combined.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/97830136 (1).pdf`
- `downloads/97830136.pdf`
