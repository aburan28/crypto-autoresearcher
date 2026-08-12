---
id: KN-LIT-5973
type: literature
title: "Provably Secure Higher-Order Masking of AES"
authors:
  - "Matthieu Rivain"
  - "Emmanuel Prouff"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, mpc, pairing, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Implementations of cryptographic algorithms are vulnerable to Side Channel Analysis (SCA). To counteract it, masking schemes are usually involved which randomize key-dependent data by the addition of one or several random value(s) (the masks).

## Key claims (as reported)
- When dth-order masking is involved (i.e. when d masks are used per key-dependent variable), the complexity of performing an SCA grows exponentially with the order d.
- The design of generic dth-order masking schemes taking the order d as security parameter is therefore of great interest for the physical security of cryptographic implementations.
- This paper presents the first generic dth-order masking scheme for AES with a provable security and a reasonable software implementation overhead.
- Our scheme is based on the hardware-oriented masking scheme published by Ishai et al. at Crypto 2003.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62250403 (1).pdf`
- `downloads/62250403 (2).pdf`
- `downloads/62250403 (3).pdf`
- `downloads/62250403.pdf`
