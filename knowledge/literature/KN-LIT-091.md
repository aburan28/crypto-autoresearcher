---
id: KN-LIT-091
type: literature
title: A Key Recovery Attack on Discrete Log-based Schemes Using a Prime Order Subgroup
authors: [Lim Chae Hoon, Lee Pil Joong]
year: 1997
venue: Advances in Cryptology - CRYPTO '97, LNCS 1294, pp. 249-263
identifiers:
  eprint: null
  doi: 10.1007/BFb0052240
  url: https://doi.org/10.1007/bfb0052240
tags: [small-subgroup, lim-lee, key-recovery, oracle-attack, crt, parameter-validation, static-key, protocol, ecdlp-adjacent, hygiene]
confidence: established
citation_verified: web
added: 2026-07-24
superseded_by: null
---

## Contribution
The small-subgroup confinement attack. In a protocol working in a prime-order
subgroup of order q inside a larger group (typically Z_p^* with q | p-1), an
attacker who can submit group elements of small order and observe the result
of exponentiation by a static secret learns the secret modulo those small
orders. Repeating over the small prime factors and applying the Chinese
Remainder Theorem recovers part of, and often all of, the key.

## Key claims (as reported)
- Many published discrete-log protocols leak secret-key bits under this oracle
  attack unless received values are explicitly checked to lie in the intended
  prime-order subgroup.
- The attack recovers the whole secret in reasonable time for a range of
  Diffie-Hellman-type key exchanges and ElGamal encryption/signature variants.
- Two defences: validate subgroup membership on every received element
  (correct but costly), or use a "secure prime" p such that all prime factors
  of (p-1)/2q exceed q, which limits the leak to one bit.

## Relevance to this program
This is the protocol-layer twin of Pohlig-Hellman (KN-LIT-082): the group
order's small factors are exploitable not only when you own the instance but
when an adversary can steer an honest party into the small part. It is
recorded here for scope discipline rather than as an ECDLP mechanism -- the
program is academic and defensive, and its target is the plain ECDLP with no
oracle, no static-key reuse, and no attacker-chosen inputs. Any proposal whose
advantage requires querying a party with chosen points is operating in this
adjacent leakage model, not in the program's model, and must be classified as
such (compare KN-OPEN-011, which draws the same line for the Hidden Number
Problem). The elliptic-curve analogue is the invalid-curve attack, KN-LIT-092.
See KN-TECH-034.

## Not verified here
Full paper not fetched. Authors, title, venue (CRYPTO '97, LNCS 1294,
pp. 249-263, Springer) and DOI confirmed against the SpringerLink DOI record
and an independent bibliographic index; the abstract and the paper's own
conclusion paragraph (quoted for the two defences) were read from the DOI
landing page. The concrete leakage rates for individual named protocols were
not checked.
