---
id: KN-LIT-a4b3d8
type: literature
title: "RCKangaroo (SOTA/SOTA+ kangaroo with symmetry) and Kang-1/Kang-2 method write-ups"
authors:
  - "RetiredCoder (pseudonymous; GitHub RetiredC)"
year: 2024
venue: "GitHub software and README write-ups, 2024-2026; discussion bitcointalk topic 5517607"
identifiers:
  eprint: null
  arxiv: null
  doi: null
  url: "https://github.com/RetiredC/RCKangaroo"
tags: [pollard-rho, kangaroo, gpu, secp256k1, software, interval-dlp, community, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Community (not peer-reviewed) kangaroo variants that use the negation symmetry with 3 or 2 kangaroo herds (SOTA). SOTA+ also uses the cheap second point P-J when computing P+J, the same observation as Galbraith-Wang-Zhang 2015. Kang-2 describes loop detection and escape through a second table of large jumps so that DP chains stay intact. RCKangaroo v4 uses hand-written SASS "turbo" kernels and a "triple Montgomery trick" that hides the inversion.

## Key claims (as reported)

- Claimed K (ops/sqrt(range)): classic 2.1, 3-way 1.6, mirror 1.3, SOTA 1.15, SOTA+ ~1.02 if the cheap point is free (~0.99 paying 1M+1S, ~1.05 paying (1M+1S)/4). Loop handling keeps K ~1.16 incl. DP overhead in tests to 60-bit ranges. Throughput: ~14.5 G ops/s on RTX 4090 and 19.3 G ops/s on RTX 5090 (turbo kernels); inversion ~3% of GPU resources; ranges up to 170 bits.

## Relevance to this program

Community GPU kangaroo with symmetry ('SOTA', claimed K≈1.15; 'SOTA+' ≈1.02 using the Galbraith–Wang–Zhang X−Y trick) and hand-tuned kernels (claimed 14.5G/s RTX 4090, 19.3G/s RTX 5090). Not peer-reviewed; the de facto state of the art in GPU EC collision-search engineering that an academic GPU rho paper should position against.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
