---
id: KN-LIT-1250
type: literature
title: "Improved Boomerang Attacks on 6-Round AES"
authors:
  - "Augustin Bariant"
  - "Orr Dunkelman"
  - "Nathan Keller"
  - "Gaëtan Leurent"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/977"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/977"
tags: [cryptanalysis, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The boomerang attack is a cryptanalytic technique which allows combining two short high-probability differentials into a distinguisher for a large number of rounds. Since its introduction by Wagner in 1999, it has been applied to many ciphers.

## Key claims (as reported)
- One of the best-studied targets is a 6-round variant of AES, on which the boomerang attack is outperformed only by the dedicated Square attack.
- Recently, two new variants of the boomerang attack were presented: retracing boomerang (Eurocrypt’20) and truncated boomerang (Eurocrypt’23).
- These variants seem incompatible: the former achieves lower memory complexity by throwing away most of the data in order to force dependencies, while the latter achieves lower time complexity by using large structures, which inevitably leads to a large memory complexity.
- In this paper we show that elements of the two techniques can be combined to get ‘the best of the two worlds’ – the practical memory complexity of the retracing attack and the lower time complexity of the truncated attack.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-977.pdf`
