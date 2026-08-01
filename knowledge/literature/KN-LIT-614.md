---
id: KN-LIT-614
type: literature
title: "MULTIPARTY NON-INTERACTIVE KEY EXCHANGE AND MORE FROM ISOGENIES ON ELLIPTIC CURVES arXiv:1807.03038v3 [cs.CR] 31 Aug 2018"
authors:
  - "ALICE SILVERBERG"
  - "MEHDI TIBOUCHI"
  - "MARK ZHANDRY"
year: 2018
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1807.03038"
  url: "https://arxiv.org/abs/1807.03038"
tags: [abelian-variety, class-group, cryptanalysis, elliptic-curve, endomorphism, finite-field, hash, isogeny, number-theory, pairing, protocol, provable-security, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a framework for constructing an efficient non-interactive key exchange (NIKE) protocol for n parties for any n ≥ 2. Our approach is based on the problem of computing isogenies between isogenous elliptic curves, which is believed to be difficult.

## Key claims (as reported)
- We do not obtain a working protocol because of a missing step that is currently an open mathematical problem.
- What we need to complete our protocol is an efficient algorithm that takes as input an abelian variety presented as a product of isogenous elliptic curves, and outputs an isomorphism invariant of the abelian variety.
- Our framework builds a cryptographic invariant map, which is a new primitive closely related to a cryptographic multilinear map, but whose range does not necessarily have a group structure.
- Nevertheless, we show that a cryptographic invariant map can be used to build several cryptographic primitives, including NIKE, that were previously constructed from multilinear maps and indistinguishability obfuscation.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1807.03038v3.pdf`
