---
id: KN-LIT-19665f
type: literature
title: "Solving the Elliptic Curve Discrete Logarithm Problem Using Semaev Polynomials, Weil Descent and Gröbner Basis Methods - An Experimental Study"
authors:
  - "Michael Shantz"
  - "Edlyn Teske"
year: 2013
venue: "Number Theory and Cryptography (Buchmann Festschrift), LNCS 8260, pp. 94-107; ePrint 2013/596"
identifiers:
  eprint: "iacr:2013/596"
  arxiv: null
  doi: "10.1007/978-3-642-42001-6_7"
  url: null
tags: [index-calculus, binary-field, weil-descent, groebner, experimental, factor-base, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Experimental test of Petit-Quisquater's heuristics for binary ECDLP (Semaev polynomials + Weil descent + Groebner bases), including a variant that introduces intermediate variables to lower degrees. It is often quoted as validating the degree-of-regularity assumption on small parameters, with parameter ranges too small to settle asymptotics.

## Key claims (as reported)

- Experiments for n in {11,...,29}, m = 2 (per secondary summary); no sub-rho result at cryptographic size.

## Relevance to this program

Experimental study of Semaev + Weil descent + Gröbner for binary curves, including factor-base choices. Supersedes KN-LIT-010, which had this title and ePrint number but the authors of a different paper (HPST 2013). Must be cited by any binary PDP measurement paper (pdp-scaling, pdp-degree-heuristics, EV-ICPERF-784b25).

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-010 (bulk stub or misattributed entry; see that file's `superseded_by`).
