---
id: KN-LIT-4265
type: literature
title: "How to Build Optimally Secure PRFs Using Block Ciphers"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In EUROCRYPT ’96, Aiello and Venkatesan proposed two candidates for 2n-bit to 2n-bit pseudorandom functions (PRFs), called Benes and modified Benes (or mBenes), based on n-bit to n-bit PRFs. While Benes is known to be secure up to 2n queries (Patarin, AFRICACRYPT ’08), the security of mBenes has only been proved up to 2n(1−) queries for all  > 0 by Patarin and Montreuil in ICISC ’05.

## Key claims (as reported)
- In this work, we show that the composition of a 2n-bit hash function with mBenes is a secure variable input length (VIL) PRF up to 2n−2 queries (given appropriate hash function bounds).
- We extend our analysis with block ciphers as the underlying primitive and obtain two optimally secure VIL PRFs using block ciphers.
- The first of these candidates requires 6 calls to the block cipher.
- The second candidate requires just 4 calls to the block cipher, but here the proof is based on Patarin’s mirror theory.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491327 (1).pdf`
- `downloads/12491327.pdf`
