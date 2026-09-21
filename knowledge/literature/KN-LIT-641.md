---
id: KN-LIT-641
type: literature
title: "Simulations of Optical Emissions for Attacking"
authors:
  - "Masked AES"
year: 2018
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2018/291"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2018/291"
tags: [cryptanalysis, implementation, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we present a novel attack based on photonic emission analysis targeting software implementations of AES. We focus on the particular case in which the attacker can collect the photonic emission of a limited number of sense amplifiers (e.g. only one) of the SRAM storing the S-Box.

## Key claims (as reported)
- The attack consists in doing hypothesis on the secret key based on the knowledge of the partial output of the SubBytes operation.
- We also consider the possibility to attack a masked implementation of AES using the photonic emission analysis.
- In the case of masking, the attacker needs 2 leakages of the same encryption to overcome the randomization of the masks.
- For our analysis, we assume the same physical setup described in other previous works.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2018-291.pdf`
