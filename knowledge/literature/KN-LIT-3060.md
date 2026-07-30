---
id: KN-LIT-3060
type: literature
title: "Computing small discrete logarithms faster"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, fhe, hyperelliptic, pairing, pollard-rho, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Computations of small discrete logarithms are feasible even in “secure” groups, and are used as subroutines in several cryptographic protocols in the literature. For example, the Boneh–Goh–Nissim degree2-homomorphic public-key encryption system uses generic square-root discrete-logarithm methods for decryption.

## Key claims (as reported)
- This paper shows how to use a small group-specific table to accelerate these subroutines.
- The cost of setting up the table grows with the table size, but the acceleration also grows with the table size.
- This paper shows experimentally that computing a discrete logarithm in an interval of order ` takes only 1.93 · `1/3 multiplications on average using a table of size `1/3 precomputed with 1.21 · `2/3 multiplications, and computing a discrete logarithm in a group of order ` takes only 1.77 · `1/3 multiplications on average using a table of size `1/3 precomputed with 1.24 · `2/3 multiplications.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/cuberoot-20120919.pdf`
