---
id: KN-LIT-5679
type: literature
title: "Optimizing double-base elliptic-curve single-scalar multiplication"
authors:
  - "Daniel J. Bernstein"
  - "Peter Birkner"
  - "Tanja Lange"
  - "Christiane Peters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, hyperelliptic, jacobian, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper analyzes the best speeds that can be obtained for single-scalar multiplication with variable base point by combining a huge range of options: – many choices of coordinate systems and formulas for individual group operations, including new formulas for tripling on Edwards curves; – double-base chains with many different doubling/tripling ratios, including standard base-2 chains as an extreme case; – many precomputation strategies, going beyond Dimitrov, Imbert, Mishra (Asiacrypt 2005) and Doche and Imbert (Indocrypt 2006). The analysis takes account of speedups such as S − M tradeoffs and includes recent advances such as inverted Edwards coordinates.

## Key claims (as reported)
- The main conclusions are as follows.
- Optimized precomputations and triplings save time for single-scalar multiplication in Jacobian coordinates, Hessian curves, and tripling-oriented Doche/Icart/Kohel curves.
- However, even faster single-scalar multiplication is possible in Jacobi intersections, Edwards curves, extended Jacobi-quartic coordinates, and inverted Edwards coordinates, thanks to extremely fast doublings and additions; there is no evidence that double-base chains are worthwhile for the fastest curves.
- Inverted Edwards coordinates are the speed leader.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/doublebase-20071028.pdf`
