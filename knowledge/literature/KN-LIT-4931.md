---
id: KN-LIT-4931
type: literature
title: "Minimalism of Software Implementation - Extensive Performance Analysis of Symmetric Primitives on the RL78 Microcontroller Mitsuru Matsui and Yumiko Murakami"
authors:
  - "Information Technology R&D Center"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, implementation, pairing, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper studies state-of-the-art software implementation of lightweight symmetric primitives from embedded system programmer’s standpoint. In embedded environments, due to many possible variations of ROM/RAM-size combinations, it is not always easy to obtain an entire performance picture of a given primitive and to create a fair benchmark from top speed records.

## Key claims (as reported)
- In this study we classify these size combinations into several categories and optimize operation speed in each category.
- We implemented on Renesas’ RL78 microcontroller - a typical CISC embedded processor, four block ciphers and seven hash functions with various combinations of ROM and RAM sizes to make performance characteristics of these primitives clearer.
- We also discuss how to create an interface and measure size and speed of a given primitive from a practical point of view.
- As a result, our AES encryption codes run at as fast as 3,855 cycles/block in the ROM-1KB RAM-64B category, and 6,622 cycles/block in the ROM-512B RAM-128B category.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84240365 (1).pdf`
- `downloads/84240365 (2).pdf`
- `downloads/84240365 (3).pdf`
- `downloads/84240365.pdf`
