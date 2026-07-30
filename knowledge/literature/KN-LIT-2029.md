---
id: KN-LIT-2029
type: literature
title: "A DETERMINISTIC ALGORITHM FOR FINDING r-POWER DIVISORS"
authors:
  - "DAVID HARVEY"
  - "MARKUS HITTMEIR"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, factoring, lattice, number-theory, pairing, pollard-rho, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Building on work of Boneh, Durfee and Howgrave-Graham, we present a deterministic algorithm that provably finds all integers p such that pr | N in time O(N 1/4r+ε ) for any ε > 0. For example, the algorithm can be used to test squarefreeness of N in time O(N 1/8+ε ); previously, the best rigorous bound for this problem was O(N 1/6+ε ), achieved via the Pollard– Strassen method.

## Key claims (as reported)
- (Abstract too short to separate claims; see Contribution.)

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/ANTS-XV_harvey-hittmeir.pdf`
