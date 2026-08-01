---
id: KN-LIT-026
type: literature
title: An Algorithm for Finding the Basis Elements of the Residue Class Ring of a Zero-Dimensional Polynomial Ideal (Buchberger's thesis)
authors: [Buchberger Bruno]
year: 1965
venue: PhD thesis, Univ. Innsbruck; English transl. J. Symbolic Computation 41(3-4):475-511 (2006)
identifiers:
  eprint: null
  doi: 10.1016/j.jsc.2005.09.007
  url: https://www.sciencedirect.com/science/article/pii/S0747717105001483
tags: [groebner-basis, buchberger, s-polynomial, elimination, polynomial-system, solving, foundational]
confidence: established
citation_verified: web
added: 2026-07-22
superseded_by: null
---

## Contribution
The founding work of Grobner basis theory. Defines a Grobner basis as a
canonical generating set of a polynomial ideal w.r.t. a monomial order, and
gives the *completion algorithm*: repeatedly form S-polynomials of pairs of
generators, reduce modulo the current basis, and adjoin any nonzero remainder
until all S-polynomials reduce to zero. With an elimination (lex) order this
triangularizes the system, so polynomial systems can be solved.

## Key claims (as reported)
- Termination and correctness of the completion algorithm (Buchberger's
  criterion: basis complete iff all S-polynomials reduce to 0).
- Elimination-order Grobner bases give the algebraic backbone for solving
  multivariate polynomial systems.
- Citable modern forms: the 2006 JSC English translation (Abramson, transl.);
  the survey Buchberger, "Grobner Bases: An Algorithmic Method in Polynomial
  Ideal Theory," in Bose (ed.), Multidimensional Systems Theory, Reidel 1985,
  pp. 184-232.

## Relevance to this program
Every algebraic ECDLP point-decomposition attack ultimately computes a Grobner
basis of the Semaev summation system (KN-TECH-002, KN-TECH-004): this is the
primitive on which all downstream F4/F5 speedups (KN-LIT-027, KN-LIT-028) and
the whole solving-degree complexity debate (KN-OPEN-002) are built. The cost is
dominated by the highest degree reached, which motivates the first-fall /
degree-of-regularity analyses.

## Not verified here
Full thesis not read; the S-polynomial completion algorithm is textbook-level
and reconstructible (hence confidence: established). Bibliographic fields
confirmed against the JSC/Elsevier DOI record via search, not by fetching the
primary page.
