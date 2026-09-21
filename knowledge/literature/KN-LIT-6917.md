---
id: KN-LIT-6917
type: literature
title: "Symmetrized Summation Polynomials: Using Small Order Torsion Points to Speed up Elliptic Curve Index Calculus"
authors:
  - "Jean-Charles Faugère"
  - "Louise Huot"
  - "Antoine Joux"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, dlp, ecdlp, elliptic-curve, extension-field, finite-field, groebner, index-calculus, point-decomposition, semaev, summation-polynomial]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Decomposition-based index calculus methods are currently efficient only for elliptic curves E defined over non-prime finite fields of very small extension degree n. This corresponds to the fact that the Semaev summation polynomials, which encode the relation search (or “sieving”), grows over-exponentially with n.

## Key claims (as reported)
- Actually, even their computation is a first stumbling block and the largest Semaev polynomial ever computed is the 6-th.
- Following ideas from Faugère, Gaudry, Huot and Renault, our goal is to use the existence of small order torsion points on E to define new summation polynomials whose symmetrized expressions are much more compact and easier to compute.
- This setting allows to consider smaller factor bases, and the high sparsity of the new summation polynomials provides a very efficient decomposition step.
- In this paper the focus is on 2-torsion points, as it is the most important case in practice.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410158 (1).pdf`
- `downloads/84410158 (2).pdf`
- `downloads/84410158 (3).pdf`
- `downloads/84410158.pdf`
