---
id: KN-LIT-7077
type: literature
title: "The SPHINCS+ Signature Framework"
authors:
  - "Full version"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [ecdsa, hash, pairing, pqc, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce SPHINCS+ , a stateless hash-based signature framework. SPHINCS+ has significant advantages over the state of the art in terms of speed, signature size, and security, and is among the nine remaining signature schemes in the second round of the NIST PQC standardization project.

## Key claims (as reported)
- One of our main contributions in this context is a new few-time signature scheme that we call FORS.
- Our second main contribution is the introduction of tweakable hash functions and a demonstration how they allow for a unified security analysis of hash-based signature schemes.
- We give a security reduction for SPHINCS+ using this abstraction and derive secure parameters in accordance with the resulting bound.
- Finally, we present speed results for our optimized implementation of SPHINCS+ and compare to SPHINCS-256, Gravity-SPHINCS, and Picnic.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/spx-20190923.pdf`
