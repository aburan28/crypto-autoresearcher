---
id: KN-LIT-2101
type: literature
title: "A low-resource quantum factoring algorithm"
authors:
  - "Daniel J. Bernstein"
  - "Jean-François Biasse"
  - "Michele Mosca"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, factoring, pairing, pqc, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we present a factoring algorithm that, assuming standard heuristics, uses just (log N )2/3+o(1) qubits to factor an integerp N in time Lq+o(1) where L = exp((log N )1/3 (log log N )2/3 ) and q = 3 8/3 ≈ 1.387. For comparison, the lowest asymptotic time complexity for known pre-quantum factoring algorithms, assuming standard heuristics, is Lp+o(1) where p > 1.9.

## Key claims (as reported)
- The new time complexity is asymptotically worse than Shor’s algorithm, but the qubit requirements are asymptotically better, so it may be possible to physically implement it sooner.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/grovernfs-20170419.pdf`
