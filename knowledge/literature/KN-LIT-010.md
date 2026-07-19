---
id: KN-LIT-010
type: literature
title: Solving the elliptic curve discrete logarithm problem using Semaev polynomials, Weil descent and Groebner basis methods - an experimental study
authors: [Huang Yun-Ju, Petit Christophe, Shinohara Naoyuki, Takagi Tsuyoshi]
year: 2013
venue: IWSEC 2013 / IACR Cryptology ePrint Archive
identifiers:
  eprint: iacr:2013/596
  doi: null
  url: https://eprint.iacr.org/2013/596
tags: [experimental, semaev, weil-descent, groebner, first-fall-degree, binary-field, ecdlp, methodology]
confidence: reported
citation_verified: web
added: 2026-07-19
superseded_by: null
---

## Contribution
Experimental study of the summation-polynomial + Weil-descent + Gröbner-basis
pipeline for binary-field ECDLP, measuring the actual Gröbner behavior
(degrees, timings) against the heuristic first-fall-degree predictions.

## Key claims (as reported)
- Empirically probes whether the low-degree-of-regularity heuristic
  (cf. KN-LIT-005) holds at reachable sizes, and where the Gröbner step
  becomes the bottleneck.
- Highlights the gap between asymptotic heuristics and measured toy-scale cost.

## Relevance to this program
A methodological template: it is exactly the kind of bounded, artifact-
producing measurement study this harness formalizes. Use it to calibrate what
metrics (solving degree, first-fall degree, wall time vs. bit size) an
EXP-SEMAEV experiment should record, and to avoid re-running already-published
binary-field measurements without a new variable.

## Not verified here
Full paper not read; specific measured degrees/timings not extracted -- do so
before comparing the program's own measurements against this study.
