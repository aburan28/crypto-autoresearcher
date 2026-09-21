---
id: KN-LIT-7296
type: literature
title: "Two Power Analysis Attacks against One-Mask Methods"
authors:
  - "Mehdi-Laurent Akkar"
  - "Régis Bévan"
  - "Louis Goubin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In order to protect a cryptographic algorithm against Power Analysis attacks, a well-known method consists in hiding all the internal data with randomly chosen masks. Following this idea, an AES implementation can be protected against Differential Power Analysis (DPA) by the “Transformed Masking Method”, proposed by Akkar and Giraud at CHES’2001, requiring two distinct masks.

## Key claims (as reported)
- At CHES’2002, Trichina, De Seta and Germani suggested the use of a single mask to improve the performances of the protected implementation.
- We show here that their countermeasure can still be defeated by usual first-order DPA techniques.
- In another direction, Akkar and Goubin introduced at FSE’2003 a new countermeasure for protecting secret-key cryptographic algorithms against high-order differential power analysis (HO-DPA).
- As particular case, the “Unique Masking Method” is particularly well suited to the protection of DES implementations.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/30170331 (1).pdf`
- `downloads/30170331 (2).pdf`
- `downloads/30170331.pdf`
