---
id: KN-LIT-1196
type: literature
title: "Alternative Key Schedules for the AES"
authors:
  - "Christina Boura"
  - "Patrick Derbez"
  - "Margot Funk"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/315"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/315"
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The AES block cipher is today the most important and analyzed symmetric algorithm. While all versions of the AES are known to be secure in the single-key setting, this is not the case in the related-key scenario.

## Key claims (as reported)
- In this article we try to answer the question whether the AES would resist better differential-like related-key attacks if the key schedule was different.
- For this, we search for alternative permutation-based key schedules by extending the work of Khoo et al. at ToSC 2017 and Derbez et al. at SAC 2018.
- We first show that the model of Derbez et al. was flawed.
- Then, we develop different approaches together with MILP-based tools to find good permutations that could be used as the key schedule for AES-128, AES-192 and AES-256.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-315.pdf`
