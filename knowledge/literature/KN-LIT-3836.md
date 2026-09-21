---
id: KN-LIT-3836
type: literature
title: "Faster Evaluation of SBoxes via Common Shares"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, finite-field, hash, mpc, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a new technique for improving the efficiency of the masking countermeasure against side-channel attacks. Our technique is based on using common shares between secret variables, in order to reduce the number of finite field multiplications.

## Key claims (as reported)
- Our algorithms are proven secure in the ISW probing model with n ⩾ t + 1 shares against t probes.
- For AES, we get an equivalent of 2.8 non-linear multiplications for every SBox evaluation, instead of 4 in the Rivain-Prouff countermeasure.
- We obtain similar improvements for other block-ciphers.
- Our technique is easy to implement and performs relatively well in practice, with roughly a 20% speed-up compared to existing algorithms.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98130115 (1).pdf`
- `downloads/98130115.pdf`
