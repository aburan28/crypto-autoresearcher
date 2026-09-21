---
id: KN-LIT-6899
type: literature
title: "Superscalar Coprocessor for High-speed Curve-based Cryptography ?"
authors:
  - "K. Sakiyama"
  - "L. Batina"
  - "B. Preneel"
  - "I. Verbauwhede"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, hyperelliptic, implementation, rsa, side-channel, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a superscalar coprocessor for high-speed curvebased cryptography. It accelerates scalar multiplication by exploiting instruction-level parallelism (ILP) dynamically and processing multiple instructions in parallel.

## Key claims (as reported)
- The system-level architecture is designed so that the coprocessor can fully utilize the superscalar feature.
- The implementation results show that scalar multiplication of Elliptic Curve Cryptography (ECC) over GF(2163 ), Hyperelliptic Curve Cryptography (HECC) of genus 2 over GF(283 ) and ECC over a composite field, GF((283 )2 ) can be improved by a factor of 1.8, 2.7 and 2.5 respectively compared to the case of a basic single-scalar architecture.
- This speed-up is achieved by exploiting parallelism in curve-based cryptography.
- The coprocessor deals with a single instruction that can be used for all field operations such as multiplications and additions.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/33 (1).pdf`
- `downloads/33 (2).pdf`
- `downloads/33 (3).pdf`
- `downloads/33.pdf`
