---
id: KN-LIT-838
type: literature
title: "A Semi-Permanent Stuck-At Fault Analysis on AES"
authors:
  - "Rijndael SBox"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/1124"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/1124"
tags: [cryptanalysis, implementation, provable-security, rsa, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Fault attacks have gained particular attention in recent years as they present a severe threat to security in rapidly rising Internet-of-Things (IoT) devices. IoT devices are generally security-critical and resource-constrained.

## Key claims (as reported)
- Therefore, any security protocol deployed in these devices has to satisfy several constraints such as small area footprint, low power, and memory consumption.
- Combinational circuit implementation of S-box is preferable over look-up table (LUT) in terms of memory consumption as the memory operations are usually the costliest part of lightweight cipher implementations.
- In this work, we analyze the S-box of AES against a novel fault analysis technique, Semi-Permanent Stuck-At (SPSA) fault analysis.
- We pinpoint hotspots in an optimized implementation of AES S-box that weaken the cryptographic properties of the S-box, leading to key recovery attacks.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-1124.pdf`
