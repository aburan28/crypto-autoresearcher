---
id: KN-LIT-7291
type: literature
title: "TWO GRUMPY GIANTS AND A BABY"
authors:
  - "DANIEL J. BERNSTEIN"
  - "TANJA LANGE"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, elliptic-curve, index-calculus, pollard-rho, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Pollard’s rho algorithm, along with parallelized, vectorized, and negating variants, is the standard method to compute discrete logarithms in generic prime-order groups. This paper presents two reasons that Pollard’s rho algorithm is farther from optimality than generally believed.

## Key claims (as reported)
- First, “higherdegree local anti-collisions” make the rho walk less random than the predictions made by the conventional Brent–Pollard heuristic.
- Second, even a truly random walk is suboptimal, because it suffers from “global anti-collisions” that √ can at least partially be avoided.
- For example, after (1.5 + o(1)) ` additions in a group of order ` (without fast negation), the baby-step-giant-step method has probability 0.5625 + o(1) of finding a uniform random discrete logarithm; a truly random walk would have probability 0.6753 . . . + o(1); and this paper’s new two-grumpy-giants-and-a-baby method has probability 0.71875 + o(1).

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/grumpy-20120709.pdf`
