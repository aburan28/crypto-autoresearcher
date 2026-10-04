---
id: KN-LIT-e72678
type: literature
title: "Speeding the Pollard and elliptic curve methods of factorization"
authors:
  - "Peter L. Montgomery"
year: 1987
venue: "Mathematics of Computation 48:243-264"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1090/S0025-5718-1987-0866113-7"
  url: null
tags: [pollard-rho, simultaneous-inversion, montgomery-trick, batch-inversion, arithmetic, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Source of Montgomery-form curves and of the simultaneous-inversion trick (replace k field inversions by 1 inversion plus about 3(k-1) multiplications). Every affine-coordinate rho/kangaroo implementation batches its point additions this way; recent GPU work (gECC, RCKangaroo "triple Montgomery trick") builds on it.

## Key claims (as reported)

- k inversions -> 1 inversion + ~3(k-1) multiplications (standard statement).

## Relevance to this program

Simultaneous inversion (Montgomery's trick): n inversions for one inversion plus ~3(n−1) multiplications — the batching every affine-coordinate GPU rho kernel uses, including this program's 4-warp product-tree inversion. A 'share one inversion across walks' proposal is known; the new part can only be the GPU scheduling.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
