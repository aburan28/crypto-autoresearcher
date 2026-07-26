---
id: KN-LIT-3299
type: literature
title: "Cryptographic applications of capacity theory: On the optimality of Coppersmith’s method for univariate polynomials"
authors:
  - "Ted Chinburg"
  - "Brett Hemenway"
  - "Nadia Heninger"
  - "Zachary Scherr"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, lattice, pairing, provable-security, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We draw a new connection between Coppersmith’s method for finding small solutions to polynomial congruences modulo integers and the capacity theory of adelic subsets of algebraic curves. Coppersmith’s method uses lattice basis reduction to construct an auxiliary polynomial that vanishes at the desired solutions.

## Key claims (as reported)
- Capacity theory provides a toolkit for proving when polynomials with certain boundedness properties do or do not exist.
- Using capacity theory, we prove that Coppersmith’s bound for univariate polynomials is optimal in the sense that there are no auxiliary polynomials of the type he used that would allow finding roots of size N 1/d+ for any monic degree-d polynomial modulo N .
- Our results rule out the existence of polynomials of any degree and do not rely on lattice algorithms, thus eliminating the possibility of improvements for special cases or even superpolynomial-time improvements to Coppersmith’s bound.
- We extend this result to constructions of auxiliary polynomials using binomial polynomials, and rule out the existence of any auxiliary polynomial of this form that would find solutions of size N 1/d+ unless N has a very small prime factor.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10031302 (1).pdf`
- `downloads/10031302.pdf`
