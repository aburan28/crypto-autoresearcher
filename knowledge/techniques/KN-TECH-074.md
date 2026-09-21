---
id: KN-TECH-074
type: technique
title: Division property and monomial prediction - deciding when an integral distinguisher survives
tags: [division-property, integral-attack, bit-based-division-property, three-subset, monomial-prediction, parity-set, todo, superpoly-recovery, milp, algebraic-degree, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "propagation over the round function is tracked as a set of exponent vectors; bit-based tracking is exponential in state size if done naively, which is why the standard implementation is an MILP/SAT model whose feasibility answers the distinguisher question"
applicability: deciding whether a summation over a chosen input set is guaranteed to vanish after r rounds - i.e. whether an integral distinguisher exists - and, in its monomial-prediction form, recovering cube superpolies too large to evaluate experimentally
source_refs: [KN-TECH-063, KN-TECH-073, KN-TECH-076, KN-LIT-2713, KN-LIT-2567, KN-LIT-2646, KN-LIT-2564, KN-LIT-2453, KN-LIT-3165, KN-LIT-3343, KN-LIT-4403, KN-LIT-5472, KN-LIT-1995, KN-LIT-4527, KN-LIT-2087]
added: 2026-07-31
superseded_by: null
---

## Method

### The question it answers

Integral/saturation/square attacks (Daemen–Knudsen–Rijmen; Knudsen–Wagner) take
a structured input set — typically all values of one word, everything else fixed
— and observe that some output word sums to zero. Classically these
distinguishers were found by hand, by tracking a small vocabulary of word
states (ALL / CONSTANT / BALANCED / UNKNOWN) through the rounds. The vocabulary
is coarse: it loses information at the S-box, so it reports UNKNOWN where a
sharper analysis would still prove balance.

Todo (2015) replaced the vocabulary with an algebraic invariant. For a multiset
`X ⊆ F_2^n`, ask for which exponent vectors `u` the sum `Σ_{x∈X} x^u` is
**guaranteed** zero — where `x^u = Π x_i^{u_i}`. The **division property** is the
bookkeeping of the surviving `u`'s, propagated through the round function by
rules for COPY, XOR, AND and S-box application (the S-box rule being governed by
its algebraic degree). If after `r` rounds the vector selecting an output bit is
guaranteed absent, that bit's sum is zero — an integral distinguisher, proved
rather than guessed.

### Refinements, in the order they mattered

- **Bit-based division property** (`KN-LIT-2713`): track individual bits rather
  than words. Far sharper, and immediately expensive — the state set is
  exponential in the state size.
- **MILP/SAT modelling** (`KN-LIT-2567`, `KN-LIT-2646`): encode the propagation
  rules as constraints and let a solver decide feasibility. This is what made
  bit-based tracking practical, and it is why this technique and `KN-TECH-076`
  are inseparable in practice.
- **Three-subset division property and monomial prediction.** The plain division
  property proves a monomial *absent*; it cannot prove one *present*, because
  cancellation is not tracked. Refining the state to count parity exactly turns
  the method from a one-sided proof into an exact computation of whether a given
  monomial appears — which is precisely **superpoly recovery** for cube attacks
  (`KN-TECH-073`).
- **Alternative formulations**: parity sets and the set-theoretic view
  (`KN-LIT-2564`), an algebraic formulation tying it to degree evaluation
  (`KN-LIT-2453`), convexity structure in the transitions (`KN-LIT-3165`), and
  a field-based version for primitives over large prime fields (`KN-LIT-5472`,
  used against the designs of `KN-TECH-075`).

### What it delivered

- Integral distinguishers beyond what hand analysis found, including the full-
  MISTY1 results (`KN-LIT-1995`, `KN-LIT-4527`).
- Division-property-based cube attacks (`KN-LIT-3343`, `KN-LIT-4403`), which
  lifted cube attacks past the `2^k`-evaluation barrier and produced the deepest
  reported results on Trivium-family ciphers (`KN-LIT-2087`).

## Program usage

- **This is the entry with the most direct methodological transfer to this
  program's own work.** Its content is: *replace an ad-hoc propagation
  vocabulary with an algebraic invariant that is exactly preserved by the
  operations you care about, then decide the question by constraint solving.*
  The program's own degree-of-regularity and syzygy analysis (`KN-FIND-006`) is
  the same species of move — replacing a heuristic rank count with a structural
  one — and `KN-TECH-056`'s object-first protocol asks for exactly this kind of
  tracked object.
- **It is also a case study in one-sidedness.** The plain division property
  proves absence only; treating "no distinguisher found" as "no distinguisher
  exists" was the standing error, and the three-subset/monomial-prediction
  refinement is what closed it. The program's rule that a timeout is never
  negative mathematical evidence (`AGENTS.md`) is the same principle; here the
  field paid for learning it, and the fix was a sharper invariant rather than a
  bigger budget.
- **Keccak and AES relevance is indirect.** The technique bears on the symmetric
  components the PQC standards use, at round-reduced scale only, as recorded in
  `KN-TECH-066` and `KN-TECH-073`.

## Applicability limits

- **Absence is proved; presence is not** — unless the three-subset or
  monomial-prediction refinement is used. A plain division-property search that
  finds no distinguisher has proved nothing about the cipher.
- **Model correctness is the attack surface.** The result is a solver verdict on
  an encoding; an incorrect propagation constraint yields a confidently wrong
  answer in either direction. Independent re-encoding is the standard check,
  and `KN-TECH-076` records the wider hygiene.
- **Solver cost is unpredictable.** MILP/SAT feasibility on these models has no
  useful a-priori bound, and reported run times are instance-specific
  observations, not complexities.
- **Distinguisher, not break.** An integral distinguisher on `r` rounds is a
  distinguisher on `r` rounds; converting it to key recovery costs extra rounds
  and extra data, and that conversion is a separate argument.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The division-property definition, the
propagation-rule structure, the one-sidedness of the plain form and the role of
the three-subset/monomial-prediction refinement in superpoly recovery are
standard published results, written from established knowledge and not
re-derived or implemented here. Todo's originating papers, the Todo–Morii
bit-based paper, the Xiang et al. MILP modelling and the Hu–Sun–Wang–Wang
monomial-prediction line are named in prose or cited only through this corpus's
**title-level** records; no identifier was minted for any paper this corpus does
not hold. The attributions of full MISTY1 to `KN-LIT-1995`/`KN-LIT-4527` and of
855-round Trivium to `KN-LIT-2087` are read from titles; **their complexity
figures were not read and are not quoted.** The comparison to `KN-FIND-006` and
to the program's timeout rule is this program's own reasoning.
