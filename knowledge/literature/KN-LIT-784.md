---
id: KN-LIT-784
type: literature
title: "MixColumns Coefficient Property and Security of the AES with A Secret S-Box"
authors:
  - "Xin An"
  - "Kai Hu"
  - "Meiqin Wang ( )"
year: 2020
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2020/546"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2020/546"
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The MixColumns operation is an important component providing diffusion for the AES. The branch number of it ensures that any continuous four rounds of the AES have at least 25 active S-Boxes, which makes the AES secure against the differential and linear cryptanalysis.

## Key claims (as reported)
- However, the choices of the coefficients of the MixColumns matrix may undermine the AES security against some novel-type attacks.
- A particular property of the AES MixColumns matrix coefficient has been noticed in recent papers that each row or column of the matrix has elements that sum to zero.
- Several attacks have been developed taking advantage of the coefficient property.
- In this paper we investigate further the influence of the specific coefficient property on the AES security.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2020-546.pdf`
