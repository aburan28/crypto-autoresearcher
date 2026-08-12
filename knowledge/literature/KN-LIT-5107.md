---
id: KN-LIT-5107
type: literature
title: "New Cryptanalytic Results on IDEA Eli Biham1"
authors:
  - "Orr Dunkelman∗"
  - "Nathan Keller⋆⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mov-fr, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
IDEA is a 64-bit block cipher with 128-bit keys introduced by Lai and Massey in 1991. IDEA is one of the most widely used block ciphers, due to its inclusion in several cryptographic packages, such as PGP and SSH.

## Key claims (as reported)
- The cryptographic strength of IDEA relies on a combination of three incompatible group operations – XOR, addition and modular multiplication.
- Since its introduction in 1991, IDEA has withstood extensive cryptanalytic effort, but no attack was found on the full variant of the cipher.
- In this paper we present the first known non-trivial relation that involves all the three operations of IDEA.
- Using this relation and other techniques, we devise a linear attack on 5-round IDEA that uses 219 known plaintexts and has a time complexity of 2103 encryptions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/42840416 (1).pdf`
- `downloads/42840416 (2).pdf`
- `downloads/42840416 (3).pdf`
- `downloads/42840416.pdf`
