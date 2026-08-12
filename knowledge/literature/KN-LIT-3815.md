---
id: KN-LIT-3815
type: literature
title: "FAST SQUARE-FREE DECOMPOSITION OF INTEGERS USING CLASS GROUPS ERIK MULDER"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, elliptic-curve, endomorphism, factoring, finite-field, lattice, number-theory, pollard-rho, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Let n = a2 b, where b is square-free. In this paper we present an algorithm based on class groups of binary quadratic forms that finds the square-free decomposition of n, i.e. a and b, in heuristic expected time: e O(Lb [1/2, 1] ln(n) + Lb [1/2, 1/2] ln(n)2 ).

## Key claims (as reported)
- If a, b are both primes of roughly the same cryptographic size, then our method is currently the fastest known method to factor n.
- This has applications in cryptography, since some cryptosystems rely on the hardness of factoring integers of this form.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/Mulder (2).pdf`
- `downloads/Mulder.pdf`
