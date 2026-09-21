---
id: KN-LIT-025
type: literature
title: Algebraic Approaches for the Elliptic Curve Discrete Logarithm Problem over Prime Fields
authors: [Petit Christophe, Kosters Michiel, Messeng Ange]
year: 2016
venue: PKC 2016, LNCS 9615, pp. 3-18
identifiers:
  eprint: null
  doi: 10.1007/978-3-662-49387-8_1
  url: https://link.springer.com/chapter/10.1007/978-3-662-49387-8_1
tags: [petit-kosters-messeng, index-calculus, prime-field, point-decomposition, groebner, ecdlp, frontier]
confidence: reported
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
Adapts algebraic/index-calculus decomposition ideas -- developed for binary and
small-degree extension fields -- to the harder *prime-field* setting E(F_p).
Constructs a decomposition base and uses algebraic or rational maps meeting
specific conditions, reducing point decomposition to polynomial systems solved
by Grobner-basis methods, generalizing earlier extension-field attacks.

## Key claims (as reported)
- A prime-field decomposition/index-calculus construction, validated with
  computer experiments at small parameters.
- Explicitly hedged: practical only for small parameters (limited by
  understanding of Grobner-basis behavior); framed as flagging a *potential*
  prime-field vulnerability needing further study, NOT a practical attack.

## Relevance to this program
The most direct prior art for the program's CENTRAL regime: prime-field algebraic
ECDLP (KN-OPEN-001). Any prime-field decomposition proposal must be diffed
against this construction -- matching it is `known`/`adaptation`, not novel.
Establishes that the prime-field frontier is *active but unresolved*, and that
Grobner behavior is the bottleneck (KN-OPEN-002), precisely where the program's
own measurements (EXP-SEMAEV, EXP-DREG, BKK cluster) operate. Keeps prime-field
and extension-field claims (KN-LIT-022) strictly separated.

## Not verified here
Full paper not read; the construction, its small-parameter limitation, and the
authors' hedged framing relayed from the abstract and secondary sources. No IACR
ePrint located. Fields confirmed against the PKC/Springer record via search, not
by fetching the primary page.
