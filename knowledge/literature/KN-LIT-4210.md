---
id: KN-LIT-4210
type: literature
title: "Higher Order Masking of Look-up Tables Jean-Sébastien Coron"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, mov-fr, mpc, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a new algorithm for masking look-up tables of block-ciphers at any order, as a countermeasure against side-channel attacks. Our technique is a generalization of the classical randomized table countermeasure against first-order attacks.

## Key claims (as reported)
- We prove the security of our new algorithm against t-th order attacks in the usual Ishai-SahaiWagner model from Crypto 2003; we also improve the bound on the number of shares from n ≥ 4t + 1 to n ≥ 2t + 1 for an adversary who can adaptively move its probes between successive executions.
- Our algorithm has the same time complexity O(n2 ) as the Rivain-Prouff algorithm for AES, and its extension by Carlet et al. to any look-up table.
- In practice for AES our algorithm is less efficient than Rivain-Prouff, which can take advantage of the special algebraic structure of the AES Sbox; however for DES our algorithm performs slightly better.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410126 (1).pdf`
- `downloads/84410126 (2).pdf`
- `downloads/84410126 (3).pdf`
- `downloads/84410126.pdf`
