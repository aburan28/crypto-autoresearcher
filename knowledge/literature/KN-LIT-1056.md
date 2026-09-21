---
id: KN-LIT-1056
type: literature
title: "Yet Another Algebraic Cryptanalysis of Small Scale Variants of AES"
authors:
  - "Marek Bielik"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/695"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/695"
tags: [cryptanalysis, finite-field, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This work presents new advances in algebraic cryptanalysis of small scale derivatives of AES. We model the cipher as a system of polynomial equations over GF(2), which involves only the variables of the initial key, and we subsequently attempt to solve this system using Gröbner bases.

## Key claims (as reported)
- We show, for example, that one of the attacks can recover the secret key for one round of AES-128 under one minute on a contemporary CPU.
- This attack requires only two known plaintexts and their corresponding ciphertexts.
- We also compare the performance of Gröbner bases to a SAT solver, and provide an insight into the propagation of diffusion within the cipher.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2022-695.pdf`
