---
id: KN-LIT-046
type: literature
title: Factoring polynomials with rational coefficients (the LLL algorithm)
authors: [Lenstra Arjen K., Lenstra Hendrik W. Jr., Lovasz Laszlo]
year: 1982
venue: Mathematische Annalen, 261(4):515-534
identifiers:
  eprint: null
  doi: 10.1007/BF01457454
  url: https://link.springer.com/article/10.1007/BF01457454
tags: [lattice-reduction, lll, svp, coppersmith, cryptanalysis, foundational]
confidence: established
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Introduces the LLL algorithm: given a lattice basis, in polynomial time produce a
"reduced" basis whose first vector is provably within a 2^{(n-1)/2} factor of the
shortest nonzero vector. Applied to give the first polynomial-time algorithm for
factoring univariate polynomials over the rationals.

## Key claims (as reported)
- Polynomial-time approximate-SVP with a 2^{O(n)} approximation factor; in
  practice the output is far better than the worst-case guarantee.
- Foundational for lattice cryptanalysis, Coppersmith's small-root method
  (KN-LIT-037), integer programming in fixed dimension, and simultaneous
  Diophantine approximation.

## Relevance to this program
The base-case reduction engine underneath every lattice attack the corpus
records: BKZ with block size 2 IS LLL (KN-LIT-047), and the Coppersmith and
(EC)DSA-HNP attacks (KN-LIT-037, KN-LIT-043, KN-LIT-044) call LLL directly. This
is the primitive that makes the lattice/ECDLP intersection (KN-TECH-019)
computationally effective; it is not itself an ECDLP attack.

## Not verified here
Full paper not read; the LLL guarantee is textbook-level (hence confidence:
established). Bibliographic fields confirmed against the Math. Ann. / Springer
DOI and EUDML records via search, not by fetching the primary page.
