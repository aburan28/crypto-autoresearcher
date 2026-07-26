---
id: KN-LIT-5759
type: literature
title: "Performance Analysis of the SHA-3 Candidates on Exotic Multi-Core Architectures"
authors:
  - "Joppe W. Bos"
  - "Deian Stefan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, pairing, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The NIST hash function competition to design a new cryptographic hash standard ‘SHA-3’ is currently one of the hot topics in cryptologic research, its outcome heavily depends on the public evaluation of the remaining 14 candidates. There have been several cryptanalytic efforts to evaluate the security of these hash functions.

## Key claims (as reported)
- Concurrently, invaluable benchmarking efforts have been made to measure the performance of the candidates on multiple architectures.
- In this paper we contribute to the latter; we evaluate the performance of all second-round SHA-3 candidates on two exotic platforms: the Cell Broadband Engine (Cell) and the NVIDIA Graphics Processing Units (GPUs).
- Firstly, we give performance estimates for each candidate based on the number of arithmetic instructions, which can be used as a starting point for evaluating the performance of the SHA-3 candidates on various platforms.
- Secondly, we use these generic estimates and Cell-/GPU-specific optimization techniques to give more precise figures for our target platforms, and finally, we present implementation results of all 10 non-AES based SHA-3 candidates.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62250268 (1).pdf`
- `downloads/62250268 (2).pdf`
- `downloads/62250268 (3).pdf`
- `downloads/62250268.pdf`
