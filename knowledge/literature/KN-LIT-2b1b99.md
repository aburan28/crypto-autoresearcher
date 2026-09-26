---
id: KN-LIT-2b1b99
type: literature
title: "Usable assembly language for GPUs: a success story"
authors:
  - "Daniel J. Bernstein"
  - "Hsieh-Chung Chen"
  - "Chen-Mou Cheng"
  - "Tanja Lange"
  - "Ruben Niederhagen"
  - "Peter Schwabe"
  - "Bo-Yin Yang"
year: 2012
venue: "IACR ePrint 2012/137"
identifiers:
  eprint: "iacr:2012/137"
  arxiv: null
  doi: null
  url: null
tags: [pollard-rho, gpu, assembly, qhasm, ecc2k-130, cuda, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

qhasm-cudasm, a higher-level GPU assembly language that gives register-allocation and scheduling control that nvcc/ptxas do not. It was used to build the 90,000-instruction ECC2K-130 kernel. The takeaway is that the compiler leaves a >2x constant factor on the table for rho kernels; RCKangaroo's hand-written SASS "turbo kernels" (2024-2026) repeat this lesson.

## Key claims (as reported)

- GTX 295: 25M iterations/s with nvcc+ptxas vs 63M iterations/s with qhasm-cudasm.

## Relevance to this program

How the 2010 GPU ECC2K-130 kernel reached 63M it/s (25M with nvcc): an assembly toolchain for GPUs. Relevant when comparing compiler-generated CUDA against hand-scheduled kernels.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
