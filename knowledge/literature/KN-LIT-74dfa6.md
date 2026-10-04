---
id: KN-LIT-74dfa6
type: literature
title: "gECC: A GPU-based high-throughput framework for Elliptic Curve Cryptography"
authors:
  - "Qian Xiong"
  - "Weiliang Ma"
  - "Xuanhua Shi"
  - "Yongluan Zhou"
  - "Hai Jin"
  - "Kaiyi Huang"
  - "Haozhou Wang"
  - "Zhengru Wang"
year: 2025
venue: "ACM Transactions on Architecture and Code Optimization (2025); arXiv:2501.03245"
identifiers:
  eprint: null
  arxiv: "2501.03245"
  doi: "10.1145/3736176"
  url: "https://github.com/CGCL-codes/gECC"
tags: [gpu, ecc, cuda, batch-inversion, arithmetic, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Batch EC operations on GPUs using Montgomery's trick (the same batched-affine-addition pattern as a rho/kangaroo step), with memory-layout and microarchitecture work. It identifies IMAD issue rate as the modular-multiplication bottleneck and replaces IMADs with IADD3 plus predicate-register carries. Evaluated on A100.

## Key claims (as reported)

- 5.56x (ECDSA) and 4.94x (ECDH) over the prior state-of-the-art GPU system; 1.56x in a blockchain application vs CPU state of the art.

## Relevance to this program

GPU EC framework (ACM TACO 2025): the current academic reference for high-throughput GPU EC arithmetic (prime field). Any GPU rho paper should compare its per-operation throughput against gECC.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-1394 (bulk stub or misattributed entry; see that file's `superseded_by`).
