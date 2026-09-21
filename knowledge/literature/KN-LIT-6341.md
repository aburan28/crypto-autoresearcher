---
id: KN-LIT-6341
type: literature
title: "Rounding and Chaining LLL: Finding Faster Small Roots of Univariate Polynomial Congruences"
authors:
  - "Jingguo Bi"
  - "Jean-Sébastien Coron"
  - "Jean-Charles Faugère"
  - "Phong Q"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, lattice, provable-security, quantum, rsa, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In a seminal work at EUROCRYPT ’96, Coppersmith showed how to find all small roots of a univariate polynomial congruence in polynomial time: this has found many applications in public-key cryptanalysis and in a few security proofs. However, the running time of the algorithm is a high-degree polynomial, which limits experiments: the bottleneck is an LLL reduction of a high-dimensional matrix with extra-large coefficients.

## Key claims (as reported)
- We present in this paper the first significant speedups over Coppersmith’s algorithm.
- The first speedup is based on a special property of the matrices used by Coppersmith’s algorithm, which allows us to provably speed up the LLL reduction by rounding, and which can also be used to improve the complexity analysis of Coppersmith’s original algorithm.
- The exact speedup depends on the LLL algorithm used: for instance, the speedup is asymptotically quadratic in the bit-size of the small-root bound if one uses the Nguyen-Stehlé L2 algorithm.
- The second speedup is heuristic and applies whenever one wants to enlarge the root size of Coppersmith’s algorithm by exhaustive search.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/83830188 (1).pdf`
- `downloads/83830188 (2).pdf`
- `downloads/83830188 (3).pdf`
- `downloads/83830188 (4).pdf`
- `downloads/83830188 (5).pdf`
- `downloads/83830188.pdf`
