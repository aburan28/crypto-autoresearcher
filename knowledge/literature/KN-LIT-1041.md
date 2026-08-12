---
id: KN-LIT-1041
type: literature
title: "Structural Evaluation of AES-like Ciphers against Mixture Differential Cryptanalysis"
authors:
  - "Xiaofeng Xie"
  - "Tian Tian"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/1199"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/1199"
tags: [cryptanalysis, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In ASIACRYPT 2017, Rønjom et al. analyzed AES with the yoyo attack. Similar to their 4-round AES distinguisher, Grassi proposed the 4-round mixture differential cryptanalysis as well as a key recovery attack on 5-round AES, which was shown to be better than the classical square attack in computation complexity.

## Key claims (as reported)
- After that, Bardeh et al. combined the exchange attack with the 4-round mixture differential distinguisher of AES, leading to the first secret-key chosen plaintext distinguisher for 6-round AES.
- Unlike the attack on 5-round AES, the result of 6-round keyrecovery attack on AES has extremely large complexity, which implies the weakness of mixture difference to a certain extent.
- Our work aims at evaluating the security of AES-like ciphers against mixture differential cryptanalysis.
- We propose a new structure called a boomerang structure and illustrate that a differential distinguisher of a boomerang structure just corresponds to a mixture differential distinguisher for AES-like ciphers.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2022-1199.pdf`
