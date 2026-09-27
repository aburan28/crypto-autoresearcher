---
id: KN-LIT-f0a590
type: literature
title: A Forgery Attack against Frobenius-UOV
authors:
- Augustin Bariant
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/1927
identifiers:
  eprint: iacr:2026/1927
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/1927
source:
  citation: Augustin Bariant. A Forgery Attack against Frobenius-UOV. Cryptology ePrint Archive 2026/1927, 2026.
  url: https://eprint.iacr.org/2026/1927
tags:
- frobenius-uov
- multivariate
- forgery
- linearized-resultant
- finite-field
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

Specific public exponents in Frobenius-UOV permit a six-term univariate forgery equation to be reduced to two low-degree bivariate equations and solved with a linearized resultant, without the secret key. Under heuristic success-probability assumptions, the authors estimate soft-O(e*p^6) field operations, approximately 2^45, 2^52 and 2^53 field operations for the claimed 128-, 192- and 256-bit instances.

## Scope and evidence boundary

This is specific to Frobenius-UOV exponent choices, not to the Frobenius endomorphism in ECDLP or to UOV/SNOVA generally. The reported field-operation counts are heuristic estimates, not published full-instance forgeries in the abstract.

## Research follow-up

Implement small-instance signature verification and instrument average successful forgery cost against the original and modified exponent sets.

Source: [https://eprint.iacr.org/2026/1927](https://eprint.iacr.org/2026/1927); ePrint received 2026-09-08. Abstract and metadata read on 2026-09-26; result not reproduced.
