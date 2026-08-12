---
id: KN-LIT-022
type: literature
title: Elliptic Curve Discrete Logarithm Problem over Small Degree Extension Fields
authors: [Joux Antoine, Vitse Vanessa]
year: 2013
venue: Journal of Cryptology, 26(1):119-143 (ePrint 2010)
identifiers:
  eprint: iacr:2010/157
  doi: 10.1007/s00145-011-9116-z
  url: https://eprint.iacr.org/2010/157
tags: [joux-vitse, index-calculus, extension-field, large-prime, groebner, f4, static-diffie-hellman, ecdlp]
confidence: reported
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
A variant of the Gaudry/Diem index-calculus method (KN-LIT-002, KN-LIT-003) for
the DLP on E(F_{q^n}) with small extension degree n. Uses Semaev-summation
point decomposition together with a *double-large-prime* variation to cut
relation-collection and linear-algebra cost, plus a new F4-style Grobner-basis
variant that substantially speeds the point-decomposition solves.

## Key claims (as reported)
- Improved overall asymptotic complexity in the regime log q <= c*n^3.
- Concrete record: an oracle-assisted resolution of the elliptic-curve *static*
  Diffie-Hellman problem over a 130-bit field with E(F_{q^5}).

## Relevance to this program
Defines the extension-field (small-degree) index-calculus regime and its record
scale, and is the origin of the double-large-prime cost model the program's
harvesting candidates reference (2LP occupancy, RT-1472/RT-1476). CRITICAL
scoping: these gains are *extension-field*; they do not transfer to prime fields
(KN-OPEN-001). A prime-field proposal must not silently borrow Joux-Vitse
asymptotics or its large-prime thresholds without re-deriving them over F_p.

## Not verified here
Full paper not read; the complexity regime and the 130-bit record relayed from
the ePrint abstract and secondary sources. Fields confirmed against IACR ePrint /
publisher records via search, not by fetching the primary pages.
