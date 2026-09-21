---
id: KN-LIT-650
type: literature
title: "Truncated Differential Properties of the Diagonal Set of Inputs for 5-round AES (Extended Version)"
authors:
  - "Lorenzo Grassi"
  - "Christian Rechberger"
year: 2018
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2018/182"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2018/182"
tags: [cryptanalysis, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the last couple of years, a new wave of results appeared, proposing and exploiting new properties of round-reduced AES. In this paper we survey and combine some of these results (namely, the multipleof-n property and the mixture differential cryptanalysis) in a systematic way in order to answer more general questions regarding the probability distribution of encrypted diagonal sets.

## Key claims (as reported)
- This allows to analyze this special set of inputs, and report on new properties regarding the probability distribution of the number of different pairs of corresponding ciphertexts are equal in certain anti-diagonal(s) after 5 rounds.
- An immediate corollary of the multiple-of-8 property is that the variance of such a distribution can be shown to be higher than for a random permutation.
- Surprisingly, also the mean of the distribution is significantly different from random, something which cannot be explained by the multiple-of-8 property.
- We propose a theoretical explanation of this, by assuming an APN-like assumption on the S-Box which closely resembles the AES-Sbox.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2018-182.pdf`
