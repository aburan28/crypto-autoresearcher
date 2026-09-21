---
id: KN-LIT-3473
type: literature
title: "DPA on n-bit sized Boolean and Arithmetic"
authors:
  - "its Application to IDEA"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Differential Power Analysis (DPA) has turned out to be an efficient method to attack the implementations of cryptographic algorithms and has been well studied for ciphers that incorporate a nonlinear substitution box as e.g. in DES. Other product ciphers and message authentication codes are based on the mixing of different algebraic groups and do not use look-up tables.

## Key claims (as reported)
- Among these are IDEA, the AES finalist RC6 and HMAC-constructions such as HMAC-SHA-1 and HMACRIPEMD-160.
- These algorithms restrict the use of the selection function to the Hamming weight and Hamming distance of intermediate data as the addresses used do not depend on cryptographic keys.
- Because of the linearity of the primitive operations secondary DPA signals arise.
- This article gives a deeper analysis of the characteristics of DPA results obtained on the basic group operations XOR, addition modulo 2n and modular multiplication using multi-bit selection functions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/31560205 (1).pdf`
- `downloads/31560205 (2).pdf`
- `downloads/31560205.pdf`
