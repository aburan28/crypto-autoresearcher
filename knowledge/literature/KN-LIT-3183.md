---
id: KN-LIT-3183
type: literature
title: "Cost analysis of hash collisions: Will quantum computers make SHARCS obsolete?"
authors:
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, hash, number-theory, pollard-rho, pqc, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Current proposals for special-purpose factorization hardware will become obsolete if large quantum computers are built: the numberfield sieve scales much more poorly than Shor’s quantum algorithm for factorization. Will all special-purpose cryptanalytic hardware become obsolete in a post-quantum world?

## Key claims (as reported)
- A quantum algorithm by Brassard, Høyer, and Tapp has frequently been claimed to reduce the cost of b-bit hash collisions from 2b/2 to 2b/3 .
- This paper analyzes the Brassard–Høyer–Tapp algorithm and shows that it has fundamentally worse price-performance ratio than the classical van Oorschot–Wiener hash-collision circuits, even under optimistic assumptions regarding the speed of quantum computers.

## Relevance to this program
Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/collisioncost-20090823.pdf`
