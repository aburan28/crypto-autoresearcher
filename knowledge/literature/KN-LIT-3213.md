---
id: KN-LIT-3213
type: literature
title: "Cryptanalysis of 2R− schemes"
authors:
  - "Jean-Charles Faugère"
  - "Ludovic Perret"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mov-fr, pairing, point-decomposition, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we study the security of 2R− schemes [17, 18], which are the “minus variant” of two-round schemes. This variant consists in removing some of the n polynomials of the public key, and permits to thwart an attack described at Crypto’99 [25] against two-round schemes.

## Key claims (as reported)
- Usually, the “minus variant” leads to a real strengthening of the considered schemes.
- We show here that this is − actually not true for 2R− schemes.
- We indeed ̈ ̋ propose an efficient algorithm for decomposing 2R schemes.
- For instance, we can remove up to n2 equations and still be able to recover a decomposition in O(n12 ).

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/41170356 (1).pdf`
- `downloads/41170356 (2).pdf`
- `downloads/41170356 (3).pdf`
- `downloads/41170356.pdf`
