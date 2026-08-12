---
id: KN-LIT-5758
type: literature
title: "Performance Analysis and Parallel Implementation of Dedicated Hash Functions"
authors:
  - "Junko Nakajima"
  - "Mitsuru Matsui"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, implementation, mov-fr, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper shows an extensive software performance analysis of dedicated hash functions, particularly concentrating on Pentium III, which is a current dominant processor. The targeted hash functions are MD5, RIPEMD-128 -160, SHA-1 -256 -512 and Whirlpool, which fully cover currently used and future promising hashing algorithms.

## Key claims (as reported)
- We try to optimize hashing speed not only by carefully arranging pipeline scheduling but also by processing two or even three message blocks in parallel using MMX registers for 32-bit oriented hash functions.
- Moreover we thoroughly utilize 64-bit MMX instructions for maximizing performance of 64-bit oriented hash functions, SHA-512 and Whirlpool.
- To our best knowledge, this paper gives the first detailed measured performance analysis of SHA-256, SHA-512 and Whirlpool.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/hash (1).pdf`
- `downloads/hash (2).pdf`
- `downloads/hash.pdf`
