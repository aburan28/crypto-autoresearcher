---
id: KN-LIT-2417
type: literature
title: "Algorithms in HElib"
authors:
  - "Shai Halevi"
  - "Victor Shoup"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, implementation, lattice, mov-fr]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
HElib is a software library that implements homomorphic encryption (HE), specifically the Brakerski-Gentry-Vaikuntanathan (BGV) scheme, focusing on effective use of the Smart-Vercauteren ciphertext packing techniques and the Gentry-Halevi-Smart optimizations. The underlying cryptosystem serves as the equivalent of a “hardware platform” for HElib, in that it defines a set of operations that can be applied homomorphically, and specifies their cost.

## Key claims (as reported)
- This “platform” is a SIMD environment (somewhat similar to Intel SSE and the like), but with unique cost metrics and parameters.
- In this report we describe some of the algorithms and optimization techniques that are used in HElib for data movement, linear algebra, and other operations over this “platform.”

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/86160286 (1).pdf`
- `downloads/86160286 (2).pdf`
- `downloads/86160286 (3).pdf`
- `downloads/86160286 (4).pdf`
- `downloads/86160286 (5).pdf`
- `downloads/86160286 (6).pdf`
- (+2 more duplicate copies)
