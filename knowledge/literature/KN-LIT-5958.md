---
id: KN-LIT-5958
type: literature
title: "Protecting Cryptographic Keys Against Continual Leakage"
authors:
  - "Ali Juma"
  - "Yevgeniy Vahlis"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, pairing, side-channel, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Side-channel attacks have often proven to have a devastating effect on the security of cryptographic schemes. In this paper, we address the problem of storing cryptographic keys and computing on them in a manner that preserves security even when the adversary is able to obtain information leakage during the computation on the key.

## Key claims (as reported)
- Using any fully homomorphic encryption with re-randomizable ciphertexts, we show how to encapsulate a key and repeatedly evaluate arbitrary functions on it so that no adversary can gain any useful information from a large class of side-channel attacks.
- We work in the model of Micali and Reyzin, assuming that only the active part of memory during computation leaks information.
- Our construction makes use of a single “leak-free” hardware token that samples from a distribution that does not depend on the protected key or the function that is evaluated on it.
- Our construction is the first general compiler to achieve resilience against polytime leakage functions without performing any leak-free computation on the protected key.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230041 (1).pdf`
- `downloads/62230041 (2).pdf`
- `downloads/62230041 (3).pdf`
- `downloads/62230041.pdf`
