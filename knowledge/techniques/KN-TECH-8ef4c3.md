---
id: KN-TECH-8ef4c3
type: technique
title: >-
  Teske's isogeny-hidden GHS trapdoor -- a secret isogeny from a public curve over a composite-degree binary field to a Weil-descent-vulnerable curve in its isogeny class
tags: [trapdoor, teske, ghs, weil-descent, isogeny, binary-field, composite-degree, hyperelliptic, escrow, ecdlp]
confidence: reported
complexity: >-
  holder solves the DLP at the cost of GHS index calculus on a genus-g hyperelliptic Jacobian over the subfield (subexponential-to-polynomial in the subfield size for the published parameters, g ~ 8 over F_{2^23}); outsider faces rho at sqrt(n) unless they recover the isogeny, whose best public cost is the isogeny-class walk (~O(#E^{1/4}) meet-in-the-middle in the class, per the ECTD briefing's threat model)
applicability: >-
  curves over F_{q^m} with m composite (published: F_{2^161} = F_{(2^23)^7}); NOT applicable over prime fields (no subfield to descend to) and not to any weakness that is an isogeny-class invariant
source_refs: [KN-LIT-7261, KN-LIT-3305, KN-LIT-3748, KN-LIT-007, KN-LIT-7630, KN-LIT-7631, KN-LIT-7632, KN-TECH-6ead00, KN-OPEN-cc1988, GOAL-ECTD-001, RQ-ECTD-001]
added: 2026-09-30
superseded_by: null
---

## Construction (as reported from KN-LIT-7261 and the ECTD briefing)

1. Fix a composite-degree binary field `F_{2^{161}} = F_{(2^{23})^7}`.
2. Choose a curve `E_s` whose Weil restriction to `F_{2^{23}}` is GHS-vulnerable:
   the descent (KN-LIT-007) lands the DLP in the Jacobian of a hyperelliptic
   curve of genus small enough (about 8) that index calculus over `F_{2^{23}}`
   is feasible.
3. Walk a secret chain of small-degree isogenies from `E_s` to a curve
   `E_pub` in the same class that is **not** directly GHS-vulnerable. Publish
   `E_pub` and its base point; keep the chain.
4. To solve a DLP on `E_pub`, map the instance through the chain to `E_s`,
   descend, solve on the Jacobian, and map back.

## Why it works

GHS vulnerability depends on the curve equation (the 2-rank of the Weil
restriction), not on the group order, so it is **not** an isogeny invariant.
Menezes and Teske (KN-LIT-3305) and Galbraith, Hess and Smart (KN-LIT-3748)
showed that within the isogeny class of a GHS-vulnerable curve every curve is
attackable *in principle*, by walking to the vulnerable one; Teske's trapdoor
is the observation that the walk is the hard part when it is long and secret.
The public attack on `E_pub` is therefore an isogeny-path search, which
(KN-LIT-7630) is at best a meet-in-the-middle over the class.

## Detectability

There is no polynomial-time public invariant that distinguishes `E_pub` from
a random curve over the same field, as far as is reported. What is visible is
the field: `m = 161 = 7 * 23` is composite, and composite-degree binary
fields have been avoided by every post-2000 standard precisely because of
GHS. The construction therefore hides *which* curve, not *that* the field
class is dangerous.

## Applicability limits (this program's reading)

- Requires a proper subfield: `q^m` with `m > 1`. Over `F_p` the descent has
  nowhere to go; this is the first of the four obstructions listed in the
  ECTD briefing and in KN-OPEN-cc1988.
- The hidden weakness must be non-invariant under the hiding map. Anomaly,
  embedding degree, order smoothness and Cheon divisors are class invariants
  and cannot be hidden this way (KN-TECH-6ead00, hiding criterion).
- The holder's advantage is bounded by GHS itself: for larger subfields or
  larger genus the Jacobian DLP is no longer cheap, so the parameter window is
  narrow.

## Relevance

This is the single published *genuine* ECDLP trapdoor and the anchor of
GOAL-ECTD-001, whose objective is the prime-field analogue. The program's own
short-neighbour Semaev audit (`H-ISO-001`, `rejected_scoped`) found no
advantage among near isogenous curves over prime fields, which bounds the
easy version of the analogue but not the heavy-tail search the goal pursues.
