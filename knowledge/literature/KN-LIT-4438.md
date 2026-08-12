---
id: KN-LIT-4438
type: literature
title: "Improved Side-Channel Analysis of Finite-Field Multiplication Sonia Belaı̈d1 , Jean-Sébastien"
authors:
  - "Jean-Gabriel Kammerer"
  - "Emmanuel Prouff"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, implementation, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A side-channel analysis of multiplication in GF(2128 ) has recently been published by Belaı̈d, Fouque and Gérard at Asiacrypt 2014, with an application to AES-GCM. Using the least significant bit of the Hamming weight of the multiplication result, the authors have shown how to recover the secret multiplier efficiently.

## Key claims (as reported)
- However such least significant bit is very sensitive to noise measurement; this implies that, without averaging, their attack can only work for high signal-to-noise ratios (SNR > 128).
- In this paper we describe a new side-channel attack against the multiplication in GF(2128 ) that uses the most significant bits of the Hamming weight.
- We show that much higher values of noise can be then tolerated.
- For instance with an SNR equal to 8, the key can be recovered using 220 consumption traces with time and memory complexities respectively equal to 251.68 and 236 .

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930380 (1).pdf`
- `downloads/92930380.pdf`
