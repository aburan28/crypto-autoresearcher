---
id: KN-LIT-1084
type: literature
title: "Computing Isogenies of Power-Smooth Degrees"
authors:
  - "Between PPAVs"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/508"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/508"
tags: [abelian-variety, complexity-theory, elliptic-curve, hash, isogeny, jacobian, pairing, sidh-csidh, signature, supersingular, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The wave of attacks by Castryck and Decru (Eurocrypt, 2023), Maino, Martindale, Panny, Pope and Wesolowski (Eurocrypt, 2023) and Robert (Eurocrypt, 2023), highlight the destructive facet of calculating power-smooth degree isogenies between higher-dimensional abelian varieties in isogeny-based cryptography. Despite those recent attacks, there is still interest in using isogenies but for building protocols on top of higherdimensional abelian varieties.

## Key claims (as reported)
- Examples of such protocols are Public-Key Encryption, Key Encapsulation Mechanism, Verifiable Delay Function, Verifiable Random Function, and Digital Signatures.
- This work abstracts and proposes a generalization of the strategy technique by Jao, De Feo and Plût (Journal of Mathematical Cryptology, 2014) to give an efficient generic algorithm for computing isogenies between higherdimensional abelian varieties with kernels being maximal isotropic of power-smooth degree.
- To illustrate the impact of using such strategy technique, we draft our experiments on the computation of isogenies over two-dimensional abelian varieties determined by a maximal isotropic subgroup of torsion with a power of two or three.
- Our experiments illustrate a speed-up of 1.25x faster than the state-of-the-art (about 20% of savings).

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-508.pdf`
