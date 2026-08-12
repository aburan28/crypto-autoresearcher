---
id: KN-LIT-020
type: literature
title: The Xedni Calculus and the Elliptic Curve Discrete Logarithm Problem
authors: [Silverman Joseph H.]
year: 2000
venue: Designs, Codes and Cryptography, 20(1):5-40
identifiers:
  eprint: null
  doi: 10.1023/A:1008319518035
  url: https://link.springer.com/article/10.1023/A:1008319518035
tags: [xedni, lift, mordell-weil, rational-points, ecdlp, dead-end, novelty-check]
confidence: reported
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
Proposes the "xedni" calculus ("index" reversed), a conceptual reversal of index
calculus for ECDLP. Instead of collecting relations over a factor base, one
lifts several points from E(F_p) to rational/integer coordinates and chooses a
curve E/Q through them, arranging (Mestre-style) for small Mordell-Weil rank so
the lifted points are linearly dependent over Q; reducing that dependence mod p
would yield the discrete-log relation, in principle solving one instance without
a subexponential relation-collection phase.

## Key claims (as reported)
- Presented as a *candidate* algorithm whose practicality is uncertain and
  explicitly open to analysis -- not a demonstrated break.
- Trades the relation-collection phase for a single global-lift construction.

## Relevance to this program
The canonical "reverse index calculus" / global-lift idea and a standard
novelty-check reference. Its companion analysis (KN-LIT-021) makes it a
documented DEAD END: any prime-field proposal that lifts to Q / uses rational
points (e.g. the function-field xedni / Mordell-Weil-lattice candidate
EXP-XEDN-001) is matching known-refuted territory unless it demonstrably changes
the lift-success scaling. Keep it to classify such proposals as `known`.

## Not verified here
Full paper not read; the mechanism is relayed from the abstract and secondary
sources. Fields confirmed against the DCC publisher record via search, not by
fetching the primary page.
