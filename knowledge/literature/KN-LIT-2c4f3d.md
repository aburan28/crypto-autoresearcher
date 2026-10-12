---
id: KN-LIT-2c4f3d
type: literature
title: "Kangaroo: Pollard's kangaroo for SECPK1 (GPU ECDLP interval solver)"
authors:
  - "Jean-Luc Pons"
year: 2020
venue: "GitHub software (JeanLucPons/Kangaroo)"
identifiers:
  eprint: null
  arxiv: null
  doi: null
  url: "https://github.com/JeanLucPons/Kangaroo"
tags: [pollard-rho, kangaroo, gpu, secp256k1, software, interval-dlp, community, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Open-source CUDA kangaroo solver for secp256k1 interval ECDLP with distinguished points, a jump table of powers of two, and client/server DP collection. It solved Bitcoin "puzzle transaction" keys #110 and #115, whose public keys are exposed. No symmetry (negation) is used.

## Key claims (as reported)

- #110 (109-bit interval): 2.1 days on 256 Tesla V100, 2^55.55 group operations (DP25). #115 (114-bit): 13 days, 2^58.36 operations. 4x V100: 7828.45 MKeys/s (~1.96 G/s per V100). #130 estimated "several years on 256 V100".

## Relevance to this program

Open-source GPU kangaroo (JeanLucPons): the community reference implementation for interval ECDLP on GPUs (≈1.96G/s per V100 as reported in its README). Not peer-reviewed; cite as software.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
