---
id: KN-LIT-867
type: literature
title: "Extending the GLS endomorphism to speed up GHS Weil descent using Magma Jesús-Javier Chi-Domı́nguezb,a,, Francisco Rodrı́guez-Henrı́quezb,a,1, Benjamin Smithc,2"
authors: []
year: 2021
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2106.09967"
  url: "https://arxiv.org/abs/2106.09967"
tags: [binary-field, dlp, elliptic-curve, endomorphism, extension-field, glv-gls, hyperelliptic, index-calculus, isogeny, jacobian, pollard-rho, weil-descent]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Let q = 2n , and let E/Fql be a generalized Galbraith–Lin–Scott (GLS) binary curve, with l ≥ 2 and (l, n) = 1. We show that the GLS endomorphism on E/Fql induces an efficient endomorphism on the Jacobian JacH (Fq ) of the genus-g hyperelliptic curve H corresponding to the image of the GHS Weil-descent attack applied to E/Fql , and that this endomorphism yields a factor-n speedup when using standard index-calculus procedures for solving the Discrete Logarithm Problem (DLP) on JacH (Fq ).

## Key claims (as reported)
- Our analysis is backed up by the explicit computation of a discrete logarithm defined on a prime-order subgroup of a GLS elliptic curve over the field F25·31 .
- A Magma implementation of our algorithm finds the aforementioned discrete logarithm in about 1, 035 CPU-days.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2106.09967v1 (1).pdf`
- `downloads/2106.09967v1.pdf`
