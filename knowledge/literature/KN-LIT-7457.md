---
id: KN-LIT-7457
type: literature
title: "Verifiable Random Functions from Identity-based Key Encapsulation?"
authors:
  - "Michel Abdalla"
  - "Dario Catalano"
  - "Dario Fiore"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a methodology to construct verifiable random functions from a class of identity based key encapsulation mechanisms (IB-KEM) that we call VRF suitable. Informally, an IB-KEM is VRF suitable if it provides what we call unique decryption (i.e. given a ciphertext C produced with respect to an identity ID, all the secret keys corresponding to identity ID 0 , decrypt to the same value, even if ID 6= ID 0 ) and it satisfies an additional property that we call pseudorandom decapsulation.

## Key claims (as reported)
- In a nutshell, pseudorandom decapsulation means that if one decrypts a ciphertext C, produced with respect to an identity ID, using the decryption key corresponding to any other identity ID 0 the resulting value looks random to a polynomially bounded observer.
- Interestingly, we show that most known IB-KEMs already achieve pseudorandom decapsulation.
- Our construction is of interest both from a theoretical and a practical perspective.
- Indeed, apart from establishing a connection between two seemingly unrelated primitives, our methodology is direct in the sense that, in contrast to most previous constructions, it avoids the inefficient Goldreich-Levin hardcore bit transformation.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54790555 (1).pdf`
- `downloads/54790555 (2).pdf`
- `downloads/54790555 (3).pdf`
- `downloads/54790555.pdf`
