---
id: KN-LIT-006
type: literature
title: Recent progress on the elliptic curve discrete logarithm problem
authors: [Galbraith Steven D., Gaudry Pierrick]
year: 2016
venue: Designs, Codes and Cryptography, 78(1):51-72
identifiers:
  eprint: iacr:2015/1022
  doi: 10.1007/s10623-015-0146-7
  url: https://eprint.iacr.org/2015/1022
tags: [survey, index-calculus, summation-polynomial, ecdlp, prime-field, extension-field, baseline]
confidence: reported
citation_verified: web
added: 2026-07-19
superseded_by: null
---

## Contribution
Survey of the state of ECDLP circa 2015: generic algorithms, index calculus
via summation polynomials, Weil-descent attacks, and the (lack of) progress
over prime fields. A primary orientation document for the program.

## Key claims (as reported)
- Over prime fields, no algorithm is known that beats generic square-root
  (Pollard rho) methods; the summation-polynomial approaches that help over
  extension fields do not translate to an advantage over GF(p).
- The bottleneck for prime-field index calculus is the cost of the Gröbner /
  point-decomposition step, which does not scale favorably.

## Relevance to this program
The single best "what is already known / already ruled out" reference for
novelty checks. Use it to classify prime-field proposals: matching a surveyed
dead-end is `known`. Grounds the program's central open question (KN-OPEN-001).

## Not verified here
Full survey not read end-to-end; summary claims relayed from abstract and the
program's general familiarity, flagged for deeper reading before any claim
leans on a specific section.
