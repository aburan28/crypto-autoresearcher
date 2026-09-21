---
id: KN-LIT-5597
type: literature
title: "On the Static Diffie-Hellman Problem on Elliptic Curves over Extension Fields"
authors:
  - "Robert Granger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, elliptic-curve, extension-field, hyperelliptic, index-calculus, jacobian, provable-security, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show that for any elliptic curve E(Fqn ), if an adversary has access to a Static Diffie-Hellman Problem (Static DHP) oracle, then 1 by making O(q 1− n+1 ) Static DHP oracle queries during an initial learning phase, for fixed n > 1 and q → ∞ the adversary can solve any further 1 instance of the Static DHP in heuristic time Õ(q 1− n+1 ). Our proposal also solves the Delayed Target DHP as defined by Freeman, and naturally extends to provide algorithms for solving the Delayed Target DLP, the One-More DHP and One-More DLP, as studied by Koblitz and Menezes in the context of Jacobians of hyperelliptic curves of small genus.

## Key claims (as reported)
- We also argue that for any group in which index calculus can be effectively applied, the above problems have a natural relationship, and will always be easier than the DLP.
- While practical only for very small n, our algorithm reduces the security provided by the elliptic curves defined over Fp2 and Fp4 proposed by Galbraith, Lin and Scott at EUROCRYPT 2009, should they be used in any protocol where a user can be made to act as a proxy Static DHP oracle, or if used in protocols whose security is related to any of the above problems.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/6477285 (1).pdf`
- `downloads/6477285 (2).pdf`
- `downloads/6477285 (3).pdf`
- `downloads/6477285.pdf`
