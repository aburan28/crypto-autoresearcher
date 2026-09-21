---
id: KN-LIT-5807
type: literature
title: "Post-Quantum Security of Fiat-Shamir"
authors:
  - "Dominique Unruh"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, pqc, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Fiat-Shamir construction (Crypto 1986) is an efficient transformation in the random oracle model for creating non-interactive proof systems and signatures from sigma-protocols. In classical cryptography, Fiat-Shamir is a zero-knowledge proof of knowledge assuming that the underlying sigma-protocol has the zero-knowledge and special soundness properties.

## Key claims (as reported)
- Unfortunately, Ambainis, Rosmanis, and Unruh (FOCS 2014) ruled out non-relativizing proofs under those conditions in the quantum setting.
- In this paper, we show under which strengthened conditions the Fiat-Shamir proof system is still post-quantum secure.
- Namely, we show that if we require the sigma-protocol to have computational zero-knowledge and statistical soundness, then Fiat-Shamir is a zero-knowledge simulation-sound proof system (but not a proof of knowledge!).
- Furthermore, we show that Fiat-Shamir leads to a post-quantum secure unforgeable signature scheme when additionally assuming a “dual-mode hard instance generator” for generating key pairs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240307 (1).pdf`
- `downloads/106240307.pdf`
