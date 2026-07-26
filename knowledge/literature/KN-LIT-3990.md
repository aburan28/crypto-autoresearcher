---
id: KN-LIT-3990
type: literature
title: "Fully Homomorphic Encryption with Polylog Overhead"
authors:
  - "C. Gentry"
  - "S. Halevi"
  - "N.P. Smart"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, finite-field, implementation, lattice, mov-fr, number-theory, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show that homomorphic evaluation of (wide enough) arithmetic circuits can be accomplished with only polylogarithmic overhead. Namely, we present a construction of fully homomorphic encryption (FHE) schemes that for security parameter λ can evaluate any width-Ω(λ) circuit with t gates in time t · polylog(λ).

## Key claims (as reported)
- To get low overhead, we use the recent batch homomorphic evaluation techniques of Smart-Vercauteren and Brakerski-Gentry-Vaikuntanathan, who showed that homomorphic operations can be applied to “packed” ciphertexts that encrypt vectors of plaintext elements.
- In this work, we introduce permuting/routing techniques to move plaintext elements across these vectors efficiently.
- Hence, we are able to implement general arithmetic circuit in a batched fashion without ever needing to “unpack” the plaintext vectors.
- We also introduce some other optimizations that can speed up homomorphic evaluation in certain cases.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72370461 (1).pdf`
- `downloads/72370461 (2).pdf`
- `downloads/72370461 (3).pdf`
- `downloads/72370461.pdf`
