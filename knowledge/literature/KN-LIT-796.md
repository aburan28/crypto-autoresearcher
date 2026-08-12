---
id: KN-LIT-796
type: literature
title: "On Index Calculus Algorithms for Subfield Curves"
authors:
  - "Steven D. Galbraith"
  - "Robert Granger"
  - "Simon-Philipp Merz"
  - "Christophe Petit"
year: 2020
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2020/1315"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2020/1315"
tags: [complexity-theory, dlp, ecdlp, elliptic-curve, endomorphism, extension-field, factoring, finite-field, index-calculus, pollard-rho, protocol, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we further the study of index calculus methods for solving the elliptic curve discrete logarithm problem (ECDLP). We focus on the index calculus for subfield curves, also called Koblitz curves, defined over Fq with ECDLP in Fqn .

## Key claims (as reported)
- Instead of accelerating the solution of polynomial systems during index calculus as was predominantly done in previous work, we define factor bases that are invariant under the q-power Frobenius automorphism of the field Fqn , reducing the number of polynomial systems that need to be solved.
- A reduction by a factor of 1/n is the best one could hope for.
- We show how to choose factor bases to achieve this, while simultaneously accelerating the linear algebra step of the index calculus method for Koblitz curves by a factor n2 .
- Furthermore, we show how to use the Frobenius endomorphism to improve symmetry breaking for Koblitz curves.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2020-1315.pdf`
