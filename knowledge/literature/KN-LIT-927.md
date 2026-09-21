---
id: KN-LIT-927
type: literature
title: "Side Channel Analysis against the ANSSI’s protected AES implementation on ARM"
authors:
  - "Loïc Masure"
  - "Rémi Strullu"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/592"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/592"
tags: [implementation, mpc, quantum, rsa, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In 2019, the ANSSI released a protected software implementation of AES running on an STM32 platform with ARM Cortex-M architecture, publicly available on Github. The release of the code was shortly followed by a first paper written by Bronchain et al. at Ches 2020, analyzing the security of the implementation and proposing some attacks.

## Key claims (as reported)
- In order to propose fair comparisons for future attacks on this target device, this paper aims at presenting a new publicly available dataset, called ASCADv2 based on this implementation.
- Along with the dataset, we also provide a benchmark of deep learning based side-channel attacks, thereby extending the works of Bronchain et al.
- Our attacks revisit and leverage the multi-task learning approach, introduced by Maghrebi in 2020, in order to efficiently target several intermediate computations at the same time.
- We hope that this work will draw the community’s interest towards the evaluation of highly protected software AES, whereas some of the current public SCA datasets are nowadays reputed to be less and less challenging.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-592.pdf`
