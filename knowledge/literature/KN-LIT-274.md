---
id: KN-LIT-274
type: literature
title: "A Subexponential Algorithm for Evaluating"
authors:
  - "Large Degree Isogenies"
year: 2010
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1002.4228"
  url: "https://arxiv.org/abs/1002.4228"
tags: [curve-arithmetic, dlp, elliptic-curve, endomorphism, finite-field, isogeny, pairing, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An isogeny between elliptic curves is an algebraic morphism which is a group homomorphism. Many applications in cryptography require evaluating large degree isogenies between elliptic curves efficiently.

## Key claims (as reported)
- For ordinary curves of the same endomorphism ring, the previous best known algorithm has a worst case running time which is exponential in the length of the input.
- In this paper we show this problem can be solved in subexponential time under reasonable heuristics.
- Our approach is based on factoring the ideal corresponding to the kernel of the isogeny, modulo principal ideals, into a product of smaller prime ideals for which the isogenies can be computed directly.
- Combined with previous work of Bostan et al., our algorithm yields equations for large degree isogenies in quasi-optimal time given only the starting curve and the kernel.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1002.4228v2 (1).pdf`
- `downloads/1002.4228v2.pdf`
