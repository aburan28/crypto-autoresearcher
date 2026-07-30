---
id: KN-LIT-1387
type: literature
title: "Enhanced Algorithms for the Representation of integers by Binary Quadratic forms: Reduction to Subset Sum"
authors:
  - "MAHER MAMAH"
year: 2025
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2502.11402"
  url: "https://arxiv.org/abs/2502.11402"
tags: [complexity-theory, elliptic-curve, endomorphism, factoring, isogeny, number-theory, pairing, provable-security, quantum, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we give efficient algorithms for solving the Diophantine equation f (x, y) = m for arbitrary definite binary quadratic form f , given the factorization of m. While Cornacchia’s algorithm to solve x2 + dy 2 = m provides an efficient method in many cases, its running time becomes exponentially large when m is highly composite, and inherits some subtleties when generalizing to arbitrary form f .

## Key claims (as reported)
- To address these issues, we show how to reduce the problem to an instance of the Subset-Sum, a weakly NP-complete problem, allowing for more efficient solutions.
- Leveraging this approach, we develop deterministic algorithms that adapt to different cases based on disc(f ) and m.
- In particular, when |disc(f )| = polylog(m), we provide a polynomial-time solution that remains efficient regardless of the structure of m.
- For more general cases, we present an algorithm that improves upon Cornacchia’s method, achieving a quadratic speedup.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2502.11402v2.pdf`
