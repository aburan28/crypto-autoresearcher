---
id: KN-LIT-4742
type: literature
title: "Limits on the Power of Garbling Techniques for Public-Key Encryption"
authors:
  - "Sanjam Garg"
  - "Mohammad Hajiabadi"
  - "Mohammad Mahmoody"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Understanding whether public-key encryption can be based on one-way functions is a fundamental open problem in cryptography. The seminal work of Impagliazzo and Rudich [STOC’89] shows that black-box constructions of public-key encryption from one-way functions are impossible.

## Key claims (as reported)
- However, this impossibility result leaves open the possibility of using non-black-box techniques for achieving this goal.
- One of the most powerful classes of non-black-box techniques, which can be based on one-way functions (OWFs) alone, is Yao’s garbled circuit technique [FOCS’86].
- As for the non-black-box power of this technique, the recent work of Döttling and Garg [CRYPTO’17] shows that the use of garbling allows us to circumvent known black-box barriers in the context of identity-based encryption.
- We prove that garbling of circuits that have OWF (or even random oracle) gates in them are insufficient for obtaining public-key encryption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993438 (1).pdf`
- `downloads/10993438.pdf`
