---
id: KN-LIT-4953
type: literature
title: "More Efficient (Almost) Tightly Secure Structure-Preserving Signatures"
authors:
  - "Romain Gay ∗"
  - "Dennis Hofheinz"
  - "Lisa Kohl"
  - "Jiaxin Pan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, signature, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide a structure-preserving signature (SPS) scheme with an (almost) tight security reduction to a standard assumption. Compared to the state-of-the-art tightly secure SPS scheme of Abe et al.

## Key claims (as reported)
- (CRYPTO 2017), our scheme has smaller signatures and public keys (of about 56%, resp.
- 40% of the size of signatures and public keys in Abe et al.’s scheme), and a lower security loss (of O(log Q) instead of O(λ), where λ is the security parameter, and Q = poly(λ) is the number of adversarial signature queries).
- While our scheme is still less compact than structure-preserving signature schemes without tight security reduction, it significantly lowers the price to pay for a tight security reduction.
- In fact, when accounting for a non-tight security reduction with larger key (i.e., group) sizes, the computational efficiency of our scheme becomes at least comparable to that of non-tightly secure SPS schemes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10822293 (1).pdf`
- `downloads/10822293.pdf`
