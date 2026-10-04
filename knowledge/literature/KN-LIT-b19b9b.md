---
id: KN-LIT-b19b9b
type: literature
title: "Time-Memory Analysis of Parallel Collision Search Algorithms"
authors:
  - "Monika Trimoska"
  - "Sorina Ionica"
  - "Gilles Dequen"
year: 2021
venue: "IACR TCHES 2021(2):254-274; ePrint 2017/581"
identifiers:
  eprint: "iacr:2017/581"
  arxiv: null
  doi: "10.46586/tches.v2021.i2.254-274"
  url: null
tags: [pollard-rho, distinguished-points, memory, collision-search, time-memory-tradeoff, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Argues theoretically that memory, not just iteration count, determines parallel-collision-search runtime. It replaces the usual DP hash table with a radix-tree-like structure that saves space and speeds look-up and insertion, and benchmarks linear parallel scaling for ECDLP and MITM applications.

## Key claims (as reported)

- Constant-factor runtime gain for many-collision search; linear parallel scaling (exact factors in paper).

## Relevance to this program

Time–memory analysis of parallel collision search (DP storage, memory-limited regimes). Directly relevant to the ECC2K-130 campaign's DP32 corpus (≈2^32.5 records) and restart-limit accounting.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
