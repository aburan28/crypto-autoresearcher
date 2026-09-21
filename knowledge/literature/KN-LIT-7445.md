---
id: KN-LIT-7445
type: literature
title: "Vector Commitments over Rings and Compressed Σ-Protocols"
authors:
  - "Thomas Attema"
  - "Ignacio Cascudo"
  - "Ronald Cramer"
  - "Ivan Damgård"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, mpc, pairing, prime-field, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Compressed Σ-Protocol Theory (CRYPTO 2020) presents an “alternative” to Bulletproofs that achieves the same communication complexity while adhering more elegantly to existing Σ-protocol theory, which enables their techniques to be directly applicable to other widely used settings in the context of “plug & play” algorithmics. Unfortunately, their techniques are restricted to arithmetic circuits over prime fields, which rules out the possibility of using more machine-friendly moduli such as powers of 2, which have proven to improve efficiency in applications.

## Key claims (as reported)
- In this work we show that such techniques can be generalized to the case of arithmetic circuits modulo any number.
- This enables the use of powers of 2, which can prove to be beneficial for efficiency, but it also facilitates the use of other moduli that might prove useful in different applications.
- In order to achieve this, we first present an instantiation of the main building block of the theory of compressed Σ-protocols, namely compact vector commitments.
- Our construction, which may be of independent interest, is homomorphic modulo any positive integer m, a result that was not known in the literature before.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470020 (1).pdf`
- `downloads/137470020.pdf`
