---
id: KN-LIT-2794
type: literature
title: "Breaking pairing-based cryptosystems using ηT pairing over GF (397 ) Takuya Hayashi1"
authors:
  - "Naoyuki Shinohara"
  - "Tsuyoshi Takagi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, ecdlp, elliptic-curve, implementation, lattice, pairing, pollard-rho, protocol, quantum, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we discuss solving the DLP over GF (36·97 ) by using the function field sieve (FFS) for breaking paring-based cryptosystems using the ηT pairing over GF (397 ). The extension degree 97 has been intensively used in benchmarking tests for the implementation of the ηT pairing, and the order (923-bit) of GF (36·97 ) is substantially larger than the previous world record (676-bit) of solving the DLP by using the FFS.

## Key claims (as reported)
- We implemented the FFS for the medium prime case, and proposed several improvements of the FFS.
- Finally, we succeeded in solving the DLP over GF (36·97 ).
- The entire computational time requires about 148.2 days using 252 CPU cores.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/76580039 (1).pdf`
- `downloads/76580039 (2).pdf`
- `downloads/76580039 (3).pdf`
- `downloads/76580039.pdf`
