---
id: KN-LIT-90e34c
type: literature
title: "Security Analysis of the Strong Diffie-Hellman Problem"
authors:
  - "Jung Hee Cheon"
year: 2006
venue: "Advances in Cryptology -- EUROCRYPT 2006, LNCS 4004, pp. 1-11"
identifiers:
  eprint: null
  doi: "10.1007/11761679_1"
  arxiv: null
  url: "https://link.springer.com/chapter/10.1007/11761679_1"
tags: [cheon, auxiliary-input, strong-diffie-hellman, q-sdh, group-order, n-minus-one, n-plus-one, generic, baseline, ecdlp]
confidence: reported
citation_verified: web
added: "2026-10-01"
superseded_by: null
---

## Contribution

Shows that the discrete logarithm with **auxiliary inputs** is strictly
easier than the plain DLP when the group order has a conveniently sized
divisor near it. For `g` of prime order `p`:

- Given `g, g^alpha, g^(alpha^d)` with `d | p - 1`, the secret `alpha` is
  recovered in `O(log p * (sqrt(p/d) + sqrt(d)))` group operations with
  memory `O(max(sqrt(p/d), sqrt(d)))`.
- Given `g^(alpha^i)` for `i` up to `2d` with `d | p + 1`, recovery costs
  `O(log p * (sqrt(p/d) + d))`.

The paper applies the attack to Boldyreva's blind signature and to an
ElGamal-type scheme whose security rests on a strong Diffie-Hellman
(`q`-SDH) assumption. The journal version, "Discrete Logarithm Problems
with Auxiliary Inputs" (J. Cryptology 23(3), 2010), is reported but was not
retrieved here.

## Key claims (as reported from the publisher abstract)

- The complexity drops from `O(sqrt(p))` to about `O(sqrt(p/d))` whenever
  the protocol exposes the `d`-th power of the secret in the exponent and
  `d` divides `p - 1` (or, with more inputs, `p + 1`).
- The attack is generic: it uses only the group law and the structure of
  `F_p^*` (resp. the norm-one subgroup of `F_{p^2}^*`), so it applies to
  elliptic-curve groups unchanged.

## Relevance to this program

Primary source for `KN-TECH-febb4f` (Cheon-friendly group orders as a
standardizer's lever) and the "Cheon divisors" entry in the public-invariant
list of `KN-TECH-6ead00`. It is also the model the ECTD briefing names for
the "trapdoor DDH first" route (private auxiliary inputs plus Cheon-style
acceleration) in `GOAL-ECTD-001`. For the program's generic baseline
(`KN-TECH-005`) it is the standard example of how extra oracle outputs move
the `sqrt(n)` bound without breaking the generic model.
