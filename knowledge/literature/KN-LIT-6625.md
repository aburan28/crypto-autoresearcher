---
id: KN-LIT-6625
type: literature
title: "Sieving for shortest vectors in lattices using angular locality-sensitive hashing"
authors:
  - "Thijs Laarhoven"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
By replacing the brute-force list search in sieving algorithms with Charikar’s angular locality-sensitive hashing (LSH) method, we get both theoretical and practical speedups for solving the shortest vector problem (SVP) on lattices. Combining angular LSH with a variant of Nguyen and Vidick’s heuristic sieve algorithm, we obtain heuristic time and space complexities for solving SVP of 20.3366n+o(n) and 20.2075n+o(n) respectively, while combining the same hash family with Micciancio and Voulgaris’ GaussSieve algorithm leads to an algorithm with (conjectured) heuristic time and space complexities of 20.3366n+o(n) .

## Key claims (as reported)
- Experiments with the GaussSieve-variant show that in moderate dimensions the proposed HashSieve algorithm already outperforms the GaussSieve, and the practical increase in the space complexity is much smaller than the asymptotic bounds suggest, and can be further reduced with probing.
- Extrapolating to higher dimensions, we estimate that a fully optimized and parallelized implementation of the GaussSieve-based HashSieve algorithm might need a few core years to solve SVP in dimension 130 or even 140.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160123 (1).pdf`
- `downloads/92160123 (2).pdf`
- `downloads/92160123.pdf`
