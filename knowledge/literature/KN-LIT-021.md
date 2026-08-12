---
id: KN-LIT-021
type: literature
title: Analysis of the Xedni Calculus Attack
authors: [Jacobson Michael J., Koblitz Neal, Silverman Joseph H., Stein Andreas, Teske Edlyn]
year: 2000
venue: Designs, Codes and Cryptography, 20(1):41-64
identifiers:
  eprint: null
  doi: 10.1023/A:1008312401197
  url: https://link.springer.com/article/10.1023/A:1008312401197
tags: [xedni, lift, ecdlp, dead-end, negative-result, novelty-check]
confidence: reported
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
Analyzes the practicality of Silverman's xedni attack (KN-LIT-020) and reaches a
negative conclusion: asymptotically the algorithm is "virtually certain to
fail," and even at small parameters the odds against finding a suitable lifting
are prohibitive.

## Key claims (as reported)
- The failure is driven by an absolute bound on the size of the coefficients of
  any relation the lifted points can satisfy, so a usable global dependence
  almost never exists as p grows.
- Supported experimentally, not by asymptotic argument alone; conclusion: xedni
  is not faster than existing methods and poses no threat to ECDLP cryptography.

## Relevance to this program
The authoritative "why lift-to-Q attacks fail" reference. Directly usable as the
known-dead-end citation when screening novelty of global-lift / rational-point /
Mordell-Weil proposals (e.g. the function-field xedni candidate EXP-XEDN-001):
such a proposal must show its lift-success probability decays strictly slower
than the bound established here, or it is proposing into refuted territory.

## Not verified here
Full paper not read; the coefficient-bound argument and experimental conclusion
relayed from the abstract and secondary sources. Fields confirmed against the DCC
publisher record via search, not by fetching the primary page.
