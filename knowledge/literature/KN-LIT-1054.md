---
id: KN-LIT-1054
type: literature
title: "Truncated Boomerang Attacks and Application to AES-based Ciphers"
authors:
  - "Augustin Bariant"
  - "Gaëtan Leurent"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/701"
  doi: "10.1007/978-3-031-30634-1_1"
  arxiv: null
  url: "https://eprint.iacr.org/2022/701"
tags: [cryptanalysis, glv-gls, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The boomerang attack is a cryptanalysis technique that combines two short differentials instead of using a single long differential. It has been applied to many primitives, and results in the best known attacks against several AES-based ciphers (Kiasu-BC, Deoxys-BC).

## Key claims (as reported)
- In this paper, we introduce a general framework for boomerang attacks with truncated differentials.
- We show that the use of truncated differentials provides a significant improvement over the best boomerang attacks in the literature.
- In particular, we take into account structures on the plaintext and ciphertext sides, and include an analysis of the key recovery step.
- On 6-round AES, we obtain a competitive structural distinguisher with complexity 287 and a key recovery attack with complexity 261 .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004329 (1).pdf`
- `downloads/14004329.pdf`
- `downloads/2022-701.pdf`
