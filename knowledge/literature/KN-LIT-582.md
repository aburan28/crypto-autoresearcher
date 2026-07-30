---
id: KN-LIT-582
type: literature
title: "A First-Order SCA Resistant AES without Fresh Randomness"
authors:
  - "Felix Wegener"
  - "Amir Moradi"
year: 2018
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2018/172"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2018/172"
tags: [finite-field, pairing, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Since the advent of Differential Power Analysis (DPA) in the late 1990s protecting embedded devices against Side-Channel Analysis (SCA) attacks has been a major research effort. Even though many different first-order secure masking schemes are available today, when applied to the AES S-box they all require fresh random bits in every evaluation.

## Key claims (as reported)
- As the quality criteria for generating random numbers on an embedded device are not well understood, an integrated Random Number Generator (RNG) can be the weak spot of any protected implementation and may invalidate an otherwise secure implementation.
- We present a new construction based on Threshold Implementations and Changing of the Guards to realize a first-order secure AES with zero per-round randomness.
- Hence, our design does not need a built-in RNG, thereby enhancing security and reducing the overhead.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2018-172.pdf`
