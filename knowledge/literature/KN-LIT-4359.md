---
id: KN-LIT-4359
type: literature
title: "Implementing the Elliptic"
authors:
  - "Hoang Le"
  - "Mohammed Khaleeluddin"
  - "Ramakrishna Bachimanchi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, factoring, implementation, number-theory, pollard-rho, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A novel portable hardware architecture for the Elliptic Curve Method of factoring, designed and optimized for application in the relation collection step of the Number Field Sieve, is described and analyzed. A comparison with an earlier proof-of-concept design by Pelzl, Šimka, et al. has been performed, and a substantial improvement has been demonstrated in terms of both the execution time and the area-time product.

## Key claims (as reported)
- The ECM architecture has been ported across three different families of FPGA devices in order to select the family with the best performance to cost ratio.
- A timing comparison with a highly optimized software implementation, GMP-ECM, has been performed.
- Our results indicate that low-cost families of FPGAs, such as Xilinx Spartan 3, offer at least an order of magnitude improvement over the same generation of microprocessors in terms of the performance to cost ratio.

## Relevance to this program
Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10 (1).pdf`
- `downloads/10 (2).pdf`
- `downloads/10 (3).pdf`
- `downloads/10.pdf`
