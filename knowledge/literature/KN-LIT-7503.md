---
id: KN-LIT-7503
type: literature
title: "What output size resists collisions in a xor of independent expansions?"
authors:
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, pollard-rho, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Bellare and Micciancio proposed compressing (m1 , m2 , . . .) to f1 (m1 ) ⊕ f2 (m2 ) ⊕ · · · . Collisions are easy to find for long messages but are much more difficult to find for short messages.

## Key claims (as reported)
- Exactly how secure is the 4-xor compression function (m1 , m2 , m3 , m4 ) 7→ f1 (m1 ) ⊕ f2 (m2 ) ⊕ f3 (m3 ) ⊕ f4 (m4 ), with an output size of 4b bits?
- This paper analyzes, under constraints on machine cost and computation time, the chance of finding 4b-bit collisions using an improved version of Wagner’s generalized-birthday algorithm.
- In particular, as the machine cost grows past 22b/3 , the price-performance ratio of this paper’s attack drops below 22b , eventually reaching a limit of 24b/3 .
- This paper also proposes the Rumba20 compression function, reusing large components of the Salsa20 stream cipher as a specific choice of functions f1 , f2 , f3 , f4 .

## Relevance to this program
Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/expandxor-20070503.pdf`
