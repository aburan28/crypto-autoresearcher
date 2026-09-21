---
id: KN-LIT-4793
type: literature
title: "Low Probability Differentials and the Cryptanalysis of Full-Round CLEFIA-128"
authors:
  - "Sareh Emami"
  - "San Ling"
  - "Ivica Nikolić"
  - "Josef Pieprzyk and"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
So far, low probability differentials for the key schedule of block ciphers have been used as a straightforward proof of security against related-key differential analysis. To achieve resistance, it is believed that for cipher with k-bit key it suffices the upper bound on the probability to be 2−k .

## Key claims (as reported)
- Surprisingly, we show that this reasonable assumption is incorrect, and the probability should be (much) lower than 2−k .
- Our counter example is a related-key differential analysis of the well established block cipher CLEFIA-128.
- We show that although the key schedule of CLEFIA-128 prevents differentials with a probability higher than 2−128 , the linear part of the key schedule that produces the round keys, and the Feistel structure of the cipher, allow to exploit particularly chosen differentials with a probability as low as 2−128 .
- CLEFIA-128 has 214 such differentials, which translate to 214 pairs of weak keys.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730193 (1).pdf`
- `downloads/88730193 (2).pdf`
- `downloads/88730193 (3).pdf`
- `downloads/88730193.pdf`
