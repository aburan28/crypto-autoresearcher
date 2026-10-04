---
id: KN-LIT-f34f74
type: literature
title: "Solving Small Exponential ECDLP in EC-based Additively Homomorphic Encryption and Applications"
authors:
  - "Fei Tang"
  - "Guowei Ling"
  - "Chaochao Cai"
  - "Jinyong Shan"
  - "Xuanqi Liu"
  - "Peng Tang"
  - "Weidong Qiu"
year: 2022
venue: "IACR ePrint 2022/1573"
identifiers:
  eprint: "iacr:2022/1573"
  arxiv: null
  doi: null
  url: null
tags: [pollard-rho, small-dlp, bsgs, homomorphic-encryption, precomputation, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

FastECDLP: precomputed BSGS tables tuned for recovering l-bit plaintexts m from m*G in EC-ElGamal-type additively homomorphic encryption. Related: Chatzigiannis-Chalkias-Nikolaenko, truncated BSGS lookup tables for secp curves (ePrint 2021/899, CBT 2021), 7x-14x storage reduction.

## Key claims (as reported)

- l = 40-bit decryption in 0.35 ms single-threaded (~30x faster than Paillier); experiments for l = 32..54.

## Relevance to this program

Fast small-exponent ECDLP for EC-ElGamal-type additively homomorphic encryption; precomputation-table engineering baseline.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-1037 (bulk stub or misattributed entry; see that file's `superseded_by`).
