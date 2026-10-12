---
id: KN-LIT-c8e485
type: literature
title: "On the Correct Use of the Negation Map in the Pollard rho Method"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
  - "Peter Schwabe"
year: 2011
venue: "PKC 2011, LNCS 6571, pp. 128-146 (expanded version ePrint 2011/003)"
identifiers:
  eprint: "iacr:2011/003"
  arxiv: null
  doi: "10.1007/978-3-642-19379-8_8"
  url: null
tags: [pollard-rho, negation-map, fruitless-cycles, simd, prime-field, ps3, ecdlp]
confidence: reported
citation_verified: read
added: "2026-09-26"
superseded_by: null
---

## Contribution

A branch-free negating walk that detects and escapes fruitless cycles of length 2, 4, 6, ... by occasional sparse checks, together with faster modular arithmetic. It essentially recovers the full sqrt(2) on SIMD hardware. Reference design for "negation map on GPU"; the same fruitless-cycle issue reappears in symmetric kangaroo methods (RetiredCoder SOTA, Galbraith-Ruprai).

## Key claims (as reported)

- secp112r1 ECDLP about twice as fast as the ~65 PS3-year estimate of Bos et al.; 362 cycles/iteration per Cell SPU vs a 306.08-cycle lower bound (and 453 cycles in the earlier record code). Fruitless 2-cycles appear with probability ~1/(2r) for an r-adding walk; checking every w ~ 2*sqrt(r) iterations is optimal, so negation costs a factor 1 + Theta(1/sqrt(r)), versus Theta(1/r) from walk non-randomness.

## Relevance to this program

Branch-free handling of fruitless cycles achieving close to the full √2 negation gain (362 cycles/iteration on Cell for secp112r1, lower bound 306). The fruitless-cycle reference: cycle rules in the ECC2K-130 table walk and EXP-RHO-60da4f must be compared with it.

## Not verified here

The full text was read during the 2026-09-26 ECDLP literature sweep. Numbers are quoted from it, not re-derived or reproduced.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-324 (bulk stub or misattributed entry; see that file's `superseded_by`).
