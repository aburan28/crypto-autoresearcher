---
id: KN-LIT-3748
type: literature
title: "Extending the GHS Weil Descent Attack"
authors:
  - "S. D. Galbraith"
  - "F. Hess"
  - "N. P. Smart"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, ecdlp, elliptic-curve, finite-field, hyperelliptic, isogeny, jacobian, weil-descent]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we extend the Weil descent attack due to Gaudry, Hess and Smart (GHS) to a much larger class of elliptic curves. This extended attack applies to fields of composite degree over F2 .

## Key claims (as reported)
- The principle behind the extended attack is to use isogenies to find an elliptic curve for which the GHS attack is effective.
- The discrete logarithm problem on the target curve can be transformed into a discrete logarithm problem on the isogenous curve.
- A further contribution of the paper is to give an improvement to an algorithm of Galbraith for constructing isogenies between elliptic curves, and this is of independent interest in elliptic curve cryptography.
- We show that a larger proportion than previously thought of elliptic curves over F2155 should be considered weak.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/smart (1).pdf`
- `downloads/smart (2).pdf`
- `downloads/smart.pdf`
