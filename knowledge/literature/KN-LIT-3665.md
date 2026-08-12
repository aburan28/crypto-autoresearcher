---
id: KN-LIT-3665
type: literature
title: "Elliptic and Hyperelliptic Curves: a Practical Security Analysis"
authors:
  - "Joppe W. Bos"
  - "Craig Costello"
  - "Andrea Miele"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, ecdlp, elliptic-curve, finite-field, hyperelliptic, jacobian, pairing, pollard-rho, prime-field]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Motivated by the advantages of using elliptic curves for discrete logarithm-based public-key cryptography, there is an active research area investigating the potential of using hyperelliptic curves of genus 2. For both types of curves, the best known algorithms to solve the discrete logarithm problem are generic attacks such as Pollard rho, for which it is well-known that the algorithm can be sped up when the target curve comes equipped with an efficiently computable automorphism.

## Key claims (as reported)
- In this paper we incorporate all of the known optimizations (including those relating to the automorphism group) in order to perform a systematic security assessment of two elliptic curves and two hyperelliptic curves of genus 2.
- We use our software framework to give concrete estimates on the number of core years required to solve the discrete logarithm problem on four curves that target the 128-bit security level: on the standardized NIST CurveP-256, on a popular curve from the Barreto-Naehrig family, and on their respective analogues in genus 2.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/83830154 (1).pdf`
- `downloads/83830154 (2).pdf`
- `downloads/83830154 (3).pdf`
- `downloads/83830154 (4).pdf`
- `downloads/83830154 (5).pdf`
- `downloads/83830154.pdf`
