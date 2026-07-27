---
id: KN-LIT-6254
type: literature
title: "Reversible Proofs of Sequential Work"
authors:
  - "Hamza Abusalah"
  - "Chethan Kamath"
  - "Karen Klein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, hash, pairing, provable-security, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Proofs of sequential work (PoSW) are proof systems where a prover, upon receiving a statement χ and a time parameter T computes a proof φ(χ, T ) which is efficiently and publicly verifiable. The proof can be computed in T sequential steps, but not much less, even by a malicious party having large parallelism.

## Key claims (as reported)
- A PoSW thus serves as a proof that T units of time have passed since χ was received.
- PoSW were introduced by Mahmoody, Moran and Vadhan [MMV11], a simple and practical construction was only recently proposed by Cohen and Pietrzak [CP18].
- In this work we construct a new simple PoSW in the random permutation model which is almost as simple and efficient as [CP18] but conceptually very different.
- Whereas the structure underlying [CP18] is a hash tree, our construction is based on skip lists and has the interesting property that computing the PoSW is a reversible computation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114760189 (1).pdf`
- `downloads/114760189.pdf`
