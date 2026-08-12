---
id: KN-LIT-561
type: literature
title: "Multi-Collision Resistant Hash Functions and their Applications"
authors:
  - "Itay Berman"
  - "Akshay Degwekar"
  - "Ron D. Rothblum"
  - "Prashant Nalini"
year: 2017
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2017/489"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2017/489"
tags: [cryptanalysis, hash, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Collision resistant hash functions are functions that shrink their input, but for which it is computationally infeasible to find a collision, namely two strings that hash to the same value (although collisions are abundant). In this work we study multi-collision resistant hash functions (MCRH) a natural relaxation of collision resistant hash functions in which it is difficult to find a t-way collision (i.e., t strings that hash to the same value) although finding (t − 1)-way collisions could be easy.

## Key claims (as reported)
- We show the following: – The existence of MCRH follows from the average case hardness of a variant of the Entropy Approximation problem.
- The goal in this problem (Goldreich, Sahai and Vadhan, CRYPTO ’99) is to distinguish circuits whose output distribution has high entropy from those having low entropy. – MCRH imply the existence of constant-round statistically hiding (and computationally binding) commitment schemes.
- As a corollary, using a result of Haitner et al.
- (SICOMP, 2015), we obtain a blackbox separation of MCRH from any one-way permutation.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10822177 (1).pdf`
- `downloads/10822177.pdf`
