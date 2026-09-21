---
id: KN-LIT-7652
type: literature
title: "Linear Code Equivalence via Plücker Coordinates"
authors:
  - "Gessica Alecci"
  - "Giuseppe D'Alconzo"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/495 (also arXiv:2603.09869)"
identifiers:
  eprint: "iacr:2026/495"
  doi: null
  arxiv: "2603.09869"
  url: "https://eprint.iacr.org/2026/495"
tags: [code-equivalence, group-action, invariant-theory, plucker, grassmannian, groebner, algebraic-cryptanalysis, signature, pqc, negative-result, less]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
An **algebraic model for the Linear Code Equivalence problem (LCE)** — the hardness
assumption behind the LESS signature scheme — built from **invariant theory on the
Grassmannian**.

LCE asks whether two linear codes are related by a monomial matrix `Q = DP` (`D`
diagonal, `P` permutation); recovery of `Q` is known to reduce to recovery of `P`
alone. The authors model the action of monomial matrices via **Plücker coordinates**,
treating the diagonal part as a scaling action on Grassmannian coordinates, and give a
method to determine **algebraically independent generators of the field of invariant
rational functions** — notably **without Reynolds operators and without Gröbner-basis
computation**. From each invariant they construct explicitly a polynomial having `P` as
a root.

## Key claims (as reported)
- Explicit algebraically independent generators of the invariant function field for the
  diagonal action on the Grassmannian, obtained without Reynolds operators or Gröbner
  bases.
- An algebraic system in `P` alone, with explicit polynomials vanishing at `P`.
- **The construction is not practically usable.** The authors state the polynomials have
  high degree at cryptographically relevant parameters and an exponentially growing
  number of monomials, making them infeasible to manipulate. They present the work as
  of theoretical interest.

## Relevance to this program
Held for the **method and the honest negative**, not for an attack.

- **Invariant theory as the systematic way to test an isomorphism assumption.** The
  question "does a computable invariant separate the orbits?" is the same question that
  decides [[KN-LIT-7648]] (where genus/spinor-genus theory collapses the orbits and
  DEFI falls). Here the invariants exist and are constructible, but their **description
  complexity** is the barrier. Those two entries together are the useful pair: the
  method is general, and whether it bites depends entirely on how expensive the
  invariants are to write down.
- **Direct methodological transfer to the ECDLP program.** Index calculus with
  summation polynomials fails for the same *shape* of reason: the algebraic system
  exists and is correct, but its degree and monomial count defeat solving
  (`first-fall-degree`/`degree-of-regularity` thread, [[KN-TECH-056]]). This is an
  independent 2026 instance of the pattern "correct algebraic model, useless at scale,"
  and the authors report it as such rather than hiding it — which is the standard
  `docs/inventor-protocol.md` asks for.
- **Avoiding Reynolds operators and Gröbner bases** is a technique note worth keeping
  on its own for anyone building invariant-theoretic models here.

**Does not bear on the ECDLP** directly, and **is not an attack on LESS** — the authors
say the model is infeasible at cryptographic parameters.

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/495,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, two authors, report number, year 2026.

**Dual identifier**, recorded deliberately: this paper is also `arXiv:2603.09869`
(submitted 2026-03-10, math.AG/cs.IT). The two were matched by title and author during
this sweep, not by any automatic mechanism — see the dedup note in
`knowledge/gathers/GATHER-20260801.md`.

NOT verified here: the invariant-generator construction; the claim that Reynolds
operators and Gröbner bases are avoided; the degree and monomial-count estimates; and
the infeasibility assessment. No LESS parameter set is assessed.
