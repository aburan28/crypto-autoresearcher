---
id: KN-LIT-009
type: literature
title: New algorithm for the discrete logarithm problem on elliptic curves
authors: [Semaev Igor]
year: 2015
venue: IACR Cryptology ePrint Archive
identifiers:
  eprint: iacr:2015/310
  doi: null
  url: https://eprint.iacr.org/2015/310
tags: [semaev, summation-polynomial, index-calculus, prime-field, ecdlp, complexity]
confidence: reported
citation_verified: web
added: 2026-07-19
superseded_by: null
---

## Contribution
Proposes a newer summation-polynomial-based approach aiming at improved
complexity for ECDLP, with analysis of the probability that random points
decompose over a chosen factor base and the resulting relation-collection cost.

## Key claims (as reported)
- Presents heuristic complexity arguments for the decomposition approach;
  claims of this style have drawn scrutiny and are contested in the community.
- Treats the factor-base decomposition probability as the central quantity.

## Relevance to this program
Directly relevant to any factor-base-design or decomposition-probability
proposal. Because its complexity claims are contested, treat cited numbers as
`reported` and controversial; an experiment measuring decomposition
probability vs. factor-base size is a legitimate replication/audit target.

## Not verified here
Full paper not read; the standing of its complexity claims summarized from
general community reception, flagged for careful reading before reliance.
