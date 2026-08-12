---
id: KN-LIT-7635
type: literature
title: "A Kilobit Hidden SNFS Discrete Logarithm Computation"
authors:
  - "Joshua Fried"
  - "Pierrick Gaudry"
  - "Nadia Heninger"
  - "Emmanuel Thomé"
year: 2017
venue: "EUROCRYPT 2017; IACR ePrint 2016/961"
identifiers:
  eprint: "2016/961"
  doi: "10.1007/978-3-319-56620-7_8"
  arxiv: null
  url: "https://eprint.iacr.org/2016/961"
tags: [snfs, trapdoor, discrete-log, prime-field, hidden-structure, parameter-generation]
confidence: reported
citation_verified: true
added: "2026-07-31"
superseded_by: null
---

## Contribution

Performs a 1024-bit special-NFS discrete log in $\mathbb{F}_p^*$ for a prime that
appears random (DSA-friendly $p-1$ factorization) but was trapdoored to admit
SNFS. Demonstrates practical parameter-level trapdoors with private
precomputation and hard public detection.

## Key claims (from fetched PDF abstract)

- First reported kilobit prime-field DL computation (academic cluster, CADO-NFS).
- Trapdoor hidden in the prime's algebraic structure; detection argued out of reach.
- Defense: verifiably random primes.
- Also reports SNFS DLs on conspicuously weak primes found in the wild.

## Relevance to GOAL-ECTD-001

Gold-standard analogy for what a prime-field ECDLP trapdoor should look like:
ordinary-looking public parameters, hidden algebraic representation, expensive
private precomputation, cheap individual logs, no obvious public detector.
Not an elliptic-curve result.

## Local copies

- `inputs/ECTD-TESKE-20260731/sources/fght-2016-961.pdf`
  (Wayback Machine mirror of eprint PDF; direct eprint HTTP 403;
  sha256 `5ba7f4b411803cf0f35789e881083014d0acaffbab19050e4bbcfb103fee36ea`)
