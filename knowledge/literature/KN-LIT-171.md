---
id: KN-LIT-171
type: literature
title: "Do All Elliptic Curves of the Same Order Have the Same Difficulty of Discrete Log?"
authors:
  - "David Jao"
  - "Stephen Miller⋆"
  - "Ramarathnam Venkatesan"
year: 2004
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "0411378"
  url: "https://arxiv.org/abs/0411378"
tags: [dlp, ecdlp, elliptic-curve, endomorphism, finite-field, isogeny, number-theory, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The aim of this paper is to justify the common cryptographic practice of selecting elliptic curves using their order as the primary criterion. We can formalize this issue by asking whether the discrete log problem (dlog) has the same difficulty for all curves over a given finite field with the same order.

## Key claims (as reported)
- We prove that this is essentially true by showing polynomial time random reducibility of dlog among such curves, assuming the Generalized Riemann Hypothesis (GRH).
- We do so by constructing certain expander graphs, similar to Ramanujan graphs, with elliptic curves as nodes and low degree isogenies as edges.
- The result is obtained from the rapid mixing of random walks on this graph.
- Our proof works only for curves with (nearly) the same endomorphism rings.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/021 (2).pdf`
- `downloads/021 (3).pdf`
- `downloads/021 (5).pdf`
- `downloads/021 (7).pdf`
- `downloads/0411378v3 (1).pdf`
- `downloads/0411378v3 (2).pdf`
- (+2 more duplicate copies)
