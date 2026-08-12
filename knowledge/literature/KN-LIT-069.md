---
id: KN-LIT-069
type: literature
title: CSIDH - An Efficient Post-Quantum Commutative Group Action
authors: [Castryck Wouter, Lange Tanja, Martindale Chloe, Panny Lorenz, Renes Joost]
year: 2018
venue: ASIACRYPT 2018, LNCS 11274, pp. 395-427
identifiers:
  eprint: iacr:2018/383
  doi: 10.1007/978-3-030-03332-3_15
  url: https://eprint.iacr.org/2018/383
tags: [csidh, class-group-action, commutative, supersingular, prime-field, key-exchange, hidden-shift, post-quantum, adjacent]
confidence: established
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
An efficient commutative group action for non-interactive post-quantum key
exchange: the ideal class group of an imaginary quadratic order acts on
supersingular elliptic curves defined over a large PRIME field F_p (not F_{p^2}).
Follows the Couveignes-Rostovtsev-Stolbunov layout (KN-LIT-070) but in the
supersingular/prime-field setting for efficiency.

## Key claims (as reported)
- Diffie-Hellman-like scheme with ~64-byte public keys at a conjectured NIST
  category-I level; cheap public-key validation.
- NOT affected by the 2022 SIDH break (publishes no torsion-point images), but as
  a commutative group action / abelian hidden-shift instance it is subject to
  Kuperberg-style quantum subexponential attack (KN-LIT-071), which drives its
  parameter sizing (KN-OPEN-014).

## Relevance to this program
The commutative-group-action branch of isogeny crypto that SURVIVED the SIDH
break. Its class-group action on supersingular curves and the underlying volcano /
orientation structure connect directly to the program's isogeny / volcano-
orientation research (RQ-ISO-001, ISO-AR). Adjacent to the ECDLP mission; the
class-group action is CM-theoretic, kin to the program's CM-endomorphism work.

## Not verified here
Full paper not read; the group action and key sizes are textbook-level in isogeny
cryptography (hence confidence: established). Fields confirmed against IACR ePrint
2018/383 and the Springer DOI via search, not by fetching the primary pages.
