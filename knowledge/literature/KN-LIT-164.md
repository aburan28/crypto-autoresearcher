---
id: KN-LIT-164
type: literature
title: "A double large prime variation for small genus hyperelliptic index calculus"
authors:
  - "P. Gaudry"
  - "E. Thomé"
  - "N. Thériault"
  - "C. Diem"
year: 2004
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2004/153"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2004/153"
tags: [dlp, elliptic-curve, factoring, finite-field, hyperelliptic, index-calculus, jacobian, pairing, pollard-rho]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this article, we examine how the index calculus approach for computing discrete logarithms in small genus hyperelliptic curves can be improved by introducing a double large prime variation. Two algorithms are presented.

## Key claims (as reported)
- The first algorithm is a rather natural adaptation of the double large prime variation to the intended context.
- On heuristic and experimental grounds, it seems to perform quite well but lacks a complete and precise analysis.
- Our second algorithm is a considerably simplified variant, which can be analyzed easily.
- The resulting complexity improves on the fastest known algorithms.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2004-153.pdf`
