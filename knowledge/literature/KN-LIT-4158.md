---
id: KN-LIT-4158
type: literature
title: "Hardness of SIS and LWE with Small Parameters"
authors:
  - "Daniele Micciancio"
  - "Chris Peikert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Short Integer Solution (SIS) and Learning With Errors (LWE) problems are the foundations for countless applications in latticebased cryptography, and are provably as hard as approximate lattice problems in the worst case. An important question from both a practical and theoretical perspective is how small their parameters can be made, while preserving their hardness.

## Key claims (as reported)
- We prove two main results on SIS and LWE with small parameters.
- For SIS, we show that the problem retains its hardness for moduli q ≥ β · nδ for any constant δ > 0, where β is the bound on the Euclidean norm √ of the solution.
- This improves upon prior results which required q > β· n log n, and is close to optimal since the problem is trivially easy for q ≤ β.
- For LWE, we show that it remains hard even when the errors are small (e.g., uniformly random from {0, 1}), provided that the number of samples is small enough (e.g., linear in the dimension n of the LWE secret).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80420136 (1).pdf`
- `downloads/80420136 (2).pdf`
- `downloads/80420136 (3).pdf`
- `downloads/80420136.pdf`
