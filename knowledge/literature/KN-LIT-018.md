---
id: KN-LIT-018
type: literature
title: The Tate pairing via elliptic nets
authors: [Stange Katherine E.]
year: 2007
venue: Pairing-Based Cryptography (Pairing) 2007, LNCS 4575, pp. 329-348
identifiers:
  eprint: iacr:2006/392
  doi: 10.1007/978-3-540-73489-5_19
  url: https://eprint.iacr.org/2006/392
tags: [elliptic-nets, elliptic-divisibility-sequence, eds, tate-pairing, recurrence, representation, ecdlp]
confidence: reported
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
Introduces *elliptic nets*: maps from Z^n to a ring satisfying a nonlinear
recurrence, generalizing elliptic divisibility sequences (EDS) to multiple
ranks. Derives a formula for the Tate pairing on an elliptic curve over a
finite field in terms of net values, computable in linear time via the
recurrence (the "elliptic net algorithm").

## Key claims (as reported)
- Net values recompute the Tate/Weil pairing; the net is an algebraic map on the
  curve driven by a Somos-type quadratic recurrence.
- Foundations: Ward, "Memoir on elliptic divisibility sequences," Amer. J. Math.
  70(1):31-74, 1948 (rank-1 EDS from division polynomials); Shipsey, "Elliptic
  divisibility sequences," PhD thesis, Goldsmiths, Univ. of London, 2000 (EDS
  applied to ECDLP); Stange, "Elliptic nets and elliptic curves," Algebra &
  Number Theory 5(2):197-229, 2011 (arXiv:0710.1316, doi:10.2140/ant.2011.5.197)
  -- the multi-rank algebraic-geometry foundation.

## Relevance to this program
The representation underlying the program's elliptic-net candidate (RQ-NET-001,
EXP-NET-001): re-encode ECDLP in the net domain and test whether Somos identities
supply relations below the birthday bound. CRITICAL scoping caveat, per the
program's own literature search: nets were built to *compute* pairings, and *no
sub-rho EDS/net DLOG mechanism is known* -- the likely obstruction is that Somos
identities are universal (hold for every k), so restricted to a k-fiber they may
yield only tautologies simulable in the generic group model (KN-LIT-011,
KN-OPEN-005). The entry records the representation, not an advantage.

## Not verified here
Full paper not read; the net/pairing construction and the EDS lineage are
relayed from the ePrint abstract and secondary sources. Ward's JSTOR DOI could
not be confirmed and is omitted (vol/issue/pages cross-checked); Shipsey's year
is cited as 2000/2001 across sources. Fields confirmed against IACR ePrint /
publisher records via search, not by fetching the primary pages.
