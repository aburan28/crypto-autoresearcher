---
id: KN-LIT-1492
type: literature
title: "THE SEA ALGORITHM FOR ENDOMORPHISMS OF SUPERSINGULAR"
authors:
  - "ELLIPTIC CURVES"
year: 2025
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2501.16321"
  url: "https://arxiv.org/abs/2501.16321"
tags: [curve-arithmetic, elliptic-curve, endomorphism, isogeny, lattice, pairing, provable-security, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
For a prime p > 3 and a supersingular elliptic curve E defined over Fp2 with j(E) ∈ / {0, 1728}, consider an endomorphism α of E represented as a composition of L isogenies of degree at most d. We prove that the trace of α may be computed in O(n4 (log n)2 + dLn3 ) bit operations, where n = log(p), using a generalization of the SEA algorithm for computing the trace of the Frobenius endomorphism of an ordinary elliptic curve.

## Key claims (as reported)
- When L ∈ O(log p) and d ∈ O(1), this complexity matches the heuristic complexity of the SEA algorithm.
- Our theorem is unconditional, unlike the complexity analysis of the SEA algorithm, since the kernel of an arbitrary isogeny of a supersingular elliptic curve is defined over an extension of constant degree, independent of p.
- We also provide practical speedups, including a fast algorithm to compute the trace of α modulo p.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2501.16321v1 (1).pdf`
- `downloads/2501.16321v1.pdf`
