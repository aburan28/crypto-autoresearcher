---
id: KN-LIT-2966
type: literature
title: "Collusion-Resistant Functional Encryption for RAMs"
authors:
  - "Prabhanjan Ananth"
  - "Kai-Min Chung"
  - "Xiong Fan"
  - "Luowen Qian"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In recent years, functional encryption (FE) has established itself as one of the fundamental primitives in cryptography. The choice of model of computation to represent the functions associated with the functional keys plays a critical role in the complexity of the algorithms of an FE scheme.

## Key claims (as reported)
- Historically, the functions are represented as circuits.
- However, this results in the decryption time of the FE scheme growing proportional to not only the worst case running time of the function but also the size of the input, which in many applications can be quite large.
- In this work, we present the first construction of a public-key collusion-resistant FE scheme, where the functions, associated with the keys, are represented as random access machines (RAMs).
- We base the security of our construction on the existence of: (i) public-key collusion-resistant FE for circuits and, (ii) public-key doubly-efficient private-information retrieval [Boyle et al., Canetti et al., TCC 2017].

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910176 (1).pdf`
- `downloads/137910176.pdf`
