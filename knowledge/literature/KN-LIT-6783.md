---
id: KN-LIT-6783
type: literature
title: "SSE Implementation of Multivariate PKCs on Modern x86"
authors:
  - "Jintai Ding"
  - "Eric Li-Hsiang Kuo"
  - "Frost Yu-Shuang Lee"
  - "Bo-Yin Yang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, hash, implementation, mov-fr, rsa, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Multivariate Public Key Cryptosystems (MPKCs) are often touted as future-proo ng against Quantum Computers. It also has been known for e ciency compared to traditional alternatives.

## Key claims (as reported)
- However, this advantage seems to erode with the increase of arithmetic resources in modern CPUs and improved algorithms, especially with respect to Elliptic Curve Cryptography (ECC).
- In this paper, we show that hardware advances do not just favor ECC.
- Modern commodity CPUs also have many small integer arithmetic/logic resources, embodied by SSE2 or other vector instruction sets, that are useful for MPKCs.
- In particular, Intel's SSSE3 instructions can speed up both public and private maps over prior software implementations of Rainbow-type systems up to 4×.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/57470031 (1).pdf`
- `downloads/57470031 (2).pdf`
- `downloads/57470031 (3).pdf`
- `downloads/57470031.pdf`
