---
id: KN-LIT-3812
type: literature
title: "Fast Reduction of Algebraic Lattices over Cyclotomic fields"
authors:
  - "Paul Kirchner"
  - "Thomas Espitau"
  - "Pierre-Alain Fouque"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, lattice, number-theory, pqc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe two very efficient polynomial-time algorithms for reducing module lattices defined over arbitrary cyclotomic fields that solve the γ-Hermite Module-SVP problem. They both exploit the structure of tower fields and the second one also uses the symplectic geometry existing in these fields.

## Key claims (as reported)
- We conjecture that a rank-2 module over a cyclotomic field of degree n with B-bit coefficients can be heuristically reduced within  e approximation factor 2O(n) in time e O n2 B .
- In the symplectic algorithm, if the (log-)condition number C of the input matrix is large enough,  e nlog2 3 C .
- In cryptography, matrices are this complexity shrinks to O well-conditioned and we can take C = B, but in the worst case, C can be as large as nB.
- This last result is particularly striking as for some matrices, we can go below the n2 B swaps lower bound given by the analysis of LLL based on the potential.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171223 (1).pdf`
- `downloads/12171223.pdf`
