---
id: KN-LIT-3595
type: literature
title: "Efficient NIZKs from LWE via Polynomial Reconstruction and “MPC in the Head”"
authors:
  - "Riddhi Ghosal∗"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [extension-field, fhe, hash, lattice, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
All existing works building non-interactive zero-knowledge (NIZK) arguments for NP from the Learning With Errors (LWE) assumption have studied instantiating the Fiat-Shamir paradigm on a parallel repetition of an underlying honest-verifier zero knowledge (HVZK) Σ protocol, via an appropriately built correlation-intractable (CI) hash function from LWE. This technique has inherent efficiency losses that arise from parallel repetition.

## Key claims (as reported)
- In this work, we show how to make use of the more efficient “MPC in the Head” technique for building an underlying honest-verifier protocol upon which to apply the Fiat-Shamir paradigm.
- To make this possible, we provide a new and more efficient construction of CI hash functions from LWE, using efficient algorithms for polynomial reconstruction as the main technical tool.
- We stress that our work provides a new and more efficient “base construction” for building LWE-based NIZK arguments for NP.
- Our protocol can be the building block around which other efficiency-focused bootstrapping techniques can be applied, such as the bootstrapping technique of Gentry et al.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910231 (1).pdf`
- `downloads/137910231.pdf`
