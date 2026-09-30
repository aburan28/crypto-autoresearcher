---
id: KN-TECH-a7e9a8
type: technique
title: >-
  Point-relation trapdoor (Dual EC DRBG) -- a sound curve with two published points Q = dP whose secret scalar d lets the holder recover generator state from output
tags: [trapdoor, dual-ec, drbg, point-relation, shumow-ferguson, nist-sp-800-90, kleptography, protocol-level, ecdlp]
confidence: reported
complexity: >-
  holder recovers the internal state from one 30-byte output block with about 2^16 candidate-point trials (the truncation) plus one scalar multiplication by d; outsider must solve the DLP of Q to base P on P-256
applicability: >-
  any protocol that fixes two or more curve points whose discrete-log relation is unknown to the public and whose security argument silently assumes the relation is unknown to everyone (Dual EC, but also any second generator in a commitment or proof system, see KN-TECH-c3a5e4)
source_refs: [KN-LIT-3476, KN-LIT-5546, KN-LIT-2923, KN-TECH-6ead00, KN-TECH-c3a5e4, KN-TECH-257dbc]
added: 2026-09-30
superseded_by: null
---

## Mechanism

Dual EC DRBG (NIST SP 800-90A, 2006) iterates `s_{i+1} = x(s_i * P)` and
outputs `r_i = x(s_i * Q)` truncated by 16 bits, with `P`, `Q` fixed points on
P-256. Shumow and Ferguson (CRYPTO 2007 rump session; the full analysis is
KN-LIT-3476) observed that if `Q = dP` with `d` known, then from one output
`r_i` the holder lifts the (about `2^16`) candidate points `R` with
`x(R) = r_i`, computes `e * R` with `e = d^{-1} mod n`; for the correct
candidate `R = s_i * Q` this equals `s_i * P`, whose x-coordinate is the
next state, so all future output is recovered. KN-LIT-5546 shows the attack is practical
against deployed TLS stacks.

## The trapdoor, precisely

- The **curve** (P-256) is sound; the ECDLP is not attacked.
- The **secret** is the relation `Q = dP`. To the public, `log_P Q` is an
  ECDLP instance; to the holder it is a stored scalar.
- The **hiding** is perfect in the sense of the hiding criterion
  (KN-TECH-6ead00): no public invariant of `(P, Q)` reveals `d`, and the
  only public test is to solve the DLP.

## Detectability

Undetectable from the parameters alone. The public evidence that the
relation was known to the designer is historical (the option to generate
one's own `Q` was added to the standard, and its use disabled by default in
deployed products), not mathematical.

## Applicability limits

It is a protocol trapdoor, not an ECDLP trapdoor: it leaks *state*, and the
attack is only as strong as the protocol's dependence on the second point.
A protocol that uses a single generator, or derives its second generator by
hash-to-curve from a public string, is immune.

## Relevance

Two reasons it belongs in an ECDLP corpus. First, it is the canonical example
of the "sound curve, trapdoored constant" pattern that every review of
multi-point protocols must check (generalized in KN-TECH-c3a5e4). Second, its
secret `d` *is* a hidden discrete logarithm, so any ECDLP advance moves the
public from "cannot verify" to "can verify": the program's own claim tiers
(docs/claims-and-verification.md) would treat a recovery of `log_P Q` on a
real standard's constants as a real-curve claim requiring the breakthrough
review tier.
