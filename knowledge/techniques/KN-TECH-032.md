---
id: KN-TECH-032
type: technique
title: Pairing transfers (MOV / Frey-Ruck) and the embedding degree
tags: [mov, frey-ruck, pairing, weil-pairing, tate-pairing, embedding-degree, transfer, supersingular, special-curves, genericity, ecdlp, hygiene]
confidence: established
complexity: subexponential in q^k once transferred (finite-field index calculus); the transfer itself is polynomial, so the attack is only useful for small embedding degree k
applicability: curves whose prime subgroup order l has small embedding degree (the least k with l dividing q^k - 1); always the case for supersingular curves (k <= 6), negligibly rare for random ordinary curves
source_refs: [KN-LIT-084, KN-LIT-085, KN-LIT-086, KN-TECH-005]
added: 2026-07-24
superseded_by: null
---

## Method
Let l be the prime order of the target subgroup and k the embedding degree,
the least k with l | q^k - 1. A bilinear pairing -- the Weil pairing in the
MOV formulation (KN-LIT-084), the Tate pairing in Frey-Rück (KN-LIT-085) --
maps the subgroup injectively into the l-th roots of unity in F_{q^k}^*. A
discrete logarithm in E(F_q) becomes a discrete logarithm in a finite field,
where index calculus is subexponential. The whole attack costs the pairing
evaluations plus a field DLP of size q^k, so it wins exactly when k is small.

## What it settles, and for which curves
This is the model case of a *structure transfer*: it does not improve the
generic bound, it exhibits curve families that are not generic. The
population statistics are what make it a closed question rather than an open
one. Balasubramanian and Koblitz (KN-LIT-086) show that l | (q^k - 1) is not
just necessary but sufficient in practice, and that for a random prime p and a
random curve over F_p with prime order, small k occurs with negligible
probability. Supersingular curves always have k <= 6; ordinary curves chosen
at random essentially never do. Pairing-friendly curves with small k exist but
are deliberately constructed for pairing-based protocols, not encountered by
accident.

For this program the consequence is a screening rule. GOAL-CRYPTO-001 targets
ordinary large-prime-order curves over prime fields, where the embedding degree
is of size comparable to p. Any proposal that transfers the ECDLP into a field
DLP is therefore `known` unless it supplies a mechanism that works at *large*
k, and a demonstration on a supersingular or pairing-friendly curve is out of
scope by construction, not merely weaker evidence.

## Applicability limits
The transfer preserves the DLP only when the pairing is non-degenerate on the
target subgroup; Frey-Rück additionally requires char(k_0) prime to m. The
generalization to Jacobians (KN-LIT-085) means a cover or Weil-restriction
route (KN-LIT-007, KN-LIT-090) must check the embedding degree of the *target*
Jacobian, since a transfer that lands somewhere with small k would be an
accidental win unrelated to the proposed mechanism. Nothing here applies to
anomalous curves, which are handled by an entirely different transfer
(KN-TECH-033).

## Verified vs reported
The reductions and the k <= 6 supersingular bound are textbook and proven in
their sources (confidence: established), but neither paper was read in full --
the claims are relayed from abstracts and publisher records, as recorded in
KN-LIT-084 and KN-LIT-085. The negligible-probability bound is quoted in
KN-LIT-086 from a secondary restatement and was not re-derived. The screening
rule in the middle section is this program's policy, not a claim from the
literature.
