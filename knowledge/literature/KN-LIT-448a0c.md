---
id: KN-LIT-448a0c
type: literature
title: "ECC2K-130 on Cell CPUs"
authors:
  - "Joppe W. Bos"
  - "Thorsten Kleinjung"
  - "Ruben Niederhagen"
  - "Peter Schwabe"
year: 2010
venue: "AFRICACRYPT 2010, pp. 225-242"
identifiers:
  eprint: "iacr:2010/077"
  arxiv: null
  doi: "10.1007/978-3-642-12678-9_14"
  url: null
tags: [pollard-rho, ecc2k-130, cell, ps3, bitslicing, normal-basis, binary-field, ecdlp]
confidence: reported
citation_verified: read
added: "2026-09-26"
superseded_by: null
---

## Contribution

Bitsliced vs non-bitsliced and normal- vs polynomial-basis binary-field arithmetic for the ECC2K-130 rho iteration on Cell SPUs; bitsliced normal basis wins. Notes that Koblitz structure lowers the iteration count by sqrt(4*2*131) (cofactor, negation, Frobenius) at the cost of a heavier iteration.

## Key claims (as reported)

- 749 cycles/iteration per SPU (vs ~620 extrapolated from the 453-cycle 112-bit prime-field code); ECC2K-130 in one year on fewer than 2700 PS3s.

## Relevance to this program

ECC2K-130 on Cell SPEs: bitsliced vs non-bitsliced, normal vs polynomial basis; <2700 PS3s for one year. Must be cited by any ECC2K-130 implementation paper (the cryptanalysis-repo manuscripts omit it).

## Not verified here

The full text was read during the 2026-09-26 ECDLP literature sweep. Numbers are quoted from it, not re-derived or reproduced.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
