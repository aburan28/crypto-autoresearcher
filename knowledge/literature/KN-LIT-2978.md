---
id: KN-LIT-2978
type: literature
title: "Communication Efficient Secure Linear Algebra"
authors:
  - "Kobbi Nissim"
  - "Enav Weinreb"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, finite-field, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present communication efficient secure protocols for a variety of linear algebra problems. Our main building block is a protocol for computing Gaussian Elimination on encrypted data.

## Key claims (as reported)
- As input for this protocol, Bob holds a k × k matrix M , encrypted with Alice’s key.
- At the end of the protocol run, Bob holds an encryption of an upper-triangular matrix M 0 such that the number of nonzero elements on the diagonal equals the rank of M .
- The communication complexity of our protocol is roughly O(k2 ).
- Building on Oblivious Gaussian elimination, we present secure protocols for several problems: deciding the intersection of linear and affine subspaces, picking a random vector from the intersection, and obliviously solving a set of linear equations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/38760526 (1).pdf`
- `downloads/38760526 (2).pdf`
- `downloads/38760526 (3).pdf`
- `downloads/38760526.pdf`
