---
id: KN-LIT-087
type: literature
title: Evaluation of discrete logarithms in a group of p-torsion points of an elliptic curve in characteristic p
authors: [Semaev Igor A.]
year: 1998
venue: Mathematics of Computation, 67(221):353-356
identifiers:
  eprint: null
  doi: 10.1090/S0025-5718-98-00887-4
  url: https://www.ams.org/journals/mcom/1998-67-221/S0025-5718-98-00887-4/
tags: [anomalous, trace-one, p-torsion, additive-transfer, polynomial-time, special-curves, prime-field, ecdlp, hygiene]
confidence: established
citation_verified: web
added: 2026-07-24
superseded_by: null
---

## Contribution
The first of the three independent anomalous-curve attacks. Semaev constructs
an explicit isomorphism from the order-p subgroup of an elliptic curve over a
field of characteristic p onto the *additive* group of that field, and shows
its values can be evaluated cheaply. Since discrete logarithms in an additive
group are a single division, the ECDLP collapses.

## Key claims (as reported)
- The DLP in a subgroup of order p of an elliptic curve over a finite field of
  characteristic p requires O(ln p) field operations (proven).
- The mechanism is an isomorphism phi from the p-torsion subgroup to (F_q, +);
  given Q = nP one recovers n = phi(Q) * phi(P)^{-1}.

## Relevance to this program
Anomalous curves (#E(F_p) = p, trace of Frobenius one) are the sharpest
counterexample to "ECDLP is generically square-root hard": here the problem is
linear time, and the reason is that the group has a *non-generic
representation* as an additive group. This is directly load-bearing for
KN-OPEN-005, which asks whether a non-generic representation can supply
k-dependent information below the birthday bound. The anomalous case proves
the answer is yes in general -- but only when the curve order coincides with
the field characteristic, a measure-zero condition that any parameter check
rejects. The program's screening rule follows: a proposed representation-based
mechanism must state why it is not simply rediscovering the additive transfer
on a curve class where it applies. Companion papers KN-LIT-088 (Satoh-Araki)
and KN-LIT-089 (Smart). See KN-TECH-033.

## Not verified here
Full paper not fetched. Author, title, venue (Math. Comp. 67(221):353-356,
1998), DOI and MathSciNet review MR1432133 confirmed against the AMS journal
page; the abstract and the isomorphism statement quoted above were read from
that page. The construction of phi was not re-derived. Note the AMS record also
lists a later remark by Rück on a related Semaev paper, which was not consulted.
