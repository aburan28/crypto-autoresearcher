---
id: KN-LIT-068
type: literature
title: The number of curves of genus two with elliptic differentials (Kani's theorem)
authors: [Kani Ernst]
year: 1997
venue: Journal fur die reine und angewandte Mathematik (Crelle), 485:93-122
identifiers:
  eprint: null
  doi: 10.1515/crll.1997.485.93
  url: https://eudml.org/doc/183547
tags: [kani, genus-two, abelian-surface, reducibility, glue-and-split, isogeny, sidh-attack, adjacent]
confidence: established
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
A genus-2 / elliptic-differential result characterizing when genus-2 curves have
Jacobians isogenous to products of elliptic curves. It underpins the
*reducibility* ("glue-and-split") criterion: whether an isogeny between products
of elliptic curves splits versus glues into a genus-2 Jacobian.

## Key claims (as reported)
- The reducibility criterion is the classical mathematical engine used by the 2022
  SIDH breaks to embed the secret isogeny into a reducible principally polarized
  abelian surface (KN-LIT-065) or higher-dimensional variety (KN-LIT-067).
- A 1997 arithmetic-geometry theorem, predating and independent of any
  cryptographic use.

## Relevance to this program
The mathematics that converts published torsion-point images into an exploitable
decomposable abelian-variety structure (KN-TECH-026). Recorded because the
program's cryptanalytic methodology centers on exactly this kind of
structure-exploitation; Kani's theorem is a clean example of a pure-math
reducibility result becoming a cryptanalytic tool. Adjacent to the ECDLP mission
(shares the abelian-variety / Jacobian machinery of the program's genus-2 / Prym
/ cover-transfer work).

## Not verified here
Full paper not read; the reducibility criterion is textbook-level in the isogeny-
attack literature (hence confidence: established). Fields confirmed against the
Crelle DOI and EUDML records via search, not by fetching the primary pages.
