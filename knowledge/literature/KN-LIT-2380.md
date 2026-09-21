---
id: KN-LIT-2380
type: literature
title: "Algebraic (Trapdoor) One-Way Functions and their Applications"
authors:
  - "Dario Catalano"
  - "Dario Fiore"
  - "Rosario Gennaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, lattice, pairing, rsa, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we introduce the notion of Algebraic (Trapdoor) One Way Functions, which, roughly speaking, captures and formalizes many of the properties of number-theoretic one-way functions. Informally, a (trapdoor) one way function F : X → Y is said to be algebraic if X and Y are (finite) abelian cyclic groups, the function is homomorphic i.e.

## Key claims (as reported)
- F (x) · F (y) = F (x · y), and is ring-homomorphic, meaning that it is possible to compute linear operations “in the exponent” over some ring (which may be different from Zp where p is the order of the underlying group X) without knowing the bases.
- Moreover, algebraic OWFs must be flexibly one-way in the sense that given y = F (x), it must be infeasible to compute (x0 , d) such that F (x0 ) = y d (for d 6= 0).
- Interestingly, algebraic one way functions can be constructed from a variety of standard number theoretic assumptions, such as RSA, Factoring and CDH over bilinear groups.
- As a second contribution of this paper, we show several applications where algebraic (trapdoor) OWFs turn out to be useful.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/77850679 (1).pdf`
- `downloads/77850679 (2).pdf`
- `downloads/77850679 (3).pdf`
- `downloads/77850679.pdf`
