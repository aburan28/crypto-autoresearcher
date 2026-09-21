---
id: KN-LIT-3470
type: literature
title: "Double-Block-Length Hash Function for Minimum Memory Size"
authors:
  - "Yusuke Naito"
  - "Yu Sasaki"
  - "Takeshi Sugawara"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Sharing a common primitive for multiple functionalities is essential for lightweight cryptography, and NIST’s lightweight cryptography competition (LWC) considers the integration of hashing to AEAD. While permutations are natural primitive choices in such a goal, for design diversity, it is interesting to investigate how small block-cipher (BC) based and tweakable block-cipher (TBC) based schemes can be.

## Key claims (as reported)
- Doubleblock-length (DBL) hash function modes are suitable to ensure the same security level for AEAD and hashing, but hard to achieve a small memory size.
- Romulus, a TBC-based finalist in NIST LWC, introduced the DBL hashing scheme Romulus-H, but it requires 3n + k bits of memory using an underlying primitive with an n-bit block and a k-bit (twea)key.
- Even the smallest DBL modes in the literature require 2n + k bits of memory.
- Addressing this issue, we present new DBL modes EXEX-NI and EXEX-I achieving (n + k)-bit state size, i.e., no extra memory in addition to n + k bits needed within the primitive.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900071 (1).pdf`
- `downloads/130900071.pdf`
