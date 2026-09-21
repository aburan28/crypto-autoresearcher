---
id: KN-LIT-762
type: literature
title: "Far Field EM Side-Channel Attack on AES Using Deep Learning"
authors:
  - "Ruize Wang"
year: 2020
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2020/1096"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2020/1096"
tags: [cryptanalysis, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present the first deep learning-based side-channel attack on AES128 using far field electromagnetic emissions as a side channel. Our neural networks are trained on traces captured from five different Bluetooth devices at five different distances to target and tested on four other Bluetooth devices.

## Key claims (as reported)
- We can recover the key from less than 10K traces captured in an office environment at 15 m distance to target even if the measurement for each encryption is taken only once.
- Previous template attacks required multiple repetitions of the same encryption.
- For the case of 1K repetitions, we need less than 400 traces on average at 15 m distance to target.
- This improves the template attack presented at CHES’2020 which requires 5K traces and key enumeration up to 223 .

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2020-1096.pdf`
