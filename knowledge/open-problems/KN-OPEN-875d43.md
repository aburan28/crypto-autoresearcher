---
id: KN-OPEN-875d43
type: open_problem
title: Does weakness beat description length as a hypothesis-selection proxy under a non-uniform (cryptanalytic) task distribution?
tags: [methodology, hypothesis-selection, induction, generalisation, weakness, mdl, occams-razor, non-uniform-prior, harness-evaluation, open]
confidence: unverified
status: open
source_refs: [KN-LIT-3822a6, KN-TECH-276d30, KN-TECH-056, KN-TECH-080]
added: 2026-08-05
superseded_by: null
---

## Statement

Bennett ([[KN-LIT-3822a6]]) proves — inside a formalism of enactive cognition and
**assuming a uniform distribution over tasks** (`Definition 4`) — that maximising a
hypothesis's weakness `|Z_h|` is necessary and sufficient to maximise the probability it
generalises, and that minimising description length is neither.

This program's hypothesis space is not uniformly distributed. Structure is its entire
subject matter: the curves, parameter ranges, and solver behaviours it reasons about are
drawn from a heavily biased distribution, and the paper's own no-free-lunch framing says
explicitly that another proxy can beat weakness on a non-uniform sub-family (at the cost
of losing on the rest). So the theorem does not transfer, and the practical question is
open:

**Under the actual, structured distribution of hypotheses this program generates, does
preferring the weakest valid hypothesis produce hypotheses that survive parameter changes
more often than the program's current informal simplicity-flavoured default?**

## Why it is not answerable by reading the paper

Two gaps, both load-bearing:

1. **Embedding.** `|Z_h|` is defined for statements in a finite implementable language
   `L_v`. It is not defined for a hypothesis such as "relation search over curve family F
   has cost exponent e". [[KN-TECH-276d30]] proposes a hand-applied surrogate (rank by how
   few structural preconditions the hypothesis assumes) and claims none of the paper's
   guarantees for it. Whether any embedding exists for which weakness is both defined and
   computable at this program's scale is itself unknown.
2. **Prior.** Even granting an embedding, the proofs' uniform prior is what makes
   `2^{|Z̄ ∩ Z_h|}/2^{|Z̄|}` a probability of generalisation. Replacing it with the
   program's empirical distribution over tasks changes the quantity being maximised, and
   nothing in the paper bounds the difference.

## Cheapest discriminating test

Retrospective, no new experiments needed, and it is the reason this is worth filing rather
than deferring:

Take a set of already-closed hypotheses in the ledger whose fate is known — those that
were later re-tested at different parameters, curves, or budget, so it is recorded whether
they held. For each, reconstruct the sibling candidates that fit the same original
evidence (from the proposal and design records, not invented after the fact). Score each
candidate pair by (a) the surrogate weakness ordering and (b) a description-length-flavoured
simplicity ordering. Then ask which ordering more often ranked first the hypothesis that
actually survived re-testing.

Failure modes to design against before running it: the sibling candidates must come from
contemporaneous records or the reconstruction is hindsight; the sample of re-tested
hypotheses is small and the result will at best be suggestive; and both orderings are
applied by an agent, so the scoring has to be blind to the outcome column.

A null result — the two orderings agree on nearly every historical case — is the most
likely outcome and is worth recording, because it would mean the choice of proxy has not
yet been load-bearing in this program and the discipline in [[KN-TECH-276d30]] is cheap
insurance rather than a change of behaviour.

## What would close this

Either (i) the retrospective above, replicated, showing one ordering predicts survival
better in this domain, or (ii) a derivation of what weakness maximisation optimises under
a stated non-uniform prior over `Γ_v`, which would say whether the transfer is principled
or coincidental. Neither exists. Until one does, weakness is adopted here as a motivated
default, not a proven one.
