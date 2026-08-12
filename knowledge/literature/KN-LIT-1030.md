---
id: KN-LIT-1030
type: literature
title: "Quantum Impossible Differential Attacks:"
authors:
  - "Applications to AES"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/754"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/754"
tags: [cryptanalysis, mov-fr, pqc, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we propose the first efficient quantum version of key-recovery attacks on block ciphers based on impossible differentials, which was left as an open problem in previous work. These attacks work in two phases.

## Key claims (as reported)
- First, a large number of differential pairs are collected, by solving a limited birthday problem with the attacked block cipher considered as a black box.
- Second, these pairs are filtered with respect to partial key candidates.
- We show how to translate the pair filtering step into a quantum procedure, and provide a complete analysis of its complexity.
- If the path of the attack can be properly reoptimized, this procedure can reach a significant speedup with respect to classical attacks.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2022-754.pdf`
