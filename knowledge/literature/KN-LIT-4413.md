---
id: KN-LIT-4413
type: literature
title: "Improved Key Recovery Attacks on Reduced-Round AES in the Single-Key Setting"
authors:
  - "Patrick Derbez"
  - "Pierre-Alain Fouque"
  - "Jérémy Jean"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we revisit meet-in-the-middle attacks on AES in the single-key model and improve on Dunkelman, Keller and Shamir attacks at Asiacrypt 2010. We present the best attack on 7 rounds of AES-128 where data/time/memory complexities are below 2100 .

## Key claims (as reported)
- Moreover, we are able to extend the number of rounds to reach attacks on 8 rounds for both AES-192 and AES-256.
- This gives the best attacks on those two versions with a data complexity of 2107 chosen-plaintexts, a memory complexity of 296 and a time complexity of 2172 for AES-192 and 2196 for AES-256.
- Finally, we also describe the best attack on 9 rounds of AES-256 with 2120 chosen plaintexts and time and memory complexities of 2203 .
- All these attacks have been found by carefully studying the number of reachable multisets in Dunkelman et al. attacks.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/78810368 (1).pdf`
- `downloads/78810368 (2).pdf`
- `downloads/78810368 (3).pdf`
- `downloads/78810368.pdf`
