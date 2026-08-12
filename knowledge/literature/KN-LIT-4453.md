---
id: KN-LIT-4453
type: literature
title: "Improving Key-Recovery in Linear Attacks: Application to 28-round PRESENT"
authors:
  - "Antonio Flórez-Gutiérrez"
  - "Marı́a Naya-Plasencia"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Linear cryptanalysis is one of the most important tools in use for the security evaluation of symmetric primitives. Many improvements and refinements have been published since its introduction, and many applications on different ciphers have been found.

## Key claims (as reported)
- Among these upgrades, Collard et al. proposed in 2007 an acceleration of the key-recovery part of Algorithm 2 for last-round attacks based on the FFT.
- In this paper we present a generalized, matrix-based version of the previous algorithm which easily allows us to take into consideration an arbitrary number of key-recovery rounds.
- We also provide efficient variants that exploit the key-schedule relations and that can be combined with multiple linear attacks.
- Using our algorithms we provide some new cryptanalysis on PRESENT, including, to the best of our knowledge, the first attack on 28 rounds.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105293 (1).pdf`
- `downloads/12105293.pdf`
