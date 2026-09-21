---
id: KN-LIT-138
type: literature
title: Efficient Algorithms for Solving Overdefined Systems of Multivariate Polynomial Equations
authors: [Courtois Nicolas T, Klimov Alexander, Patarin Jacques, Shamir Adi]
year: 2000
venue: 'Advances in Cryptology - EUROCRYPT 2000, pages 392-407, Springer'
identifiers:
  eprint: null
  doi: 10.1007/3-540-45539-6_27
  url: https://www.iacr.org/archive/eurocrypt2000/1807/18070398-new.pdf
tags: [mq, multivariate-quadratic, xl, relinearization, overdetermined, polynomial-system, groebner, np-hard, solving, foundational, index-calculus]
confidence: established
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
Introduces the **XL** (eXtended Linearization) algorithm and related
relinearization techniques for solving overdefined systems of multivariate
quadratic equations. The motivating observation is that many cryptosystems rest
on the difficulty of solving large multivariate quadratic systems, that the
problem is NP-hard over any field, and that when the number of equations equals
the number of unknowns the best known approaches were exhaustive search over small
fields and Groebner basis methods over large ones. XL targets the **overdefined**
regime, where more equations than unknowns make the problem easier than the
square case.

## Key claims (as reported)
- Solving multivariate quadratic systems is NP-hard over any field.
- For `m = n` the prior state of the art was exhaustive search (small fields) or
  a Groebner basis algorithm (large fields).
- Overdefined systems (`m` substantially greater than `n`) admit better
  algorithms; XL multiplies the original equations by monomials and then
  linearises the enlarged system.

## Relevance to this program
The origin point of the algorithm family the ICI thread's headline number comes
from, and the corpus had no entry for any of it — greps for `XL`, `MQ`,
`crossbred` and `mutant` all returned zero across 190 entries before this batch.

The connection to the program's main line is structural, not incidental.
Point-decomposition index calculus (`KN-TECH-003`) reduces relation-finding to
solving a polynomial system derived from a summation polynomial
(`KN-TECH-002`), so the achievable index-calculus exponent is a function of the
polynomial-system solver used. The corpus documented the Groebner route
thoroughly (`KN-LIT-026`-`029`, `KN-TECH-004`, `KN-TECH-011`) and the XL/MQ route
not at all, which meant one of the two solver families the program's own
experiments compare had no prior art recorded.

## Not verified here
Verification was by web search surfacing primary-index listings (DBLP
`conf/eurocrypt/CourtoisKPS00`, Springer DOI 10.1007/3-540-45539-6_27, EUROCRYPT
2000 pp. 392-407, an IACR archive PDF path, and a Weizmann publication record);
direct fetches returned HTTP 403 under this session's egress policy. The LNCS
volume number is suggested by the IACR archive path but was not confirmed and is
omitted. `confidence: established` reflects XL's textbook status, not a reading
performed here.

NOT verified here: XL's precise formulation, the conditions under which it
terminates, its complexity analysis, and its relationship to Groebner methods —
all of which have been the subject of substantial subsequent debate that this
entry does not record.
