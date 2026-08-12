---
id: KN-LIT-2080
type: literature
title: "A HEURISTIC SUBEXPONENTIAL ALGORITHM TO FIND PATHS IN MARKOFF GRAPHS OVER FINITE FIELDS JOSEPH H. SILVERMAN"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, ecdlp, finite-field, hash, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Charles, Goren, and Lauter [J. Cryptology 22(1), 2009] explained how one can construct hash functions using expander graphs in which it is hard to find paths between specified vertices.

## Key claims (as reported)
- The set of solutions to the classical Markoff equation X 2 + Y 2 + Z 2 = 3XY Z in a finite field Fq has a natural structure as a tri-partite graph using three non-commuting polynomial automorphisms to connect the points.
- These graphs conjecturally form an expander family, and Fuchs, Lauter, Litman, and Tran [Mathematical Cryptology 1(1), 2022] suggested using this family of Markoff graphs in the CGL construction.
- In this note we show that in both a theoretical and a practical sense, assuming two randomness hypotheses, one can compute paths in a Markoff graph over Fq by factoring q − 1 and solving three discrete logarithm problems in F∗q .
- In particular, the path problem can be solved in subexponential time.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/Silverman (2).pdf`
- `downloads/Silverman.pdf`
