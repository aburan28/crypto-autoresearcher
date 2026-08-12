---
id: KN-LIT-1710
type: literature
title: "Key-Independent Secret-Key Distinguisher for 7-Round AES based on the Joint Generalized Zero-Difference Property"
authors:
  - "Hanbeom Shin"
  - "Sunyeop Kim"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/980"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/980"
tags: [cryptanalysis, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A key-independent secret-key distinguisher identifies structural deviations from an ideal random permutation without discovering any information about the secret key. It is therefore of primary importance for understanding the inherent properties of a block cipher’s round function.

## Key claims (as reported)
- While numerous key-independent secret-key distinguishers have been proposed for 5- and 6-round AES, none has been proposed for 7round AES to date.
- In this paper, we propose the first key-independent secret-key distinguisher for 7-round AES, which exploits solely the structural properties of the round function.
- We propose the Joint Generalized Zero-Difference Property, where a quartet constructed from related differences satisfies three distinct generalized zero-difference properties simultaneously.
- By leveraging this joint property, we construct a new 7-round differential characteristic that a right quartet follows with a probability of 2−250.4 , whereas a random permutation satisfies the same conditions with a probability of 2−253.4 .

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-980 (1).pdf`
- `downloads/2026-980.pdf`
