---
id: KN-LIT-193
type: literature
title: "CONSTRUCTING ELLIPTIC CURVES IN ALMOST POLYNOMIAL TIME"
authors:
  - "Reinier Bröker"
  - "Peter Stevenhagen"
year: 2005
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "0511729"
  url: "https://arxiv.org/abs/0511729"
tags: [curve-arithmetic, dlp, elliptic-curve, factoring, finite-field, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present an algorithm that, on input of an integer N ≥ 1 together with its prime factorization, constructs a finite field F and an elliptic curve E over F for which E(F) has order N. Although it is unproved that this can be done for all N, a heuristic analysis shows that the algorithm has an expected run time that is polynomial in 2ω(N ) log N, where ω(N) is the number of distinct prime factors of N.

## Key claims (as reported)
- In the cryptographically relevant case where N is prime, an expected run time O((log N)4+ε ) can be achieved.
- We illustrate the efficiency of the algorithm by constructing elliptic curves with point groups of order N = 102004 and N = nextprime(102004 ) = 102004 + 4863.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/0511729v1.pdf`
