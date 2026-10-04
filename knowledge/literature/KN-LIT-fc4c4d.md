---
id: KN-LIT-fc4c4d
type: literature
title: "Harder, better, faster, stronger: elliptic curve discrete logarithm computations on FPGAs"
authors:
  - "Erich Wenger"
  - "Paul Wolfger"
year: 2016
venue: "Journal of Cryptographic Engineering 6:287-297 (online 2015); ePrint 2015/143"
identifiers:
  eprint: "iacr:2015/143"
  arxiv: null
  doi: "10.1007/s13389-015-0108-z"
  url: null
tags: [pollard-rho, fpga, binary-field, record, sect113r1, ecdlp]
confidence: reported
citation_verified: read
added: "2026-09-26"
superseded_by: null
---

## Contribution

FPGA architecture for binary Weierstrass and Koblitz curves with a negation map and fruitless-cycle handling. Used to compute the first discrete logarithm on the standardized curve sect113r1. NOTE: the 117.35-bit record often attributed to this paper is by Bernstein et al. (ePrint 2016/382); this paper's record is sect113r1 (group order ~2^112).

## Key claims (as reported)

- sect113r1 solved in ~2.5 months on 10 Kintex-7 (KC705) boards; 900e6 iterations/s per FPGA (5 cores x 180 MHz, 1 iteration/cycle/core).

## Relevance to this program

sect113r1 solved on 10 Kintex-7 FPGAs (~900M it/s each) in ~2.5 months. NOT the 117.35-bit record (that is Bernstein et al. 2016/382, KN-LIT-097).

## Not verified here

The full text was read during the 2026-09-26 ECDLP literature sweep. Numbers are quoted from it, not re-derived or reproduced.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
