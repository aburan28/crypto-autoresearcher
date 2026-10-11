---
id: KN-LIT-63a5c5
type: literature
title: "Breaking Elliptic Curve Cryptosystems Using Reconfigurable Hardware"
authors:
  - "Junfeng Fan"
  - "Daniel V. Bailey"
  - "Lejla Batina"
  - "Tim Güneysu"
  - "Christof Paar"
  - "Ingrid Verbauwhede"
year: 2010
venue: "FPL 2010, pp. 133-138"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1109/FPL.2010.34"
  url: null
tags: [pollard-rho, ecc2k-130, fpga, spartan-3, binary-field, hardware, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

FPGA implementation of the ECC2K-130 rho iteration, improving on the Spartan-3 design in "Breaking ECC2K-130".

## Key claims (as reported)

- 111 million iterations/s on a 5 W Xilinx XC3S5000 (Spartan-3), as cited by Bernstein et al. 2016/382.

## Relevance to this program

ECC2K-130 on Spartan-3 FPGAs (111M it/s per chip as later cited); the FPGA baseline for this program's AWS F2 VU47P engine (8.249G steps/s).

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-2791 (bulk stub or misattributed entry; see that file's `superseded_by`).
