---
id: KN-LIT-6741
type: literature
title: "Solving Quadratic Equations with XL on Parallel Architectures"
authors:
  - "Chen-Mou Cheng"
  - "Tung Chou"
  - "Ruben Niederhagen"
  - "Bo-Yin Yang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, finite-field, groebner, mov-fr, number-theory, provable-security, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Solving a system of multivariate quadratic equations (MQ) is an NP-complete problem whose complexity estimates are relevant to many cryptographic scenarios. In some cases it is required in the best known attack; sometimes it is a generic attack (such as for the multivariate PKCs), and sometimes it determines a provable level of security (such as for the QUAD stream ciphers).

## Key claims (as reported)
- Under reasonable assumptions, the best way to solve generic MQ systems is the XL algorithm implemented with a sparse matrix solver such as Wiedemann’s algorithm.
- Knowing how much time an implementation of this attack requires gives us a good idea of how future cryptosystems related to MQ can be broken, similar to how implementations of the General Number Field Sieve that factors smaller RSA numbers give us more insight into the security of actual RSA-based cryptosystems.
- This paper describes such an implementation of XL using the block Wiedemann algorithm.
- In 5 days we are able to solve a system with 32 variables and 64 equations over F16 (a computation of about 260.3 bit operations) on a small cluster of 8 nodes, with 8 CPU cores and 36 GB of RAM in each node.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74280353 (1).pdf`
- `downloads/74280353 (2).pdf`
- `downloads/74280353 (3).pdf`
- `downloads/74280353.pdf`
