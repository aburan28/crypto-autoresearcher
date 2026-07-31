---
id: KN-OPEN-019
type: open_problem
title: What object does each ECDLP attack family track, and is that enumeration closed?
tags: [ecdlp, methodology, tracked-object, attack-families, closure, saturation, index-calculus, generic-group, isogeny, open]
confidence: reported
status: open
source_refs: [KN-TECH-056, KN-LIT-7595, KN-LIT-7601, KN-LIT-7594, KN-OPEN-005, KN-OPEN-011, KN-OPEN-018]
added: 2026-07-28
superseded_by: null
---

## Statement
Symmetric-key cryptanalysis has a usable taxonomy of attack families indexed by **what
object is tracked through the rounds** — differences, parities, sums over structured sets,
adaptive oracle interaction, algebraic degree ([[KN-LIT-7595]]). That taxonomy is
productive: it lets a researcher forbid the known families, enumerate candidate objects,
and — in the source case — argue a **closure** over an entire class of them.

**The ECDLP has no such taxonomy.** This program catalogues its attack families by
*name and lineage* — generic/rho and its variants, index calculus with summation
polynomials and descent, isogeny and endomorphism-ring methods, lattice/HNP in the leakage
model — not by any shared answer to "what is being tracked." The question is whether an
object-indexed taxonomy exists here at all, and if so whether the list is closed.

## Why it matters
Practically, not aesthetically. This program has repeatedly concluded that the classical
ECDLP space is saturated — the 2026-07-20 completeness sweep found no classical survivor,
and the idea-generation series has run to dozens of consecutive rejection reports. Every
one of those conclusions is currently a **statement about the search**, not about the
problem: it says the generator stopped finding things, in a generator whose candidate space
is organized by lineage rather than by object. `KN-TECH-056` component 7 sets out what a
closure has to look like to be worth more than that. **This program cannot currently write
such a closure for the ECDLP, because it has no enumeration to close over.**

The stakes are recorded plainly in [[KN-LIT-7594]]: a model declined to attempt AES
cryptanalysis on the grounds that the target was exhaustively studied, and that assessment
was wrong.

## Current state (as reported)
- **The symmetric-side taxonomy does not obviously port.** The round-function framing is
  essential to it: an object is tracked *through iterated rounds*, and the family is
  characterized by what survives one round. The ECDLP has no round structure. Whether the
  analogue is "what survives one group operation," "what survives one step of a random
  walk," or something without a step at all is undetermined.
- **A partial mapping is visible but unverified.** Generic/rho methods arguably track
  *collisions in a walk*, index calculus tracks *smoothness/factor-base decompositions*,
  isogeny methods track *paths in an isogeny graph*, HNP tracks *short vectors in a lattice
  built from leaked bits*. Whether these are instances of one taxonomy or four unrelated
  descriptions has not been examined, and the fourth is confined to the leakage model
  ([[KN-OPEN-011]], [[KN-OPEN-018]]).
- **Unification is a live possibility on the symmetric side.** [[KN-LIT-7601]] exhibits a
  single formalism computing linear, differential, integral, differential-linear, and
  boomerang properties as instances of one formula. If the families unify there, the
  question of whether they unify here is at least well posed — though that paper's
  machinery is built for chunked Boolean functions on fixed-width state and supplies
  nothing directly.
- **A generic-group lower bound is not the closure being asked for.** The `√p` barrier
  bounds algorithms in the generic group model; every family above that matters — index
  calculus, isogeny methods — works by *leaving* that model. A closure over tracked objects
  would be a statement about what structure the concrete group exposes, which is a
  different question.

## What would resolve it
The first step is cheap and has not been taken: **write the enumeration down.** For each
known ECDLP family, state the object tracked, the operation it must survive, and the
obstruction that stops it — in the form `KN-TECH-056` component 7 demands. Three outcomes,
all informative:
1. The families turn out to track genuinely different objects with no common frame ⇒ the
   symmetric-side analogy fails, and this program's saturation claims must be justified
   some other way. Record the failure and close this entry.
2. A common frame emerges ⇒ candidate objects outside the enumerated set become
   generatable, and `KN-TECH-056` components 1–4 become directly usable by the
   Idea Generator.
3. A frame emerges *and* a transitivity-style argument closes it ⇒ this program would
   have, for the first time, a saturation result that is an argument rather than a tally.

**Nothing here asserts that outcome 2 or 3 is reachable, and no candidate object outside
the known families is proposed.** The claim is only that the enumeration has never been
written down, and that this program's repeated saturation conclusions are weaker than they
read until it is.

## Not verified here
This entry is a methodological question raised by [[KN-LIT-7595]] and [[KN-TECH-056]], not
a result. The partial mapping of families to objects above is this program's own sketch;
it appears in no source, has not been checked against the literature, and may be wrong in
any of its four parts. No claim is made that an ECDLP object-taxonomy exists.
