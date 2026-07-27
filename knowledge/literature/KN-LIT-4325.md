---
id: KN-LIT-4325
type: literature
title: "ICEPOLE: High-speed"
authors:
  - "Josef Pieprzyk"
  - "Marcin Rogawski"
  - "Marian Srebrny"
  - "Marcin Wójcik"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, pairing, protocol, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces our dedicated authenticated encryption scheme ICEPOLE. ICEPOLE is a high-speed hardware-oriented scheme, suitable for high-throughput network nodes or generally any environment where specialized hardware (such as FPGAs or ASICs) can be used to provide high data processing rates.

## Key claims (as reported)
- ICEPOLE-128 (the primary ICEPOLE variant) is very fast.
- On the modern FPGA device Virtex 6, a basic iterative architecture of ICEPOLE reaches 41 Gbits/s, which is over 10 times faster than the equivalent implementation of AES-128-GCM.
- The throughput-to-area ratio is also substantially better when compared to AES-128-GCM.
- We have carefully examined the security of the algorithm through a range of cryptanalytic techniques and our findings indicate that ICEPOLE offers high security level.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310178 (1).pdf`
- `downloads/87310178 (2).pdf`
- `downloads/87310178 (3).pdf`
- `downloads/87310178.pdf`
