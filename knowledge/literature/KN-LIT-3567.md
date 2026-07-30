---
id: KN-LIT-3567
type: literature
title: "Efficient Hashing using the AES Instruction Set"
authors:
  - "Joppe W. Bos"
  - "Onur Özen"
  - "Martijn Stam"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we provide a software benchmark for a large range of 256-bit blockcipher-based hash functions. We instantiate the underlying blockcipher with AES, which allows us to exploit the recent AES instruction set (AESNI).

## Key claims (as reported)
- Since AES itself only outputs 128 bits, we consider double-block-length constructions, as well as (single-block-length) constructions based on R IJNDAEL 256.
- Although we primarily target architectures supporting AES-NI, our framework has much broader applications by estimating the performance of these hash functions on any (micro-)architecture given AES-benchmark results.
- As far as we are aware, this is the first comprehensive performance comparison of multiblock-length hash functions in software.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/69170507 (1).pdf`
- `downloads/69170507 (2).pdf`
- `downloads/69170507 (3).pdf`
- `downloads/69170507.pdf`
