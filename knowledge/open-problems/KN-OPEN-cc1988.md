---
id: KN-OPEN-cc1988
type: open_problem
title: >-
  Does any ECDLP weakness over a prime field vary within an isogeny class (a non-isogeny-invariant weakness), so that a Teske-style secret isogeny could hide it? The prime-field trapdoor question stated as a single existence problem
tags: [trapdoor, isogeny, prime-field, isogeny-invariant, teske, hiding-criterion, heavy-tail, semaev, factor-base, ecdlp, open]
confidence: reported
status: open
source_refs: [KN-TECH-6ead00, KN-TECH-8ef4c3, KN-TECH-031027, KN-LIT-7261, KN-LIT-3305, KN-LIT-7630, KN-LIT-7631, KN-TECH-ee6696, KN-FIND-f293c6, GOAL-ECTD-001, RQ-ECTD-001, H-ECTD-001, H-ISO-001]
added: 2026-09-30
superseded_by: null
---

## Statement

Let `p` be prime and let `C` be an ordinary isogeny class of elliptic curves
over `F_p` with prime group order `n`. Is there a property `W` of a curve
`E in C` such that

1. `W` is **not** constant on `C` (it is not a function of the trace, the
   order, the embedding degree, or the endomorphism algebra alone);
2. a curve with `W` admits an ECDLP algorithm of cost `n^{c}` with `c < 1/2`,
   or at least a precomputation / individual-log separation of hidden-SNFS
   type (KN-TECH-fcd4a7), on that curve;
3. `W` is rare enough (density `2^-k`, `k` in the affordable range of
   KN-TECH-031027) that a random curve in `C` does not have it; and
4. deciding `W` from the public curve equation, or finding a curve with `W`
   in `C` from a random starting curve, costs at least `sqrt(n)`?

If yes, Teske's construction (KN-TECH-8ef4c3) transfers to prime fields:
choose `E_s` with `W`, walk a secret isogeny to `E_pub`, publish `E_pub`. If
no such `W` exists, no isogeny-based ECDLP trapdoor exists over prime fields
and the only prime-field trapdoors are those in KN-TECH-6ead00 that hide
something other than a curve property.

## What is already known (as reported)

- Every *qualitative* known weakness is a class invariant: anomaly, small
  embedding degree, smooth order and Cheon divisors are all decided by `n`
  and `p`. GHS-type descent needs a subfield, and `F_p` has none. The
  ECTD briefing lists these as the four obstructions; GOAL-ECTD-001
  deprioritizes hiding any of them.
- Endomorphism-ring differences across a class give at most a GLV-style
  constant factor (`sqrt(#Aut)` or a small speedup from an efficiently
  computable endomorphism), not a change of exponent.
- Jao, Miller and Venkatesan (KN-LIT-7631) prove, under GRH, that the DLP is
  random-self-reducible across curves of the same endomorphism ring level via
  short isogeny walks, which means any `W` satisfying (4) must be sparse
  *within* a level or must live across a large-conductor barrier
  (KN-OPEN-cbbd97). KN-FIND-f293c6 evaluates the concrete cost of that
  reduction and finds it non-vacuous at 256 bits only for a large
  polynomial-degree parameter, so the barrier's concrete strength is itself
  open.
- The program's own short-neighbour audit (`H-ISO-001`, `rejected_scoped`)
  measured Semaev `d_reg` and relation yield across `l`-neighbours of small
  prime-field curves and found no advantage; it bounds the *easy* version
  (near neighbours, average behaviour), not the heavy-tail search across a
  whole class that `H-ECTD-001` pursues.

## Candidate properties under study (from the ECTD briefing, priority order)

1. Secret isogeny-aligned factor bases: an endpoint `E_s` plus a structured
   factor base `B_s` on which summation-polynomial relations are anomalously
   dense or Groebner degrees anomalously low.
2. A large-conductor vertical barrier between `E_pub` and `E_s`
   (KN-OPEN-cbbd97).
3. A hidden correspondence to another algebraic group (Jacobian, torus,
   disguised restriction of scalars) in the Dent-Galbraith style
   (KN-LIT-7633).
4. Trapdoor DDH first (KN-LIT-7634): a weaker target that shares the
   hiding architecture.

## Why it matters here

This is the single gap that separates the taxonomy's mechanisms from
attacks on prime-field standards. A positive answer composes immediately
with seed manipulation (KN-TECH-031027) into a deployable backdoor on
"verifiably random" curves; a negative answer (a proof that every
sub-`sqrt(n)` property is a class invariant, or is efficiently searchable)
would close GOAL-ECTD-001 and would be a real structural result about the
prime-field ECDLP. Either outcome is worth the search; premature closure
on the grounds that "nothing is known" is the failure mode the inventor
protocol warns against.
