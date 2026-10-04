---
id: KN-LIT-c75942
type: literature
title: "ECC2K-130 on NVIDIA GPUs"
authors:
  - "Daniel J. Bernstein"
  - "Hsieh-Chung Chen"
  - "Chen-Mou Cheng"
  - "Tanja Lange"
  - "Ruben Niederhagen"
  - "Peter Schwabe"
  - "Bo-Yin Yang"
year: 2010
venue: "INDOCRYPT 2010, LNCS 6498, pp. 328-346 (updated version ePrint 2012/002)"
identifiers:
  eprint: "iacr:2012/002"
  arxiv: null
  doi: "10.1007/978-3-642-17401-8_23"
  url: null
tags: [pollard-rho, ecc2k-130, gpu, gtx-295, bitslicing, binary-field, cuda, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Maps bitsliced F_2^131 arithmetic for the ECC2K-130 iteration onto the GT200 GPU, which is poorly suited to binary-field work, by careful register/shared-memory scheduling. It remains the canonical "rho on GPU" design paper; the techniques carry over to server-side batch ECC.

## Key claims (as reported)

- >63 million iterations/s on one US$500 GTX 295 (incl. 320 million F_2^131 multiplications/s); whole attack ~2^77 bit operations in ~2^61 iterations.

## Relevance to this program

The prior GPU state of the art for ECC2K-130: >63M iterations/s on a GTX 295 (320M F_2^131 multiplications/s), ~2^77 bit operations in 2^61 iterations. The Blackwell/clmad work (cryptanalysis docs/papers/ecc2k130-blackwell) is measured against this; ~1,180 SM-cycles/iteration then vs ~20 now (derived in the 2026-09-26 review).

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-3503 (bulk stub or misattributed entry; see that file's `superseded_by`).
