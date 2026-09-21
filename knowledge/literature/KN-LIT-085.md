---
id: KN-LIT-085
type: literature
title: A remark concerning m-divisibility and the discrete logarithm in the divisor class group of curves
authors: [Frey Gerhard, Rueck Hans-Georg]
year: 1994
venue: Mathematics of Computation, 62(206):865-874
identifiers:
  eprint: null
  doi: 10.1090/S0025-5718-1994-1218343-6
  url: https://doi.org/10.1090/s0025-5718-1994-1218343-6
tags: [frey-ruck, tate-pairing, embedding-degree, transfer, divisor-class-group, jacobian, higher-genus, special-curves, ecdlp, hygiene]
confidence: established
citation_verified: web
added: 2026-07-24
superseded_by: null
---

## Contribution
The Frey-Rück (or Tate-pairing) transfer. Using a variant of the tame Tate
pairing for abelian varieties over local fields, the discrete logarithm in the
m-torsion of the divisor class group of a curve X over a finite field k_0 is
reduced to a discrete logarithm in k_0(zeta_m)^*. This generalizes the MOV
reduction (KN-LIT-084) beyond elliptic curves to Jacobians of arbitrary genus,
and does so with the Tate rather than the Weil pairing -- which in practice is
cheaper and does not require the full m-torsion to be rational.

## Key claims (as reported)
- The DLP in the m-torsion part of Pic^0(X) over a finite field (char prime to
  m), or over a local field with that residue field, reduces to the DLP in
  k_0(zeta_m)^* (proven).
- The same machinery decides which linear combinations of a finite set of
  divisor classes are divisible by m.
- The required extension degree is the least k with m | q^k - 1, i.e. the
  embedding degree; the attack is only effective when that k is small.

## Relevance to this program
Together with KN-LIT-084 this closes the "transfer to a field DLP" direction as
a novelty route: the reduction exists, is classical, and its cost is governed
entirely by the embedding degree, which for a random ordinary curve is of size
comparable to q (KN-LIT-086). It also generalizes the boundary to higher genus,
which matters when the program considers Weil-restriction or cover routes
(KN-LIT-007, KN-LIT-090) that move an elliptic instance into a Jacobian: the
Frey-Rück pairing is the reason such a move must be checked for an accidental
small embedding degree in the target. See KN-TECH-032.

## Not verified here
The AMS DOI landing page (including the paper's abstract and opening sections)
was fetched; the complete article was not read. Authors, title, venue
(Math. Comp. 62(206):865-874, 1994) and both DOIs (10.1090/S0025-5718-1994-1218343-6,
and the JSTOR record 10.2307/2153546) were confirmed. The pairing-theoretic
proof was not re-derived; the standard status of the reduction is why
confidence is `established`.
