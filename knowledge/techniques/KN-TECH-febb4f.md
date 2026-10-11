---
id: KN-TECH-febb4f
type: technique
title: >-
  Cheon-friendly group orders -- choosing n so that n-1 or n+1 has a divisor d of convenient size, making the DLP with auxiliary inputs cost sqrt(n/d) in protocols that expose P, aP, ..., a^d P
tags: [trapdoor, cheon, auxiliary-input, strong-diffie-hellman, group-order, n-minus-one, n-plus-one, bls, boneh-boyen, snark-setup, unchecked-weakness, ecdlp]
confidence: reported
complexity: >-
  given P, aP, ..., a^d P with d | n-1, recover a in O(sqrt(n/d) + sqrt(d)) group operations (Cheon 2006); with d | n+1 and inputs up to a^{2d} the same bound holds via the norm-one torus; against sqrt(n) for plain rho
applicability: >-
  protocols that publish consecutive powers of a secret in the exponent (Boneh-Boyen signatures and IBE, BLS-style q-SDH assumptions, KZG / SNARK structured reference strings of degree d); the standardizer's lever is the factorization of n +- 1, which is public
source_refs: [KN-TECH-6ead00, KN-TECH-005, KN-TECH-006]
added: 2026-09-30
superseded_by: null
---

## Mechanism (Cheon, EUROCRYPT 2006, "Security analysis of the strong Diffie-Hellman problem"; not yet a KN-LIT entry)

Let `G = <P>` have prime order `n` and let `d | n - 1`. Given `P, aP` and
`a^d P`, write `a = g^i` for a generator `g` of `F_n^*`. Then `a^d` lies in
the subgroup of order `(n-1)/d`, and a baby-step giant-step on `a^d P`
recovers `a^d` (hence `i mod (n-1)/d`) in `O(sqrt((n-1)/d))` operations; a
second baby-step giant-step of size `O(sqrt(d))` finishes. With `d | n + 1`
the same argument runs in the norm-one subgroup of `F_{n^2}^*` and needs
inputs up to `a^{2d} P`. The total is `O(sqrt(n/d) + sqrt(d))`, which is
`n^{1/3}` when `d ~ n^{1/3}` and `n^{1/4}` when `d ~ n^{1/2}` is available.

## As a standardizer's lever

The order `n` of a standard curve fixes `n - 1` and `n + 1`. A standardizer
who chooses `n` such that `n - 1` has a divisor near `n^{1/3}` (many random
`n` do; the choice is which ones to keep) hands every protocol that exposes
`d` consecutive powers a `sqrt(d)`-factor loss with no visible change to the
curve. The point is not that the standardizer *hides* anything; it is that
the choice is invisible to anyone who audits the curve but not the
protocols later built on it.

## Detectability

Fully public: factor `n - 1` and `n + 1`. For 256-bit `n` this is routine.
The check belongs in every parameter review of a group used under a q-type
assumption. Several deployed pairing curves (BN254, BLS12-381) have been
checked this way in the literature and have `n +- 1` with usable divisors,
which is one reason their SRS degrees are bounded.

## Applicability limits

- Needs the protocol to expose consecutive powers; plain ECDH, ECDSA and
  Schnorr expose only `aP`.
- The gain is polynomial in `d`; it never beats `n^{1/4}` and never becomes
  subexponential. It is an *unchecked weakness* in the taxonomy of
  KN-TECH-6ead00, not a hidden one.

## Relevance

The program's generic lower bound (KN-TECH-005) is stated for the plain DLP
oracle; Cheon's attack is the standard example of how additional oracle
outputs move the bound, and it is the model for the "trapdoor DDH first"
route the ECTD briefing lists as its weakest but nearest target.
