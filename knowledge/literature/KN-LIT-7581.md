---
id: KN-LIT-7581
type: literature
title: Quantum Lazy Sampling and Path Recording for Any Group
authors:
  - "Ben Foxman"
  - "Alex Lombardi"
  - "Fermi Ma"
  - "Barak Nehoran"
  - "John Wright"
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/1510'
identifiers:
  eprint: iacr:2026/1510
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/1510
tags: [generic-group-model, oracle-simulation, compressed-oracle, lazy-sampling, query-complexity, lower-bound, quantum, pseudorandom-unitary, foundations, proof-technique]
confidence: reported
citation_verified: web
added: "2026-07-27"
superseded_by: null
---

## Contribution
Defines and analyses a general-purpose, interpretable **path-recording oracle** that
perfectly simulates a random element of *any closed subgroup of `U(N)`*. This unifies and
generalises the compressed-oracle line: Zhandry (CRYPTO '19) for random functions,
Ma–Huang (STOC '25) for random unitaries, Carolan (STOC '26) for permutations.

## Key claims (as reported)
- The path-recording oracle stores superpositions of `t` input-output pairs
  `|(x_1,y_1), ..., (x_t,y_t)>`, encoding the Feynman path explored by the algorithm, and
  so transparently records what the algorithm may have learned from its queries.
- It **perfectly** simulates random elements of any closed subgroup of `U(N)` — the
  generality is the headline.
- The update procedure has an "operationally useful" mathematical description in terms of
  the **commutant of the group's tensor-power representation**.
- Because the construction is uniform in the group, it enables *direct comparison* between
  compressed oracles for different groups — presented as a new technique for proving
  pseudorandomness results.
- Main application: formally relating the `S_N` and `U(N)` compressed oracles yields
  "arguably the simplest construction to date" of pseudorandom unitaries — the product
  `PC` of a pseudorandom permutation and a random Clifford, improving on the prior `PFC`
  construction (Metger–Poremba–Sinha–Yuen, FOCS '24; Ma–Huang, STOC '25).
- Builds on Grinko–Yoshida (QIP '26), who gave a different general-purpose compressed
  oracle that the authors characterise as lacking clear interpretability.

## Relevance to this program
This is the entry in the 2026-07-27 gather with the most direct methodological bearing on
the program's own foundations, and it is worth being precise about *where* the bearing is.

`KN-TECH-005` (generic group model and the square-root discrete-log lower bound) is the
program's record of the argument that makes `sqrt(p)` a barrier rather than merely a
best-known bound. That argument is, at its core, an *oracle-simulation* argument: one
shows that an algorithm interacting with an abstractly-presented group learns nothing it
could not have learned from a lazily-sampled stand-in, and then counts queries. This paper
is a general theory of exactly that simulation step, in the quantum setting, for arbitrary
closed subgroups of `U(N)`.

What that does and does not imply:

- It is a **proof-technique** entry, not an ECDLP result. The paper's own application is
  pseudorandom unitaries, which is unrelated to discrete logarithms. It supplies
  machinery, not evidence about `sqrt(p)`.
- The commutant-of-the-tensor-power description is the potentially reusable instrument.
  The program's generic-group reasoning has so far been conducted in the classical
  idiom; a uniform quantum recording oracle for an arbitrary group is the natural tool
  for asking what a quantum generic-group adversary knows after `t` queries.
- The standing caveat on all generic-group reasoning applies unchanged and should not be
  softened by this entry: a *generic*-group lower bound bounds algorithms that do not
  exploit the concrete representation of the group. The ECDLP's actual security question
  is whether the explicit `E(F_p)` representation admits non-generic structure. Better
  tools for the generic model do not narrow that gap; if anything, sharper generic
  machinery makes it more important to record that the barrier it certifies is a barrier
  *for generic algorithms only*.

No existing entry is superseded. `KN-TECH-005` is unchanged by this; the relationship is
that this paper strengthens the toolkit in which `KN-TECH-005`-style arguments are
conducted.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved from
eprint.iacr.org on 2026-07-27 (hence `confidence: reported`). ePrint history: received
2026-07-23, approved 2026-07-25. Not peer-reviewed or formally published as of this
entry; no DOI on the ePrint page. Category: FOUNDATIONS.

NOT verified here: the perfect-simulation claim and its precise statement (what
"perfectly" quantifies over, and for which subgroups the analysis is unconditional); the
commutant characterisation of the update rule; the `PC` pseudorandom-unitary construction
and the sense in which it improves on `PFC`; the attributions to Zhandry, Ma–Huang,
Carolan, Metger–Poremba–Sinha–Yuen, and Grinko–Yoshida; and the query-complexity
consequences, if any, for group-theoretic problems. **Nothing here has been checked to
apply to the ECDLP or to the generic-group bound recorded in `KN-TECH-005`** — the
connection drawn above is this program's reading of the technique's scope, not a claim
made by the paper.
