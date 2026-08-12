---
id: KN-LIT-6642
type: literature
title: "Simpira v2: A Family of Efficient Permutations Using the AES Round Function"
authors:
  - "Shay Gueron"
  - "Nicky Mouha"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, protocol, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces Simpira, a family of cryptographic permutations that supports inputs of 128 × b bits, where b is a positive integer. Its design goal is to achieve high throughput on virtually all modern 64-bit processors, that nowadays already have native instructions for AES.

## Key claims (as reported)
- To achieve this goal, Simpira uses only one building block: the AES round function.
- For b = 1, Simpira corresponds to 12-round AES with fixed round keys, whereas for b ≥ 2, Simpira is a Generalized Feistel Structure (GFS) with an F -function that consists of two rounds of AES.
- We claim that there are no structural distinguishers for Simpira with a complexity below 2128 , and analyze its security against a variety of attacks in this setting.
- The throughput of Simpira is close to the theoretical optimum, namely, the number of AES rounds in the construction.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10031150 (1).pdf`
- `downloads/10031150.pdf`
