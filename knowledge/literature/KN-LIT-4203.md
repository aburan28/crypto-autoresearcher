---
id: KN-LIT-4203
type: literature
title: "High-Performance Scalar Multiplication using 8-Dimensional GLV/GLS Decomposition"
authors:
  - "Joppe W. Bos"
  - "Craig Costello"
  - "Huseyin Hisil"
  - "Kristin Lauter"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [abelian-variety, curve-arithmetic, dlp, elliptic-curve, endomorphism, extension-field, finite-field, glv-gls, hyperelliptic, index-calculus, jacobian, pairing, prime-field, provable-security, survey, weil-descent]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper explores the potential for using genus 2 curves over quadratic extension fields in cryptography, motivated by the fact that they allow for an 8-dimensional scalar decomposition when using a combination of the GLV/GLS algorithms. Besides lowering the number of doublings required in a scalar multiplication, this approach has the advantage of performing arithmetic operations in a 64-bit ground field, making it an attractive candidate for embedded devices.

## Key claims (as reported)
- We found cryptographically secure genus 2 curves which, although susceptible to index calculus attacks, aim for the standardized 112-bit security level.
- Our implementation results on both high-end architectures (Ivy Bridge) and low-end ARM platforms (Cortex-A8) highlight the practical benefits of this approach.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80860190 (1).pdf`
- `downloads/80860190 (2).pdf`
- `downloads/80860190 (3).pdf`
- `downloads/80860190.pdf`
