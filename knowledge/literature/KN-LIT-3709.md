---
id: KN-LIT-3709
type: literature
title: "Essential Algebraic Structure Within the AES"
authors:
  - "Sean Murphy"
  - "Matthew J.B. Robshaw"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, cryptanalysis, mov-fr, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
One difficulty in the cryptanalysis of the Advanced Encryption Standard AES is the tension between operations in the two fields GF (28 ) and GF (2). This paper outlines a new approach that avoids this conflict.

## Key claims (as reported)
- We define a new block cipher, the BES, that uses only simple algebraic operations in GF (28 ).
- Yet the AES can be regarded as being identical to the BES with a restricted message space and key space, thus enabling the AES to be realised solely using simple algebraic operations in one field GF (28 ).
- This permits the exploration of the AES within a broad and rich setting.
- One consequence is that AES encryption can be described by an extremely sparse overdetermined multivariate quadratic system over GF (28 ), whose solution would recover an AES key.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/24420001 (1).pdf`
- `downloads/24420001 (2).pdf`
- `downloads/24420001.pdf`
