---
id: KN-LIT-6842
type: literature
title: "Structural Lattice Reduction: Generalized Worst-Case to Average-Case Reductions and Homomorphic Cryptosystems"
authors:
  - "Nicolas Gama"
  - "Malika Izabachène"
  - "Phong Q. Nguyen"
  - "Xiang Xie"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, fhe, lattice, protocol, provable-security, quantum, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In lattice cryptography, worst-case to average-case reductions rely on two problems: Ajtai’s SIS and Regev’s LWE, which both refer to a very small class of random lattices related to the group G = Zn q. We generalize worst-case to average-case reductions to all integer lattices of sufficiently large determinant, by allowing G to be any (sufficiently large) finite abelian group.

## Key claims (as reported)
- Our main tool is a novel generalization of lattice reduction, which we call structural lattice reduction: given a finite abelian group G and a lattice L, it finds a short basis of some lattice L̄ such that L ⊆ L̄ and L̄/L ≃ G.
- Our group generalizations of SIS and LWE allow us to abstract lattice cryptography, yet preserve worstcase assumptions: as an illustration, we provide a somewhat conceptually simpler generalization of the Alperin-Sheriff-Peikert variant of the Gentry-Sahai-Waters homomorphic scheme.
- We introduce homomorphic mux gates, which allows us to homomorphically evaluate any boolean function with a noise overhead proportional to the square root of its number of variables, and bootstrap the full scheme using only a linear noise overhead.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650318 (1).pdf`
- `downloads/96650318.pdf`
