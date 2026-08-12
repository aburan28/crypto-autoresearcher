---
id: KN-LIT-5994
type: literature
title: "Pseudorandom Generators from Regular One-way Functions: New Constructions with Improved Parameters"
authors:
  - "Yu Yu"
  - "Xiangxue Li"
  - "Jian Weng"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, mov-fr, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We revisit the problem of basing pseudorandom generators on regular one-way functions, and present the following constructions: – For any known-regular one-way function (on n-bit inputs) that is known to be ε-hard to invert, we give a neat (and tighter) proof for the folklore construction of pseudorandom generator of seed length Θ(n) by making a single call to the underlying one-way function. – For any unknown-regular one-way function with known ε-hardness, we give a new construction with seed length Θ(n) and O(n/ log (1/ε)) calls. Here the number of calls is also optimal by matching the lower bounds of Holenstein and Sinha (FOCS 2012).

## Key claims (as reported)
- Both constructions require the knowledge about ε, but the dependency can be removed while keeping nearly the same parameters.
- In the latter case, we get a construction of pseudo-random generator from any unknown-regular one-way function using seed length Õ(n) and Õ(n/ log n) calls, where Õ omits a factor that can be made arbitrarily close to constant (e.g. log log log n or even less).
- This improves the randomized iterate approach by Haitner, Harnik and Reingold (CRYPTO 2006) which requires seed length O(n·logn) and O(n/ log n) calls.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/82700262 (1).pdf`
- `downloads/82700262 (2).pdf`
- `downloads/82700262 (3).pdf`
- `downloads/82700262.pdf`
