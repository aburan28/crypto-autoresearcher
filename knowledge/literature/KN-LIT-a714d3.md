---
id: KN-LIT-a714d3
type: literature
title: "Pollard Rho on the PlayStation 3"
authors:
  - "Joppe W. Bos"
  - "Marcelo E. Kaihara"
  - "Peter L. Montgomery"
year: 2009
venue: "SHARCS 2009 (workshop record)"
identifiers:
  eprint: null
  arxiv: null
  doi: null
  url: "https://www.joppebos.com/files/rho_ps3.pdf"
tags: [pollard-rho, ps3, cell, prime-field, secp112r1, record, simd, ecdlp]
confidence: reported
citation_verified: read
added: "2026-09-26"
superseded_by: null
---

## Contribution

Cell/SPE implementation of parallel rho over a 112-bit prime field, using arithmetic modulo 2^128-3 with sloppy reduction. It set the prime-field ECDLP record by solving an instance on the standardized secp112r1 domain parameters.

## Key claims (as reported)

- secp112r1 ECDLP solved: 62.6 PS3-years on >200 PS3s, 13 Jan - 8 Jul 2009 (3.5 months if run continuously with the final code); ~453 cycles/iteration per SPE (estimate). 16-adding walk, 400 concurrent walks per SPE with Montgomery simultaneous inversion, no negation map (fruitless-cycle branches cost too much on the SPE). 33 PS3s (price of one COPACOBANA) = 1.4e9 it/s.

## Relevance to this program

Workshop version of the 112-bit prime-field ECDLP record on PS3s (453 cycles/iteration per SPU). With KN-LIT-095, the prime-field rho record baseline.

## Not verified here

The full text was read during the 2026-09-26 ECDLP literature sweep. Numbers are quoted from it, not re-derived or reproduced.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
