---
id: KN-LIT-a2f7b3
type: literature
title: "Last fall degree of semi-local polynomial systems"
authors:
  - "Huang, Ming-Deh A."
year: 2023
venue: "arXiv preprint (submitted 2023-11-06); no peer-reviewed venue established here"
identifiers:
  eprint: null
  doi: null
  arxiv: "2311.02804"
  url: "https://arxiv.org/abs/2311.02804"
tags: [last-fall-degree, semi-local, zero-dimensional, closed-points, solving-degree,
  groebner, weil-descent, hfe, summation-polynomial, ecdlp, small-characteristic,
  candidate-ingredient, abstract-only, prior-art]
confidence: reported
citation_verified: web
citation_provenance: retrieved
added: "2026-09-16"
superseded_by: null
---

## Why this entry exists

This paper has **no prior entry in this corpus** and it is the most recent
member of the last-fall-degree line the corpus already tracks (`KN-LIT-7607`,
`KN-LIT-7605`). It was found during the novelty check for the
`RQ-DREG-bd6c86` ideation batch of 2026-09-16 and is recorded under the Idea
Generator's ingredient-scouting duty (search bias 2 of
`agents/idea-generator.md`): log a candidate external structural result even
when no idea follows immediately. Here one does follow —
`IDEA-20260916-e6540d` names it as a *candidate rigorous ingredient with a
mandatory proves-too-much audit attached*, and does not rely on it.

## Contribution (ABSTRACT ONLY — the body was not read)

Studies the last fall degree of **semi-local** polynomial systems over finite
fields. As relayed from the abstract:

- the main results **bound the last fall degree of a semi-local polynomial
  system in terms of the number of closed point solutions**;
- there is **an efficient algorithm for finding all rational-point solutions
  when the prime characteristic of the finite field and the number of rational
  solutions are both small**;
- the results are stated to give improvements to polynomial-time attacks on
  HFE cryptosystems, and to extend to other semi-local systems with either a
  small closed-point-solution count or small characteristic;
- the paper suggests that semi-local systems over **large** prime
  characteristic with **exponentially many** closed points may provide
  cryptographic security.

## Why it is a candidate ingredient for this program, and why the audit is mandatory

A Weil-descended Semaev point-decomposition system **with field equations** is
zero-dimensional (hence semi-local), lives in characteristic 2 (small), and
typically has very few rational solutions (a random target has zero or a
handful of decompositions over the factor base). That is, on its face, exactly
the favourable regime the abstract describes — which is precisely why it must
not be applied on the strength of an abstract.

**The proves-too-much check, stated before anyone reads the body.** A random
Boolean quadratic system with one planted solution also has small
characteristic and a small rational-solution count. If a naive reading of the
bound gave a constant last fall degree there, it would assert that random MQ
with a planted solution is efficiently solvable — which contradicts the
standard hardness expectation and is directly testable at small `n` with a
degree-fall profile. So one of three things is true and the audit decides
which: (i) the hypotheses exclude systems of this kind (useful closure, and the
excluding hypothesis should be quoted); (ii) they do not, and the bound is a
real ingredient; (iii) the naive reading proves too much, and the hypothesis
doing the work should be named. The audit is reading plus one small
measurement.

## Relation to KN-LIT-7605 — a discrepancy recorded, not resolved

`KN-LIT-7605` records arXiv:**2103.07282** and summarises it as: "the **last
fall degree is bounded independently of `n`**, the field extension degree" with
"bounded-fall-degree results ... stated for summation-polynomial systems over
`F_2` specifically." That record itself discloses that the full text was not
read, that the claims came from "a fetched summary of the PDF", and that
**authors, year and publication venue were not established** and were left
empty.

Fetching `https://arxiv.org/abs/2103.07282` on 2026-09-16 returned instead:

- **author Ming-Deh Huang, submitted 2021-03-08** (filling the fields
  `KN-LIT-7605` left empty);
- a theorem **relating the last fall degrees of a polynomial system and of its
  Weil descent**, for systems **not necessarily of dimension zero**;
- as an application, **upper bounds on the last fall degree in the case where
  the system is a set of linearized polynomials**;
- **summation polynomials are not named in the abstract.**

This session could therefore **not confirm** the "bounded independently of `n`
for summation-polynomial systems over `F_2`" reading. That matters beyond
bookkeeping, because `KN-LIT-7605` is cited in this corpus as "direct prior
art for `KN-FIND-006`" and as establishing "in **proved** form what
`KN-FIND-006` reports as a **measurement**", and `KN-LIT-7607` carries a
standing rule requiring both records to be cited before any claim that the
deficit is bounded in system size.

**Nothing is asserted here about which reading is correct.** Per `AGENTS.md`
rule 2 the prior record is not edited and is not marked superseded by this one:
they are different papers. What is asserted is exactly this: the arXiv landing
page for 2103.07282, fetched on 2026-09-16, does not support the summary
`KN-LIT-7605` carries, and the disagreement is resolvable only by reading the
2103.07282 body. Until someone does, **no proposal should lean on
`KN-LIT-7605`'s "bounded independently of n" sentence**, and the three
2026-09-16 proposals that cite it say so in their citation blocks.

A third, adjacent record found in the same search and **not** entered here
because only its title and abstract-level description were seen: Caminata and
Gorla, "Solving degree, last fall degree, and related invariants", ePrint
2021/1611 / J. Symbolic Computation, whose abstract states that its main
results include "a connection between the solving degree and the last fall
degree and one between the degree of regularity and the Castelnuovo–Mumford
regularity". It is already cited (as `retrieved`, introduction and stated main
result only) by `IDEA-20260905-d76d38`. It is the natural place to find the
precise inequality this corpus keeps needing and keeps not having.

## Not verified here

- **The body was not read.** Every claim above under "Contribution" is relayed
  from the arXiv abstract as returned by a single fetch on 2026-09-16.
- The **definition** of last fall degree used by this paper was not obtained,
  so its relation to the four first-fall-degree definitions catalogued in
  `KN-OPEN-7f0511` and to the fall-profile observable of
  `IDEA-20260916-4b7c1e` is **unknown**.
- No hypothesis of the main bound was checked, no application to
  summation-polynomial systems is asserted by the source or by this record, and
  **no numerical bound on any Semaev system follows from this entry**.
- Peer-review status, published venue and any later revision were not
  established; only the arXiv landing page was seen.
- The paper was **not vendored** and no frozen source record exists for it.

## Identifier provenance

The agent that wrote this record had no shell in its tool surface and could not
run `tools/allocate_id.py`. Its documented semantics were reproduced by hand: a
random 6-hex token drawn **without scanning state**, then a collision check
over the identifier space with `Glob '**/*a2f7b3*'` (no match). A Coordinator
should confirm with `python3 tools/allocate_id.py --check KN-LIT-a2f7b3` before
committing this file.
